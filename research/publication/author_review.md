<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Author review (for the owner)

Status (2026-11-25): the owner approved the funding, competing-interest and AI-use statements of the manuscript on 2026-11-25 ("Approve all", post-M4; D-017) and the authorship metadata at the freeze (record C3). The FLOW manuscript title was not in the post-M4 title approval list and remains to be approved. The owner's full-text review of the manuscript and articles is pending and belongs to M6. Only the owner ticks the boxes below; none is ticked.

- [ ] Authorship and affiliation metadata approved.
- [ ] Research question, hypotheses and claims boundary approved.
- [ ] AI assistance disclosure accurate.
- [ ] Every claim in the manuscript and articles reviewed.
- [ ] Limitations adequate.
- [ ] Publication target and licence statement approved.

No box above was ticked by an agent at M6, so none was unticked.

## Prepared for the owner (M6, 2026-11-25)

What to read for each box:

- **Authorship and affiliation metadata.** `research/paper/manuscript.md`, section "Author and affiliation metadata"; `CITATION.cff` (`authors`); `README.md`, section "Citation".
- **Research question, hypotheses and claims boundary.** `research/paper/manuscript.md`, sections 1 (Introduction), 4.1 (Design and protocol registration) and 6.1 (What the evidence supports); `research/claims_register.csv` (21 rows).
- **AI assistance disclosure.** `research/paper/manuscript.md`, section "Funding, competing interests and AI assistance" (approved as drafted, D-017); `CITATION.cff`, `message`.
- **Every claim in the manuscript and articles.** `research/paper/manuscript.pdf` (12 pages), `research/paper/supplementary.pdf`, the six `research/experiments/EXP-00N/report.pdf`, `articles/medium.md`, `articles/linkedin.md`; audits in `research/publication/evidence_audit.md` (section 6 for the M6 source levels) and `research/publication/claims_audit.md`.
- **Limitations.** `research/paper/manuscript.md`, section 7; `research/limitations.md`.
- **Publication target and licence statement.** `README.md`, section "Licence"; `research/publication/dependency_licences.md`; `research/publication/release_checklist.md`; `research/publication/reproducibility_report.md`.

Open decisions for this repository (each is the owner's):

1. Whether to publish anything at all: no push, tag, release or public repository exists, and each needs the owner's approval (G-PUBLIC).
2. The manuscript title "Individually optimal routing and total travel time on synthetic grid networks: a preregistered simulation study" was not in the titles approved on 2026-11-25 and needs the owner's approval or a replacement.
3. `CITATION.cff` keeps the software title "FLOW: Navigation and collective congestion", which differs from the manuscript title; the owner decides whether the citation should name the manuscript instead (not changed at M6 because the manuscript title is not approved).
4. `CITATION.cff` now reads version `0.1.0-rc1` with no `date-released` (coordinator default under owner-approvals-2026-11-25e); re-adding a release date is part of the owner's publication step.
5. The repository URL and the demo URL are owner-only facts and stay placeholders until a release is approved.
6. Blocker B5 in `roadmap.md` is still open: the owner confirms the public licence wording ("source-available, not open-source").
7. The flagged tool and font licences in `research/publication/dependency_licences.md` (pandoc GPL-2.0-or-later as a build tool, embedded OFL and DejaVu fonts, headless Chrome as a test tool, hatchling not read from metadata) need the owner's acknowledgement.
8. The two exact checks (EXP-001, EXP-002) remain "contradicted" under their frozen rule; the owner accepted this framing on 2026-11-25 (D-016), and a registered rerun at the intended tolerance would be a new study.

Remaining owner placeholders (text "[to be added on owner-approved release]"), by file and line at M6:

- `README.md` lines 22 (demo URL) and 101 (repository URL);
- `CITATION.cff` line 5 (repository URL, in `message`);
- `research/paper/manuscript.md` line 280 (repository URL, section "Data and code availability"), and its generated copy `research/paper/manuscript.tex` line 1024;
- `articles/medium.md` line 41; `articles/linkedin.md` lines 12 (repository) and 13 (demo);
- `demo/README.md` line 37 (demo URL);
- `demo/site/index.html` line 64 (page footer).
