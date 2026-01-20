#!/usr/bin/env python3
"""
PNG to ICNS Converter
====================

This script converts PNG images to macOS ICNS format with all required sizes.

Requirements:
- macOS platform
- iconutil (part of Xcode Command Line Tools)
- Pillow (PIL) for image processing

Usage:
    python png_to_icns.py input.png [output.icns]

Examples:
    python png_to_icns.py icon.png
    python png_to_icns.py icon.png icon.icns
    python png_to_icns.py logo.png --size 512
"""

import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List

try:
    from PIL import Image
except ImportError:
    print("[ERROR] Pillow (PIL) is required")
    print("        Install with: pip install Pillow")
    sys.exit(1)

# Platform check
if sys.platform != "darwin":
    print("[ERROR] This script requires macOS")
    print("        iconutil is only available on macOS")
    sys.exit(1)


# Required icon sizes for macOS (standard + retina)
ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def check_iconutil() -> bool:
    """Check if iconutil is available."""
    iconutil_path = shutil.which("iconutil")
    if not iconutil_path:
        print("[ERROR] iconutil not found")
        print("[INFO] iconutil is part of Xcode Command Line Tools")
        print("[INFO] Install with: xcode-select --install")
        return False
    return True


def create_iconset(png_path: Path, iconset_dir: Path, max_size: int = 1024) -> bool:
    """
    Create an iconset directory with all required sizes from a PNG.
    
    Args:
        png_path: Path to the input PNG file
        iconset_dir: Path to the iconset directory
        max_size: Maximum icon size to generate (default: 1024)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create iconset directory
        iconset_dir.mkdir(parents=True, exist_ok=True)
        
        # Load source PNG
        print(f"  Loading source image: {png_path}")
        source = Image.open(png_path)
        
        # Check source size
        source_size = source.size[0]  # Assuming square
        print(f"  Source size: {source_size}x{source_size}")
        
        if source.size[0] != source.size[1]:
            print(f"[WARN] Source image is not square: {source.size}")
            print("[INFO] Icons should be square for best results")
        
        # Convert to RGBA if needed
        if source.mode != 'RGBA':
            source = source.convert('RGBA')
            print(f"  Converted to RGBA mode")
        
        # Generate required sizes (only up to max_size)
        sizes_to_generate = [s for s in ICON_SIZES if s <= max_size]
        generated_count = 0
        
        for target_size in sizes_to_generate:
            # Determine if we need to resize
            if source_size >= target_size:
                # Source is large enough, resize down
                resized = source.resize((target_size, target_size), Image.Resampling.LANCZOS)
                print(f"  Generated {target_size}x{target_size} (resized from {source_size}x{source_size})")
            elif target_size == sizes_to_generate[-1]:
                # Use source as is for largest size if it's smaller
                resized = source
                print(f"  Using source as {target_size}x{target_size} (actual: {source_size}x{source_size})")
            else:
                # Skip if source is too small (unless it's the largest target)
                print(f"  Skipping {target_size}x{target_size} (source too small: {source_size}x{source_size})")
                continue
            
            # Save standard resolution
            standard_path = iconset_dir / f"icon_{target_size}x{target_size}.png"
            resized.save(standard_path, "PNG")
            generated_count += 1
            
            # Save Retina (@2x) resolution if size <= 512
            if target_size <= 512:
                retina_size = target_size * 2
                retina_path = iconset_dir / f"icon_{target_size}x{target_size}@2x.png"
                
                if source_size >= retina_size:
                    retina_img = source.resize((retina_size, retina_size), Image.Resampling.LANCZOS)
                    print(f"  Generated {retina_size}x{retina_size} (@2x)")
                else:
                    # Use same image for retina if source is too small
                    retina_img = resized
                    print(f"  Using {target_size}x{target_size} for {retina_size}x{retina_size} (@2x)")
                
                retina_img.save(retina_path, "PNG")
        
        print(f"  [OK] Generated {generated_count} sizes")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create iconset: {e}")
        import traceback
        traceback.print_exc()
        return False


def convert_to_icns(iconset_dir: Path, output_path: Path) -> bool:
    """
    Convert iconset directory to ICNS file using iconutil.
    
    Args:
        iconset_dir: Path to the iconset directory
        output_path: Path for the output ICNS file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Verify iconset directory exists
        if not iconset_dir.exists():
            print(f"[ERROR] Iconset directory not found: {iconset_dir}")
            return False
        
        # Remove existing ICNS file if present
        if output_path.exists():
            output_path.unlink()
        
        # Create parent directory for output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run iconutil
        cmd = [
            "iconutil",
            "-c", "icns",
            str(iconset_dir),
            "-o", str(output_path)
        ]
        
        print(f"\n-> Running iconutil...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print(f"[ERROR] iconutil failed with exit code {result.returncode}")
            print(f"       stderr: {result.stderr}")
            return False
        
        # Verify output
        if output_path.exists():
            file_size = output_path.stat().st_size
            file_size_kb = file_size / 1024
            print(f"[OK] Created ICNS file: {output_path}")
            print(f"     Size: {file_size_kb:.2f} KB")
            return True
        else:
            print("[ERROR] ICNS file was not created")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to convert to ICNS: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert PNG images to macOS ICNS format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python png_to_icns.py icon.png
  python png_to_icns.py icon.png icon.icns
  python png_to_icns.py logo.png --size 512
  python png_to_icns.py Psylensai_log_raw.png --output resources/icon.icns
        """
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Input PNG file path"
    )
    
    parser.add_argument(
        "output",
        type=str,
        nargs='?',
        help="Output ICNS file path (default: same as input with .icns extension)"
    )
    
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=1024,
        metavar="MAX_SIZE",
        help="Maximum icon size to generate (default: 1024, valid: 16, 32, 64, 128, 256, 512, 1024)"
    )
    
    parser.add_argument(
        "-k", "--keep-iconset",
        action="store_true",
        help="Keep the iconset directory after conversion (for debugging)"
    )
    
    args = parser.parse_args()
    
    # Check iconutil
    if not check_iconutil():
        sys.exit(1)
    
    # Parse input path
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    
    if input_path.suffix.lower() != '.png':
        print(f"[WARN] Input file doesn't have .png extension: {input_path}")
    
    # Validate max_size
    valid_sizes = ICON_SIZES
    if args.size not in valid_sizes:
        print(f"[ERROR] Invalid max size: {args.size}")
        print(f"[INFO] Valid sizes are: {valid_sizes}")
        sys.exit(1)
    
    # Parse output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        # Replace .png with .icns
        output_path = input_path.with_suffix('.icns')
    
    print("=" * 60)
    print("  PNG to ICNS Converter")
    print("=" * 60)
    print(f"\nInput:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Max Size: {args.size}x{args.size}")
    
    # Create iconset directory
    iconset_dir = output_path.parent / f"{output_path.stem}.iconset"
    print(f"\n-> Creating iconset at: {iconset_dir}")
    
    if not create_iconset(input_path, iconset_dir, args.size):
        print("[ERROR] Failed to create iconset")
        sys.exit(1)
    
    # Convert to ICNS
    if not convert_to_icns(iconset_dir, output_path):
        print("[ERROR] Failed to convert to ICNS")
        # Cleanup
        if iconset_dir.exists():
            shutil.rmtree(iconset_dir)
        sys.exit(1)
    
    # Cleanup iconset directory (unless --keep-iconset)
    if not args.keep_iconset:
        if iconset_dir.exists():
            shutil.rmtree(iconset_dir)
            print(f"-> Cleaned up iconset directory")
    else:
        print(f"-> Keeping iconset directory at: {iconset_dir}")
    
    print("\n" + "=" * 60)
    print("  Conversion successful!")
    print("=" * 60)
    print(f"\nOutput file: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    main()
