import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")

# Sales sample
sales = pd.DataFrame({
    "order_id": [1, 2],
    "order_date": ["2025-01-01", "2025-01-02"],
    "customer_id": [101, 102],
    "product_category": ["Electronics", "Clothing"],
    "product_name": ["Phone", "T-Shirt"],
    "unit_price": [500, 20],
    "quantity": [2, 5],
    "revenue": [1000, 100],
    "location": ["New York", "London"],
    "customer_segment": ["Premium", "Regular"]
})
sales.to_sql("sales", conn, if_exists="replace", index=False)

# Marketing sample
marketing = pd.DataFrame({
    "campaign_id": [1, 2],
    "channel": ["Email", "Social"],
    "roi": [3.5, 2.1]
})
marketing.to_sql("marketing", conn, if_exists="replace", index=False)

# Website analytics sample
website = pd.DataFrame({
    "session_id": [1001, 1002],
    "session_date": ["2025-01-01", "2025-01-02"]
})
website.to_sql("website_analytics", conn, if_exists="replace", index=False)

# Inventory
inventory = pd.DataFrame({
    "product_id": [1, 2],
    "product_name": ["Phone", "T-Shirt"],
    "quantity_available": [50, 200]
})
inventory.to_sql("inventory", conn, if_exists="replace", index=False)

# Customers
customers = pd.DataFrame({
    "customer_id": [101, 102],
    "name": ["Alice", "Bob"],
    "churned": [0, 1]
})
customers.to_sql("customers", conn, if_exists="replace", index=False)

conn.close()
print("✅ Sample data restored")
