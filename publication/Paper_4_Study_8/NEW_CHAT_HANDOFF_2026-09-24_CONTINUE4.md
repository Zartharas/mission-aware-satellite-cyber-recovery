# Continue-4 Paper 4 Handoff

Date: 2026-09-24

Required next chat title:

`Continue-4 Paper-4 IJSCN Mission Aware`

## Repository state

Repository:

`Zartharas/mission-aware-satellite-cyber-recovery`

Canonical branch:

`main`

Current authoritative `main` commit after Paper 4 IJSCCN closeout:

`99209219956e7c629951775fcd12dcde70b01a55`

Merged closeout PR:

`#169 - Paper 4: close IJSCCN scope rejection and open fresh venue audit`

PR #169 is merged. Its merge commit is the current authoritative Paper 4 publication-governance state.

Project-management tracking issue for the next venue-selection gate:

`#170 - Paper 4: select next venue after IJSCCN scope rejection`

## Latest publisher decision

Journal:

**International Journal of Satellite Communications and Networking (Wiley)**

Submitted manuscript ID:

`4920969`

Submitted title:

**Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing**

Submitted:

`2026-09-22`

Decision date:

`2026-09-24`

Decision:

`REJECTED__EDITORIAL_SCREENING__OUT_OF_SCOPE__NO_EXTERNAL_REVIEW`

The decision email states that the manuscript will not be considered for publication and gives the reason:

`out of scope`

No external reviewer reports were supplied. The decision did not identify a methodological defect, statistical error, reproducibility problem, result-integrity concern, or other specific technical defect.

Decision authority:

`publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`

Machine-readable status:

`publication/Paper_4_Study_8/IJSCCN/PACKAGE_STATUS.json`

Historical final IJSCCN submission record:

`publication/Paper_4_Study_8/IJSCCN/R5_FINAL_SUBMISSION_RECORD_2026-09-22.md`

The submitted R5 IJSCCN package remains immutable historical provenance.

## Outlook / Wiley Transfer Desk state

The latest Outlook search on 2026-09-24 found no separate Wiley Transfer Desk recommendation email.

The only matching message remains:

`Decision on manuscript: 4920969`

That message says Wiley Research Publishing's Transfer Desk may send journal suggestions later.

No automatic transfer is authorized.

Do not approve any Wiley transfer without separate explicit author authorization.

## Fresh venue audit

Current venue-audit authority:

`publication/Paper_4_Study_8/NEXT_VENUE_AUDIT_2026-09-24.md`

Current candidate set for author review:

1. International Journal of Information Security
2. IEEE Systems Journal
3. Journal of Information Security and Applications
4. Aerospace
5. IEEE Access

Computers & Security is excluded from the active shortlist because its current publisher scope excludes cryptology when it is a principal component.

No new venue is locked.

The next chat should independently re-open and verify the live official journal scope/author-guideline pages before locking a venue, because journal policies can change.

## Scientific authority and boundaries

Paper 4 combines:

- Study 8 / `S8-PQC-ICR-001`
- Study 8E / `S8E-ECTV-001`

The studies remain separately governed and are never statistically pooled.

### Study 8

- 3 profiles x 4 policies x 4 regimes x 4 disruptions x 6 offsets x 3 deadlines = 3,456 deterministic positions.
- Profiles: `PROFILE_512_44`, `PROFILE_768_65`, `PROFILE_1024_87`.
- Object budgets: 12,560 / 17,460 / 24,236 bytes.
- Policies: P0 / P1 / P2 / P3.
- Every policy: 635/864 = 73.4954%.
- P3 - P1 = 0.000000 percentage points.
- Profile success: 93.7500%, 64.9306%, 61.8056%.
- Logical slots are ordering units only and have no physical-time mapping.
- Do not infer CPU, PQC runtime latency, memory, energy, thermal behavior, RF throughput, BER, coding, link margin, physical duration, ground processing, mission availability, or operational recovery time.
- `TRUST_RESTORED` is a modeled terminal state only.

### Study 8E

- Experiment: `S8E-ECTV-001`
- Corrected population: `S8E-SATNOGS-POP-002`
- Frozen trace: `S8E-SATNOGS-TRACE-002`
- 20 satellite-station pairs
- 476 frozen observation rows
- 454 eligible anchors
- Canonical cases: 65,376
- Finite thresholds: 17,640
- Non-finite: 47,736
- Finite proportion: 26.9824%
- Threshold range: 48 to 57,727 modeled bit/s
- Median threshold: 345 modeled bit/s
- 6 h: 5.2863%
- 12 h: 20.5947%
- 24 h: 55.0661%
- A0/A1: 40.5286%
- A2/A3: 13.4361%
- Each policy finite: 4,410 / 16,344
- Each profile finite: 5,880 / 21,792
- P3 vs P1 matched cases: 16,344
- Both finite: 4,410
- Both non-finite: 11,934
- Every finite P3/P1 threshold difference: 0 bit/s
- Profile-burden ordering comparisons: 21,792
- Ordering violations: 0
- Rollback/stale sums/violations: 0

Corrected scientific authority:

`S8E-CANON-RESULTS-002-FREEZE-001`

The earlier Results-001 package is invalidated and must not be used.

The corrected strict bound is:

`U_strict = floor(8B/d_min) + 1`

The prior `ceil(8B/d_min)` construction failed in exact-divisibility cases where exactly `B` modeled bytes could be delivered exactly at the horizon, violating the strict-before-horizon rule.

SatNOGS observations are observation-opportunity timing proxies only. They are not authenticated bidirectional command contacts.

Modeled bit/s values are not measured physical link capacity.

Transmitter baud is not usable throughput.

Station identity is not cryptographic trust.

TLE epoch is not cryptographic epoch.

There is no operational spacecraft-recovery validation.

## Paper 5 boundary

Paper 5 / Study 9 remains separate.

Do not import Paper 5 evidence into Paper 4.

Paper 5 concerns recovery-state semantic interoperability and downstream action identifiability. Paper 4 remains focused on cryptographic transition semantics, intermittent-contact recovery feasibility, and external observation-opportunity timing.

Architecture/non-overlap authority:

`publication/Paper_4_Study_8/PAPER4_STUDY8_8E_ARCHITECTURE_AND_NONOVERLAP_GATE_2026-09-20.md`

## Privacy and local files

Private contact metadata, the author photograph source, and personalized publisher files remain local-only.

Ignored paths:

`publication/Paper_4_Study_8/IJSCCN/_local_private/`

`publication/Paper_4_Study_8/IJSCCN/_local_submission/`

Do not commit private author metadata, photographs, or personalized publisher binaries.

The final submitted IJSCCN personalized package under the ignored local path should be retained as historical evidence and not rewritten for another venue.

## Repository-isolation rule

Paper 4 branches and publication derivatives must remain isolated from Paper 3, Paper 5, Study 7/7E, Study 9, and other unrelated research.

The next venue-specific Paper 4 branch should be created fresh from current `main` only after the author selects a target venue.

Do not reuse historical IJSCCN preparation branches or Study 8/8E scientific provenance branches as active publication-development branches.

## Immediate next-chat tasks

The next chat should:

1. Read this handoff file first.
2. Verify current `main` and issue #170.
3. Search Outlook for any new Wiley Transfer Desk recommendation received after the latest check.
4. If recommendations exist, extract them but do not authorize a transfer.
5. Re-open the official live scope and author-instruction pages for the current venue candidates.
6. Compare candidate fit against the actual Paper 4 claim/evidence boundaries.
7. Consider publication model, page/word limits, manuscript type, figure requirements, APC/open-access requirements, peer-review model, data/AI disclosures, and submission mechanics.
8. Select a target only after author review.
9. Do not rerun Study 8 or Study 8E to improve publication prospects.
10. Do not create a new venue-specific manuscript derivative until a venue is selected.
11. Any future final publisher submission or Wiley transfer requires separate explicit author authorization.

## Copy-paste prompt for the new chat

Start a new chat and name it exactly:

`Continue-4 Paper-4 IJSCN Mission Aware`

Then paste:

> Continue Paper 4 from the repository handoff after the IJSCCN editorial scope rejection. Work only on Paper 4 unless a cross-paper boundary check is required. First read `publication/Paper_4_Study_8/NEW_CHAT_HANDOFF_2026-09-24_CONTINUE4.md`, `publication/Paper_4_Study_8/IJSCCN/R5_IJSCCN_EDITORIAL_DECISION_2026-09-24.md`, `publication/Paper_4_Study_8/NEXT_VENUE_AUDIT_2026-09-24.md`, `publication/Paper_4_Study_8/IJSCCN/PACKAGE_STATUS.json`, and GitHub issue #170. Verify current `main` before doing anything else.
>
> IJSCCN manuscript 4920969 was submitted on 2026-09-22 and rejected at editorial screening on 2026-09-24 as `out of scope`. No external reviewer reports or specific technical/methodological defects were supplied. Treat the submitted IJSCCN R5 package as immutable historical provenance. Do not rerun or alter Study 8 or Study 8E because of this decision.
>
> First search my connected Outlook for any Wiley Transfer Desk recommendation that arrived after the latest check. If one exists, review it as a candidate only. Do not approve or execute a transfer.
>
> Then perform a fresh live official-source venue-fit and author-guideline validation for the active candidates recorded in `NEXT_VENUE_AUDIT_2026-09-24.md`: International Journal of Information Security, IEEE Systems Journal, Journal of Information Security and Applications, Aerospace, and IEEE Access. Recheck all official scope and submission-policy pages rather than relying only on the prior audit. Computers & Security was excluded because cryptology is a principal component of Paper 4 and its publisher scope currently excludes cryptology as a principal component.
>
> Paper 4 combines Study 8 / S8-PQC-ICR-001 and Study 8E / S8E-ECTV-001, but the populations remain separate and must never be pooled. Study 8 remains the 3,456-position deterministic modeled population. Study 8E remains frozen under S8E-CANON-RESULTS-002-FREEZE-001 with 65,376 canonical cases, 17,640 finite, 47,736 non-finite, threshold range 48-57,727 modeled bit/s, median 345 modeled bit/s, and all matched finite P3/P1 threshold differences equal to 0 bit/s. Results-001 is invalidated and must not be used.
>
> Preserve all claim boundaries: logical slots are not physical time; SatNOGS observations are not authenticated/bidirectional command contacts; modeled bit/s is not measured physical link capacity; transmitter baud is not usable throughput; station identity is not cryptographic trust; TLE epoch is not cryptographic epoch; no CPU, PQC latency, RF, BER, link margin, energy, thermal, operational recovery time, mission availability, or flight-performance claims are supported.
>
> Keep Paper 5 / Study 9 completely separate. Use `publication/Paper_4_Study_8/PAPER4_STUDY8_8E_ARCHITECTURE_AND_NONOVERLAP_GATE_2026-09-20.md` as the cross-paper boundary authority.
>
> The immediate goal is to select the next venue based on actual scope fit and submission requirements, not to change the science. Do not create a new venue-specific manuscript derivative until I approve the venue selection. Any Wiley transfer or final publisher submission requires separate explicit authorization.
