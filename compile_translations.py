#!/usr/bin/env python
"""
Compile translation files (.po to .mo)
Run this after updating translation files
"""

import os
import sys
import subprocess

def compile_translations():
    """Compile all .po files to .mo files"""
    print("Compiling translation files...")
    
    try:
        # Run Django's compilemessages command
        result = subprocess.run(
            [sys.executable, 'manage.py', 'compilemessages'],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        print("✓ Translation files compiled successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error compiling translations:")
        print(e.stdout)
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("✗ Error: manage.py not found. Run this script from the project root.")
        return False

if __name__ == '__main__':
    success = compile_translations()
    sys.exit(0 if success else 1)
