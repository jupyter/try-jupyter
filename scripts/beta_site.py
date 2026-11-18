#!/usr/bin/env python3
"""
Post-build script for the beta site, built into a subfolder of the stable site.

This script appends " (beta)" to the application name, and makes the beta site
load the xeus kernel packages of the stable site, so that both sites fit in the
size limit of GitHub Pages. The beta site keeps its own copy of the kernel
binaries and logos, which jupyterlite-xeus looks up relative to the site.
"""

import argparse
import json
import os
import shutil
from pathlib import Path

SUFFIX = " (beta)"

# The LFortran kernel binary alone takes 77 MB, more than the size limit leaves.
SKIPPED_KERNELS = {"fortran"}


def mark_beta(beta_dir: Path) -> None:
    """Append the beta suffix to the application name of the site."""
    config_file = beta_dir / "jupyter-lite.json"
    config = json.loads(config_file.read_text())
    data = config["jupyter-config-data"]
    name = data.get("appName", "JupyterLite")
    if not name.endswith(SUFFIX):
        data["appName"] = name + SUFFIX
        config_file.write_text(json.dumps(config, indent=2))
    print(f"Application name: {data['appName']}")


def reuse_stable_kernels(stable_dir: Path, beta_dir: Path) -> None:
    """Point the xeus kernels of the beta site at the environments of the stable site."""
    stable_xeus = stable_dir / "xeus"
    beta_xeus = beta_dir / "xeus"
    kernels_file = stable_xeus / "kernels.json"
    if not kernels_file.exists():
        print(f"Warning: {kernels_file} not found, the beta site gets no xeus kernels")
        return

    kernels = json.loads(kernels_file.read_text())
    kernels = [k for k in kernels if k["kernel"] not in SKIPPED_KERNELS]
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
    reuse_stable_kernels(args.stable_dir, args.beta_dir)
    print("Done!")


if __name__ == "__main__":
    main()
