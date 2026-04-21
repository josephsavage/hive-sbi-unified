# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('steem', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='steemoptransfer',
            index=models.Index(fields=['block_num'], name='steem_transf_block_idx'),
        ),
        migrations.AddIndex(
            model_name='steemopvote',
            index=models.Index(fields=['block_num'], name='steem_vote_block_idx'),
        ),
    ]
