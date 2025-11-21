"""Tests for JupyterLite notebooks execution."""

from pathlib import Path
from urllib.parse import quote

import pytest
from playwright.sync_api import Page

from utils import (
    check_for_errors,
    execute_all_cells,
    wait_for_jupyterlite_ready,
    wait_for_notebook_ready,
)

# Auto-discover all notebooks in content/notebooks/
CONTENT_DIR = Path(__file__).parent.parent / "content" / "notebooks"
NOTEBOOKS = sorted(CONTENT_DIR.glob("*.ipynb"))
TIMEOUT = 300_000

if not NOTEBOOKS:
    pytest.fail(f"No notebooks found in {CONTENT_DIR}")


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda p: p.stem)
def test_notebook_execution(page: Page, base_url: str, notebook_path: Path) -> None:
    # Construct the URL to open the notebook
    # JupyterLite URL format: /lab/index.html?path=notebooks/NotebookName.ipynb
    relative_path = notebook_path.relative_to(notebook_path.parent.parent)
    notebook_url = f"{base_url}/lab/index.html?path={quote(str(relative_path))}"

    page.goto(notebook_url, wait_until="networkidle", timeout=60000)

    wait_for_jupyterlite_ready(page, timeout=60000)

    wait_for_notebook_ready(page, timeout=60000)

    execute_all_cells(page, notebook_name=notebook_path.name, timeout=TIMEOUT)

    errors = check_for_errors(page, notebook_name=notebook_path.name)

    # Take screenshot on failure for debugging
    if errors:
        screenshot_path = Path(__file__).parent / f"screenshot_{notebook_path.stem}.png"
        page.screenshot(path=str(screenshot_path))

    # Assert no errors were found
    assert not errors, (
        f"Notebook '{notebook_path.name}' execution failed with errors:\n"
        + "\n---\n".join(errors)
    )
