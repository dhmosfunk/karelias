import requests
import json
import os

WEBHOOK = os.getenv("DISCORD_WEBHOOK")
LAST_FILE = "last_cve.json"

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=10"

# Load previously seen CVEs
if os.path.exists(LAST_FILE):
    with open(LAST_FILE, "r") as f:
        last_seen = set(json.load(f))
else:
    last_seen = set()

response = requests.get(NVD_API).json()
new_ids = []

for item in response.get("vulnerabilities", []):
    cve = item["cve"]
    cve_id = cve["id"]

    if cve_id not in last_seen:
        new_ids.append(cve_id)

        description = cve["descriptions"][0]["value"]
        link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"

        message = f"**New CVE Detected:** {cve_id}\n{description}\n{link}"

        requests.post(WEBHOOK, json={"content": message})

# Save updated CVE list
with open(LAST_FILE, "w") as f:
    json.dump(list(last_seen.union(new_ids)), f)
