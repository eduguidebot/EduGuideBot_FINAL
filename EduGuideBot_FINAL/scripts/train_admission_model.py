# scripts/train_admission_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# --- Configuration ---
DATA_PATH = 'data/synthetic_admissions_data.csv'
MODEL_DIR = 'src/core/ml_models/'
MODEL_PATH = os.path.join(MODEL_DIR, 'admission_model.pkl')

def train_model():
    """
    Loads data, trains, evaluates, and saves the model artifact (model + columns).
    """
    print("--- Starting Model Training ---")
    
    # 1. Load Data
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"Successfully loaded dataset with {len(df)} records.")
    except FileNotFoundError:
        print(f"❌ ERROR: Data file not found at '{DATA_PATH}'. Please run the data generation script first.")
        return

    # 2. Feature Engineering
    print("Performing one-hot encoding on 'applied_major_category'...")
    df_encoded = pd.get_dummies(df, columns=['applied_major_category'], prefix='major')
    
    X = df_encoded.drop('admission_decision', axis=1)
    y = df_encoded['admission_decision']
    
    # 3. Split Data
    print("Splitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Train Model
    print("Training the Logistic Regression model...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    print("Model training complete.")
    
    # 5. Evaluate Model
    print("\n--- Evaluating Model Performance on Test Data ---")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Rejected (0)', 'Admitted (1)']))
    
    # 6. Save Model and Columns Together
    print("\n--- Saving Trained Model and Column Blueprint ---")
    model_artifact = {
        'model': model,
        'columns': list(X.columns)
    }
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model_artifact, MODEL_PATH)
    print(f"✅ Model artifact successfully saved to: {MODEL_PATH}")

if __name__ == '__main__':
    train_model()