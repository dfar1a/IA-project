import os
import sys
import subprocess

VENV_DIR = "venv"
REQ_FILE = "requirements.txt"
PYTHON_EXEC = sys.executable


def create_venv():
    print("Creating virtual environment...")
    subprocess.run([PYTHON_EXEC, "-m", "venv", VENV_DIR], check=True)
    install_dependencies()


def install_dependencies():
    if os.path.exists(REQ_FILE):
        print("Installing dependencies...")
        subprocess.run(
            [
                (
                    os.path.join(VENV_DIR, "bin", "python")
                    if os.name != "nt"
                    else os.path.join(VENV_DIR, "Scripts", "python")
                ),
                "-m",
                "pip",
                "install",
                "-r",
                REQ_FILE,
            ],
            check=True,
        )


def run_menu():
    python_bin = (
        os.path.join(VENV_DIR, "bin", "python")
        if os.name != "nt"
        else os.path.join(VENV_DIR, "Scripts", "python")
    )
    subprocess.run([python_bin, "menu.py"], check=True)


if __name__ == "__main__":
    if not os.path.exists(VENV_DIR):
        create_venv()
    run_menu()
