#!/usr/bin/env python3
"""
Test suite for the Makefile
"""

import subprocess
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MAKEFILE = PROJECT_ROOT / "Makefile"


class TestMakefile:
    """Test Makefile functionality"""
    
    def test_makefile_exists(self):
        """Test that Makefile exists"""
        assert MAKEFILE.exists(), "Makefile should exist"
    
    def test_makefile_syntax(self):
        """Test Makefile syntax using make --dry-run"""
        result = subprocess.run([
            "make", "--dry-run", "--file", str(MAKEFILE)
        ], capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        # Note: make returns 0 even for dry-run, so we check stderr for syntax errors
        if "error" in result.stderr.lower() or "fatal" in result.stderr.lower():
            pytest.fail(f"Makefile has syntax errors: {result.stderr}")
    
    def test_makefile_default_target(self):
        """Test that default target is defined"""
        with open(MAKEFILE, 'r') as f:
            content = f.read()
        
        # Should have a default target
        assert "default:" in content, "Makefile should have default target"
        assert "install" in content, "Makefile should reference install target"
    
    def test_makefile_install_target(self):
        """Test that install target exists and calls install.sh"""
        with open(MAKEFILE, 'r') as f:
            content = f.read()
        
        assert "install:" in content, "Makefile should have install target"
        assert "install.sh" in content, "Install target should reference install.sh"
    
    def test_make_targets_available(self):
        """Test that expected make targets are available"""
        result = subprocess.run([
            "make", "--print-targets", "--file", str(MAKEFILE)
        ], capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        # Some versions of make don't support --print-targets, so we skip if not available
        if result.returncode != 0 and "unrecognized option" in result.stderr:
            pytest.skip("make --print-targets not supported")
        
        expected_targets = ["default", "install"]
        for target in expected_targets:
            assert target in result.stdout, f"Target {target} should be available"


if __name__ == "__main__":
    pytest.main([__file__]) 