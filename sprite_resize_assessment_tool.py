#!/usr/bin/env python3
"""Side-by-side sprite resize assessment tool.

Goal:
- Compare generated sprites (AI) vs fallback upscaled originals.
- Adjust per-sprite scale/offset and persist to sprite_size_overrides.json.

Sprite IDs are assumed to be in the form:
- AI dir:        group,image.png   (comma)
- Fallback dir:  group-image.png   (dash)

This tool writes overrides keyed by "group,image".
"""

import argparse
import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageTk


@dataclass(frozen=True)
class SpriteKey:
    group: int
    index: int

    @property
    def as_override_key(self) -> str:
        return f"{self.group},{self.index}"


def parse_sprite_key(stem: str) -> Optional[SpriteKey]:
    # Accept either "g,i" or "g-i"
    if ',' in stem:
        parts = stem.split(',')
    elif '-' in stem:
        parts = stem.split('-')
    else:
        return None
    if len(parts) != 2:
        return None
    if not (parts[0].strip().lstrip('-').isdigit() and parts[1].strip().lstrip('-').isdigit()):
        return None
    return SpriteKey(int(parts[0]), int(parts[1]))


def load_overrides(path: Path) -> Dict[str, Dict[str, float]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    result: Dict[str, Dict[str, float]] = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, dict):
            out: Dict[str, float] = {}
            for kk in ("scale", "offset_x", "offset_y"):
                if kk in v:
                    try:
                        out[kk] = float(v[kk])
                    except Exception:
                        pass
            if out:
                result[k] = out
    return result


def save_overrides(path: Path, overrides: Dict[str, Dict[str, float]]) -> None:
    path.write_text(json.dumps(overrides, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def alpha_bbox(img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
    rgba = img.convert("RGBA")
    return rgba.getchannel("A").getbbox()


def fit_to_reference_canvas(
    source: Image.Image,
    reference: Image.Image,
    scale: float,
    offset_x: float,
    offset_y: float,
) -> Image.Image:
    """Fit source onto reference canvas using the same logic as build_test_character.

    - Compute bbox of reference alpha; align source (cropped bbox) to reference bbox.
    - Apply extra scale/offset.
    """
    ref_rgba = reference.convert("RGBA")
    src_rgba = source.convert("RGBA")

    ref_bbox = alpha_bbox(ref_rgba)
    src_bbox = alpha_bbox(src_rgba)

    canvas = Image.new("RGBA", ref_rgba.size, (0, 0, 0, 0))
    if src_bbox is None:
        return canvas

    cropped = src_rgba.crop(src_bbox)

    if ref_bbox is None:
        target_left, target_top = 0, 0
        target_width, target_height = ref_rgba.size
    else:
        target_left, target_top, target_right, target_bottom = ref_bbox
        target_width = max(1, target_right - target_left)
        target_height = max(1, target_bottom - target_top)

    fit_scale = min(target_width / max(1, cropped.width), target_height / max(1, cropped.height))
    fit_scale *= float(scale)

    resized_size = (
        max(1, int(round(cropped.width * fit_scale))),
        max(1, int(round(cropped.height * fit_scale))),
    )
    resized = cropped.resize(resized_size, Image.Resampling.LANCZOS)

    anchor_x = target_left + (target_width - resized_size[0]) // 2
    anchor_y = target_top + (target_height - resized_size[1])
    anchor_x += int(round(float(offset_x)))
    anchor_y += int(round(float(offset_y)))

    canvas.alpha_composite(resized, (anchor_x, anchor_y))
    return canvas


def make_checkerboard(size: Tuple[int, int], cell: int = 16) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, (200, 200, 200))
    p = img.load()
    for y in range(h):
        for x in range(w):
            if ((x // cell) + (y // cell)) % 2 == 0:
                p[x, y] = (220, 220, 220)
            else:
                p[x, y] = (180, 180, 180)
    return img


class App:
    def __init__(
        self,
        ai_dir: Path,
        fallback_dir: Path,
        overrides_path: Path,
        preview_scale: float,
    ) -> None:
        self.ai_dir = ai_dir
        self.fallback_dir = fallback_dir
        self.overrides_path = overrides_path
        self.preview_scale = preview_scale

        self.overrides: Dict[str, Dict[str, float]] = load_overrides(overrides_path)
        self.keys: List[SpriteKey] = self._collect_keys()
        if not self.keys:
            raise RuntimeError("No sprites found in either directory.")

        self.idx = 0

        self.root = tk.Tk()
        self.root.title("Sprite Resize Assessment Tool")
        self.root.geometry("1400x900")

        self._build_ui()
        self._load_current()

    def _collect_keys(self) -> List[SpriteKey]:
        found = set()
        for d in (self.ai_dir, self.fallback_dir):
            if not d.exists():
                continue
            for p in d.glob("*.png"):
                k = parse_sprite_key(p.stem)
                if k is not None:
                    found.add(k)
        return sorted(found, key=lambda k: (k.group, k.index))

    def _sprite_paths(self, key: SpriteKey) -> Tuple[Optional[Path], Optional[Path]]:
        ai = self.ai_dir / f"{key.group},{key.index}.png"
        fb = self.fallback_dir / f"{key.group}-{key.index}.png"
        return (ai if ai.exists() else None, fb if fb.exists() else None)

    def _build_ui(self) -> None:
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=10)

        self.title_var = tk.StringVar(value="")
        tk.Label(top, textvariable=self.title_var, font=("Arial", 16, "bold")).pack(side=tk.LEFT)

        nav = tk.Frame(top)
        nav.pack(side=tk.RIGHT)
        tk.Button(nav, text="Prev", command=self.prev).pack(side=tk.LEFT, padx=5)
        tk.Button(nav, text="Next", command=self.next).pack(side=tk.LEFT, padx=5)
        tk.Button(nav, text="Save override", command=self.save_current).pack(side=tk.LEFT, padx=5)
        tk.Button(nav, text="Reset override", command=self.reset_current).pack(side=tk.LEFT, padx=5)

        mid = tk.Frame(self.root)
        mid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Three panels: AI, fallback, fitted result
        self.panel_ai = tk.Label(mid)
        self.panel_fb = tk.Label(mid)
        self.panel_fit = tk.Label(mid)

        self.panel_ai.grid(row=0, column=0, padx=10, pady=10)
        self.panel_fb.grid(row=0, column=1, padx=10, pady=10)
        self.panel_fit.grid(row=0, column=2, padx=10, pady=10)

        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)
        mid.columnconfigure(2, weight=1)

        # Controls
        controls = tk.Frame(self.root)
        controls.pack(fill=tk.X, padx=10, pady=10)

        self.scale_var = tk.DoubleVar(value=1.0)
        self.offx_var = tk.DoubleVar(value=0.0)
        self.offy_var = tk.DoubleVar(value=0.0)

        def add_slider(label: str, var: tk.DoubleVar, from_: float, to: float, resolution: float):
            row = tk.Frame(controls)
            row.pack(fill=tk.X)
            tk.Label(row, text=label, width=12, anchor="w").pack(side=tk.LEFT)
            s = tk.Scale(
                row,
                variable=var,
                from_=from_,
                to=to,
                orient=tk.HORIZONTAL,
                resolution=resolution,
                length=900,
                command=lambda _v: self._render(),
            )
            s.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Entry(row, textvariable=var, width=8).pack(side=tk.LEFT, padx=5)

        add_slider("scale", self.scale_var, 0.5, 2.0, 0.01)
        add_slider("offset_x", self.offx_var, -200.0, 200.0, 1.0)
        add_slider("offset_y", self.offy_var, -200.0, 200.0, 1.0)

        help_row = tk.Frame(self.root)
        help_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Label(
            help_row,
            text="Keyboard: Left/Right = Prev/Next, S = Save override, R = Reset override",
            anchor="w",
        ).pack(fill=tk.X)

        self.root.bind("<Left>", lambda _e: self.prev())
        self.root.bind("<Right>", lambda _e: self.next())
        self.root.bind("<s>", lambda _e: self.save_current())
        self.root.bind("<S>", lambda _e: self.save_current())
        self.root.bind("<r>", lambda _e: self.reset_current())
        self.root.bind("<R>", lambda _e: self.reset_current())

        # Keep image refs
        self._img_ai = None
        self._img_fb = None
        self._img_fit = None

    def _load_current(self) -> None:
        key = self.keys[self.idx]
        ai_path, fb_path = self._sprite_paths(key)

        self.title_var.set(
            f"{key.group},{key.index}   ({self.idx + 1}/{len(self.keys)})"
            + ("   [AI missing]" if ai_path is None else "")
            + ("   [fallback missing]" if fb_path is None else "")
        )

        ov = self.overrides.get(key.as_override_key, {})
        self.scale_var.set(float(ov.get("scale", 1.0)))
        self.offx_var.set(float(ov.get("offset_x", 0.0)))
        self.offy_var.set(float(ov.get("offset_y", 0.0)))

        self._render()

    def _load_image_or_blank(self, path: Optional[Path], size_hint: Tuple[int, int] = (256, 256)) -> Image.Image:
        if path is None:
            return Image.new("RGBA", size_hint, (0, 0, 0, 0))
        return Image.open(path).convert("RGBA")

    def _composite_on_checker(self, rgba: Image.Image) -> Image.Image:
        base = make_checkerboard(rgba.size).convert("RGBA")
        base.alpha_composite(rgba)
        return base

    def _to_photo(self, img: Image.Image) -> ImageTk.PhotoImage:
        if self.preview_scale != 1.0:
            new_size = (
                max(1, int(round(img.width * self.preview_scale))),
                max(1, int(round(img.height * self.preview_scale))),
            )
            img = img.resize(new_size, Image.Resampling.NEAREST)
        return ImageTk.PhotoImage(img)

    def _render(self) -> None:
        key = self.keys[self.idx]
        ai_path, fb_path = self._sprite_paths(key)

        ai_img = self._load_image_or_blank(ai_path)
        fb_img = self._load_image_or_blank(fb_path, size_hint=ai_img.size)

        # Determine reference canvas: prefer fallback if available, else AI
        reference = fb_img if fb_path is not None else ai_img

        fitted = fit_to_reference_canvas(
            source=ai_img,
            reference=reference,
            scale=float(self.scale_var.get()),
            offset_x=float(self.offx_var.get()),
            offset_y=float(self.offy_var.get()),
        )

        # Composite on checkerboard for visibility
        ai_disp = self._composite_on_checker(ai_img)
        fb_disp = self._composite_on_checker(fb_img)
        fit_disp = self._composite_on_checker(fitted)

        self._img_ai = self._to_photo(ai_disp)
        self._img_fb = self._to_photo(fb_disp)
        self._img_fit = self._to_photo(fit_disp)

        self.panel_ai.configure(image=self._img_ai, text="")
        self.panel_fb.configure(image=self._img_fb, text="")
        self.panel_fit.configure(image=self._img_fit, text="")

    def prev(self) -> None:
        if self.idx > 0:
            self.idx -= 1
            self._load_current()

    def next(self) -> None:
        if self.idx < len(self.keys) - 1:
            self.idx += 1
            self._load_current()

    def save_current(self) -> None:
        key = self.keys[self.idx]
        self.overrides[key.as_override_key] = {
            "scale": float(self.scale_var.get()),
            "offset_x": float(self.offx_var.get()),
            "offset_y": float(self.offy_var.get()),
        }
        try:
            save_overrides(self.overrides_path, self.overrides)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write overrides: {e}")
            return
        messagebox.showinfo("Saved", f"Saved override for {key.as_override_key}")

    def reset_current(self) -> None:
        key = self.keys[self.idx]
        if key.as_override_key in self.overrides:
            del self.overrides[key.as_override_key]
            try:
                save_overrides(self.overrides_path, self.overrides)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to write overrides: {e}")
                return
        self.scale_var.set(1.0)
        self.offx_var.set(0.0)
        self.offy_var.set(0.0)
        self._render()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Side-by-side sprite resize assessment tool")
    parser.add_argument(
        "--ai-dir",
        default="/Users/oliverlibaw/Downloads/MK-assets/resized-transparent-gen-ai-sprites",
        help="Directory containing generated sprites named group,image.png",
    )
    parser.add_argument(
        "--fallback-dir",
        default="/Users/oliverlibaw/Downloads/MK-assets/upscaled-original-low-res-sprites",
        help="Directory containing fallback sprites named group-index.png",
    )
    parser.add_argument(
        "--overrides",
        default="./sprite_size_overrides.json",
        help="Path to sprite_size_overrides.json",
    )
    parser.add_argument(
        "--preview-scale",
        type=float,
        default=1.0,
        help="Scale factor for on-screen display only (does not affect saved offsets)",
    )

    args = parser.parse_args()
    ai_dir = Path(args.ai_dir)
    fb_dir = Path(args.fallback_dir)
    overrides_path = Path(args.overrides)

    try:
        app = App(ai_dir=ai_dir, fallback_dir=fb_dir, overrides_path=overrides_path, preview_scale=float(args.preview_scale))
    except Exception as e:
        print(f"Error: {e}")
        return
    app.run()


if __name__ == "__main__":
    main()
