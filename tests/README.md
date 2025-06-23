# Test Suite for Environment Configuration

This directory contains comprehensive tests for the environment-configuration project, which is an Ansible-based system for setting up development environments.

## Test Categories

### 1. Ansible Syntax Tests (`test_ansible_syntax.py`)
- Validates YAML syntax for all Ansible playbooks and task files
- Checks playbook structure and required elements
- Verifies that all referenced roles and task files exist
- Uses `ansible-playbook --syntax-check` when Ansible is available

### 2. Install Script Tests (`test_install_script.py`)
- Tests the `install.sh` shell script functionality
- Validates script syntax using bash parser
- Tests dotfile installation, backup creation, and symlink management
- Includes integration tests in isolated environments

### 3. Makefile Tests (`test_makefile.py`)
- Validates Makefile syntax and structure
- Tests that required targets exist and work correctly
- Verifies make commands execute without errors

### 4. Integration Tests (`test_integration.py`)
- End-to-end testing of the complete system
- Linting with ansible-lint, yamllint, and shellcheck
- Full playbook execution in check mode
- Docker-based testing in clean environments

## Prerequisites

### Required for Basic Tests
```bash
pip install -r tests/requirements.txt
```

### Optional for Extended Testing
```bash
# For Ansible validation
sudo dnf install -y ansible-core ansible-collection-ansible-posix ansible-collection-community-general

# For linting
pip install ansible-lint yamllint
sudo dnf install -y shellcheck

# For Docker tests
sudo dnf install -y docker
sudo systemctl start docker
sudo usermod -a -G docker $USER
```

## Running Tests

### Quick Start
```bash
# Run all fast tests (recommended for development)
python test_runner.py --fast

# Run specific test file
python -m pytest tests/test_ansible_syntax.py -v
```

### Test Runner Options
```bash
# Fast tests only (skip slow integration tests)
python test_runner.py --fast

# Integration tests only
python test_runner.py --integration

# Include Docker-based tests (requires Docker)
python test_runner.py --docker

# All tests with coverage
python test_runner.py --coverage

# Linting only
python test_runner.py --lint

# Verbose output
python test_runner.py --verbose
```

### Direct pytest Usage
```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run only fast tests
python -m pytest tests/ -m "not slow and not docker"

# Run specific test class
python -m pytest tests/test_ansible_syntax.py::TestAnsibleSyntax -v
```

## Test Markers

Tests are marked with the following categories:
- `slow`: Tests that take longer to run (e.g., full playbook execution)
- `docker`: Tests that require Docker to be available
- `integration`: End-to-end integration tests

## Understanding Test Output

### Success
- ✅ All tests passing indicates the configuration is valid
- Green output from pytest indicates individual test success

### Failures
- ❌ Test failures indicate issues that need to be addressed
- Check the detailed output for specific error messages
- Common issues:
  - YAML syntax errors in playbooks
  - Missing task files referenced in main.yaml
  - Shell script syntax errors
  - Missing required Ansible roles

## Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── pytest.ini          # Pytest settings
├── requirements.txt     # Test dependencies
├── README.md           # This file
├── test_ansible_syntax.py    # Ansible validation tests
├── test_install_script.py    # Shell script tests
├── test_makefile.py          # Makefile tests
└── test_integration.py       # Integration tests
```

## Contributing

When adding new functionality to the project:

1. Add corresponding tests to the appropriate test file
2. Run the fast test suite to verify your changes: `python test_runner.py --fast`
3. For significant changes, run the full test suite: `python test_runner.py`
4. Update this README if you add new test categories or requirements

## Troubleshooting

### "ansible-playbook command not found"
- Install Ansible: `sudo dnf install -y ansible-core`
- Or the tests will skip Ansible-specific validation

### "yamllint command not found"
- Install yamllint: `pip install yamllint`
- Or the tests will skip YAML linting

### Docker tests failing
- Ensure Docker is running: `sudo systemctl start docker`
- Add your user to docker group: `sudo usermod -a -G docker $USER`
- Log out and back in for group changes to take effect

### Permission errors
- Ensure test files are executable: `chmod +x test_runner.py`
- Check file permissions in the tests directory 