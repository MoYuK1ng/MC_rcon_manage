# Contributing to MC RCON Manager

First off, thank you for considering contributing to MC RCON Manager! It's people like you that make this project better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## 📜 Code of Conduct

This project and everyone participating in it is governed by respect and professionalism. By participating, you are expected to uphold this standard.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Include your environment details** (OS, Python version, Django version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any alternative solutions you've considered**

### Pull Requests

- Fill in the required template
- Follow the coding standards
- Include appropriate test coverage
- Update documentation as needed
- End all files with a newline

## 🛠️ Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/MC_rcon_manage.git
cd MC_rcon_manage
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up the database**

```bash
python generate_key.py
python manage.py migrate
python manage.py createsuperuser
```

5. **Run tests**

```bash
pytest servers/tests/
```

6. **Start development server**

```bash
python manage.py runserver
```

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules

### Django Best Practices

- Use Django's built-in features when possible
- Follow Django's naming conventions
- Use class-based views for complex logic
- Keep views thin, models fat
- Use Django's ORM instead of raw SQL

### Frontend Standards

- Use Tailwind CSS utility classes
- Follow responsive design principles
- Ensure accessibility (ARIA labels, semantic HTML)
- Test on multiple browsers
- Use Lucide icons for consistency

### Example Code Style

```python
def add_whitelist(self, username: str) -> dict:
    """
    Add a player to the server's whitelist via RCON.
    
    Args:
        username: Minecraft username to whitelist
        
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        # Implementation
        pass
    except Exception as e:
        return {'success': False, 'message': str(e)}
```

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the AAA pattern (Arrange, Act, Assert)

### Test Types

1. **Unit Tests** - Test individual functions/methods
2. **Integration Tests** - Test component interactions
3. **Property-Based Tests** - Test with generated inputs (Hypothesis)

### Running Tests

```bash
# All tests
pytest servers/tests/

# Specific test file
pytest servers/tests/test_models.py

# With coverage
pytest --cov=servers servers/tests/

# Property-based tests only
pytest servers/tests/test_properties.py -v
```

### Test Example

```python
import pytest
from django.contrib.auth.models import User
from servers.models import Server

@pytest.mark.django_db
class TestServerModel:
    def test_server_password_encryption(self):
        """Test that RCON passwords are encrypted"""
        server = Server(name="Test", ip_address="127.0.0.1", rcon_port=25575)
        server.set_password("test_password")
        
        assert server.rcon_password_encrypted != b"test_password"
        assert server.get_password() == "test_password"
```

## 💬 Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(dashboard): add real-time player count updates

Implement HTMX polling for player counts that updates every 30 seconds
without requiring page refresh.

Closes #123
```

```
fix(auth): resolve login redirect loop

Fixed issue where users were stuck in redirect loop after login
when accessing protected pages.

Fixes #456
```

## 🔄 Pull Request Process

1. **Create a feature branch**

```bash
git checkout -b feature/amazing-feature
```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Commit your changes**

```bash
git add .
git commit -m "feat: add amazing feature"
```

4. **Push to your fork**

```bash
git push origin feature/amazing-feature
```

5. **Open a Pull Request**
   - Use a clear title and description
   - Reference any related issues
   - Ensure all tests pass
   - Wait for review

### PR Checklist

- [ ] Code follows the style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No merge conflicts

## 🌍 Translation Contributions

We welcome translations! See [locale/README.md](locale/README.md) for details on adding or updating translations.

## 📚 Documentation

- Keep README.md up to date
- Update docstrings for code changes
- Add comments for complex logic
- Update CHANGELOG.md for notable changes

## ❓ Questions?

Feel free to:
- Open an issue for questions
- Start a discussion on GitHub Discussions
- Contact the maintainer: MoYuK1ng

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Happy Coding! 🚀**
