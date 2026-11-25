<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
<!-- Draft (M5, 2026-11-25). Not published. Publication is the owner's decision (G-PUBLIC); the owner's full-text review is pending (M6). Every number is printed as in research/paper/manuscript.md. -->

# Can the fastest route make everyone slower? A small, preregistered simulation

*Draft. Author: Mohamed Bechir Kefi. An AI system (Claude, Anthropic) was used as a research and development assistant; it is not an author.*

Most of us pick the route that gets us there fastest. A classical result of transport economics says that when everyone does this, the total time spent on the road can be larger than if traffic were coordinated, and that adding a road can even make every driver slower. That is Braess's paradox. How large is the gap in practice? FLOW asks a narrower question that a simulation can answer honestly: **can individually optimal routing worsen collective travel time, and by how much, in a controlled family of synthetic networks?**

This is a simulation study. It does not model Google Maps or any navigation product, it makes no prediction for any real city, and its synthetic travellers are not people.

## The picture in one network

![Two drawings of a four-node network, before and after adding a link from A to B, with measured flows at demand 6, and a chart of equilibrium mean trip time against demand with and without the extra link; the shaded interval marks where the extra link makes everyone slower.](../docs/demo.png)

*Figure 1. The Braess network on the FLOW demo page. Left: without the extra link e. Right: with it. At demand 6 the equilibrium travel time is 83 without the link and 92 with it. Below: equilibrium mean trip time against demand; inside the shaded interval (80/31, 80/9) the extra link makes every traveller slower. Values are the measured EXP-002 records.*

## What we did

Before solving a single confirmatory instance, the protocol was frozen and hashed: the question, the primary metric, the 0.01 margin, the decision rule and the seeds. The primary metric is the relative excess `R` of a routing rule's total travel time over the system optimum on the same network and demand. We compared three rules: free-flow shortest paths (the simplest baseline), user equilibrium (every traveller minimises their own time under congestion) and the system optimum. The primary test used 100 seeded 6 by 6 grid networks with quartic (BPR) link costs at twice the demand at which free-flow routing first saturates a link, with bootstrap intervals over instances.

## What we found

- **Equilibrium routing cost a median 0.02317 more total travel time than the optimum** (95 percent interval [0.02075, 0.02559]; one-sided lower bound 0.02134). The preregistered null hypothesis of an excess of at most 0.01 is rejected.
- **It depends on the setting.** The decision held at tighter and looser solver tolerances and under an alternative demand calibration. It did not hold with linear-in-flow costs (median 0.00304) or at light demand, where all three rules were within 1 percent of the optimum in median.
- **Ignoring congestion is much worse.** Free-flow routing exceeded equilibrium by a paired median of 0.2007 at the primary demand level.
- **Partial coordination helps step by step.** Routing a growing share of travellers system-optimally lowered the excess at every step, in one operationalisation of compliance.
- **Braess links are common but small.** 77 of 100 small grids contained a link whose removal lowers equilibrium travel time; in an exploratory check the median effect was 0.0030.
- **One real test network agrees, barely.** On Sioux Falls, which its maintainers do not consider realistic, the excess was 0.01453.

## What did not work

Two exact checks on the Braess network were **contradicted** under their own frozen rule: the solver stopped at a relative gap of 1e-6, while the check demanded an absolute accuracy of 1e-6, and the residuals were 1e-5 to 6e-5. An exploratory rerun at a relative gap of 1e-10 met the rule (largest difference 7.53e-9). That rerun was decided after the results were seen, so the frozen verdicts stand as reported.

## Limits

Synthetic lattices with 12 origin-destination pairs; static, deterministic assignment with perfect information; quartic costs only; congested demand only; one solver implementation on grids, because the independent Frank-Wolfe reference did not converge on most instances; the 0.01 margin is the study's own convention. None of this transfers to real roads without new work.

## Reproduce it

Everything is offline and free to rerun: code, frozen protocols, configs, per-record results, reports and an interactive page. Repository: [to be added on owner-approved release]. Demo: [to be added on owner-approved release]. Manuscript: `research/paper/manuscript.md` in the repository.
