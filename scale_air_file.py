#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path

PAIR_RE = re.compile(r'^(\s*[0-9]+\s*,\s*[0-9]+\s*,\s*)(-?\d+)\s*,\s*(-?\d+)(\s*,.*)$')
BOX_RE = re.compile(r'^(\s*Clsn[12](?:Default)?\[\d+\]\s*=\s*)(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(\s*)$')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('input_air')
    parser.add_argument('output_air')
    parser.add_argument('--scale', type=float, default=3.0)
    return parser.parse_args()


def scale_int(value: str, factor: float) -> str:
    return str(int(round(int(value) * factor)))


def main() -> None:
    args = parse_args()
    src = Path(args.input_air)
    dst = Path(args.output_air)
    lines = src.read_text(encoding='utf-8-sig', errors='ignore').splitlines()
    output: list[str] = []

    for line in lines:
        box_match = BOX_RE.match(line)
        if box_match is not None:
            output.append(
                ''.join(
                    [
                        box_match.group(1),
                        scale_int(box_match.group(2), args.scale), ', ',
                        scale_int(box_match.group(3), args.scale), ', ',
                        scale_int(box_match.group(4), args.scale), ', ',
                        scale_int(box_match.group(5), args.scale),
                        box_match.group(6),
                    ]
                )
            )
            continue

        pair_match = PAIR_RE.match(line)
        if pair_match is not None:
            output.append(
                ''.join(
                    [
                        pair_match.group(1),
                        scale_int(pair_match.group(2), args.scale), ', ',
                        scale_int(pair_match.group(3), args.scale),
                        pair_match.group(4),
                    ]
                )
            )
            continue

        output.append(line)

    dst.write_text('\n'.join(output) + '\n', encoding='utf-8')
    print(f'Scaled AIR written to {dst}')


if __name__ == '__main__':
    main()
