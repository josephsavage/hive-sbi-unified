from django.contrib import admin

from .models import (Member,
                     Configuration,
                     Transaction,
                     Sponsee,
                     FailedTransaction,
                     Post,
                     Vote,
                     MaxDailyHivePerMVest)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'updated_at',
    )

    search_fields = ['account',]

    list_filter = [
        'last_comment',
        'last_post',
        'original_enrollment',
        'latest_enrollment',
        'updated_at',
        'first_cycle_at',
        'last_received_vote',
        'blacklisted',
        'hivewatchers',
        'buildawhale',
    ]


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        'share_cycle_min',
        'sp_share_ratio',
        'rshares_per_cycle',
        'del_rshares_per_cycle',
        'comment_vote_divider',
        'comment_vote_timeout_h',
        'last_cycle',
        'upvote_multiplier',
        'upvote_multiplier_adjusted',
        'last_paid_post',
        'last_paid_comment',
        'minimum_vote_threshold',
        'last_delegation_check',
        'comment_footer',
    )


class SponseeInline(admin.TabularInline):
    model = Sponsee
    verbose_name_plural = 'sponsees'
    extra = 0


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    inlines = (SponseeInline,)

    def has_add_permission(self, request, obj=None):
        return False

    list_display = (
        'index',
        'source',
        'account',
        'sponsor',
        'shares',
        'status',
        'share_type',
        'timestamp',
    )

    search_fields = ['index',]

    list_filter = [
        'source',
        'status',
        'share_type',
    ]


@admin.register(FailedTransaction)
class FailedTransactionAdmin(admin.ModelAdmin):
#    def has_add_permission(self, request, obj=None):
#        return False

#    def has_delete_permission(self, request, obj=None):
#        return False

    list_display = (
        'id',
        'fail_type',
        'trx_index',
        'transaction',
        'status',
        'share_type',
        'account',
        'sponsor',
    )

    search_fields = ['trx_index',]

    list_filter = [
        'fail_type',
        'is_solved',
        'status',
        'share_type',
    ]

    readonly_fields = [
        # "fail_type",
        # "description",
        # "spoonse_text",
        # "trx_index",
        "transaction",
    ]


class VoteInline(admin.TabularInline):
    model = Vote
    verbose_name_plural = 'votes'
    extra = 0

    readonly_fields = [
        'voter',
        'weight',
        'rshares',
        'percent',
        'reputation',
        'post',
        #'time',
        #'member_hist_datetime',
    ]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = (VoteInline,)

    list_display = (
        'permlink',
        'author',
        'title',
        'created',
    )

    search_fields = ['author', 'permlink', 'title']

    list_filter = [
        'created',
        'empty_votes',
    ]

    readonly_fields = [
        'permlink',
        'author',
        'title',
        'created',
        'vote_rshares',
        'total_payout_value',
        'author_rewards',
        'total_rshares',
        'empty_votes',
        'percent_hbd',
        'curator_payout_value',
    ]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        'voter',
        'time',
        'member_hist_datetime',
        'post',
        'weight',
        'rshares',
        'percent',
        'reputation',
    )

    search_fields = ['post__author', 'post__permlink', 'post__title']

    list_filter = [
        'voter',
        'time',
    ]

    readonly_fields = [
        'voter',
        'weight',
        'rshares',
        'percent',
        'reputation',
        'post',
        #'time',
    ]


@admin.register(MaxDailyHivePerMVest)
class MaxDailyHivePerMVestAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'hive_per_mvest',
        'block_num',
        'hivesql_id',
    )

    readonly_fields = [
        'timestamp',
        'hive_per_mvest',
        'block_num',
        'hivesql_id',
    ]

    list_filter = [
        'timestamp',
        ("hive_per_mvest", admin.EmptyFieldListFilter),
    ]
