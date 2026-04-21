from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SteemSbiOpRaw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('op_acc_name', models.CharField(db_index=True, help_text='The account name to differentiate the 10 source tables (e.g., sbi, sbi2)', max_length=50)),
                ('block_num', models.BigIntegerField()),
                ('timestamp', models.DateTimeField()),
                ('op_type', models.CharField(db_index=True, max_length=50)),
                ('op_dict', models.JSONField(help_text='The raw operation payload stored as JSONB')),
            ],
            options={
                'verbose_name': 'Steem SBI Raw Operation',
                'verbose_name_plural': 'Steem SBI Raw Operations',
                'db_table': 'steem_sbi_op_raw',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='SteemOpTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('op_acc_name', models.CharField(db_index=True, max_length=50)),
                ('block_num', models.BigIntegerField()),
                ('timestamp', models.DateTimeField()),
                ('sender', models.CharField(max_length=50)),
                ('receiver', models.CharField(max_length=50)),
                ('amount', models.CharField(max_length=50)),
                ('memo', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'steem_op_transfer',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='SteemOpVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('op_acc_name', models.CharField(db_index=True, max_length=50)),
                ('block_num', models.BigIntegerField()),
                ('timestamp', models.DateTimeField()),
                ('voter', models.CharField(max_length=50)),
                ('author', models.CharField(max_length=50)),
                ('permlink', models.CharField(max_length=512)),
                ('weight', models.IntegerField()),
            ],
            options={
                'db_table': 'steem_op_vote',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='steemsbiopraw',
            index=models.Index(fields=['op_acc_name'], name='steem_op_acc_idx'),
        ),
        migrations.AddIndex(
            model_name='steemsbiopraw',
            index=models.Index(fields=['block_num'], name='steem_block_num_idx'),
        ),
    ]
