#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import replicate
import requests

try:
    import replicate
    from PIL import Image
except ImportError as exc:
    print('Missing required packages. Install with:')
    print('pip install replicate pillow')
    sys.exit(1)

SUPIR_MODEL = (
    'zust-ai/supir:'
    '9daf6d19556db0fd6e347a7a5cae7d4a68cf25486266ca3e6dc82618f0a2e0b9'
)

DEFAULT_PARAMS = {
    'upscale': 4,
    'edm_steps': 50,
    's_cfg': 7.5,
    'a_prompt': (
        'Cinematic, high contrast, highly detailed photorealistic 90s martial arts fighter, '
        'studio lighting, realistic fabric textures, skin pore detailing, hyper sharpness, '
        '8k resolution, white background'
    ),
    'n_prompt': (
        'painting, illustration, pixel art, cartoon, 3D render, deformed, blurry, '
        'over-smoothed, flat lighting, background'
    ),
}

ULTRA_MINIMAL_PARAMS = {
    'upscale': 2,
    'edm_steps': 5,
    's_cfg': 7.5,
    'a_prompt': DEFAULT_PARAMS['a_prompt'],
    'n_prompt': DEFAULT_PARAMS['n_prompt'],
}

REALESRGAN_PARAMS = {
    'scale': 4,
    'face_enhance': True,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Upscale Johnny Cage sprites using Replicate SUPIR.'
    )
    parser.add_argument('api_key', help='Replicate API key')
    parser.add_argument(
        '--source-dir',
        default='Cage_all_low_res_sprites',
        help='Folder containing the original low-res sprites',
    )
    parser.add_argument(
        '--output-dir',
        default='Cage_upscaled_preview',
        help='Folder to write upscaled preview images',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=2,
        help='Number of sprites to upscale for preview (default: 2)',
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Use lightweight parameters to avoid GPU memory limits',
    )
    parser.add_argument(
        '--ultra-test',
        action='store_true',
        help='Use ultra-minimal parameters for severely constrained GPU memory',
    )
    parser.add_argument(
        '--use-realesrgan',
        action='store_true',
        help='Use Real-ESRGAN model (faster, lower memory) instead of SUPIR',
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['png', 'jpg', 'jpeg', 'bmp', 'tga'],
        help='Image file extensions to process',
    )
    return parser.parse_args()


def list_image_files(directory: Path, extensions: List[str]) -> List[Path]:
    if not directory.is_dir():
        raise FileNotFoundError(f'Source directory not found: {directory}')
    files = [
        p
        for p in directory.rglob('*')
        if p.is_file() and p.suffix.lower().lstrip('.') in extensions
    ]
    files.sort()
    return files


def upscale_image(api_client: replicate.Client, image_path: Path, output_path: Path, params: Dict[str, Any], model: str) -> None:
    print(f'Upscaling {image_path.name}...')
    try:
        output = api_client.run(
            model,
            input={
                'image': open(image_path, 'rb'),
                **params,
            },
        )
    except Exception as e:
        print(f'  ERROR: {e}')
        return

    if isinstance(output, list) and len(output) > 0:
        result_url = output[0]
    else:
        result_url = output

    response = requests.get(result_url)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    print(f'  Saved: {output_path.resolve()}')


def main() -> None:
    args = parse_args()
    os.environ['REPLICATE_API_TOKEN'] = args.api_key
    client = replicate.Client(api_token=args.api_key)

    src_dir = Path(args.source_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    image_files = list_image_files(src_dir, args.extensions)
    if not image_files:
        print('No image files found in source directory.')
        return

    preview_files = image_files[: args.limit]
    print(f'Found {len(image_files)} total images; upscaling first {len(preview_files)} for preview.')

    params = DEFAULT_PARAMS
    model = 'zust-ai/supir:9daf6d19556db0fd6e347a7a5cae7d4a68cf25486266ca3e6dc82618f0a2e0b9'
    if args.use_realesrgan:
        params = REALESRGAN_PARAMS
        model = 'nightmareai/real-esrgan'
        print('Using Real-ESRGAN model (faster, lower memory).')
    elif args.ultra_test:
        params = ULTRA_MINIMAL_PARAMS
        print('Using ultra-minimal test parameters for severely constrained GPU memory.')
    elif args.test_mode:
        params = LIGHTWEIGHT_TEST_PARAMS
        print('Using lightweight test parameters to avoid GPU memory limits.')

    for img_path in preview_files:
        out_path = out_dir / (img_path.stem + '_upscaled.png')
        upscale_image(client, img_path, out_path, params, model)

    print('\nPreview upscaling complete.')
    print(f'Output directory: {out_dir.resolve()}')


if __name__ == '__main__':
    main()
