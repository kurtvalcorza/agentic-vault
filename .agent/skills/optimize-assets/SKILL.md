---
name: optimize-assets
description: "Optimizes image assets (PNG, JPG) in a directory to WebP/JPG format with optional max file size targeting. Use when you need to reduce asset file sizes for web performance, storage efficiency, or meeting specific size constraints."
---

# Optimize Assets Skill

## Purpose
This skill provides batch processing tools to optimize image assets. Two modes are available:

1. **Standard Optimization** (`batch_optimize.py`): Converts to WebP (quality 80) and re-compresses originals with optimization flags.
2. **Size-Targeted Optimization** (`.agent/scripts/optimize-to-max-size.py`): Uses binary search over quality settings to find the highest quality that fits under a specified file size limit. Supports WebP, JPG, or both.

## Features
- **WebP Conversion**: Generates `.webp` versions for modern browser support.
- **JPEG Conversion**: Generates `.jpg` versions for maximum compatibility.
- **Size-Targeted Mode**: Binary search to hit a max KB target at the highest possible quality.
- **PNGOUT-style Optimization**: Re-compresses PNGs with `optimize=True` (standard mode).
- **Batch Processing**: Handles entire directories at once.

## Usage

### Requirements
```bash
pip install Pillow
```

### Standard Optimization (format conversion, no size target)
```bash
python .agent/skills/optimize-assets/scripts/batch_optimize.py "path/to/assets"
python .agent/skills/optimize-assets/scripts/batch_optimize.py "path/to/assets" --output-dir "dist/assets"
```

### Size-Targeted Optimization (max KB constraint)
```bash
# WebP under 200KB (default)
python .agent/scripts/optimize-to-max-size.py "path/to/images" --max-kb 200

# JPG under 200KB
python .agent/scripts/optimize-to-max-size.py "path/to/images" --max-kb 200 --format jpg

# Both formats
python .agent/scripts/optimize-to-max-size.py "path/to/images" --max-kb 200 --format both

# Custom output directory
python .agent/scripts/optimize-to-max-size.py "path/to/images" --max-kb 150 --output-dir "dist/photos"
```

## Choosing a Mode

| Need | Use |
|------|-----|
| General web optimization, no strict size limit | `batch_optimize.py` |
| Strict max file size (e.g., 200KB for email/press) | `optimize-to-max-size.py` |
| Both WebP and JPG fallback under size limit | `optimize-to-max-size.py --format both` |

## Output
Creates a sibling directory named `<input_dir>-optimized` (or custom `--output-dir`) containing optimized files.

## Examples
```powershell
# Standard optimization
python .agent/skills/optimize-assets/scripts/batch_optimize.py "01_Projects\Project Atlas\cedar\assets"

# Press release photos under 200KB as WebP + JPG fallback
python .agent/scripts/optimize-to-max-size.py "01_Projects\Project Cedar\Press Release\Photos" --max-kb 200 --format both
```
