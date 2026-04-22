def run_incremental_elt(cursor):
    """
    Executes the incremental ELT pipeline for Steem operations using High-Water Marks.
    This must be called within an active transaction block.
    """
    
    # 1. Staging Table: Consolidate raw data incrementally with corrected column mapping
    # Legacy 'block' -> 'block_num'
    # Legacy 'type'  -> 'op_type'
    source_tables = [f"sbi{i}_ops" if i > 1 else "sbi_ops" for i in range(1, 11)]
    
    fragments = []
    for table in source_tables:
        # Match the hardcoded label logic from your original script
        label = table.replace("_ops", "")
        
        fragments.append(f"""
            SELECT '{label}', block, timestamp, type, CAST(op_dict AS JSONB) 
            FROM {table} 
            WHERE block > COALESCE((SELECT MAX(block_num) FROM steem_sbi_op_raw WHERE op_acc_name = '{label}'), 0)
        """)

    union_all_query = f"""
        INSERT INTO steem_sbi_op_raw (op_acc_name, block_num, timestamp, op_type, op_dict)
        {" UNION ALL ".join(fragments)}
    """
    
    cursor.execute(union_all_query)
    
    # 2. Domain Table: Transfer operations (References clean staging table)
    cursor.execute("""
        WITH transfer_hwm AS (
            SELECT h.op_acc_name, COALESCE((
                SELECT MAX(block_num) FROM steem_op_transfer t WHERE t.op_acc_name = h.op_acc_name
            ), 0) as max_block_num
            FROM (VALUES ('sbi'), ('sbi2'), ('sbi3'), ('sbi4'), ('sbi5'), ('sbi6'), ('sbi7'), ('sbi8'), ('sbi9'), ('sbi10')) AS h(op_acc_name)
        )
        INSERT INTO steem_op_transfer (op_acc_name, block_num, timestamp, sender, receiver, amount, memo)
        SELECT 
            r.op_acc_name,
            r.block_num,
            r.timestamp,
            r.op_dict->>'from',
            r.op_dict->>'to',
            r.op_dict->>'amount',
            r.op_dict->>'memo'
        FROM steem_sbi_op_raw r
        LEFT JOIN transfer_hwm hwm ON r.op_acc_name = hwm.op_acc_name
        WHERE r.op_type = 'transfer'
          AND r.block_num > COALESCE(hwm.max_block_num, 0);
    """)
    
    # 3. Domain Table: Vote operations (References clean staging table)
    cursor.execute("""
        WITH vote_hwm AS (
            SELECT h.op_acc_name, COALESCE((
                SELECT MAX(block_num) FROM steem_op_vote t WHERE t.op_acc_name = h.op_acc_name
            ), 0) as max_block_num
            FROM (VALUES ('sbi'), ('sbi2'), ('sbi3'), ('sbi4'), ('sbi5'), ('sbi6'), ('sbi7'), ('sbi8'), ('sbi9'), ('sbi10')) AS h(op_acc_name)
        )
        INSERT INTO steem_op_vote (op_acc_name, block_num, timestamp, voter, author, permlink, weight)
        SELECT 
            r.op_acc_name,
            r.block_num,
            r.timestamp,
            r.op_dict->>'voter',
            r.op_dict->>'author',
            r.op_dict->>'permlink',
            COALESCE(CAST(NULLIF(r.op_dict->>'weight', '') AS INTEGER), 0)
        FROM steem_sbi_op_raw r
        LEFT JOIN vote_hwm hwm ON r.op_acc_name = hwm.op_acc_name
        WHERE r.op_type = 'vote'
          AND r.block_num > COALESCE(hwm.max_block_num, 0);
    """)
