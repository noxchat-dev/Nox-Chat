
import socket
import subprocess
import sys
import time
from pathlib import Path

from launcher.cloudflare import start_tunnel, stop_tunnel
from launcher.installer import install_cloudflared
from launcher.platform_detect import detect_platform


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def wait_for_server(process, host, port, timeout=15):
    """Attend que le serveur accepte les connexions."""

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                "Le serveur NOXCHAT s'est arrêté pendant son démarrage."
            )

        try:
            with socket.create_connection(
                (host, port),
                timeout=1,
            ):
                return True
        except OSError:
            time.sleep(0.25)

    raise TimeoutError(
        "Le serveur NOXCHAT n'a pas démarré à temps."
    )


def start_server(host, port):
    """Démarre le serveur NOXCHAT comme processus indépendant."""

    command = [
        sys.executable,
        str(PROJECT_ROOT / "server" / "server.py"),
        "--host",
        host,
        "--port",
        str(port),
    ]

    print("[NOXCHAT] Démarrage du serveur...")

    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
    )

    try:
        wait_for_server(process, host, port)
    except Exception:
        if process.poll() is None:
            process.terminate()
            process.wait()
        raise

    print(f"[NOXCHAT] Serveur actif sur ws://{host}:{port}")

    return process


def run_noxchat(public=False, host="127.0.0.1", port=8765):
    """Orchestre le serveur et, facultativement, Cloudflare."""

    server_process = None
    tunnel_process = None

    try:
        server_process = start_server(host, port)

        if public:
            platform_info = detect_platform()

            if not platform_info["supported"]:
                raise RuntimeError(
                    "Système ou architecture non pris en charge."
                )

            cloudflared = install_cloudflared(platform_info)

            tunnel_process, public_url = start_tunnel(
                cloudflared,
                f"http://{host}:{port}",
            )

            websocket_url = public_url.replace(
                "https://",
                "wss://",
                1,
            )

            print("[NOXCHAT] Adresse de connexion publique :")
            print(f"  {websocket_url}")

        else:
            print("[NOXCHAT] Mode local activé.")
            print(f"  ws://{host}:{port}")

        print("\n[NOXCHAT] Services actifs. Ctrl+C pour arrêter.\n")

        while server_process.poll() is None:
            if (
                tunnel_process is not None
                and tunnel_process.poll() is not None
            ):
                raise RuntimeError(
                    "Le tunnel Cloudflare s'est arrêté."
                )

            time.sleep(0.5)

        raise RuntimeError(
            "Le serveur NOXCHAT s'est arrêté."
        )

    except KeyboardInterrupt:
        print("\n[NOXCHAT] Arrêt demandé.")

    finally:
        if tunnel_process is not None:
            stop_tunnel(tunnel_process)

        if server_process is not None:
            if server_process.poll() is None:
                print("[NOXCHAT] Arrêt du serveur...")
                server_process.terminate()

                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()
                    server_process.wait()

            print("[NOXCHAT] Serveur arrêté.")
