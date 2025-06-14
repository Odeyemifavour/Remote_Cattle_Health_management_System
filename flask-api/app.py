# app.py (Your Flask application file)

print("--- APP.PY EXECUTION STARTED ---")

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import datetime
import os
from google.cloud import firestore

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
    exit() # Exit if models aren't loaded, as app won't function
except Exception as e:
    print(f"An unexpected error occurred during loading: {e}")
    exit() # Exit if models aren't loaded

# --- Initialize Firebase/Firestore ---
db = None # Initialize to None
try:
    db = firestore.Client()
    print("Firestore client initialized using default credentials.")
except Exception as e:
    print(f"Flask Warning: Failed to initialize Firestore client. Error: {e}")
    print("Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set for local runs.")


# --- IMPORTANT: Define the EXACT feature order from your training ---
training_features_for_model = [
    'body_temperature', 'breed_type_enc', 'milk_production', 'respiratory_rate',
    'walking_capacity', 'sleeping_duration', 'body_condition_score', 'heart_rate',
    'eating_duration', 'lying_down_duration', 'ruminating', 'rumen_fill',
    'faecal_consistency_enc', 'activity_ratio', 'eating_efficiency', 'vital_sign_index'
]

# --- Define the original categorical columns that need Label Encoding ---
original_categorical_cols = ['breed_type', 'faecal_consistency']

# --- Helper Function for Rule-Based Alerts ---
def get_rule_based_alerts(data):
    detected_diseases = []
    generated_alerts = []
    abnormal_indicator_count = 0

    THRESHOLDS = {
        'body_temperature_high_respiratory': 39.5,
        'respiratory_rate_high_respiratory': 40,
        'faecal_consistency_abnormal': ['watery', 'black faece', 'fresh blood in faeces', 'very liquid faeces'],
        'milk_production_low': 8.0,
        'body_condition_score_low_reproductive': 2.5,
        'heart_rate_high_reproductive': 80,
        'walking_capacity_low': 9000,
        'body_temperature_high_systemic': 39.8,
        'heart_rate_high_systemic': 80,
        'respiratory_rate_high_systemic': 42,
    }

    # Respiratory Disease
    if data.get('body_temperature', 0) > THRESHOLDS['body_temperature_high_respiratory'] and \
       data.get('respiratory_rate', 0) > THRESHOLDS['respiratory_rate_high_respiratory']:
        detected_diseases.append('Respiratory Disease')
        generated_alerts.append({
            'symptom': 'body_temperature',
            'value': data.get('body_temperature'),
            'message': f"High body temperature detected ({data.get('body_temperature')}°C)!",
            'severity': 'Medium',
            'rule_triggered': 'Respiratory_Temp'
        })
        generated_alerts.append({
            'symptom': 'respiratory_rate',
            'value': data.get('respiratory_rate'),
            'message': f"High respiratory rate detected ({data.get('respiratory_rate')} breaths/min)!",
            'severity': 'Medium',
            'rule_triggered': 'Respiratory_Rate'
        })
        abnormal_indicator_count += 2

    # GI Disease
    faecal_consistency = data.get('faecal_consistency', '').lower()
    if faecal_consistency in THRESHOLDS['faecal_consistency_abnormal']:
        detected_diseases.append('Gastrointestinal Disease')
        generated_alerts.append({
            'symptom': 'faecal_consistency',
            'value': data.get('faecal_consistency'),
            'message': f"Abnormal faecal consistency detected ({data.get('faecal_consistency')})!",
            'severity': 'High',
            'rule_triggered': 'GI_Feces'
        })
        abnormal_indicator_count += 1

    # Udder Health Issue
    if data.get('milk_production', 0) < THRESHOLDS['milk_production_low']:
        detected_diseases.append('Udder Health Issue')
        generated_alerts.append({
            'symptom': 'milk_production',
            'value': data.get('milk_production'),
            'message': f"Very low milk production detected ({data.get('milk_production')} L/day)!",
            'severity': 'Medium',
            'rule_triggered': 'Udder_MilkProd'
        })
        abnormal_indicator_count += 1

    # Reproductive Disease
    if data.get('body_condition_score', 0) < THRESHOLDS['body_condition_score_low_reproductive'] and \
       data.get('heart_rate', 0) > THRESHOLDS['heart_rate_high_reproductive']:
        detected_diseases.append('Reproductive Disease')
        generated_alerts.append({
            'symptom': 'body_condition_score',
            'value': data.get('body_condition_score'),
            'message': f"Low body condition score detected ({data.get('body_condition_score')})!",
            'severity': 'Medium',
            'rule_triggered': 'Reproductive_BCS'
        })
        generated_alerts.append({
            'symptom': 'heart_rate',
            'value': data.get('heart_rate'),
            'message': f"High heart rate detected ({data.get('heart_rate')} bpm)!",
            'severity': 'Medium',
            'rule_triggered': 'Reproductive_HR'
        })
        abnormal_indicator_count += 2

    # Musculoskeletal Issue
    if data.get('walking_capacity', 0) < THRESHOLDS['walking_capacity_low']:
        detected_diseases.append('Lameness / Musculoskeletal Issue')
        generated_alerts.append({
            'symptom': 'walking_capacity',
            'value': data.get('walking_capacity'),
            'message': f"Low walking capacity detected ({data.get('walking_capacity')} steps/day)!",
            'severity': 'High',
            'rule_triggered': 'Musculoskeletal_Walking'
        })
        abnormal_indicator_count += 1

    # Systemic Infection
    if data.get('body_temperature', 0) > THRESHOLDS['body_temperature_high_systemic'] and \
       data.get('heart_rate', 0) > THRESHOLDS['heart_rate_high_systemic'] and \
       data.get('respiratory_rate', 0) > THRESHOLDS['respiratory_rate_high_systemic']:
        detected_diseases.append('Systemic Infection')
        generated_alerts.append({
            'symptom': 'body_temperature',
            'value': data.get('body_temperature'),
            'message': f"Critically high body temperature detected ({data.get('body_temperature')}°C)!",
            'severity': 'Critical',
            'rule_triggered': 'Systemic_Temp'
        })
        generated_alerts.append({
            'symptom': 'heart_rate',
            'value': data.get('heart_rate'),
            'message': f"Critically high heart rate detected ({data.get('heart_rate')} bpm)!",
            'severity': 'Critical',
            'rule_triggered': 'Systemic_HR'
        })
        generated_alerts.append({
            'symptom': 'respiratory_rate',
            'value': data.get('respiratory_rate'),
            'message': f"Critically high respiratory rate detected ({data.get('respiratory_rate')} breaths/min)!",
            'severity': 'Critical',
            'rule_triggered': 'Systemic_RR'
        })
        abnormal_indicator_count += 3

    # Remove duplicate alert messages and sort by severity
    unique_alerts_by_message = {}
    for alert in generated_alerts:
        unique_alerts_by_message[alert['message']] = alert
    final_alerts_list = list(unique_alerts_by_message.values())

    severity_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
    final_alerts_list.sort(key=lambda x: severity_order.get(x.get('severity', 'Low'), 0), reverse=True)

    return list(set(detected_diseases)), final_alerts_list, abnormal_indicator_count


# --- 2. Initialize Flask App ---
app = Flask(__name__)
CORS(app)

# --- 3. Define the /predict API endpoint ---
@app.route('/predict', methods=['POST'])
def predict(): # REMOVED 'async'
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
        fallback_breed_type_idx = 0
        print(f"Warning: Unseen breed_type '{breed_type_val}' in input. Encoding as '{le_breed.classes_[fallback_breed_type_idx]}' ({fallback_breed_type_idx}).")
        input_df['breed_type_enc'] = fallback_breed_type_idx

    # Handle 'faecal_consistency'
    faecal_consistency_val = input_df['faecal_consistency'].iloc[0]
    if faecal_consistency_val in le_faecal.classes_:
        input_df['faecal_consistency_enc'] = le_faecal.transform([faecal_consistency_val])[0]
    else:
        fallback_faecal_idx = 0
        print(f"Warning: Unseen faecal_consistency '{faecal_consistency_val}' in input. Encoding as '{le_faecal.classes_[fallback_faecal_idx]}' ({fallback_faecal_idx}).")
        input_df['faecal_consistency_enc'] = fallback_faecal_idx

    # Drop the original categorical columns now that they are encoded
    input_df = input_df.drop(columns=original_categorical_cols)

    # --- Prepare final DataFrame for model by selecting and ordering features ---
    final_input_df_for_model = pd.DataFrame(0, index=input_df.index, columns=training_features_for_model)

    for col in training_features_for_model:
        if col in input_df.columns:
            final_input_df_for_model[col] = input_df[col]
        else:
            print(f"Warning: Feature '{col}' not found in processed input_df. Using default 0.")

    # Ensure all columns are numeric before scaling
    for col in final_input_df_for_model.columns:
        final_input_df_for_model[col] = pd.to_numeric(final_input_df_for_model[col], errors='coerce')
        if final_input_df_for_model[col].isnull().any():
            print(f"Warning: NaN detected in numeric column {col}. Filling with 0.")
            final_input_df_for_model[col].fillna(0, inplace=True)

    # --- Scale features with the scaler fitted on training data ---
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
                    overall_health_status = "Unhealthy" # If critical alert, always unhealthy
                    break
                elif alert.get('severity') == 'High' and overall_risk_level not in ["Critical"]:
                    overall_risk_level = "High"
                    if overall_health_status == "Healthy":
                        overall_health_status = "Unhealthy"
                elif overall_risk_level not in ["Critical", "High"]:
                    if alert.get('severity') == 'Medium':
                        overall_risk_level = "Medium"
                        if overall_health_status == "Healthy":
                            overall_health_status = "Observation"

    # Final structured output dictionary
    response_data = {
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
        "specific_diseases_detected": list(set(rule_based_diseases)), # Ensure unique diseases
        "alerts": structured_alerts_list,
        "input_data_snapshot": data
    }

    # --- Save to Firestore ---
    if db:
        try:
            user_id = request.headers.get('X-User-Id')
            if not user_id:
                print("Flask Warning: 'X-User-Id' header not found. Using 'anonymous_flask_user'.")
                user_id = 'anonymous_flask_user'
            
            app_id = os.environ.get('CANVAS_APP_ID', 'default_app_id_for_local') 

            if response_data.get('cattle_id'):
                doc_ref = db.collection(f'artifacts/{app_id}/users/{user_id}/cattle_data').document(response_data['cattle_id'])
                doc_ref.set(response_data) # REMOVED 'await'
                print(f"Flask: Data for Cattle ID {response_data['cattle_id']} saved to Firestore successfully for user {user_id}.")
            else:
                print("Flask Warning: cattle_id missing in response_data, skipping Firestore save.")
        except Exception as firestore_e:
            print(f"Flask ERROR: Failed to save data to Firestore: {firestore_e}")
    else:
        print("Flask: Firestore client not initialized, skipping database save.")

    return jsonify(response_data)

# --- 4. Run the Flask App ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
