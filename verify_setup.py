#!/usr/bin/env python
"""
Setup verification script to ensure environment is correctly configured.
Checks dependencies, API keys, and system requirements.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Verify Python version >= 3.8"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Verify required packages are installed"""
    print("\n📦 Checking dependencies...")
    required = {
        "pydantic": "2.0.0",
        "langchain": "0.3.13",
        "langchain_groq": "0.2.1",
        "langchain_core": "0.3.28",
        "dotenv": "1.0.0",
        "pytest": "7.0.0"
    }
    
    missing = []
    for package, min_version in required.items():
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} not found")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages: pip install {' '.join(missing)}")
        return False
    return True


def check_env_file():
    """Verify .env file exists with API key"""
    print("\n🔑 Checking environment configuration...")
    env_path = Path(".env")
    
    if not env_path.exists():
        print("   ❌ .env file not found")
        print("   Create .env file with: GROQ_API_KEY=your_key_here")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
        if "GROQ_API_KEY" not in content:
            print("   ❌ GROQ_API_KEY not found in .env")
            return False
        if "your_key_here" in content or "=" not in content:
            print("   ⚠️  .env exists but API key may not be configured")
            print("   Ensure .env contains: GROQ_API_KEY=your_actual_api_key")
            return False
    
    print("   ✅ .env file configured")
    return True


def check_directory_structure():
    """Verify required directories exist"""
    print("\n📁 Checking directory structure...")
    required_dirs = ["src", "src/agents", "src/models", "output"]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print(f"   ❌ {dir_name}/ not found")
            all_exist = False
        else:
            print(f"   ✅ {dir_name}/")
    
    # Create output and logs directories if missing
    for dir_name in ["output", "logs"]:
        Path(dir_name).mkdir(exist_ok=True)
    
    return all_exist


def check_core_files():
    """Verify core system files exist"""
    print("\n📄 Checking core files...")
    required_files = [
        "main.py",
        "requirements.txt",
        "src/agents/orchestrator_langchain.py",
        "src/agents/base_agent.py",
        "src/models/product.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"   ❌ {file_path}")
            all_exist = False
        else:
            print(f"   ✅ {file_path}")
    
    return all_exist


def main():
    """Run all verification checks"""
    print("="*60)
    print("Kasparro Multi-Agent System - Setup Verification")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("Environment Config", check_env_file()),
        ("Directory Structure", check_directory_structure()),
        ("Core Files", check_core_files())
    ]
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
    
    all_passed = all(result for _, result in checks)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - System ready!")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Run tests: pytest test_system.py test_robustness.py -v")
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues above")
        print("\nSetup instructions:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Create .env file: echo GROQ_API_KEY=your_key > .env")
        print("  3. Get API key: https://console.groq.com/keys")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
