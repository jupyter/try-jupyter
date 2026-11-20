#!/usr/bin/env python3
"""
Post-build script for the beta site, built into a subfolder of the stable site.

This script appends " (beta)" to the application name, adds a Beta badge and a
Report a Problem button to the top bar, and makes the beta site load the xeus
kernel packages of the stable site, so that both sites fit in the size limit of
GitHub Pages. The beta site keeps its own copy of the kernel binaries and logos,
which jupyterlite-xeus looks up relative to the site.
"""

import argparse
import json
import os
import shutil
from pathlib import Path

SUFFIX = " (beta)"
TOP_BAR = "@jupyterlab/application-extension:top-bar"
BADGE_STYLE = """<style>
  #jp-top-bar [data-jp-item-name="beta"] .jp-ToolbarButtonComponent-label {
    padding: 2px 6px;
    border-radius: 9px;
    background: var(--jp-warn-color1, #f57c00);
    color: #000;
    font-size: var(--jp-ui-font-size0);
    font-weight: 600;
    letter-spacing: 0.05em;
    line-height: normal;
    text-transform: uppercase;
  }
</style>
"""


def mark_beta(beta_dir: Path) -> None:
    """Mark the site as the beta in its application name and its top bar."""
    config_file = beta_dir / "jupyter-lite.json"
    config = json.loads(config_file.read_text())
    data = config["jupyter-config-data"]
    name = data.get("appName", "JupyterLite")
    if not name.endswith(SUFFIX):
        data["appName"] = name + SUFFIX

    versions = [f"JupyterLite {data.get('appVersion', 'unknown')}"]
    for info in data.get("versionInfo", {}).values():
        versions.append(f"{info['label']} {info['version']}")
    items = [
        {
            "name": "beta",
            "command": "application:about",
            "label": "Beta",
            "caption": ", ".join(versions),
            "rank": 60,
        },
        # The toolbar hides this item when the feedback extension is not installed.
        {
            "name": "report-problem",
            "command": "try-jupyter:report-problem",
            "label": "Report a Problem",
            "icon": "ui-components:bug",
            "rank": 61,
        },
    ]
    overrides = data.setdefault("settingsOverrides", {})
    toolbar = overrides.setdefault(TOP_BAR, {}).setdefault("toolbar", [])
    names = {item["name"] for item in items}
    toolbar[:] = [item for item in toolbar if item.get("name") not in names] + items

    config_file.write_text(json.dumps(config, indent=2))
    print(f"Application name: {data['appName']}, top bar items: {sorted(names)}")


def style_badge(beta_dir: Path) -> None:
    """Add the style of the Beta badge to the page of every app."""
    pages = sorted(beta_dir.glob("*/index.html"))
    for page in pages:
        html = page.read_text()
        if BADGE_STYLE not in html:
            page.write_text(html.replace("</head>", BADGE_STYLE + "</head>", 1))
    print(f"Badge style in: {[page.parent.name for page in pages]}")


def reuse_stable_kernels(stable_dir: Path, beta_dir: Path) -> None:
    """Point the xeus kernels of the beta site at the environments of the stable site."""
    stable_xeus = stable_dir / "xeus"
    beta_xeus = beta_dir / "xeus"
    kernels_file = stable_xeus / "kernels.json"
    if not kernels_file.exists():
        print(f"Warning: {kernels_file} not found, the beta site gets no xeus kernels")
        return

    kernels = json.loads(kernels_file.read_text())
    # jupyterlite-xeus joins the environment name to the site URL, so this
    # relative name reaches the environment folders of the stable site.
    prefix = os.path.relpath(stable_xeus, beta_xeus)
    for kernel in kernels:
        env_name = kernel["env_name"]
        # Kernel binaries and logos are looked up relative to the beta site.
        sources = [stable_xeus / env_name / "bin"]
        sources += sorted((stable_xeus / env_name / kernel["kernel"]).glob("logo-*"))
        for source in sources:
            target = beta_xeus / source.relative_to(stable_xeus)
            if source.is_dir():
                shutil.copytree(source, target, dirs_exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        kernel["env_name"] = f"{prefix}/{env_name}"

    beta_xeus.mkdir(parents=True, exist_ok=True)
    (beta_xeus / "kernels.json").write_text(json.dumps(kernels))
    print(f"Kernels from the stable site: {[k['kernel'] for k in kernels]}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Finish the beta JupyterLite site that sits inside the stable one."
    )
    parser.add_argument("stable_dir", type=Path, help="Path to the built stable site")
    parser.add_argument("beta_dir", type=Path, help="Path to the built beta site")
    args = parser.parse_args()

    for path in (args.stable_dir, args.beta_dir):
        if not path.exists():
            print(f"Error: directory not found at {path}")
            return

    mark_beta(args.beta_dir)
    style_badge(args.beta_dir)
    reuse_stable_kernels(args.stable_dir, args.beta_dir)
    print("Done!")


if __name__ == "__main__":
    main()
