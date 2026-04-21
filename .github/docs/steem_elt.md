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
*   **Models Involved:** `SteemSbiOpRaw`, `SteemOpTransfer`, `SteemOpVote` (found in `app/hive_sbi_api/steem/models.py`)
*   **Action:** Once `pgloader` completes, this command is executed manually (`python manage.py run_steem_elt`). It uses raw SQL to:
    1. Truncate destination tables for idempotency.
    2. Consolidate the 10 raw tables into a single staging table (`steem_sbi_op_raw`).
    3. Extract specific JSON payloads into strongly-typed domain tables (`steem_op_transfer`, `steem_op_vote`).
*   **Safety Features:** Includes `COALESCE(CAST(NULLIF(..., ''))) AS INTEGER` protection to prevent the entire transaction from aborting if a legacy payload contains empty strings where an integer is expected.

## Testing Strategy
Integration tests for this pipeline are deliberately deferred. Because `run_steem_elt.py` depends on data populated by the external `pgloader` tool connecting to a live MariaDB instance, mocking the entire flow inside the standard Django test suite is impractical and introduces unnecessary infrastructure overhead. The pipeline is validated manually during deployment.
