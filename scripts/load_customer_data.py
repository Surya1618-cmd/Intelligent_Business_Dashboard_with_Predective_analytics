import pandas as pd
import sqlite3

DATA_PATH = "../data/customer_data.csv"
DB_PATH = "../database.db"

df = pd.read_csv(DATA_PATH)
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

conn = sqlite3.connect(DB_PATH)
df.to_sql("customers", conn, if_exists="replace", index=False)
conn.close()
print("✅ Customer data loaded.")
