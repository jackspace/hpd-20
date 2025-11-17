# Contributing to HPD-20 Editor

Thank you for your interest in contributing to the HPD-20 Editor! This document provides guidelines and instructions for setting up your development environment and contributing to the project.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Code Standards](#code-standards)
3. [Testing Guidelines](#testing-guidelines)
4. [Pull Request Process](#pull-request-process)
5. [Issue Reporting](#issue-reporting)

---

## Development Setup

### Prerequisites

- **Python 3.8+** (Python 3.11 recommended)
- **Git** for version control
- **pip** for package management
- **wxPython** (optional, for GUI development)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/hpd-20.git
cd hpd-20
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Optional: Install wxPython for GUI development
pip install wxPython
```

### 4. Verify Installation

```bash
# Run tests to verify setup
pytest

# Check code coverage
pytest --cov=hpd20 --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

---

## Code Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Quotes**: Use double quotes for strings
- **Docstrings**: Google style

### Code Formatting

We use **Black** for automatic code formatting:

```bash
# Format all Python files
black hpd20/

# Check formatting without changing files
black --check hpd20/
```

### Linting

We use **flake8** for linting:

```bash
# Run linter
flake8 hpd20/

# Run with specific configuration
flake8 --max-line-length=100 --extend-ignore=E203,W503 hpd20/
```

### Type Hints

We encourage the use of type hints for new code:

```python
def get_kit_name(kit_index: int) -> str:
    """Get the name of a kit at the specified index.

    Args:
        kit_index: Zero-based index of the kit (0-199)

    Returns:
        The kit name as a string

    Raises:
        IndexError: If kit_index is out of range
    """
    ...
```

### Docstring Format

Use Google-style docstrings:

```python
def apply_scale(instrument_name: str, scale: str, mode: int,
                first_note: int, kit_index: int, pad_list: list) -> None:
    """Apply a musical scale to specified pads in a kit.

    This method generates a musical scale based on the specified parameters
    and applies it to the pads in the given pattern.

    Args:
        instrument_name: Name of the melodic instrument (e.g., "Marimba")
        scale: Scale pattern (e.g., "major", "minor", "pentatonic major")
        mode: Mode number (0-11, where 0=Ionian, 1=Dorian, etc.)
        first_note: MIDI note number for the root note (0-127)
        kit_index: Zero-based kit index (0-199)
        pad_list: List of pad indices to apply the scale to

    Raises:
        ValueError: If instrument_name is not found or parameters are invalid

    Example:
        >>> hpd.apply_scale("Marimba", "major", 0, 60, 0, [0, 1, 2, 3, 4])
    """
    ...
```

---

## Testing Guidelines

### Test-Driven Development (TDD)

We strongly encourage TDD practices:

1. **Write the test first** - Define the expected behavior
2. **Run the test** - It should fail (Red)
3. **Write minimal code** - Make the test pass (Green)
4. **Refactor** - Improve the code while keeping tests green

### Test Organization

```
tests/
├── unit/                 # Unit tests for individual modules
│   ├── test_memoryops.py
│   ├── test_kit.py
│   ├── test_pad.py
│   ├── test_hpd20.py
│   └── test_scales.py
├── integration/          # Integration tests for full workflows
│   ├── test_file_operations.py
│   └── test_scale_application.py
├── fixtures/             # Test data and sample files
└── conftest.py          # Shared fixtures and configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_kit.py

# Run specific test class
pytest tests/unit/test_kit.py::TestKit

# Run specific test method
pytest tests/unit/test_kit.py::TestKit::test_kit_main_name

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=hpd20 --cov-report=term-missing

# Run in parallel (faster)
pytest -n auto

# Run only tests that failed last time
pytest --lf
```

### Writing Tests

#### Unit Test Example

```python
import pytest
from hpd20.kit import Kit

class TestKit:
    """Test suite for Kit class"""

    @pytest.fixture
    def sample_memory(self):
        """Create sample kit memory for testing"""
        memory = bytearray(224)
        # Set up test data
        return memory

    def test_kit_name_returns_string(self, sample_memory):
        """Test that kit name returns a string"""
        kit = Kit(sample_memory)
        name = kit.main_name()
        assert isinstance(name, str)
        assert len(name) == 12
```

#### Integration Test Example

```python
import pytest
from hpd20.hpd20 import hpd

def test_load_save_roundtrip(sample_hs0_file, tmp_path):
    """Test loading and saving preserves data integrity"""
    # Load original file
    hpd_original = hpd(sample_hs0_file)

    # Save to temp location
    temp_file = str(tmp_path / "test.HS0")
    hpd_original.save_file(temp_file)

    # Load saved file
    hpd_loaded = hpd(temp_file)

    # Verify data matches
    assert hpd_loaded.memoryBlock == hpd_original.memoryBlock
```

### Test Coverage Requirements

- **Minimum coverage**: 80% for new code
- **Target coverage**: 90%+ for core modules (hpd20.py, kit.py, pad.py)
- **Coverage report**: Generated automatically in `htmlcov/`

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_it_tests>`

Examples:
- `test_get_kit_name_returns_valid_string()`
- `test_set_pitch_with_negative_value_works_correctly()`
- `test_load_invalid_file_raises_exception()`

---

## Pull Request Process

### Before Submitting

1. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Write tests** for your changes

3. **Run the test suite** and ensure all tests pass:
   ```bash
   pytest
   ```

4. **Check code coverage**:
   ```bash
   pytest --cov=hpd20 --cov-report=term-missing
   ```

5. **Format your code**:
   ```bash
   black hpd20/
   ```

6. **Lint your code**:
   ```bash
   flake8 hpd20/
   ```

7. **Update documentation** if needed

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks

**Examples:**

```
feat(scales): Add support for exotic scales from SCL files

Implemented read_scl() function to parse Scala .scl files
and generate scales from ratio definitions.

Closes #42
```

```
fix(hpd20): Fix MD5 checksum calculation for Python 3

Changed str() to bytes() when calculating MD5 hash to
ensure compatibility with Python 3.

Fixes #38
```

```
test(pad): Add comprehensive tests for Pad class

Added 25 new tests covering all getter/setter methods,
boundary conditions, and error handling.
```

### Pull Request Guidelines

1. **Title**: Clear, descriptive title following commit message format
2. **Description**:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
3. **Checklist**:
   - [ ] Tests added/updated
   - [ ] All tests pass
   - [ ] Code coverage maintained or improved
   - [ ] Documentation updated
   - [ ] Code formatted with Black
   - [ ] No linting errors

### Code Review Process

1. PR will be reviewed by maintainers
2. Address any feedback or requested changes
3. Once approved, PR will be merged

---

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **HPD-20 Editor version**: Run `hpd20-cli --version`
2. **Python version**: Run `python --version`
3. **Operating system**: Windows, macOS, Linux (distribution)
4. **Steps to reproduce**: Clear, step-by-step instructions
5. **Expected behavior**: What should happen
6. **Actual behavior**: What actually happens
7. **Error messages**: Full error output if applicable
8. **Sample files**: If relevant (attach .HS0 or .kit files)

### Feature Requests

When requesting features:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: How you envision the feature working
3. **Alternatives**: Other solutions you've considered
4. **Additional context**: Screenshots, mockups, examples

---

## Development Tips

### Working with .HS0 Files

Sample .HS0 files are included in the repository:
- `BKUP-021.HS0`
- `BKUP-058.HS0`

Use these for testing and development.

### Memory Structure

The HPD-20 memory structure:
```
Offset      Size        Content
0           1180        Unknown/header
1180        1920        15 Chains (128 bytes each)
6922        44800       200 Kits (224 bytes each)
51596       231200      3400 Pads (68 bytes each)
282796      16          MD5 checksum
```

### Debugging

Use Python's built-in debugger:

```python
import pdb; pdb.set_trace()  # Set breakpoint
```

Or use pytest with `--pdb` flag:

```bash
pytest --pdb  # Drop into debugger on failure
```

### Performance Profiling

```bash
# Profile code execution
python -m cProfile -s cumtime hpd20/hpd20.py BKUP-021.HS0 show kits
```

---

## Questions?

If you have questions not covered by this guide:

1. Check existing [Issues](https://github.com/YOUR_REPO/hpd-20/issues)
2. Check [Discussions](https://github.com/YOUR_REPO/hpd-20/discussions)
3. Open a new issue with the `question` label

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to HPD-20 Editor!** 🎵
