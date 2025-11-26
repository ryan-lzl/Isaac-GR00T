"""Generate meta/tasks.jsonl from meta/tasks.parquet for SO-100/101 datasets.

LeRobot datasets sometimes include only meta/tasks.parquet. This script converts
that Parquet file into a JSONL mapping that gr00t expects:
    {"task_index": <int>, "task": "<description>"}
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd


def infer_task_column(df: pd.DataFrame) -> str:
    """Pick the column that holds the task text."""
    if "task" in df.columns:
        return "task"
    non_index_cols = [c for c in df.columns if c != "task_index"]
    if len(non_index_cols) == 1:
        return non_index_cols[0]
    if len(df.columns) == 1 and df.index.name is None and df.index.dtype == object:
        # Only task_index column present; tasks live in the index.
        return ""
    raise ValueError(f"Unable to infer task text column from columns={df.columns}")


def build_tasks_jsonl(dataset_path: Path) -> int:
    tasks_parquet = dataset_path / "meta" / "tasks.parquet"
    out_path = dataset_path / "meta" / "tasks.jsonl"
    if not tasks_parquet.exists():
        raise FileNotFoundError(f"Missing {tasks_parquet}")

    df = pd.read_parquet(tasks_parquet)
    task_col = infer_task_column(df)

    df_reset = df.reset_index()
    task_field = df_reset.columns[0] if task_col == "" else task_col

    rows = []
    for _, row in df_reset.iterrows():
        task_text = str(row[task_field])
        task_index = int(row["task_index"]) if "task_index" in row else int(row[df_reset.columns[0]])
        rows.append({"task_index": task_index, "task": task_text})

    with open(out_path, "w") as f:
        for obj in rows:
            f.write(json.dumps(obj))
            f.write("\n")

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create meta/tasks.jsonl from meta/tasks.parquet"
    )
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=os.environ.get("DATASET_PATH"),
        help="Path to dataset root (containing meta/tasks.parquet). Can also use DATASET_PATH env var.",
    )
    args = parser.parse_args()

    if args.dataset_path is None:
        raise SystemExit("Please provide --dataset-path or set DATASET_PATH")

    count = build_tasks_jsonl(args.dataset_path)
    print(f"Wrote {count} tasks to {args.dataset_path / 'meta' / 'tasks.jsonl'}")


if __name__ == "__main__":
    main()
