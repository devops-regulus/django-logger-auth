## Contributor Guide

Thank you for your interest in contributing to django-logger-auth!

## Environment Requirements
- Python 3.10+
- Virtual environment (recommended)
- Django 5.0+

## Quick Development Setup
1. Clone the repository and install dependencies:
```bash
python -m venv venv
source venv/bin/activate # Unix
venv\\Scripts\\activate # Windows
pip install -U pip
pip install -r requirements.txt
```
2. Run local migrations and start the example app (optional):
```bash
python manage.py migrate
python manage.py runserver
```
3. Run formatters/linters (if you use them):
```bash
black --check .\django_logger_auth\ .
isort --check-only .\django_logger_auth\ .
flake8 .\django_logger_auth\ --count --select=E9,F63,F7,F82 --show-source --statistics
# Exit-zero treats all errors as warnings
flake8 .\django_logger_auth\ --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics
```

## Commit Style
- Make atomic commits with clear, descriptive messages.
- Follow Semantic Versioning (semver) when updating the version in `pyproject.toml`.

## Changelog
- Update `CHANGELOG.md` for each release following the Keep a Changelog format.

## Релиз и публикация на PyPI
Release and Publishing to PyPI

Publishing is automated via GitHub Actions:

- The workflow runs on pushes to main/master if any of the following change:
  - `pyproject.toml`, `MANIFEST.in`, `CHANGELOG.md`, or files inside `django_logger_auth/`
- It can also be triggered manually (`workflow_dispatch`) or when a GitHub Release is created.

## Discussions and Questions

Open an Issue for bugs, ideas, or suggestions — we appreciate your contributions!

