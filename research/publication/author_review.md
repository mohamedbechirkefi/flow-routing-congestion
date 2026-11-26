<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Author review (for the owner)

Status (2026-11-25): the owner approved the funding, competing-interest and AI-use statements of the manuscript on 2026-11-25 ("Approve all", post-M4; D-017) and the authorship metadata at the freeze (record C3). The FLOW manuscript title was approved on 2026-11-26 (owner, 2026-11-26, decision sheet, B6). The owner's full-text review of the manuscript and articles is pending (B16). Only the owner ticks the boxes below; none is ticked.

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

1. The release (B18): the repository is public at <https://github.com/mohamedbechirkefi/flow-routing-congestion> since 2026-11-25; no tag, release, DOI or preprint exists, and each needs the owner's approval (G-PUBLIC). (Item corrected on 2026-11-26; it said at M6 that no push or public repository existed.)
2. The manuscript title "Individually optimal routing and total travel time on synthetic grid networks: a preregistered simulation study" was not in the titles approved on 2026-11-25 and needs the owner's approval or a replacement.
3. `CITATION.cff` keeps the software title "FLOW: Navigation and collective congestion", which differs from the manuscript title; the owner decides whether the citation should name the manuscript instead (not changed at M6 because the manuscript title is not approved).
4. `CITATION.cff` now reads version `0.1.0-rc1` with no `date-released` (coordinator default under owner-approvals-2026-11-25e); re-adding a release date is part of the owner's publication step.
5. The repository URL and the demo URL are owner-only facts and stay placeholders until a release is approved.
6. Blocker B5 in `roadmap.md` is still open: the owner confirms the public licence wording ("source-available, not open-source").
7. The flagged tool and font licences in `research/publication/dependency_licences.md` (pandoc GPL-2.0-or-later as a build tool, embedded OFL and DejaVu fonts, headless Chrome as a test tool, hatchling not read from metadata) need the owner's acknowledgement.
8. The two exact checks (EXP-001, EXP-002) remain "contradicted" under their frozen rule; the owner accepted this framing on 2026-11-25 (D-016), and a registered rerun at the intended tolerance would be a new study.

Remaining owner placeholders: none. The text "[to be added on owner-approved release]" was replaced on 2026-11-26 (B1, B2) in `README.md`, `CITATION.cff` (now `repository-code`), `research/paper/manuscript.md` and its generated `manuscript.tex`, `articles/medium.md`, `articles/linkedin.md`, `demo/README.md` and `demo/site/index.html`. Items 2 to 5 and 7 of the list above are settled by the answers below; items 6 and 8 are unchanged.

## Owner answers recorded (2026-11-26)

Authority: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md`, answers in `labs/_shared/owner-approvals-2026-11-26.md`). Recorded in decision D-022. No box above is ticked by this record.

- **A1.** Out-of-date "nothing pushed / nothing published" sentences corrected in this file, `release_checklist.md` and `README.md`. Append-only records keep their dated wording.
- **B1.** Repository URL `https://github.com/mohamedbechirkefi/flow-routing-congestion` filled everywhere; `repository-code` added to `CITATION.cff`.
- **B2.** Demo URL `https://flow-routing-congestion.kefimohamedbechir.workers.dev` filled; `demo/wrangler.jsonc` added (Cloudflare Workers static assets, free plan, assets directory `./dist`, no Worker script); the deploy is the coordinator's, not this repository's.
- **B3.** Author line "Mohamed Bechir Kefi, independent researcher" in the manuscript, supplementary, the six experiment reports, README, both articles and the demo footer; `CITATION.cff` `affiliation: "Independent researcher"`. `pyproject.toml` keeps the name only (no affiliation field). Frozen protocols not edited.
- **B4.** "No funding was received." and "The author declares no competing interests." in the manuscript.
- **B6, B7.** Manuscript title approved as written; `CITATION.cff` `title` now equals it (the software title "FLOW: Navigation and collective congestion" is no longer the citation title; it stays the README heading).
- **B8.** Version `0.1.0-rc1`, no `date-released`; the release step is recorded in `release_checklist.md`.
- **B9.** Editable files hold no home path; 18 lines in 5 append-only or result files remain (`reproducibility_report.md`, section "Home paths remaining (2026-11-26)").
- **B10.** Committed PDFs stay and are attached to the release.
- **B11.** Not applicable to FLOW (no figure listed).
- **B13.** Release-note sentence on build tools added to `release_checklist.md`.
- **B14.** The source-level labels (six sources "metadata verified; text not read") are accepted as stated in the manuscript; no "for the owner to accept" mark existed in this repository.
- **Flags of `dependency_licences.md` (item 7).** Acknowledged through B13 for pandoc, Chrome and the embedded fonts; the hatchling licence stays unverified in this repository.

Still open, the owner's: B15 (article drafts, before any posting), B16 (full-text review of the manuscript, then the sign-off of the boxes above), B18 (release, tag, optional DOI or preprint), blocker B5 in `roadmap.md` (public licence wording "source-available, not open-source", not covered by the decision sheet), and item 8 (the contradicted exact checks stay as framed in D-016). No freeze is pending in FLOW.
