import subprocess
import sys
import os

def run_command(command, description):
    """Runs a command and prints its status."""
    print(f"\n[INFO] {description}...", flush=True)
    try:
        if isinstance(command, str):
            command = command.split()
            
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False
        )

        if result.returncode != 0:
            print(f"[ERROR] Failed: {description}", file=sys.stderr)
            # Prefer stderr for error details, fallback to stdout
            error_output = result.stderr if result.stderr else result.stdout
            print(error_output, file=sys.stderr)
            sys.exit(1)
        else:
            print(f"[SUCCESS] {description} complete.")
            if result.stdout.strip():
                 print(result.stdout)

    except FileNotFoundError:
        print(f"[ERROR] Command not found: {command[0]}. Make sure it's installed and in your PATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main build process for the application."""
    print("="*80)
    print("Starting MC RCON Manager Build Process")
    print("="*80)
    
    # Step 1: Compile translations using the dependency-free script
    run_command([sys.executable, "compile_mo.py"], "Step 1/3: Compiling translations")
    
    # Step 2: Collect static files (crucial for django-jazzmin)
    run_command([sys.executable, "manage.py", "collectstatic", "--noinput", "--clear"], "Step 2/3: Collecting static files")

    # Step 3: Run database migrations
    run_command([sys.executable, "manage.py", "migrate"], "Step 3/3: Running database migrations")

    print("\n" + "="*80)
    print("Build process completed successfully!")
    print("="*80)


if __name__ == "__main__":
    if not os.path.exists('manage.py'):
        print("[ERROR] This script must be run from the project's root directory.", file=sys.stderr)
        sys.exit(1)
        
    main()
