# Contributing to CorpChat Analytics

Thank you for your interest in contributing to CorpChat Analytics! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Install dependencies using the package manager
4. Set up your development environment with the required API keys

## Code Structure

The project follows a modular architecture:

- `app.py` - Main application entry point
- `components/` - Reusable UI components
- `utils/` - Data processing and analysis utilities
- `assets/` - Static files and graphics
- `.streamlit/` - Configuration files

## Coding Standards

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Maintain consistent indentation and formatting

## UI/UX Guidelines

- Maintain the Space Grotesk font family throughout the interface
- Use the established black/white/gray color scheme
- Ensure both light and dark themes are properly supported
- Keep the interface clean and professional
- Test responsive design across different screen sizes

## Testing

- Test all features in both light and dark mode
- Verify data upload functionality with various file formats
- Ensure AI features work properly when API keys are provided
- Check visualization rendering across different data types

## Pull Request Process

1. Create a feature branch from main
2. Make your changes following the coding standards
3. Test your changes thoroughly
4. Update documentation if needed
5. Submit a pull request with a clear description

## Reporting Issues

When reporting bugs or requesting features:

- Use clear, descriptive titles
- Provide steps to reproduce the issue
- Include relevant error messages or screenshots
- Specify your environment (browser, OS, etc.)

## API Integration

- Never include API keys in code or commits
- Use environment variables for sensitive data
- Document any new external service integrations
- Ensure graceful handling when services are unavailable

## Documentation

- Update README.md for significant changes
- Add inline comments for complex logic
- Maintain accurate project structure documentation
- Update configuration examples when needed