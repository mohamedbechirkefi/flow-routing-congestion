<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Literature review (M0 working notes)

Status: M0 source audit, not a systematic review. Searches ran on 2026-11-24 with web search and direct fetches. Each source carries a verification level:

- **Read**: the full text (or the relevant part) was opened this session.
- **Abstract read**: the abstract page was opened, not the full text.
- **Metadata verified**: bibliographic metadata confirmed through the Crossref API (`api.crossref.org/works/<DOI>`); the text was not opened. Content statements about these works are background knowledge and must be re-verified before they appear in any report.
- **Unverified**: mentioned in a search result or recalled; not opened. Never cited as read.

## 1. Sources

| Key | Reference | Access | Level | What it supports in FLOW |
|---|---|---|---|---|
| braess2005 | Braess, D., Nagurney, A., Wakolbinger, T. (2005). On a Paradox of Traffic Planning (English translation of Braess 1968). *Transportation Science* 39(4):446-450. doi:10.1287/trsc.1050.0127 | Author-hosted PDF https://homepage.rub.de/Dietrich.Braess/Paradox-BNW.pdf, opened 2026-11-24, SHA-256 `921f9c2e606917ff5d2c24b58e7972bcf023e1eb1859760e032bccf43c2b0c69`, 5 pages (text extracted with pypdf) | Read | The paradox: with the extra link and total flow 6, the unique critical (equilibrium) flow has path flows 2, 2, 2 and travel time 92; it does not coincide with the optimal flow; eliminating the link makes the critical flow coincide with the optimal flow. |
| braess1968 | Braess, D. (1968). Über ein Paradoxon aus der Verkehrsplanung. *Unternehmensforschung* 12(1):258-268. doi:10.1007/BF01918335 | Crossref, 2026-11-24 | Metadata verified | Original German paper; cited through the translation. |
| nagurney_boyce2005 | Nagurney, A., Boyce, D. (2005). Preface to "On a Paradox of Traffic Planning". *Transportation Science* 39(4):443-445. doi:10.1287/trsc.1050.0126 | Crossref, 2026-11-24 | Metadata verified | Context only. |
| supernet_braess | Nagurney, A. The Braess Paradox (web page, Virtual Center for Supernetworks, UMass Amherst). https://supernet.isenberg.umass.edu/facts/braess.html | Opened 2026-11-24 | Read | The canonical numerical example used in EXP-001: link costs 10f_a, f_b+50, f_c+50, 10f_d, added link f_e+10; demand 6; path cost 83 before and 92 after adding the link. |
| roughgarden_tardos2002 | Roughgarden, T., Tardos, E. (2002). How bad is selfish routing? *Journal of the ACM* 49(2):236-259. doi:10.1145/506147.506153 | Author preprint https://theory.stanford.edu/~tim/papers/routing.pdf (dated 5 December 2001), opened 2026-11-24, SHA-256 `886704f95ab8d800d0c8c29094a207afdbbc42cda34dda6f71c4d913400f24a5`, 26 pages; abstract and introduction read. Publisher page returned HTTP 403. | Read (preprint, abstract and introduction) | With linear latencies, the total latency of selfish routing is at most 4/3 of the minimum; with continuous nondecreasing latencies it can be arbitrarily worse, but is no more than the optimal latency of routing twice the traffic. Motivates the price-of-anarchy metric and the expectation that FLOW's linear Braess network has a ratio of at most 4/3. Journal-version wording not yet checked against the preprint. |
| youn2008 | Youn, H., Gastner, M. T., Jeong, H. (2008). Price of Anarchy in Transportation Networks: Efficiency and Optimality Control. *Physical Review Letters* 101(12):128701. doi:10.1103/PhysRevLett.101.128701; arXiv:0712.1598 | arXiv abstract page https://arxiv.org/abs/0712.1598, opened 2026-11-24 | Abstract read | Price of anarchy measured on city road networks; closing certain streets can reduce travel time. Related work only; FLOW makes no city claim. |
| wardrop1952 | Wardrop, J. G. (1952). Some theoretical aspects of road traffic research. *Proceedings of the Institution of Civil Engineers* 1(3):325-362. doi:10.1680/ipeds.1952.11259 | Crossref, 2026-11-24 | Metadata verified | Source of the user-equilibrium and system-optimum principles (content not re-read this session). |
| beckmann1955 | Beckmann, M. J., McGuire, C. B., Winsten, C. B. (1955). *Studies in the Economics of Transportation*. RAND Corporation, RM-1488. https://www.rand.org/pubs/research_memoranda/RM1488.html | Product page opened 2026-11-24 (free PDF offered, "noncommercial use only"; reposting prohibited) | Metadata verified | Convex (Beckmann) formulation of user equilibrium. Link only; never redistribute the PDF. |
| frank_wolfe1956 | Frank, M., Wolfe, P. (1956). An algorithm for quadratic programming. *Naval Research Logistics Quarterly* 3(1-2):95-110. doi:10.1002/nav.3800030109 | Crossref, 2026-11-24 | Metadata verified | Frank-Wolfe algorithm used for UE and SO. |
| leblanc1975 | LeBlanc, L. J., Morlok, E. K., Pierskalla, W. P. (1975). An efficient approach to solving the road network equilibrium traffic assignment problem. *Transportation Research* 9(5):309-318. doi:10.1016/0041-1647(75)90030-1 | Crossref, 2026-11-24 | Metadata verified | Frank-Wolfe applied to traffic assignment. |
| sheffi1985 | Sheffi, Y. (1985). *Urban Transportation Networks: Equilibrium Analysis with Mathematical Programming Methods*. Prentice-Hall. Author page https://web.mit.edu/sheffi/www/urbanTransportation-copyright.html | Copyright page opened 2026-11-24: the copyright holder grants "permission to any person to copy any and all parts of this book for use in education, research, consulting, planning, or any other activity" without royalty; third-party material excluded | Metadata verified (book text not opened) | Textbook reference for UE/SO formulations, relative gap and the BPR function. To read at M1. |
| steinberg_zangwill1983 | Steinberg, R., Zangwill, W. I. (1983). The prevalence of Braess' paradox. *Transportation Science* 17(3):301-318. doi:10.1287/trsc.17.3.301 | Crossref, 2026-11-24 | Metadata verified | Prevalence of the paradox; a search snippet states it is "about as likely to occur as not" under their assumptions (unverified). |
| valiant_roughgarden2010 | Valiant, G., Roughgarden, T. (2010). Braess's paradox in large random graphs. *Random Structures and Algorithms* 37(4):495-515. doi:10.1002/rsa.20325 | Crossref, 2026-11-24 | Metadata verified | Paradox likely in dense random graphs (claim from search snippets, unverified). |
| roughgarden2004 | Roughgarden, T. (2004). Stackelberg scheduling strategies. *SIAM Journal on Computing* 33(2):332-350. doi:10.1137/S0097539701397059 | Crossref, 2026-11-24 | Metadata verified | Partial central control of a fraction of traffic; related to the compliance arm in EXP-004 (relation to be checked against the full text at M1). |
| harker1988 | Harker, P. T. (1988). Multiple equilibrium behaviors on networks. *Transportation Science* 22(1):39-46. doi:10.1287/trsc.22.1.39 | Crossref, 2026-11-24 | Metadata verified | Mixed user-equilibrium and system-optimal behaviour classes; related to EXP-004 (to read at M1). |
| bpr | Bureau of Public Roads link performance function `t = t0 (1 + 0.15 (v/c)^4)`. | Only secondary sources seen in search results (National Academies Press OpenBook, an R package); the 1964 original manual was not found | Unverified | Grid cost function. The parameter values are standard practice; the primary attribution remains unverified and must be cited as such or replaced by Sheffi (1985) after reading. |
| chung_young_zhao | Chung, F., Young, S. J., Zhao, W. Braess's paradox in expanders. https://mathweb.ucsd.edu/~fan/wp/braess_rsa.pdf | Search result only | Unverified | Not cited. |

## 2. Known work and FLOW's narrow contribution

Known: Braess's example (equilibrium cost 83 without the extra link, 92 with it, demand 6); the price-of-anarchy bound of 4/3 for linear latencies; theoretical and empirical evidence that the paradox is not rare (to be verified). Standard solution methods for UE and SO (Frank-Wolfe on the Beckmann objective and on total cost).

FLOW does not claim a new theoretical result. Its proposed contribution is narrow and practical:

1. a small, fully reproducible, tested open-source-available engine that reproduces the analytic Braess example exactly and checks the closed-form demand interval for the paradox in that network;
2. a pre-registered, multi-seed measurement of the UE-to-SO gap and the free-flow baseline gap on seeded BPR grids at matched demand levels, with paired uncertainty and a solver-tolerance sensitivity check that could expose the gap as a convergence artefact;
3. a compliance sweep (a fraction of demand routed system-optimally) and a capacity sweep on the same instances;
4. an interactive static page that keeps measured, sandbox and hypothetical results visibly separate.

Novelty is not claimed. Whether grid-specific prevalence results already exist was not established by the M0 search (one search found no grid-specific study; that is not evidence of absence).

## 3. Open reading list for M1

- Full text of Roughgarden and Tardos (journal version), Sheffi (1985) chapters on UE, SO and the relative gap, Roughgarden (2004) and Harker (1988) for the compliance arm.
- Steinberg and Zangwill (1983) and Valiant and Roughgarden (2010) for prevalence claims.
- A primary or authoritative source for the BPR function parameters.

## 4. M4 additions (2026-11-25)

| Key | Reference | Access | Level | What it supports in FLOW |
|---|---|---|---|---|
| tntp_siouxfalls_readme | Transportation Networks for Research Core Team. `SiouxFalls/README.md` at commit `d1639b4ef218c17928ba573e806ddf8ba5e7ae6d`, https://github.com/bstabler/TransportationNetworks | Fetched 2026-11-25 (4,581 bytes, SHA-256 `ebe1f3dcca4736ca55a059ad82275a2c37489c3c5df915713c518635086054c1`), kept outside the repository | Read | "WARNING: The Sioux-Falls network is not considered as a realistic one. However, this network was used in many publications. It is good for code debugging."; free-flow times in 0.01 hours; the "traditional" BPR value B = 0.15 is assumed; network data taken from LeBlanc, Morlok and Pierskalla (1975). |

**Evidence-audit note.** The quotation "not considered as a realistic one" appeared in `research/limitations.md` and the EXP-006 report from M3 without a recorded access entry. The M4 evidence audit fetched the README at the pinned commit and confirmed the wording (finding F-3 in `research/publication/evidence_audit.md`). The root README (licence text) was read on 2026-11-24 (D-010).

**Manuscript citation levels (M4).** Content statements rest only on sources at level "Read" (braess2005, supernet_braess, roughgarden_tardos2002 preprint abstract and introduction, TNTP READMEs) or "Abstract read" (youn2008, labelled as abstract-only). wardrop1952, beckmann1955, frank_wolfe1956, leblanc1975, roughgarden2004 and harker1988 are cited for attribution only and labelled "metadata verified, text not read". sheffi1985, steinberg_zangwill1983, valiant_roughgarden2010 and the BPR manual are not cited.
