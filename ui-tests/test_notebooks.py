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

if not NOTEBOOKS:
    pytest.fail(f"No notebooks found in {CONTENT_DIR}")


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda p: p.stem)
def test_notebook_execution(page: Page, base_url: str, notebook_path: Path) -> None:
    """Test that a notebook executes without errors in JupyterLite.

    Args:
        page: Playwright page fixture
        base_url: Base URL of the JupyterLite server
        notebook_path: Path to the notebook file to test
    """
    # Construct the URL to open the notebook
    # JupyterLite URL format: /lab/index.html?path=notebooks/NotebookName.ipynb
    relative_path = notebook_path.relative_to(notebook_path.parent.parent)
    notebook_url = f"{base_url}/lab/index.html?path={quote(str(relative_path))}"

    # Navigate to the notebook
    page.goto(notebook_url, wait_until="networkidle", timeout=60000)

    # Wait for JupyterLite to be ready
    wait_for_jupyterlite_ready(page, timeout=60000)

    # Wait for the notebook to be loaded
    wait_for_notebook_ready(page, timeout=60000)

    # Execute all cells in the notebook
    execute_all_cells(page, timeout=180000)  # 3 minutes for execution

    # Check for any errors
    errors = check_for_errors(page)

    # Take screenshot on failure for debugging
    if errors:
        screenshot_path = Path(__file__).parent / f"screenshot_{notebook_path.stem}.png"
        page.screenshot(path=str(screenshot_path))

    # Assert no errors were found
    assert not errors, (
        f"Notebook '{notebook_path.name}' execution failed with errors:\n"
        + "\n---\n".join(errors)
    )
