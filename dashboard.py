
# Intelligent Business Dashboard - Full Updated Version with Static/Dynamic DB Switching
import streamlit as st
import pandas as pd
import sqlite3
import joblib
import numpy as np
import plotly.express as px
from datetime import datetime
import os

# ------------------ Setup ------------------
st.set_page_config(page_title="Intelligent Business Dashboard", layout="wide")

# ------------------ Mode Selection ------------------
st.sidebar.title("⚙️ Settings")
db_mode = st.sidebar.radio("Select Data Source:", ["Static Dataset", "Dynamic Upload"])
DB_PATH = "database.db" if db_mode == "Static Dataset" else "dynamic.db"

# Clear cache when mode changes
if "last_mode" not in st.session_state or st.session_state.last_mode != db_mode:
    st.cache_data.clear()
    st.session_state.last_mode = db_mode

# ------------------ File Uploads (For Dynamic Mode) ------------------
if db_mode == "Dynamic Upload":
    st.sidebar.subheader("📤 Upload CSVs (Optional)")
    upload_tables = {
        "Sales": "sales",
        "Customers": "customers",
        "Inventory": "inventory",
        "Marketing": "marketing",
        "Website Analytics": "website_analytics"
    }

    for label, table in upload_tables.items():
        uploaded_file = st.sidebar.file_uploader(f"Upload {label} CSV", type=["csv"], key=label)
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
            conn = sqlite3.connect(DB_PATH)
            df.to_sql(table, conn, if_exists="replace", index=False)
            conn.close()
            st.sidebar.success(f"{label} data uploaded and saved to dynamic database.")

    if st.sidebar.button("♻️ Reset Dynamic Database"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for table in upload_tables.values():
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()
        conn.close()
        st.sidebar.success("✅ Dynamic database reset.")

# ------------------ Connect to Database ------------------
conn = sqlite3.connect(DB_PATH)

@st.cache_data
def get_summary(query):
    return pd.read_sql_query(query, conn)

# ------------------ Navigation ------------------
page = st.sidebar.selectbox("📁 Select Page", [
    "Overview", "Visualizations", "Prediction",
    "Inventory Forecast", "Campaign Recommendations", "Model Retraining"
])

# ------------------ Overview ------------------
if page == "Overview":
    st.title("📊 Intelligent Business Dashboard")
    st.markdown(f"📁 **Current Mode:** `{db_mode}`")

    try:
        sales = get_summary("SELECT SUM(unit_price * quantity) AS total_sales FROM sales")
        cust = get_summary("SELECT COUNT(DISTINCT customer_id) AS total_customers FROM customers")
        inv = get_summary("SELECT SUM(quantity_available) AS inventory_count FROM inventory")

        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Total Sales", f"${sales.iloc[0,0]:,.2f}")
        col2.metric("👥 Total Customers", f"{cust.iloc[0,0]:,}")
        col3.metric("📦 Inventory Items", f"{inv.iloc[0,0]:,}")
    except Exception as e:
        st.warning(f"⚠️ Could not load summary metrics: {e}")

    st.markdown("### 📄 Sample Data")
    for label, table in [("🧾 Sales", "sales"), ("📢 Marketing", "marketing"), ("🌐 Website Analytics", "website_analytics")]:
        with st.expander(label):
            try:
                st.dataframe(get_summary(f"SELECT * FROM {table} LIMIT 10"))
            except:
                st.info(f"{table.title()} data not available.")

# ------------------ Visualizations ------------------
elif page == "Visualizations":
    st.title("📈 Dashboard Visualizations")
    st.sidebar.markdown("### 📅 Filter by Date")
    start_date = pd.to_datetime(st.sidebar.text_input("Start Date", "2022/01/01"))
    end_date = pd.to_datetime(st.sidebar.text_input("End Date", "2025/05/24"))

    vis_queries = {
        "📉 Sales Trend Over Time": "SELECT order_date, revenue FROM sales",
        "📊 ROI by Marketing Channel": "SELECT channel, roi FROM marketing",
        "🛍️ Sales by Product Category": "SELECT product_category, SUM(revenue) as total_revenue FROM sales GROUP BY product_category",
        "🌍 Sales by Region": "SELECT location, SUM(revenue) as total_revenue FROM sales GROUP BY location",
        "🧑‍🤝‍🧑 Customer Segment Distribution": "SELECT customer_segment, COUNT(*) as count FROM sales GROUP BY customer_segment",
        "🧾 Top 10 Best-Selling Products": "SELECT product_name, SUM(quantity) as total_quantity FROM sales GROUP BY product_name ORDER BY total_quantity DESC LIMIT 10",
        "🌐 Website Traffic Trends": "SELECT session_date, session_id FROM website_analytics",
        "🎯 Campaign Performance Comparison": "SELECT campaign_id, ROUND(AVG(roi), 2) as avg_roi FROM marketing GROUP BY campaign_id ORDER BY avg_roi DESC LIMIT 10"
    }

    for title, query in vis_queries.items():
        with st.expander(title):
            try:
                df = get_summary(query)
                if "order_date" in df.columns:
                    df["order_date"] = pd.to_datetime(df["order_date"])
                    df = df[(df["order_date"] >= start_date) & (df["order_date"] <= end_date)]
                    df_grouped = df.groupby("order_date")["revenue"].sum().reset_index()
                    st.plotly_chart(px.line(df_grouped, x="order_date", y="revenue", title=title), use_container_width=True)
                elif "session_date" in df.columns:
                    df["session_date"] = pd.to_datetime(df["session_date"])
                    df = df[(df["session_date"] >= start_date) & (df["session_date"] <= end_date)]
                    df_count = df.groupby("session_date").count().reset_index().rename(columns={"session_id": "sessions"})
                    st.plotly_chart(px.line(df_count, x="session_date", y="sessions", title=title), use_container_width=True)
                elif "roi" in df.columns and "channel" in df.columns:
                    df_group = df.groupby("channel")["roi"].mean().reset_index()
                    st.plotly_chart(px.bar(df_group, x="channel", y="roi", title=title), use_container_width=True)
                elif "total_revenue" in df.columns:
                    st.plotly_chart(px.bar(df, x=df.columns[0], y="total_revenue", title=title), use_container_width=True)
                elif "count" in df.columns:
                    st.plotly_chart(px.pie(df, names=df.columns[0], values="count", title=title), use_container_width=True)
                elif "total_quantity" in df.columns:
                    st.plotly_chart(px.bar(df, x=df.columns[0], y="total_quantity", title=title), use_container_width=True)
                elif "avg_roi" in df.columns:
                    st.plotly_chart(px.bar(df, x="campaign_id", y="avg_roi", title=title), use_container_width=True)
            except Exception as e:
                st.warning(f"{title} error: {e}")

# ------------------ Prediction ------------------
elif page == "Prediction":
    st.title("🔮 Prediction Center")

    # Revenue Prediction
    with st.form("revenue_form"):
        st.subheader("💰 Revenue Prediction")
        pc = st.selectbox("Product Category", ['Electronics', 'Groceries', 'Clothing', 'Beauty', 'Home'])
        up = st.number_input("Unit Price", value=100.0)
        qty = st.number_input("Quantity", value=1)
        disc = st.number_input("Discount (%)", value=0.0)
        month = st.selectbox("Month", list(range(1, 13)))
        day = st.selectbox("Day", list(range(1, 32)))
        weekday = st.selectbox("Weekday", list(range(7)))
        if st.form_submit_button("Predict Revenue"):
            try:
                model = joblib.load("models/sales_model.pkl")
                encoder = joblib.load("models/sales_encoder.pkl")
                df = pd.DataFrame([{
                    "product_category": pc, "unit_price": up, "quantity": qty,
                    "discount_(%)": disc, "month": month, "day": day, "weekday": weekday
                }])
                encoded = encoder.transform(df[["product_category"]])
                final_input = np.hstack((encoded, df.drop(columns=["product_category"])))
                pred = model.predict(final_input)[0]
                st.success(f"Predicted Revenue: ${pred:,.2f}")
            except Exception as e:
                st.error(f"Prediction failed: {e}")

    # Churn Prediction
    st.markdown("---")
    with st.form("churn_form"):
        st.subheader("🚨 Customer Churn Prediction")
        g = st.selectbox("Gender", ["Male", "Female"])
        c = st.selectbox("Country", ["India", "USA", "UK", "Germany"])
        seg = st.selectbox("Segment", ["Premium", "Regular", "New"])
        dob = st.date_input("Date of Birth")
        reg = st.date_input("Registration Date")
        if st.form_submit_button("Predict Churn"):
            try:
                age = (datetime.now().date() - dob).days // 365
                tenure = (datetime.now().date() - reg).days // 30
                df = pd.DataFrame([{
                    "gender": g, "country": c, "customer_segment": seg, "age": age, "tenure": tenure
                }])
                model = joblib.load("models/churn_model.pkl")
                enc = joblib.load("models/churn_encoder.pkl")
                features = joblib.load("models/churn_feature_names.pkl")
                encoded = enc.transform(df[["gender", "country", "customer_segment"]])
                df_encoded = pd.DataFrame(encoded, columns=enc.get_feature_names_out())
                final_df = pd.concat([df_encoded, df[["age", "tenure"]].reset_index(drop=True)], axis=1)
                final_df = final_df.reindex(columns=features, fill_value=0)
                pred = model.predict(final_df.values)[0]
                if pred == 1:
                    st.warning("⚠️ This customer is likely to churn.")
                else:
                    st.success("✅ Customer retention likely.")
            except Exception as e:
                st.error(f"Churn prediction error: {e}")

# ------------------ Inventory Forecast ------------------
elif page == "Inventory Forecast":
    st.title("📦 Inventory Demand Forecasting")
    try:
        product_list = joblib.load("models/inventory_forecast_products.pkl")
        prod = st.selectbox("Select Product", product_list)
        days = st.slider("Forecast Days", 30, 180, 90)
        if st.button("Generate Forecast"):
            model_path = f"models/prophet_{prod.replace(' ', '_').replace('/', '_')}.pkl"
            model = joblib.load(model_path)
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            fig = px.line(forecast, x="ds", y="yhat", title=f"{prod} Forecast")
            fig.add_scatter(x=forecast["ds"], y=forecast["yhat_upper"], mode="lines", name="Upper Bound")
            fig.add_scatter(x=forecast["ds"], y=forecast["yhat_lower"], mode="lines", name="Lower Bound")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Forecast error: {e}")

# ------------------ Campaign Recommendations ------------------
elif page == "Campaign Recommendations":
    st.title("💌 Campaign Recommendation Engine")
    try:
        df = get_summary("SELECT channel, AVG(roi) as avg_roi FROM marketing GROUP BY channel ORDER BY avg_roi DESC")
        st.dataframe(df)
        best = df.iloc[0]
        st.success(f"Based on past ROI, the best-performing channel is *{best['channel']}* with ROI {best['avg_roi']:.2f}")
    except Exception as e:
        st.error(f"Recommendation error: {e}")

# ------------------ Model Retraining ------------------
elif page == "Model Retraining":
    st.title("🔄 Model Retraining Interface")
    st.info("Click the button to retrain both models.")
    if st.button("Retrain All Models"):
        try:
            os.system("python models/train_sales_model.py")
            os.system("python models/train_churn_model.py")
            st.success("✅ Models retrained successfully.")
        except Exception as e:
            st.error(f"Retraining failed: {e}")
