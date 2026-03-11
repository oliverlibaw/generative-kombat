#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
import re
import struct
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from PIL import Image, ImageDraw, ImageFont


Pair = Tuple[int, int]


@dataclass
class SpriteRecord:
    sequence_index: int
    group: int
    image: int
    axis_x: int
    axis_y: int
    same_palette: int
    linked_index: int
    raw_image_data: bytes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--original",
        default="ikemen-go-stable/chars/MK1_CAGE/CODE/CAGE.sff",
    )
    parser.add_argument(
        "--hd-dir",
        default="hd_sprite_sources",
    )
    parser.add_argument(
        "--output-dir",
        default="sff_compare_output",
    )
    parser.add_argument(
        "--cell-size",
        type=int,
        default=160,
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--merged-dir",
        default="hd_sprite_sources_merged",
    )
    parser.add_argument(
        "--fallback-scale",
        type=float,
        default=3.0,
    )
    return parser.parse_args()


def parse_sff_v1(path: Path) -> List[SpriteRecord]:
    data = path.read_bytes()
    if data[:12] != b"ElecbyteSpr\x00":
        raise ValueError(f"{path} is not an SFF v1 file")

    image_count = struct.unpack_from("<I", data, 20)[0]
    first_subheader_offset = struct.unpack_from("<I", data, 24)[0]

    sprites: List[SpriteRecord] = []
    payloads_by_seq: Dict[int, bytes] = {}
    offset = first_subheader_offset
    visited_offsets = set()

    for seq in range(image_count):
        if offset == 0:
            break
        if offset in visited_offsets:
            break
        if offset + 32 > len(data):
            break

        visited_offsets.add(offset)
        next_offset = struct.unpack_from("<I", data, offset)[0]
        length = struct.unpack_from("<I", data, offset + 4)[0]
        axis_x = struct.unpack_from("<h", data, offset + 8)[0]
        axis_y = struct.unpack_from("<h", data, offset + 10)[0]
        group = struct.unpack_from("<H", data, offset + 12)[0]
        image = struct.unpack_from("<H", data, offset + 14)[0]
        linked_index = struct.unpack_from("<H", data, offset + 16)[0]
        same_palette = struct.unpack_from("<B", data, offset + 18)[0]
        payload_start = offset + 32
        payload_end = payload_start + length
        if payload_end > len(data):
            payload_end = len(data)
        payload = data[payload_start:payload_end]

        if length == 0:
            payload = payloads_by_seq.get(linked_index, b"")
        else:
            payloads_by_seq[seq] = payload

        sprites.append(
            SpriteRecord(
                sequence_index=seq,
                group=group,
                image=image,
                axis_x=axis_x,
                axis_y=axis_y,
                same_palette=same_palette,
                linked_index=linked_index,
                raw_image_data=payload,
            )
        )
        offset = next_offset

    return sprites


def decode_sprite(record: SpriteRecord) -> Image.Image | None:
    if not record.raw_image_data:
        return None
    try:
        image = Image.open(BytesIO(record.raw_image_data))
        image.load()
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        return image
    except Exception:
        return None


def write_merged_sprite_set(
    original_pairs: List[Pair],
    original_map: Dict[Pair, SpriteRecord],
    hd_map: Dict[Pair, Path],
    merged_dir: Path,
    fallback_scale: float,
) -> Tuple[int, int]:
    merged_dir.mkdir(parents=True, exist_ok=True)
    reused_hd = 0
    generated_fallbacks = 0

    def fit_image_to_canvas(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        if image.size == target_size:
            return image
        target_width, target_height = target_size
        scale = min(target_width / image.width, target_height / image.height)
        resized_size = (
            max(1, int(round(image.width * scale))),
            max(1, int(round(image.height * scale))),
        )
        resized = image.resize(resized_size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
        offset = (
            (target_width - resized_size[0]) // 2,
            (target_height - resized_size[1]) // 2,
        )
        canvas.paste(resized, offset, resized)
        return canvas

    for pair in original_pairs:
        destination = merged_dir / f"{pair[0]},{pair[1]}.png"
        original_sprite = original_map.get(pair)
        if original_sprite is None:
            continue
        original_image = decode_sprite(original_sprite)
        if original_image is None:
            continue
        target_size = (
            max(1, int(round(original_image.width * fallback_scale))),
            max(1, int(round(original_image.height * fallback_scale))),
        )
        hd_source = hd_map.get(pair)
        if hd_source is not None:
            image = decode_loose_image(hd_source)
            if image is not None:
                if image.size != target_size:
                    image = fit_image_to_canvas(image, target_size)
                image.save(destination)
                reused_hd += 1
                continue

        image = original_image
        if image.size != target_size:
            image = image.resize(target_size, Image.Resampling.NEAREST)
        image.save(destination)
        generated_fallbacks += 1

    return reused_hd, generated_fallbacks


def build_pair_map(sprites: Iterable[SpriteRecord]) -> Dict[Pair, SpriteRecord]:
    pair_map: Dict[Pair, SpriteRecord] = {}
    for sprite in sprites:
        pair = (sprite.group, sprite.image)
        if pair not in pair_map:
            pair_map[pair] = sprite
    return pair_map


def parse_loose_hd_dir(path: Path) -> Tuple[Dict[Pair, Path], List[Path]]:
    pair_map: Dict[Pair, Path] = {}
    unmatched: List[Path] = []
    pattern = re.compile(r"^(\d+),(\d+)\.(png|jpg|jpeg|webp)$", re.IGNORECASE)

    for candidate in sorted(path.iterdir()):
        if not candidate.is_file():
            continue
        match = pattern.match(candidate.name)
        if match is None:
            unmatched.append(candidate)
            continue
        pair = (int(match.group(1)), int(match.group(2)))
        if pair not in pair_map:
            pair_map[pair] = candidate

    return pair_map, unmatched


def decode_loose_image(path: Path) -> Image.Image | None:
    try:
        image = Image.open(path)
        image.load()
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        return image
    except Exception:
        return None


def make_tile(
    pair: Pair,
    sprite: SpriteRecord | None,
    decoded: Image.Image | None,
    cell_size: int,
    side_label: str,
    present: bool,
) -> Image.Image:
    header_h = 38
    footer_h = 28
    image_area_h = cell_size
    tile_w = cell_size
    tile_h = header_h + image_area_h + footer_h
    tile = Image.new("RGBA", (tile_w, tile_h), (28, 28, 32, 255))
    draw = ImageDraw.Draw(tile)
    font = ImageFont.load_default()

    border = (80, 80, 90, 255) if present else (170, 70, 70, 255)
    draw.rectangle([0, 0, tile_w - 1, tile_h - 1], outline=border, width=2)
    draw.text((8, 8), f"{side_label} {pair[0]},{pair[1]}", fill=(235, 235, 235, 255), font=font)

    image_box = (8, header_h, tile_w - 8, header_h + image_area_h - 8)
    draw.rectangle(image_box, outline=(70, 70, 78, 255), width=1)

    if decoded is not None:
        render = decoded.copy()
        render.thumbnail((image_box[2] - image_box[0] - 8, image_box[3] - image_box[1] - 8), Image.Resampling.NEAREST)
        paste_x = image_box[0] + ((image_box[2] - image_box[0]) - render.width) // 2
        paste_y = image_box[1] + ((image_box[3] - image_box[1]) - render.height) // 2
        tile.alpha_composite(render, (paste_x, paste_y))
    else:
        missing_text = "missing" if not present else "decode fail"
        tw = draw.textlength(missing_text, font=font)
        draw.text(
            ((tile_w - tw) / 2, header_h + image_area_h / 2 - 8),
            missing_text,
            fill=(220, 120, 120, 255),
            font=font,
        )

    footer = side_label
    if sprite is not None:
        footer = f"seq {sprite.sequence_index} axis {sprite.axis_x},{sprite.axis_y}"
    draw.text((8, tile_h - 20), footer, fill=(190, 190, 200, 255), font=font)
    return tile


def assemble_contact_sheet(
    original_pairs: List[Pair],
    original_map: Dict[Pair, SpriteRecord],
    hd_map: Dict[Pair, Path],
    decoded_original: Dict[Pair, Image.Image | None],
    decoded_hd: Dict[Pair, Image.Image | None],
    output_path: Path,
    cell_size: int,
    columns: int,
) -> None:
    row_count = math.ceil(len(original_pairs) / columns) if original_pairs else 1
    sample_tile = make_tile((0, 0), None, None, cell_size, "ORIG", False)
    tile_w, tile_h = sample_tile.size
    gutter = 16
    row_label_w = 0
    sheet_w = columns * (tile_w * 2 + gutter) + gutter + row_label_w
    sheet_h = row_count * (tile_h + gutter) + gutter
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (16, 16, 20, 255))

    for idx, pair in enumerate(original_pairs):
        row = idx // columns
        col = idx % columns
        x = gutter + col * (tile_w * 2 + gutter)
        y = gutter + row * (tile_h + gutter)

        orig_sprite = original_map.get(pair)
        hd_sprite = hd_map.get(pair)
        orig_tile = make_tile(pair, orig_sprite, decoded_original.get(pair), cell_size, "ORIG", orig_sprite is not None)
        hd_tile = make_tile(pair, None, decoded_hd.get(pair), cell_size, "HD", hd_sprite is not None)
        sheet.alpha_composite(orig_tile, (x, y))
        sheet.alpha_composite(hd_tile, (x + tile_w, y))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)


def write_report(
    original_map: Dict[Pair, SpriteRecord],
    hd_map: Dict[Pair, Path],
    unmatched_hd_files: List[Path],
    output_path: Path,
) -> List[Pair]:
    original_pairs = sorted(original_map)
    hd_pairs = sorted(hd_map)
    missing_in_hd = sorted(set(original_pairs) - set(hd_pairs))
    extra_in_hd = sorted(set(hd_pairs) - set(original_pairs))

    lines = [
        f"original_sprite_count={len(original_pairs)}",
        f"hd_sprite_count={len(hd_pairs)}",
        f"missing_in_hd_count={len(missing_in_hd)}",
        f"extra_in_hd_count={len(extra_in_hd)}",
        "",
        "[missing_in_hd]",
    ]
    lines.extend(f"{group},{image}" for group, image in missing_in_hd)
    lines.extend([
        "",
        "[extra_in_hd]",
    ])
    lines.extend(f"{group},{image}" for group, image in extra_in_hd)
    lines.extend([
        "",
        "[unmatched_hd_filenames]",
    ])
    lines.extend(str(path.name) for path in unmatched_hd_files)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return original_pairs


def main() -> None:
    args = parse_args()
    original_path = Path(args.original)
    hd_dir = Path(args.hd_dir)
    output_dir = Path(args.output_dir)
    merged_dir = Path(args.merged_dir)

    original_sprites = parse_sff_v1(original_path)

    original_map = build_pair_map(original_sprites)
    hd_map, unmatched_hd_files = parse_loose_hd_dir(hd_dir)

    original_pairs = write_report(original_map, hd_map, unmatched_hd_files, output_dir / "pair_report.txt")
    if args.limit > 0:
        original_pairs = original_pairs[: args.limit]

    decoded_original = {pair: decode_sprite(sprite) for pair, sprite in original_map.items() if pair in original_pairs}
    decoded_hd = {pair: decode_loose_image(sprite_path) for pair, sprite_path in hd_map.items() if pair in original_pairs}

    assemble_contact_sheet(
        original_pairs=original_pairs,
        original_map=original_map,
        hd_map=hd_map,
        decoded_original=decoded_original,
        decoded_hd=decoded_hd,
        output_path=output_dir / "contact_sheet_side_by_side.png",
        cell_size=args.cell_size,
        columns=args.columns,
    )

    reused_hd, generated_fallbacks = write_merged_sprite_set(
        original_pairs=sorted(original_map),
        original_map=original_map,
        hd_map=hd_map,
        merged_dir=merged_dir,
        fallback_scale=args.fallback_scale,
    )

    missing_in_hd = sorted(set(original_map) - set(hd_map))
    print(f"Original unique pairs: {len(original_map)}")
    print(f"HD unique pairs: {len(hd_map)}")
    print(f"Missing in HD: {len(missing_in_hd)}")
    print(f"Unmatched HD filenames: {len(unmatched_hd_files)}")
    print(f"Merged sprite dir: {merged_dir}")
    print(f"Reused HD sprites: {reused_hd}")
    print(f"Generated fallback sprites: {generated_fallbacks}")
    print(f"Wrote report: {output_dir / 'pair_report.txt'}")
    print(f"Wrote contact sheet: {output_dir / 'contact_sheet_side_by_side.png'}")


if __name__ == "__main__":
    main()
