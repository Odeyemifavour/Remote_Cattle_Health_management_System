<template>
    <div class="content-area">
        <div class="card">
            <h2 class="card-title">Cattle Health Prediction</h2>
            <p>Input the cattle's physiological data to get a health prediction and alerts from the AI model.</p>

            <!-- Loading & Error Messages -->
            <div v-if="loading" class="message-center loading-message">
                <p>Predicting health... Please wait.</p>
            </div>
            <div v-if="error" class="error-message">
                <p><strong>Prediction Error:</strong> {{ error }}</p>
                <p>Please check your network connection and ensure the Flask API is running.</p>
            </div>

            <!-- Input Form -->
            <form @submit.prevent="submitPrediction" class="prediction-form">
                <div class="form-grid">
                    <!-- Text Inputs -->
                    <div class="form-group">
                        <label for="cattleId">Cattle ID:</label>
                        <input type="text" id="cattleId" v-model="formData.cattle_id" required />
                    </div>
                    <div class="form-group">
                        <label for="bodyTemperature">Body Temperature (°C):</label>
                        <input type="number" id="bodyTemperature" v-model.number="formData.body_temperature" step="0.1" required />
                    </div>
                    <div class="form-group">
                        <label for="milkProduction">Milk Production (L/day):</label>
                        <input type="number" id="milkProduction" v-model.number="formData.milk_production" step="0.1" required />
                    </div>
                    <div class="form-group">
                        <label for="respiratoryRate">Respiratory Rate (breaths/min):</label>
                        <input type="number" id="respiratoryRate" v-model.number="formData.respiratory_rate" required />
                    </div>
                    <div class="form-group">
                        <label for="walkingCapacity">Walking Capacity (steps/day):</label>
                        <input type="number" id="walkingCapacity" v-model.number="formData.walking_capacity" required />
                    </div>
                    <div class="form-group">
                        <label for="sleepingDuration">Sleeping Duration (hours):</label>
                        <input type="number" id="sleepingDuration" v-model.number="formData.sleeping_duration" step="0.1" required />
                    </div>
                    <div class="form-group">
                        <label for="bodyConditionScore">Body Condition Score (1-5):</label>
                        <input type="number" id="bodyConditionScore" v-model.number="formData.body_condition_score" min="1" max="5" required />
                    </div>
                    <div class="form-group">
                        <label for="heartRate">Heart Rate (bpm):</label>
                        <input type="number" id="heartRate" v-model.number="formData.heart_rate" required />
                    </div>
                    <div class="form-group">
                        <label for="eatingDuration">Eating Duration (hours):</label>
                        <input type="number" id="eatingDuration" v-model.number="formData.eating_duration" step="0.1" required />
                    </div>
                    <div class="form-group">
                        <label for="lyingDownDuration">Lying Down Duration (hours):</label>
                        <input type="number" id="lyingDownDuration" v-model.number="formData.lying_down_duration" step="0.1" required />
                    </div>
                    <div class="form-group">
                        <label for="ruminating">Ruminating (hours):</label>
                        <input type="number" id="ruminating" v-model.number="formData.ruminating" step="0.1" required />
                    </div>
                    <div class="form-group">
                        <label for="rumenFill">Rumen Fill (1-5):</label>
                        <input type="number" id="rumenFill" v-model.number="formData.rumen_fill" min="1" max="5" required />
                    </div>

                    <!-- Select Inputs -->
                    <div class="form-group">
                        <label for="breedType">Breed Type:</label>
                        <select id="breedType" v-model="formData.breed_type" required>
                            <option value="">Select Breed</option>
                            <option value="Cross Breed">Cross Breed</option>
                            <option value="Normal Breed">Normal Breed</option>
                            <option value="Holstein">Holstein</option>
                            <option value="Indigenous Breed">Indigenous Breed</option>
                            <!-- Add other breeds as per your training data if necessary -->
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="faecalConsistency">Faecal Consistency:</label>
                        <select id="faecalConsistency" v-model="formData.faecal_consistency" required>
                            <option value="">Select Consistency</option>
                            <option value="ideal">Ideal</option>
                            <option value="extremely firm">Extremely Firm</option>
                            <option value="Black faeces">Black Faeces</option>
                            <option value="Fresh blood in faeces">Fresh Blood in Faeces</option>
                            <option value="very liquid faeces">Very Liquid Faeces</option>
                            <option value="Black faece">Black Faeces (Alternative)</option>
                            <!-- Add other consistencies as per your training data -->
                        </select>
                    </div>
                </div>

                <button type="submit" :disabled="loading" class="submit-button">
                    {{ loading ? 'Predicting...' : 'Get Prediction' }}
                </button>
            </form>
        </div>

        <!-- Prediction Results Display -->
        <div v-if="predictionResult" class="card prediction-results">
            <h3 class="card-title">Prediction Results for {{ predictionResult.cattle_id }}</h3>

            <div class="result-section">
                <h4>Monitoring Results:</h4>
                <p><strong>Health Status:</strong>
                    <span :class="getHealthStatusClass(predictionResult.monitoring_results.health_status)">
                        {{ predictionResult.monitoring_results.health_status }}
                    </span>
                </p>
                <p><strong>Confidence:</strong> {{ predictionResult.monitoring_results.confidence }}</p>
                <p><strong>Risk Level:</strong>
                    <span :class="getRiskLevelClass(predictionResult.monitoring_results.risk_level)">
                        {{ predictionResult.monitoring_results.risk_level }}
                    </span>
                </p>
                <p><strong>Timestamp:</strong> {{ predictionResult.timestamp }}</p>
            </div>

            <div v-if="predictionResult.ml_predictions_detail" class="result-section">
                <h4>ML Predictions Detail:</h4>
                <p><strong>Predicted Class:</strong> {{ predictionResult.ml_predictions_detail.predicted_class }}</p>
                <p><strong>Prediction Probabilities:</strong></p>
                <ul>
                    <li v-for="(prob, class_name) in predictionResult.ml_predictions_detail.prediction_probabilities" :key="class_name">
                        {{ class_name }}: {{ prob }}%
                    </li>
                </ul>
            </div>

            <div v-if="predictionResult.specific_diseases_detected && predictionResult.specific_diseases_detected.length > 0" class="result-section">
                <h4>Specific Diseases Detected (Rule-Based):</h4>
                <ul>
                    <li v-for="disease in predictionResult.specific_diseases_detected" :key="disease">{{ disease }}</li>
                </ul>
            </div>

            <div v-if="predictionResult.alerts && predictionResult.alerts.length > 0" class="result-section">
                <h4>Active Alerts:</h4>
                <div v-for="alert in predictionResult.alerts" :key="alert.message" :class="getAlertClass(alert.severity)">
                    <p><strong>Severity:</strong> {{ alert.severity }}</p>
                    <p><strong>Message:</strong> {{ alert.message }}</p>
                    <p v-if="alert.indicator"><strong>Indicator:</strong> {{ alert.indicator }}</p>
                    <p v-if="alert.value"><strong>Value:</strong> {{ alert.value }}</p>
                </div>
            </div>

            <div class="result-section">
                <h4>Input Data Snapshot:</h4>
                <pre>{{ JSON.stringify(predictionResult.input_data_snapshot, null, 2) }}</pre>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { store } from '../main.js'; // Assuming store is exported from main.js

// Initialize form data with default or empty values
const formData = reactive({
    cattle_id: '',
    body_temperature: null,
    breed_type: '',
    milk_production: null,
    respiratory_rate: null,
    walking_capacity: null,
    sleeping_duration: null,
    body_condition_score: null,
    heart_rate: null,
    eating_duration: null,
    lying_down_duration: null,
    ruminating: null,
    rumen_fill: null,
    faecal_consistency: '',
});

const predictionResult = ref(null);
const loading = ref(false);
const error = ref(null);

// Function to send data to Flask API
const submitPrediction = async () => {
    loading.value = true;
    error.value = null;
    predictionResult.value = null; // Clear previous results

    try {
        const response = await fetch(store.flaskApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`API Error: ${response.status} - ${errorData.error || response.statusText}`);
        }

        const data = await response.json();
        predictionResult.value = data;
        console.log('Prediction successful:', data);

    } catch (e) {
        error.value = e.message;
        console.error('Error during prediction:', e);
    } finally {
        loading.value = false;
    }
};

// Helper function for dynamic health status class
const getHealthStatusClass = (status) => {
    switch (status.toLowerCase()) {
        case 'healthy': return 'status-healthy';
        case 'unhealthy': return 'status-unhealthy';
        default: return '';
    }
};

// Helper function for dynamic risk level class
const getRiskLevelClass = (risk) => {
    switch (risk.toLowerCase()) {
        case 'critical': return 'risk-critical';
        case 'high': return 'risk-high';
        case 'medium': return 'risk-medium';
        case 'low-medium': return 'risk-low-medium';
        case 'low': return 'risk-low';
        default: return '';
    }
};

// Helper function for dynamic alert severity class
const getAlertClass = (severity) => {
    switch (severity.toLowerCase()) {
        case 'critical': return 'alert-critical';
        case 'high': return 'alert-high';
        case 'medium': return 'alert-medium';
        case 'low-medium': return 'alert-low-medium';
        case 'low': return 'alert-low';
        default: return '';
    }
};
</script>

<style scoped>
/* Scoped styles for this component */
.prediction-form {
    background-color: var(--card-bg);
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    margin-bottom: 30px;
    border: 1px solid var(--border-color);
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px;
    margin-bottom: 30px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group label {
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-dark);
    font-size: 0.95em;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select {
    padding: 12px 15px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-size: 1em;
    color: var(--text-dark);
    background-color: var(--background-light);
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    outline: none;
}

.submit-button {
    display: block;
    width: 100%;
    padding: 15px 25px;
    background-color: var(--primary-color);
    color: var(--text-light);
    border: none;
    border-radius: 8px;
    font-size: 1.1em;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.submit-button:hover:not(:disabled) {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
}

.submit-button:disabled {
    background-color: #A5D6A7;
    cursor: not-allowed;
}

.loading-message {
    color: var(--primary-dark);
    font-style: italic;
    font-size: 1.1em;
    text-align: center;
    padding: 15px;
    border-radius: 8px;
    background-color: #E8F5E9;
    margin-bottom: 20px;
}

.prediction-results {
    padding-top: 20px; /* Add some padding above the results title */
}

.prediction-results .result-section {
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px dashed var(--border-color);
}

.prediction-results .result-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.prediction-results h4 {
    font-size: 1.3em;
    color: var(--primary-dark);
    margin-bottom: 15px;
    border-left: 4px solid var(--primary-color);
    padding-left: 15px;
}

.prediction-results p, .prediction-results ul {
    font-size: 1em;
    line-height: 1.6;
    color: var(--text-dark);
    margin-bottom: 8px;
}

.prediction-results ul {
    list-style-type: disc;
    padding-left: 25px;
}

.prediction-results pre {
    background-color: #eceff1;
    padding: 15px;
    border-radius: 8px;
    white-space: pre-wrap; /* Ensures long lines wrap */
    word-break: break-all; /* Breaks words if necessary */
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
    font-size: 0.9em;
    color: #37474F;
    border: 1px solid #CFD8DC;
}

/* Dynamic Text Colors for Status and Risk */
.status-healthy { color: var(--primary-color); font-weight: 700; }
.status-unhealthy { color: var(--alert-critical-border); font-weight: 700; }

.risk-critical { color: var(--alert-critical-text); font-weight: 700; }
.risk-high { color: var(--alert-high-text); font-weight: 700; }
.risk-medium { color: var(--alert-medium-text); font-weight: 700; }
.risk-low-medium { color: var(--alert-low-medium-text); font-weight: 700; }
.risk-low { color: var(--alert-low-text); font-weight: 700; }

/* Alert Box Styling */
.alert-critical {
    background-color: var(--alert-critical-bg);
    border: 1px solid var(--alert-critical-border);
    color: var(--alert-critical-text);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}
.alert-high {
    background-color: var(--alert-high-bg);
    border: 1px solid var(--alert-high-border);
    color: var(--alert-high-text);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}
.alert-medium {
    background-color: var(--alert-medium-bg);
    border: 1px solid var(--alert-medium-border);
    color: var(--alert-medium-text);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}
.alert-low-medium {
    background-color: var(--alert-low-medium-bg);
    border: 1px solid var(--alert-low-medium-border);
    color: var(--alert-low-medium-text);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}
.alert-low {
    background-color: var(--alert-low-bg);
    border: 1px solid var(--alert-low-border);
    color: var(--alert-low-text);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}

/* Responsive Grid for Form */
@media (max-width: 768px) {
    .form-grid {
        grid-template-columns: 1fr; /* Stack columns on smaller screens */
    }
}
</style>
