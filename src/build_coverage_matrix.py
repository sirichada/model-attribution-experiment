"""Turn stage0_submissions.csv into a coverage matrix per SWE-bench variant.

Keeps models in >= K_MIN_FRAMEWORKS frameworks, then frameworks with
>= FRAMEWORKS_MIN_MODELS of those models. Reports the matrix only; does not
decide go/no-go.
"""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
IN_PATH = REPO_ROOT / "data" / "stage0_submissions.csv"
OUT_DIR = REPO_ROOT / "data"

K_MIN_FRAMEWORKS = 3
FRAMEWORKS_MIN_MODELS = 2


def build_matrix_for_variant(df: pd.DataFrame, variant: str):
    sub = df[(df["variant"] == variant) & (df["needs_readme_review"] == False)].copy()
    sub = sub[sub["model_ids"].str.len() > 0]

    if sub.empty:
        print(f"{variant}: no clean single-model submissions to build a matrix from")
        return None

    # one row per (model, submission) — model_ids is a single exact model ID here
    # since needs_readme_review filters out multi-model/ambiguous entries
    counts = sub.groupby("model_ids")["submission_id"].nunique().sort_values(ascending=False)

    retained_models = counts[counts >= K_MIN_FRAMEWORKS].index.tolist()
    print(f"\n=== {variant} ===")
    print(f"{len(counts)} distinct exact model IDs found in clean submissions")
    print(f"{len(retained_models)} models retained at k >= {K_MIN_FRAMEWORKS} frameworks")

    if not retained_models:
        print(f"{variant}: no models cleared the k >= {K_MIN_FRAMEWORKS} threshold")
        return None

    retained = sub[sub["model_ids"].isin(retained_models)]
    matrix = pd.crosstab(retained["submission_id"], retained["model_ids"])

    frameworks_with_enough_models = matrix[(matrix > 0).sum(axis=1) >= FRAMEWORKS_MIN_MODELS].index
    print(
        f"{len(frameworks_with_enough_models)} frameworks contain >= {FRAMEWORKS_MIN_MODELS} "
        f"retained models"
    )

    final_matrix = matrix.loc[matrix.index.isin(frameworks_with_enough_models)]
    return final_matrix


def main():
    df = pd.read_csv(IN_PATH)
    df["needs_readme_review"] = df["needs_readme_review"].astype(str) == "True"

    for variant in sorted(df["variant"].unique()):
        matrix = build_matrix_for_variant(df, variant)
        if matrix is None or matrix.empty:
            print(f"{variant}: empty result after filtering — does not clear Stage 0's gate on its own")
            continue
        out_path = OUT_DIR / f"stage0_coverage_matrix_{variant}.csv"
        matrix.to_csv(out_path)
        print(f"Wrote {out_path} ({matrix.shape[0]} frameworks x {matrix.shape[1]} models)")


if __name__ == "__main__":
    main()
