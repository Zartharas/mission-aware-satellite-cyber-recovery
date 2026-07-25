# Public Data and Software Source Register

## Policy

Third-party data and source code must not be copied into this repository unless redistribution is explicitly permitted and the license obligations are documented. Prefer download scripts, persistent identifiers, hashes, and pinned upstream references.

## Approved or conditionally approved sources

### NASA cFS

- Type: Open-source flight software framework
- Repository: https://github.com/nasa/cFS
- License: Apache License 2.0 for the open-source bundle
- Intended use: Flight-software and command/telemetry baseline
- Restrictions: NASA states that lab applications are examples and the bundle is not a verified operational flight distribution
- Repository treatment: Pin upstream commit; do not imply NASA endorsement

### NASA NOS3

- Type: Software-only spacecraft simulation environment
- Repository: https://github.com/nasa/nos3
- License: NASA Open Source Agreement 1.3
- Intended use: Digital-twin infrastructure, mission-state simulation, command and telemetry
- Restrictions: Preserve license and modification notices; review export notice and all third-party component licenses
- Repository treatment: Use an upstream checkout/submodule or installer; do not copy source into this repository

### ESA Anomaly Dataset

- Type: Real satellite telemetry with curated anomaly annotations
- DOI: 10.5281/zenodo.12528696
- License: CC BY 3.0 IGO
- Intended use: Calibrate telemetry missingness, anomaly duration, and operational data characteristics
- Limitation: Anomalies are not automatically cyberattacks and must not be relabeled without support
- Repository treatment: Do not redistribute raw data; store DOI, citation, license, and local checksum

### OPSSAT-AD

- Type: OPS-SAT telemetry anomaly benchmark
- DOI: 10.5281/zenodo.15108715
- License: CC BY 4.0
- Intended use: Calibration and external benchmarking of telemetry processing
- Limitation: Not a direct dataset of cyber-response and trusted-recovery outcomes
- Repository treatment: Download locally; cite creators; do not commit raw files

### CuCD-ID

- Type: Simulated CubeSat cyber command and telemetry dataset
- DOI: 10.17632/7n2d42pm3n.2
- License: CC BY 4.0
- Intended use: Validate data pipeline and compare synthetic event signatures
- Scenarios: Nominal, command flooding, false data injection, defense impairment, storage exhaustion
- Limitation: Does not contain the mission-response and trusted-recovery outcome variables required for this paper
- Repository treatment: Download locally; preserve citation and license; do not commit raw files

### AegisSat dataset

- Type: Physical CubeSat telemetry with labeled attacks
- DOI: 10.5281/zenodo.14960983
- Status: Hold pending direct confirmation of the record license and usage terms
- Intended use: External plausibility comparison only
- Repository treatment: Do not download or use until license is recorded

### SPARTA

- Type: Public unclassified space-cyber TTP and countermeasure taxonomy
- Source: https://sparta.aerospace.org/
- Intended use: Event classification and traceability
- Limitation: Taxonomy use does not validate scenario prevalence or attack feasibility
- Repository treatment: Cite version and access date; do not scrape or redistribute the full site without permission review

## Prohibited sources

- Leaked or stolen telemetry
- Classified or export-controlled material
- Proprietary operator data without a signed data-use agreement
- Credentials, packet captures, or logs from operational ground systems
- Unlicensed copies of conference materials or commercial software
- Data obtained through unauthorized scanning or interception
