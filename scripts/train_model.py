import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import os
import seaborn as sns
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import json

# Load environment variables (if using .env file)
load_dotenv()

# MySQL Configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DATABASE', 'crop_recommendation'),
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"[v0] MySQL connection error: {e}")
        return None

def load_dataset_from_mysql():
    """Load the crop_yield table from MySQL into a DataFrame."""
    print("Loading dataset from MySQL...")
    conn = get_db_connection()
    if not conn:
        print("[v0] Could not connect to MySQL. Check MYSQL_HOST/USER/PASSWORD/DATABASE env vars.")
        return None
    try:
        query = """
            SELECT
                Crop,
                Crop_Year,
                Season,
                State,
                Area,
                Production,
                Annual_Rainfall,
                Fertilizer,
                Pesticide,
                yield_value
            FROM crop_yield
        """
        df = pd.read_sql(query, conn)
        numeric_columns = ['Area', 'Production', 'Annual_Rainfall', 'Fertilizer', 'Pesticide', 'yield_value']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['Crop', 'Season', 'State'])
        print(f"MySQL dataset loaded. Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"[v0] Error loading from MySQL: {e}")
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass

def preprocess_data(df):
    """Preprocess the dataset for training"""
    print("\nPreprocessing data...")
    data = df.copy().dropna()
    numeric_columns = ['Area', 'Production', 'Annual_Rainfall', 'Fertilizer', 'Pesticide', 'yield_value']
    for col in numeric_columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data = data.dropna()
    data['Fertilizer_per_Area'] = data['Fertilizer'] / (data['Area'] + 1)
    data['Pesticide_per_Area'] = data['Pesticide'] / (data['Area'] + 1)
    data['Production_per_Area'] = data['Production'] / (data['Area'] + 1)
    label_encoders = {}
    for col in ['Season', 'State']:
        le = LabelEncoder()
        data[f'{col}_encoded'] = le.fit_transform(data[col])
        label_encoders[col] = le
    print(f"Preprocessed data shape: {data.shape}")
    print(f"Number of unique crops: {data['Crop'].nunique()}")
    return data, label_encoders

def create_features_and_target(data):
    """Create feature matrix and target variable"""
    feature_columns = [
        'Season_encoded',
        'State_encoded',
        'Area',
        'Annual_Rainfall',
        'Fertilizer',
        'Pesticide',
        'Fertilizer_per_Area',
        'Pesticide_per_Area'
    ]
    X = data[feature_columns]
    le_crop = LabelEncoder()
    y = le_crop.fit_transform(data['Crop'])
    print(f"Features shape: {X.shape}, Target shape: {y.shape}")
    return X, y, le_crop, feature_columns

def train_model(X, y):
    """Train the Random Forest model with hyperparameter tuning"""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
    grid_search.fit(X_train_scaled, y_train)
    model = grid_search.best_estimator_
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model trained successfully with accuracy: {acc:.4f}")
    return model, scaler, X_test_scaled, y_test, y_pred

def evaluate_model(model, X_test, y_test, y_pred, le_crop):
    """Generate evaluation report"""
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le_crop.classes_))

    # Fix for feature_names_in_ error
    try:
        feature_names = model.feature_names_in_
    except AttributeError:
        # fallback if model was trained with NumPy arrays
        feature_names = [f"feature_{i}" for i in range(len(model.feature_importances_))]

    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    return feature_importance


def save_model_artifacts(model, scaler, le_crop, label_encoders, feature_columns, feature_importance):
    """Save model and related artifacts"""
    os.makedirs('models', exist_ok=True)
    pickle.dump(model, open('models/crop_recommendation_model.pkl', 'wb'))
    pickle.dump(scaler, open('models/scaler.pkl', 'wb'))
    pickle.dump(le_crop, open('models/crop_label_encoder.pkl', 'wb'))
    pickle.dump(label_encoders, open('models/label_encoders.pkl', 'wb'))
    pickle.dump(feature_columns, open('models/feature_columns.pkl', 'wb'))
    feature_importance.to_csv('models/feature_importance.csv', index=False)
    metadata = {
        'training_date': datetime.now().isoformat(),
        'model_type': 'RandomForestClassifier',
        'n_features': len(feature_columns),
        'n_crops': len(le_crop.classes_),
        'crops': le_crop.classes_.tolist()
    }
    json.dump(metadata, open('models/model_metadata.json', 'w'), indent=2)
    print("Model artifacts saved successfully in /models")

def main():
    print("="*50)
    print("TRAINING CROP RECOMMENDATION MODEL (MySQL Version)")
    print("="*50)
    df = load_dataset_from_mysql()
    if df is None or df.empty:
        print("Failed to load dataset from MySQL.")
        return
    data, label_encoders = preprocess_data(df)
    X, y, le_crop, feature_columns = create_features_and_target(data)
    model, scaler, X_test, y_test, y_pred = train_model(X, y)
    feature_importance = evaluate_model(model, X_test, y_test, y_pred, le_crop)
    save_model_artifacts(model, scaler, le_crop, label_encoders, feature_columns, feature_importance)
    print("\nTRAINING COMPLETE!")

if __name__ == "__main__":
    main()
