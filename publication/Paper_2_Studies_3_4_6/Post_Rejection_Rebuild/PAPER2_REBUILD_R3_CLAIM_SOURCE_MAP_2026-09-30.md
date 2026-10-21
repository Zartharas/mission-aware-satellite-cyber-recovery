# Paper 2 Rebuild R3 — Claim-to-Source Map

**Purpose:** bind the R3 S6X integration to the effective Campaign-004 result freeze while preserving R2 and the historical TAES R10 package.

## Authoritative base

- main: `2ddbd795c4734654f421616de996911fa62ee27a`
- S6X result freeze: `S6X-CANONICAL-RESULT-FREEZE-004`
- S6X result-freeze blob: `2e6b213b994062fd108e4b8435d9c0c36d93fdc0`
- post-merge CI: #1314 / run `36808689393` — SUCCESS
- R2 manuscript: immutable blob `9e3f345a3a16102c39bb978f4e522c261e80cfb4`

## S6X bound sources

| Source | Git blob SHA-1 | R3 use |
|---|---|---|
| Result Freeze 004 | 2e6b213b994062fd108e4b8435d9c0c36d93fdc0 | Canonical Campaign-004 evidence and hashes |
| Runtime Authorization 004 | d5a329be6c0803c5345845746c66844db8cfb552 | Campaign and acceptance boundaries |
| Runner 004 | 99088f34886c50d38efaabf1c0aca4679fe07342 | Build/test/signing/repeat execution semantics |
| Evidence Schema 004 | af697b5407bf1eda49667109d208aa9e57030494 | Objective-adjudication versus gate-visible evidence separation |
| Population generator 004 | 965fde110b7dc754553efe08b1530beeba752908 | 12-row Block A and 384-row Block B semantics |
| Primary gate evaluator | c6045b249daa6a3ff3b2ff54982b047c299fd04c | Six qualification-gate definitions |
| Reference gate evaluator | c3834f478196fe3fd3e9290ff0ecc603a0933247 | Independent gate interpretation |
| Equality-boundary harness | b3318be396a6c4e5c98f2339846d9ea59bcd5def | Research functional adjudication |
| Controlled fixture | e3189e5a06ff47a2cf68bb7d343c563a300dc313 | GT `>` → `>=` source change |
| Frozen invariant oracle | 70b555cec84cb455c72094c6539df3873662182d | Independent GT/GE truth table |

## Claim firewall

R3 may state only that S6X is a separate executable stress test of the Study-6 observability mechanism. It may not describe S6X as an external empirical replication, pool S6X with Study 6, claim a NASA/cFS/LC vulnerability, generalize research attestations to production assurance, or treat the research functional harness as one of the six qualification signals.

## Display decision

R3 adds Table V and leaves Figure 1 unchanged.
