#!/usr/bin/env python3
"""Utility to update image tag inside a Kustomize kustomization.yaml."""

import sys
from pathlib import Path

import yaml


def update_image_tag(file_path: Path, service: str, tag: str) -> bool:
    data = yaml.safe_load(file_path.read_text()) or {}
    images = data.get("images", [])
    updated = False
    for image in images:
        if image.get("name") == f"cr.yandex/bpm-registry/{service}":
            image["newTag"] = tag
            updated = True
    if not updated:
        return False
    file_path.write_text(yaml.safe_dump(data, sort_keys=False))
    return True


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: update_image_tag.py <file> <service> <tag>", file=sys.stderr)
        return 2
    file_arg, service, tag = sys.argv[1:]
    file_path = Path(file_arg)
    if not file_path.exists():
        print(f"error: {file_path} not found", file=sys.stderr)
        return 1
    if not update_image_tag(file_path, service, tag):
        print(
            f"warning: image cr.yandex/bpm-registry/{service} not found in {file_path}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
