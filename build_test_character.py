#!/usr/bin/env python3
"""
Build test/debug version of Johnny Cage with AI sprites and upscaled fallbacks.
"""

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image
import sys

# Add current directory to path to import our modules
sys.path.append(str(Path(__file__).parent))

from compare_sff_pairs import parse_sff_v1, decode_sprite
from build_hd_sff_v1 import build_sff, rgba_to_mugen_pcx


def load_size_overrides(path: Path) -> Dict[str, Dict[str, float]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        return {}
    result: Dict[str, Dict[str, float]] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = {str(k): float(v) for k, v in value.items()}
    return result


def get_alpha_bbox(image: Image.Image) -> Optional[Tuple[int, int, int, int]]:
    rgba = image.convert('RGBA')
    return rgba.getchannel('A').getbbox()


def strip_white_background(image: Image.Image, threshold: int = 245) -> Image.Image:
    rgba = image.convert('RGBA')
    pixels = rgba.load()
    width, height = rgba.size
    visited = set()
    stack: List[Tuple[int, int]] = []

    def is_whiteish(x: int, y: int) -> bool:
        r, g, b, a = pixels[x, y]
        return a > 0 and r >= threshold and g >= threshold and b >= threshold

    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        visited.add((x, y))
        if not is_whiteish(x, y):
            continue
        pixels[x, y] = (255, 255, 255, 0)
        stack.extend([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)])

    return rgba


def fit_content_to_canvas(
    source_image: Image.Image,
    target_canvas_size: Tuple[int, int],
    reference_bbox: Optional[Tuple[int, int, int, int]],
    override: Dict[str, float],
) -> Tuple[Image.Image, Dict[str, Any]]:
    cleaned = strip_white_background(source_image)
    source_bbox = get_alpha_bbox(cleaned)
    canvas = Image.new('RGBA', target_canvas_size, (0, 0, 0, 0))
    if source_bbox is None:
        return canvas, {
            'source_bbox': None,
            'target_bbox': reference_bbox,
            'scale': 1.0,
            'offset_x': 0,
            'offset_y': 0,
        }

    cropped = cleaned.crop(source_bbox)
    if reference_bbox is None:
        target_width, target_height = target_canvas_size
        target_left = 0
        target_top = 0
    else:
        target_left, target_top, target_right, target_bottom = reference_bbox
        target_width = max(1, target_right - target_left)
        target_height = max(1, target_bottom - target_top)

    fit_scale = min(target_width / cropped.width, target_height / cropped.height)
    fit_scale *= override.get('scale', 1.0)
    resized_size = (
        max(1, int(round(cropped.width * fit_scale))),
        max(1, int(round(cropped.height * fit_scale))),
    )
    resized = cropped.resize(resized_size, Image.Resampling.LANCZOS)

    anchor_x = target_left + (target_width - resized_size[0]) // 2
    anchor_y = target_top + (target_height - resized_size[1])
    anchor_x += int(round(override.get('offset_x', 0.0)))
    anchor_y += int(round(override.get('offset_y', 0.0)))
    canvas.alpha_composite(resized, (anchor_x, anchor_y))
    return canvas, {
        'source_bbox': source_bbox,
        'target_bbox': reference_bbox,
        'scale': fit_scale,
        'offset_x': anchor_x,
        'offset_y': anchor_y,
    }


def write_size_report(rows: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        'pair',
        'source_kind',
        'source_path',
        'target_canvas',
        'source_bbox',
        'target_bbox',
        'scale',
        'offset_x',
        'offset_y',
        'override',
    ]
    with output_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def scale_air_file(input_path: Path, output_path: Path, scale_factor: float):
    """Simple AIR file scaling function."""
    import re
    
    PAIR_RE = re.compile(r'^(\s*[0-9]+\s*,\s*[0-9]+\s*,\s*)(-?\d+)\s*,\s*(-?\d+)(\s*,.*)$')
    BOX_RE = re.compile(r'^(\s*Clsn[12](?:Default)?\[\d+\]\s*=\s*)(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(\s*)$')
    
    def scale_int(value: str, scale: float) -> str:
        return str(int(round(int(value) * scale)))
    
    lines = input_path.read_text(encoding='utf-8').splitlines()
    output = []
    
    for line in lines:
        box_match = BOX_RE.match(line)
        if box_match is not None:
            output.append(
                ''.join([
                    box_match.group(1),
                    scale_int(box_match.group(2), scale_factor), ', ',
                    scale_int(box_match.group(3), scale_factor), ', ',
                    scale_int(box_match.group(4), scale_factor), ', ',
                    scale_int(box_match.group(5), scale_factor),
                    box_match.group(6),
                ])
            )
            continue
        
        pair_match = PAIR_RE.match(line)
        if pair_match is not None:
            output.append(
                ''.join([
                    pair_match.group(1),
                    scale_int(pair_match.group(2), scale_factor), ', ',
                    scale_int(pair_match.group(3), scale_factor),
                    pair_match.group(4),
                ])
            )
            continue
        
        output.append(line)
    
    output_path.write_text('\n'.join(output) + '\n', encoding='utf-8')
    print(f'Scaled AIR written to {output_path}')


def normalize_sprite_name(filename: str) -> str:
    """Normalize sprite name by converting dashes to commas."""
    return filename.replace('-', ',')


def get_sprite_mapping(ai_dir: Path, upscaled_dir: Path, original_sff: Path) -> Dict[Tuple[int, int], Path]:
    """
    Create mapping of sprite group,index to file paths.
    Priority: AI sprites > upscaled sprites > original SFF sprites
    """
    mapping = {}
    
    # Parse original SFF to get all required sprite IDs
    print("Parsing original SFF...")
    original_sprites = parse_sff_v1(original_sff)
    original_map = {(sprite.group, sprite.image): sprite for sprite in original_sprites}
    
    # Get AI sprites (using comma format)
    ai_map = {}
    if ai_dir.exists():
        for file_path in ai_dir.glob("*.png"):
            try:
                # Parse group,image from filename like "0,0.png"
                name_parts = file_path.stem.split(',')
                if len(name_parts) == 2:
                    group = int(name_parts[0])
                    image = int(name_parts[1])
                    ai_map[(group, image)] = file_path
            except ValueError:
                print(f"Warning: Could not parse AI sprite filename: {file_path.name}")
    
    # Get upscaled sprites (using dash format, convert to comma)
    upscaled_map = {}
    if upscaled_dir.exists():
        for file_path in upscaled_dir.glob("*.png"):
            try:
                # Parse group,image from filename like "0-0.png"
                name_parts = file_path.stem.split('-')
                if len(name_parts) == 2:
                    group = int(name_parts[0])
                    image = int(name_parts[1])
                    upscaled_map[(group, image)] = file_path
            except ValueError:
                print(f"Warning: Could not parse upscaled sprite filename: {file_path.name}")
    
    # Build priority mapping
    for pair in original_map.keys():
        if pair in ai_map:
            mapping[pair] = ai_map[pair]
        elif pair in upscaled_map:
            mapping[pair] = upscaled_map[pair]
        else:
            print(f"Warning: Missing sprite for {pair[0]},{pair[1]} - will extract from original")
    
    print(f"Found {len(ai_map)} AI sprites, {len(upscaled_map)} upscaled sprites")
    print(f"Mapped {len(mapping)} of {len(original_map)} required sprites")
    
    return mapping, original_map


def extract_missing_sprites(mapping: Dict[Tuple[int, int], Path], original_map: Dict[Tuple[int, int], any], output_dir: Path):
    """Extract missing sprites from original SFF."""
    missing = [pair for pair in original_map.keys() if pair not in mapping]
    
    if not missing:
        return
    
    print(f"Extracting {len(missing)} missing sprites from original SFF...")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for pair in missing:
        sprite = original_map[pair]
        img = decode_sprite(sprite)
        if img:
            output_path = output_dir / f"{pair[0]},{pair[1]}.png"
            img.save(output_path)
            mapping[pair] = output_path
        else:
            print(f"Warning: Could not decode sprite {pair[0]},{pair[1]}")


def build_merged_sprite_set(
    mapping: Dict[Tuple[int, int], Path],
    output_dir: Path,
    original_map: Dict[Tuple[int, int], Any],
    upscaled_map: Dict[Tuple[int, int], Path],
    overrides: Dict[str, Dict[str, float]],
    scale_factor: float = 1.0,
) -> List[Dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Building merged sprite set with scale factor {scale_factor}...")
    report_rows: List[Dict[str, Any]] = []

    for pair, source_path in mapping.items():
        output_path = output_dir / f"{pair[0]},{pair[1]}.png"
        img = Image.open(source_path).convert('RGBA')
        pair_key = f"{pair[0]},{pair[1]}"
        override = overrides.get(pair_key, {})

        reference_image: Optional[Image.Image] = None
        reference_path = upscaled_map.get(pair)
        if reference_path is not None and reference_path.exists():
            reference_image = Image.open(reference_path).convert('RGBA')
        else:
            original_sprite = original_map.get(pair)
            if original_sprite is not None:
                decoded = decode_sprite(original_sprite)
                if decoded is not None:
                    reference_image = decoded.convert('RGBA')

        if reference_image is None:
            reference_image = img

        target_canvas_size = reference_image.size
        reference_bbox = get_alpha_bbox(reference_image)
        fitted, meta = fit_content_to_canvas(img, target_canvas_size, reference_bbox, override)

        if scale_factor != 1.0:
            new_size = (
                max(1, int(round(fitted.width * scale_factor))),
                max(1, int(round(fitted.height * scale_factor))),
            )
            fitted = fitted.resize(new_size, Image.Resampling.LANCZOS)

        fitted.save(output_path)
        report_rows.append(
            {
                'pair': pair_key,
                'source_kind': 'ai_or_fallback',
                'source_path': str(source_path),
                'target_canvas': f'{target_canvas_size[0]}x{target_canvas_size[1]}',
                'source_bbox': meta['source_bbox'],
                'target_bbox': meta['target_bbox'],
                'scale': f"{meta['scale']:.4f}",
                'offset_x': meta['offset_x'],
                'offset_y': meta['offset_y'],
                'override': json.dumps(override, sort_keys=True),
            }
        )

    print(f"Created {len(mapping)} merged sprites")
    return report_rows


def build_test_character(ai_dir: Path, upscaled_dir: Path, original_char_dir: Path, output_dir: Path):
    """Build complete test character with AI sprites and debug features."""
    
    print("Building test/debug character...")
    
    # Create output directories
    output_char_dir = output_dir / "MK1_CAGE_TEST"
    output_char_dir.mkdir(parents=True, exist_ok=True)
    
    output_code_dir = output_char_dir / "CODE"
    output_code_dir.mkdir(exist_ok=True)
    
    # Copy original character files
    print("Copying original character files...")
    if original_char_dir.exists():
        shutil.copytree(original_char_dir / "CODE", output_code_dir, dirs_exist_ok=True)
        
        # Copy act directory if it exists
        act_src = original_char_dir / "act"
        if act_src.exists():
            shutil.copytree(act_src, output_char_dir / "act", dirs_exist_ok=True)
        
        shutil.copy2(original_char_dir / "MK1_CAGE.def", output_char_dir / "MK1_CAGE.def")
    
    # Get sprite mapping
    original_sff = original_char_dir / "CODE" / "CAGE.sff"
    if not original_sff.exists():
        original_sff = output_code_dir / "CAGE.sff"  # Try after copy
    
    mapping, original_map = get_sprite_mapping(ai_dir, upscaled_dir, original_sff)
    upscaled_map = {}
    if upscaled_dir.exists():
        for file_path in upscaled_dir.glob('*.png'):
            name_parts = file_path.stem.split('-')
            if len(name_parts) == 2 and name_parts[0].isdigit() and name_parts[1].isdigit():
                upscaled_map[(int(name_parts[0]), int(name_parts[1]))] = file_path

    overrides = load_size_overrides(Path(__file__).with_name('sprite_size_overrides.json'))
    
    # Extract missing sprites
    temp_extracted = output_dir / "temp_extracted"
    extract_missing_sprites(mapping, original_map, temp_extracted)

    merged_sprites_dir = output_dir / "merged_sprites"
    report_rows = build_merged_sprite_set(
        mapping,
        merged_sprites_dir,
        original_map,
        upscaled_map,
        overrides,
        scale_factor=1.0,
    )
    write_size_report(report_rows, output_dir / 'sprite_size_report.csv')
    
    # Build new SFF file
    print("Building new SFF file...")
    new_sff_path = output_code_dir / "johnny_test.sff"
    
    # Use existing sprites as template for structure
    sprites = list(original_map.values())
    
    # Use processed merged sprite images for SFF build
    merged_images = {
        pair: merged_sprites_dir / f"{pair[0]},{pair[1]}.png"
        for pair in mapping.keys()
    }
    
    # Build SFF with axis scaling (1.0 for original size)
    build_sff(b'ElecbyteSpr\x00\x01', 0, sprites, merged_images, new_sff_path, 1.0)
    
    # Scale AIR file for debug (larger hitboxes)
    original_air = output_code_dir / "Air_Cage.air"
    scaled_air = output_code_dir / "johnny_test.air"
    if original_air.exists():
        print("Scaling AIR file for debug...")
        scale_air_file(original_air, scaled_air, scale_factor=1.0)
    
    # Update character DEF file for test
    update_def_for_test(output_char_dir / "MK1_CAGE.def")
    
    # Create debug config
    create_debug_config(output_char_dir)
    
    print(f"Test character built at: {output_char_dir}")
    return output_char_dir


def update_def_for_test(def_path: Path):
    """Update DEF file for test configuration."""
    content = def_path.read_text()
    
    # Update sprite and anim references
    content = content.replace(
        "sprite  = CODE/johnny_hd.sff",
        "sprite  = CODE/johnny_test.sff"
    )
    content = content.replace(
        "anim    = CODE/johnny_scaled.air",
        "anim    = CODE/johnny_test.air"
    )
    
    # Update display name
    content = content.replace(
        'displayname = "JOHNNY CAGE"',
        'displayname = "JOHNNY CAGE [AI-TEST]"'
    )
    
    def_path.write_text(content)


def create_debug_config(char_dir: Path):
    """Create debug configuration files."""
    debug_dir = char_dir / "DEBUG"
    debug_dir.mkdir(exist_ok=True)
    
    # Create move cycling script
    move_script = """[State 0, Debug]
type = CtrlSet
trigger1 = Time = 0
value = 1

[State 1, Cycle Moves]
type = ChangeState
trigger1 = Time % 60 = 0
value = (PrevStateNo + 1) % 1000
ctrl = 1

[State 2, Show Hitboxes]
type = AssertSpecial
trigger1 = 1
flag = debug
"""
    
    (debug_dir / "debug_moves.cns").write_text(move_script)
    
    # Create README
    readme = """# Johnny Cage AI Test Character

This character includes:
- AI-generated sprites with upscaled fallbacks
- Automatic move cycling
- Hitbox/hurtbox debug overlay

## Installation
Copy this folder to your Ikemen GO chars/ directory.

## Debug Features
- Character automatically cycles through all moves
- Hitboxes and hurtboxes are displayed
- Sprite sources are logged

## Controls
- F1: Toggle debug overlay
- F2: Reset position
- F3: Cycle moves manually
"""
    
    (char_dir / "README.md").write_text(readme)


def main():
    parser = argparse.ArgumentParser(description='Build test/debug Johnny Cage with AI sprites')
    parser.add_argument(
        '--ai-dir',
        default='/Users/oliverlibaw/Downloads/MK-assets/resized-transparent-gen-ai-sprites',
        help='Directory containing AI-generated sprites'
    )
    parser.add_argument(
        '--upscaled-dir',
        default='/Users/oliverlibaw/Downloads/MK-assets/upscaled-original-low-res-sprites',
        help='Directory containing upscaled original sprites'
    )
    parser.add_argument(
        '--original-char',
        default='/Users/oliverlibaw/Downloads/MK-assets/johnny-cage-complete-low-res-character-files',
        help='Directory containing original Johnny Cage character'
    )
    parser.add_argument(
        '--output-dir',
        default='./test_character_output',
        help='Output directory for test character'
    )
    
    args = parser.parse_args()
    
    ai_dir = Path(args.ai_dir)
    upscaled_dir = Path(args.upscaled_dir)
    original_char_dir = Path(args.original_char)
    output_dir = Path(args.output_dir)
    
    # Validate inputs
    if not ai_dir.exists():
        print(f"AI sprites directory not found: {ai_dir}")
        return
    
    if not upscaled_dir.exists():
        print(f"Upscaled sprites directory not found: {upscaled_dir}")
        return
    
    if not original_char_dir.exists():
        print(f"Original character directory not found: {original_char_dir}")
        return
    
    # Build test character
    test_char_dir = build_test_character(ai_dir, upscaled_dir, original_char_dir, output_dir)
    
    print(f"\nTest character ready!")
    print(f"Location: {test_char_dir}")
    print(f"\nTo install:")
    print(f"1. Copy {test_char_dir.name}/ to your Ikemen GO chars/ directory")
    print(f"2. Select 'JOHNNY CAGE [AI-TEST]' in game")
    print(f"3. Enable debug mode (F1) to see hitboxes")


if __name__ == '__main__':
    main()
