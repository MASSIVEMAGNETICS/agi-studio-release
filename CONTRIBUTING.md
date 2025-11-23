# Contributing to AGI Studio

First off, thank you for considering contributing to AGI Studio! It's people like you that make AGI Studio such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- **Be respectful:** Treat everyone with respect
- **Be collaborative:** Work together towards common goals
- **Be inclusive:** Welcome newcomers and diverse perspectives
- **Be professional:** Focus on what is best for the project

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, Node version, etc.)

**Bug Report Template:**

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Python Version: [e.g. 3.10.5]
- Node Version: [e.g. 20.0.0]
- AGI Studio Version: [e.g. 2.0.0]
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case:** Why is this enhancement useful?
- **Possible implementation:** If you have ideas on how to implement
- **Alternatives considered**

### Your First Code Contribution

Unsure where to start? Look for issues labeled:

- `good first issue` - Simple issues for beginners
- `help wanted` - Issues where we need community help
- `documentation` - Documentation improvements

---

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 20+
- Git
- PostgreSQL 15+ (optional, for database features)
- Redis 7+ (optional, for caching)

### Setup Steps

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/agi-studio-release.git
   cd agi-studio-release
   ```

2. **Set up backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   cp .env.example .env
   ```

3. **Set up frontend:**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   ```

4. **Install pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Run tests to verify setup:**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

---

## Pull Request Process

### Before Submitting

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes:**
   - Follow coding standards
   - Add tests
   - Update documentation

3. **Run tests and linting:**
   ```bash
   # Backend
   cd backend
   pytest
   ruff check .
   black .
   mypy .

   # Frontend
   cd frontend
   npm test
   npm run lint
   npx tsc --noEmit
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

5. **Push to your fork:**
   ```bash
   git push origin feature/my-new-feature
   ```

### Submitting the PR

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Choose your fork and branch
4. Fill out the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
```

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged

---

## Coding Standards

### Python (Backend)

**Style:**
- Follow PEP 8
- Use Black for formatting
- Use type hints
- Maximum line length: 100

**Example:**
```python
from typing import Optional, List

def process_data(
    data: List[str],
    max_length: int = 100,
    validate: bool = True
) -> Optional[str]:
    """
    Process input data and return result.
    
    Args:
        data: List of strings to process
        max_length: Maximum allowed length
        validate: Whether to validate input
    
    Returns:
        Processed string or None if invalid
    """
    if validate and not data:
        return None
    
    result = " ".join(data)
    return result[:max_length] if len(result) > max_length else result
```

**Best Practices:**
- Use meaningful variable names
- Keep functions small and focused
- Add docstrings to all public functions
- Handle exceptions appropriately
- Use context managers for resources

### TypeScript/JavaScript (Frontend)

**Style:**
- Follow ESLint configuration
- Use Prettier for formatting
- Use TypeScript strict mode
- Maximum line length: 100

**Example:**
```typescript
interface User {
  id: string
  name: string
  email: string
}

/**
 * Fetch user data from API
 * @param userId - The user's unique identifier
 * @returns Promise resolving to User object
 */
async function fetchUser(userId: string): Promise<User> {
  const response = await fetch(`/api/users/${userId}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.statusText}`)
  }
  
  return response.json()
}
```

**Best Practices:**
- Use functional components with hooks
- Avoid any type unless absolutely necessary
- Keep components small and reusable
- Use meaningful prop names
- Handle loading and error states

---

## Testing Guidelines

### Test Coverage Requirements

- **Backend:** Minimum 80% coverage
- **Frontend:** Minimum 70% coverage
- **New features:** Must include tests

### Writing Tests

**Backend (pytest):**
```python
import pytest
from mymodule import MyClass

class TestMyClass:
    @pytest.fixture
    def instance(self):
        return MyClass()
    
    def test_basic_functionality(self, instance):
        result = instance.process("test")
        assert result == "expected"
    
    def test_error_handling(self, instance):
        with pytest.raises(ValueError):
            instance.process(None)
```

**Frontend (Vitest + React Testing Library):**
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MyComponent from './MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent title="Test" />)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
  
  it('handles click events', () => {
    const onClick = vi.fn()
    render(<MyComponent onClick={onClick} />)
    
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalled()
  })
})
```

---

## Documentation

### Code Documentation

- Add docstrings/JSDoc to all public functions
- Include type information
- Describe parameters and return values
- Add usage examples for complex functions

### README Updates

When adding features:
- Update relevant documentation files
- Add usage examples
- Update API documentation if applicable

### Changelog

Update `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [Unreleased]

### Added
- New feature X that does Y

### Changed
- Modified feature Z to improve performance

### Fixed
- Bug in component A that caused B
```

---

## Questions?

Feel free to:
- Open a GitHub issue
- Start a discussion
- Reach out to maintainers

Thank you for contributing to AGI Studio! 🚀
