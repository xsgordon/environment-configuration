#!/usr/bin/env python3
"""
Integration test suite for the entire environment configuration system
"""

import os
import tempfile
import subprocess
import pytest
import docker
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).parent.parent


class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_ansible_lint_passes(self):
        """Test that Ansible playbooks pass ansible-lint"""
        if not self._has_ansible_lint():
            pytest.skip("ansible-lint not available")
        
        result = subprocess.run([
            "ansible-lint", 
            str(PROJECT_ROOT / "environment-configuration.yaml")
        ], capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        # ansible-lint returns non-zero for warnings, so we check for actual errors
        if result.returncode != 0 and "error" in result.stdout.lower():
            pytest.fail(f"ansible-lint found errors: {result.stdout}")
    
    def test_yamllint_passes(self):
        """Test that YAML files pass yamllint"""
        if not self._has_yamllint():
            pytest.skip("yamllint not available")
        
        yaml_files = list(PROJECT_ROOT.glob("*.yaml")) + list(PROJECT_ROOT.glob("roles/**/*.yaml"))
        
        for yaml_file in yaml_files:
            result = subprocess.run([
                "yamllint", str(yaml_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                pytest.fail(f"yamllint failed for {yaml_file}: {result.stdout}")
    
    def test_shellcheck_passes(self):
        """Test that shell scripts pass shellcheck"""
        if not self._has_shellcheck():
            pytest.skip("shellcheck not available")
        
        shell_scripts = [PROJECT_ROOT / "install.sh"]
        
        for script in shell_scripts:
            if script.exists():
                result = subprocess.run([
                    "shellcheck", str(script)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    pytest.fail(f"shellcheck failed for {script}: {result.stdout}")
    
    @pytest.mark.slow
    def test_full_playbook_check_mode(self):
        """Test running the full playbook in check mode"""
        if not self._has_ansible():
            pytest.skip("Ansible not available")
        
        # Create a temporary inventory file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[test]\nlocalhost ansible_connection=local\n")
            inventory_file = f.name
        
        try:
            result = subprocess.run([
                "ansible-playbook",
                "-i", inventory_file,
                "--check",
                "--extra-vars", "user=testuser",
                str(PROJECT_ROOT / "environment-configuration.yaml")
            ], capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            # Check mode should succeed without making changes
            if result.returncode != 0:
                pytest.fail(f"Playbook check mode failed: {result.stderr}")
        finally:
            os.unlink(inventory_file)
    
    def test_make_install_dry_run(self):
        """Test make install with dry-run to ensure it would work"""
        result = subprocess.run([
            "make", "--dry-run", "install"
        ], capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode != 0:
            pytest.fail(f"make install dry-run failed: {result.stderr}")
        
        # Should show it would run the install script
        assert "install.sh" in result.stdout, "Make should invoke install.sh"
    
    def test_project_structure_complete(self):
        """Test that project has all expected files and structure"""
        expected_files = [
            "environment-configuration.yaml",
            "install.sh", 
            "Makefile",
            "README.md"
        ]
        
        for file_path in expected_files:
            assert (PROJECT_ROOT / file_path).exists(), f"{file_path} should exist"
        
        expected_dirs = [
            "roles",
            "roles/common",
            "roles/common/tasks", 
            "roles/desktop",
            "roles/desktop/tasks"
        ]
        
        for dir_path in expected_dirs:
            assert (PROJECT_ROOT / dir_path).is_dir(), f"{dir_path} should be a directory"
    
    def test_all_task_files_exist(self):
        """Test that all task files referenced in main.yaml files exist"""
        common_main = PROJECT_ROOT / "roles/common/tasks/main.yaml"
        desktop_main = PROJECT_ROOT / "roles/desktop/tasks/main.yaml"
        
        import yaml
        
        # Check common tasks
        with open(common_main, 'r') as f:
            common_tasks = yaml.safe_load(f)
        
        for task in common_tasks:
            if "import_tasks" in task:
                task_file = PROJECT_ROOT / "roles/common/tasks" / task["import_tasks"]
                assert task_file.exists(), f"Common task file {task['import_tasks']} should exist"
        
        # Check desktop tasks  
        with open(desktop_main, 'r') as f:
            desktop_tasks = yaml.safe_load(f)
        
        for task in desktop_tasks:
            if "import_tasks" in task and not task["import_tasks"].startswith("#"):
                task_file = PROJECT_ROOT / "roles/desktop/tasks" / task["import_tasks"]
                assert task_file.exists(), f"Desktop task file {task['import_tasks']} should exist"
    
    def _has_ansible(self):
        """Check if ansible commands are available"""
        try:
            subprocess.run(["ansible-playbook", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _has_ansible_lint(self):
        """Check if ansible-lint is available"""
        try:
            subprocess.run(["ansible-lint", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _has_yamllint(self):
        """Check if yamllint is available"""
        try:
            subprocess.run(["yamllint", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _has_shellcheck(self):
        """Check if shellcheck is available"""
        try:
            subprocess.run(["shellcheck", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


@pytest.mark.docker
class TestDockerIntegration:
    """Docker-based integration tests (requires Docker)"""
    
    def test_fedora_environment_setup(self):
        """Test environment setup in a Fedora container"""
        if not self._has_docker():
            pytest.skip("Docker not available")
        
        client = docker.from_env()
        
        try:
            # Create a Fedora container
            container = client.containers.run(
                "fedora:latest",
                command="sleep 300",
                detach=True,
                volumes={str(PROJECT_ROOT): {'bind': '/workspace', 'mode': 'ro'}}
            )
            
            # Install prerequisites
            result = container.exec_run([
                "dnf", "install", "-y", 
                "ansible-core", "python3-pip", "git", "which"
            ])
            assert result.exit_code == 0, "Should install prerequisites"
            
            # Test ansible syntax check
            result = container.exec_run([
                "ansible-playbook", "--syntax-check", 
                "/workspace/environment-configuration.yaml"
            ])
            assert result.exit_code == 0, f"Ansible syntax check should pass: {result.output}"
            
        finally:
            try:
                container.stop()
                container.remove()
            except:
                pass  # Container cleanup is best effort
    
    def _has_docker(self):
        """Check if Docker is available"""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except:
            return False


if __name__ == "__main__":
    pytest.main([__file__]) 