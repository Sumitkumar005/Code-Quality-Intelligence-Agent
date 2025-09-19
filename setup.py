#!/usr/bin/env python3
"""
CQIA Setup Script
Automated setup for Code Quality Intelligence Agent
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_node_version():
    """Check if Node.js is available"""
    success, stdout, stderr = run_command("node --version", check=False)
    if success:
        version = stdout.strip()
        print(f"✅ Node.js {version}")
        return True
    else:
        print("⚠️  Node.js not found - web interface will not be available")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    # Install CLI dependencies
    success, stdout, stderr = run_command(
        "pip install click rich requests pathlib2",
        cwd="backend"
    )
    
    if not success:
        print(f"❌ Failed to install CLI dependencies: {stderr}")
        return False
    
    # Try to install full requirements
    if Path("backend/requirements.txt").exists():
        success, stdout, stderr = run_command(
            "pip install -r requirements.txt",
            cwd="backend",
            check=False
        )
        
        if success:
            print("✅ All Python dependencies installed")
        else:
            print("⚠️  Some advanced dependencies failed - basic functionality available")
    
    return True

def install_node_dependencies():
    """Install Node.js dependencies"""
    if not Path("package.json").exists():
        return True
        
    print("\n📦 Installing Node.js dependencies...")
    success, stdout, stderr = run_command("npm install")
    
    if success:
        print("✅ Node.js dependencies installed")
        return True
    else:
        print(f"❌ Failed to install Node.js dependencies: {stderr}")
        return False

def create_executable():
    """Create executable script"""
    print("\n🔧 Creating executable script...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Create batch file for Windows
        batch_content = '''@echo off
python "%~dp0backend\\cli.py" %*'''
        
        with open("cqia.bat", "w") as f:
            f.write(batch_content)
        print("✅ Created cqia.bat")
        
    else:
        # Create shell script for Unix-like systems
        script_content = '''#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/backend/cli.py" "$@"'''
        
        with open("cqia", "w") as f:
            f.write(script_content)
        
        # Make executable
        os.chmod("cqia", 0o755)
        print("✅ Created cqia executable")
    
    return True

def check_ollama():
    """Check if Ollama is available"""
    print("\n🤖 Checking for Ollama (optional)...")
    success, stdout, stderr = run_command("ollama --version", check=False)
    
    if success:
        print(f"✅ Ollama available: {stdout.strip()}")
        
        # Check if llama3 model is available
        success, stdout, stderr = run_command("ollama list", check=False)
        if "llama3" in stdout:
            print("✅ Llama3 model available")
        else:
            print("💡 To install Llama3 model: ollama pull llama3:8b")
    else:
        print("⚠️  Ollama not found - install from https://ollama.ai for AI features")

def run_test():
    """Run a quick test of the CLI"""
    print("\n🧪 Testing CLI functionality...")
    
    # Create a simple test file
    test_dir = Path("test_code")
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "test.py"
    test_file.write_text('''
def hello_world():
    password = "hardcoded_secret"  # Security issue
    for i in range(1000):
        for j in range(1000):  # Performance issue
            pass
    return "Hello, World!"
''')
    
    # Test the CLI
    system = platform.system().lower()
    command = "cqia.bat" if system == "windows" else "./cqia"
    
    success, stdout, stderr = run_command(
        f"{command} analyze test_code --format json",
        check=False
    )
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
    if success and "Security" in stdout:
        print("✅ CLI test passed - security issues detected correctly")
        return True
    else:
        print("⚠️  CLI test had issues - check installation")
        return False

def main():
    """Main setup function"""
    print("🚀 CQIA Setup - Code Quality Intelligence Agent")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    has_node = check_node_version()
    
    # Install dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    if has_node:
        install_node_dependencies()
    
    # Create executable
    create_executable()
    
    # Check optional components
    check_ollama()
    
    # Run test
    run_test()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n📋 Quick Start:")
    
    system = platform.system().lower()
    if system == "windows":
        print("   cqia.bat analyze <path-to-code>")
        print("   cqia.bat interactive")
    else:
        print("   ./cqia analyze <path-to-code>")
        print("   ./cqia interactive")
    
    if has_node:
        print("\n🌐 Web Interface:")
        print("   npm run dev  (starts web interface)")
        print("   python backend/main.py  (starts API server)")
    
    print("\n📚 Documentation:")
    print("   README.md - Usage guide")
    print("   ARCHITECTURE.md - Technical details")
    
    print("\n💡 Tips:")
    print("   - Install Ollama for AI features: https://ollama.ai")
    print("   - Run 'ollama pull llama3:8b' for best AI experience")
    print("   - Use --help flag for detailed command options")

if __name__ == "__main__":
    main()