import pandas as pd
import sqlite3
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report

# Connect to the database
conn = sqlite3.connect("database.db")

# Load customer data
df = pd.read_sql_query("SELECT gender, country, customer_segment, dob, registration_date FROM customers", conn)
conn.close()

# Create synthetic 'churned' label for testing
import numpy as np
np.random.seed(42)
df['churned'] = np.random.choice([0, 1], size=len(df))

# Calculate age and tenure
df['dob'] = pd.to_datetime(df['dob'], errors='coerce')
df['registration_date'] = pd.to_datetime(df['registration_date'], errors='coerce')
df['age'] = (pd.Timestamp.now() - df['dob']).dt.days // 365
df['tenure'] = (pd.Timestamp.now() - df['registration_date']).dt.days // 30
df.dropna(subset=['age', 'tenure'], inplace=True)

# Features
categorical = ['gender', 'country', 'customer_segment']
numeric = ['age', 'tenure']
target = 'churned'

X = df[categorical + numeric]
y = df[target]

# One-hot encode categorical features
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = encoder.fit_transform(X[categorical])
X_encoded_df = pd.DataFrame(X_encoded, columns=encoder.get_feature_names_out(categorical))

# Combine encoded categorical and numeric features
X_final = pd.concat([X_encoded_df, X[numeric].reset_index(drop=True)], axis=1)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_final, y)

# Save model, encoder, and feature names
joblib.dump(model, "models/churn_model.pkl")
joblib.dump(encoder, "models/churn_encoder.pkl")
joblib.dump(list(X_final.columns), "models/churn_feature_names.pkl")

# Print evaluation
y_pred = model.predict(X_final)
print("✅ Model trained. Evaluation Report:")
print(classification_report(y, y_pred))
print("✅ Churn model and encoder saved to 'models/' folder.")
