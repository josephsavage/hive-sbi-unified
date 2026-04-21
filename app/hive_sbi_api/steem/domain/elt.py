def run_incremental_elt(cursor):
    """
    Executes the incremental ELT pipeline for Steem operations using High-Water Marks.
    This must be called within an active transaction block.
    """
    # 1. Staging Table: Consolidate raw data incrementally
    cursor.execute("""
        INSERT INTO steem_sbi_op_raw (op_acc_name, block_num, timestamp, op_type, op_dict)
        SELECT 'sbi', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi'), 0)
        UNION ALL 
        SELECT 'sbi2', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi2_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi2'), 0)
        UNION ALL 
        SELECT 'sbi3', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi3_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi3'), 0)
        UNION ALL 
        SELECT 'sbi4', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi4_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi4'), 0)
        UNION ALL 
        SELECT 'sbi5', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi5_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi5'), 0)
        UNION ALL 
        SELECT 'sbi6', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi6_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi6'), 0)
        UNION ALL 
        SELECT 'sbi7', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi7_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi7'), 0)
        UNION ALL 
        SELECT 'sbi8', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi8_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi8'), 0)
        UNION ALL 
        SELECT 'sbi9', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi9_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi9'), 0)
        UNION ALL 
        SELECT 'sbi10', block_num, timestamp, op_type, CAST(op_dict AS JSONB) 
        FROM sbi10_ops 
        WHERE block_num > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = 'sbi10'), 0);
    """)
    
    # 2. Domain Table: Transfer operations
    cursor.execute("""
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
        WHERE op_type = 'transfer'
          AND block_num > COALESCE((SELECT MAX(block_num) FROM steem_op_transfer), 0);
    """)
    
    # 3. Domain Table: Vote operations
    cursor.execute("""
        INSERT INTO steem_op_vote (op_acc_name, block_num, timestamp, voter, author, permlink, weight)
        SELECT 
            op_acc_name,
            block_num,
            timestamp,
            op_dict->>'voter',
            op_dict->>'author',
            op_dict->>'permlink',
            COALESCE(CAST(NULLIF(op_dict->>'weight', '') AS INTEGER), 0)
        FROM steem_sbi_op_raw
        WHERE op_type = 'vote'
          AND block_num > COALESCE((SELECT MAX(block_num) FROM steem_op_vote), 0);
    """)
