# Study 4 canonical findings — S4-MPQ-001

**Status:** `CANONICAL_RESULTS_FROZEN_PENDING_REPOSITORY_MERGE`  
**Design merge:** `b33e409b77b5e9c257979b0d3dc0d5ea8feb0925`  
**Canonical execution:** `42b64a7a6431f2130efceec389ce25fe9b1a2382`  
**Workflow / job:** `33658900540` / `100344267677`  
**Artifact:** `9857848543`  
**Artifact ZIP SHA-256:** `09f20ecfd90baf739c4a3226631fddb4b5279779094d9c75a2ddd90f6f6b285e`

The canonical population contains 18 quorum/provenance rules evaluated against all 128 producer-compromise subsets and all 128 honest-producer-unavailability subsets: 4,608 exact observations. No random sampling or operational frequency model is used.

## Findings

1. **Absolute vote count sets the basic compromise threshold; provenance diversity changes which subsets can cross it.** With `Q2_D1`, any two compromised producers are sufficient and every two-producer subset fails. Requiring two provenance domains (`Q2_D2`) does not change the first possible failure count (2), but moves systematic safety failure from 2 to 4 compromised producers because same-domain pairs no longer qualify.

2. **Stronger provenance diversity can materially delay systematic unsafe qualification.** For `Q3_D1`, three compromised producers are both the first and systematic safety failure. For `Q3_D3`, a three-producer compromise can fail only when it spans all three domains, while systematic failure does not occur until six of seven producers are compromised. The same pattern appears at `Q4_D3` and `Q5_D3`, whose systematic safety-failure threshold is six producers.

3. **The safety gain is purchased with an availability cost.** `Q3_D1` first becomes false-conservative only after five producers are unavailable. `Q3_D3` can become false-conservative after only two unavailable producers if domain diversity is lost, although systematic availability failure still occurs at five. `Q4_D3` similarly has an availability first-failure count of two versus four for `Q4_D1`.

4. **A simple majority-style threshold gives a symmetric boundary only without added provenance constraints.** `Q4_D1` first and systematically fails for safety at four compromised producers and first/systematically fails for availability at four unavailable producers. Adding `D3` retains safety first-failure at four but delays systematic unsafe qualification to six, while availability can first fail at two unavailable producers.

5. **High vote thresholds improve compromise tolerance but sharply reduce loss tolerance.** `Q5_D1` requires five compromised producers for unsafe qualification but becomes false-conservative after three unavailable producers. At `Q6`, safety failure requires six compromised producers while availability failure begins at two unavailable producers; `Q7` requires all seven compromised producers for unsafe qualification but rejects recovery after any single producer becomes unavailable.

6. **No single rule dominates both objectives.** The exact finite grid exposes a safety/availability frontier rather than a globally best quorum. Provenance diversity is most useful when common-domain compromise is a meaningful concern, but it must be justified against the corresponding risk of losing an entire provenance domain through benign unavailability.

## Interpretation boundary

This experiment studies a recovery-evidence qualification gate, not distributed Byzantine consensus, leader election, network agreement, or sensor-estimation accuracy. The provenance domains are synthetic independence classes; they do not establish real organizational, hardware, software, or supply-chain independence. The 128 subsets per block are an exhaustive combinatorial state space and must not be interpreted as probabilities of compromise or outage in operational missions. Studies 1–3 remain frozen and are not pooled with Study 4.
