# Production Deployment Checklist

This checklist ensures your MC RCON Manager deployment is secure, optimized, and production-ready.

## Pre-Deployment

### Security Configuration

- [ ] **Generate new SECRET_KEY** for Django
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] **Generate RCON encryption key**
  ```bash
  python generate_key.py
  ```

- [ ] **Set DEBUG=False** in `.env`

- [ ] **Configure ALLOWED_HOSTS** with your domain(s)
  ```
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
  ```

- [ ] **Configure CSRF_TRUSTED_ORIGINS** with protocol
  ```
  CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  ```

- [ ] **Review file permissions** on `.env` file
  ```bash
  chmod 600 .env
  ```

- [ ] **Verify no secrets in version control**
  ```bash
  git log --all --full-history --source -- .env
  ```

### Database Configuration

- [ ] **Run all migrations**
  ```bash
  python manage.py migrate
  ```

- [ ] **Create superuser account**
  ```bash
  python manage.py createsuperuser
  ```

- [ ] **Test database backup**
  ```bash
  sudo bash manage.sh
  # Select option 8) Backup Data
  ```

- [ ] **Set up automated backups** (cron job)

### Static Files

- [ ] **Collect static files**
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] **Verify Whitenoise configuration** in settings.py

- [ ] **Test static file serving**

### Dependencies

- [ ] **Install production dependencies only**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Verify all packages are up to date**
  ```bash
  pip list --outdated
  ```

- [ ] **Run security audit**
  ```bash
  pip install safety
  safety check
  ```

## Server Configuration

### Web Server (Nginx)

- [ ] **Install Nginx**
  ```bash
  sudo apt install nginx
  ```

- [ ] **Configure reverse proxy** to Gunicorn

- [ ] **Set up SSL/TLS certificate** (Let's Encrypt recommended)
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d yourdomain.com
  ```

- [ ] **Configure security headers** in Nginx
  - X-Frame-Options
  - X-Content-Type-Options
  - Strict-Transport-Security

- [ ] **Test Nginx configuration**
  ```bash
  sudo nginx -t
  ```

### Application Server (Gunicorn)

- [ ] **Configure Gunicorn workers** (2-4 × CPU cores)

- [ ] **Set up systemd service**
  ```bash
  sudo systemctl enable mc-rcon
  sudo systemctl start mc-rcon
  ```

- [ ] **Verify service is running**
  ```bash
  sudo systemctl status mc-rcon
  ```

- [ ] **Test application restart**
  ```bash
  sudo systemctl restart mc-rcon
  ```

### Firewall

- [ ] **Configure firewall rules**
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable
  ```

- [ ] **Verify firewall status**
  ```bash
  sudo ufw status
  ```

## Application Configuration

### Django Settings

- [ ] **Verify production settings** in `irongate/settings.py`
  - DEBUG = False
  - SECURE_SSL_REDIRECT = True
  - SESSION_COOKIE_SECURE = True
  - CSRF_COOKIE_SECURE = True
  - SECURE_HSTS_SECONDS = 31536000

- [ ] **Configure logging** for production

- [ ] **Set up error monitoring** (optional: Sentry)

### RCON Configuration

- [ ] **Add Minecraft servers** in admin panel

- [ ] **Set RCON passwords** using `set_rcon_password.py`

- [ ] **Test RCON connections** to all servers

- [ ] **Verify encryption key** works
  ```bash
  python verify_key.py --test-passwords
  ```

### User Management

- [ ] **Create user groups** for server access

- [ ] **Assign users to groups**

- [ ] **Test user permissions**

- [ ] **Configure display settings** (IP/port visibility)

## Testing

### Functional Testing

- [ ] **Test user registration** (if enabled)

- [ ] **Test user login/logout**

- [ ] **Test server dashboard** displays correctly

- [ ] **Test player list** auto-refresh

- [ ] **Test whitelist addition** via RCON

- [ ] **Test language switching** (EN/ZH)

- [ ] **Test announcement system**

### Security Testing

- [ ] **Test CSRF protection** on forms

- [ ] **Test SQL injection** prevention

- [ ] **Test XSS** prevention

- [ ] **Test authentication** bypass attempts

- [ ] **Test unauthorized access** to admin panel

- [ ] **Verify HTTPS** redirect works

- [ ] **Test session security**

### Performance Testing

- [ ] **Test page load times**

- [ ] **Test concurrent user access**

- [ ] **Test RCON connection pooling**

- [ ] **Monitor memory usage**

- [ ] **Monitor CPU usage**

## Monitoring & Maintenance

### Logging

- [ ] **Configure application logs**
  ```bash
  sudo journalctl -u mc-rcon -f
  ```

- [ ] **Set up log rotation**

- [ ] **Configure error alerting**

### Backups

- [ ] **Test database restore** procedure

- [ ] **Verify automated backups** are running

- [ ] **Test backup to remote location**

- [ ] **Document backup retention policy**

### Updates

- [ ] **Document update procedure**

- [ ] **Test update process** on staging

- [ ] **Schedule regular updates**

- [ ] **Subscribe to security advisories**

## Documentation

- [ ] **Document server configuration**

- [ ] **Document deployment procedure**

- [ ] **Document backup/restore procedure**

- [ ] **Document troubleshooting steps**

- [ ] **Create runbook** for common issues

- [ ] **Document emergency contacts**

## Post-Deployment

### Verification

- [ ] **Access application** via domain

- [ ] **Verify SSL certificate** is valid

- [ ] **Test all major features**

- [ ] **Check error logs** for issues

- [ ] **Monitor performance** for 24 hours

### Cleanup

- [ ] **Remove development files** from server

- [ ] **Remove test data** from database

- [ ] **Clear temporary files**

- [ ] **Verify no debug output** in logs

### Communication

- [ ] **Notify users** of new deployment

- [ ] **Provide user documentation**

- [ ] **Set up support channels**

- [ ] **Create announcement** for launch

## Emergency Procedures

### Rollback Plan

- [ ] **Document rollback procedure**

- [ ] **Keep previous version** available

- [ ] **Test rollback** on staging

- [ ] **Define rollback triggers**

### Incident Response

- [ ] **Define incident severity levels**

- [ ] **Create incident response plan**

- [ ] **Document escalation procedures**

- [ ] **Set up status page** (optional)

---

## Checklist Completion

Date: _______________

Deployed by: _______________

Verified by: _______________

Production URL: _______________

Notes:
_______________________________________________
_______________________________________________
_______________________________________________

---

**Remember:** Security is an ongoing process. Regularly review and update this checklist as your deployment evolves.
