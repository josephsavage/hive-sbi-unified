from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('steem', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            TRUNCATE TABLE steem_sbi_op_raw;
            
            INSERT INTO steem_sbi_op_raw (op_acc_name, block_num, timestamp, op_type, op_dict)
            SELECT 'sbi', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi_ops
            UNION ALL SELECT 'sbi2', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi2_ops
            UNION ALL SELECT 'sbi3', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi3_ops
            UNION ALL SELECT 'sbi4', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi4_ops
            UNION ALL SELECT 'sbi5', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi5_ops
            UNION ALL SELECT 'sbi6', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi6_ops
            UNION ALL SELECT 'sbi7', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi7_ops
            UNION ALL SELECT 'sbi8', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi8_ops
            UNION ALL SELECT 'sbi9', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi9_ops
            UNION ALL SELECT 'sbi10', block_num, timestamp, op_type, CAST(op_dict AS JSONB) FROM sbi10_ops;
            """,
            reverse_sql="TRUNCATE TABLE steem_sbi_op_raw;"
        ),
        migrations.RunSQL(
            sql="""
            INSERT INTO steem_op_transfer (op_acc_name, block_num, timestamp, sender, receiver, amount, memo)
            SELECT 
                op_acc_name,
                block_num,
                timestamp,
                op_dict->>'from',
                op_dict->>'to',
                op_dict->>'amount',
                op_dict->>'memo'
            FROM steem_sbi_op_raw
            WHERE op_type = 'transfer';
            """,
            reverse_sql="TRUNCATE TABLE steem_op_transfer;"
        ),
        migrations.RunSQL(
            sql="""
            INSERT INTO steem_op_vote (op_acc_name, block_num, timestamp, voter, author, permlink, weight)
            SELECT 
                op_acc_name,
                block_num,
                timestamp,
                op_dict->>'voter',
                op_dict->>'author',
                op_dict->>'permlink',
                CAST(op_dict->>'weight' AS INTEGER)
            FROM steem_sbi_op_raw
            WHERE op_type = 'vote';
            """,
            reverse_sql="TRUNCATE TABLE steem_op_vote;"
        ),
    ]
