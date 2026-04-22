from django.db import models
from django.utils.translation import gettext_lazy as _

class SteemSbiOpRaw(models.Model):
    """
    Staging table for raw operations extracted from the legacy MariaDB database.
    This consolidates the 10 legacy sbi_ops tables.
    """
    op_acc_name = models.CharField(
        max_length=50,
        help_text=_("The account name to differentiate the 10 source tables (e.g., sbi, sbi2)"),
    )
    block_num = models.BigIntegerField()
    timestamp = models.DateTimeField()
    op_type = models.CharField(max_length=50, db_index=True)
    op_dict = models.JSONField(
        help_text=_("The raw operation payload stored as JSONB"),
    )

    class Meta:
        db_table = 'steem_sbi_op_raw'
        verbose_name = 'Steem SBI Raw Operation'
        verbose_name_plural = 'Steem SBI Raw Operations'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['op_acc_name', 'block_num'], name='steem_raw_acc_block_idx'),
        ]

    def __str__(self):
        return f"{self.op_acc_name} - {self.op_type} - {self.block_num}"

class SteemOpTransfer(models.Model):
    """
    Transformed domain model for 'transfer' operations.
    """
    op_acc_name = models.CharField(max_length=50)
    block_num = models.BigIntegerField()
    timestamp = models.DateTimeField()
    
    sender = models.CharField(max_length=50) # Maps to json 'from'
    receiver = models.CharField(max_length=50) # Maps to json 'to'
    amount = models.CharField(max_length=50)
    memo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'steem_op_transfer'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['op_acc_name', 'block_num'], name='steem_transf_acc_block_idx'),
        ]


    def __str__(self):
        return f"Transfer {self.amount} from {self.sender} to {self.receiver}"

class SteemOpVote(models.Model):
    """
    Transformed domain model for 'vote' operations.
    """
    op_acc_name = models.CharField(max_length=50)
    block_num = models.BigIntegerField()
    timestamp = models.DateTimeField()
    
    voter = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    permlink = models.CharField(max_length=512)
    weight = models.IntegerField()

    class Meta:
        db_table = 'steem_op_vote'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['op_acc_name', 'block_num'], name='steem_vote_acc_block_idx'),
        ]


    def __str__(self):
        return f"Vote {self.weight} by {self.voter} on {self.author}/{self.permlink}"
