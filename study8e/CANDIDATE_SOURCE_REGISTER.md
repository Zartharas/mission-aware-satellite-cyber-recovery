# Study 8E Candidate Source Register

**Experiment:** `S8E-ECTV-001`  
**Verification date:** 2026-09-19  
**Status:** `CANDIDATE_SOURCES_DEFINED__NO_EXTERNAL_DATA_ROWS_ACCESSED`

## Selection principle

Sources are selected for complementary evidence roles before Study 8E endpoints are inspected. Candidate-source inclusion is based on public accessibility, stable provenance, field semantics, legal/reuse terms, and relevance to external contact timing or clearly bounded sensitivity analysis.

Source selection must not depend on whether a source makes a Study 8 result look stronger, weaker, statistically attractive, or publication-friendly.

## Source A: SatNOGS Network

**Planned role:** primary external contact-window source.

Current documentation establishes that the Network API provides observation records with source `start` and `end` datetimes, ground-station identifier, NORAD catalog identifier, observation status, station metadata, transmitter metadata including baud, and TLE fields. SatNOGS states that API access is open and API data are distributed under CC BY-SA.

Verification sources:

- https://librespacefoundation.gitlab.io/satnogs/satnogs-network/api.html
- https://librespacefoundation.gitlab.io/-/satnogs/satnogs-network/-/jobs/1380080108/artifacts/satnogs-network-api-client/html2/index.html
- https://network.satnogs.org/about/

### Primary semantic use

Only `id`, `start`, `end`, `ground_station`, and `norad_cat_id` are permitted to construct the primary timing trace.

Other fields may be retained for provenance or descriptive stratification but may not be converted into missing cryptographic or mission semantics.

### Frozen planned window

`2026-06-01T00:00:00Z <= start < 2026-07-01T00:00:00Z`

### Population-selection rule

The unit is one `norad_cat_id x ground_station` trace.

A pair must contain at least 20 observations in the source window. Qualifying pairs are ranked by ascending SHA-256 of:

`SATNOGS|<norad_cat_id>|<ground_station>`

The canonical candidate population will contain at most 32 trace pairs, with at most two pairs per NORAD catalog identifier and at most two per ground station. Selection may use only identifiers, counts, date-window membership, and record-validity checks. It may not inspect duration, gaps, clustering, status outcome, baud, or any recovery endpoint before the selected population is frozen.

If fewer than 32 pairs qualify under these rules, all qualifying pairs satisfying the caps are retained.

### Invalid source records

A record with nonparseable/missing start/end or `end <= start` is not repaired. It is accounted for in the source-validation report and excluded from contact arithmetic under the predeclared invalid-window rule.

## Source B: ESA OPS-SAT-1 re-entry UHF telemetry

**Planned role:** secondary dependent reception-density/gap sensitivity evidence.

ESA documents a UHF telemetry dataset from 2024-05-01 through 2024-05-22, collected during OPS-SAT-1's final mission period with participation from the amateur-radio community and SatNOGS.

Verification source:

- https://live.opssat.esa.int/ops-sat-1/docs/tm_analysis.html

The source is **not independent of SatNOGS in provenance** and must never be counted as a separate independent replication of SatNOGS timing findings.

Because the public telemetry table is reception timestamp oriented rather than an explicit authenticated command-window schedule, Study 8E will not infer uplink/contact capacity from it.

If later admitted, reception episodes are reported under all three predeclared gap sensitivities: 300, 600, and 900 seconds. No single threshold may be chosen after inspecting which produces a preferred recovery result.

## Source C: LENS

**Planned role:** secondary LEO-network physical sensitivity evidence only.

The public LENS repository describes a Starlink measurement dataset originally published in the ACM MMSys 2024 Open-Source Software and Dataset track. The current project also documents newer measurements, including Starlink dish gRPC metrics from late 2025 onward.

Verification source:

- https://github.com/clarkzjw/LENS

LENS may later support a separately frozen throughput/latency sensitivity layer. It must not be represented as spacecraft TT&C or as the capacity of a SatNOGS/OPS-SAT contact.

No LENS archive is selected or downloaded by this protocol phase.

## Source D: NASA HDTN

**Planned role:** future implementation harness, not a dataset.

NASA describes the High-rate Delay Tolerant Networking Network Operations Release as supporting BPv7, LTP, Contact Graph Routing, dynamic contact-plan updates, and other DTN capabilities, with flight demonstrations.

Verification sources:

- https://software.nasa.gov/software/LEW-19897-2
- https://www.nasa.gov/technology/space-comms/delay-disruption-tolerant-networking-mission-resources/

HDTN may be used only in a separately authorized implementation-validation layer after the external trace evidence has its own freeze. It is not a source of empirical contact availability for Study 8E.

## Candidate-source admission gate

Before any canonical Study 8E execution, every admitted source must have:

1. a stable source/version/API extraction identity;
2. license/reuse terms recorded;
3. exact extraction query/window recorded;
4. byte hash(es) for materialized artifacts;
5. schema and type validation;
6. invalid-record accounting;
7. provenance and dependence assessment;
8. field-to-endpoint semantic mapping frozen;
9. no endpoint values inspected before population and mapping freeze;
10. independent audit path specified.

Any source that cannot satisfy the gate is excluded rather than repaired into compliance.
