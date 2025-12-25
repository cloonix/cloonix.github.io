#!/usr/bin/env python3
"""
Check if all dependencies for publish-blog-post.py are installed.
Run this before using the publish script for the first time.
"""

import sys

def check_dependency(module_name, package_name=None):
    """Check if a Python module is available"""
    if package_name is None:
        package_name = module_name
    
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {package_name:20s} installed (version: {version})")
        return True
    except ImportError:
        print(f"✗ {package_name:20s} NOT installed")
        return False

def main():
    print("Checking dependencies for publish-blog-post.py\n")
    print("=" * 60)
    
    # Check standard library (should always be available)
    print("\nStandard Library (built-in):")
    print("-" * 60)
    std_libs = [
        ('os', 'os'),
        ('sys', 'sys'),
        ('re', 're'),
        ('shutil', 'shutil'),
        ('argparse', 'argparse'),
        ('pathlib', 'pathlib'),
        ('datetime', 'datetime'),
    ]
    
    for module, name in std_libs:
        check_dependency(module, name)
    
    # Check external dependencies
    print("\nExternal Dependencies (need installation):")
    print("-" * 60)
    
    missing = []
    
    # Check Pillow
    if not check_dependency('PIL', 'Pillow'):
        missing.append('Pillow>=10.0.0')
    else:
        # Check if Image.Resampling is available (Pillow 10+)
        try:
            from PIL import Image
            _ = Image.Resampling.LANCZOS
            print("  → Image.Resampling API available (Pillow 10+)")
        except AttributeError:
            print("  ⚠ Warning: Pillow version may be too old (need 10.0+)")
            print("  → Please upgrade: pip3 install --upgrade Pillow")
    
    # Check PyYAML
    if not check_dependency('yaml', 'PyYAML'):
        missing.append('PyYAML>=6.0')
    
    # Summary
    print("\n" + "=" * 60)
    if missing:
        print("\n❌ Missing dependencies!")
        print("\nTo install missing packages, run:")
        print(f"  pip3 install {' '.join(missing)}")
        print("\nOr install all requirements:")
        print("  pip3 install -r requirements.txt")
        return 1
    else:
        print("\n✅ All dependencies are installed!")
        print("\nYou're ready to use publish-blog-post.py")
        return 0

if __name__ == '__main__':
    sys.exit(main())
