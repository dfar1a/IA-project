import os
import sys
import subprocess
import hashlib

VENV_DIR = "venv"
REQ_FILE = "requirements.txt"
REQ_HASH_FILE = ".req_hash"
PYTHON_EXEC = sys.executable


def get_file_hash(filename):
    """Returns a SHA256 hash of a file, ignoring line endings and extra spaces."""
    if not os.path.exists(filename):
        return None
    hasher = hashlib.sha256()
    with open(filename, "rb") as f:
        # Normalize line endings and remove extra spaces
        normalized_content = (
            b"\n".join(line.strip() for line in f.read().splitlines()) + b"\n"
        )
        hasher.update(normalized_content)
    return hasher.hexdigest()


def create_venv():
    """Creates a virtual environment and installs dependencies."""
    print("Creating virtual environment...")
    subprocess.run([PYTHON_EXEC, "-m", "venv", VENV_DIR], check=True)
    install_dependencies(force=True)


def get_installed_packages():
    """Returns a set of currently installed packages in the virtual environment."""
    pip_exec = (
        os.path.join(VENV_DIR, "bin", "pip")
        if os.name != "nt"
        else os.path.join(VENV_DIR, "Scripts", "pip")
    )
    result = subprocess.run(
        [pip_exec, "freeze"], capture_output=True, text=True, check=True
    )
    return {line.split("==")[0] for line in result.stdout.splitlines()}


def get_required_packages():
    """Returns a set of packages listed in requirements.txt."""
    if not os.path.exists(REQ_FILE):
        return set()
    with open(REQ_FILE, "r") as f:
        return {
            line.strip().split("==")[0]
            for line in f
            if line.strip() and not line.startswith("#")
        }


def install_dependencies(force=False):
    """Installs and removes dependencies as needed."""
    if not os.path.exists(REQ_FILE):
        print("No requirements.txt found, skipping dependency installation.")
        return

    current_hash = get_file_hash(REQ_FILE)
    previous_hash = None

    mode = "x"

    if os.path.exists(REQ_HASH_FILE):
        with open(REQ_HASH_FILE, "r") as f:
            mode = "w"
            previous_hash = f.read().strip()

    if force or current_hash != previous_hash:
        print("Updating dependencies...")

        pip_exec = (
            os.path.join(VENV_DIR, "bin", "pip")
            if os.name != "nt"
            else os.path.join(VENV_DIR, "Scripts", "pip")
        )

        # Get installed and required packages
        installed_packages = get_installed_packages()
        required_packages = get_required_packages()

        # Uninstall packages that are no longer required
        packages_to_remove = installed_packages - required_packages
        if packages_to_remove:
            print(f"Removing unused dependencies: {', '.join(packages_to_remove)}")
            subprocess.run(
                [pip_exec, "uninstall", "-y"] + list(packages_to_remove), check=True
            )

        # Install missing and updated dependencies
        subprocess.run([pip_exec, "install", "-r", REQ_FILE], check=True)

        # Save new hash
        with open(REQ_HASH_FILE, mode) as f:
            f.write(current_hash)
    else:
        print("Dependencies are up to date.")


def run_menu():
    """Runs menu.py inside the virtual environment."""
    python_bin = (
        os.path.join(VENV_DIR, "bin", "python")
        if os.name != "nt"
        else os.path.join(VENV_DIR, "Scripts", "python")
    )
    subprocess.run([python_bin, "menu.py"], check=True)


if __name__ == "__main__":
    if not os.path.exists(VENV_DIR):
        create_venv()
    else:
        install_dependencies()

    run_menu()
