#!/usr/bin/env python3
"""
Post-build script to filter xeus kernels.

This script modifies the built JupyterLite site to only include
the selected kernels (C++23, R, Python, SQLite) from the xeus kernels list.
"""

import argparse
import json
from pathlib import Path

# Kernels to keep
KERNELS_TO_KEEP = {"xcpp23", "xc23", "xr", "xpython", "xsqlite"}


def filter_kernels(dist_dir: Path) -> None:
    """Filter the xeus kernels to only keep the selected kernels."""
    xeus_dir = dist_dir / "xeus"
    kernels_file = xeus_dir / "kernels.json"

    if not kernels_file.exists():
        print(f"Warning: {kernels_file} not found, skipping kernel filtering")
        return

    with open(kernels_file) as f:
        kernels = json.load(f)

    print(f"Found {len(kernels)} kernels: {[k['kernel'] for k in kernels]}")

    filtered_kernels = [k for k in kernels if k["kernel"] in KERNELS_TO_KEEP]

    print(f"Keeping {len(filtered_kernels)} kernels: {[k['kernel'] for k in filtered_kernels]}")

    with open(kernels_file, "w") as f:
        json.dump(filtered_kernels, f)

    print(f"Updated {kernels_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Filter xeus kernels to only keep selected kernels (C++23, R, Python, SQLite)."
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
        print("Please run 'pixi run build' first.")
        return

    filter_kernels(dist_dir)
    print("Done!")


if __name__ == "__main__":
    main()
