# Build batch task files for GitHub Pages from your dataset folder.
# Comments in English.

import json
import math
import random
from pathlib import Path

DATASET_DIR = Path("../datahost/dataset")   # local dataset root
OUT_TASKS_DIR = Path("tasks")               # put into your github.io repo
BATCH_SIZE = 25                             # trials per participant (e.g., 25)
IMAGE_REPO_RAW_BASE = "https://raw.githubusercontent.com/nature21/create_tool_use_dataset/main/dataset"

# Use a fixed seed for reproducibility. Change it when you want a new randomization.
RANDOM_SEED = 20260111

def main():
    trials = []

    # dataset/<class>/<id>.json
    for cls_dir in sorted([p for p in DATASET_DIR.iterdir() if p.is_dir()]):
        cls = cls_dir.name
        for json_path in sorted(cls_dir.glob("*.json")):
            stem = json_path.stem  # "000"
            jpg_path = cls_dir / f"{stem}.jpg"
            if not jpg_path.exists():
                continue

            data = json.loads(json_path.read_text(encoding="utf-8"))
            options = data.get("object_list", [])
            instruction = data.get("instruction", "")
            target = data.get("target", "")

            image_url = f"{IMAGE_REPO_RAW_BASE}/{cls}/{stem}.jpg"

            trials.append({
                "task_id": f"{cls}/{stem}",
                "image_url": image_url,
                "instruction": instruction,
                "options": options,
                "target": target
            })

    if not trials:
        raise RuntimeError("No trials found. Check DATASET_DIR and file naming.")

    # Shuffle so each batch mixes task classes
    rng = random.Random(RANDOM_SEED)
    rng.shuffle(trials)

    OUT_TASKS_DIR.mkdir(parents=True, exist_ok=True)

    n_batches = math.ceil(len(trials) / BATCH_SIZE)
    for i in range(n_batches):
        chunk = trials[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        batch_id = f"{i+1:03d}"
        out_path = OUT_TASKS_DIR / f"{batch_id}.json"
        out_path.write_text(json.dumps(chunk, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Built {len(trials)} trials into {n_batches} batch files in {OUT_TASKS_DIR}/")
    print(f"Shuffled with seed = {RANDOM_SEED}")

if __name__ == "__main__":
    main()
