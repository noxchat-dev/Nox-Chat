import json


def encode_message(message_type: str, payload: str) -> str:
    """Transforme un message en une structure JSON."""
    return json.dumps({
        "type": message_type,
        "payload": payload,
    })


def decode_message(raw_message: str) -> dict:
    """Vérifie et décode la structure JSON d'un message."""
    data = json.loads(raw_message)

    if not isinstance(data, dict):
        raise ValueError("Format de message invalide.")

    if not isinstance(data.get("type"), str):
        raise ValueError("Type de message invalide.")

    if not isinstance(data.get("payload"), str):
        raise ValueError("Contenu de message invalide.")

    return data
