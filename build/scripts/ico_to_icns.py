#!/usr/bin/env python3
"""
ICO to ICNS Converter
====================

This script converts Windows ICO files to macOS ICNS format.

Requirements:
- macOS platform
- iconutil (part of Xcode Command Line Tools)
- Pillow (PIL) for image processing

Usage:
    python ico_to_icns.py input.ico [output.icns]

Examples:
    python ico_to_icns.py icon.ico
    python ico_to_icns.py icon.ico icon.icns
    python ico_to_icns.py ../resources/icon.ico ./icon.icns
"""

import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

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


def extract_ico_sizes(ico_path: Path) -> List[Tuple[int, Image.Image]]:
    """
    Extract all sizes from an ICO file.
    
    Returns:
        List of (size, image) tuples
    """
    try:
        img = Image.open(ico_path)
        sizes = []
        
        # ICO files can have multiple sizes embedded
        # We'll extract all available sizes
        for i in range(20):  # Check up to 20 frames
            try:
                img.seek(i)
                size = img.size[0]  # Assuming square icons
                # Create a copy of the image for each size
                sizes.append((size, img.copy()))
            except EOFError:
                break
            except Exception as e:
                print(f"[WARN] Error reading frame {i}: {e}")
                continue
        
        return sizes
    except Exception as e:
        print(f"[ERROR] Failed to open ICO file: {e}")
        return []


def create_iconset(ico_path: Path, iconset_dir: Path, sizes_data: List[Tuple[int, Image.Image]]) -> bool:
    """
    Create an iconset directory with all required sizes.
    
    Args:
        ico_path: Path to the input ICO file
        iconset_dir: Path to the iconset directory
        sizes_data: List of (size, image) tuples extracted from ICO
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create iconset directory
        iconset_dir.mkdir(parents=True, exist_ok=True)
        
        # Dictionary to store the best image for each size
        size_dict = {}
        
        # Organize images by size
        for size, img in sizes_data:
            # Store the image; if multiple images have the same size, keep the last one
            size_dict[size] = img
        
        # Generate all required sizes
        generated_sizes = []
        for target_size in ICON_SIZES:
            # Find the best source image
            source_size = None
            source_img = None
            
            # Strategy: Use the closest size >= target_size, or the largest available
            # Sort available sizes
            available_sizes = sorted(size_dict.keys())
            
            # Try to find a size >= target_size
            for size in available_sizes:
                if size >= target_size:
                    source_size = size
                    source_img = size_dict[size]
                    break
            
            # If no size >= target_size, use the largest
            if source_img is None:
                source_size = max(available_sizes)
                source_img = size_dict[source_size]
            
            # Resize the image
            if source_size != target_size:
                # Resize using high-quality resampling
                resized = source_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                print(f"  Resized {source_size}x{source_size} -> {target_size}x{target_size}")
            else:
                resized = source_img
                print(f"  Using original size {target_size}x{target_size}")
            
            # Convert to RGBA if needed
            if resized.mode != 'RGBA':
                resized = resized.convert('RGBA')
            
            # Save standard resolution
            standard_path = iconset_dir / f"icon_{target_size}x{target_size}.png"
            resized.save(standard_path, "PNG")
            generated_sizes.append(target_size)
            
            # Save Retina (@2x) resolution if size <= 512
            if target_size <= 512:
                retina_size = target_size * 2
                retina_path = iconset_dir / f"icon_{target_size}x{target_size}@2x.png"
                
                # Check if we already have a source for retina size
                if retina_size in size_dict:
                    retina_img = size_dict[retina_size]
                else:
                    # Resize to retina size
                    retina_img = resized.resize((retina_size, retina_size), Image.Resampling.LANCZOS)
                    print(f"  Generated retina {retina_size}x{retina_size} (@2x)")
                
                # Ensure RGBA
                if retina_img.mode != 'RGBA':
                    retina_img = retina_img.convert('RGBA')
                
                retina_img.save(retina_path, "PNG")
        
        print(f"  [OK] Generated {len(generated_sizes)} sizes: {sorted(generated_sizes)}")
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
        description="Convert Windows ICO files to macOS ICNS format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ico_to_icns.py icon.ico
  python ico_to_icns.py icon.ico icon.icns
  python ico_to_icns.py ../resources/icon.ico ./icon.icns --verbose
        """
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Input ICO file path"
    )
    
    parser.add_argument(
        "output",
        type=str,
        nargs='?',
        help="Output ICNS file path (default: same as input with .icns extension)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
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
    
    if input_path.suffix.lower() != '.ico':
        print(f"[WARN] Input file doesn't have .ico extension: {input_path}")
    
    # Parse output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        # Replace .ico with .icns
        output_path = input_path.with_suffix('.icns')
    
    print("=" * 60)
    print("  ICO to ICNS Converter")
    print("=" * 60)
    print(f"\nInput:  {input_path}")
    print(f"Output: {output_path}")
    
    # Extract sizes from ICO
    print(f"\n-> Extracting sizes from ICO...")
    sizes_data = extract_ico_sizes(input_path)
    
    if not sizes_data:
        print("[ERROR] No sizes found in ICO file")
        sys.exit(1)
    
    available_sizes = sorted(set(size for size, _ in sizes_data))
    print(f"  Found sizes: {available_sizes}")
    
    # Create iconset directory
    iconset_dir = output_path.parent / f"{output_path.stem}.iconset"
    print(f"\n-> Creating iconset at: {iconset_dir}")
    
    if not create_iconset(input_path, iconset_dir, sizes_data):
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
