"""CLI: read a docker-compose file and `docker save` each service image to a directory."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def load_compose(path: Path) -> dict:
    with path.open("r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not look like a valid compose file")
    return data


def collect_images(compose: dict) -> tuple[list[str], list[str]]:
    """Return (images, skipped_service_names) from a parsed compose dict."""
    services = compose.get("services") or {}
    images: list[str] = []
    skipped: list[str] = []
    seen: set[str] = set()

    for name, config in services.items():
        if not isinstance(config, dict):
            continue
        image = config.get("image")
        if not image:
            skipped.append(name)
            continue
        if image not in seen:
            seen.add(image)
            images.append(image)

    return images, skipped


def sanitize_filename(image: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", image) + ".tar"


def save_image(image: str, out_path: Path, dry_run: bool = False) -> None:
    if dry_run:
        print(f"[dry-run] docker save -o {out_path} {image}")
        return
    subprocess.run(["docker", "save", "-o", str(out_path), image], check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="docker-images-saver",
        description="Save all image referenced in a docker-compose file to a directory as tar files.",
    )
    parser.add_argument("compose_file", type=Path, help="Path to docker-compose YAML file")
    parser.add_argument("out_dir", type=Path, help="Directory to save image tar files into")
    parser.add_argument(
        "-f", "--force", action="store_true", help="Re-save images even if the tar file already exists"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be done without running docker save"
    )
    args = parser.parse_args(argv)

    if not args.compose_file.is_file():
        parser.error(f"compose file not found: {args.compose_file}")

    if shutil.which("docker") is None and not args.dry_run:
        parser.error("docker executable not found in PATH")

    compose = load_compose(args.compose_file)
    images, skipped = collect_images(compose)

    if skipped:
        print(f"Warning: skipping {len(skipped)} service(s) with no image: {', '.join(skipped)}", file=sys.stderr)

    if not images:
        print("No images found in compose file.", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    for image in images:
        out_path = args.out_dir / sanitize_filename(image)
        if out_path.exists() and not args.force:
            print(f"Skip (already exists): {image} -> {out_path}")
            continue
        print(f"Saving: {image} -> {out_path}")
        try:
            save_image(image, out_path, dry_run=args.dry_run)
        except subprocess.CalledProcessError as e:
            print(f"Failed to save {image}: {e}", file=sys.stderr)
            failures.append(image)

    if failures:
        print(f"\n{len(failures)} image(s) failed: {', '.join(failures)}", file=sys.stderr)
        return 1

    print(f"\nDone. Saved {len(images) - len(failures)} image(s) to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
