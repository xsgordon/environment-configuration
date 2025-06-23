#!/usr/bin/env python3
"""
Pytest configuration and fixtures for environment-configuration tests
"""

import os
import tempfile
import shutil
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def project_root():
    """Fixture that provides the project root directory"""
    return PROJECT_ROOT


@pytest.fixture
def temp_home():
    """Fixture that provides a temporary home directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_repo():
    """Fixture that provides a temporary repository directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_dotfiles(temp_repo):
    """Fixture that creates mock dotfiles in a temporary repository"""
    dotfiles = ['.vimrc', '.bashrc', '.gitconfig']
    
    for dotfile in dotfiles:
        (temp_repo / dotfile).write_text(f"# Mock {dotfile} content\n")
    
    # Create mock .vim directory
    vim_dir = temp_repo / ".vim"
    vim_dir.mkdir()
    (vim_dir / "plugin.vim").write_text("\" Mock vim plugin\n")
    
    return temp_repo


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "docker: marks tests as requiring Docker"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if any(keyword in item.name for keyword in ["full_playbook", "docker", "container"]):
            item.add_marker(pytest.mark.slow)
        
        # Mark docker tests
        if "docker" in item.name.lower() or "container" in item.name.lower():
            item.add_marker(pytest.mark.docker) 