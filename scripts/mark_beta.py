#!/usr/bin/env python3
"""
Post-build script to mark a JupyterLite site as the beta deployment.

This script appends " (beta)" to the application name, which shows in the
browser tab titles and in the About dialog of the site.
"""

import argparse
import json
from pathlib import Path

SUFFIX = " (beta)"


def mark_beta(dist_dir: Path) -> None:
    """Append the beta suffix to the application name of the site."""
    config_file = dist_dir / "jupyter-lite.json"
    config = json.loads(config_file.read_text())
    data = config["jupyter-config-data"]
    name = data.get("appName", "JupyterLite")

    if not name.endswith(SUFFIX):
        data["appName"] = name + SUFFIX
        config_file.write_text(json.dumps(config, indent=2))

    print(f"Application name in {config_file}: {data['appName']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mark the built JupyterLite site as the beta deployment."
    )
    parser.add_argument(
        "dist_dir",
        type=Path,
        help="Path to the dist directory containing the built JupyterLite site",
    )
    args = parser.parse_args()

    dist_dir = args.dist_dir

    if not dist_dir.exists():
        print(f"Error: dist directory not found at {dist_dir}")
        print("Please build the beta site first.")
        return

    mark_beta(dist_dir)
    print("Done!")


if __name__ == "__main__":
    main()
