
import argparse
import sys

from launcher.startup import run_noxchat


def main():
    parser = argparse.ArgumentParser(
        description="NOXCHAT — Unified Launcher"
    )

    parser.add_argument(
        "--public",
        action="store_true",
        help="Démarrer NOXCHAT avec un tunnel Cloudflare.",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Adresse d'écoute du serveur (défaut : 127.0.0.1).",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port du serveur (défaut : 8765).",
    )

    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("Le port doit être compris entre 1 et 65535.")

    if args.public and args.host not in ("127.0.0.1", "localhost"):
        parser.error(
            "Le mode public doit utiliser 127.0.0.1 ou localhost."
        )

    try:
        run_noxchat(
            public=args.public,
            host=args.host,
            port=args.port,
        )

    except (RuntimeError, OSError, TimeoutError) as error:
        print(f"\n[NOXCHAT] ERREUR : {error}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[NOXCHAT] Interruption.")
        sys.exit(130)
