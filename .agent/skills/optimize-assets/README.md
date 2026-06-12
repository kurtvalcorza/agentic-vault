# Optimize Assets

Batch image optimization for reducing file sizes in the vault.

## What It Does

Two modes available:

- **Standard**: Converts PNG/JPG to WebP (quality 80) and re-compresses originals. Good for general web optimization.
- **Size-Targeted**: Compresses to WebP and/or JPG under a strict max file size (e.g., 200KB). Uses binary search to find the highest quality that fits. Ideal for press releases, email attachments, or any context with size limits.

## When to Use

- Vault contains large image files
- Preparing presentations or reports for sharing
- Reducing storage footprint
- Optimizing images for web publishing
- Meeting strict file size requirements (e.g., 200KB max per photo)

## Quick Start

**Trigger**: "Optimize assets in [directory]" or "Compress photos to under [X]KB"

Requires Python with Pillow library installed:
```bash
pip install Pillow
```

### Standard (no size limit)
```bash
python .agent/skills/optimize-assets/scripts/batch_optimize.py "path/to/images"
```

### Size-Targeted (max KB)
```bash
python .agent/scripts/optimize-to-max-size.py "path/to/images" --max-kb 200
python .agent/scripts/optimize-to-max-size.py "path/to/images" --max-kb 200 --format jpg
python .agent/scripts/optimize-to-max-size.py "path/to/images" --max-kb 200 --format both
```

## Related Skills

- `purge-desktop-ini` - Clean up system files
- `optimize-workspace` - Comprehensive vault maintenance
