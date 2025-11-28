#!/usr/bin/env python
"""
Compile .po files to .mo files using polib
This works on Windows without requiring gettext tools
"""
import polib
from pathlib import Path

def main():
    print("Compiling translation files with polib...")
    print()
    
    locale_dir = Path('locale')
    po_files = list(locale_dir.glob('**/*.po'))
    
    if not po_files:
        print("✗ No .po files found")
        return 1
    
    success = 0
    for po_file in po_files:
        try:
            mo_file = po_file.with_suffix('.mo')
            po = polib.pofile(str(po_file))
            po.save_as_mofile(str(mo_file))
            print(f"✓ Compiled: {po_file} -> {mo_file}")
            success += 1
        except Exception as e:
            print(f"✗ Failed to compile {po_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print(f"Successfully compiled {success}/{len(po_files)} file(s)")
    return 0 if success == len(po_files) else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
