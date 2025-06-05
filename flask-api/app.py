print("--- APP.PY EXECUTION STARTED ---")

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import datetime

# --- 1. Load the pre-trained model and preprocessing tools ---
try:
    model = joblib.load('model.joblib')
    scaler = joblib.load('scaler.joblib')
    le_health = joblib.load('le_health.joblib')
    le_breed = joblib.load('le_breed.joblib') # Load your breed LabelEncoder
    le_faecal = joblib.load('le_faecal.joblib') # Load your faecal consistency LabelEncoder
    print("Model, Scaler, and LabelEncoders loaded successfully!")
except FileNotFoundError as e:
    print(f"Error loading a required file: {e}. Make sure all .joblib files are in the same directory.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred during loading: {e}")
    exit()

# --- IMPORTANT: Define the EXACT feature order from your training ---
# This list comes directly from your training script's output!
training_features_for_model = [
    'body_temperature', 'breed_type_enc', 'milk_production', 'respiratory_rate',
    'walking_capacity', 'sleeping_duration', 'body_condition_score', 'heart_rate',
    'eating_duration', 'lying_down_duration', 'ruminating', 'rumen_fill',
    'faecal_consistency_enc', 'activity_ratio', 'eating_efficiency', 'vital_sign_index'
]

# --- Define the original categorical columns that need Label Encoding ---
original_categorical_cols = ['breed_type', 'faecal_consistency']

# --- Helper Function for Rule-Based Alerts ---
# Make sure this function matches the one in your training environment.
def get_rule_based_alerts(data):
    detected_diseases = []
    alerts = []
    abnormal_count = 0

    # Example rules (replace with your actual rules)
    if data.get('body_temperature') > 39.5:
        alerts.append({"indicator": "Body Temperature", "value": data['body_temperature'], "threshold": ">39.5", "severity": "High", "message": "High body temperature detected."})
        abnormal_count += 1
    if data.get('respiratory_rate') > 40:
        alerts.append({"indicator": "Respiratory Rate", "value": data['respiratory_rate'], "threshold": ">40", "severity": "Medium", "message": "Elevated respiratory rate."})
        abnormal_count += 1
    if data.get('faecal_consistency') in ['watery', 'Black faece']:
        alerts.append({"indicator": "Faecal Consistency", "value": data['faecal_consistency'], "threshold": "watery/Black faece", "severity": "High", "message": "Abnormal faecal consistency."})
        abnormal_count += 1
        detected_diseases.append("Diarrhea")

    # Example for Mastitis (hypothetical combined indicators)
    if data.get('body_temperature') > 39.0 and data.get('milk_production') < 10:
        if "Mastitis" not in detected_diseases:
            detected_diseases.append("Mastitis")
        alerts.append({"indicator": "Mastitis Indicators", "value": "Combined", "threshold": "High temp & low milk", "severity": "Critical", "message": "Potential Mastitis based on combined indicators."})

    return detected_diseases, alerts, abnormal_count

# --- 2. Initialize Flask App ---
app = Flask(__name__)
CORS(app)

# --- 3. Define the /predict API endpoint ---
@app.route('/predict', methods=['POST'])
def predict():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print(f"Received data: {data}")

    required_input_features = [
        'body_temperature', 'breed_type', 'milk_production',
        'respiratory_rate', 'walking_capacity', 'sleeping_duration',
        'body_condition_score', 'heart_rate', 'eating_duration',
        'lying_down_duration', 'ruminating', 'rumen_fill', 'faecal_consistency'
    ]

    if not all(feature in data for feature in required_input_features):
        missing_features = [feature for feature in required_input_features if feature not in data]
        return jsonify({"error": "Missing features in input", "missing": missing_features}), 400

    input_df = pd.DataFrame([data])

    # --- Feature Engineering (MUST mirror training) ---
    epsilon = 1e-6
    input_df['activity_ratio'] = input_df['walking_capacity'] / (input_df['sleeping_duration'] + epsilon)
    input_df['eating_efficiency'] = input_df['milk_production'] / (input_df['eating_duration'] + epsilon)
    input_df['vital_sign_index'] = (input_df['heart_rate'] + input_df['respiratory_rate'] + input_df['body_temperature']) / 3

    # --- Categorical Encoding (MUST mirror training: Use LabelEncoder) ---
    # Handle 'breed_type'
    breed_type_val = input_df['breed_type'].iloc[0]
    if breed_type_val in le_breed.classes_:
        input_df['breed_type_enc'] = le_breed.transform([breed_type_val])[0]
    else:
        # Fallback: Use the encoding for the first class, or a pre-defined 'unknown' if you have one
        fallback_breed_type_idx = 0 # Index of the first class in le_breed.classes_
        print(f"Warning: Unseen breed_type '{breed_type_val}' in input. Encoding as '{le_breed.classes_[fallback_breed_type_idx]}' ({fallback_breed_type_idx}).")
        input_df['breed_type_enc'] = fallback_breed_type_idx # Assign the integer encoding

    # Handle 'faecal_consistency'
    faecal_consistency_val = input_df['faecal_consistency'].iloc[0]
    if faecal_consistency_val in le_faecal.classes_:
        input_df['faecal_consistency_enc'] = le_faecal.transform([faecal_consistency_val])[0]
    else:
        # Fallback: Use the encoding for the first class, or a pre-defined 'unknown' if you have one
        fallback_faecal_idx = 0 # Index of the first class in le_faecal.classes_
        print(f"Warning: Unseen faecal_consistency '{faecal_consistency_val}' in input. Encoding as '{le_faecal.classes_[fallback_faecal_idx]}' ({fallback_faecal_idx}).")
        input_df['faecal_consistency_enc'] = fallback_faecal_idx # Assign the integer encoding

    # Drop the original categorical columns now that they are encoded
    input_df = input_df.drop(columns=original_categorical_cols)

    # --- Prepare final DataFrame for model by selecting and ordering features ---
    # Create an empty DataFrame with the exact columns and order expected by the model
    final_input_df_for_model = pd.DataFrame(0, index=input_df.index, columns=training_features_for_model)

    # Populate it with the values from our processed input_df
    for col in training_features_for_model:
        if col in input_df.columns:
            final_input_df_for_model[col] = input_df[col]
        else:
            # This should ideally not happen if features are correctly handled,
            # but acts as a safeguard. Missing engineered features would be 0.
            print(f"Warning: Feature '{col}' not found in processed input_df. Using default 0.")

    # Ensure all columns are numeric before scaling
    for col in final_input_df_for_model.columns:
        final_input_df_for_model[col] = pd.to_numeric(final_input_df_for_model[col], errors='coerce')
        if final_input_df_for_model[col].isnull().any():
            print(f"Warning: NaN detected in numeric column {col}. Filling with 0.")
            final_input_df_for_model[col].fillna(0, inplace=True)

    # --- Scale features with the scaler fitted on training data ---
    # The scaler expects a NumPy array, but it will respect the order of columns if passed a DataFrame
    X_processed_scaled = scaler.transform(final_input_df_for_model)

    # Make prediction
    prediction = model.predict(X_processed_scaled)
    predicted_label_encoded = prediction[0]
    predicted_health_status = le_health.inverse_transform([predicted_label_encoded])[0]

    # Get prediction probabilities
    probabilities = model.predict_proba(X_processed_scaled)[0]
    confidence = max(probabilities) * 100
    probability_dict = {
        le_health.inverse_transform([i])[0]: round(probabilities[i]*100, 2)
        for i in range(len(le_health.classes_))
    }

    # --- Rule-Based Disease Detection and Alert Generation Part ---
    rule_based_diseases, structured_alerts_list, abnormal_indicator_count = get_rule_based_alerts(data)

    # --- Consolidate and Finalize Output for Dashboard ---
    overall_health_status = predicted_health_status.capitalize()
    overall_risk_level = "Low"

    if predicted_health_status.lower() == 'unhealthy':
        if confidence > 80:
            overall_risk_level = "High"
        elif confidence > 50:
            overall_risk_level = "Medium"
        else:
            overall_risk_level = "Low-Medium"
    else:
        overall_risk_level = "Low"

    if rule_based_diseases:
        if overall_risk_level == "Low" or overall_risk_level == "Low-Medium":
            for alert in structured_alerts_list:
                if alert.get('severity') == 'Critical':
                    overall_risk_level = "Critical"
                    break
                elif alert.get('severity') == 'High' and overall_risk_level != "Critical":
                    overall_risk_level = "High"
                elif overall_risk_level not in ["Critical", "High"]: # Only upgrade to Medium if not already Critical/High
                    if alert.get('severity') == 'Medium':
                        overall_risk_level = "Medium"

        overall_health_status = "Unhealthy"

    # Final structured output dictionary
    response = {
        "cattle_id": data.get('cattle_id', 'Unknown'),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring_results": {
            "health_status": overall_health_status,
            "confidence": f"{confidence:.2f}%",
            "risk_level": overall_risk_level
        },
        "ml_predictions_detail": {
            "predicted_class": predicted_health_status,
            "prediction_probabilities": probability_dict
        },
        "specific_diseases_detected": rule_based_diseases,
        "alerts": structured_alerts_list,
        "input_data_snapshot": data
    }

    return jsonify(response)

# --- 4. Run the Flask App ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)