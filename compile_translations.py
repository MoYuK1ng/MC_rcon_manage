#!/usr/bin/env python
"""
Compile .po files to .mo files without requiring gettext tools.
This script uses Python's built-in msgfmt module.
"""
import os
import sys
from pathlib import Path

def compile_po_file(po_file):
    """Compile a single .po file to .mo"""
    try:
        # Import Django's msgfmt compiler
        from django.core.management.commands.compilemessages import Command
        from io import StringIO
        
        # Read the .po file
        with open(po_file, 'r', encoding='utf-8') as f:
            po_content = f.read()
        
        # Generate .mo file path
        mo_file = str(po_file).replace('.po', '.mo')
        
        # Use polib to compile
        try:
            import polib
            po = polib.pofile(str(po_file))
            po.save_as_mofile(str(mo_file))
            print(f"✓ Compiled: {po_file} -> {mo_file}")
            return True
        except ImportError:
            # Fallback: use msgfmt.py from Django
            import subprocess
            result = subprocess.run(
                [sys.executable, '-m', 'django.core.management', 'compilemessages', '-l', 'zh_hans'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ Compiled: {po_file}")
                return True
            else:
                print(f"✗ Failed: {po_file}")
                print(result.stderr)
                return False
                
    except Exception as e:
        print(f"✗ Error compiling {po_file}: {e}")
        return False

def main():
    """Find and compile all .po files"""
    print("Compiling translation files...\n")
    
    # Find all .po files
    locale_dir = Path('locale')
    po_files = list(locale_dir.glob('**/*.po'))
    
    if not po_files:
        print("No .po files found!")
        return 1
    
    print(f"Found {len(po_files)} .po file(s)\n")
    
    # Try to install polib if not available
    try:
        import polib
    except ImportError:
        print("Installing polib...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'polib', '-q'])
        print("✓ polib installed\n")
    
    # Compile each file
    success_count = 0
    for po_file in po_files:
        if compile_po_file(po_file):
            success_count += 1
    
    print(f"\nCompiled {success_count}/{len(po_files)} file(s) successfully")
    return 0 if success_count == len(po_files) else 1

if __name__ == '__main__':
    sys.exit(main())
