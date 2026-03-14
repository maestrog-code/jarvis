#!/usr/bin/env python3
"""
🚀 Jarvis Quick-Start Launcher (Cross-Platform)

This script starts both the Telegram bot and HTTP API bridge
in separate processes/terminals.

Usage:
    python start.py
    # or
    python3 start.py

Works on: Windows, macOS, Linux
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from typing import Optional

# Colors (work in most modern terminals)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    RESET = '\033[0m'

    @staticmethod
    def disable_on_windows():
        if sys.platform == 'win32':
            Colors.GREEN = ''
            Colors.YELLOW = ''
            Colors.BLUE = ''
            Colors.RED = ''
            Colors.RESET = ''


def print_header():
    """Print fancy startup header."""
    Colors.disable_on_windows()
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║{Colors.RESET}          🚀 Jarvis Local Dev Environment             {Colors.BLUE}║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()


def check_python():
    """Verify Python version."""
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 11):
        print(f"{Colors.RED}❌ Python 3.11+ required (found {sys.version}){Colors.RESET}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ Python: {sys.version.split()[0]}{Colors.RESET}")


def setup_env():
    """Check and create .env if needed."""
    env_file = Path('.env')
    env_example = Path('.env.example')

    if not env_file.exists():
        if env_example.exists():
            print(f"{Colors.YELLOW}⚠️  .env file not found!{Colors.RESET}")
            print("Creating .env from template...")
            env_file.write_text(env_example.read_text())
            print(f"{Colors.GREEN}✅ Created .env (please edit with your credentials){Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ .env.example not found!{Colors.RESET}")
            sys.exit(1)
    print()


def setup_venv():
    """Create and activate virtual environment."""
    venv_path = Path('venv')

    if not venv_path.exists():
        print(f"{Colors.YELLOW}📦 Creating virtual environment...{Colors.RESET}")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print(f"{Colors.GREEN}✅ Virtual environment created{Colors.RESET}")

    print(f"{Colors.GREEN}✅ Virtual environment ready{Colors.RESET}")
    print()


def install_deps():
    """Install dependencies."""
    print(f"{Colors.YELLOW}📦 Installing dependencies...{Colors.RESET}")

    if sys.platform == 'win32':
        pip_cmd = Path('venv/Scripts/pip')
    else:
        pip_cmd = Path('venv/bin/pip')

    subprocess.run([str(pip_cmd), 'install', '-q', '-r', 'requirements.txt'], check=True)
    print(f"{Colors.GREEN}✅ Dependencies installed{Colors.RESET}")
    print()


def get_python_executable() -> str:
    """Get the Python executable for the virtual environment."""
    if sys.platform == 'win32':
        return str(Path('venv/Scripts/python.exe'))
    else:
        return str(Path('venv/bin/python'))


def create_logs_dir():
    """Ensure logs directory exists."""
    Path('logs').mkdir(exist_ok=True)


def check_telegram_token():
    """Verify Telegram token is set."""
    env_file = Path('.env')
    if not env_file.exists():
        return

    for line in env_file.read_text().splitlines():
        if line.startswith('TELEGRAM_BOT_TOKEN'):
            token = line.split('=', 1)[1].strip()
            if not token or token == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
                print(f"{Colors.YELLOW}⚠️  WARNING: TELEGRAM_BOT_TOKEN not set!{Colors.RESET}")
                print("Edit .env and add your bot token from @BotFather")
                print()
            return


def print_startup_info():
    """Print startup information."""
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║{Colors.RESET}              🎯 Starting Services                      {Colors.BLUE}║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    print("Starting in 2 seconds... (Press Ctrl+C to cancel)")
    print()
    time.sleep(2)


def start_services():
    """Start Telegram bot and API bridge."""
    python_exe = get_python_executable()
    create_logs_dir()

    # Commands to run
    main_cmd = [python_exe, '-m', 'jarvis.main']
    api_cmd = [python_exe, '-m', 'jarvis.api_bridge']

    print(f"{Colors.YELLOW}Starting: Telegram Bot + Background Tasks...{Colors.RESET}")
    print(f"  Command: {' '.join(main_cmd)}")

    try:
        main_proc = subprocess.Popen(
            main_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        print(f"{Colors.GREEN}✅ Main process (PID {main_proc.pid}){Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start main process: {e}{Colors.RESET}")
        sys.exit(1)

    time.sleep(2)

    print(f"{Colors.YELLOW}Starting: HTTP API Bridge...{Colors.RESET}")
    print(f"  Command: {' '.join(api_cmd)}")

    try:
        api_proc = subprocess.Popen(
            api_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        print(f"{Colors.GREEN}✅ API Bridge process (PID {api_proc.pid}){Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start API process: {e}{Colors.RESET}")
        main_proc.terminate()
        sys.exit(1)

    print()
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║{Colors.RESET}              ✨ All Services Running!                 {Colors.BLUE}║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()

    print("🎯 Endpoints:")
    print(f"   API Health:   {Colors.YELLOW}curl http://localhost:8000/api/health{Colors.RESET}")
    print(f"   Send Command: {Colors.YELLOW}curl -X POST http://localhost:8000/api/command -H 'Content-Type: application/json' -d '{{\"command\": \"/status\"}}'​{Colors.RESET}")
    print()

    print("📋 Logs:")
    print(f"   Main:    {Colors.YELLOW}tail -f logs/main.log{Colors.RESET}")
    print(f"   API:     {Colors.YELLOW}tail -f logs/api_bridge.log{Colors.RESET}")
    print()

    print("🛑 To stop: Press Ctrl+C")
    print()

    # Keep running and handle signals
    def signal_handler(signum, frame):
        print()
        print(f"{Colors.YELLOW}Shutting down...{Colors.RESET}")
        main_proc.terminate()
        api_proc.terminate()

        try:
            main_proc.wait(timeout=5)
            api_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            main_proc.kill()
            api_proc.kill()

        print(f"{Colors.GREEN}✅ Services stopped{Colors.RESET}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Monitor processes
    while True:
        if main_proc.poll() is not None:
            print(f"{Colors.RED}❌ Main process died (exit code: {main_proc.poll()}){Colors.RESET}")
            api_proc.terminate()
            break
        if api_proc.poll() is not None:
            print(f"{Colors.RED}❌ API process died (exit code: {api_proc.poll()}){Colors.RESET}")
            main_proc.terminate()
            break

        time.sleep(1)


def main():
    """Main entry point."""
    try:
        print_header()
        check_python()
        setup_env()
        setup_venv()
        install_deps()
        check_telegram_token()
        print_startup_info()
        start_services()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
