<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
<!-- Draft (M5, 2026-11-25). Not published. Publication is the owner's decision (G-PUBLIC); the owner's full-text review is pending (M6). Numbers are printed as in research/paper/manuscript.md. -->

Can the fastest route make everyone slower?

I built FLOW, a small, offline, preregistered simulation study of selfish routing: a tested traffic-assignment engine, six frozen experiments, a public record of every result, and an interactive page with an animated Braess network.

One defensible finding: on 100 synthetic 6 by 6 grid networks with conventional quartic link costs, at twice the saturation demand, equilibrium routing used a median 0.02317 more total travel time than the system optimum (95 percent interval [0.02075, 0.02559]), above the preregistered 1 percent margin.

The caveats matter as much: with linear-in-flow costs or light demand the excess fell below 1 percent; two exact checks on the Braess network failed their own frozen tolerance rule and are reported as contradicted; and this is a simulation on synthetic networks, not a statement about any real city or navigation app.

Repository: https://github.com/mohamedbechirkefi/flow-routing-congestion
Demo: https://flow-routing-congestion.kefimohamedbechir.workers.dev

Mohamed Bechir Kefi, independent researcher. An AI system (Claude, Anthropic) was used as a research and development assistant.
