<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Release checklist (M6)

Status: not started. Every box is ticked only with the command and its recorded output in `progress.md`.

- [ ] Owner froze every confirmatory protocol (hashes in `research/decision_log.md`).
- [ ] Every registered experiment has a standalone report (status visible: completed, failed, null, exploratory or abandoned).
- [ ] Clean clone into a separate directory; `uv sync --frozen`; `uv run pytest` passes (count recorded).
- [ ] Smoke reproduction in the clean clone matches recorded results within tolerance.
- [ ] Demo builds and works offline after first load.
- [ ] `data/manifest.json` complete; no non-redistributable data bundled.
- [ ] Claims audit complete (`claims_audit.md`); every number maps to a result id.
- [ ] Manuscript and report PDFs compiled (pandoc to Typst) and visually inspected.
- [ ] Links and cross-references checked.
- [ ] Secret, e-mail and personal-identifier scan clean.
- [ ] Licence headers present; third-party licences recorded.
- [ ] `author_review.md` completed by the owner.
- [ ] Owner approval for any publication (G-PUBLIC). Nothing pushed before that.
