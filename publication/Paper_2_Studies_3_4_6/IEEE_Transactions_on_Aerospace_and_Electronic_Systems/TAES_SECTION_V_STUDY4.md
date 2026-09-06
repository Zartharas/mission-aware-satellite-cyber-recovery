# V. Multi-Producer Qualification and Provenance-Domain Constraints

## A. Study Question and Exact Population

Study 4 (`S4-MPQ-001`) evaluates how recovery qualification changes when evidence is supplied by multiple modeled producers rather than by a single producer. The study asks two separate questions. First, how many compromised producers are required before false authorization can satisfy a qualification rule? Second, how many benign producer losses can occur before a true authorization state is rejected conservatively? The experiment varies both absolute vote count and a synthetic provenance-domain requirement.

Seven modeled producers, `P1` through `P7`, are assigned to three frozen provenance domains: `D1={P1,P2,P3}`, `D2={P4,P5}`, and `D3={P6,P7}`. These domains are synthetic independence classes. They do not establish that the modeled producers correspond to independent organizations, hardware, software stacks, supply chains, or operators.

A qualification rule is denoted `Qq_Dd`, where `q` is the required number of qualifying producer claims and `d` is the required number of represented provenance domains. Total-vote thresholds range from one through seven. The domain threshold ranges from one through `min(3,q)`, producing 18 prespecified rules. The denominator is always the registered seven-producer set, not the number of producers that happen to respond.

The study contains two separate exhaustive blocks. In the **safety block**, hidden authorization truth is false, all producers are available, compromised producers emit a visible authorization-true claim with a valid signature, and honest producers emit authorization false. The endpoint `unsafe_qualified` is true when the compromised subset satisfies the rule despite hidden authorization being false.

In the **benign availability block**, hidden authorization truth is true, affected producers are unavailable, all available producers emit a true claim with valid signatures, and no producer is malicious. The endpoint `false_conservative` is true when the rule rejects the true authorization state because too few producers or provenance domains remain available.

Every subset of the seven producers is evaluated. There are 128 subsets per block per rule. The complete population is therefore `18 x 2 x 128 = 4,608` exact observations. The compromise and benign-unavailability blocks are not combined, and the study does not evaluate simultaneous malicious compromise plus benign producer loss.

## B. First and Systematic Failure Definitions

For each rule and block, the analysis records two thresholds.

The **first failure count** is the smallest number of affected producers for which at least one subset of that size causes the endpoint to fail. It identifies when failure becomes possible.

The **systematic failure count** is the smallest number of affected producers for which every subset of that size causes failure. It identifies when failure becomes unavoidable within the frozen producer assignment.

The distinction is necessary whenever provenance diversity matters. A rule can first fail at a given compromised-producer count because one cross-domain subset satisfies the rule, while other same-size subsets remain blocked. The systematic threshold captures when subset composition no longer matters because every subset of that size crosses the boundary.

Because the study exhausts all subsets, these thresholds and subset proportions are finite combinatorial properties. They are not estimates of operational compromise probability, outage probability, or mission availability.

## C. Exact Threshold Map

Table III reports the complete frozen threshold map. Safety entries are shown as `first/systematic` compromised-producer counts. Availability entries are shown as `first/systematic` unavailable-producer counts.

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

The table exposes two separate effects. Raising the absolute vote threshold increases the number of compromised producers required to qualify false authorization, but reduces tolerance to benign producer loss. Adding provenance-domain requirements can further delay systematic unsafe qualification for selected vote thresholds, but can also make false-conservative rejection possible after fewer unavailable producers.

## D. Absolute Vote Count Sets the Basic Compromise Boundary

Without an added provenance constraint beyond one represented domain, the safety threshold follows the absolute vote count directly. `Q1_D1` fails with one compromised producer, `Q2_D1` with two, `Q3_D1` with three, and so on through `Q7_D1`, which requires all seven producers to be compromised before false authorization qualifies.

The corresponding benign-unavailability boundary moves in the opposite direction. `Q1_D1` continues to qualify a true authorization state until all seven producers are unavailable. `Q4_D1` first and systematically fails after four producers are unavailable. `Q7_D1` becomes false-conservative after loss of any single producer. The finite model therefore exposes the expected tension between requiring more positive claims for resistance to compromise and requiring fewer unavailable producers for continued qualification.

This pattern is not presented as new quorum theory. Quorum safety and availability relationships are well established [7], [8]. The Study-4 contribution is the exact mapping of those structural effects onto the frozen recovery-evidence qualification problem, including the additional domain-composition rules and the distinction between first and systematic failure.

## E. Provenance Diversity Changes Systematic Failure Without Necessarily Changing First Failure

The clearest provenance effect appears at `Q3`. Under `Q3_D1`, three compromised producers are sufficient for both first and systematic unsafe qualification. Every three-producer compromise contains enough positive votes because no cross-domain requirement is imposed.

Under `Q3_D3`, the first unsafe qualification still occurs at three compromised producers, but only a three-producer subset spanning all three provenance domains can satisfy the rule. Same-domain or two-domain triples remain blocked. Systematic unsafe qualification does not occur until six of the seven producers are compromised. Thus the provenance requirement leaves the first possible failure count unchanged at three while moving systematic failure from three to six.

The same structural effect appears at `Q4_D3` and `Q5_D3`. `Q4_D3` first fails for unsafe qualification at four compromised producers but does not fail systematically until six. `Q5_D3` first fails at five and becomes systematic at six.

This distinction matters because a single threshold such as "fails at three" would obscure the subset dependence introduced by provenance composition. First and systematic counts are therefore reported together whenever interpretation depends on which provenance domains are represented in the affected subset.

## F. Provenance Diversity Also Creates Earlier Benign Rejection for Selected Rules

The stronger safety boundary carries a corresponding qualification-availability cost. Under `Q3_D1`, benign producer unavailability first causes false-conservative rejection at five unavailable producers and is systematic at five. Under `Q3_D3`, the first false-conservative failure occurs after only two unavailable producers because a subset can remove an entire provenance domain even while five producers remain. Systematic false-conservative rejection still occurs at five.

`Q4_D3` has the same qualitative pattern. `Q4_D1` first and systematically fails after four unavailable producers. `Q4_D3` can first fail after only two unavailable producers while becoming systematic at four. `Q5_D3` can also first fail after two unavailable producers, whereas `Q5_D1` first fails at three.

These results do not mean that provenance diversity reduces mission availability. The endpoint is narrower: under the frozen registered-producer denominator and domain assignment, selected benign producer-loss subsets can make the recovery-evidence gate reject a true authorization state earlier because the required diversity of visible evidence is no longer present.

## G. Null and Equal-Threshold Results

The provenance requirement does not always change the qualification boundary. These null results are important because they prevent a monotonic "more provenance is always better" interpretation.

At `Q4`, `Q4_D1` and `Q4_D2` have identical first and systematic thresholds in both blocks: safety 4/4 and benign availability 4/4. Requiring two domains adds no threshold effect under this particular producer allocation and vote requirement.

At `Q5`, `Q5_D1` and `Q5_D2` are also identical: safety 5/5 and benign availability 3/3. Again, the two-domain requirement does not alter the frozen thresholds.

At `Q6`, all three domain variants are identical. Safety fails at 6/6 and benign availability at 2/2 for `D1`, `D2`, and `D3`. At `Q7`, every domain variant is also identical at safety 7/7 and benign availability 1/1 because requiring all seven producers necessarily includes all three provenance domains.

These equal-threshold cases show that the effect of provenance constraints is conditional on the interaction among vote threshold, domain allocation, and affected subset composition. The experiment does not support the claim that increasing provenance-domain requirements universally improves resistance to unsafe qualification.

## H. The Q4 Boundary as a Symmetric Reference Case

`Q4_D1` provides a useful finite-model reference because the first and systematic thresholds are symmetric across the two separately evaluated blocks. Four compromised producers are required for unsafe qualification, and four unavailable producers cause false-conservative rejection. Adding a three-domain requirement in `Q4_D3` changes that structure: safety first failure remains four, systematic safety failure moves to six, benign availability first failure moves to two, and systematic availability failure remains four.

This comparison illustrates why a single vote threshold does not fully describe the qualification rule once provenance constraints are added. Absolute vote count establishes the base boundary, while provenance composition determines which same-size subsets can satisfy that boundary.

## I. High Vote Thresholds and the Loss-Tolerance Boundary

At high vote thresholds, compromise tolerance increases while benign loss tolerance becomes restrictive. `Q5_D1` requires five compromised producers for unsafe qualification but rejects true authorization after three producers become unavailable. `Q6` requires six compromised producers for unsafe qualification and becomes false-conservative after two unavailable producers. `Q7` requires all seven producers to be compromised before false authorization can qualify, but any single unavailable producer prevents qualification of the true state.

The finite grid therefore does not identify a globally best rule. A higher threshold can reduce the modeled unsafe-qualification region while increasing the modeled false-conservative region. The study contains no utility weights, operational failure probabilities, or mission costs that would justify collapsing those two objectives into a single score.

## J. Relationship to Distributed Trust Prior Art

The Study-4 model deliberately stops short of Byzantine consensus or distributed agreement. Producers do not run a protocol to reach agreement with one another. The model does not analyze message scheduling, leaders, forks, liveness, replicated state, network partitions, or Byzantine broadcast. Instead, a recovery gate receives modeled producer claims and applies a deterministic qualification rule.

The connection to quorum-system literature [7], [8] is therefore conceptual and structural. That literature establishes that fault assumptions and quorum structure govern consistency and availability properties in distributed systems. Study 4 uses a simpler finite qualification abstraction to ask how total vote count and synthetic provenance-domain composition affect one recovery-authorization decision boundary. Likewise, the existence of satellite architectures using endorsement quorums [9] means that satellite quorum trust itself is not claimed as novel.

## K. Study-4 Residual Trust Boundary

Study 4 shows that producer composition can move the residual qualification boundary without eliminating the underlying dependence on trusted producer structure. Absolute vote count sets the minimum compromised-producer count needed for false qualification. Provenance-domain requirements can prevent selected same-size compromised subsets from qualifying and can therefore delay systematic failure. The same requirements can also reject a true authorization state after fewer benign producer losses when domain diversity disappears.

The result is a finite safety-versus-qualification-availability frontier, not a global policy ranking. The synthetic provenance domains are model labels rather than demonstrated real independence, and the 128 subsets in each block are model states rather than probabilities. Study 4 also contains no contact model. The next study moves to a third boundary, asking which incorrect recovery artifacts remain qualified when progressively stronger artifact-assurance signals are required.
