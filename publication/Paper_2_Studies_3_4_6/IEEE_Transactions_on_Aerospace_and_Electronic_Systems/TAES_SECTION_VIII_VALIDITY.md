# VIII. Validity, Aerospace Interpretation Boundaries, and Future Evaluation

## A. Internal and Construct Validity

The three experiments are exact evaluations of frozen finite models, so their strongest validity claim is internal to those models. Study 3 preserves the distinction between policy-visible evidence and hidden authorization truth, prespecifies the two allowable origins of false qualification, and independently audits the resulting trajectories and epoch rules. Study 4 exhausts every producer subset for every registered quorum/provenance rule in two separately defined blocks. Study 6 exhausts its prespecified artifact states and all subsets of benign assurance-signal unavailability. These controls reduce ambiguity about what each frozen endpoint represents.

The common residual-trust framework introduced in this manuscript was not itself a prospectively tested experimental treatment. Studies 3, 4, and 6 were designed and frozen independently. The common framework is a post hoc systems-level interpretation used to compare their mechanisms without changing the frozen outcomes. It should therefore be evaluated as a synthesis of three separately supported results, not as evidence that an integrated three-layer recovery architecture was experimentally validated.

The endpoint terminology also requires care. In Study 3, `unsafe_qualified` means that the modeled recovery gate remains policy-visible qualified while hidden authorization truth is false. In Study 4, the safety block measures resistance to unsafe qualification, and the availability block measures false-conservative rejection under benign producer unavailability. In Study 6, benign availability loss means rejection of the objectively correct artifact when required assurance signals are unavailable. None of these constructs is equivalent to spacecraft physical safety, mission availability, or successful completion of a recovery procedure.

## B. Study-3 Boundary Conditions

Study 3 uses one continuous-contact regime and one synthetic intermittent-contact regime. K4 contains four fixed contact windows over a 240-logical-second horizon. The result therefore characterizes that registered schedule and the associated five-logical-second epoch and freshness semantics. It does not establish how the same policies would behave under other contact schedules, real orbital geometry, different latency distributions, variable evidence lifetimes, or mission-specific ground coverage.

Logical seconds are model units. Although the labels preserve the frozen timing semantics, they are not measurements of spacecraft processor time, radio-link latency, ground-station delay, operator response time, or elapsed orbital time. The reported 122.5, 55.326, 49.022, 5, and 0.326 logical-second exposures must therefore remain model quantities.

The 46 onset phases exhaust the frozen onset grid, but they are not 46 random draws from an operational distribution. Similarly, the 67,620 epoch states are repeated states nested within 1,380 trajectories and are not independent statistical observations. The trajectory remains the study unit.

The trusted-producer compromise in `V5` is also abstract. It assumes that a trusted producer can validly sign a false authorization claim. The experiment does not model how that compromise occurs, whether a signing key is stolen, whether software is maliciously modified, or how likely the condition is in a real mission. Conversely, `V4` models a post-signature value change that invalidates the signature. The contrast establishes a bounded difference between altered signed data and false data signed by the trusted producer; it does not evaluate cryptographic strength or key-management security.

## C. Study-4 Boundary Conditions

Study 4 fixes the producer population at seven and the synthetic provenance allocation at 3/2/2. Its exact thresholds are therefore conditional on that registered producer set, domain allocation, denominator, and 18 rule definitions. A different number of producers, a different provenance allocation, dynamic membership, weighted voting, or a responder-based denominator could produce different thresholds.

The provenance domains are synthetic independence classes. The experiment does not demonstrate organizational, hardware, software, network, administrative, sensing-path, or supply-chain independence among real producers. Any operational use of a provenance constraint would require an external justification for what failure separation the domains represent.

The safety and benign-availability populations are deliberately separate. The study does not evaluate simultaneous malicious compromise and benign producer unavailability. It also does not model adaptive adversaries, collusion strategies beyond the affected-subset state, network timing, Byzantine agreement, leader election, or sensor-estimation error.

The 128 subsets per block are the complete power set of the seven modeled producers. Fractions of failing subsets at a given affected-producer count are therefore combinatorial properties of the model, not probabilities that a real subset will be compromised or unavailable. First and systematic failure thresholds likewise describe the frozen set structure and should not be interpreted as operational reliability limits.

## D. Study-6 Boundary Conditions

Study 6 is an abstract six-state, six-gate Boolean assurance model. The five objectively incorrect states were selected to expose distinct trust assumptions, but they are not an exhaustive taxonomy of software-supply-chain failure. Consequently, values such as 4/5, 3/5, 2/5, and 1/5 are finite state counts rather than detection rates, false-negative rates, or estimates of residual compromise probability.

The six assurance signals are also modeled Boolean variables. `independent_target_digest_match` and `independent_reproduced_build_match` do not demonstrate real organizational or infrastructure independence. `source_review_attested` and `release_approved` do not measure the quality, competence, or adversarial resistance of a real review and approval process.

`APPROVED_BAD_SOURCE` is intentionally defined so that all six gate-visible signals are true while objective correctness is false. It therefore identifies the observability boundary of the frozen model. The result is not a theorem that semantic correctness can never be established, nor does it imply that additional techniques such as formal verification, independent behavioral testing, semantic review, runtime validation, or diverse implementations could not add evidence. Those mechanisms were outside the frozen Study-6 design and were not added after observing the result.

The benign assurance-unavailability block is likewise structural. All 64 unavailable-signal subsets are evaluated with the objectively correct baseline. Counts such as 63/64 describe deterministic rejection across that finite subset space. They do not estimate service outage probability, contact probability, or the frequency with which real assurance systems become unavailable.

## E. External Validity and Aerospace Generalization

No experiment in Paper 2 operates an on-orbit spacecraft, ground station, RF link, flight processor, production key infrastructure, or real mission command path. No operational spacecraft recovery is executed. The results therefore do not establish flightworthiness, certification, mission assurance compliance, operational attack prevalence, recovery success probability, or mission-level availability.

Only Study 3 directly includes a contact variable. Study 4 producer unavailability must not be interpreted as loss of spacecraft contact, and Study 6 assurance-signal unavailability must not be interpreted as either contact loss or network outage. Treating all three as manifestations of intermittent connectivity would erase important construct differences among the experiments.

The spacecraft relevance instead comes from the systems question being modeled: recovery qualification can depend on evidence received under intermittent contact, evidence composed across trusted producers, and assurance about the recovery artifact itself. The experiments isolate those mechanisms in deterministic abstractions. Generalization to a specific spacecraft program would require mapping the abstract evidence producers, provenance domains, gates, timing semantics, and failure states to mission-specific components and then validating that mapping against the target architecture.

## F. Statistical Interpretation

The studies evaluate complete finite populations specified by their frozen protocols. Sampling-based inferential statistics are therefore not used to make claims about the registered grids. No p-value gate, confidence interval over an assumed superpopulation, or pooled effect estimate is required to establish an exact count or threshold within the enumerated state space.

This does not make the results universal. Exactness applies to the registered model population, not to all possible spacecraft or attack conditions. The absence of sampling uncertainty within a finite grid is distinct from uncertainty about model choice, external validity, or omitted operational variables.

The three populations also remain incommensurate. Study 3 uses trajectories, Study 4 uses rule-by-subset observations, and Study 6 uses artifact-state and assurance-unavailability observations. Their arithmetic sum is not a scientifically meaningful sample size. No pooled `N`, success percentage, confidence interval, or global rank is defined in this paper.

## G. Reproducibility and Independence

Each experiment is provenance-bound and independently audited within the repository. Study 3 reports zero trajectory, epoch-rule, false-qualification-origin, and hash mismatches. Study 4 reports zero observation and threshold mismatches under independent reconstruction. Study 6 reports zero mismatches with matching frozen outputs and no tracked-file drift.

These controls support same-repository reproducibility and strengthen confidence that the reported manuscript projections reflect the frozen experiments. They do not constitute external empirical replication because the independent implementations and audits remain within the same research program and repository. External replication would require an independent research group, environment, or evidence source beyond the present repository controls.

## H. Standards and Framework Interpretation

RATS, SPARTA, SLSA, TUF, in-toto, and related sources are used to position the modeled evidence dimensions against established security concepts. The studies do not implement every requirement of those frameworks, and no compliance assessment was performed. References to provenance, attestation, reproducible builds, trusted baselines, or cyber-safe recovery therefore identify conceptual relationships only.

This distinction is particularly important for Study 6. The presence of model variables named provenance, reproduced build, source review, and release approval does not establish that a deployed implementation would satisfy SLSA, TUF, SPARTA, or any other standard or framework.

## I. Limits of the Cross-Study Synthesis

The cross-study synthesis compares residual mechanisms, not causal transitions from one experiment to the next. Study 4 does not experimentally mitigate Study 3, and Study 6 does not experimentally validate a downstream artifact gate for either Study 3 or Study 4. No data flow connects the frozen populations.

The synthesis also does not imply that the three qualification layers are complete. Real recovery systems can depend on additional dimensions, including command authority, hardware roots of trust, behavioral verification, physical-state estimation, network path integrity, human authorization, fault-management logic, and mission-phase constraints. The present paper focuses only on the three independently frozen mechanisms that were evaluated.

Accordingly, the layered residual-trust interpretation should be read as an analytical decomposition: temporal evidence, producer composition, and artifact assurance each expose a distinct trust boundary. It is not a claim that every recovery architecture should contain exactly these three layers or evaluate them in this order.

## J. Future Evaluation

Several extensions could test the portability of the present findings without altering the frozen evidence reported here. Study 3 could be complemented by prospectively designed orbital-contact schedules, variable evidence lifetimes, or hardware/software-in-the-loop timing measurements. Study 4 could be extended to different producer counts, empirically justified failure domains, dynamic membership, or joint compromise-and-unavailability conditions. Study 6 could be evaluated against real build pipelines, independently operated assurance services, additional semantic-validation mechanisms, or prospectively defined joint artifact-compromise and evidence-loss scenarios.

A separate integrated experiment could also test how runtime evidence, multi-producer composition, and artifact assurance interact in one recovery architecture. Such an experiment would be scientifically different from the present manuscript because it would define new joint interventions, units, and endpoints. It should therefore be designed and frozen prospectively rather than inferred from the three existing populations.

These extensions are opportunities for external validation and broader generalization. They are not defects that justify reopening or rerunning the frozen Studies 3, 4, or 6 for the present paper.
