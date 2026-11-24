<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-002: Braess demand sweep, when does the added link hurt?

**Status: protocol v1.0, FROZEN (owner-approved 2026-11-24, round 2), not yet run.** Amendments before the freeze: umbrella `research/protocol.md` section 15. Depends on EXP-001 passing.

1. **Question.** For which total demands `d` does adding link e raise UE travel time in the Braess network, and how do FF, UE and SO compare across demand?
2. **Mechanism.** At low demand the added link is a pure shortcut; at high demand the congested links make it unattractive; in between, private and social incentives diverge.
3. **Rationale.** Braess et al. (2005) and the supernet page (read) give the single point `d = 6`. The interval is not taken from a source.
4. **Competing explanations.** Solver error near regime boundaries; discretisation of the sweep.
5. **Hypothesis (deterministic, hand-derived by the assistant on 2026-11-24, not yet checked against a published source).** With symmetric flows `f` on each outer path and `g` on the path a-e-d: for `d <= 40/11` all demand uses a-e-d with time `21d + 10`; for `40/11 <= d <= 80/9`, `f = (11d - 40)/13`, `g = (80 - 9d)/13`, time `(31d + 1010)/13`; for `d >= 80/9` link e is unused and time is `5.5d + 50`. Without link e the time is `5.5d + 50`. Hence the link raises UE time exactly for `d in (80/31, 80/9)`. Before any run this derivation is to be verified by exact rational unit tests. Contradiction: computed regime boundaries or paradox interval deviating by more than `1e-6`.
6. **Estimand.** `Delta(d) = TSTT_UE(with e) - TSTT_UE(without e)` over the demand grid; the set where `Delta > 0`.
7. **Unit and scope.** Deterministic; 48 demand values `0.25, 0.50, ..., 12.00`.
8. **Variables.** Independent: `d`, link presence, arm. Dependent: TSTT, path times, R, `Delta`.
9. **Treatment and control.** With and without link e at matched `d`.
10. **Baseline.** FF at each `d`.
11. **Seeds and sample size.** None; sweep fixed in advance.
12. **Compute budget.** Under a few minutes (planning estimate).
13. **Metrics.** TSTT, mean time, R for each arm, `Delta`.
14. **Uncertainty.** None; exact values with tolerance. Interval endpoints reported analytically, the sweep shows agreement.
15. **Exclusion and stopping.** None.
16. **Failure modes.** Solver: gradient projection (umbrella 15.3 item 1). Degenerate equilibria at regime boundaries (`d = 40/11`, `80/9`).
17. **Sensitivity.** Finer step (0.05) around the predicted boundaries.
18. **Reproduction (planned).** `uv run flow run EXP-002`.
