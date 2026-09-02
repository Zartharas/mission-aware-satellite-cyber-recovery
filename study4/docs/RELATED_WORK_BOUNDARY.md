# Study 4 related-work boundary

Checked 2026-09-02.

Byzantine-resilient consensus and sensor fusion are established research areas. Contemporary work includes Byzantine-resilient distributed consensus for satellite constellations (Results in Engineering, 2026), resilient satellite formation against Byzantine adversaries (Aerospace Science and Technology, 2026), and Byzantine-fault-tolerant multi-sensor fusion with guaranteed output delivery (ACM CCS 2024).

Therefore Study 4 does **not** claim to invent Byzantine voting, q-of-N consensus, or fault-tolerant sensor fusion. Its narrower contribution is to quantify, inside the repository's trusted-recovery evidence model, how independently signed false authorization claims cross a recovery qualification gate as producer compromise grows, and how adding provenance-domain diversity changes the safety/availability frontier.

The model is deliberately simpler than PBFT/MSR protocols: it does not model distributed agreement messages, network scheduling, leader election, equivocation between receivers, or orbital control. It evaluates evidence qualification only.
