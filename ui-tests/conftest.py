"""Pytest configuration and fixtures for JupyterLite UI tests."""

import socket
import subprocess
import time
from pathlib import Path

import pytest


def find_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture(scope="session")
def dist_dir() -> Path:
    """Return path to the built JupyterLite distribution."""
    dist_path = Path(__file__).parent.parent / "dist"
    if not dist_path.exists():
        pytest.fail(
            f"Distribution directory not found: {dist_path}\n"
            "Please run 'pixi run build' first to build the JupyterLite site."
        )
    return dist_path


@pytest.fixture(scope="session")
def server_port() -> int:
    """Get a free port for the test server."""
    return find_free_port()


@pytest.fixture(scope="session", autouse=True)
def http_server(dist_dir: Path, server_port: int):
    """Start HTTP server serving the built JupyterLite site."""
    process = subprocess.Popen(
        ["python", "-m", "http.server", str(server_port), "--directory", str(dist_dir)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    time.sleep(1)

    if process.poll() is not None:
        pytest.fail(f"Failed to start HTTP server on port {server_port}")

    yield process

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="session")
def base_url(server_port: int) -> str:
    """Return the base URL for accessing JupyterLite."""
    return f"http://localhost:{server_port}"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with video recording on failure."""
    videos_dir = Path(__file__).parent / "videos"
    videos_dir.mkdir(exist_ok=True)

    return {
        **browser_context_args,
        "record_video_dir": str(videos_dir),
        "record_video_size": {"width": 1280, "height": 720},
    }
