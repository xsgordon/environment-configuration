#!/usr/bin/env python3
"""
Test runner for environment-configuration project

This script provides an easy way to run different test suites:
- Fast tests (syntax, structure, unit tests)
- Integration tests (including Ansible checks)
- All tests including slow Docker-based tests
"""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"Running {description}...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        print(f"✅ {description} PASSED")
    else:
        print(f"❌ {description} FAILED")
    
    print("-" * 50)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run environment-configuration tests")
    parser.add_argument(
        "--fast", 
        action="store_true", 
        help="Run only fast tests (skip slow integration tests)"
    )
    parser.add_argument(
        "--integration", 
        action="store_true",
        help="Run integration tests only"
    )
    parser.add_argument(
        "--docker", 
        action="store_true",
        help="Include Docker-based tests"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--lint", 
        action="store_true",
        help="Run linting tools only"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    all_passed = True
    
    if args.lint:
        # Run linting tools
        lint_commands = [
            (["flake8", "tests/"], "Python linting (flake8)"),
            (["black", "--check", "tests/"], "Python formatting check (black)"),
        ]
        
        for cmd, desc in lint_commands:
            try:
                if not run_command(cmd, desc):
                    all_passed = False
            except FileNotFoundError:
                print(f"⚠️  Skipping {desc} - tool not installed")
        
        return 0 if all_passed else 1
    
    # Determine which tests to run
    pytest_cmd = ["python", "-m", "pytest"]
    
    if args.coverage:
        pytest_cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.fast:
        pytest_cmd.extend(["-m", "not slow and not docker"])
        test_description = "fast tests"
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
        test_description = "integration tests"
    elif args.docker:
        pytest_cmd.extend(["-m", "docker"])
        test_description = "Docker tests"
    else:
        # Run all tests except Docker tests by default
        pytest_cmd.extend(["-m", "not docker"])
        test_description = "all tests (excluding Docker)"
    
    pytest_cmd.append("tests/")
    
    # Run the tests
    if not run_command(pytest_cmd, test_description):
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 