# Instructions

## Step 1: Technical Documentation
Validate the relevant .github/docs/*.md files for the current session and make update recommendations.
Technical documentation should make explicit which code files each piece lives in so they can be easily referenced to build appropriate context.
Prompt for acceptance of documentation updates before moving on to Step 2 

## Step 2: Generate a Session Handover Summary for our next chat.
Append the generated summary to the bottom of this file (`.github/docs/gemini_summaries.md`) under a new heading with an incremental session ID (e.g., `## Session 1`).

Please include:
Logic Implemented: Specific functions or logic flows we finished.
The 'Hanging Thread': Exactly where we stopped (e.g., 'The function is written but not yet imported into the worker').
Architectural Decisions: Why we chose a specific approach (to prevent me from suggesting a different one next time).
The Next Immediate Step: The very first thing I should do when I 'wake up' in the next session.

# Summaries

## Session 1
**Logic Implemented:** We successfully diagnosed and resolved a series of cascading PostgreSQL connection failures.
1.  Fixed the PostgreSQL service on the host machine, which was failing to start.
2.  Corrected a port mismatch between the application's `.env` configuration and the actual running port of the PostgreSQL server.
3.  Resolved a `Connection refused` error by updating `pg_hba.conf` to allow connections from Docker's dynamic internal network.

**The 'Hanging Thread':** All systems are now operational. The immediate troubleshooting is complete.

**Architectural Decisions:** To prevent future connection issues from Docker, we configured `pg_hba.conf` to authorize the entire default Docker subnet (`172.17.0.0/16`) rather than a single, ephemeral IP address. This makes the local development setup more robust.

**The Next Immediate Step:** Verify all services are running without errors by checking their logs, and then continue with the planned development work.

## Session 2
**Logic Implemented:** Built the complete ELT pipeline to migrate legacy Steem data from remote MariaDB to PostgreSQL.
1.  Created a parameterized `pgloader` script (`steem_ops.load`) to mirror the 10 raw `sbi_ops` tables into Postgres.
2.  Built a new Django `steem` app containing staging (`SteemSbiOpRaw`) and domain (`SteemOpTransfer`, `SteemOpVote`) models.
3.  Wrote a custom Postgres `RunSQL` migration (`0002_elt_transform_ops.py`) that consolidates the 10 tables and executes fast JSON -> relational data extraction.
4.  Patched `Dockerfile` to run `dos2unix` on boot scripts, resolving `\r` (CRLF) crash errors.
5.  Fixed legacy `admin.py` system check errors preventing migrations.

**The 'Hanging Thread':** The local environment is configured with SSH tunneling to test the ELT process. The next goal is to deploy these changes to production where the extraction will run at gigabit speeds, and then sync the resulting transformed tables back to the local database.

**Architectural Decisions:** 
- Avoided putting staging consolidation logic inside `pgloader` because its parser is overly sensitive to complex SQL options mixed with `LOAD DATABASE`. Instead, we let `pgloader` do a fast, dumb 1:1 table dump, and moved all consolidation (`UNION ALL`) and extraction logic into a robust Postgres native SQL migration.
- Fully parameterized the `pgloader` script using `.env` variables so it works seamlessly across dev (with SSH tunnels) and bare-metal production without code changes.

**The Next Immediate Step:** Open a PR with the generated `walkthrough.md` deployment instructions, deploy to the production server, execute the pgloader/migration scripts, and confirm data populates successfully.
## Session 3
**Logic Implemented:** Addressed the 4 critical issues identified in the code review of PR 61 (Steem ELT Pipeline).
1. Deleted the risky `0002_elt_transform_ops.py` migration and extracted its raw SQL logic into a new, safely triggerable Django management command (`run_steem_elt.py`).
2. Hardened the raw SQL JSON extraction logic using `COALESCE(CAST(NULLIF(op_dict->>'weight', '') AS INTEGER), 0)` to prevent transaction crashes on legacy records with empty/null weights.
3. Updated the `docker-compose.yml` `api` service to explicitly wait for `postgres` to become `service_healthy` to eliminate boot race conditions.
4. Parameterized the target Postgres host in `pgloader_scripts/steem_ops.load` so it dynamically resolves based on `.env` context (WSL native vs. Docker).
5. Initialized `.github/docs/document_guide.md` and added `.github/docs/steem_elt.md` to establish our new documentation standards.
6. Merged improved operational rules into `GEMINI.md` to harden the workflow.

**The 'Hanging Thread':** The ELT pipeline is now fully refactored for safety and idempotency. The actual automated integration tests for this pipeline were explicitly deferred due to the infrastructure overhead of mocking MariaDB inside standard test suites.

**Architectural Decisions:** 
- Moved ELT execution strictly out of Django's automated migration system into a manual command (`run_steem_elt`) because schema migrations should not depend on external data pipelines (`pgloader`) completing first.
- Decided against writing Python-level tests for `run_steem_elt.py` because testing it correctly requires an end-to-end integration test with a seeded MariaDB container, which is outside the current scope.

**The Next Immediate Step:** Merge PR 61 if ready, or pull down the changes to test the pipeline natively against the remote MariaDB before production deployment.

## Session 4
**Logic Implemented:** Critical refactoring of the PR 61 Steem ELT pipeline to align with core architectural rules:
1.  Extracted ELT SQL execution from the management command into the domain layer (`steem/domain/elt.py`) to satisfy the "Fat Domains" rule.
2.  Wrapped the execution in `run_steem_elt.py` inside a single `transaction.atomic()` block, shifting database commits safely to the top-level worker.
3.  Replaced `TRUNCATE` idempotency with a High-Water Mark (`MAX(block_num)`) incremental load approach, allowing the script to run seamlessly on a schedule.
4.  Created a Django migration adding `block_num` indexes to domain tables for fast incremental lookups.
5.  Updated `steem_elt.md` to formally document the exception for deferring tests until initial data patterns are analyzed.

**The 'Hanging Thread':** The codebase is now fully compliant with the stricter development pattern introduced in PR 61. The incremental logic is ready to execute either an initial full load or a scheduled delta run.

**Architectural Decisions:** 
- Chosen a single database transaction for the incremental load instead of application-level batching. Since `INSERT INTO ... SELECT ...` executes entirely inside the Postgres engine, batching in Python is unnecessary and would break atomicity.
- Deployed a High-Water Mark approach for idempotency to seamlessly support both the initial bulk load and all future scheduled fetches without configuration changes.

**The Next Immediate Step:** Verify that `python manage.py run_steem_elt` correctly runs the incremental pipeline. If it passes successfully against the remote/test data, merge PR 61 and deploy.
