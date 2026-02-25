import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from .data import (TRX_SOURCE_CHOICES,
                   TRX_STATUS_CHOICES,
                   TRX_SHARE_TYPE_CHOICES,
                   FAILED_TRX_TYPE_CHOICES)


logger = logging.getLogger('v1')

# app/hive_sbi_api/core/models.py

class PostVotes(models.Model):
    post = models.OneToOneField(
        "core.Post",
        on_delete=models.CASCADE,
        related_name="votes_payload",
        primary_key=True,
    )
#    active_votes = models.JSONField(null=True, blank=True)
#    beneficiaries = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "core_post_votes"
      
class Configuration(models.Model):
    share_cycle_min = models.FloatField(
        default=144,
    )

    sp_share_ratio = models.FloatField(
        default=2,
    )

    rshares_per_cycle = models.BigIntegerField(
        null=True,
        default=800000000,
    )

    del_rshares_per_cycle = models.BigIntegerField(
        default=800000000,
    )

    comment_vote_divider = models.FloatField(
        null=True,
    )

    comment_vote_timeout_h = models.FloatField(
        null=True,
    )

    last_cycle = models.DateTimeField(
        null=True,
    )

    upvote_multiplier = models.FloatField(
        default=1.05,
    )

    upvote_multiplier_adjusted = models.FloatField(
        default=1,
    )

    last_paid_post = models.DateTimeField(
        null=True,
    )

    last_paid_comment = models.DateTimeField()

    minimum_vote_threshold = models.BigIntegerField(
        default=800000000,
    )

    last_delegation_check = models.DateTimeField(
        null=True,
    )

    comment_footer = models.TextField(
        null=True,
    )

    def __str__(self):
        return "Configuration"

    class Meta:
        verbose_name = 'configuration'
        verbose_name_plural = 'configuration'


class Member(models.Model):
    account = models.CharField(
        unique=True,
        max_length=50,
    )

    note = models.TextField(
        blank=True,
        null=True,
    )

    shares = models.PositiveIntegerField()
    bonus_shares = models.PositiveIntegerField()

    total_shares = models.PositiveBigIntegerField(
        default=0,
    )

    total_share_days = models.PositiveIntegerField(
        null=True,
    )

    avg_share_age = models.FloatField(
        null=True,
    )

    last_comment = models.DateTimeField(
        null=True,
    )

    last_post = models.DateTimeField(
        null=True,
    )

    original_enrollment = models.DateTimeField(
        null=True,
    )

    latest_enrollment = models.DateTimeField(
        null=True,
    )

    flags = models.TextField(
        blank=True,
        null=True,
    )

    earned_rshares = models.PositiveBigIntegerField(
        null=True,
    )

    subscribed_rshares = models.PositiveBigIntegerField(
        default=0,
    )

    curation_rshares = models.PositiveBigIntegerField(
        default=0,
    )

    delegation_rshares = models.PositiveBigIntegerField(
        default=0,
    )

    other_rshares = models.PositiveBigIntegerField(
        default=0,
    )

    rewarded_rshares = models.PositiveBigIntegerField(
        null=True,
    )

    pending_balance = models.FloatField(
        default=0,
    )

    estimate_rewarded = models.FloatField(
        default=0,
    )

    next_upvote_estimate = models.FloatField(
        default=0,
    )

    balance_rshares = models.BigIntegerField(
        null=True,
    )

    total_rshares = models.BigIntegerField(
        null=True,
    ) 

    upvote_delay = models.FloatField(
        null=True,
    )

    updated_at = models.DateTimeField()
    first_cycle_at = models.DateTimeField()

    last_received_vote = models.DateTimeField(
        null=True,
    )

    blacklisted = models.BooleanField(
        null=True,
    )

    hivewatchers = models.BooleanField()
    buildawhale = models.BooleanField()
    comment_upvote = models.BooleanField(default=False)

    @property
    def skiplist(self):
        if self.blacklisted:
            skiplist = True
        elif self.blacklisted is False:
            skiplist = False
        elif self.blacklisted is None:
            if self.buildawhale or self.hivewatchers:
                skiplist = True
            else:
                skiplist = False

        return skiplist

    # OLD API SUPPORT
    @property
    def username(self):
        return self.account

    @property
    def bonusShares(self):
        return self.bonus_shares

    @property
    def totalShares(self):
        return self.total_shares

    @property
    def balanceRShares(self):
        return self.balance_rshares

    @property
    def subscribedRShares(self):
        return self.subscribed_rshares

    @property
    def curationRShares(self):
        return self.curation_rshares

    @property
    def delegationRShares(self):
        return self.delegation_rshares

    @property
    def otherRShares(self):
        return self.other_rshares

    @property
    def totalRShares(self):
        return self.total_rshares

    @property
    def rewardedRShares(self):
        return self.rewarded_rshares

    @property
    def commentUpvote(self):
        return self.comment_upvote

    @property
    def estimateBalanceValue(self):
        return self.pending_balance

    @property
    def estimatedNextVote(self):
        return self.next_upvote_estimate

    @property
    def estimateRewarded(self):
        return self.estimate_rewarded

    @property
    def skiplisted(self):
        return self.skiplist

    def __str__(self):
        return self.account

    class Meta:
        verbose_name = 'member'
        verbose_name_plural = 'members'
        ordering  = ['-total_shares']


class Transaction(models.Model):
    index = models.BigIntegerField()

    source = models.CharField(
        choices=TRX_SOURCE_CHOICES,
        max_length=50,
    )

    memo = models.TextField(
        blank=True,
        null=True,
    )

    account = models.CharField(
        max_length=200,
    )

    sponsor = models.CharField(
        max_length=200,
    )

    shares = models.IntegerField(
        null=True,
    )

    vests = models.FloatField(
        null=True,
    )

    timestamp = models.DateTimeField()

    status = models.CharField(
        choices=TRX_STATUS_CHOICES,
        max_length=50,
    )

    share_type = models.CharField(
        choices=TRX_SHARE_TYPE_CHOICES,
        max_length=50,
    )

    def __str__(self):
        return "{}".format(self.index)

    class Meta:
        verbose_name = 'transaction'
        verbose_name_plural = 'transactions'
        ordering = ['-timestamp']


class Sponsee(models.Model):
    trx = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='sponsees',
        verbose_name=_('trx'),
    )

    account = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        verbose_name=_('account'),
    )

    units = models.IntegerField()

    def __str__(self):
        return "{} - {}".format(
            self.account,
            self.units,
        )

    class Meta:
        verbose_name = 'sponsee'
        verbose_name_plural = 'sponsees'
        ordering  = ['account']


class FailedTransaction(models.Model):
    trx_index = models.BigIntegerField()

    fail_type = models.PositiveSmallIntegerField(
        choices=FAILED_TRX_TYPE_CHOICES,
    )

    transaction = models.ForeignKey(
        Transaction,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('transaction'),
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    trx_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('transaction data'),
    )

    spoonse_text = models.TextField(
        blank=True,
        null=True,
    )

    is_solved = models.BooleanField(
        default=False,
    )

    status = models.CharField(
        choices=TRX_STATUS_CHOICES,
        max_length=50,
    )

    share_type = models.CharField(
        choices=TRX_SHARE_TYPE_CHOICES,
        max_length=50,
    )

    account = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    sponsor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "{}".format(self.trx_index)

    class Meta:
        verbose_name = 'failed transaction'
        verbose_name_plural = 'failed transactions'
        ordering  = ['-transaction']


class Post(models.Model):
    author = models.CharField(max_length=50)
    permlink = models.CharField(max_length=512)
    title = models.TextField()
    created = models.DateTimeField()
    vote_rshares = models.BigIntegerField()
    total_payout_value = models.FloatField()
    author_rewards = models.FloatField()
#    active_votes = models.JSONField(
        null=True,
    )

    total_rshares = models.BigIntegerField()
    empty_votes = models.BooleanField(default=False)

    has_beneficiaries = models.BooleanField(default=False)
    # TODO: Remove this field once the beneficiaries update script has finished.
    updated_beneficiaries = models.BooleanField(default=True)

    # TODO: Remove if confirm that is not used.
    beneficiaries = models.JSONField(
        null=True,
    )

    percent_hbd = models.SmallIntegerField(
        null=True,
        blank=True,
    )

    curator_payout_value = models.FloatField(
        null=True,
        blank=True,
    )

    def get_hbd_rewards(self):
        hbd_rewards = 0

        for vote in self.vote_set.all():
            hbd_rewards = hbd_rewards + vote.get_hbd_rewards()

        return hbd_rewards

    def get_hive_power_rewards(self):
        hive_power_rewards = 0

        for vote in self.vote_set.all():
            if vote.get_hive_power_rewards() is not None:
                hive_power_rewards = hive_power_rewards + vote.get_hive_power_rewards()

        return hive_power_rewards

    def __str__(self):
        return "@{}/{}".format(
            self.author,
            self.permlink,
        )

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering  = ['created']


class Vote(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('post'),
    )
    voter = models.CharField(max_length=50)
    weight = models.BigIntegerField()
    rshares = models.BigIntegerField()
    percent = models.BigIntegerField()
    reputation = models.BigIntegerField()
    time = models.DateTimeField()
    member_hist_datetime = models.DateTimeField()

    def get_hbd_rewards(self):
        if not self.rshares:
            return self.rshares

        return self.post.total_payout_value * 0.5 * (self.rshares / self.post.total_rshares)

    def get_hive_power_rewards(self):
        if not self.rshares:
            return self.rshares

        max_hive_per_mvest = MaxDailyHivePerMVest.objects.filter(
            timestamp__year=self.time.year,
            timestamp__month=self.time.month,
            timestamp__day=self.time.day,
        ).first()

        if not max_hive_per_mvest:
            return None

        hive_per_mvest = max_hive_per_mvest.hive_per_mvest

        if not hive_per_mvest:
            return hive_per_mvest

        return (self.post.author_rewards * 0.5 / hive_per_mvest) * (self.rshares / self.post.total_rshares)

    def __str__(self):
        return "{} - {}".format(
            self.voter,
            self.post,
        )

    class Meta:
        verbose_name = 'vote'
        verbose_name_plural = 'votes'
        ordering  = ['time']


class MaxDailyHivePerMVest(models.Model):
    timestamp = models.DateTimeField()
    hivesql_id = models.BigIntegerField(
        blank=True,
        null=True,
    )
    block_num = models.BigIntegerField(
        blank=True,
        null=True,)
    hive_per_mvest = models.FloatField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return "{} - {}".format(
            self.hive_per_mvest,
            self.timestamp,
        )

    class Meta:
        verbose_name = 'maximum daily Hive per mvest'
        verbose_name_plural = 'maximum daily Hive per mvest'
        ordering  = ['timestamp']


class LastSyncOlderPostOriginalEnrollment(models.Model):
    original_enrollment = models.DateTimeField()
