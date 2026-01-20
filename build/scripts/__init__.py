"""
Build Scripts Package
===================

This package contains helper scripts for application packaging.

Available scripts:
- ico_to_icns.py: Convert Windows ICO files to macOS ICNS format
- png_to_icns.py: Convert PNG images to macOS ICNS format
"""

__version__ = "1.0.0"
__author__ = "NormCode"

# Export main functions for programmatic use
from .ico_to_icns import convert_to_icns as ico_to_icns
from .png_to_icns import convert_to_icns as png_to_icns

__all__ = ['ico_to_icns', 'png_to_icns']
