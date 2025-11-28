#!/usr/bin/env python
"""
Manual .mo file compiler for Windows environments without gettext
This script converts .po files to .mo files using Python's msgfmt module
"""
import os
import sys
from pathlib import Path

def compile_po_to_mo(po_file):
    """Compile a .po file to .mo file"""
    mo_file = po_file.replace('.po', '.mo')
    
    try:
        # Read .po file
        with open(po_file, 'rb') as f:
            po_content = f.read()
        
        # Use Django's msgfmt
        from django.core.management.commands.compilemessages import Command
        cmd = Command()
        
        # Compile using Django's built-in compiler
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'django.core.management', 'compilemessages'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Compiled: {po_file} -> {mo_file}")
            return True
        else:
            print(f"✗ Failed to compile: {po_file}")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error compiling {po_file}: {e}")
        return False

def main():
    """Find and compile all .po files"""
    print("Compiling translation files...")
    print()
    
    # Find all .po files
    locale_dir = Path('locale')
    po_files = list(locale_dir.glob('**/*.po'))
    
    if not po_files:
        print("No .po files found in locale directory")
        return 1
    
    print(f"Found {len(po_files)} .po file(s)")
    print()
    
    success_count = 0
    for po_file in po_files:
        if compile_po_to_mo(str(po_file)):
            success_count += 1
    
    print()
    print(f"Compiled {success_count}/{len(po_files)} file(s) successfully")
    
    return 0 if success_count == len(po_files) else 1

if __name__ == '__main__':
    sys.exit(main())
