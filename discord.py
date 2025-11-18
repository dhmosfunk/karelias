import os
import requests

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_to_discord(message: str) -> None:
    if not WEBHOOK:
        raise ValueError("DISCORD_WEBHOOK environment variable is not set.")

    payload = {"content": message}
    response = requests.post(WEBHOOK, json=payload)

    if response.status_code >= 400:
        raise RuntimeError(
            f"Failed to send message to Discord. Status: {response.status_code}, Response: {response.text}"
        )
