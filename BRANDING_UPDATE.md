# Branding Update - Removed IronGate and Jazzmin References

**Date:** November 29, 2025  
**Developer:** MoYuK1ng

## Changes Made

### 1. Removed IronGate Branding
All references to "IronGate" have been replaced with "MC RCON Manager" throughout the codebase:

**Updated Files:**
- `servers/models.py` - Model docstrings
- `servers/views.py` - View docstrings and success messages
- `servers/forms.py` - Form docstrings
- `servers/decorators.py` - Decorator docstrings
- `servers/admin.py` - Admin configuration and site headers
- `servers/services/rcon_manager.py` - Service docstrings
- `servers/utils/encryption.py` - Utility docstrings
- `servers/utils/exceptions.py` - Exception docstrings
- `servers/utils/file_security.py` - Security utility docstrings
- `servers/utils/key_validator.py` - Validator docstrings
- `verify_key.py` - Script docstrings
- `rotate_key.py` - Script docstrings
- `servers/templates/registration/register.html` - Registration page
- `servers/templates/registration/register_zh.html` - Chinese registration page
- `locale/README.md` - Translation documentation
- `locale/zh_hans/LC_MESSAGES/django.po` - Chinese translations
- `README.md` - Project documentation

### 2. Removed Jazzmin Admin Theme
The django-jazzmin package has been removed as it's a third-party UI theme:

**Changes:**
- Removed `jazzmin` from `INSTALLED_APPS` in `irongate/settings.py`
- Removed `django-jazzmin>=2.6.0` from `requirements.txt`
- Removed `JAZZMIN_SETTINGS` and `JAZZMIN_UI_TWEAKS` configuration
- Added custom admin site headers directly in `servers/admin.py`:
  - `admin.site.site_header = "MC RCON Manager Admin"`
  - `admin.site.site_title = "MC RCON Manager"`
  - `admin.site.index_title = "Welcome to MC RCON Manager Admin Panel"`

### 3. Updated Copyright Information
Footer copyright updated to:
- English: `© 2025 MC RCON Manager by MoYuK1ng`
- Chinese: `© 2025 MC RCON Manager by MoYuK1ng`

## Benefits

1. **Cleaner Branding**: All references now use the actual project name "MC RCON Manager"
2. **Reduced Dependencies**: Removed unnecessary third-party admin theme
3. **Simpler Maintenance**: Using Django's default admin interface
4. **Proper Attribution**: Copyright now properly credits MoYuK1ng as the developer

## Next Steps

If you want to reinstall dependencies without jazzmin:
```bash
pip install -r requirements.txt
```

The admin interface will now use Django's default clean and professional look.

## Translation Note

New translation strings have been added to `locale/zh_hans/LC_MESSAGES/django.po`:
- "Join MC RCON Manager" → "加入 MC RCON Manager"
- "Registration successful! Welcome to MC RCON Manager." → "注册成功！欢迎使用 MC RCON Manager。"
- Admin panel titles in Chinese

To compile translations on Linux/Mac:
```bash
python manage.py compilemessages
```

On Windows, the .po file will be used directly (gettext tools not required for development).
