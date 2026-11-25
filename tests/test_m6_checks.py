# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""M6 release-candidate checks (scripts/m6_checks.py): links, numbers, manifests, CITATION.cff."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    spec = importlib.util.spec_from_file_location("m6_checks", ROOT / "scripts" / "m6_checks.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_every_relative_link_resolves():
    assert _mod().check_links() == []


def test_readme_and_article_numbers_are_in_the_manuscript():
    assert _mod().check_numbers() == []


def test_manifest_paths_and_local_data_hashes():
    assert _mod().check_manifests() == []


def test_citation_cff_is_a_release_candidate_without_release_date():
    assert _mod().check_cff() == []


def test_link_parser_finds_links_and_anchors(tmp_path):
    m = _mod()
    md = tmp_path / "a.md"
    md.write_text("# Top title\n\n## 2. Results, in brief\n\nSee [x](b.md#top) and ![img](f.png).\n\n"
                  "```\n[not](a link)\n```\n`[nor](this)`\n")
    assert m.links_in(md) == ["b.md#top", "f.png"]
    assert {"top-title", "2-results-in-brief"} <= m.anchors(md)


def test_number_pattern_and_brace_expansion():
    m = _mod()
    assert m.NUM_RE.findall("median 0.02317, [0.678, 0.842], 1e-10 and 7.53e-9; 5,154 solves") == [
        "0.02317", "0.678", "0.842", "1e-10", "7.53e-9"]
    assert m._expand("x/EXP-00{1..3}/a") == ["x/EXP-001/a", "x/EXP-002/a", "x/EXP-003/a"]


def test_pdf_source_promotes_the_title(tmp_path):
    from flow.report import typst_source

    md = tmp_path / "r.md"
    md.write_text("<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->\n# A title\n\n## Section\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    typ, root = typst_source(md)
    text = typ.read_text()
    typ.unlink()
    assert "title: [A title]" in text and root == tmp_path
    assert "#show figure: set block(breakable: true)" in text
