# Generative Kombat

## 1) What this project is

This repo is an **intermediate pipeline** toward the end goal:

- Take a **single full-body user image**.
- Generate all required animation frames to create **high-res (~400px tall) photoreal sprites**.
- Build a fully playable Ikemen GO character that preserves **Johnny Cage’s gameplay** (moves, hitboxes/hurtboxes, timing, special moves, etc.) while swapping the visuals to the user likeness.

### Current milestone (what works today)

- You have a **test character build pipeline** that produces a new character folder (`MK1_CAGE_TEST`) using:
  - **Johnny Cage gameplay logic** (copied from the original character files).
  - **Generated transparent PNG frames** when present.
  - **Upscaled original low-res frames** as fallback when a generated frame is missing.
  - A mechanism to **adjust sprite scale/offset per frame** (`sprite_size_overrides.json`) so generated frames fit the expected canvas.

## 2) Repository layout

- `build_test_character.py`
  - Main build script.
  - Produces `./test_character_output/MK1_CAGE_TEST`.
  - Merges sprites (AI first, fallback second) and builds a new `.sff`.
  - Uses `sprite_size_overrides.json` to tweak problematic sprites.
  - Writes a sizing report to `test_character_output/sprite_size_report.csv`.

- `launch_test_character.py`
  - Installs the built test character into `ikemen-go-stable/chars/`.
  - Optionally registers it in `ikemen-go-stable/data/select.def`.
  - Optionally enables debug options in `ikemen-go-stable/save/config.json`.
  - Launches Ikemen GO.

- `test_game.sh`
  - Simple smoke test that launches Ikemen with an existing character matchup and writes `ikemen-go-stable/debug.log`.

- `ikemen-go-stable/`
  - A local Ikemen GO distribution, including:
    - `Ikemen_GO_MacOS` (Mac executable)
    - `data/select.def`
    - `save/config.json`
    - `chars/` (where the test character is installed)

- `sprite_size_overrides.json`
  - Per-sprite overrides keyed by `"group,image"` (example: `"40,0"`).
  - Values:
    - `scale` (float)
    - `offset_x` (float)
    - `offset_y` (float)

- `sprite_review_tool.py`
  - A small Tkinter GUI to visually compare sprites between two directories.

## 3) Required external assets (MK-assets)

This repo expects assets in `/Users/oliverlibaw/Downloads/MK-assets/` (as currently hardcoded defaults in `build_test_character.py`).

Folders you will typically populate:

- `MK-assets/johnny-cage-complete-low-res-character-files/`
  - Source character files (CODE, DEF, original SFF, etc.).

- `MK-assets/resized-transparent-gen-ai-sprites/`
  - Your generated frames as **transparent PNGs**.
  - Naming: `group,image.png` (commas) is the format consumed directly by the builder.

- `MK-assets/upscaled-original-low-res-sprites/`
  - Fallback sprites when a generated sprite is missing.
  - Naming: `group-image.png` (dashes) is supported and normalized internally.

If `resized-transparent-gen-ai-sprites/` or `upscaled-original-low-res-sprites/` are empty, the build will fall back to extracting from the original SFF for anything missing.

## 4) Building the test character

### Prereqs

- Python 3
- Pillow

Install Pillow (if needed):

```bash
python3 -m pip install pillow
```

### Run the build

From the repo root:

```bash
python3 build_test_character.py \
  --ai-dir "/Users/oliverlibaw/Downloads/MK-assets/resized-transparent-gen-ai-sprites" \
  --upscaled-dir "/Users/oliverlibaw/Downloads/MK-assets/upscaled-original-low-res-sprites" \
  --original-char "/Users/oliverlibaw/Downloads/MK-assets/johnny-cage-complete-low-res-character-files" \
  --output-dir "./test_character_output"
```

Expected output:

- `test_character_output/MK1_CAGE_TEST/` (the character folder)
- `test_character_output/sprite_size_report.csv` (metadata helpful for diagnosing sizing)

## 5) Installing + testing in Ikemen GO (debug-friendly)

### Option A: install + configure + launch (recommended)

```bash
python3 launch_test_character.py
```

This will:

- Copy `test_character_output/MK1_CAGE_TEST` into `ikemen-go-stable/chars/`.
- Add an entry into `ikemen-go-stable/data/select.def` (if not already present).
- Enable debug settings in `ikemen-go-stable/save/config.json`.
- Launch Ikemen.

### Option B: smoke test launch script

```bash
./test_game.sh
```

Then check:

- `ikemen-go-stable/debug.log`

### What “success” looks like

- Character loads without missing file errors.
- Animations play without obvious sprite misalignment.
- Debug overlays (hitboxes/hurtboxes) are visible when enabled.
- The test character’s move set behaves like the original Johnny Cage.

## 6) Reviewing sprites and fixing “too large / too small” frames

### The intended process

1. Build the test character.
2. Run the game and visually identify problematic sprites (e.g. splits too small).
3. Add or adjust entries in `sprite_size_overrides.json` for the affected `group,image` keys.
4. Rebuild the test character.
5. Re-test.

### Where to record adjustments

- `sprite_size_overrides.json` is the authoritative place to store per-frame adjustments.
- These overrides are meant to be reusable later when you generate new user-likeness frames.

### How overrides work

For a given sprite key like `"40,0"`:

- `scale`: multiply the auto-fit scale (example: `1.15` to make it bigger).
- `offset_x`: shift the fitted sprite horizontally (positive = right).
- `offset_y`: shift the fitted sprite vertically (positive = down).

After editing overrides:

```bash
python3 build_test_character.py
python3 launch_test_character.py
```

### Optional: use the GUI reviewer

You can compare two directories of sprite images (for example generated vs fallback) using:

```bash
python3 sprite_review_tool.py \
  --low-res-dir "/Users/oliverlibaw/Downloads/MK-assets/upscaled-original-low-res-sprites" \
  --hd-dir "/Users/oliverlibaw/Downloads/MK-assets/resized-transparent-gen-ai-sprites"
```

## 7) Next steps toward the final “upload one image” goal

- Replace the current “use existing generated frames” step with a generator that:
  - accepts one user image,
  - produces a full sprite sheet worth of frames,
  - outputs PNGs named by `group,image`.

- Keep `sprite_size_overrides.json` as the durable knowledge base for problematic poses.

## 8) Publishing to GitHub

### Recommended repo hygiene

- Do not commit large binary assets or user photos.
- Do not commit secrets (e.g. Replicate API keys).

### Typical commands

```bash
git init

git add .
git commit -m "Initial commit"

git branch -M main

git remote add origin <YOUR_GITHUB_REPO_URL>

git push -u origin main
```

If you want, I can add a `.gitignore` tailored for this repo (venv/cache/output/game logs) before you push.
