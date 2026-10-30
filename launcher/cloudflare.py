
import queue
import re
import subprocess
import threading


TUNNEL_URL_PATTERN = re.compile(
    r"https://[a-zA-Z0-9-]+\.trycloudflare\.com"
)


def start_tunnel(binary, local_url, timeout=45):
    """Démarre Cloudflare et récupère son URL publique."""

    command = [
        str(binary),
        "tunnel",
        "--no-autoupdate",
        "--url",
        local_url,
    ]

    print("[NOXCHAT] Démarrage du tunnel Cloudflare...")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    output_queue = queue.Queue()

    def read_output():
        try:
            for line in process.stdout:
                output_queue.put(line)
        finally:
            output_queue.put(None)

    reader = threading.Thread(
        target=read_output,
        daemon=True,
    )
    reader.start()

    public_url = None

    try:
        while True:
            try:
                line = output_queue.get(timeout=timeout)
            except queue.Empty:
                raise TimeoutError(
                    "Cloudflare n'a pas fourni de lien à temps."
                )

            if line is None:
                raise RuntimeError(
                    "Cloudflare s'est arrêté avant de fournir un lien."
                )

            print(line, end="", flush=True)

            match = TUNNEL_URL_PATTERN.search(line)

            if match:
                public_url = match.group(0)
                break

            if process.poll() is not None:
                raise RuntimeError(
                    "Le processus Cloudflare s'est arrêté."
                )

        print("\n[NOXCHAT] Tunnel public disponible :")
        print(f"  {public_url}\n")

        return process, public_url

    except Exception:
        if process.poll() is None:
            process.terminate()

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        raise


def stop_tunnel(process):
    """Arrête proprement le processus Cloudflare."""

    if process and process.poll() is None:
        print("\n[NOXCHAT] Arrêt du tunnel Cloudflare...")

        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

        print("[NOXCHAT] Tunnel arrêté.")
