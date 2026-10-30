
import platform
import sys


def detect_platform():
    """Détecte le système d'exploitation et l'architecture."""

    system = platform.system().lower()
    machine = platform.machine().lower()

    architectures = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "i386": "386",
        "i686": "386",
    }

    architecture = architectures.get(machine)

    if system == "linux":
        try:
            os_info = platform.freedesktop_os_release()
            distribution = os_info.get("ID", "unknown")
        except (OSError, AttributeError):
            distribution = "unknown"

    elif system == "windows":
        distribution = "windows"

    elif system == "darwin":
        distribution = "macos"

    else:
        distribution = "unknown"

    return {
        "system": system,
        "distribution": distribution,
        "architecture": architecture,
        "machine": machine,
        "python": sys.version.split()[0],
        "supported": (
            system in ("linux", "windows", "darwin")
            and architecture in ("amd64", "arm64", "386")
        ),
    }


if __name__ == "__main__":
    info = detect_platform()

    print("===== NOXCHAT PLATFORM DETECTION =====")

    for key, value in info.items():
        print(f"{key:<15}: {value}")
