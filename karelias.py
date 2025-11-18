import feedparser
import json
import os
import requests

from firestore_state import init_firestore, load_seen_ids, save_seen_ids

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# --- Add your two feeds here ---
SOURCES = {
    "msrc": "https://api.msrc.microsoft.com/update-guide/rss",
    "cisco": "https://sec.cloudapps.cisco.com/security/center/psirtrss20/CiscoSecurityAdvisory.xml",
}

# --- Initialize Firestore ---
db = init_firestore()


def send_to_discord(message):
    requests.post(WEBHOOK, json={"content": message})


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


def process_cisco(entry):
    """Parse Cisco RSS feed entries."""
    # Cisco uses advisory URL as GUID
    advisory_id = entry.get("guid", entry.link)

    title = entry.get("title", "Cisco Security Advisory")
    description = entry.get("description", "")
    link = entry.get("link", "")
    date = entry.get("pubDate", entry.get("published", ""))

    # Extract CVEs if present in description
    import re
    cve_matches = re.findall(r"CVE-\d{4}-\d+", description)
    cve_list = ", ".join(cve_matches) if cve_matches else "None listed"

    message = (
        f"🔔 **New Cisco Security Advisory**\n"
        f"**Advisory:** {title}\n"
        f"**ID:** {advisory_id}\n"
        f"**CVEs:** {cve_list}\n"
        f"**Date:** {date}\n\n"
        f"{description}\n\n"
        f"🔗 {link}"
    )

    return advisory_id, message


# --- PROCESS ALL FEEDS ---
for source_name, url in SOURCES.items():
    print(f"Checking {source_name} feed...")

    # Load seen IDs for this specific feed
    seen = load_seen_ids(db, source_name)
    feed = feedparser.parse(url)
    new_ids = []

    for entry in feed.entries:

        # Choose parser based on feed name
        if source_name == "msrc":
            unique_id, message = process_msrc(entry)
        elif source_name == "cisco":
            unique_id, message = process_cisco(entry)

        if unique_id not in seen:
            new_ids.append(unique_id)
            send_to_discord(message)

    # Save updated results
    if new_ids:
        save_seen_ids(db, source_name, seen.union(new_ids))
        print(f"Saved {len(new_ids)} new items for {source_name}.")
    else:
        print(f"No new items for {source_name}.")
