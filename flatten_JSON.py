import json
import pandas as pd
from urllib.parse import urlparse

# Load JSON file
with open("urlhaus_full.json", "r") as f:
    data = json.load(f)

rows = []
for url_id, entries in data.items():
    for entry in entries:
        url = entry.get("url")
        domain = urlparse(url if "://" in url else "http://" + url).hostname
        tags = entry.get("tags")
        if isinstance(tags, list):
            tags_str = ",".join(tags)
        elif isinstance(tags, str):
            tags_str = tags
        else:
            tags_str = ""

        rows.append({
            "url_id": url_id,
            "url": url,
            "domain": domain.lower() if domain else None,
            "date_added": entry.get("dateadded"),
            "url_status": entry.get("url_status"),
            "threat_type": entry.get("threat"),
            "tags": tags_str,
            "urlhaus_link": entry.get("urlhaus_link"),
            "reporter": entry.get("reporter"),
            "source": "urlhaus"
        })

# Convert to DataFrame
df_json = pd.DataFrame(rows)

# Optional: standardize labels for CRUD app
def map_label(threat):
    if threat is None:
        return None
    t = threat.lower()
    if "phish" in t:
        return "phishing"
    elif "malware" in t or "download" in t:
        return "malware"
    else:
        return t

df_json["label"] = df_json["threat_type"].apply(map_label)

# Save flattened CSV
df_json.to_csv("urlhaus_flattened.csv", index=False)
print("Flattened JSON saved to urlhaus_flattened.csv")
print("Counts by label:\n", df_json['label'].value_counts())
