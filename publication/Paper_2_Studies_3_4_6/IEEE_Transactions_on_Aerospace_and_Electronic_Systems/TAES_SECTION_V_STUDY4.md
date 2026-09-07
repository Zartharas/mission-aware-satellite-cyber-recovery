# V. Multi-Producer Qualification and Provenance-Domain Constraints

## A. Study Question and Exact Population

Study 4 (`S4-MPQ-001`) evaluates how absolute vote count and synthetic provenance-domain requirements change recovery qualification under two separate conditions: malicious producer compromise and benign producer unavailability.

Seven producers `P1`-`P7` are assigned to frozen domains `D1={P1,P2,P3}`, `D2={P4,P5}`, and `D3={P6,P7}`. These are synthetic independence classes, not demonstrated organizational, hardware, software, supply-chain, or operator independence. A rule `Qq_Dd` requires `q` qualifying claims and `d` represented domains, with `q=1..7` and `d=1..min(3,q)`, yielding 18 rules. The denominator is always the registered seven-producer set.

In the safety block, hidden authorization is false; all producers are available; compromised producers emit validly signed authorization-true claims and honest producers emit false. `unsafe_qualified` is true when the compromised subset satisfies the rule. In the benign availability block, hidden authorization is true; affected producers are unavailable; all available producers emit validly signed true claims; and `false_conservative` is true when the rule rejects because insufficient votes or domains remain.

Every producer subset is evaluated: 128 subsets per block per rule, for `18 x 2 x 128 = 4,608` exact observations. The two blocks are not combined and do not model simultaneous compromise plus benign loss.

## B. First and Systematic Failure Definitions

For each rule and block, the **first failure count** is the smallest affected-producer count for which at least one subset fails; the **systematic failure count** is the smallest count for which every subset fails. The distinction captures subset dependence introduced by provenance composition. Because all subsets are enumerated, these are finite combinatorial properties, not compromise, outage, or mission-availability probabilities.

## C. Exact Threshold Map

Table III gives the complete frozen map as `first/systematic` counts.

### Table III. Study-4 first and systematic failure thresholds

| Rule | Unsafe qualification, compromised producers | False-conservative rejection, unavailable producers |
|---|---:|---:|
| `Q1_D1` | 1/1 | 7/7 |
| `Q2_D1` | 2/2 | 6/6 |
| `Q2_D2` | 2/4 | 4/6 |
| `Q3_D1` | 3/3 | 5/5 |
| `Q3_D2` | 3/4 | 4/5 |
| `Q3_D3` | 3/6 | 2/5 |
| `Q4_D1` | 4/4 | 4/4 |
| `Q4_D2` | 4/4 | 4/4 |
| `Q4_D3` | 4/6 | 2/4 |
| `Q5_D1` | 5/5 | 3/3 |
| `Q5_D2` | 5/5 | 3/3 |
| `Q5_D3` | 5/6 | 2/3 |
| `Q6_D1` | 6/6 | 2/2 |
| `Q6_D2` | 6/6 | 2/2 |
| `Q6_D3` | 6/6 | 2/2 |
| `Q7_D1` | 7/7 | 1/1 |
| `Q7_D2` | 7/7 | 1/1 |
| `Q7_D3` | 7/7 | 1/1 |

Absolute vote count sets the basic compromise boundary while moving benign-loss tolerance in the opposite direction. Provenance can further delay systematic unsafe qualification for selected thresholds, but can also cause earlier false-conservative rejection.

## D. Absolute Vote Count Sets the Basic Compromise Boundary

With only one required domain, unsafe qualification follows the vote threshold directly: `Q1_D1` through `Q7_D1` require one through seven compromised producers. Benign tolerance moves oppositely: `Q1_D1` can tolerate six unavailable producers, `Q4_D1` fails at 4/4, and `Q7_D1` rejects after any single loss. This familiar quorum tradeoff is prior art [7], [8]; Study 4 contributes the exact mapping for the frozen recovery-evidence model and its provenance variants.

## E. Provenance Diversity Changes Systematic Failure Without Necessarily Changing First Failure

`Q3_D3` shows the clearest provenance effect. First unsafe failure remains at three compromised producers, as under `Q3_D1`, but a three-producer subset must span all three domains; systematic failure moves from 3 under `Q3_D1` to 6 under `Q3_D3`. The same pattern appears at `Q4_D3` (4/6) and `Q5_D3` (5/6). Reporting first and systematic counts together prevents a single threshold from hiding this subset dependence.

## F. Provenance Diversity Also Creates Earlier Benign Rejection for Selected Rules

The same structure can reduce benign qualification tolerance. `Q3_D1` fails at 5/5 unavailable producers, whereas `Q3_D3` first fails at two and becomes systematic at five because two losses can remove an entire domain. `Q4_D3` similarly changes benign failure from 4/4 under `Q4_D1` to 2/4, and `Q5_D3` first fails at two versus three under `Q5_D1`. These are qualification effects under the frozen denominator and domain assignment, not mission-availability measurements.

## G. Null and Equal-Threshold Results

Provenance is not monotonically beneficial. `Q4_D1` and `Q4_D2` are identical in both blocks at 4/4; `Q5_D1` and `Q5_D2` are identical at safety 5/5 and benign availability 3/3; all `Q6` variants are 6/6 and 2/2; and all `Q7` variants are 7/7 and 1/1. The effect of domain requirements is therefore conditional on vote threshold, domain allocation, and subset composition.

## H. The Q4 Boundary as a Symmetric Reference Case

`Q4_D1` is symmetric at 4/4 in both separately evaluated blocks, whereas `Q4_D3` preserves first unsafe failure at four, moves systematic unsafe failure to six, moves first benign failure to two, and leaves systematic benign failure at four. This compact case illustrates why vote count alone does not describe a provenance-constrained rule.

## I. High Vote Thresholds and the Loss-Tolerance Boundary

At high thresholds, compromise resistance increases while benign-loss tolerance tightens: `Q5_D1`, `Q6`, and `Q7` require five, six, and seven compromised producers respectively, but become false-conservative after three, two, and one unavailable producers. With no utility weights, operational probabilities, or mission costs, the grid does not define a globally best rule.

## J. Relationship to Distributed Trust Prior Art

Study 4 is a deterministic qualification model, not Byzantine consensus or distributed agreement: producers do not run an agreement protocol, and the model does not analyze leaders, forks, liveness, partitions, replicated state, or Byzantine broadcast. Quorum literature [7], [8] and satellite endorsement-quorum work [9] provide structural prior art; the contribution here is the frozen recovery-qualification threshold map.

## K. Study-4 Residual Trust Boundary

Absolute vote count sets the basic compromise boundary, while synthetic provenance constraints change which same-size subsets qualify, delaying systematic failure in selected cells and causing earlier benign rejection in others. The 128 subsets are model states rather than probabilities, the domains are labels rather than demonstrated real independence, and Study 4 contains no contact model. The result is a conditional qualification frontier, not a global policy ranking.
