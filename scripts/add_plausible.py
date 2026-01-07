#!/usr/bin/env python3
"""
Post-build script to inject Plausible analytics into the JupyterLite site.

This script modifies the built JupyterLite HTML files to include
Plausible analytics tracking with hash-based routing support.
"""

import argparse
from pathlib import Path

from bs4 import BeautifulSoup

PLAUSIBLE_SRC = "https://plausible.io/js/pa-B75UO5--FNXYQSG7GBWkf.js"
PLAUSIBLE_INIT = (
    "window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},"
    "plausible.init=plausible.init||function(i){plausible.o=i||{}};"
    "plausible.init({hashBasedRouting:true})"
)


def inject_plausible(dist_dir: Path) -> None:
    """Inject Plausible analytics scripts into all HTML files."""
    html_files = list(dist_dir.rglob("*.html"))
    print(f"Found {len(html_files)} HTML files")

    for html_file in html_files:
        soup = BeautifulSoup(html_file.read_text(), "html.parser")

        head = soup.find("head")
        if not head:
            print(f"Warning: No <head> found in {html_file}, skipping")
            continue

        # Add the external Plausible script
        external_script = soup.new_tag("script")
        external_script["async"] = ""
        external_script["src"] = PLAUSIBLE_SRC
        head.append(external_script)

        # Add the inline initialization script
        init_script = soup.new_tag("script")
        init_script.string = PLAUSIBLE_INIT
        head.append(init_script)

        html_file.write_text(str(soup))
        print(f"Injected Plausible into: {html_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inject Plausible analytics into the built JupyterLite site."
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

    inject_plausible(dist_dir)
    print("Done!")


if __name__ == "__main__":
    main()
