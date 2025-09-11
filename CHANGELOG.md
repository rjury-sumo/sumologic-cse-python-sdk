# CHANGELOG for sumologic-cse-python-sdk
This project adheres to [Semantic Versioning](http://semver.org/). The CHANGELOG follows the format listed at [Keep A Changelog](http://keepachangelog.com/)

## [0.1.0] - 2025-01-12

### 🚀 Major Updates
- **Modernized Python Support**: Updated to Python 3.9+ (dropped Python 3.8 EOL support)
- **UV Package Manager**: Migrated from pip/venv to modern uv for faster dependency management
- **Build System**: Switched from setuptools to hatchling for modern Python packaging

### 📦 Dependency Updates
- **requests**: Updated to >=2.32.0 (latest security fixes)
- **pytest**: Updated to >=8.4.0 (latest testing framework)
- **black**: Updated to >=25.1.0 (latest code formatter)
- **mypy**: Updated to >=1.17.0 (improved type checking)
- **ruff**: Added modern linter replacing flake8 and pre-commit hooks

### 🛠️ Developer Experience
- **Documentation**: Comprehensive README update with uv workflow and modern practices
- **Code Quality**: Full codebase linting with ruff, improved type hints and formatting
- **Testing**: Enhanced pytest configuration with proper integration test markers
- **VS Code**: Updated settings for optimal development experience with uv

### 🔧 Technical Improvements
- **Code Style**: Modernized code formatting and linting rules
- **Type Safety**: Enhanced mypy configuration with strict mode
- **Security**: Updated all dependencies to latest secure versions
- **Performance**: Faster development workflow with uv package management

### 📋 API Compatibility
- **Backward Compatible**: All existing API methods preserved
- **Enhanced**: Improved error handling and documentation
- **Rules API**: Comprehensive rules endpoint support from v0.0.6

## [0.0.6]
Added rules API endpoints: get_rules(), get_rule(), and query_rules() methods.
Added integration tests for rules API endpoints.
Added example script get_rules.py.

## [0.0.5]
Fixed the mess around endpoint. Default, 'prod' or 'us1' all resolve to https://api.sumologic.com/docs/sec.

## [0.0.4]
Fixed a typo where a line of code had been removed accidentally in a prior commit.

## [0.0.3]
Updated dependencies to fix confict so package will build again.