"""Lightweight metadata-only check of two Hugging Face trajectory datasets.

Confirms model-variant count and instance-set identity without pulling full
data. No HF token required (anonymous access).
"""

from pathlib import Path

from huggingface_hub import HfApi

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "data" / "stage0_hf_datasets_notes.md"

DATASETS = ["nebius/SWE-agent-trajectories", "Multi-SWE-bench_trajs"]


def check_dataset(api: HfApi, dataset_id: str) -> str:
    lines = [f"## {dataset_id}"]
    try:
        info = api.dataset_info(dataset_id)
        lines.append(f"- private: {info.private}")
        lines.append(f"- siblings (files): {len(info.siblings) if info.siblings else 0}")
        card = getattr(info, "card_data", None)
        if card:
            lines.append(f"- card_data keys: {list(dict(card).keys())}")
    except Exception as e:
        lines.append(f"- ERROR fetching dataset_info: {e}")

    lines.append("")
    return "\n".join(lines)


def main():
    api = HfApi()
    sections = [check_dataset(api, d) for d in DATASETS]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write("# Stage 0 — HF dataset coverage notes\n\n")
        f.write(
            "Metadata-only check, not a full download. nebius/SWE-agent-trajectories's "
            "model variants appear to be near-sibling fine-tunes of one model family, "
            "not distinct commercial models.\n\n"
        )
        f.write("\n".join(sections))

    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
