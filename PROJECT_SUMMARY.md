# MC RCON Manager - Project Summary

## 📊 Project Overview

**MC RCON Manager** is a modern, secure web portal for managing Minecraft servers via the RCON protocol. Built with Django 5.0 and featuring a beautiful Tailwind CSS interface, it provides group-based access control and real-time server monitoring.

**Creator**: MoYuK1ng  
**License**: MIT  
**Version**: 2.3.0  
**Status**: Production Ready ✅

## 🎯 Project Goals

1. **Security First**: Encrypted credentials, input validation, and secure authentication
2. **User-Friendly**: Modern, intuitive interface inspired by industry leaders
3. **Scalable**: Support for multiple servers and user groups
4. **Well-Tested**: Comprehensive test suite with 70+ tests
5. **Open Source**: MIT licensed, welcoming contributions

## 📈 Project Statistics

### Code Metrics
- **Total Lines of Code**: ~5,000+
- **Test Coverage**: 70+ tests (100% passing)
- **Languages**: Python (Django), HTML, CSS (Tailwind), JavaScript (HTMX)
- **Files**: ~50+ source files

### Features
- ✅ Multi-server management
- ✅ Real-time player monitoring
- ✅ Whitelist management
- ✅ Group-based permissions
- ✅ Encrypted credentials
- ✅ Internationalization (EN/ZH)
- ✅ Responsive design
- ✅ Property-based testing

## 🏗️ Architecture

### Backend
- **Framework**: Django 5.0
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **RCON Client**: mcrcon
- **Encryption**: Fernet (cryptography)
- **Testing**: pytest + Hypothesis

### Frontend
- **CSS Framework**: Tailwind CSS
- **Icons**: Lucide Icons
- **Dynamic Updates**: HTMX
- **Design**: Inspired by Vercel, Linear, Stripe

### Deployment
- **WSGI Server**: Gunicorn
- **Reverse Proxy**: Nginx (optional)
- **Process Manager**: systemd
- **Installation**: One-click script

## 📁 Project Structure

```
MC_rcon_manage/
├── .github/                 # GitHub templates and workflows
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── irongate/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── servers/                # Main Django app
│   ├── models.py          # Server, WhitelistRequest models
│   ├── views.py           # Dashboard, player list views
│   ├── admin.py           # Custom admin interface
│   ├── context_processors.py  # Version display
│   ├── services/          # RCON handler
│   ├── utils/             # Encryption utilities
│   ├── templates/         # HTML templates
│   └── tests/             # Test suite (70+ tests)
├── locale/                # Translations (EN/ZH)
├── .env.example           # Environment template
├── manage.sh              # Management script
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── CONTRIBUTING.md        # Contribution guidelines
├── CODE_OF_CONDUCT.md     # Code of conduct
├── SECURITY.md            # Security policy
├── LICENSE                # MIT License
├── CHANGELOG.md           # Version history
└── AUTHORS.md             # Contributors list
```

## 🔒 Security Features

1. **Authentication**
   - Django's built-in auth system
   - Session management
   - CSRF protection

2. **Encryption**
   - Fernet symmetric encryption for RCON passwords
   - Secure key storage in .env
   - Never store plaintext passwords

3. **Input Validation**
   - Regex validation for usernames
   - Django form validation
   - SQL injection protection (ORM)
   - Command injection prevention

4. **Production Security**
   - HTTPS enforcement
   - Secure cookies
   - Security headers
   - Debug mode disabled

## 🧪 Testing Strategy

### Test Types
1. **Unit Tests** (58 tests)
   - Model tests
   - View tests
   - Service tests

2. **Property-Based Tests** (12 tests)
   - Encryption round-trip
   - Username validation
   - Access control
   - RCON parsing
   - Version context processor
   - Group filtering

3. **Integration Tests**
   - End-to-end workflows
   - HTMX interactions

### Test Coverage
- Models: 100%
- Views: 95%
- Services: 90%
- Utilities: 100%

## 📚 Documentation

### User Documentation
- **README.md**: Quick start and features
- **FAQ.md**: Common questions
- **UI_REDESIGN.md**: UI design system

### Developer Documentation
- **CONTRIBUTING.md**: How to contribute
- **CODE_OF_CONDUCT.md**: Community guidelines
- **SECURITY.md**: Security policy
- **CHANGELOG.md**: Version history

### Deployment Documentation
- **manage.sh**: One-click installation
- **.env.example**: Configuration template
- **requirements.txt**: Dependencies

## 🌍 Internationalization

- **Supported Languages**: English, Simplified Chinese
- **Translation System**: Django i18n
- **Coverage**: 100% of UI strings
- **Easy to Extend**: See locale/README.md

## 🚀 Deployment Options

### Development
```bash
python manage.py runserver
```

### Production (Manual)
```bash
gunicorn irongate.wsgi:application
```

### Production (One-Click)
```bash
sudo bash manage.sh
# Select: 1) Fresh Install
```

## 📊 Version History

- **v2.3.0** (2024-11-28): UI redesign with Tailwind CSS
- **v2.2.0** (2024-11-28): CSRF fixes and improvements
- **v2.1.0** (2024-11-27): Script auto-update feature
- **v2.0.0** (2024-11-26): Unified management script

## 🎯 Future Roadmap

### Planned Features
- [ ] Dark mode support
- [ ] More RCON commands (kick, ban, etc.)
- [ ] Server performance metrics
- [ ] Backup/restore functionality
- [ ] Multi-language support (more languages)
- [ ] API endpoints for automation
- [ ] Docker deployment option
- [ ] Real-time WebSocket updates

### Improvements
- [ ] Enhanced error handling
- [ ] More comprehensive logging
- [ ] Performance optimizations
- [ ] Additional property-based tests
- [ ] CI/CD pipeline

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🌍 Add translations
- 💻 Submit code
- ⭐ Star the project

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MoYuK1ng/MC_rcon_manage/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MoYuK1ng/MC_rcon_manage/discussions)
- **Security**: See [SECURITY.md](SECURITY.md)

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2024-2025 MoYuK1ng

## 🙏 Acknowledgments

- Django Community
- Tailwind CSS Team
- HTMX Team
- Hypothesis Team
- All Contributors

---

**Made with ❤️ by MoYuK1ng**

*Last Updated: 2024-11-28*
*Project Started: 2024*
