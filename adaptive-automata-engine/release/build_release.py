"""
Release Packaging Automation Script.
Assembles clean, reproducible release artifacts into the release/ directory.
"""

import os
import shutil


def build_release():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    release_dir = os.path.join(base_dir, "release")

    print(f"Assembling Clean Release Package at: {release_dir}")

    # Directories to create
    subdirs = [
        "source",
        "configs",
        "results",
        "figures",
        "documentation",
        "reproducibility",
        "demo",
    ]

    for sd in subdirs:
        os.makedirs(os.path.join(release_dir, sd), exist_ok=True)

    # Copy Source
    src_dir = os.path.join(base_dir, "src")
    if os.path.exists(src_dir):
        dest_src = os.path.join(release_dir, "source", "src")
        if os.path.exists(dest_src):
            shutil.rmtree(dest_src)
        shutil.copytree(src_dir, dest_src, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # Copy Configs
    cfg_dir = os.path.join(base_dir, "configs")
    if os.path.exists(cfg_dir):
        dest_cfg = os.path.join(release_dir, "configs")
        for item in os.listdir(cfg_dir):
            shutil.copy2(os.path.join(cfg_dir, item), os.path.join(dest_cfg, item))

    # Copy Results
    res_dir = os.path.join(base_dir, "experiments", "results")
    if os.path.exists(res_dir):
        dest_res = os.path.join(release_dir, "results")
        for item in os.listdir(res_dir):
            shutil.copy2(os.path.join(res_dir, item), os.path.join(dest_res, item))

    # Copy Figures
    plots_dir = os.path.join(base_dir, "experiments", "plots")
    if os.path.exists(plots_dir):
        dest_plots = os.path.join(release_dir, "figures")
        for item in os.listdir(plots_dir):
            shutil.copy2(os.path.join(plots_dir, item), os.path.join(dest_plots, item))

    # Copy Documentation
    docs_dir = os.path.join(base_dir, "docs")
    if os.path.exists(docs_dir):
        dest_docs = os.path.join(release_dir, "documentation")
        for item in os.listdir(docs_dir):
            if os.path.isfile(os.path.join(docs_dir, item)):
                shutil.copy2(os.path.join(docs_dir, item), os.path.join(dest_docs, item))

    # Copy Demo
    demo_file = os.path.join(base_dir, "examples", "final_demo.py")
    if os.path.exists(demo_file):
        shutil.copy2(demo_file, os.path.join(release_dir, "demo", "final_demo.py"))

    print("Release package successfully built:")
    for sd in subdirs:
        pth = os.path.join(release_dir, sd)
        count = len(os.listdir(pth)) if os.path.exists(pth) else 0
        print(f" -> release/{sd:<15} ({count} items)")


if __name__ == "__main__":
    build_release()
