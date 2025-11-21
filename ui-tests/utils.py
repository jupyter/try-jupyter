"""Utility functions for JupyterLite notebook testing."""

from playwright.sync_api import Page


def wait_for_kernel_success(page: Page, timeout: int = 30000) -> None:
    page.wait_for_selector(".jp-KernelStatus-success", timeout=timeout, state="attached")


def wait_for_jupyterlite_ready(page: Page, timeout: int = 30000) -> None:
    page.wait_for_selector("#jp-main-dock-panel", timeout=timeout)
    wait_for_kernel_success(page, timeout)


def wait_for_notebook_ready(page: Page, timeout: int = 30000) -> None:
    page.wait_for_selector(".jp-Cell", timeout=timeout)
    wait_for_kernel_success(page, timeout)


def execute_all_cells(page: Page, timeout: int = 300000) -> None:
    page.click('text="Run"')
    page.click('text="Run All Cells"')

    page.wait_for_timeout(1000)

    # Monitor for input prompts and wait for execution to complete
    start_time = page.evaluate("Date.now()")
    while True:
        # Check if there's an input prompt
        input_prompt = page.locator(".jp-Stdin-input")
        if input_prompt.count() > 0:
            # Type a default response and press enter
            page.keyboard.type("test_input")
            page.keyboard.press("Enter")
            # Wait briefly for the input to be processed
            page.wait_for_timeout(500)

        # Check if all cells have finished executing by looking at the last code cell
        code_cells = page.locator(".jp-CodeCell")
        if code_cells.count() > 0:
            # Get the last code cell's execution prompt
            last_cell = code_cells.last
            last_prompt = last_cell.locator(".jp-InputArea-prompt")
            prompt_text = last_prompt.inner_text().strip()

            # Check if it has an execution count (e.g., "[1]:", "[2]:", etc.)
            if prompt_text and prompt_text != "[ ]:" and "*" not in prompt_text:
                # Also verify kernel execution completed successfully
                try:
                    wait_for_kernel_success(page, timeout=0)
                    break
                except:
                    # continue waiting
                    pass

        # Check timeout
        elapsed = page.evaluate("Date.now()") - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Notebook execution timed out after {timeout}ms")

        # Wait a bit before checking again
        page.wait_for_timeout(500)


def check_for_errors(
    page: Page, known_warnings: list[str] | None = None
) -> list[str]:
    if known_warnings is None:
        known_warnings = [
            "Matplotlib is building the font cache; this may take a moment.",
            "some error",
            "Attaching package:",
        ]

    errors = []

    # Look for stderr outputs in cells
    stderr_outputs = page.locator(".jp-OutputArea-output[data-mime-type='application/vnd.jupyter.stderr']")

    for i in range(stderr_outputs.count()):
        stderr_text = stderr_outputs.nth(i).inner_text().strip()

        if not stderr_text:
            continue

        # Check if this stderr matches any known warning to filter
        is_known_warning = any(warning in stderr_text for warning in known_warnings)

        if not is_known_warning:
            errors.append(stderr_text)

    return errors
