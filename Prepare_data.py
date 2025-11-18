import pandas as pd
from urllib.parse import urlparse

# ------------------------------
# Step 1: Load datasets
# ------------------------------
df_urlhaus = pd.read_csv("urlhaus_flattened.csv")      # flattened JSON URL info
df_urlset = pd.read_csv("urlset.csv", encoding="latin1",on_bad_lines='skip',engine='python')                 # domain-level features
df_phis = pd.read_csv("malicious_phish.csv")          # 2-column phishing table

# ------------------------------
# Step 2: Ensure 'domain' columns exist
# ------------------------------
def extract_domain(url):
    try:
        parsed = urlparse(url if "://" in url else "http://" + url)
        return parsed.hostname.lower()
    except:
        return None

# URLhaus already has domain column; fill if missing
if "domain" not in df_urlhaus.columns or df_urlhaus["domain"].isnull().all():
    df_urlhaus["domain"] = df_urlhaus["url"].apply(extract_domain)

# Phis table: extract domain
if "domain" not in df_phis.columns:
    df_phis["domain"] = df_phis["url"].apply(extract_domain)

# ------------------------------
# Step 3: Merge URL-level tables first
# ------------------------------
# Combine urlhaus + malicious_phis on URL
df_urls_combined = pd.concat([df_urlhaus, df_phis], ignore_index=True, sort=False)

# Optional: deduplicate URLs, keep first occurrence
df_urls_combined.drop_duplicates(subset=["url"], inplace=True)

# ------------------------------
# Step 4: Merge with domain-level features (urlset)
# ------------------------------
# Left join: keep all URLs
df_master = df_urls_combined.merge(df_urlset, on="domain", how="left", suffixes=('_url','_domain'))

# ------------------------------
# Step 5: Handle missing feature values / labels
# ------------------------------
# Fill numeric columns from urlset with -1
numeric_cols = df_urlset.select_dtypes(include='number').columns.tolist()
for col in numeric_cols:
    if col in df_master.columns:
        df_master[col].fillna(-1, inplace=True)

# Fill missing labels (from urlset or url_phis) with 'unknown'
if 'label' in df_master.columns:
    df_master['label'].fillna('unknown', inplace=True)
else:
    df_master['label'] = 'unknown'

# ------------------------------
# Step 6: Save final master CSV
# ------------------------------
df_master.to_csv("master_urls_final.csv", index=False)
print("Master CSV saved as 'master_urls_final.csv'")
print("Rows:", len(df_master))
print("Columns:", df_master.columns.tolist())
