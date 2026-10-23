# NOXCHAT
### Encrypted Terminal Chat Application | Application de chat chiffré en terminal

**NOXCHAT** is a terminal-based chat application built with Python and WebSockets. It provides public messaging, private messages, colored usernames, and AES-GCM message encryption.

**NOXCHAT** est une application de discussion en terminal développée en Python avec WebSockets. Elle propose des messages publics, des messages privés, des pseudonymes colorés et le chiffrement des messages avec AES-GCM.

---

## 🇫🇷 Français

### Présentation

NOXCHAT est un projet éducatif qui explore la création d'une application de messagerie en temps réel, le chiffrement des messages et la communication client-serveur.

### Fonctionnalités

- Messagerie publique en temps réel.
- Envoi de messages privés avec `/msg`.
- Chiffrement et déchiffrement des messages avec AES-GCM.
- Pseudonymes et couleurs dans le terminal.
- Notifications de connexion et de déconnexion.
- Commandes intégrées :
  - `/help` — afficher les commandes disponibles.
  - `/users` — afficher les utilisateurs connectés.
  - `/msg pseudo message` — envoyer un message privé.
  - `/clear` — nettoyer le terminal local.
  - `/quit` — quitter l'application.

### Technologies

- Python 3.12 ou version compatible.
- WebSockets (`websockets`).
- Cryptographie (`cryptography`).
- Interface terminal (`prompt_toolkit`).

### Prérequis

- Python installé.
- Git (facultatif pour l'installation).
- Un terminal compatible avec les séquences ANSI.

### Installation

Clonez le dépôt, puis entrez dans le dossier du projet :

```bash
git clone <URL_DU_DEPOT>
cd <DOSSIER_DU_DEPOT>
```

Créez et activez un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installez les dépendances :

```bash
pip install -r requirements.txt
```

### Lancement local

Ouvrez un premier terminal à la racine du projet et démarrez le serveur :

```bash
python -m server.server
```

Ouvrez un deuxième terminal, activez l'environnement virtuel et démarrez le premier client :

```bash
python -m client.client
```

Pour tester plusieurs clients sur le même ordinateur, ouvrez d'autres terminaux et lancez également le client.

**Important :** la configuration actuelle utilise `127.0.0.1:8765`. Elle est destinée aux tests locaux. Les clients doivent utiliser une configuration de clé compatible pour pouvoir déchiffrer les messages.

### Tests

Test du chiffrement :

```bash
python -m tests.test_crypto
```

Test de connexion : démarrez d'abord le serveur, puis exécutez :

```bash
python test_connection.py
```

### Sécurité

Ce projet est éducatif et en cours de développement. Le chiffrement des messages ne signifie pas que l'ensemble du système est déjà sécurisé.

- Ne publiez jamais `.noxchat.key` ni aucune autre clé secrète.
- N'utilisez pas cette version pour des communications sensibles sans audit de sécurité.
- La gestion et la distribution des clés doivent être adaptées avant une utilisation publique.
- L'hébergement public et la connexion sécurisée des clients nécessitent une configuration supplémentaire.

### État du projet

Le chat local, les messages privés, les couleurs et les principales commandes ont été testés. Le déploiement public reste à configurer.

---

## 🇬🇧 English

### Overview

NOXCHAT is an educational project exploring real-time messaging, message encryption, and client-server communication.

### Features

- Real-time public messaging.
- Private messages using `/msg`.
- AES-GCM message encryption and decryption.
- Colored usernames in the terminal.
- User join and leave notifications.
- Built-in commands:
  - `/help` — display available commands.
  - `/users` — list connected users.
  - `/msg username message` — send a private message.
  - `/clear` — clear the local terminal.
  - `/quit` — exit the application.

### Technologies

- Python 3.12 or a compatible version.
- WebSockets (`websockets`).
- Cryptography (`cryptography`).
- Terminal interface (`prompt_toolkit`).

### Requirements

- Python installed.
- Git (optional for installation).
- A terminal that supports ANSI escape sequences.

### Installation

Clone the repository and enter the project directory:

```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_DIRECTORY>
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Run locally

Open a terminal in the project root and start the server:

```bash
python -m server.server
```

Open a second terminal, activate the virtual environment, and start the first client:

```bash
python -m client.client
```

To test multiple clients on the same computer, open additional terminals and start another client in each one.

**Important:** the current configuration uses `127.0.0.1:8765` and is intended for local testing. Clients must use compatible encryption keys to decrypt messages.

### Tests

Test encryption:

```bash
python -m tests.test_crypto
```

Connection test: start the server first, then run:

```bash
python test_connection.py
```

### Security

This is an educational project under development. Message encryption alone does not guarantee that the entire system is secure.

- Never publish `.noxchat.key` or any other secret key.
- Do not use this version for sensitive communications without a security audit.
- Key management and distribution must be redesigned appropriately before public use.
- Public hosting and secure client connections require additional configuration.

### Project status

Local chat, private messaging, terminal colors, and the main commands have been tested. Public deployment still needs to be configured.

---

## License / Licence

No license has been specified yet. All rights are reserved unless a license is added to this repository.
