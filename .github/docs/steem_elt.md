# Steem ELT Pipeline

This document describes the Extract, Load, Transform (ELT) pipeline used to migrate legacy Steem operational data from an external MariaDB database into our primary PostgreSQL database.

## Architecture & Workflow

The migration process is split into two explicit, manual steps to avoid deployment bottlenecks and race conditions:

### 1. Data Extraction (MariaDB -> PostgreSQL)
*   **Tool:** `pgloader`
*   **Script:** `pgloader_scripts/steem_ops.load`
*   **Action:** This script connects to the legacy MariaDB and performs a 1:1 raw data dump of the 10 legacy tables (`sbi_ops` through `sbi10_ops`) directly into the `public` schema of the PostgreSQL database.
*   **Context:** This runs incredibly fast but requires the database host parameters to be correctly mapped in the `.env` file (`POSTGRES_HOST`, `POSTGRES_PORT`).

### 2. Data Transformation (Django Management Command)
*   **Tool:** Django Management Command
*   **Script:** `app/hive_sbi_api/steem/management/commands/run_steem_elt.py`
*   **Domain Logic:** `app/hive_sbi_api/steem/domain/elt.py`
*   **Models Involved:** `SteemSbiOpRaw`, `SteemOpTransfer`, `SteemOpVote` (found in `app/hive_sbi_api/steem/models.py`)
*   **Action:** Once `pgloader` completes, this command is executed (`python manage.py run_steem_elt`). It calls domain logic (`steem.domain.elt.run_incremental_elt`) wrapped in a transaction to:
    1. Consolidate the 10 raw tables into a single staging table (`steem_sbi_op_raw`) using a partitioned high-water mark approach (`MAX(block_num)` grouped by account name) to avoid skipping lagging sources.
    2. Extract specific JSON payloads into strongly-typed domain tables (`steem_op_transfer`, `steem_op_vote`) incrementally. This strictly uses `VALUES` lateral subqueries (targeting exactly the 10 legacy accounts) to fetch high-water marks in O(1) time, avoiding catastrophic O(M) `GROUP BY` full-index scans over multi-million row domain tables. Furthermore, single-column `db_index` attributes are strictly avoided in favor of the single composite index (`op_acc_name`, `block_num`) to reduce disk usage and maximize `INSERT` performance.
*   **Safety Features:** Includes `COALESCE(CAST(NULLIF(..., ''))) AS INTEGER` protection to prevent the entire transaction from aborting if a legacy payload contains empty strings where an integer is expected. Executed in a single atomic database transaction to prevent partial loads.

## Testing Strategy
Integration tests for the initial ELT pipeline load are deliberately deferred. Because the data patterns of the legacy JSON payloads are not fully known until the initial load is complete, mocking the data effectively upfront is impractical. Once the initial load provides the data patterns, regression tests will be built to prevent breaking changes on future releases and ensure the incremental loads remain stable.
