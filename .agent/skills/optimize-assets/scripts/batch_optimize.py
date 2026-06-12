#!/usr/bin/env python3
import os
import argparse
import sys

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow library is not installed.", file=sys.stderr)
    print("Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

def optimize_image(filepath, optimized_dir):
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in ['.png', '.jpg', '.jpeg']:
        return

    try:
        with Image.open(filepath) as img:
            # 1. Generate WebP
            webp_filename = f"{name}.webp"
            webp_path = os.path.join(optimized_dir, webp_filename)
            print(f"Creating WebP: {webp_filename}")
            img.save(webp_path, "WEBP", quality=80)

            # 2. Optimize Original Format
            if ext == '.png':
                opt_filename = filename
                opt_path = os.path.join(optimized_dir, opt_filename)
                print(f"Optimizing PNG: {opt_filename}")
                img.save(opt_path, "PNG", optimize=True)
            
            elif ext in ['.jpg', '.jpeg']:
                opt_filename = filename
                opt_path = os.path.join(optimized_dir, opt_filename)
                print(f"Optimizing JPG: {opt_filename}")
                img.save(opt_path, "JPEG", optimize=True, quality=85)

    except Exception as e:
        print(f"Failed to process {filename}: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Batch optimize images to WebP and optimized originals.")
    parser.add_argument("input_dir", help="Directory containing images to optimize")
    parser.add_argument("--output-dir", help="Directory to save optimized images (default: <input_dir>-optimized)")
    
    args = parser.parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    if not output_dir:
        output_dir = f"{input_dir.rstrip(os.sep)}-optimized"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Scanning {input_dir}...")
    count = 0
    for root, _, files in os.walk(input_dir):
        for file in files:
            filepath = os.path.join(root, file)
            # Only process files directly in input_dir if recursive walk isn't desired, 
            # but usually recursive is fine or we just stay in root.
            # To match the simple task description: we'll stick to top-level files 
            # if the user just points to a folder. 
            # Let's actually verify if we want recursive. 
            # The previous script was non-recursive. Let's keep it simple (non-recursive) for now
            # or simple 1-level loop to match os.listdir logic.
            pass
    
    # Simple listdir to avoid deep recursion unless requested, matching typical 'assets' folder use case
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    
    for filename in files:
        filepath = os.path.join(input_dir, filename)
        optimize_image(filepath, output_dir)
        count += 1

    print(f"Finished processing {count} files.")

if __name__ == "__main__":
    main()
