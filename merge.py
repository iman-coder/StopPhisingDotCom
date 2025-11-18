import pandas as pd
from datetime import datetime

# ------------------------------
# Load datasets
# ------------------------------
main_df = pd.read_csv("master_urls_cleaned.csv", encoding="utf-8", on_bad_lines="skip", low_memory=False)
phi_df = pd.read_csv("PhiUSIIL_Phishing_URL_Dataset.csv", encoding="utf-8", on_bad_lines="skip", low_memory=False)

# ------------------------------
# Columns required for CRUD app
# ------------------------------
required_columns = {
    'url': '',
    'domain': '',
    'date_added': pd.Timestamp(datetime.today()),
    'url_status': 'online',
    'threat_category': 'phishing',
    'source': 'PhiUSIIL',
    'filename': ''
}

# ------------------------------
# Function to normalize a dataset
# ------------------------------
def normalize_df(df):
    df = df.copy()  # avoid SettingWithCopyWarning

    # Ensure all required columns exist
    for col, default in required_columns.items():
        if col not in df.columns:
            df[col] = default
        else:
            df.loc[:, col] = df[col].fillna(default)

    # Convert date_added safely, handling mixed types and NaT
    df.loc[:, 'date_added'] = df['date_added'].apply(
        lambda x: pd.to_datetime(x, errors='coerce', utc=True) if pd.notnull(x) else pd.Timestamp(datetime.today())
    )
    # Make naive datetime
    df.loc[:, 'date_added'] = df['date_added'].apply(lambda x: x.tz_convert(None) if pd.notnull(x) else pd.Timestamp(datetime.today()))

    # Fill other CRUD-required columns
    df.loc[:, 'url_status'] = df['url_status'].fillna('online')
    df.loc[:, 'threat_category'] = df['threat_category'].fillna('phishing')
    df.loc[:, 'source'] = df['source'].fillna('PhiUSIIL')
    df.loc[:, 'filename'] = df['filename'].fillna('')

    return df

# ------------------------------
# Normalize both datasets
# ------------------------------
main_df_norm = normalize_df(main_df)
phi_df_norm = normalize_df(phi_df)

# ------------------------------
# Merge datasets, preserve all columns
# ------------------------------
merged_df = pd.concat([main_df_norm, phi_df_norm], ignore_index=True)

# ------------------------------
# Generate unique sequential IDs
# ------------------------------
merged_df.insert(0, 'id', range(1, len(merged_df) + 1))

# ------------------------------
# Save the final merged dataset
# ------------------------------
merged_df.to_csv("urls_merged_crud.csv", index=False)
print("Merge complete. All URLs/domains preserved, filenames normalized, ready for CRUD app.")

'''
# Load your dataset
df = pd.read_csv("master_urls_final.csv", encoding="utf-8", on_bad_lines="skip", low_memory=False)

# 1. Fill empty threat_type values using type
df['threat_type'] = df['threat_type'].fillna(df['type'])

# 2. Drop the now redundant column
df.drop(columns=['type'], inplace=True)

# 3. Clean the final threat_type column
df['threat_type'] = df['threat_type'].astype(str).str.strip().str.lower()

# 4. (Optional) rename it for clarity
df.rename(columns={'threat_type': 'threat_category'}, inplace=True)

# 5. Save the cleaned result
df.to_csv("master_urls_cleaned.csv", index=False)
print("Clean merge done. 'type' dropped and 'threat_type' unified into 'threat_category'.")
'''

'''
df = pd.read_csv("master_urls_final.csv", encoding="utf-8", on_bad_lines="skip", low_memory=False)

# Check sample values
print(df[['threat_type', 'type']].head(20))

# Compare unique values and differences
print("Unique threat_type:", df['threat_type'].dropna().unique()[:10])
print("Unique type:", df['type'].dropna().unique()[:10])

# Check if they match exactly (ignoring case)
same = (df['threat_type'].astype(str).str.lower() == df['type'].astype(str).str.lower())
print(f"Same entries: {same.sum()} / {len(df)} ({same.mean()*100:.2f}%)")
'''
'''
main_df = pd.read_csv("master_urls_final.csv", encoding="utf-8", on_bad_lines="skip")
new_df  = pd.read_csv("PhiUSIIL_Phishing_URL_Dataset.csv", encoding="utf-8", on_bad_lines="skip")

#print("Main DF columns:", list(main_df.columns))
#print("New DF columns:", list(new_df.columns))

# Standardize the key for merging
new_df.rename(columns={'URL': 'url'}, inplace=True)

# Merge on the 'url' column (inner keeps only common URLs)
merged_df = pd.merge(main_df, new_df, on='url', how='inner')

print(merged_df.shape)
merged_df.to_csv("merged_dataset.csv", index=False)
'''
'''
print(main_df.shape, new_df.shape)

# Align columns
new_df = new_df[main_df.columns]

merged_df = pd.concat([main_df, new_df], axis=0, ignore_index=True)

merged_df.drop_duplicates(subset=["url"], inplace=True)

merged_df["date_added"] = pd.to_datetime(merged_df["date_added"], errors="coerce")
merged_df["tags"] = merged_df["tags"].astype(str)  # uniform type

print("Merged dataset shape:", merged_df.shape)
print("Unique URLs:", merged_df["url"].nunique())
merged_df.head()

merged_df.to_csv("merged_urls.csv", index=False, encoding="utf-8")
'''