from loguru import logger
import os
import shutil
import subprocess
import sys
import webbrowser
from typing import Optional

from .host import get_ollama_host, is_local_ollama_host


def show_installation_message(system_name: str) -> None:
    """Present a final installation message, using a GUI prompt on Windows."""
    import tkinter as tk
    import tkinter.messagebox as messagebox

    message = (
        f"Ollama installation initiated for {system_name.title()}.\n\n"
        "After installation completes:\n"
        "1. Restart this program\n"
        "2. The first scan will download the AI model automatically\n\n"
        "Visit https://ollama.com/ for troubleshooting."
    )

    if system_name == "windows":
        temp_root = None
        try:
            temp_root = tk.Tk()
            temp_root.withdraw()
            messagebox.showinfo("Ollama Installation", message, parent=temp_root)
        except Exception as exc:
            logger.debug(f"Unable to show Windows message box: {exc}")
            logger.info(message)
        else:
            logger.info(message)
        finally:
            if temp_root is not None:
                temp_root.destroy()
    else:
        logger.info(message)


def _install_ollama_windows() -> None:
    logger.info("=== Windows Installation Options ===")
    logger.info("1. Automatic download and install (Recommended)")
    logger.info("2. Manual download from website")
    logger.info("")

    download_url = "https://ollama.com/download/OllamaSetup.exe"
    logger.info("Opening the Ollama download link in your default browser...")
    logger.info(f"Download URL: {download_url}")
    try:
        opened = webbrowser.open(download_url)
        if opened:
            logger.info(
                "Browser opened successfully. Follow the prompts to install Ollama."
            )
        else:
            logger.warning(
                "The browser did not report success. Please open the link manually if nothing happens."
            )
    except Exception as e:
        logger.error(f"Unable to open browser automatically: {e}")
        logger.info("Please open the link manually to download Ollama.")


def _detect_linux_distro() -> tuple:
    try:
        with open("/etc/os-release", "r") as f:
            os_release = f.read().lower()

        if "debian" in os_release or "ubuntu" in os_release or "mint" in os_release:
            return "Debian/Ubuntu/Mint", "curl -fsSL https://ollama.com/install.sh | sh"
        elif "arch" in os_release or "manjaro" in os_release:
            return "Arch/Manjaro", "sudo pacman -S ollama"
        elif "fedora" in os_release or "rhel" in os_release or "centos" in os_release:
            return (
                "RedHat/Fedora/CentOS",
                "curl -fsSL https://ollama.com/install.sh | sh",
            )
        elif "gentoo" in os_release or "funtoo" in os_release:
            return "Gentoo/Funtoo", "sudo emerge --ask ollama"
        elif "suse" in os_release or "opensuse" in os_release:
            return "SUSE/openSUSE", "sudo zypper install ollama"
    except Exception:
        pass
    return "Unknown Linux", "curl -fsSL https://ollama.com/install.sh | sh"


def _run_linux_install_command(package_cmd: str) -> None:
    logger.info(f"Running: {package_cmd}")
    logger.info("Please enter your password if prompted...")
    try:
        result = subprocess.run(package_cmd, shell=True, check=False)
        if result.returncode == 0:
            logger.info("Ollama installation completed!")
            logger.info("Please restart this program to continue.")
        else:
            logger.warning("Installation failed or was cancelled.")
            logger.info("You can try installing manually from https://ollama.com/")
    except Exception as e:
        logger.error(f"Error running installation command: {e}")
        logger.info("Please visit https://ollama.com/ for manual installation.")


def _install_ollama_linux() -> None:
    logger.info("=== Linux Installation Options ===")
    distro_info, package_cmd = _detect_linux_distro()

    logger.info(f"Detected: {distro_info}")
    logger.info(f"Recommended command: {package_cmd}")
    logger.info("")
    logger.info("1. Run the recommended installation command")
    logger.info("2. Manual installation from website")
    logger.info("")

    choice = (
        input("Would you like to run the installation command? (y/n): ").lower().strip()
    )
    if choice in ["y", "yes", "1", ""]:
        _run_linux_install_command(package_cmd)
    else:
        logger.info("Opening Ollama website for manual installation...")
        webbrowser.open("https://ollama.com/")


def _install_ollama_unsupported() -> None:
    logger.info("=== Unsupported Operating System ===")
    logger.info("This tool currently supports Windows and Linux only.")
    logger.info("Please install Ollama manually from: https://ollama.com/")
    webbrowser.open("https://ollama.com/")


def _log_existing_ollama_version() -> None:
    try:
        version = subprocess.check_output(["ollama", "--version"], text=True).strip()
        logger.info(f"Ollama found: {version}")
    except Exception as e:
        logger.error(f"Error checking Ollama: {e}")
        sys.exit("Please install Ollama and rerun this program.")


def ensure_ollama_installed() -> None:
    """Check whether Ollama is installed locally when required."""
    host = get_ollama_host()
    if not is_local_ollama_host(host):
        logger.info(
            f"Using remote Ollama host at {host}; skipping local installation check."
        )
        return

    if shutil.which("ollama"):
        _log_existing_ollama_version()
        return

    import platform

    system = platform.system().lower()

    logger.info("Ollama not found on your system.")
    logger.info("Ollama is required for AI-powered code recognition.")
    logger.info("")

    installers = {
        "windows": _install_ollama_windows,
        "linux": _install_ollama_linux,
    }
    installers.get(system, _install_ollama_unsupported)()

    show_installation_message(system)
    input("\nPress ENTER after installing Ollama to close this program...")
    sys.exit(0)
