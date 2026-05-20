import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_squared_error

# Load the dataset
file_path = os.path.join("data", "sales_dataset_200k_updated.csv")
df = pd.read_csv(file_path)

# Rename columns for convenience (optional but clean)
df.rename(columns={
    'Order Date': 'order_date',
    'Product Category': 'product_category',
    'Unit Price': 'unit_price',
    'Quantity': 'quantity',
    'Discount (%)': 'discount',
    'Revenue': 'revenue'
}, inplace=True)

# Feature Engineering
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df = df.dropna(subset=['order_date'])  # Remove rows with invalid dates
df['month'] = df['order_date'].dt.month
df['day'] = df['order_date'].dt.day
df['weekday'] = df['order_date'].dt.weekday

# Select features and target
features = ['product_category', 'unit_price', 'quantity', 'discount', 'month', 'day', 'weekday']
target = 'revenue'

X = df[features]
y = df[target]

# One-hot encode categorical variable
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = encoder.fit_transform(X[['product_category']])

# Combine encoded and numerical features
X_numeric = X.drop(columns=['product_category']).values
X_final = np.hstack((X_encoded, X_numeric))

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_final, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"✅ Model trained. MSE on test set: {mse:.2f}")

# Save model and encoder
joblib.dump(model, "models/sales_model.pkl")
joblib.dump(encoder, "models/sales_encoder.pkl")
print("✅ Model and encoder saved to 'models/' folder.")
