"""Render every dashboard page headlessly - catches broken pages before a demo."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PAGES = sorted(str(p) for p in (Path(__file__).resolve().parents[1] / "views").glob("*.py"))


@pytest.mark.parametrize("page", PAGES, ids=lambda p: Path(p).stem)
def test_page_renders(page):
    at = AppTest.from_file(page, default_timeout=60).run()
    assert not at.exception, [e.value for e in at.exception]
