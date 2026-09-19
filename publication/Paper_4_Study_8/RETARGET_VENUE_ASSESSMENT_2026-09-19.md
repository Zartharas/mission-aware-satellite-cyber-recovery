# Study 8 Retarget Venue Assessment

**Assessment date:** 2026-09-19  
**Study:** `S8-PQC-ICR-001`  
**Roadmap publication label:** Paper 4  
**Status:** `IJSCCN_RECOMMENDED__SPECIFIC_VENUE_LOCK_PENDING`

## Decision question

Which current journal is the strongest fit for a revised Study 8 manuscript without changing the frozen science?

The assessment prioritizes topical fit, the paper's actual evidence type, current scope language, recent topical precedent, reproducibility expectations, and desk-review risk. It does not predict acceptance.

## Primary recommendation: International Journal of Satellite Communications and Networking

**Recommendation:** strongest current retarget candidate.

Official current scope states that the journal covers the theory, practice, and operation of satellite systems and networks, including satellite communications, satellite networks/networking, planning and operations, performance analysis, interoperability, standards/regulation, and network protocols. It explicitly requires a satellite component.

Live sources checked:

- https://onlinelibrary.wiley.com/page/journal/15420981/homepage/productinformation.html
- https://onlinelibrary.wiley.com/page/journal/15420981/homepage/forauthors.html

### Why Study 8 fits

The revised paper can be presented truthfully as a satellite-network transition feasibility study:

- intermittent satellite contact is an explicit modeled input;
- finite contact byte opportunities interact with standardized PQ cryptographic objects;
- logical deadlines determine whether a multi-step transition reaches the trusted terminal state;
- transition policy changes network/state resource use and acceptance-state exposure even when terminal success is unchanged;
- the model is reproducible and its data/code are publicly auditable.

This aligns more directly with network protocols, performance analysis, and satellite systems than the broader astronautics framing used for Acta.

### Topical precedent

The journal published:

T. Ghosh and I. Nath, "Secure Satellite Communication in the Post-Quantum Era: A Lattice-Based Cryptographic Approach," International Journal of Satellite Communications and Networking, vol. 44, no. 5, pp. 524-543, 2026. DOI: 10.1002/sat.70041.

That precedent confirms satellite PQC is within scope. It also raises the novelty bar, so Study 8 must be differentiated from algorithm/performance comparison. Its defensible distinction is post-compromise transition feasibility and state-cost decomposition under intermittent contact, not another generic PQC-for-satellites analysis.

### Current submission requirements relevant to the revision

The current author instructions provide:

- Research Exchange submission;
- free-format initial submission;
- editable manuscript file;
- abstract up to 250 words;
- up to eight keywords;
- required data-availability statement;
- expectation that supporting data and, where possible, scripts/artifacts are publicly archived;
- required graphical table of contents with figure and no more than 80 words or three sentences;
- numbered references in final journal style;
- no page charge.

The existing public repository and frozen provenance are therefore an asset rather than an obstacle.

Wiley's current AI policy requires transparent disclosure when generative AI is used to develop any portion of a manuscript. The retarget package must adapt the existing truthful disclosure to Wiley's current policy.

## Secondary candidate: IEEE Systems Journal

IEEE Systems Journal has attractive thematic language around modeling, simulation, mission assurance, reliability, availability, communications, security, standards, and complex cyber-physical systems.

However, its current scope also explicitly says that papers focused on one single system or one specific network component are out of scope, and that pure cryptography without communication-network impact is out of scope.

Live sources checked:

- https://ieeesystemscouncil.org/publication/ieee-systems-journal
- https://ieeesystemscouncil.org/publication/ieee-systems-journal/instructions-for-authors

**Risk:** Study 8 is a deliberately bounded transition/state-machine model. Reframing it as a systems-of-systems paper merely to satisfy scope would risk overstating what was modeled.

**Disposition:** retain as a secondary candidate, not the preferred next submission.

## Additional fallback: International Journal of Communication Systems

The current Wiley scope welcomes communication-system work on network protocols, system control/management, modeling/simulation, and performance evaluation.

Live source checked:

- https://onlinelibrary.wiley.com/page/journal/10991131/homepage/productinformation.html

It is broader and less satellite-specific than IJSCCN, so it is a fallback rather than the first retarget.

## Why not immediately return to an aerospace-general venue

The Acta rejection did not identify a specific scope defect, but the submitted Study 8 evidence deliberately excludes orbital geometry, RF/link behavior, spacecraft processor measurements, energy/thermal behavior, and operational mission validation.

A satellite-network journal can evaluate the model on the dimensions it actually contains rather than expecting a broader spacecraft/astronautics evidence layer.

## Recommendation

Proceed with **International Journal of Satellite Communications and Networking** as the primary retarget candidate, subject to explicit author confirmation of the named venue.

Do not submit the unchanged Acta manuscript.

Before a new package is frozen:

1. revise the contribution hierarchy around feasibility versus transition-state cost;
2. rewrite title and abstract;
3. tighten Introduction and Discussion;
4. expand and verify the directly relevant literature;
5. add a graphical TOC designed from existing frozen concepts/results without fabricating new data;
6. ensure a Wiley-compliant AI-use disclosure;
7. preserve all frozen counts, null findings, and claim boundaries;
8. run an independent publication-layer traceability audit against the frozen Study 8 records.

Final publisher submission remains separately gated and is not authorized by this assessment.
