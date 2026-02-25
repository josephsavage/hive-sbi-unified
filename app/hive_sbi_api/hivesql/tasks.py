import logging
import pytz

import pandas as pd

from datetime import (datetime,
                      timedelta)

from celery import (current_app,
                    shared_task,
                    states as celery_states)
from celery.exceptions import Ignore
from celery.schedules import crontab

from django.utils import timezone
from django.db.models import Sum
from hive_sbi_api.core.models import (Member,
                                      Post,
                                      Vote,
                                      MaxDailyHivePerMVest,
                                      LastSyncOlderPostOriginalEnrollment)
from hive_sbi_api.sbi.models import MemberHist
from hive_sbi_api.sbi.data import VOTER_ACCOUNTS
from hive_sbi_api.hivesql.models import (HiveSQLComment,
                                         HiveSQLTxVotes,
                                         VoFillVestingWithdraw)

logger = logging.getLogger('hivesql')
app = current_app._get_current_object()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour=8),
        set_max_vo_fill_vesting_withdrawn.s(),
        name='set_max_vo_fill_vesting_withdrawn',
    )

    # sender.add_periodic_task(
    #     crontab(minute='*/45',),
    #     sync_older_posts_from_votes.s(),
    #     name='sync_older_posts_from_votes',
    # )


@app.task(bind=True)
def set_max_vo_fill_vesting_withdrawn(self):
    if MaxDailyHivePerMVest.objects.exists():
        last_register = MaxDailyHivePerMVest.objects.latest("timestamp")
        last_registered_date = last_register.timestamp
    else:
        last_registered_date = VoFillVestingWithdraw.objects.first().timestamp

    init_date = last_registered_date + timedelta(days=1)

    end_date = init_date + timedelta(days=15)
    now = timezone.now() - timedelta(days=1)

    if end_date > now:
        end_date = now

    max_hive_per_mvests_for_create = []
    daterange = pd.date_range(init_date, end_date)

    for single_date in daterange:
        date_registers = VoFillVestingWithdraw.objects.filter(
            withdrawn_symbol="VESTS",
            deposited_symbol="HIVE",
            timestamp__year=single_date.year,
            timestamp__month=single_date.month,
            timestamp__day=single_date.day,
        )

        if not date_registers:
            if not MaxDailyHivePerMVest.objects.filter(
                timestamp__year=single_date.year,
                timestamp__month=single_date.month,
                timestamp__day=single_date.day,
            ):

                max_hive_per_mvests_for_create.append(MaxDailyHivePerMVest(
                    timestamp=single_date
                ))

            continue

        max_hive_per_mvest_obj = max(date_registers, key=lambda register: register.get_hive_per_mvest())

        max_hive_per_mvests_for_create.append(MaxDailyHivePerMVest(
            hivesql_id=max_hive_per_mvest_obj.ID,
            block_num=max_hive_per_mvest_obj.block_num,
            timestamp=max_hive_per_mvest_obj.timestamp,
            hive_per_mvest=max_hive_per_mvest_obj.get_hive_per_mvest()
        ))

    MaxDailyHivePerMVest.objects.bulk_create(max_hive_per_mvests_for_create)

    return "Calculated between {} and {}.".format(
        init_date,
        end_date,
    )

@shared_task(bind=True)
def sync_empty_votes_posts(self):
    # 1. Target posts that have no calculated rshares yet
    # and haven't been confirmed as 'empty' by a previous run.
    from hive_sbi_api.core.models import Post, Vote
    posts_to_sync = Post.objects.filter(
        total_rshares=0, 
        empty_votes=False,
    )[:50]

    posts_synced_counter = 0
    empty_posts_counter = 0

    for post in posts_to_sync:
        # 2. Use the database to sum the related Vote rows
        # This replaces the old JSON iteration entirely.
        aggregate_result = post.vote_set.aggregate(total=Sum('rshares'))
        total_found = aggregate_result['total'] or 0

        if total_found > 0:
            post.total_rshares = total_found
            # We save specifically to move this post out of the 'total_rshares=0' filter
            post.save(update_fields=['total_rshares'])
            posts_synced_counter += 1
        else:
            # 3. If no votes exist in the DB, mark it so we don't query it again
            post.empty_votes = True
            post.save(update_fields=['empty_votes'])
            empty_posts_counter += 1

    return f"Processed {posts_to_sync.count()} posts. Updated: {posts_synced_counter}. Marked Empty: {empty_posts_counter}."
  
# Unused code
@app.task(bind=True)
def sync_older_posts_from_votes(self):
    min_limit = Member.objects.all().order_by("original_enrollment").first().original_enrollment

    if LastSyncOlderPostOriginalEnrollment.objects.count():
        min_limit = LastSyncOlderPostOriginalEnrollment.objects.first().original_enrollment
    else:

        LastSyncOlderPostOriginalEnrollment.objects.create(
            original_enrollment=min_limit,
        )

    max_limit = Post.objects.get(
        author="mango-juice",
        permlink="my-daily-steemmonsters-report-73"
    ).created


    votes = HiveSQLTxVotes.objects.filter(
        voter__in=VOTER_ACCOUNTS,
        timestamp__gt=min_limit,
        timestamp__lt=max_limit,
    )[:3000]

    if not votes:
        return "REMOVE ME!!! My work is finished."

    already_registered_post_counter = 0
    created_post_counter = 0
    posts_for_create = []

    new_min_timestamp = min_limit 

    for vote in votes:
        if Post.objects.filter(
            author=vote.author,
            permlink=vote.permlink,
        ).exists():
            already_registered_post_counter += 1

            continue

        hivesql_comment = HiveSQLComment.objects.filter(
            author=vote.author,
            permlink=vote.permlink,
        ).first()

        logger.info("---------------------------------------------")
        logger.info(vote.author)
        logger.info(vote.permlink)
        logger.info("---------------------------------------------")

        if not hivesql_comment:
            continue

        Post.objects.create(
            author=hivesql_comment.author,
            permlink=hivesql_comment.permlink,
            title=hivesql_comment.title,
            created=hivesql_comment.created,
            vote_rshares=hivesql_comment.vote_rshares,
            total_payout_value=hivesql_comment.total_payout_value,
            author_rewards=hivesql_comment.author_rewards,
            active_votes=hivesql_comment.active_votes,
            total_rshares=0,
        )

        created_post_counter += 1
        new_min_timestamp = vote.timestamp

    last_register = LastSyncOlderPostOriginalEnrollment.objects.first()
    last_register.original_enrollment = new_min_timestamp
    last_register.save()

    return "{} already registered posts. {} posts created. New min timestamp = {}".format(
        already_registered_post_counter, created_post_counter, new_min_timestamp)


@app.task(bind=True)
def sync_post_votes(self):
    logger.info("Initializing votes sync")

    last_sync_datetime = None

    if Vote.objects.exists():
        last_sync_vote = Vote.objects.latest("member_hist_datetime")
        last_sync_datetime = last_sync_vote.member_hist_datetime

    timestamp_limit = timezone.now() - timedelta(days=7)
    timestamp_limit = timestamp_limit.replace(tzinfo=pytz.UTC)

    if last_sync_datetime:
        logger.info("last_sync_datetime: {}".format(last_sync_datetime))
        member_hist_qr = MemberHist.objects.filter(
            voter__in=VOTER_ACCOUNTS,
            timestamp__gt=last_sync_datetime,
            timestamp__lt=timestamp_limit,
        )[:3600]
    else:
        member_hist_qr = MemberHist.objects.filter(
            voter__in=VOTER_ACCOUNTS,
            timestamp__lt=timestamp_limit,
        )[:3600]

    new_posts_counter = 0
    votes_for_create = []

    for member_hist in member_hist_qr:
        author = member_hist.author
        permlink = member_hist.permlink
        timestamp = member_hist.timestamp
        voter = member_hist.voter

        post = Post.objects.filter(
            author=author,
            permlink=permlink,
        ).first()

        if not post:
            new_posts_counter += 1

            hivesql_comment = HiveSQLComment.objects.filter(
                author=author,
                permlink=permlink,
            ).first()

            if not hivesql_comment:
                continue

            if Post.objects.filter(
                author=hivesql_comment.author,
                permlink=hivesql_comment.permlink,
            ).exists():
                continue
            
            has_beneficiaries = False

            if hivesql_comment.beneficiaries:
                has_beneficiaries = True

            post = Post.objects.create(
                author=hivesql_comment.author,
                permlink=hivesql_comment.permlink,
                title=hivesql_comment.title,
                created=hivesql_comment.created,
                vote_rshares=hivesql_comment.vote_rshares,
                total_payout_value=hivesql_comment.total_payout_value,
                author_rewards=hivesql_comment.author_rewards,
                # active_votes=hivesql_comment.active_votes,
                total_rshares=0,
                has_beneficiaries=has_beneficiaries,
                beneficiaries=hivesql_comment.beneficiaries,
                percent_hbd=hivesql_comment.percent_hbd,
                curator_payout_value=hivesql_comment.curator_payout_value,
            )

            total_rshares = 0

            for vote in PostVotes.objects.get(post_id=post.id).active_votes:
                total_rshares = total_rshares + int(vote["rshares"])

                if vote["voter"] in VOTER_ACCOUNTS and not Vote.objects.filter(post=post, voter=vote["voter"]):

                    member_hist_vote = MemberHist.objects.filter(
                        author=author,
                        permlink=permlink,
                        voter=vote["voter"],
                    ).first()

                    vote_time = datetime.strptime(vote["time"], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=pytz.UTC) 

                    if member_hist_vote:
                        member_hist_datetime = member_hist_vote.timestamp 
                    else:
                        member_hist_datetime = vote_time - timedelta(minutes=1)

                    votes_for_create.append(Vote(
                        post=post,
                        voter=vote["voter"],
                        weight=vote["weight"],
                        rshares=vote["rshares"],
                        percent=vote["percent"],
                        reputation=vote["reputation"],
                        time=vote_time,
                        member_hist_datetime=member_hist_datetime,
                    ))

            post.total_rshares = total_rshares
            post.save()

    Vote.objects.bulk_create(votes_for_create)
    sync_empty_votes_posts.delay()

    return "Created {} posts and {} votes".format(new_posts_counter, len(votes_for_create))
