import feedparser
import json
import os
import requests

RSS_URL = "https://api.msrc.microsoft.com/update-guide/rss"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
LAST_FILE = "last_msrc.json"

# Load previously processed CVEs
if os.path.exists(LAST_FILE):
    with open(LAST_FILE, "r") as f:
        seen = set(json.load(f))
else:
    seen = set()

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

# Save updated list
with open(LAST_FILE, "w") as f:
    json.dump(list(seen.union(new_ids)), f)
