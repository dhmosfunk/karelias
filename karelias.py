import feedparser
import json
import os
import requests

from firestore_state import init_firestore, load_seen_ids, save_seen_ids

RSS_URL = "https://api.msrc.microsoft.com/update-guide/rss"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# Initialize Firestore
db = init_firestore()

# Load previously processed CVEs from Firestore
seen = load_seen_ids(db)

feed = feedparser.parse(RSS_URL)
new_ids = []

for entry in feed.entries:
    cve_id = entry.guid  # example: CVE-2025-13042

    if cve_id not in seen:
        new_ids.append(cve_id)

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

        # Send to Discord webhook
        requests.post(WEBHOOK, json={"content": message})

# Save updated list to Firestore
if new_ids:
    save_seen_ids(db, seen.union(new_ids))
    print(f"Saved {len(new_ids)} new IDs to Firestore.")
else:
    print("No new CVEs.")
