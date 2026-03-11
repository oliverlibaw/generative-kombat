#!/usr/bin/env python3

from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Tuple

from PIL import Image


Image.MAX_IMAGE_PIXELS = None


Pair = Tuple[int, int]


@dataclass
class SpriteRecord:
    sequence_index: int
    group: int
    image: int
    axis_x: int
    axis_y: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-sff", default="ikemen-go-stable/chars/MK1_CAGE/CODE/CAGE.sff")
    parser.add_argument("--merged-dir", default="hd_sprite_sources_merged")
    parser.add_argument("--output-sff", default="ikemen-go-stable/chars/MK1_CAGE/CODE/johnny_hd.sff")
    parser.add_argument("--axis-scale", type=float, default=3.0)
    return parser.parse_args()


def parse_template(path: Path) -> Tuple[bytes, int, List[SpriteRecord]]:
    data = path.read_bytes()
    if data[:12] != b"ElecbyteSpr\x00":
        raise ValueError(f"{path} is not SFF v1")
    palette_type = data[32]
    image_count = struct.unpack_from("<I", data, 20)[0]
    first_subfile_offset = struct.unpack_from("<I", data, 24)[0]
    sprites: List[SpriteRecord] = []
    offset = first_subfile_offset
    seen_offsets = set()
    for seq in range(image_count):
        if offset == 0 or offset in seen_offsets or offset + 32 > len(data):
            break
        seen_offsets.add(offset)
        next_offset = struct.unpack_from("<I", data, offset)[0]
        group = struct.unpack_from("<H", data, offset + 12)[0]
        image = struct.unpack_from("<H", data, offset + 14)[0]
        axis_x = struct.unpack_from("<h", data, offset + 8)[0]
        axis_y = struct.unpack_from("<h", data, offset + 10)[0]
        sprites.append(SpriteRecord(seq, group, image, axis_x, axis_y))
        offset = next_offset
    return data[:16], palette_type, sprites


def load_merged_images(path: Path) -> Dict[Pair, Path]:
    result: Dict[Pair, Path] = {}
    for candidate in sorted(path.iterdir()):
        if not candidate.is_file():
            continue
        stem = candidate.stem
        if "," not in stem:
            continue
        left, right = stem.split(",", 1)
        if not (left.isdigit() and right.isdigit()):
            continue
        result[(int(left), int(right))] = candidate
    return result


def rgba_to_mugen_pcx(source_path: Path, temp_dir: Path) -> bytes:
    try:
        image = Image.open(source_path)
        image.load()
    except Exception as exc:
        raise RuntimeError(f"Failed to open merged sprite image: {source_path}") from exc
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    opaque_mask = alpha.point(lambda a: 255 if a > 0 else 0)
    rgb = Image.new("RGB", rgba.size, (0, 0, 0))
    rgb.paste(rgba.convert("RGB"), mask=opaque_mask)
    quantized = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)

    qdata = list(quantized.getdata())
    adata = list(alpha.getdata())
    pdata = [0] * len(qdata)
    for idx, (pix, a) in enumerate(zip(qdata, adata)):
        if a > 0:
            pdata[idx] = min(pix + 1, 255)

    pal = quantized.getpalette()[: 255 * 3]
    full_palette = [0, 0, 0] + pal
    if len(full_palette) < 768:
        full_palette.extend([0] * (768 - len(full_palette)))

    out = Image.new("P", quantized.size)
    out.putpalette(full_palette[:768])
    out.putdata(pdata)

    temp_path = temp_dir / (source_path.stem + ".pcx")
    out.save(temp_path, format="PCX")
    return temp_path.read_bytes()


def build_sff(signature_and_version: bytes, palette_type: int, sprites: List[SpriteRecord], merged_images: Dict[Pair, Path], output_path: Path, axis_scale: float) -> None:
    group_total = len({sprite.group for sprite in sprites})
    image_total = len(sprites)
    header = bytearray(512)
    header[:12] = b"ElecbyteSpr\x00"
    header[12:16] = signature_and_version[12:16]
    struct.pack_into("<I", header, 16, group_total)
    struct.pack_into("<I", header, 20, image_total)
    struct.pack_into("<I", header, 24, 512)
    struct.pack_into("<I", header, 28, 32)
    header[32] = palette_type

    with TemporaryDirectory() as temp_dir_raw:
        temp_dir = Path(temp_dir_raw)
        payloads: List[bytes] = []
        for sprite in sprites:
            pair = (sprite.group, sprite.image)
            source = merged_images.get(pair)
            if source is None:
                raise FileNotFoundError(f"Missing merged sprite for pair {pair}")
            payloads.append(rgba_to_mugen_pcx(source, temp_dir))

        content = bytearray(header)
        current_offset = 512
        for index, (sprite, payload) in enumerate(zip(sprites, payloads)):
            next_offset = current_offset + 32 + len(payload) if index < len(sprites) - 1 else 0
            sub = bytearray(32)
            scaled_axis_x = int(round(sprite.axis_x * axis_scale))
            scaled_axis_y = int(round(sprite.axis_y * axis_scale))
            struct.pack_into("<I", sub, 0, next_offset)
            struct.pack_into("<I", sub, 4, len(payload))
            struct.pack_into("<h", sub, 8, scaled_axis_x)
            struct.pack_into("<h", sub, 10, scaled_axis_y)
            struct.pack_into("<H", sub, 12, sprite.group)
            struct.pack_into("<H", sub, 14, sprite.image)
            struct.pack_into("<H", sub, 16, index)
            struct.pack_into("<B", sub, 18, 0)
            content.extend(sub)
            content.extend(payload)
            current_offset = next_offset

        output_path.write_bytes(content)


def main() -> None:
    args = parse_args()
    template_path = Path(args.template_sff)
    merged_dir = Path(args.merged_dir)
    output_path = Path(args.output_sff)

    signature_and_version, palette_type, sprites = parse_template(template_path)
    merged_images = load_merged_images(merged_dir)
    build_sff(signature_and_version, palette_type, sprites, merged_images, output_path, args.axis_scale)
    print(f"Built {output_path} with {len(sprites)} sprites")


if __name__ == "__main__":
    main()
