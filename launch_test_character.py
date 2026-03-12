#!/usr/bin/env python3
"""
Launch script for Johnny Cage AI Test Character
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
import json


def find_ikemen_executable():
    """Find Ikemen GO executable in common locations."""
    possible_paths = [
        "./ikemen-go-stable/Ikemen_GO.command",
        "./ikemen-go-clean/Ikemen_GO.command",
        "./ikemen-go-stable/Ikemen_GO_MacOS",
        "./ikemen-go-clean/Ikemen_GO_MacOS",
        "./ikemen-go-stable/ikemen",
        "./ikemen-go-clean/ikemen",
        "./ikemen-go",
        "/usr/local/bin/ikemen",
    ]
    
    for path in possible_paths:
        exe_path = Path(path)
        if exe_path.exists():
            return exe_path
    
    # Try to find in current directory
    for exe_path in Path(".").rglob("Ikemen_GO_MacOS"):
        if exe_path.is_file():
            return exe_path
    
    for exe_path in Path(".").rglob("Ikemen_GO.command"):
        if exe_path.is_file():
            return exe_path
    
    return None


def install_test_character(ikemen_dir: Path, test_char_dir: Path):
    """Install test character to Ikemen GO chars directory."""
    chars_dir = ikemen_dir / "chars"
    chars_dir.mkdir(exist_ok=True)
    
    target_dir = chars_dir / test_char_dir.name
    
    # Remove existing installation
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    # Copy test character
    shutil.copytree(test_char_dir, target_dir)
    print(f"Installed test character to: {target_dir}")
    
    return target_dir


def register_character(ikemen_dir: Path, char_entry: str):
    """Register the test character in select.def if missing."""
    select_def = ikemen_dir / "data" / "select.def"
    if not select_def.exists():
        print("Warning: select.def not found, skipping character registration")
        return

    content = select_def.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Only consider the character "registered" if it exists as an active line
    # inside the [Characters] section (not in comments/help text).
    def _is_active_entry(line: str) -> bool:
        stripped = line.strip()
        return bool(stripped) and not stripped.startswith(";")

    in_characters = False
    found_active = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "[characters]":
            in_characters = True
            continue
        if in_characters and stripped.startswith("[") and stripped.endswith("]"):
            in_characters = False
        if in_characters and _is_active_entry(line) and stripped == char_entry:
            found_active = True
            break

    if found_active:
        print(f"Character already registered: {char_entry}")
        return

    # Clean up any stray accidental insertions outside [Characters].
    # (e.g. a broken line containing MK1_CAGE_TEST that ended up in comment blocks)
    cleaned_lines = []
    in_characters = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "[characters]":
            in_characters = True
            cleaned_lines.append(line)
            continue
        if in_characters and stripped.startswith("[") and stripped.endswith("]"):
            in_characters = False
        if (not in_characters) and _is_active_entry(line) and ("MK1_CAGE_TEST" in stripped):
            continue
        cleaned_lines.append(line)
    lines = cleaned_lines

    # Insert into the actual [Characters] section.
    insert_at = None
    in_characters = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower() == "[characters]":
            in_characters = True
            continue
        if in_characters:
            # Insert before the first randomselect *within* the section.
            if stripped.lower().startswith("randomselect"):
                insert_at = idx
                break
            # If the section ends, fall back to inserting at the end of the section.
            if stripped.startswith("[") and stripped.endswith("]"):
                insert_at = idx
                break
    if insert_at is None:
        lines.append(char_entry)
    else:
        lines.insert(insert_at, char_entry)

    content = "\n".join(lines) + "\n"
    select_def.write_text(content, encoding="utf-8")
    print(f"Registered character in select.def: {char_entry}")


def configure_debug_settings(ikemen_dir: Path):
    """Configure Ikemen GO for debug mode."""
    config_path = ikemen_dir / "save" / "config.json"
    
    if not config_path.exists():
        print("Warning: config.json not found, skipping debug configuration")
        return
    
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["DebugMode"] = True
    config["DebugKeys"] = True
    config["DebugClipboardRows"] = max(4, int(config.get("DebugClipboardRows", 2)))
    config["GameWidth"] = 1280
    config["GameHeight"] = 720
    config["Fullscreen"] = False
    config["WindowCentered"] = True
    common_lua = list(config.get("CommonLua", []))
    init_line = "if __cascade_debug_init == nil then toggleDebugDraw(); toggleClsnDraw(); __cascade_debug_init = true end"
    if init_line not in common_lua:
        common_lua.insert(0, init_line)
    if "loop()" not in common_lua:
        common_lua.append("loop()")
    config["CommonLua"] = common_lua
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print("Enabled debug mode in config.json")


def launch_game(ikemen_exe: Path, character_name: str):
    """Launch Ikemen GO with the test character."""
    cmd = [f"./{ikemen_exe.name}"]
    cwd = ikemen_exe.parent
    if ikemen_exe.name.endswith('.command'):
        cmd = ["bash", ikemen_exe.name]
    elif ikemen_exe.name == 'Ikemen_GO_MacOS':
        cmd = ["./Ikemen_GO_MacOS", "-AppleMagnifiedMode", "YES", "-debug"]
    
    print(f"Launching game: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error launching game: {e}")
        return False
    except KeyboardInterrupt:
        print("Game stopped by user")
        return True
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Launch Johnny Cage AI Test Character')
    parser.add_argument(
        '--ikemen-dir',
        default='./ikemen-go-stable',
        help='Ikemen GO installation directory'
    )
    parser.add_argument(
        '--test-char',
        default='./test_character_output/MK1_CAGE_TEST',
        help='Test character directory'
    )
    parser.add_argument(
        '--no-install',
        action='store_true',
        help='Skip character installation'
    )
    parser.add_argument(
        '--character-name',
        default='MK1_CAGE_TEST',
        help='Character name for selection'
    )
    parser.add_argument(
        '--no-launch',
        action='store_true',
        help='Install/configure only (do not launch Ikemen GO)'
    )
    
    args = parser.parse_args()
    
    ikemen_dir = Path(args.ikemen_dir)
    test_char_dir = Path(args.test_char)
    
    # Validate paths
    if not ikemen_dir.exists():
        print(f"Ikemen GO directory not found: {ikemen_dir}")
        return
    
    if not test_char_dir.exists():
        print(f"Test character directory not found: {test_char_dir}")
        return
    
    # Find executable
    ikemen_exe = find_ikemen_executable()
    if not ikemen_exe:
        print("Ikemen GO executable not found")
        return
    
    print(f"Found Ikemen GO executable: {ikemen_exe}")
    
    # Install character if needed
    if not args.no_install:
        install_test_character(ikemen_dir, test_char_dir)
        register_character(ikemen_dir, f"{test_char_dir.name}/MK1_CAGE.def, stages/kfm.def")
        configure_debug_settings(ikemen_dir)
    
    # Launch game
    print("\n" + "="*50)
    print("JOHNNY CAGE AI TEST CHARACTER")
    print("="*50)
    print("Features:")
    print("- AI-generated sprites with upscaled fallbacks")
    print("- Automatic move cycling (every 2 seconds)")
    print("- Hitbox/hurtbox debug overlay")
    print("- State and animation info display")
    print("\nDebug Controls:")
    print("- F1: Toggle debug overlay")
    print("- A: Next move")
    print("- S: Previous move") 
    print("- D: Reset to stance")
    print("- W: Pause cycling")
    print("="*50 + "\n")
    
    if args.no_launch:
        print("Skipping launch (--no-launch)")
        return
    
    launch_game(ikemen_exe, args.character_name)


if __name__ == '__main__':
    main()
