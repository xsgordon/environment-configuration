#!/usr/bin/env python3
"""
Test suite for validating Ansible playbook and task syntax
"""

import os
import yaml
import pytest
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ROLES_DIR = PROJECT_ROOT / "roles"
PLAYBOOK_FILE = PROJECT_ROOT / "environment-configuration.yaml"


class TestAnsibleSyntax:
    """Test Ansible syntax validation"""
    
    def test_main_playbook_syntax(self):
        """Test main playbook YAML syntax is valid"""
        with open(PLAYBOOK_FILE, 'r') as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in main playbook: {e}")
    
    def test_main_playbook_structure(self):
        """Test main playbook has required structure"""
        with open(PLAYBOOK_FILE, 'r') as f:
            playbook = yaml.safe_load(f)
        
        assert isinstance(playbook, list), "Playbook should be a list of plays"
        assert len(playbook) > 0, "Playbook should have at least one play"
        
        play = playbook[0]
        assert "hosts" in play, "Play should have hosts defined"
        assert "roles" in play, "Play should have roles defined"
        assert "remote_user" in play, "Play should have remote_user defined"
    
    def test_role_task_files_syntax(self):
        """Test all role task files have valid YAML syntax"""
        task_files = []
        for role_dir in ROLES_DIR.iterdir():
            if role_dir.is_dir():
                tasks_dir = role_dir / "tasks"
                if tasks_dir.exists():
                    for task_file in tasks_dir.glob("*.yaml"):
                        task_files.append(task_file)
        
        assert len(task_files) > 0, "Should find task files to test"
        
        for task_file in task_files:
            with open(task_file, 'r') as f:
                try:
                    content = yaml.safe_load(f)
                    assert content is not None, f"Task file {task_file} should not be empty"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML syntax in {task_file}: {e}")
    
    def test_ansible_playbook_check(self):
        """Test playbook syntax using ansible-playbook --syntax-check"""
        if not self._has_ansible():
            pytest.skip("Ansible not available")
        
        result = subprocess.run([
            "ansible-playbook", 
            "--syntax-check", 
            str(PLAYBOOK_FILE)
        ], capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode != 0:
            pytest.fail(f"Ansible syntax check failed: {result.stderr}")
    
    def test_required_roles_exist(self):
        """Test that all roles referenced in playbook exist"""
        with open(PLAYBOOK_FILE, 'r') as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        roles = play.get("roles", [])
        
        for role_def in roles:
            if isinstance(role_def, dict):
                role_name = role_def.get("role")
            else:
                role_name = role_def
            
            role_dir = ROLES_DIR / role_name
            assert role_dir.exists(), f"Role directory {role_name} should exist"
            
            tasks_dir = role_dir / "tasks"
            assert tasks_dir.exists(), f"Role {role_name} should have tasks directory"
            
            main_task = tasks_dir / "main.yaml"
            assert main_task.exists(), f"Role {role_name} should have main.yaml task file"
    
    def _has_ansible(self):
        """Check if ansible-playbook command is available"""
        try:
            subprocess.run(["ansible-playbook", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


class TestTaskStructure:
    """Test individual task file structure and content"""
    
    def test_common_tasks_structure(self):
        """Test common role main.yaml imports expected tasks"""
        main_task = ROLES_DIR / "common" / "tasks" / "main.yaml"
        with open(main_task, 'r') as f:
            tasks = yaml.safe_load(f)
        
        expected_imports = [
            "update.yaml",
            "common-install.yaml", 
            "journald-size.yaml",
            "nested-virt-intel.yaml",
            "virt-install.yaml",
            "dotfile-install.yaml",
            "screen.yaml"
        ]
        
        import_tasks = [task.get("import_tasks") for task in tasks if "import_tasks" in task]
        
        for expected in expected_imports:
            assert expected in import_tasks, f"Should import {expected}"
    
    def test_desktop_tasks_structure(self):
        """Test desktop role main.yaml imports expected tasks"""
        main_task = ROLES_DIR / "desktop" / "tasks" / "main.yaml"
        with open(main_task, 'r') as f:
            tasks = yaml.safe_load(f)
        
        expected_imports = [
            "coredump-disable.yaml",
            "chrome-install.yaml",
            "desktop-pkgs-install.yaml",
            "playonlinux-install.yaml",
            "sshfs-install.yaml",
            "vscode.yaml",
            "packagekit-cache-disable.yaml",
            "tlp-install.yaml"
        ]
        
        import_tasks = [task.get("import_tasks") for task in tasks 
                       if "import_tasks" in task and not task.get("import_tasks", "").startswith("#")]
        
        for expected in expected_imports:
            assert expected in import_tasks, f"Should import {expected}"
    
    def test_package_tasks_have_names(self):
        """Test that package installation tasks have descriptive names"""
        desktop_pkg_file = ROLES_DIR / "desktop" / "tasks" / "desktop-pkgs-install.yaml"
        with open(desktop_pkg_file, 'r') as f:
            tasks = yaml.safe_load(f)
        
        for task in tasks:
            if "package" in task:
                assert "name" in task, "Package tasks should have descriptive names"
                assert task["name"], "Task name should not be empty"
                assert "become" in task, "Package tasks should have become: true"
                assert task["become"] is True, "Package tasks should use privilege escalation"


if __name__ == "__main__":
    pytest.main([__file__]) 