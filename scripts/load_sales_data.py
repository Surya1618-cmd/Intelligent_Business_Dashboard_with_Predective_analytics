import pandas as pd
import sqlite3
import os

# ✅ Corrected path
DATA_PATH = "../data/sales_dataset_200k_updated.csv"
DB_PATH = "../database.db"

# Step 1: Load the sales dataset
df = pd.read_csv(DATA_PATH)

# Step 2: Preprocess the data
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Step 3: Connect to SQLite and create table
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create sales table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    order_id TEXT,
    order_date TEXT,
    customer_id TEXT,
    product_id TEXT,
    category TEXT,
    sub_category TEXT,
    product_name TEXT,
    quantity INTEGER,
    unit_price REAL,
    discount REAL,
    profit REAL,
    region TEXT,
    country TEXT
)
""")

# Step 4: Insert data into the database
df.to_sql("sales", conn, if_exists="replace", index=False)

# Step 5: Confirm and close
print("✅ Sales data successfully loaded into database.")
conn.close()
