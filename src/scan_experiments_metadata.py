"""Scan SWE-bench/experiments metadata.yaml files into a flat table.

Walks evaluation/{lite,verified,test}. Ambiguous model fields (missing, empty, or
multi-model) are flagged needs_readme_review rather than guessed.
"""

import csv
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = REPO_ROOT / "data" / "raw" / "swe-bench-experiments"
VARIANTS = ["lite", "verified", "test"]
OUT_PATH = REPO_ROOT / "data" / "stage0_submissions.csv"

FIELDNAMES = [
    "variant",
    "submission_id",
    "model_ids",
    "model_org",
    "agent_name",
    "assets_repo",
    "assets_trajs",
    "assets_logs",
    "retrievable",
    "needs_readme_review",
    "parse_error",
]


def is_ambiguous_model_field(model_field) -> bool:
    if model_field is None:
        return True
    if isinstance(model_field, list):
        if len(model_field) == 0:
            return True
        # more than one distinct model in a single submission usually means a
        # multi-model/routing system, not a single clean model ID
        return len(model_field) > 1
    if isinstance(model_field, str):
        stripped = model_field.strip()
        return stripped == "" or "/" in stripped or "+" in stripped
    return True


def scan_variant(variant: str):
    variant_dir = EXPERIMENTS_DIR / "evaluation" / variant
    rows = []
    if not variant_dir.exists():
        print(f"WARNING: {variant_dir} does not exist — did you run fetch_experiments_repo.py?")
        return rows

    for submission_dir in sorted(p for p in variant_dir.iterdir() if p.is_dir()):
        metadata_path = submission_dir / "metadata.yaml"
        row = {field: "" for field in FIELDNAMES}
        row["variant"] = variant
        row["submission_id"] = submission_dir.name

        if not metadata_path.exists():
            row["parse_error"] = "metadata.yaml missing"
            rows.append(row)
            continue

        try:
            with open(metadata_path) as f:
                meta = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            row["parse_error"] = f"yaml parse error: {e}"
            rows.append(row)
            continue

        tags = meta.get("tags", {}) or {}
        info = meta.get("info", {}) or {}
        assets = meta.get("assets", {}) or {}

        model_field = tags.get("model")
        row["model_ids"] = ";".join(model_field) if isinstance(model_field, list) else (model_field or "")
        row["model_org"] = tags.get("model_org", "")
        row["agent_name"] = tags.get("agent", info.get("name", ""))
        row["assets_repo"] = assets.get("repo", "") or ""
        row["assets_trajs"] = assets.get("trajs", "") or ""
        row["assets_logs"] = assets.get("logs", "") or ""
        row["retrievable"] = str(bool(row["assets_repo"] or row["assets_logs"] or row["assets_trajs"]))
        row["needs_readme_review"] = str(is_ambiguous_model_field(model_field))

        rows.append(row)

    return rows


def main():
    all_rows = []
    for variant in VARIANTS:
        variant_rows = scan_variant(variant)
        print(f"{variant}: {len(variant_rows)} submissions scanned")
        all_rows.extend(variant_rows)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    n_review = sum(1 for r in all_rows if r["needs_readme_review"] == "True")
    print(f"Wrote {len(all_rows)} rows to {OUT_PATH}")
    print(f"{n_review} rows flagged needs_readme_review")


if __name__ == "__main__":
    main()
