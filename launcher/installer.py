
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen


GITHUB_API = (
    "https://api.github.com/repos/"
    "cloudflare/cloudflared/releases/latest"
)

INSTALL_DIR = Path.home() / ".noxchat" / "bin"


def get_asset_name(system, architecture):
    """Détermine le fichier Cloudflare compatible."""

    assets = {
        ("linux", "amd64"): "cloudflared-linux-amd64",
        ("linux", "arm64"): "cloudflared-linux-arm64",
        ("linux", "386"): "cloudflared-linux-386",
        ("windows", "amd64"): "cloudflared-windows-amd64.exe",
        ("windows", "386"): "cloudflared-windows-386.exe",
        ("darwin", "amd64"): "cloudflared-darwin-amd64.tgz",
        ("darwin", "arm64"): "cloudflared-darwin-arm64.tgz",
    }

    return assets.get((system, architecture))


def download_file(url, destination):
    """Télécharge un fichier depuis une URL HTTPS."""

    request = Request(
        url,
        headers={"User-Agent": "NOXCHAT-Installer"},
    )

    digest = hashlib.sha256()

    with urlopen(request, timeout=60) as response:
        with open(destination, "wb") as output:
            while True:
                chunk = response.read(1024 * 1024)

                if not chunk:
                    break

                output.write(chunk)
                digest.update(chunk)

    return digest.hexdigest()


def extract_macos_binary(archive_path):
    """Extrait uniquement le binaire cloudflared."""

    with tarfile.open(archive_path, "r:gz") as archive:
        members = [
            member for member in archive.getmembers()
            if Path(member.name).name == "cloudflared"
            and member.isfile()
        ]

        if len(members) != 1:
            raise RuntimeError(
                "Archive macOS invalide : binaire introuvable."
            )

        source = archive.extractfile(members[0])

        if source is None:
            raise RuntimeError(
                "Impossible de lire le binaire macOS."
            )

        return source.read()


def install_cloudflared(platform_info):
    """Détecte, télécharge et vérifie cloudflared."""

    system = platform_info["system"]
    architecture = platform_info["architecture"]

    # Vérifier une installation système existante.
    system_binary = shutil.which("cloudflared")

    if system_binary:
        print(f"[NOXCHAT] Cloudflare détecté : {system_binary}")
        return system_binary

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    binary_name = (
        "cloudflared.exe"
        if system == "windows"
        else "cloudflared"
    )

    local_binary = INSTALL_DIR / binary_name

    if local_binary.is_file():
        print("[NOXCHAT] Installation locale détectée.")
        return str(local_binary)

    asset_name = get_asset_name(system, architecture)

    if not asset_name:
        raise RuntimeError(
            f"Plateforme non prise en charge : "
            f"{system}/{architecture}"
        )

    print("[NOXCHAT] Recherche de la dernière version...")

    request = Request(
        GITHUB_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "NOXCHAT-Installer",
        },
    )

    with urlopen(request, timeout=30) as response:
        release = json.loads(response.read().decode("utf-8"))

    version = release.get("tag_name")

    asset = next(
        (
            item for item in release.get("assets", [])
            if item.get("name") == asset_name
        ),
        None,
    )

    if not version or not asset:
        raise RuntimeError(
            "Version ou fichier compatible introuvable."
        )

    expected_digest = asset.get("digest", "")

    if not expected_digest.startswith("sha256:"):
        raise RuntimeError(
            "Empreinte SHA-256 officielle indisponible. "
            "Installation annulée."
        )

    expected_digest = expected_digest.split(":", 1)[1]

    print(f"[NOXCHAT] Version trouvée : {version}")
    print(f"[NOXCHAT] Téléchargement : {asset_name}")

    download_url = asset.get("browser_download_url")

    if not download_url:
        raise RuntimeError("URL de téléchargement absente.")

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            dir=INSTALL_DIR,
            delete=False,
        ) as temporary:
            temp_path = Path(temporary.name)

        actual_digest = download_file(
            download_url,
            temp_path,
        )

        if actual_digest.lower() != expected_digest.lower():
            raise RuntimeError(
                "Échec de vérification SHA-256. "
                "Fichier rejeté."
            )

        print("[NOXCHAT] Intégrité SHA-256 vérifiée.")

        if system == "darwin":
            binary_data = extract_macos_binary(temp_path)

            with open(local_binary, "wb") as output:
                output.write(binary_data)

        else:
            shutil.move(str(temp_path), str(local_binary))
            temp_path = None

        if system != "windows":
            local_binary.chmod(0o755)

        print(f"[NOXCHAT] Installation terminée : {local_binary}")

        return str(local_binary)

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
