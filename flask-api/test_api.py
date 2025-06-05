import requests
import json

# URL of your Flask API's predict endpoint
# Use 127.0.0.1 (localhost) if running on the same machine
api_url = "http://127.0.0.1:5000/predict"

# Sample data for an unhealthy cow (this should match the input features your model expects)
# Ensure all required features are present and their types match your model's expectation
unhealthy_cow_data = {
    'body_temperature': 40.2,
    'breed_type': 'Holstein', # Or 'Cross Breed', 'Normal Breed', etc., from your training data
    'milk_production': 9.5,
    'respiratory_rate': 45,
    'walking_capacity': 8500,
    'sleeping_duration': 5.1,
    'body_condition_score': 2,
    'heart_rate': 75,
    'eating_duration': 2.7,
    'lying_down_duration': 11.0,
    'ruminating': 4.5,
    'rumen_fill': 2,
    'faecal_consistency': 'Black faece', # Or 'ideal', 'extremely firm', etc., from your training data
    'cattle_id': 'TestCattle007' # Optional, for output identification
}

print("Sending data to API...")
print(json.dumps(unhealthy_cow_data, indent=4))

try:
    response = requests.post(api_url, json=unhealthy_cow_data)
    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

    # Parse and print the JSON response
    prediction_result = response.json()
    print("\nAPI Response (Prediction Result):")
    print(json.dumps(prediction_result, indent=4))

except requests.exceptions.RequestException as e:
    print(f"\nError connecting to the API or receiving response: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"API Response Content (if available): {e.response.text}")
except json.JSONDecodeError:
    print("\nError: Could not decode JSON from API response.")
    print(f"Raw API Response: {response.text}")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")