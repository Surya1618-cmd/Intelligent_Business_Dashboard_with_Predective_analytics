import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")
df = pd.read_sql_query("SELECT * FROM customers LIMIT 1", conn)
print(df.columns)
