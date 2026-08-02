# Reportable Findings Register

## Opening Statement

No confirmed third-party vulnerability has been established as of this
revision. Entries in this register must distinguish internal prototype
defects from independently validated upstream or third-party defects.
Nothing in this register authorizes external disclosure.

## Purpose

This is an internal research record maintained for bugs, defects, security
findings, upstream issue candidates, and responsible-disclosure candidates
discovered during the remaining research work.

Creating an entry does NOT authorize a public GitHub issue, an upstream pull
request, a vendor report, a CERT report, a CVE request, contact with an
authority, public disclosure, or publication of exploit details. All
external disclosure requires separate review and explicit user approval.

## Classifications

- INTERNAL_FIX
- UPSTREAM_ISSUE_CANDIDATE
- RESPONSIBLE_DISCLOSURE_CANDIDATE
- RESEARCH_OBSERVATION
- NOT_REPORTABLE

## Finding Fields

Each finding must contain:

- Finding ID
- discovery date
- activity or checkpoint
- component
- component owner
- concise summary
- supporting evidence or reproduction reference
- observed impact
- affected version or commit
- classification
- disclosure sensitivity
- fix or mitigation
- commit, issue, PR, or report reference
- validation status
- current disposition

## Finding Identifiers

Findings use the form `RF-YYYY-NNN`, for example `RF-2026-001`.

An RF entry is added only when a concrete defect or defensible research
observation is supported by evidence. Entries are not created merely to
populate the register.

## Activities

### RF-ACT-001

- Activity: WP4 Checkpoint 2PB2B-A — Synthetic Outer-Transaction Engine
- Start date: 2026-07-31
- Status: COMPLETED_FINDINGS_RECORDED
- Finding count: 15
- Note: The activity begins with no predetermined reportable finding.
  Findings will be recorded only when supported by reproducible evidence and
  will not be treated as third-party vulnerabilities without independent
  upstream validation. Earlier prototype defects are not backfilled during
  this checkpoint.

### RF-ACT-002

- Activity: WP4 Checkpoints 2PB2B-B1 through B1R3 — Canonical Materialization-Plan Compiler and Independent-Review Corrections
- Start date: 2026-08-01
- Status: COMPLETED_FINDINGS_RECORDED
- Finding count: 5
- Note: Activity covers Checkpoints 2PB2B-B1, B1R1, B1R2, and B1R3. Findings are
  internal prototype corrections only; no third-party vulnerability claim.

## Findings

### RF-2026-001

- **Finding ID:** RF-2026-001
- **Discovery date:** 2026-07-31
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_validate_absolute_authorized_root` descriptor lifecycle
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** The strict authorized-root opener opened an initial `/` directory descriptor during descriptor-relative traversal but, on the success path, closed only `parents[1:-1]` and never closed `parents[0]` (the `/` descriptor).  Each successful synthetic transaction therefore leaked one file descriptor (+1 per transaction), which accumulated and would raise `EMFILE` under repeated use.
- **Supporting evidence or reproduction reference:** Repeated `run_synthetic_outer_transaction` calls under temporary authorized roots showed `FD_DELTA_SUCCESS = +20` across 20 transactions (exactly +1 each).  Self-tests `repeated_successful_synthetic_transactions_do_not_leak_fds` and `repeated_failed_synthetic_transactions_do_not_leak_fds` initially returned `False`; several `publication_failure_cleans_stage` / file-creation tests initially raised `OSError(24, 'Too many open files')`.
- **Observed impact:** Descriptor exhaustion under repeated transactions; not a confidentiality, integrity, or availability vulnerability of any third-party component.  Pure internal descriptor-lifecycle defect in the prototype transaction tool.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Refactored `_validate_absolute_authorized_root` so every opened descriptor has one explicit owner; each previous traversal descriptor is closed as ownership advances, all still-owned descriptors close on rejection, and only the successfully returned final descriptor remains open.
- **Commit, issue, PR, or report reference:** None.  Corrected in-tree during Checkpoint 2PB2B-A.  No external issue or PR opened.
- **Validation status:** Validated by the current in-tree self-test suite and the standalone descriptor-leak deltas (success and repeated failure deltas both 0).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-002

- **Finding ID:** RF-2026-002
- **Discovery date:** 2026-07-31
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_desc_rmtree` descriptor-relative staging cleanup
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** `_desc_rmtree` contained a non-terminating directory-list loop and failed to close the opened subdirectory descriptor on its successful path.
- **Supporting evidence or reproduction reference:** The Checkpoint 2PB2B-A self-test hung in `pre_publication_fsync_failure_cleans_stage`; the traceback identified the loop in `_desc_rmtree`; direct source inspection established that `os.listdir(sub_fd)` returned successfully inside a `while True` with no `break`, and `sub_fd` was not closed on the successful path.
- **Observed impact:** Cleanup could hang indefinitely and retain a descriptor, preventing bounded failure cleanup of a staging tree.
- **Affected version or commit:** Pre-fix Checkpoint 2PB2B-A working-tree implementation of `scripts/nos3_runtime_transaction_v1.py` (prior to this R1 correction).
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Replaced the non-terminating loop with one bounded directory enumeration, recursively remove validated entries, and close `sub_fd` exactly once on the successful path.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the in-tree self-test suite (`pre_publication_fsync_failure_cleans_stage_before_publish`) and the standalone descriptor-leak deltas (success and repeated failure deltas both 0).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-003

- **Finding ID:** RF-2026-003
- **Discovery date:** 2026-07-31
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_create_synthetic_tree` and `_write_canonical_receipt` synthetic tree and receipt construction
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** `_create_synthetic_tree` retained intermediate and regular-file descriptors, and `_write_canonical_receipt` failed to close its receipt descriptor.
- **Supporting evidence or reproduction reference:** Self-tests initially failed with `OSError` errno 24 (`Too many open files`); source inspection identified unclosed intermediate-directory, regular-file, and receipt descriptors retained across one transaction.
- **Observed impact:** Repeated transactions exhausted the process descriptor limit and produced `EMFILE`.
- **Affected version or commit:** Pre-fix Checkpoint 2PB2B-A working-tree implementation of `scripts/nos3_runtime_transaction_v1.py` (prior to this R1 correction).
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Close every intermediate and regular-file descriptor immediately after its validated use and close the receipt descriptor in all paths.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the in-tree self-test suite (`repeated_successful_synthetic_transactions_do_not_leak_fds`, `repeated_failed_synthetic_transactions_do_not_leak_fds`) and the standalone descriptor-leak deltas (success and repeated failure deltas both 0).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-004

- **Finding ID:** RF-2026-004
- **Discovery date:** 2026-07-31
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — fault-injection test controls
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Fault hooks used truthiness checks such as `inject.get("file_write_failure")`, while test hook values were empty dictionaries.  The hooks were therefore skipped and transactions succeeded instead of exercising the intended failure paths.
- **Supporting evidence or reproduction reference:** An isolated file-write-failure run completed successfully and left the injection dictionary unchanged; replacing truthiness with explicit key-membership checks caused the intended hook to execute.
- **Observed impact:** Negative tests could report misleading behavior without reaching their named failure point.
- **Affected version or commit:** Pre-fix Checkpoint 2PB2B-A working-tree implementation of `scripts/nos3_runtime_transaction_v1.py` (prior to this R1 correction).
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Use exact key-membership checks (`"<hook>" in inject`) and require every fault test's injection counter to equal exactly one.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the in-tree self-test suite (all fault tests assert their intended injection counter equals exactly one and the publication call count).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-005

- **Finding ID:** RF-2026-005
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_validate_absolute_authorized_root` first-component rejection
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Early authorized-root first-component failures leaked the initial `/` descriptor opened at the start of the descriptor-relative traversal, because the rejection paths did not close the opened root descriptor.
- **Supporting evidence or reproduction reference:** A missing first-component rejection, a symlink first-component rejection, a non-directory first-component rejection, a first-component lstat failure, and a first opened-component fstat failure each initially left an open descriptor; the repeated missing-first-component run leaked descriptors.  After the refactor, every rejection path closes all owned descriptors and the repeated failure descriptor delta is zero.
- **Observed impact:** Descriptor leak on authorized-root rejection paths under repeated failures; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Refactored `_validate_absolute_authorized_root` so every opened descriptor has exactly one owner; the initial `/` descriptor and every intermediate descriptor are closed on every rejection or exception, and only the successfully returned final authorized-root descriptor remains open.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (authroot missing/symlink/non-dir/lstat/fstat rejection tests with descriptor delta zero; one-component and multi-component traversal success; 25-call repeated failure aggregate descriptor delta zero).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-006

- **Finding ID:** RF-2026-006
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_make_staging_dir` staging-directory creation
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Staging `mkdir` followed by `open` or `fstat` failure could leave an orphan staging directory and an open descriptor, because the failure paths did not roll back the newly created directory.
- **Supporting evidence or reproduction reference:** A staging open failure and a staging fstat failure initially left a hidden `.nrm-v3-stage-*` directory in the authorized root and an open descriptor.  After the refactor, both failures remove the exact newly created directory and leave zero orphans and descriptor delta zero.
- **Observed impact:** Orphan staging directories and descriptors on staging creation failure; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Refactored `_make_staging_dir` to be internally transactional: once `mkdir` succeeds the staging basename is retained, and on open/fstat/identity/mode failure the exact directory is removed via `root_fd`; on rollback failure both the creation failure and the rollback failure are reported.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (staging open/fstat/identity/mode failure tests: orphan count zero, descriptor delta zero, unrelated siblings preserved; rollback-rmdir failure reports the combined failure).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-007

- **Finding ID:** RF-2026-007
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_fd_listdir` and `_fsync_staged_hierarchy`
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** `_fd_listdir` converted enumeration errors (unsupported fd `TypeError` and every `OSError`) into an empty directory, and the staged-fsync traversal lacked opened-directory identity continuity.
- **Supporting evidence or reproduction reference:** A `listdir` EIO and an unsupported-fd `TypeError` initially returned an empty list and let publication proceed.  After the refactor, both raise `_TransactionClosed`, and the staged-fsync traversal verifies lstat-to-fstat identity for every opened child directory.
- **Observed impact:** Enumeration errors could be mistaken for an empty directory and allow publication of an incompletely fsynced tree; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** `_fd_listdir` converts unsupported fd enumeration and every `OSError` into `_TransactionClosed` and returns a deterministic sorted tuple; `_fsync_staged_hierarchy` uses descriptor-relative no-follow traversal with lstat-to-fstat continuity, closes every child descriptor once, and fsyncs children before their parent.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (listdir EIO/TypeError rejection, child open/fstat/identity/fsync failure rejection; publication_calls=0 and staging removed in each case).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-008

- **Finding ID:** RF-2026-008
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — transaction-level failure cleanup
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Transaction-level cleanup failures were silently suppressed with `contextlib.suppress(_TransactionClosed)`, allowing an orphan staging tree while reporting only the primary failure.
- **Supporting evidence or reproduction reference:** A primary file-write failure combined with a cleanup `rmdir` failure initially re-raised only the primary failure and left the staging tree in place without reporting the cleanup failure.  After the refactor, a controlled combined failure reports both failures and does not claim the staging tree was removed.
- **Observed impact:** False clean disposition and orphan staging trees on cleanup failure; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Removed `contextlib.suppress(_TransactionClosed)`; on primary pre-publication failure, cleanup is attempted once and, on cleanup failure, a single controlled combined failure containing the primary, cleanup, and staging basename is raised without removing `final_basename` and without `KeyboardInterrupt`/`SystemExit` conversion.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (file-write + cleanup failure, pre-publication-fsync + cleanup failure, symlink rejection during transaction failure, enumeration failure during transaction failure; exact cleanup-hit counters and no false clean disposition).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-009

- **Finding ID:** RF-2026-009
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_atomic_noreplace_publish` Linux support
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Linux `renameat2(RENAME_NOREPLACE)` atomic publication was documented but not implemented; only the macOS `renameatx_np(RENAME_EXCL)` path existed.
- **Supporting evidence or reproduction reference:** Source inspection of `_atomic_noreplace_publish` showed a macOS-only `renameatx_np` branch and no `renameat2` path for Linux.  After the refactor, a Linux `renameat2` branch with `RENAME_NOREPLACE = 1`, exact ctypes argument/return types, and `errno` handling is present.
- **Observed impact:** Atomic no-replace publication was unavailable on Linux; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Implemented Linux `renameat2(RENAME_NOREPLACE = 1)` through ctypes with exact argument/return types and `errno` handling; `EEXIST` preserves the existing destination; the unsupported primitive fails closed; no ordinary rename fallback.  `macOS renameatx_np(RENAME_EXCL=0x4)` is preserved, and the receipt `publication_method` matches the selected platform primitive.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (isolated fake-libc tests: Linux success invokes `renameat2` once with flag 1; Linux EEXIST fails closed; Linux missing-symbol fails closed; macOS path invokes `renameatx_np` once with flag 4; no ordinary rename fallback).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-010

- **Finding ID:** RF-2026-010
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — self-test integrity
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Self-test integrity defects: an unconditional missing-component pass (`or True`), non-mutating component tests that did not exercise plan validation, a post-complete-write "mid-write" hook rather than a genuine mid-file write, and an `os.popen` process invocation missed by the source scan.
- **Supporting evidence or reproduction reference:** The `missing_component_rejected` test contained `... or True` and always passed; component tests inspected the plan only; the file-write injection fired after the complete write completed; and `external_nos3_never_modified` invoked `os.popen`.  After the refactor, malformed-plan tests reject genuinely, the mid-file write fires inside the complete-write loop, `os.popen` is removed, and an AST scan covers `os.popen`/`os.system`/`os.spawn*`/`os.fork`/`os.exec*`/`subprocess`/`pty`.
- **Observed impact:** Self-tests could pass without exercising their named failure points; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Added `_validate_synthetic_plan` with exact type/ID/mode/path checks; replaced tautological tests with genuine malformed-plan tests (missing/duplicate/unexpected component, wrong record type, mutable file list, path traversal, cross-component workspace path, duplicate file path); moved the mid-file-write injection into `_complete_write` after at least one byte and before the total; removed `os.popen`; added a process-invocation AST scan; updated the module header to state the synthetic engine is implemented and production authorization/canonical NOS3 materialization/runtime authorization are not.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (malformed-plan rejections, mid-file `bytes_written>=1`/`<total_bytes`/`fsync_calls=0`/`publication_calls=0`, `OS_POPEN_PRESENT=false`, `PROCESS_INVOCATION_PATHS=[]`).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-011

- **Finding ID:** RF-2026-011
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — filesystem absence checks
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Filesystem absence checks accepted arbitrary `OSError` values as proof of absence instead of only `errno.ENOENT`.
- **Supporting evidence or reproduction reference:** `_validate_final_basename` and the post-publication stage absence check used `except OSError: return/pass`; an `EACCES` or `EIO` lstat was therefore treated as "absent".  After the refactor, only `errno.ENOENT` proves absence and every other `OSError` fails closed.
- **Observed impact:** Permission or I/O errors could be mistaken for absence and allow an unsafe operation to proceed; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Made every absence check errno-precise: `_validate_final_basename` returns only on `errno.ENOENT`, the post-publication stage check accepts only `errno.ENOENT`, and every other `OSError` raises `_TransactionClosed`.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (final-basename lstat EACCES/EIO rejected; post-publication stage lstat EACCES/EIO rejected without treating the object as absent).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-012

- **Finding ID:** RF-2026-012
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — fsync fault self-tests
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** The child-directory open/fstat/identity self-tests activated their fault wrappers during authorized-root traversal or synthetic-tree construction instead of only while `_fsync_staged_hierarchy` was executing.
- **Supporting evidence or reproduction reference:** The three fsync fault tests initially recorded faults during `_create_synthetic_tree` file creation rather than the staged-hierarchy pass.  After the refactor, phase-guarded wrappers set a phase flag only while the original `_fsync_staged_hierarchy` runs, so faults inject exclusively during the hierarchy phase.
- **Observed impact:** Self-tests could exercise the wrong code path and report misleading pass behavior; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A-R2 working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Each fsync fault test wraps `_fsync_staged_hierarchy` with a phase guard that sets `phase["active"] = True` immediately before invoking the original function and resets it in `finally`; `os.open`/`os.fstat` fault wrappers do nothing unless the phase is active.  The identity-mismatch test changes `st_ino` or `st_dev` while preserving `st_mode` exactly, so the test requires the exact `staged identity discontinuity` rejection and does not accept `staged opened object not a directory`.  Tests prove the intended counter is exactly one and assert marker + cleanup + fd-delta + restored monkeypatches.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (identity fault requires the exact `staged identity discontinuity` rejection, changing `st_ino`/`st_dev` while preserving `st_mode`; open/fstat fault counters exactly one, publication_calls=0, final absent, staging removed, fd delta zero, phases restore in finally).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-013

- **Finding ID:** RF-2026-013
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — cleanup-symlink rejection self-test
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** The cleanup-symlink test claimed symlink injection but created no symlink and validated only the primary write failure.
- **Supporting evidence or reproduction reference:** The test reported only `injected mid-file-write failure` and never created a symlink; `_desc_rmtree` symlink rejection was never reached.  After the refactor, the test wraps `_create_synthetic_tree` to create a `cleanup-symlink-probe` symlink inside the staging root, raises a primary failure, and verifies the combined failure contains `primary`, `cleanup failed`, `symlink rejected`, and the staging basename.
- **Observed impact:** Self-test passed without exercising the symlink-rejection cleanup path; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A-R2 working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Wrapped `_create_synthetic_tree` to materialize the real tree, create a symlink probe via `dir_fd=stage_fd`, increment a creation counter exactly once, and raise a primary failure; cleanup runs normally, the combined exception reports both failures plus the symlink rejection, staging remains because cleanup correctly refused the symlink, and the wrapper is restored in `finally`.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (symlink creation hits exactly 1, combined failure contains all required tokens, final absent, staging remains, fd delta zero).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-014

- **Finding ID:** RF-2026-014
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_validate_synthetic_plan`
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Synthetic-plan validation accepted bytearray content, component files under `fortytwo-config`, and leafless workspace-root paths.
- **Supporting evidence or reproduction reference:** A bytearray file content, a component file rooted under `fortytwo-config`, and a workspace path equal only to `workspaces/<cid>/work/nos3` all passed validation.  After the refactor, bytes-only is exact, component files under `fortytwo-config` are rejected, workspace paths require a leaf after `nos3`, and `fortytwo-config` without a component is rejected.
- **Observed impact:** Malformed synthetic plans could pass validation and stage unexpected layouts; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A-R2 working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Required `type(sf.content) is bytes` exactly (no bytearray conversion), forbade component files under `fortytwo-config`, required `len(comps) >= 5` for workspace paths (leaf after `nos3`), and required `fortytwo-config/<component>` with `len(comps) >= 2`.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (bytearray content, component-in-fortytwo, workspace-root-without-leaf, fortytwo-root-without-leaf each rejected by `_validate_synthetic_plan`).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-015

- **Finding ID:** RF-2026-015
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-001 — WP4 Checkpoint 2PB2B-A-R2R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_fsync_staged_hierarchy` object-type coverage
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Staged-hierarchy verification skipped unsupported non-directory filesystem objects such as FIFOs by treating every non-directory, non-symlink entry as already fsynced.
- **Supporting evidence or reproduction reference:** A FIFO placed in a staging tree was silently skipped during `_fsync_staged_hierarchy` rather than rejected.  After the refactor, only directories and regular files are handled; symlinks, FIFOs, sockets, block devices, character devices, and any unclassified mode are rejected.
- **Observed impact:** Unsupported staged objects could pass durability verification; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-A-R2 working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Replaced the skip-all-non-directory branch with explicit per-type handling: symlink reject, directory open/verify/recurse/fsync, regular file allow, and FIFO/socket/block/character/unclassified reject.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (portable FIFO fixture inside a staging tree invokes `_fsync_staged_hierarchy` directly, rejects with `staged FIFO rejected`, reaches the FIFO path, fd delta zero).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.
### RF-2026-016

- **Finding ID:** RF-2026-016
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-002 — WP4 Checkpoint 2PB2B-B1
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_build_canonical_materialization_plan`
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** The compiler calculated file/directory and regular-file-prefix collisions but returned plans containing nonzero collision counts instead of failing closed.
- **Supporting evidence or reproduction reference:** Reproduced by file_directory_collision_rejected, file_prefix_ancestor_collision_rejected, and exclusion_included_target_collision_rejected, plus the compact direct collision probes that force a cFS directory onto an included file relative_path, two sim_bin files as probe/probe/child, and an exclusion identity onto an included file source_root and relative_path.
- **Observed impact:** A malformed plan could be returned carrying ambiguous or structurally unsafe transaction destinations rather than failing closed at the compiler boundary; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-B1 working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Rewrote the collision model to build deterministic checks from immutable expanded-target records and raise _TransactionClosed before returning a plan whenever a duplicate regular-file, directory, or exclusion target; a regular-file/directory/exclusion equality; a regular-file prefix ancestor of another file, directory, or exclusion; or an exclusion prefix ancestor of an included file or directory occurs.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by self-test probes that force a file/directory collision, a file-prefix ancestor collision (probe / probe/child), and an exclusion/included collision; each reaches the compiler and raises _TransactionClosed without returning a nonzero collision count.
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.
### RF-2026-017

- **Finding ID:** RF-2026-017
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-002 — WP4 Checkpoint 2PB2B-B1
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_build_canonical_materialization_plan`
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** The compiler accepted a non-octal exclusion mode, regular-file mode 0700, and an empty exclusion relative path.
- **Supporting evidence or reproduction reference:** Reproduced by regular_file_mode_0700_rejected, exclusion_mode_non_octal_rejected, exclusion_mode_unapproved_rejected, and exclusion_empty_relative_path_rejected, plus the corresponding compact probes that mutate mode/path metadata in deep copies of the parsed canonical manifest.
- **Observed impact:** Malformed mode/path metadata could cross the compiler boundary and weaken deterministic materialization validation; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-B1 working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Restricted regular-file modes to exactly 0644 and 0755 (rejecting 0700); restricted exclusion modes to the canonical exclusion modes 0644 and 0700; required every mode to be an exact 4-character ASCII-octal string; and required every exclusion relative_path to be a nonempty canonical relative path.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by self-test rejection of regular-file mode 0700, exclusion mode zzzz, exclusion mode 0777, and an empty exclusion relative path; each reaches _build_canonical_materialization_plan and raises _TransactionClosed.
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.
### RF-2026-018

- **Finding ID:** RF-2026-018
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-002 — WP4 Checkpoint 2PB2B-B1
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_build_canonical_materialization_plan`
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** Workspace and Fortytwo plans retained source-relative entries without immutable expanded transaction targets, and the Fortytwo root directory sentinel was modeled as fortytwo-config/ rather than fortytwo-config/cfg/build/InOut.
- **Supporting evidence or reproduction reference:** Reproduced by fortytwo_expanded_targets_exact, workspace_expanded_targets_exact, and expanded_target_counts_exact, plus the compact plan target-identity and Fortytwo sentinel probe asserting fortytwo-config/cfg/build/InOut.
- **Observed impact:** The absence of immutable transaction-relative target identities prevented complete downstream collision, namespace, and audit binding; not a third-party vulnerability.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-B1 working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Added the _CanonicalExpandedTarget record and immutable file/directory/exclusion target tuples to every workspace plan, every Fortytwo plan, and aggregate target tuples to the complete plan; required all transaction-relative target paths to be canonical/relative with dot/dotdot/repeated-separator/backslash/NUL/surrogate/leading-or-trailing-separator rejection; and modeled the Fortytwo root directory sentinel as fortytwo-config/cfg/build/InOut.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by self-test probes asserting exact workspace expanded target counts (1786/120/43), exact Fortytwo target counts (36/1/0), the fortytwo-config/cfg/build/InOut sentinel, owner-namespace escape rejection, and expanded total target counts (1822/121/43).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-019

- **Finding ID:** RF-2026-019
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-002 — WP4 Checkpoint 2PB2B-B1R2
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — `_is_exact_int`, `_is_exact_str`, and the deep-immutability checker
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** The compiler and its deep-immutability checker used isinstance for integer and string validation, allowing int and str subclasses despite the exact primitive-only plan contract.
- **Supporting evidence or reproduction reference:** Reproduced by exact_int_subclass_rejected, regular_file_mode_str_subclass_rejected, relative_path_str_subclass_rejected, and deep_immutability_rejects_scalar_subclasses, plus compact direct probes of `_is_exact_int`/`_is_exact_str` confirming rejection of int/str subclasses.
- **Observed impact:** A direct Python caller could provide scalar subclasses that crossed the compiler boundary and were retained in a plan that was reported as deeply immutable, violating the exact primitive-type contract. The canonical JSON-loaded manifest was not shown to contain such subclasses.
- **Affected version or commit:** Intermediate pre-fix Checkpoint 2PB2B-B1R2 working-tree implementation; no committed or retained pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record.  No external disclosure.
- **Fix or mitigation:** Changed `_is_exact_int` to require `type(value) is int`; added `_is_exact_str` requiring `type(value) is str`; updated `_is_hex64` and both canonical path helpers to require exact str; applied exact-string and exact-int checks throughout compiler-retained scalar fields; corrected the deep-immutability checks to accept only exact `None`/`bool`/`int`/`str` scalars; and added focused scalar-subclass rejection tests.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the self-test suite (exact int/str subclass rejection across nlink, size, mode, and relative_path; deep-immutability returns false for int and str subclasses; all 178 prior tests preserved).
- **Current disposition:** CLOSED — defect corrected and validated.  Retained as an INTERNAL_FIX record only; not shared externally.

### RF-2026-020

- **Finding ID:** RF-2026-020
- **Discovery date:** 2026-08-01
- **Activity or checkpoint:** RF-ACT-002 — WP4 Checkpoint 2PB2B-B1R3 independent-review correction
- **Component:** `scripts/nos3_runtime_transaction_v1.py` — current-contract self-test fixture and assertions
- **Component owner:** WP4 transaction tool (internal prototype)
- **Concise summary:** The current-contract self-test fixture supplied `/dev/null` as the candidate, which is outside the repository root. The transaction therefore could close during candidate-path validation before opening and validating the current contract, while four tests accepted only the generic closed marker and return code.
- **Supporting evidence or reproduction reference:** Independent review showed that the original fixture returned `V3_TRANSACTION_AUTHORIZATION=CLOSED` without asserting its internal reason. A focused probe using a valid repository-local regular-file candidate reached structured contract validation and returned the exact reason `v3 static verification not PASS`, with the nonexistent authorized root remaining absent.
- **Observed impact:** The implementation remained fail-closed and no authorized root, staging tree, materialization, Docker path, or runtime attempt was reached. However, the affected self-tests overstated what they proved because an earlier candidate-path rejection could satisfy their assertions without validating the current contract.
- **Affected version or commit:** Intermediate Checkpoint 2PB2B-B1R2 working-tree implementation; no committed pre-fix SHA was assigned.
- **Classification:** INTERNAL_FIX
- **Disclosure sensitivity:** Internal research record. No external disclosure.
- **Fix or mitigation:** Replaced `/dev/null` with the repository-local transaction-tool file as the fixture candidate; added an exact helper requiring `rc=1`, the exact closed marker, and the exact contract-derived reason `v3 static verification not PASS`; strengthened all four current-contract tests to use that helper; and added a regression test proving that the fixture candidate is a repository-local, single-link regular file before requiring the contract-derived rejection.
- **Commit, issue, PR, or report reference:** Not assigned — working-tree correction; no external report.
- **Validation status:** Validated by the complete self-test suite: 183 passed, 0 failed, and 0 skipped. The strengthened current-contract tests reached structured contract validation, closed specifically at `v3 static verification not PASS`, and confirmed that the authorized root remained absent.
- **Current disposition:** CLOSED — defect corrected and validated. Retained as an INTERNAL_FIX record only; not shared externally.
