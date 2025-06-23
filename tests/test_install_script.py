#!/usr/bin/env python3
"""
Test suite for the install.sh shell script
"""

import os
import tempfile
import shutil
import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

PROJECT_ROOT = Path(__file__).parent.parent
INSTALL_SCRIPT = PROJECT_ROOT / "install.sh"


class TestInstallScript:
    """Test the install.sh script functionality"""
    
    def test_install_script_exists(self):
        """Test that install.sh exists and is executable"""
        assert INSTALL_SCRIPT.exists(), "install.sh should exist"
        assert os.access(INSTALL_SCRIPT, os.X_OK), "install.sh should be executable"
    
    def test_install_script_syntax(self):
        """Test that install.sh has valid bash syntax"""
        result = subprocess.run([
            "bash", "-n", str(INSTALL_SCRIPT)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            pytest.fail(f"install.sh has syntax errors: {result.stderr}")
    
    def test_script_handles_dotfiles(self):
        """Test that script processes expected dotfiles"""
        with open(INSTALL_SCRIPT, 'r') as f:
            script_content = f.read()
        
        expected_files = ['.vimrc', '.bashrc', '.gitconfig']
        
        for dotfile in expected_files:
            assert dotfile in script_content, f"Script should handle {dotfile}"
    
    def test_script_creates_backups(self):
        """Test that script logic includes backup creation"""
        with open(INSTALL_SCRIPT, 'r') as f:
            script_content = f.read()
        
        # Check that backup logic is present
        assert "DATE=" in script_content, "Script should define DATE variable for backups"
        assert ".bak" in script_content, "Script should create .bak backup files"
        assert "mv" in script_content, "Script should move existing files to backup"
    
    def test_script_creates_symlinks(self):
        """Test that script creates symbolic links"""
        with open(INSTALL_SCRIPT, 'r') as f:
            script_content = f.read()
        
        assert "ln -s" in script_content, "Script should create symbolic links"
        assert "pwd" in script_content, "Script should use current directory for links"
    
    def test_script_handles_vim_directory(self):
        """Test that script has special handling for .vim directory"""
        with open(INSTALL_SCRIPT, 'r') as f:
            script_content = f.read()
        
        assert ".vim" in script_content, "Script should handle .vim directory"
        assert "cp -r" in script_content, "Script should recursively copy .vim content"


class TestInstallScriptIntegration:
    """Integration tests for install.sh in isolated environment"""
    
    def setup_method(self):
        """Set up temporary test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.home_dir = Path(self.test_dir) / "home"
        self.repo_dir = Path(self.test_dir) / "repo"
        
        self.home_dir.mkdir()
        self.repo_dir.mkdir()
        
        # Create test dotfiles in repo
        test_dotfiles = ['.vimrc', '.bashrc', '.gitconfig']
        for dotfile in test_dotfiles:
            (self.repo_dir / dotfile).write_text(f"# Test {dotfile}\n")
        
        # Create test .vim directory
        vim_dir = self.repo_dir / ".vim"
        vim_dir.mkdir()
        (vim_dir / "test_plugin.vim").write_text("\" Test plugin\n")
        
        # Copy install script to repo
        shutil.copy2(INSTALL_SCRIPT, self.repo_dir / "install.sh")
    
    def teardown_method(self):
        """Clean up temporary test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_install_script_with_new_dotfiles(self):
        """Test install script behavior with no existing dotfiles"""
        env = os.environ.copy()
        env['HOME'] = str(self.home_dir)
        
        result = subprocess.run([
            "bash", "install.sh"
        ], cwd=self.repo_dir, env=env, capture_output=True, text=True)
        
        assert result.returncode == 0, f"Install script failed: {result.stderr}"
        
        # Check that symlinks were created
        for dotfile in ['.vimrc', '.bashrc', '.gitconfig']:
            link_path = self.home_dir / dotfile
            assert link_path.is_symlink(), f"{dotfile} should be a symlink"
            # Check that the symlink points to the right place
            actual_target = link_path.readlink()
            expected_target = self.repo_dir / dotfile
            assert str(actual_target) == str(expected_target), f"{dotfile} should link to repo"
    
    def test_install_script_with_existing_files(self):
        """Test install script behavior with existing dotfiles"""
        # Create existing dotfiles
        for dotfile in ['.vimrc', '.bashrc']:
            (self.home_dir / dotfile).write_text(f"# Existing {dotfile}\n")
        
        env = os.environ.copy()
        env['HOME'] = str(self.home_dir)
        
        result = subprocess.run([
            "bash", "install.sh"
        ], cwd=self.repo_dir, env=env, capture_output=True, text=True)
        
        assert result.returncode == 0, f"Install script failed: {result.stderr}"
        
        # Check that backups were created
        backup_files = list(self.home_dir.glob("*.bak"))
        assert len(backup_files) >= 2, "Should create backup files"
        
        # Check that new symlinks were created
        for dotfile in ['.vimrc', '.bashrc', '.gitconfig']:
            link_path = self.home_dir / dotfile
            assert link_path.is_symlink(), f"{dotfile} should be a symlink"
    
    def test_install_script_with_existing_symlinks(self):
        """Test install script behavior with existing symlinks"""
        # Create a temporary file to link to (so the symlinks aren't broken)
        fake_target = self.home_dir / "fake_dotfile"
        fake_target.write_text("fake content")
        
        # Create existing symlinks that point to an actual file
        for dotfile in ['.vimrc', '.bashrc']:
            link_path = self.home_dir / dotfile
            link_path.symlink_to(str(fake_target))
        
        env = os.environ.copy()
        env['HOME'] = str(self.home_dir)
        
        result = subprocess.run([
            "bash", "install.sh"
        ], cwd=self.repo_dir, env=env, capture_output=True, text=True)
        
        assert result.returncode == 0, f"Install script failed: {result.stderr}\nStdout: {result.stdout}"
        
        # Check that new symlinks point to correct location
        # The script should have unlinked old symlinks and created new ones
        for dotfile in ['.vimrc', '.bashrc', '.gitconfig']:
            link_path = self.home_dir / dotfile
            assert link_path.is_symlink(), f"{dotfile} should be a symlink"
            # Use readlink to check the target
            actual_target = link_path.readlink()
            # The target should be an absolute path based on current working dir
            expected_target = str(Path(self.repo_dir) / dotfile)
            # The script uses `pwd` so the link will be to the absolute path
            assert str(actual_target) == expected_target, f"{dotfile} should link to repo, got {actual_target} expected {expected_target}"
    
    def test_install_script_vim_directory_handling(self):
        """Test install script .vim directory handling"""
        # Create existing .vim directory with content
        home_vim_dir = self.home_dir / ".vim"
        home_vim_dir.mkdir()
        (home_vim_dir / "existing_plugin.vim").write_text("\" Existing plugin\n")
        
        env = os.environ.copy()
        env['HOME'] = str(self.home_dir)
        
        result = subprocess.run([
            "bash", "install.sh"
        ], cwd=self.repo_dir, env=env, capture_output=True, text=True)
        
        assert result.returncode == 0, f"Install script failed: {result.stderr}"
        
        # Check that both existing and new content exists
        assert (home_vim_dir / "existing_plugin.vim").exists(), "Should preserve existing .vim content"
        assert (home_vim_dir / "test_plugin.vim").exists(), "Should copy new .vim content"


if __name__ == "__main__":
    pytest.main([__file__]) 