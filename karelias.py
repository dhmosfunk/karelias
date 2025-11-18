import feedparser
import json
import os
import requests

from firebase.firestore_state import init_firestore, load_seen_ids, save_seen_ids
from discord import send_to_discord

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

SOURCES = {
    "msrc": "https://api.msrc.microsoft.com/update-guide/rss",
}

db = init_firestore()

def process_msrc(entry):
    """Parse Microsoft MSRC feed entries."""
    cve_id = entry.guid
    title = entry.title
    description = entry.description
    link = entry.link
    date = entry.published

    message = (
        f"🚨 **New Microsoft CVE**\n"
        f"**{cve_id}**\n"
        f"**Title:** {title}\n"
        f"**Date:** {date}\n\n"
        f"{description}\n\n"
        f"🔗 {link}"
    )
    return cve_id, message


for source_name, url in SOURCES.items():
    print(f"Checking {source_name} feed...")

    seen = load_seen_ids(db, source_name)
    feed = feedparser.parse(url)
    new_ids = []

    for entry in feed.entries:
        if source_name == "msrc":
            unique_id, message = process_msrc(entry)
            
        if unique_id not in seen:
            new_ids.append(unique_id)
            send_to_discord(message)

    if new_ids:
        save_seen_ids(db, source_name, seen.union(new_ids))
        print(f"Saved {len(new_ids)} new items for {source_name}.")
    else:
        print(f"No new items for {source_name}.")
