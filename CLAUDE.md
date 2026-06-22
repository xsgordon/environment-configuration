# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an Ansible-based environment configuration system for replicating a standard operating environment across servers and desktops. It manages dotfiles (`.bashrc`, `.vimrc`, `.gitconfig`, `.vim/`), installs packages, and configures system settings.

## Architecture

The project has two installation methods:

1. **Simple dotfile installation** (`install.sh` / `make install`): Symlinks dotfiles from the repo to `$HOME` and copies `.vim/` contents recursively
2. **Full Ansible playbook** (`environment-configuration.yaml`): Installs packages, configures system settings, and deploys dotfiles

### Ansible Structure

The playbook uses a three-role architecture:

- **common**: Applied to all systems (both server and desktop)
  - SELinux Python bindings (version-aware for Fedora <32 vs >=32)
  - System updates, journald configuration, virtualization setup
  - Dotfile installation, screen setup
  - Task inclusion via `import_tasks` in `roles/common/tasks/main.yaml`

- **server**: Server-specific tasks
  - Minimal additional configuration

- **desktop**: Desktop-specific tasks
  - Chrome, VS Code, Docker Machine KVM, OpenRA, PlayOnLinux
  - TLP power management, PackageKit cache disabling, coredump disabling

The playbook applies roles based on `--tags` (server or desktop), with the `common` role included in both.

## Commands

### Testing

```bash
# Fast tests (syntax, structure, unit tests) - recommended for development
python test_runner.py --fast

# All tests except Docker tests
python test_runner.py

# Integration tests only
python test_runner.py --integration

# Include Docker-based tests
python test_runner.py --docker

# Linting only
python test_runner.py --lint

# Run specific test file
python -m pytest tests/test_ansible_syntax.py -v

# Run with coverage
python test_runner.py --coverage
```

Test markers: `slow`, `docker`, `integration`

### Installation

```bash
# Dotfiles only (symlinks dotfiles to $HOME, backs up existing files)
sh install.sh
# or
make install

# Full Ansible playbook for servers
ansible-playbook -i hosts environment-configuration.yaml --tags="server" --extra-vars="user=USERNAME" --ask-become-pass

# Full Ansible playbook for desktops
ansible-playbook -i hosts environment-configuration.yaml --tags="desktop" --extra-vars="user=USERNAME" --ask-become-pass
```

### Prerequisites

```bash
# Required for Ansible playbook
sudo dnf install -y ansible-core ansible-collection-ansible-posix ansible-collection-community-general

# For running tests
pip install -r tests/requirements.txt

# Optional for extended testing (linting)
pip install ansible-lint yamllint
sudo dnf install -y shellcheck
```

## Key Files

- `environment-configuration.yaml`: Main Ansible playbook
- `install.sh`: Standalone dotfile installer (backs up existing files with date suffix, creates symlinks)
- `hosts`: Ansible inventory file
- `test_runner.py`: Test orchestration script with multiple test suite options
- `.bashrc`: Bash configuration with vi mode, colored output aliases, history management
- `.vimrc`: Vim configuration
- `.gitconfig`: Git configuration

## Special Considerations

- `.bashrc` sources a private file (`~/.bashrc.private`) for machine-specific variables not committed to the repo
- The `install.sh` script backs up existing dotfiles with a date suffix (`YYYYMMDD`) before creating symlinks
- `.vim/` directory is copied recursively rather than symlinked to support local user data
- Ansible tasks are version-aware (e.g., different SELinux package names for Fedora <32 vs >=32)
