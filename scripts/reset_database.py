import sqlite3

# Path to your database
DB_PATH = "C:/Users/yedug/Documents/Intelligent_Business_Dashboard/database.db"

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Step 1: Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Step 2: Delete data from each table
for table in tables:
    table_name = table[0]
    cursor.execute(f"DELETE FROM {table_name}")
    print(f"✅ Cleared table: {table_name}")

# Step 3: Commit and close
conn.commit()
conn.close()
print("✅ All tables cleared successfully.")
