<template>
    <div class="card">
        <h2 class="card-title">Add New Cattle Data</h2>
        <div v-if="store.error" class="error-message">
            <span>{{ store.error }}</span>
        </div>
        <div v-if="successMessage" class="success-message">
            <span>{{ successMessage }}</span>
        </div>

        <form @submit.prevent="submitData" class="form-grid">
            <div class="form-group">
                <label for="cattle_id">Cattle ID:</label>
                <input type="text" id="cattle_id" v-model="formData.cattle_id" required>
            </div>
            <div class="form-group">
                <label for="body_temperature">Body Temperature (°C):</label>
                <input type="number" step="0.1" id="body_temperature" v-model.number="formData.body_temperature" required>
            </div>
            <div class="form-group">
                <label for="breed_type">Breed Type:</label>
                <select id="breed_type" v-model="formData.breed_type" required>
                    <option value="Normal Breed">Normal Breed</option>
                    <option value="Cross Breed">Cross Breed</option>
                    <option value="Holstein">Holstein</option>
                    <option value="Jersey">Jersey</option>
                    <option value="Indigenous Breed">Indigenous Breed</option> <!-- Added this option -->
                    <option value="Other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label for="milk_production">Milk Production (L/day):</label>
                <input type="number" step="0.1" id="milk_production" v-model.number="formData.milk_production" required>
            </div>
            <div class="form-group">
                <label for="respiratory_rate">Respiratory Rate (breaths/min):</label>
                <input type="number" id="respiratory_rate" v-model.number="formData.respiratory_rate" required>
            </div>
            <div class="form-group">
                <label for="walking_capacity">Walking Capacity (steps/day):</label>
                <input type="number" id="walking_capacity" v-model.number="formData.walking_capacity" required>
            </div>
            <div class="form-group">
                <label for="sleeping_duration">Sleeping Duration (hours):</label>
                <input type="number" step="0.1" id="sleeping_duration" v-model.number="formData.sleeping_duration" required>
            </div>
            <div class="form-group">
                <label for="body_condition_score">Body Condition Score (1-5):</label>
                <input type="number" step="0.1" id="body_condition_score" v-model.number="formData.body_condition_score" required>
            </div>
            <div class="form-group">
                <label for="heart_rate">Heart Rate (bpm):</label>
                <input type="number" id="heart_rate" v-model.number="formData.heart_rate" required>
            </div>
            <div class="form-group">
                <label for="eating_duration">Eating Duration (hours):</label>
                <input type="number" step="0.1" id="eating_duration" v-model.number="formData.eating_duration" required>
            </div>
            <div class="form-group">
                <label for="lying_down_duration">Lying Down Duration (hours):</label>
                <input type="number" step="0.1" id="lying_down_duration" v-model.number="formData.lying_down_duration" required>
            </div>
            <div class="form-group">
                <label for="ruminating">Ruminating (hours):</label>
                <input type="number" step="0.1" id="ruminating" v-model.number="formData.ruminating" required>
            </div>
            <div class="form-group">
                <label for="rumen_fill">Rumen Fill (1-5):</label>
                <input type="number" id="rumen_fill" v-model.number="formData.rumen_fill" required>
            </div>
            <div class="form-group">
                <label for="faecal_consistency">Faecal Consistency:</label>
                <select id="faecal_consistency" v-model="formData.faecal_consistency" required>
                    <option value="ideal">ideal</option>
                    <option value="watery">watery</option>
                    <option value="Black faece">Black faece</option>
                    <option value="extremely firm">extremely firm</option>
                    <option value="firm">firm</option>
                    <option value="Fresh blood in faeces">Fresh blood in faeces</option> <!-- Added this option -->
                    <option value="very liquid faeces">very liquid faeces</option> <!-- Added this option -->
                </select>
            </div>

            <div class="form-group full-width-button">
                <button type="submit" :disabled="store.loading" class="form-submit-button">
                    {{ store.loading ? 'Processing...' : 'Submit Data' }}
                </button>
            </div>
        </form>
    </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { store } from '../../main.js'; // Ensure this path is correct
// Removed direct Firestore import as saving is now handled by Flask API,
// but leaving it commented out for context if needed for other operations
// import { doc, setDoc } from 'firebase/firestore'; 

const formData = reactive({
    cattle_id: '',
    body_temperature: null, breed_type: 'Normal Breed', milk_production: null,
    respiratory_rate: null, walking_capacity: null, sleeping_duration: null,
    body_condition_score: null, heart_rate: null, eating_duration: null,
    lying_down_duration: null, ruminating: null, rumen_fill: null,
    faecal_consistency: 'ideal',
});
const successMessage = ref('');

const submitData = async () => {
    store.loading = true;
    store.error = null;
    successMessage.value = '';

    if (!store.userId) {
        store.error = "Authentication not ready. Please wait or refresh. User ID missing.";
        store.loading = false;
        return;
    }

    try {
        // Prepare data for Flask API
        const dataToSend = { ...formData };

        const response = await fetch(store.flaskApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': store.userId // Pass userId from store to Flask API
            },
            body: JSON.stringify(dataToSend),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to get prediction from Flask API: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('Prediction Result from Flask (and saved to Firestore by Flask):', result);

        successMessage.value = `Data for Cattle ID "${result.cattle_id}" submitted and processed successfully!`;
        // Reset form after successful submission
        formData.cattle_id = '';
        formData.body_temperature = null;
        formData.breed_type = 'Normal Breed';
        formData.milk_production = null;
        formData.respiratory_rate = null;
        formData.walking_capacity = null;
        formData.sleeping_duration = null;
        formData.body_condition_score = null;
        formData.heart_rate = null;
        formData.eating_duration = null;
        formData.lying_down_duration = null;
        formData.ruminating = null;
        formData.rumen_fill = null;
        formData.faecal_consistency = 'ideal';

    } catch (error) {
        console.error('Error submitting data:', error);
        store.error = `Error: ${error.message}`;
    } finally {
        store.loading = false;
    }
};
</script>

<style scoped>
/* Form Styles */
.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px;
}

.form-group label {
    display: block;
    color: var(--text-dark);
    font-weight: 600;
    margin-bottom: 10px;
    font-size: 15px;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-sizing: border-box;
    font-size: 16px;
    color: var(--text-dark);
    background-color: var(--card-bg);
    transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.3);
}

.form-submit-button {
    background-color: var(--primary-color);
    color: var(--text-light);
    font-weight: bold;
    padding: 14px 30px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.25s ease, transform 0.1s ease, box-shadow 0.25s ease;
    width: auto;
    margin-top: 25px;
    font-size: 1.1em;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.form-submit-button:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

.form-submit-button:disabled {
    background-color: #B0BEC5;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
}

.full-width-button {
    grid-column: 1 / -1;
    display: flex;
    justify-content: flex-end;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .form-grid {
        grid-template-columns: 1fr;
    }
    .full-width-button {
        justify-content: center;
    }
}
</style>
