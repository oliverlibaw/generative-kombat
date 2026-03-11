#!/usr/bin/env python3
"""
Interactive sprite review tool for comparing low-res and HD sprites.
Mark sprites that need replacement or fixing with checkboxes.
"""

import argparse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Set, Dict
from PIL import Image, ImageTk
import os


class SpriteReviewApp:
    def __init__(self, low_res_dir: Path, hd_dir: Path, output_file: Path = None):
        self.low_res_dir = low_res_dir
        self.hd_dir = hd_dir
        self.output_file = output_file
        self.sprite_names: List[str] = []
        self.checkboxes: Dict[str, tk.BooleanVar] = {}
        self.image_labels: Dict[str, tk.Label] = {}
        
        self.root = tk.Tk()
        self.root.title("Sprite Review - Mark for Replacement/Fixing")
        self.root.geometry("1200x800")
        
        self.setup_ui()
        self.load_sprites()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Sprite Review Tool", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(main_frame, text="Check sprites that need replacement or fixing. Use arrow keys to navigate.", wraplength=800)
        instructions.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Scrollable frame for sprites
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Bind keyboard navigation
        self.root.bind("<Down>", lambda e: self.navigate_sprites(1))
        self.root.bind("<Up>", lambda e: self.navigate_sprites(-1))
        self.root.bind("<space>", lambda e: self.toggle_current_checkbox())
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Save Selected", command=self.save_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.canvas = canvas
        self.current_row = 0
        
    def load_sprites(self):
        """Load sprite names from both directories."""
        low_res_names = self.get_sprite_names(self.low_res_dir)
        hd_names = self.get_sprite_names(self.hd_dir)
        
        # Get all unique sprite names
        all_names = sorted(low_res_names | hd_names)
        
        if not all_names:
            messagebox.showerror("Error", "No sprite files found in the specified directories.")
            return
        
        self.sprite_names = all_names
        self.create_sprite_widgets()
        self.status_var.set(f"Loaded {len(all_names)} sprites")
        
    def normalize_sprite_name(self, filename: str) -> str:
        """Normalize sprite name by converting dashes to commas."""
        return filename.replace('-', ',')
        
    def get_sprite_names(self, directory: Path) -> Set[str]:
        """Get sprite base names from directory."""
        if not directory.is_dir():
            return set()
        
        names = set()
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tga']:
                # Normalize name by converting dashes to commas
                normalized_name = self.normalize_sprite_name(file_path.stem)
                names.add(normalized_name)
        return names
        
    def create_sprite_widgets(self):
        """Create widgets for each sprite."""
        for i, sprite_name in enumerate(self.sprite_names):
            row_frame = ttk.Frame(self.scrollable_frame)
            row_frame.grid(row=i*2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
            
            # Checkbox
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(row_frame, text=sprite_name, variable=var)
            checkbox.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.checkboxes[sprite_name] = var
            
            # Status labels
            low_res_status = ttk.Label(row_frame, text="", foreground="blue")
            low_res_status.grid(row=0, column=1, padx=5)
            
            hd_status = ttk.Label(row_frame, text="", foreground="green")
            hd_status.grid(row=0, column=2, padx=5)
            
            # Check file existence (handle both dash and comma formats)
            low_res_path_dash = self.low_res_dir / f"{sprite_name}.png"
            low_res_path_comma = self.low_res_dir / f"{sprite_name.replace(',', '-')}.png"
            hd_path = self.hd_dir / f"{sprite_name}.png"
            
            # Use whichever format exists for low-res
            low_res_path = low_res_path_dash if low_res_path_dash.exists() else low_res_path_comma
            
            if low_res_path.exists():
                low_res_status.config(text="✓ Low-res")
            else:
                low_res_status.config(text="✗ Low-res missing", foreground="red")
                
            if hd_path.exists():
                hd_status.config(text="✓ HD")
            else:
                hd_status.config(text="✗ HD missing", foreground="orange")
            
            # Image preview frame
            preview_frame = ttk.Frame(self.scrollable_frame)
            preview_frame.grid(row=i*2+1, column=0, sticky=(tk.W, tk.E), padx=5, pady=(0, 10))
            
            # Load and display images
            self.load_sprite_preview(preview_frame, sprite_name, low_res_path, hd_path)
            
            # Bind row selection for keyboard navigation
            row_frame.bind("<Button-1>", lambda e, r=i: self.set_current_row(r))
            preview_frame.bind("<Button-1>", lambda e, r=i: self.set_current_row(r))
            
    def load_sprite_preview(self, parent, sprite_name: str, low_res_path: Path, hd_path: Path):
        """Load and display sprite previews."""
        # Low-res preview
        low_res_label = ttk.Label(parent, text="Low-res:")
        low_res_label.grid(row=0, column=0, padx=5)
        
        low_res_img_label = ttk.Label(parent, text="Not found", foreground="red")
        low_res_img_label.grid(row=0, column=1, padx=5)
        
        if low_res_path.exists():
            try:
                img = Image.open(low_res_path)
                img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                low_res_img_label.config(image=photo, text="")
                low_res_img_label.image = photo  # Keep reference
            except Exception as e:
                low_res_img_label.config(text="Error loading", foreground="red")
        
        # HD preview
        hd_label = ttk.Label(parent, text="HD:")
        hd_label.grid(row=0, column=2, padx=(20, 5))
        
        hd_img_label = ttk.Label(parent, text="Not found", foreground="orange")
        hd_img_label.grid(row=0, column=3, padx=5)
        
        if hd_path.exists():
            try:
                img = Image.open(hd_path)
                img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                hd_img_label.config(image=photo, text="")
                hd_img_label.image = photo  # Keep reference
            except Exception as e:
                hd_img_label.config(text="Error loading", foreground="red")
                
    def set_current_row(self, row: int):
        """Set current row for keyboard navigation."""
        self.current_row = row
        
    def navigate_sprites(self, direction: int):
        """Navigate between sprites with arrow keys."""
        new_row = self.current_row + direction
        if 0 <= new_row < len(self.sprite_names):
            self.current_row = new_row
            # Scroll to make current row visible
            self.canvas.yview_moveto((new_row * 2) / (len(self.sprite_names) * 2))
            
    def toggle_current_checkbox(self):
        """Toggle checkbox for current sprite."""
        if self.current_row < len(self.sprite_names):
            sprite_name = self.sprite_names[self.current_row]
            var = self.checkboxes[sprite_name]
            var.set(not var.get())
            
    def select_all(self):
        """Select all sprites."""
        for var in self.checkboxes.values():
            var.set(True)
            
    def deselect_all(self):
        """Deselect all sprites."""
        for var in self.checkboxes.values():
            var.set(False)
            
    def save_selected(self):
        """Save list of selected sprites."""
        selected = [name for name, var in self.checkboxes.items() if var.get()]
        
        if not selected:
            messagebox.showinfo("Info", "No sprites selected.")
            return
            
        output_text = "\n".join(selected)
        
        if self.output_file:
            self.output_file.write_text(output_text)
            messagebox.showinfo("Success", f"Saved {len(selected)} sprites to {self.output_file}")
        else:
            # Show in a new window
            result_window = tk.Toplevel(self.root)
            result_window.title("Selected Sprites")
            result_window.geometry("400x500")
            
            text_widget = tk.Text(result_window, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.insert(tk.END, output_text)
            text_widget.config(state=tk.DISABLED)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            copy_button = ttk.Button(result_window, text="Copy to Clipboard", 
                                    command=lambda: self.root.clipboard_clear() or self.root.clipboard_append(output_text))
            copy_button.pack(pady=5)
            
    def run(self):
        """Start the GUI."""
        self.root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Interactive sprite review tool for comparing low-res and HD sprites.'
    )
    parser.add_argument(
        '--low-res-dir',
        default='low_res_sprites',
        help='Directory containing low-res sprites',
    )
    parser.add_argument(
        '--hd-dir',
        default='hd_sprites',
        help='Directory containing HD sprites',
    )
    parser.add_argument(
        '--output',
        help='File to write selected sprites list (default: show in window)',
    )
    
    args = parser.parse_args()
    
    low_res_dir = Path(args.low_res_dir)
    hd_dir = Path(args.hd_dir)
    output_file = Path(args.output) if args.output else None
    
    if not low_res_dir.exists():
        print(f"Low-res directory not found: {low_res_dir}")
        return
        
    if not hd_dir.exists():
        print(f"HD directory not found: {hd_dir}")
        return
    
    app = SpriteReviewApp(low_res_dir, hd_dir, output_file)
    app.run()


if __name__ == '__main__':
    main()
