# Security Policy

## 🔒 Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.3.x   | :white_check_mark: |
| 2.2.x   | :white_check_mark: |
| < 2.2   | :x:                |

## 🛡️ Security Features

MC RCON Manager implements several security measures:

### Authentication & Authorization
- Django's built-in authentication system
- Group-based access control
- Session management with secure cookies
- CSRF protection for all forms

### Data Protection
- **Password Encryption**: RCON passwords are encrypted using Fernet symmetric encryption
- **Never Plaintext**: Passwords are never stored in plaintext
- **Secure Key Storage**: Encryption keys stored in `.env` file (excluded from git)

### Input Validation
- Regex validation for Minecraft usernames: `^[a-zA-Z0-9_]{3,16}$`
- Django form validation
- SQL injection protection via Django ORM
- Command injection prevention

### Production Security
- HTTPS enforcement (HSTS)
- Secure cookie flags
- X-Frame-Options protection
- Content Security Policy headers
- Debug mode disabled in production

## 🚨 Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### DO NOT

- ❌ Open a public GitHub issue
- ❌ Discuss the vulnerability publicly
- ❌ Exploit the vulnerability

### DO

1. **Report Privately**
   - Open a [Security Advisory](https://github.com/MoYuK1ng/MC_rcon_manage/security/advisories/new) on GitHub
   - Or email the maintainer directly (if contact info is available)

2. **Include Details**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

3. **Wait for Response**
   - We will acknowledge receipt within 48 hours
   - We will provide a detailed response within 7 days
   - We will work with you to understand and resolve the issue

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days
- **Public Disclosure**: After fix is released and deployed

## 🏆 Security Hall of Fame

We appreciate security researchers who help keep MC RCON Manager safe. Contributors who responsibly disclose vulnerabilities will be acknowledged here (with permission).

*No vulnerabilities reported yet*

## 🔐 Security Best Practices for Users

### Installation

1. **Use Strong Encryption Keys**
   ```bash
   python generate_key.py  # Generates secure random key
   ```

2. **Secure Your `.env` File**
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

3. **Use Strong Passwords**
   - Admin accounts should use strong, unique passwords
   - Consider using a password manager

### Deployment

1. **HTTPS Only**
   - Always use HTTPS in production
   - Configure SSL/TLS certificates
   - Enable HSTS

2. **Firewall Configuration**
   - Restrict access to admin panel
   - Only allow necessary ports
   - Use fail2ban for brute force protection

3. **Regular Updates**
   ```bash
   git pull origin main
   pip install -r requirements.txt --upgrade
   python manage.py migrate
   ```

4. **Database Security**
   - Use PostgreSQL in production (not SQLite)
   - Regular backups
   - Restrict database access

5. **Environment Variables**
   - Never commit `.env` to git
   - Use different keys for dev/prod
   - Rotate keys periodically

### Monitoring

1. **Check Logs Regularly**
   ```bash
   tail -f /var/log/gunicorn/error.log
   ```

2. **Monitor Failed Login Attempts**
   - Check Django admin logs
   - Set up alerts for suspicious activity

3. **Keep Dependencies Updated**
   ```bash
   pip list --outdated
   pip install -r requirements.txt --upgrade
   ```

## 📋 Security Checklist

Before deploying to production:

- [ ] `DEBUG = False` in settings
- [ ] Strong `SECRET_KEY` generated
- [ ] Encryption key generated and secured
- [ ] HTTPS configured
- [ ] ALLOWED_HOSTS configured
- [ ] CSRF_TRUSTED_ORIGINS configured
- [ ] Database credentials secured
- [ ] Static files served securely
- [ ] Firewall rules configured
- [ ] Regular backup strategy in place
- [ ] Monitoring and logging enabled
- [ ] Security headers configured

## 🔗 Security Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## 📞 Contact

For security concerns, please use:
- GitHub Security Advisories (preferred)
- GitHub Issues (for non-sensitive security discussions)

## 📜 Disclosure Policy

- We follow responsible disclosure practices
- Security fixes are released as soon as possible
- CVE IDs will be requested for significant vulnerabilities
- Public disclosure after fix is available and users have time to update

---

**Thank you for helping keep MC RCON Manager secure! 🛡️**
