import pandas as pd
import requests
import sqlite3

# ------------------ LIVE API FETCHING ------------------

def get_live_sales_data():
    try:
        response = requests.get("https://dummyjson.com/products")
        data = response.json()
        df = pd.DataFrame(data["products"])

        # Simulate transformation to match sales table
        df_sales = pd.DataFrame({
            "order_id": df["id"],
            "order_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "customer_id": df["id"],  # Simulated
            "product_name": df["title"],
            "product_category": df["category"],
            "quantity": df["stock"],
            "unit_price": df["price"],
            "revenue": df["price"] * df["stock"],
            "rating": df["rating"],
            "location": "Online",  # Placeholder
            "customer_segment": "Regular",  # Placeholder
        })
        return df_sales

    except Exception as e:
        print("Sales API error:", e)
        return pd.DataFrame()

def get_live_website_traffic():
    try:
        return pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv")  # TEMP working CSV
    except Exception as e:
        print("Website analytics error:", e)
        return pd.DataFrame()

def get_live_campaign_data():
    try:
        return pd.DataFrame({
            "campaign_id": [f"CMP-{i}" for i in range(1, 6)],
            "roi": [round(x, 2) for x in [2.5, 1.8, 3.2, 2.1, 4.0]],
            "channel": ["Email", "Social", "Google Ads", "Affiliates", "SMS"]
        })
    except Exception as e:
        print("Campaign data error:", e)
        return pd.DataFrame()

# ------------------ SYNC TO SQLITE ------------------

def sync_live_data_to_db():
    try:
        conn = sqlite3.connect("database.db")

        sales_df = get_live_sales_data()
        if not sales_df.empty:
            sales_df.to_sql("sales", conn, if_exists="replace", index=False)

        web_df = get_live_website_traffic()
        if not web_df.empty:
            web_df["session_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
            web_df["session_id"] = range(1, len(web_df)+1)
            web_df = web_df[["session_date", "session_id"]]
            web_df.to_sql("website_analytics", conn, if_exists="replace", index=False)

        campaign_df = get_live_campaign_data()
        if not campaign_df.empty:
            campaign_df.to_sql("marketing", conn, if_exists="replace", index=False)

        conn.close()
        print("✅ Live data synced successfully.")

    except Exception as e:
        print("❌ Sync failed:", e)
