import pandas as pd
import sqlite3

# File and DB paths
DATA_PATH = "../data/financial_data_realistic.csv"
DB_PATH = "../database.db"

# Load CSV
df = pd.read_csv(DATA_PATH)
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Connect to SQLite and insert
conn = sqlite3.connect(DB_PATH)
df.to_sql("financial", conn, if_exists="replace", index=False)
conn.close()

print("✅ Financial data loaded successfully into the database.")
