# NOXCHAT
### Encrypted Terminal Chat Application | Application de chat chiffré en terminal

NOXCHAT is an educational terminal-based messaging application built with Python and WebSockets. It supports real-time public messaging, private messages, colored usernames, and AES-GCM encryption functionality.

NOXCHAT est une application éducative de messagerie en terminal développée en Python avec WebSockets. Elle prend en charge la messagerie publique en temps réel, les messages privés, les pseudonymes colorés et le chiffrement AES-GCM.

---

## 🇫🇷 Français

### Présentation

NOXCHAT explore la communication client-serveur en temps réel, le chiffrement des messages, la gestion des identités et les connexions WebSocket.

Le projet comprend un serveur, des clients en terminal et un lanceur permettant de démarrer les services localement ou de créer un tunnel public avec Cloudflare.

### Fonctionnalités

- Messagerie publique en temps réel.
- Messages privés avec `/msg`.
- Fonctionnalités de chiffrement AES-GCM.
- Gestion des identités et dérivation de clés de session dans les modules dédiés.
- Pseudonymes et couleurs dans le terminal.
- Notifications de connexion et de déconnexion.
- Limite de 50 clients simultanés configurée côté serveur.
- Connexion à un serveur avec une adresse WebSocket personnalisée.
- Lanceur unifié pour le serveur et le tunnel Cloudflare.
- Arrêt des processus avec `Ctrl+C`.

### Technologies

- Python 3.12 ou version compatible.
- `websockets` 17.3.
- `cryptography` 50.0.2.
- `prompt_toolkit` 3.x.
- Cloudflare Tunnel (`cloudflared`) pour le mode public.

### Prérequis

- Python installé.
- Git.
- Connexion Internet pour installer les dépendances et utiliser le mode public.
- Un terminal compatible avec les séquences ANSI.

### Installation

Clonez le dépôt :

```bash
git clone https://github.com/noxchat-dev/Nox-Chat.git
cd Nox-Chat
```

Créez un environnement virtuel :

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Installez les dépendances :

```bash
python -m pip install -r requirements.txt
```

### Démarrage local

À la racine du projet, lancez :

```bash
python run_noxchat.py
```

Le serveur écoute par défaut sur :

```text
ws://127.0.0.1:8765
```

Dans un deuxième terminal, activez le même environnement virtuel et lancez un client :

```bash
python -m client.client "ws://127.0.0.1:8765"
```

Vous pouvez ouvrir plusieurs terminaux et démarrer plusieurs clients.

Pour arrêter les services, utilisez `Ctrl+C` dans le terminal du lanceur.

### Mode public avec Cloudflare

Lancez :

```bash
python run_noxchat.py --public
```

Le lanceur :

1. Démarre le serveur NOXCHAT.
2. Recherche `cloudflared` sur le système.
3. Si nécessaire, tente de télécharger une version compatible depuis les publications officielles de Cloudflare.
4. Vérifie l'empreinte SHA-256 fournie par l'API GitHub avant d'installer le fichier téléchargé.
5. Démarre le tunnel Cloudflare.
6. Affiche l'adresse WebSocket publique.

Un lien HTTPS de type :

```text
https://example.trycloudflare.com
```

correspond à une adresse WebSocket sécurisée :

```text
wss://example.trycloudflare.com
```

Pour rejoindre le serveur depuis un autre appareil :

```bash
python -m client.client "wss://example.trycloudflare.com"
```

Remplacez l'adresse d'exemple par celle affichée par votre lanceur.

**À savoir :** les Quick Tunnels Cloudflare utilisent des adresses temporaires. Le lien peut changer à chaque démarrage. Le mode public nécessite une connexion Internet.

### Options du lanceur

Afficher l'aide :

```bash
python run_noxchat.py --help
```

Démarrer en local avec un autre port :

```bash
python run_noxchat.py --port 9000
```

Démarrer avec une autre adresse d'écoute :

```bash
python run_noxchat.py --host 127.0.0.1 --port 9000
```

Le mode public est prévu pour écouter sur `127.0.0.1` ou `localhost`.

### Commandes du client

- `/msg pseudo message` — envoyer un message privé.
- `/quit` — quitter l'application.

Les commandes disponibles peuvent dépendre de la version du client.

### Tests

Les tests du dépôt sont des scripts Python autonomes ; le projet n'est pas actuellement organisé comme une suite pytest.

Tests des modules cryptographiques et des identités :

```bash
python -m tests.test_crypto
python -m tests.test_identity
python -m tests.test_session
python -m tests.test_session_crypto
python test_key_exchange.py
```

Certains tests nécessitent un serveur en fonctionnement. Démarrez d'abord le serveur, puis exécutez les tests concernés :

```bash
python -m server.server
```

Dans un autre terminal :

```bash
python test_connection.py
python test_chat.py
```

Le test de capacité `test_capacity.py` vérifie le comportement du serveur face à plusieurs connexions. Il doit être exécuté dans un environnement de test isolé.

Vérification de la syntaxe :

```bash
python -m compileall -q client server noxchat launcher tests run_noxchat.py
```

### Sécurité et limites connues

NOXCHAT est un projet éducatif. Il ne doit pas être considéré comme une messagerie prête pour des communications sensibles.

- Le chiffrement AES-GCM ne garantit pas à lui seul la sécurité de toute l'application.
- Les mécanismes d'identité et de dérivation de clés présents dans les modules doivent être intégrés et audités dans le protocole complet avant de revendiquer un chiffrement de bout en bout.
- Le mode public ne dispose pas encore d'un système d'authentification par jeton d'invitation.
- Une adresse Cloudflare publique peut être utilisée par toute personne qui la possède et peut atteindre le service.
- Ne transmettez aucune information confidentielle via une instance publique non protégée.
- Ne publiez jamais `.noxchat.key`, des clés privées ou des secrets.
- L'empreinte SHA-256 vérifie la correspondance avec le digest publié par GitHub ; elle ne remplace pas une vérification indépendante de signature.
- Les téléchargements et l'installation automatique de `cloudflared` doivent être validés sur chaque système cible.

### État du projet

Le lancement local, les connexions entre plusieurs clients, le lancement du tunnel Cloudflare et la connexion publique ont été testés sur l'environnement Linux Mint du développeur.

La compatibilité complète avec Windows et macOS, l'installation sur une machine dépourvue de `cloudflared` et l'authentification du mode public restent à valider ou à développer.

---

## 🇬🇧 English

### Overview

NOXCHAT is an educational terminal-based messaging application built with Python and WebSockets. It explores real-time client-server communication, message encryption, identity management, and remote connectivity.

The project includes a WebSocket server, terminal clients, and a unified launcher for local operation or public connectivity through Cloudflare Tunnel.

### Features

- Real-time public messaging.
- Private messages using `/msg`.
- AES-GCM encryption functionality.
- Identity and session-key derivation modules.
- Colored usernames.
- Join and leave notifications.
- Configured server limit of 50 simultaneous clients.
- Custom WebSocket server addresses.
- Unified server and Cloudflare tunnel launcher.
- Process cleanup using `Ctrl+C`.

### Technologies

- Python 3.12 or compatible.
- `websockets` 17.3.
- `cryptography` 50.0.2.
- `prompt_toolkit` 3.x.
- Cloudflare Tunnel (`cloudflared`) for public mode.

### Requirements

- Python.
- Git.
- Internet access for dependency installation and public mode.
- A terminal supporting ANSI escape sequences.

### Installation

Clone the repository:

```bash
git clone https://github.com/noxchat-dev/Nox-Chat.git
cd Nox-Chat
```

Create a virtual environment:

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Local startup

Run the unified launcher:

```bash
python run_noxchat.py
```

The default server address is:

```text
ws://127.0.0.1:8765
```

In another terminal, activate the virtual environment and start a client:

```bash
python -m client.client "ws://127.0.0.1:8765"
```

Additional clients can be started in separate terminals.

Press `Ctrl+C` in the launcher terminal to stop the services.

### Public mode with Cloudflare

Run:

```bash
python run_noxchat.py --public
```

The launcher starts the NOXCHAT server, checks for `cloudflared`, attempts to download a compatible official release if needed, verifies its GitHub-provided SHA-256 digest, and starts a Cloudflare Quick Tunnel.

A public HTTPS address:

```text
https://example.trycloudflare.com
```

is converted to a secure WebSocket address:

```text
wss://example.trycloudflare.com
```

Connect from another device:

```bash
python -m client.client "wss://example.trycloudflare.com"
```

Replace the example address with the URL displayed by the launcher.

Cloudflare Quick Tunnel URLs are temporary and may change after restarting the tunnel.

### Launcher options

Display help:

```bash
python run_noxchat.py --help
```

Use a custom port:

```bash
python run_noxchat.py --port 9000
```

Use a custom listening address:

```bash
python run_noxchat.py --host 127.0.0.1 --port 9000
```

Public mode is restricted by the launcher to `127.0.0.1` or `localhost`.

### Client commands

- `/msg username message` — send a private message.
- `/quit` — leave the application.

Available commands may depend on the client version.

### Tests

The repository currently uses standalone Python test scripts rather than a pytest test suite.

Run cryptography and identity tests:

```bash
python -m tests.test_crypto
python -m tests.test_identity
python -m tests.test_session
python -m tests.test_session_crypto
python test_key_exchange.py
```

Some tests require a running server. Start it first:

```bash
python -m server.server
```

Then, in another terminal:

```bash
python test_connection.py
python test_chat.py
```

The capacity test `test_capacity.py` should be run in an isolated test environment.

Check Python syntax:

```bash
python -m compileall -q client server noxchat launcher tests run_noxchat.py
```

### Security and known limitations

NOXCHAT is an educational project and must not be considered production-ready for sensitive communications.

- AES-GCM encryption alone does not guarantee the security of the entire application.
- Identity and session-key derivation modules must be fully integrated and audited within the complete protocol before claiming end-to-end encryption.
- Public mode does not yet implement invitation-token authentication.
- Anyone who obtains the public Cloudflare URL may be able to reach the service.
- Do not transmit confidential information through an unprotected public instance.
- Never publish `.noxchat.key`, private keys, or other secrets.
- SHA-256 verification checks the downloaded file against the digest published by GitHub; it is not an independent signature verification.
- Automatic `cloudflared` installation must be validated on every target operating system.

### Project status

Local startup, multiple-client communication, Cloudflare tunnel startup, and public WebSocket connectivity have been tested on the developer's Linux Mint environment.

Full Windows and macOS compatibility, installation when `cloudflared` is absent, and public-mode authentication remain to be validated or implemented.

---

## License / Licence

No license has been specified yet. All rights are reserved unless a license is added to this repository.
