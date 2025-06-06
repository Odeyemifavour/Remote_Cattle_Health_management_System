<template>
    <div class="content-area">
        <h2 class="card-title" v-if="cattleId">Cattle Profile: {{ cattleId }}</h2>
        <h2 class="card-title" v-else>Cattle Profile (Select an ID)</h2>

        <div v-if="store.loading" class="message-center">
            <i class="fa-solid fa-spinner fa-spin fa-2x"></i> Loading cattle profile...
        </div>
        <div v-else-if="store.error" class="error-message">
            <i class="fa-solid fa-circle-exclamation mr-2"></i> <span>{{ store.error }}</span>
        </div>
        <div v-else>
            <div v-if="currentCattleData">
                <!-- Current Status Summary -->
                <div class="card mb-8">
                    <h3 class="card-title-small">Current Status Overview</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div class="summary-item">
                            <strong>Health Status:</strong>
                            <span :class="['status-badge', getStatusClass(currentCattleData.monitoring_results.health_status)]">
                                {{ currentCattleData.monitoring_results.health_status }}
                            </span>
                        </div>
                        <div class="summary-item">
                            <strong>Risk Level:</strong>
                            <span :class="['risk-badge', getRiskClass(currentCattleData.monitoring_results.risk_level)]">
                                {{ currentCattleData.monitoring_results.risk_level }}
                            </span>
                        </div>
                        <div class="summary-item">
                            <strong>Last Update:</strong> {{ formatTimestamp(currentCattleData.timestamp) }}
                        </div>
                        <div class="summary-item">
                            <strong>Breed:</strong> {{ currentCattleData.raw_data?.breed_type || 'N/A' }}
                        </div>
                        <div class="summary-item">
                            <strong>Body Temp:</strong> {{ currentCattleData.raw_data?.body_temperature || 'N/A' }}°C
                        </div>
                        <div class="summary-item">
                            <strong>Resp. Rate:</strong> {{ currentCattleData.raw_data?.respiratory_rate || 'N/A' }} bpm
                        </div>
                        <div class="summary-item">
                            <strong>Heart Rate:</strong> {{ currentCattleData.raw_data?.heart_rate || 'N/A' }} bpm
                        </div>
                        <div class="summary-item">
                            <strong>Milk Prod:</strong> {{ currentCattleData.raw_data?.milk_production || 'N/A' }} L/day
                        </div>
                        <div class="summary-item">
                            <strong>Diseases Detected:</strong> {{ currentCattleData.specific_diseases_detected?.length > 0 ? currentCattleData.specific_diseases_detected.join(', ') : 'None' }}
                        </div>
                    </div>
                </div>

                <!-- Historical Data Section -->
                <div class="card mb-8">
                    <h3 class="card-title-small">Full Prediction History</h3>
                    <div v-if="filteredCattleHistory.length > 0">
                        <PredictionResult v-for="entry in filteredCattleHistory" :key="entry.id" :data="entry" />
                    </div>
                    <p v-else class="message-center">No historical prediction data available for this cattle.</p>
                </div>

            </div>
            <div v-else-if="cattleId" class="message-center p-6">
                <i class="fa-solid fa-info-circle fa-2x mb-2 text-blue-500"></i>
                <p class="font-bold">Cattle ID "{{ cattleId }}" not found in records.</p>
                <p class="text-sm mt-2 text-gray-500">Please ensure the ID is correct or add data for this cattle.</p>
                <router-link to="/dashboard/herd-dashboard" class="action-button mt-4">
                    <i class="fa-solid fa-arrow-left mr-2"></i> Back to Herd Dashboard
                </router-link>
            </div>
            <div v-else class="message-center p-6">
                <i class="fa-solid fa-magnifying-glass fa-2x mb-2 text-gray-400"></i>
                <p class="font-bold">Select a Cattle ID to view its detailed profile.</p>
                <p class="text-sm mt-2 text-gray-500">You can do this from the Herd Dashboard.</p>
                 <router-link to="/dashboard/herd-dashboard" class="action-button mt-4">
                    <i class="fa-solid fa-list mr-2"></i> View Herd Dashboard
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { store } from '../main.js';
import PredictionResult from '../components/predictions/PredictionResult.vue'; // Adjust path if moved

// Get cattleId from route params
const route = useRoute();
const cattleId = computed(() => route.params.cattleId);

// Computed property to get all historical data for the specific cattle ID
const filteredCattleHistory = computed(() => {
    if (!cattleId.value) return [];
    // Filter store.cattleData for the current cattleId and sort chronologically
    return store.cattleData
        .filter(entry => entry.cattle_id === cattleId.value)
        .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
});

// Computed property to get the latest data for the current cattle
const currentCattleData = computed(() => {
    if (!cattleId.value || filteredCattleHistory.value.length === 0) return null;
    // The last entry in the sorted history is the most recent
    return filteredCattleHistory.value[filteredCattleHistory.value.length - 1];
});

// Utility to get status badge class
const getStatusClass = (status) => {
    return status.toLowerCase() === 'unhealthy' ? 'status-unhealthy' : 'status-healthy';
};

// Utility to get risk badge class
const getRiskClass = (risk) => {
    return `risk-${risk.toLowerCase().replace(' ', '-')}`;
};

// Formats timestamp for display
const formatTimestamp = (timestampString) => {
    if (!timestampString) return 'N/A';
    const date = new Date(timestampString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
};
</script>

<style scoped>
/* Reusing global styles for .card-title, .message-center, .card, .status-badge, .risk-badge */

.summary-item {
    font-size: 0.95em;
    color: var(--text-dark);
    line-height: 1.5;
    padding: 10px;
    background-color: var(--background-light);
    border-radius: 8px;
    border: 1px solid var(--border-color);
}
.summary-item strong {
    color: var(--text-dark);
    font-weight: 600;
    margin-right: 5px;
}

.summary-item .status-badge, .summary-item .risk-badge {
    margin-left: 0; /* Override default margin */
    margin-top: 5px;
    display: block; /* Make badges block for better layout in summary */
    width: fit-content;
    padding: 5px 10px;
}

.action-button {
    background-color: var(--primary-color);
    color: var(--text-light);
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1em;
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.2s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-top: 15px;
}
.action-button:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
}
</style>
