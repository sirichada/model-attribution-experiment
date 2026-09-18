"""Clone SWE-bench/experiments (metadata only) into data/raw/.

Not committed (data/raw/ is gitignored) — this is an external metadata source,
re-cloned/pulled on demand, not a project artifact.
"""


import subprocess
from pathlib import Path

REPO_URL = "https://github.com/SWE-bench/experiments.git"
DEST = Path(__file__).resolve().parent.parent / "data" / "raw" / "swe-bench-experiments"


def fetch():
    if DEST.exists():
        print(f"{DEST} already exists, pulling latest instead of re-cloning.")
        subprocess.run(["git", "pull"], cwd=DEST, check=True)
        return
    DEST.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(DEST)], check=True)


if __name__ == "__main__":
    fetch()
