"""Normalize `count` fields in meta/stats.json for SO-100/101 datasets.

Some LeRobot exports store a single count value for multi-dimensional
action/state stats (e.g., `[37224]` for 6 joints). This script expands
those counts to match the length of the `mean` array so downstream
code that slices by joint indices does not crash.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def fix_counts(stats_path: Path) -> bool:
    """Expand per-dimension counts for action/state if needed."""
    with open(stats_path, "r") as f:
        data: dict[str, Any] = json.load(f)

    changed = False
    for key in ("action", "observation.state"):
        entry = data.get(key)
        if not isinstance(entry, dict):
            continue
        mean = entry.get("mean")
        count = entry.get("count")
        if not isinstance(mean, list) or count is None:
            continue
        expected_len = len(mean)

        # If already the right length, skip.
        if isinstance(count, list) and len(count) == expected_len:
            continue

        # If count is a list of length 1, repeat; otherwise, fall back to scalar.
        if isinstance(count, list) and len(count) == 1:
            value = count[0]
        else:
            value = count if not isinstance(count, list) else count[0]

        entry["count"] = [value] * expected_len
        changed = True

    if changed:
        with open(stats_path, "w") as f:
            json.dump(data, f, indent=4)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix count fields in meta/stats.json for action/state."
    )
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=os.environ.get("DATASET_PATH"),
        help="Path to dataset root (containing meta/stats.json). Can also use DATASET_PATH env var.",
    )
    args = parser.parse_args()

    if args.dataset_path is None:
        raise SystemExit("Please provide --dataset-path or set DATASET_PATH")

    stats_path = args.dataset_path / "meta" / "stats.json"
    if not stats_path.exists():
        raise SystemExit(f"stats.json not found at {stats_path}")

    changed = fix_counts(stats_path)
    if changed:
        print(f"Updated counts in {stats_path}")
    else:
        print(f"No changes needed in {stats_path}")


if __name__ == "__main__":
    main()
