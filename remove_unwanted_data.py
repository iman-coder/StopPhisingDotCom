import pandas as pd

# ------------------------------
# Load the merged dataset
# ------------------------------
merged_df = pd.read_csv("urls_merged_crud.csv", encoding="utf-8", low_memory=False)

# ------------------------------
# Columns to keep for CRUD export
# ------------------------------
crud_columns = ['id', 'url', 'domain', 'date_added', 'url_status', 'threat_category', 'source', 'filename']

# ------------------------------
# Remove rows without domain
# ------------------------------
merged_df = merged_df[merged_df['domain'].notna() & (merged_df['domain'] != '')]

# ------------------------------
# Prepare export DataFrame with only CRUD columns
# ------------------------------
export_df = merged_df[crud_columns]

# ------------------------------
# Save to CSV
# ------------------------------
export_df.to_csv("urls_merged_crud1.csv", index=False)
print(" Export complete. Rows without domain removed, only CRUD columns included.")
