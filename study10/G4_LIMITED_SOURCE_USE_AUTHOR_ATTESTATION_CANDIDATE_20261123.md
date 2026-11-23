# Study 10 — limited source-use author attestation candidate (NOT SIGNED)

**Study:** S10-RSEI-001, standalone research paper / Paper 5  
**Status:** `CANDIDATE_FOR_EXPLICIT_AUTHOR_APPROVAL; NO_SOURCE_USE_CLEARANCE`  
**Date drafted:** 2026-11-23 UTC  
**Controlling authority:** `B_FREEZE_DESIGN_WITH_SOURCE_USE_HOLD`, immutable receipt `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json`, Git blob SHA-1 `38e5da5edc193b358012bc9c2c3180917d7419ac`.

## Evidence-based limited-use eligibility decision

The public rights evidence supports **narrow local academic research use under the stated dataset-level public licenses**; it does not establish permission for separately held third-party rights or prove that any file lacks uninspected notices.

| Dataset and exact version | Public license basis | Author-requested prospective study scope | Current right-to-use gate |
| --- | --- | --- | --- |
| ESA Anomaly Dataset **v2**, DOI `10.5281/zenodo.15237121`, exact three Mission1/2/3 ZIPs | **CC BY 3.0 IGO**, v2-linked project dataset metadata plus author license declaration | Three primary, **within-source-family descriptive** mission strata; local, offline classification only after separate G4-06 authorization | `G4-01=HOLD` pending explicit source-specific member-rights disposition and internal author signoff |
| ESA Anomaly Dataset **v1**, DOI `10.5281/zenodo.12528696` | **CC BY 3.0 IGO**, pinned official ESA repository LICENSE/README linking the exact v1 DOI | Optional RQ-E3 **paired** `(mission, channel, metadata field)` release sensitivity only; no fifth primary stratum or replication claim | `G4-02=HOLD_IF_USED` |
| OPS-SAT-AD **v2**, DOI `10.5281/zenodo.15108715`, only `dataset.csv`, `segments.csv` and `LICENSE` from the frozen intake | **MIT License for OPS-SAT Dataset**, `Copyright (c) 2024 KP Labs`, expressly covering data | Fourth primary, distinct descriptive source-family stratum; local, offline; no raw telemetry redistribution | `G4-03=HOLD` |

**Review limitations:** V2 sanitized JSON hash independently verified `3b8af9e18722aee475fcc871503ac3ff39137e81ff2fb9e57fbf3dcf4de51adb`; V3 sanitized report hash **author-reported only** `0e12647f3c6437f196ae92f53e237f6a8fa85f705a79519c842e91c0598085d8`. Together they support **26 of 26 bounded leading CSV preambles inspected** with no recognized rights markers in those scanned prefixes. Neither original data members beyond the preambles nor all embedded third-party terms have been reviewed. A zero-marker count is **not** a finding that no exceptions exist.

The prospective public license terms support local reuse of covered material, subject to applicable copyright and other legal conditions. They are **not third-party permission grants** for any separately owned material. A positive, new contradictory member-specific license or restriction requires stopping and reassessment before continuing the affected source's use. If the frozen file-specific rights signoff threshold is not satisfied by an evidence-supported case-specific disposition, the gate stays closed; assent alone is not a waiver.

## Exact proposed author attestation (approval required)

The following is the **candidate statement** to be either accepted or rejected explicitly by the sole author. No assistant may fill in a signature, timestamp of assent, or affirmative approval until the author actually confirms this **specific text**.

> I approve the limited, local, offline, non-redistributing scholarly source-use scope described above for **ESA Anomaly Dataset v2 (DOI 10.5281/zenodo.15237121)**, **ESA Anomaly Dataset v1 (DOI 10.5281/zenodo.12528696) only as optional paired sensitivity**, and **OPS-SAT-AD v2 (DOI 10.5281/zenodo.15108715)**, strictly under the identified source-specific public licenses.
>
> I understand that the bounded rights inspection found no recognized license markers in the inspected 26 leading CSV preambles, but that uninspected in-band material, independently owned content, and third-party restrictions are **unknown, not certified absent**. I accept the documented residual uncertainty for purposes of making an **internal, limited-use eligibility determination**, insofar as the publicly stated license covers the relevant material. This acceptance neither creates third-party permissions nor overrides any actual restrictive notices or the frozen Option B signoff conditions.
>
> I will preserve the version-specific **CC BY 3.0 IGO** attribution, license URI, modification and non-endorsement conditions for ESA, and the **data-inclusive MIT** terms for OPS-SAT, including `Copyright (c) 2024 KP Labs` and the complete required copyright and permission notice if copies or substantial portions of the covered material are later included in an authorized distribution. I will not redistribute original raw telemetry and will require a separate sensitivity, privacy, reconstructability and journal-compliance review before releasing any derived results.
>
> If a source file introduces a newly identified conflicting term, identifiable third-party restriction or sensitive operational content inconsistent with this limited-use plan, I will **stop processing the affected source** and obtain a proper evidence-based disposition before proceeding.
>
> This is **not** permission for G4-06 scientific source-semantic execution, merged pull requests, data redistribution, publication/submission or contacting rights holders. Those actions require separate authorization. This statement does **not** amend the frozen G2/G3 research protocol.

### Required author response for this exact candidate

The author must approve the **quoted source-use attestation itself**, not merely authorize a further review. A sufficiently unambiguous response would be: **“I approve the G4 limited source-use attestation for ESA v2, optional ESA v1, and OPS-SAT v2, including its stated residual uncertainty and stop conditions. I do not authorize G4-06.”**

Once expressly approved, record the exact response, date/UTC and Git blob identity in a **new additive author-decision record**; then evaluate which pre-G4 file-rights gates are actually satisfied and which remain blocked by a specific missing requirement. Do **not** silently flip any gate to cleared merely because an author accepted unknowns. If the frozen file-member exception signoff requirement still cannot be met, stop or separately propose an explicitly prospective policy change without changing the frozen receipt.

## Non-negotiable separation

The intended paper includes **four primary descriptive strata × eight variables = 32 prospective classification slots**; ESA v1 is optional paired sensitivity, not a fifth independent stratum. Positive results cannot justify a retrospective source choice or policy change. Before any scientific processing, a new explicit `G4-06` author authorization is required **after** all applicable mandatory rights and notice gates. All GitHub PRs remain draft and unmerged, and prospective manuscript notices remain drafts until the research is genuinely performed and each actual final artifact is checked.

**Current disposition:** `LICENSE_LEVEL_ELIGIBILITY_SUPPORTED; FINAL_FILE_SCOPE_AUTHOR_ATTESTATION_NOT_YET_APPROVED; G4-06_NOT_AUTHORIZED`.

This is an evidence-based research-governance record, not legal advice or a grant from a dataset rights holder.
