#!/usr/bin/env python
"""
Compiles .po translation files to .mo files using the polib library.
This script has no external system dependencies (like gettext) and is suitable
for production and containerized environments.
"""
import os
import sys
from pathlib import Path

try:
    import polib
except ImportError:
    print("Error: 'polib' library not found.", file=sys.stderr)
    print("Please install it by running: pip install polib", file=sys.stderr)
    sys.exit(1)

def main():
    """Finds and compiles all .po files in the 'locale' directory."""
    print("Compiling translation files using 'polib'...")
    
    project_root = Path(__file__).parent
    locale_dir = project_root / 'locale'
    
    if not locale_dir.is_dir():
        print(f"Error: 'locale' directory not found in '{project_root}'", file=sys.stderr)
        return 1
        
    po_files = list(locale_dir.glob('**/*.po'))
    
    if not po_files:
        print("No .po files found to compile.")
        return 0
        
    print(f"Found {len(po_files)} .po file(s)...")
    success_count = 0
    
    for po_file in po_files:
        mo_path = po_file.with_suffix('.mo')
        try:
            print(f"  - Compiling {po_file.relative_to(project_root)} -> {mo_path.relative_to(project_root)}")
            po = polib.pofile(str(po_file), encoding='utf-8')
            po.save_as_mofile(str(mo_path))
            success_count += 1
        except Exception as e:
            print(f"  ✗ Error compiling {po_file.relative_to(project_root)}: {e}", file=sys.stderr)
            
    print(f"\n✓ Compiled {success_count}/{len(po_files)} file(s).")
    
    if success_count != len(po_files):
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())