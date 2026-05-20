import pandas as pd
import sqlite3
from prophet import Prophet
import joblib
import os

# Step 1: Connect to database and load sales data
conn = sqlite3.connect("database.db")
df = pd.read_sql_query("SELECT product_name, order_date, quantity FROM sales", conn)
conn.close()

# Step 2: Preprocess
df['order_date'] = pd.to_datetime(df['order_date'])
df = df.dropna(subset=['product_name', 'order_date', 'quantity'])

# Step 3: Aggregate sales per day per product
forecast_models = {}
products = df['product_name'].unique()

for product in products:
    df_product = df[df['product_name'] == product]
    daily = df_product.groupby('order_date')['quantity'].sum().reset_index()
    daily = daily.rename(columns={'order_date': 'ds', 'quantity': 'y'})

    if len(daily) < 10:
        continue  # Not enough data to train

    # Step 4: Train Prophet model
    model = Prophet()
    model.fit(daily)

    # Save the model
    model_path = f"models/prophet_{product.replace(' ', '_').replace('/', '_')}.pkl"
    joblib.dump(model, model_path)
    forecast_models[product] = model_path

# Step 5: Save the list of products
joblib.dump(products.tolist(), "models/inventory_forecast_products.pkl")
print("✅ Prophet models saved for products in 'models/'")
