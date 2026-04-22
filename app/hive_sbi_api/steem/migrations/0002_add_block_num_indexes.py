# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('steem', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='steemsbiopraw',
            name='op_acc_name',
            field=models.CharField(help_text='The account name to differentiate the 10 source tables (e.g., sbi, sbi2)', max_length=50),
        ),
        migrations.AlterField(
            model_name='steemoptransfer',
            name='op_acc_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='steemopvote',
            name='op_acc_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AddIndex(
            model_name='steemoptransfer',
            index=models.Index(fields=['op_acc_name', 'block_num'], name='steem_transf_acc_block_idx'),
        ),
        migrations.AddIndex(
            model_name='steemopvote',
            index=models.Index(fields=['op_acc_name', 'block_num'], name='steem_vote_acc_block_idx'),
        ),
        migrations.RemoveIndex(
            model_name='steemsbiopraw',
            name='steem_op_acc_idx',
        ),
        migrations.RemoveIndex(
            model_name='steemsbiopraw',
            name='steem_block_num_idx',
        ),
        migrations.AddIndex(
            model_name='steemsbiopraw',
            index=models.Index(fields=['op_acc_name', 'block_num'], name='steem_raw_acc_block_idx'),
        ),
    ]
