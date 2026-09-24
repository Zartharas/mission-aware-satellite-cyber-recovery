# AERC cFS Software Bus Probe

This is a non-canonical engineering feasibility component for `S7E-AERC-001`.

It performs one narrow check inside the pinned cFS candidate environment:

1. create a cFE Software Bus pipe;
2. subscribe to an experimental local message ID;
3. publish one message containing a fixed scenario marker;
4. receive the same message from the Software Bus;
5. verify the scenario ID and marker;
6. emit `AERC_BUS_PROBE PASS`;
7. exit.

It does **not** implement a recovery policy, learner, topology campaign, fault injection, or scientific endpoint. Its output is engineering qualification evidence only.

The experimental message ID is local to the smoke test and is not a frozen mission interface.
