# Translation Files

This directory contains translation files for IronGate.

## Structure

- `zh_hans/LC_MESSAGES/django.po` - Simplified Chinese translations

## Compiling Translations

To compile the translation files, you need GNU gettext tools installed.

### On Windows:
1. Download and install gettext from: https://mlocati.github.io/articles/gettext-iconv-windows.html
2. Add gettext bin directory to your PATH
3. Run: `python manage.py compilemessages`

### On Linux/Mac:
```bash
# Install gettext
sudo apt-get install gettext  # Ubuntu/Debian
brew install gettext           # macOS

# Compile messages
python manage.py compilemessages
```

## Manual Translation

The `django.po` file has been pre-populated with Chinese translations.
If you need to update translations:

1. Edit the `msgstr` values in `locale/zh_hans/LC_MESSAGES/django.po`
2. Run `python manage.py compilemessages` to generate the `.mo` file
3. Restart the Django server

## Note

The application will work without compiled `.mo` files, but translations won't be displayed.
English will be used as the fallback language.
