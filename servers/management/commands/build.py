import sys
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

# Attempt to import polib, which is a dependency for this command
try:
    import polib
except ImportError:
    polib = None

class Command(BaseCommand):
    help = (
        'Runs the complete build process for the application: '
        'compiles translations, collects static files, and runs migrations.'
    )

    def _compile_translations(self):
        """
        Compiles .po translation files to .mo files using the polib library.
        This method is self-contained and avoids system dependencies like gettext.
        """
        self.stdout.write(self.style.HTTP_INFO("  Step 1/3: Compiling translations..."))
        
        if polib is None:
            raise CommandError(
                "'polib' library not found. Please ensure it is installed "
                "by running: pip install -r requirements.txt"
            )

        project_root = Path().resolve()
        locale_dir = project_root / 'locale'
        if not locale_dir.is_dir():
            self.stdout.write(self.style.WARNING("    - 'locale' directory not found. Skipping translation compilation."))
            return

        po_files = list(locale_dir.glob('**/*.po'))
        if not po_files:
            self.stdout.write("    - No .po files found to compile.")
            return

        success_count = 0
        for po_file in po_files:
            mo_path = po_file.with_suffix('.mo')
            self.stdout.write(f"    - Compiling {po_file.relative_to(project_root)}...")
            try:
                po = polib.pofile(str(po_file), encoding='utf-8')
                po.save_as_mofile(str(mo_path))
                success_count += 1
            except Exception as e:
                raise CommandError(f"Error compiling {po_file}: {e}")
        
        self.stdout.write(self.style.SUCCESS(f"    - Compiled {success_count}/{len(po_files)} file(s)."))

    def _collect_static_files(self):
        """Runs the collectstatic management command."""
        self.stdout.write(self.style.HTTP_INFO("\n  Step 2/3: Collecting static files..."))
        call_command('collectstatic', no_input=True, clear=True, verbosity=1)

    def _run_migrations(self):
        """Runs the migrate management command."""
        self.stdout.write(self.style.HTTP_INFO("\n  Step 3/3: Running database migrations..."))
        call_command('migrate', verbosity=1)

    def handle(self, *args, **options):
        """The main entry point for the 'build' command."""
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS("Starting Application Build Process"))
        self.stdout.write(self.style.SUCCESS("=" * 80))

        try:
            self._compile_translations()
            self._collect_static_files()
            self._run_migrations()
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"\nBuild process failed: {e}"))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 80))
        self.stdout.write(self.style.SUCCESS("✓ Build process completed successfully!"))
        self.stdout.write(self.style.SUCCESS("=" * 80))
