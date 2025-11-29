#!/usr/bin/env python
"""
Manual .mo file compiler.
This script compiles .po files to .mo files using Django's management command.
"""
import sys
import subprocess

def main():
    """Run Django's compilemessages command."""
    print("Compiling translation files...")
    
    try:
        # Use the standard manage.py command which is the most robust method
        result = subprocess.run(
            [sys.executable, 'manage.py', 'compilemessages'],
            capture_output=True,
            text=True,
            check=False,  # We'll check the return code manually
            encoding='utf-8'
        )
        
        # Print stdout which contains the processing info
        if result.stdout:
            print(result.stdout)

        # If there's an error, print it and exit
        if result.returncode != 0:
            print("Error during compilation:", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return 1

        print("\n✓ Compilation finished.")
        return 0
        
    except FileNotFoundError:
        print("Error: 'manage.py' not found. Are you in the project root directory?", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
