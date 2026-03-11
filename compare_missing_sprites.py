#!/usr/bin/env python3
"""
Compare original Johnny Cage sprites with upscaled versions and identify missing ones.
"""

import argparse
from pathlib import Path
from typing import List, Set


def get_sprite_names(directory: Path, extensions: List[str]) -> Set[str]:
    """Get sprite base names (without _upscaled suffix) from directory."""
    if not directory.is_dir():
        return set()
    
    names = set()
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower().lstrip('.') in extensions:
            # Remove _upscaled suffix if present
            name = file_path.stem
            if name.endswith('_upscaled'):
                name = name[:-9]  # Remove '_upscaled'
            names.add(name)
    return names


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Compare original sprites with upscaled versions and find missing ones.'
    )
    parser.add_argument(
        '--original-dir',
        default='Cage_original_sprites',
        help='Directory containing original low-res sprites',
    )
    parser.add_argument(
        '--upscaled-dir',
        default='Cage_upscaled_preview',
        help='Directory containing upscaled sprites',
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['png', 'jpg', 'jpeg', 'bmp', 'tga'],
        help='Image file extensions to consider',
    )
    parser.add_argument(
        '--output',
        help='File to write missing sprites list (default: print to console)',
    )
    
    args = parser.parse_args()
    
    original_dir = Path(args.original_dir)
    upscaled_dir = Path(args.upscaled_dir)
    
    print(f'Original sprites directory: {original_dir}')
    print(f'Upscaled sprites directory: {upscaled_dir}')
    print()
    
    # Get sprite names
    original_names = get_sprite_names(original_dir, args.extensions)
    upscaled_names = get_sprite_names(upscaled_dir, args.extensions)
    
    print(f'Found {len(original_names)} original sprites')
    print(f'Found {len(upscaled_names)} upscaled sprites')
    print()
    
    # Find missing upscaled sprites
    missing = sorted(original_names - upscaled_names)
    completed = sorted(original_names & upscaled_names)
    
    print(f'Completed upscales: {len(completed)}')
    print(f'Missing upscales: {len(missing)}')
    print()
    
    if missing:
        print('Missing upscaled sprites:')
        for name in missing:
            print(f'  {name}')
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text('\n'.join(missing))
            print(f'\nMissing sprites list written to: {output_path}')
    else:
        print('All sprites have been upscaled!')
    
    # Optional: show completed sprites
    if completed and len(completed) <= 20:
        print('\nCompleted upscaled sprites:')
        for name in completed:
            print(f'  {name}')


if __name__ == '__main__':
    main()
