<template>
    <div class="prediction-result-card card mb-4">
        <h3 class="card-title-small text-lg">Prediction Details ({{ formatTimestamp(data.timestamp) }})</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <p><strong>Cattle ID:</strong> {{ data.cattle_id }}</p>
                <p><strong>Health Status:</strong>
                    <span :class="['status-badge', getStatusClass(data.monitoring_results.health_status)]">
                        {{ data.monitoring_results.health_status }}
                    </span>
                </p>
                <p><strong>Risk Level:</strong>
                    <span :class="['risk-badge', getRiskClass(data.monitoring_results.risk_level)]">
                        {{ data.monitoring_results.risk_level }}
                    </span>
                </p>
                <p><strong>Confidence:</strong> {{ data.monitoring_results.confidence }}</p>
                <p v-if="data.specific_diseases_detected && data.specific_diseases_detected.length > 0">
                    <strong>Detected Diseases:</strong> {{ data.specific_diseases_detected.join(', ') }}
                </p>
                <p v-else><strong>Detected Diseases:</strong> None</p>
            </div>
            <div>
                <p><strong>Body Temp:</strong> {{ data.raw_data?.body_temperature }}°C</p>
                <p><strong>Respiratory Rate:</strong> {{ data.raw_data?.respiratory_rate }} breaths/min</p>
                <p><strong>Heart Rate:</strong> {{ data.raw_data?.heart_rate }} bpm</p>
                <p><strong>Milk Production:</strong> {{ data.raw_data?.milk_production }} L/day</p>
                <p><strong>Faecal Consistency:</strong> {{ data.raw_data?.faecal_consistency }}</p>
                <p><strong>Breed Type:</strong> {{ data.raw_data?.breed_type }}</p>
            </div>
        </div>

        <div v-if="data.alerts && data.alerts.length > 0" class="mt-4 border-t pt-4 border-dashed border-gray-300">
            <h4 class="font-semibold text-lg mb-2 text-gray-800">Associated Alerts:</h4>
            <ul class="alert-list-nested">
                <li v-for="alert in data.alerts" :key="alert.id || alert.message"
                    :class="['alert-item-nested', getAlertSeverityClass(alert.severity)]">
                    <i :class="getAlertIconClass(alert.severity)"></i>
                    <span>{{ alert.message }}</span>
                    <span class="text-sm italic ml-auto">(Severity: {{ alert.severity }})</span>
                </li>
            </ul>
        </div>
        <div v-else class="mt-4 text-center text-gray-500 italic">No specific alerts for this record.</div>
    </div>
</template>

<script setup>
import { computed } from 'vue';

// Define the prop that this component expects
const props = defineProps({
    data: {
        type: Object,
        required: true,
        // Add a more detailed validator if needed for production
        validator: (value) => {
            return value && value.cattle_id && value.monitoring_results;
        }
    }
});

// Utility to get status badge class (reusing global styles)
const getStatusClass = (status) => {
    return status.toLowerCase() === 'unhealthy' ? 'status-unhealthy' : 'status-healthy';
};

// Utility to get risk badge class (reusing global styles)
const getRiskClass = (risk) => {
    return `risk-${risk.toLowerCase().replace(' ', '-')}`;
};

// Utility for alert item nested styling
const getAlertSeverityClass = (severity) => {
    return `alert-${severity.toLowerCase().replace(' ', '-')}`;
};

// Utility for alert icon
const getAlertIconClass = (severity) => {
    switch (severity.toLowerCase()) {
        case 'critical': return 'fa-solid fa-circle-exclamation text-red-600';
        case 'high': return 'fa-solid fa-triangle-exclamation text-orange-600';
        case 'medium': return 'fa-solid fa-info-circle text-yellow-600';
        case 'low-medium': return 'fa-solid fa-bell text-blue-600';
        case 'low': return 'fa-solid fa-check-circle text-green-600';
        default: return 'fa-solid fa-bell text-gray-600';
    }
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
/* Scoped styles for PredictionResult component */

.prediction-result-card {
    /* Uses .card from global styles */
    padding: 25px; /* Adjust padding as needed */
    margin-bottom: 25px;
}

.prediction-result-card h3 {
    margin-top: 0;
    margin-bottom: 20px;
    color: var(--text-dark);
}

.prediction-result-card p {
    margin-bottom: 8px;
    font-size: 0.95em;
    color: var(--text-dark);
}
.prediction-result-card p strong {
    color: var(--text-dark);
    font-weight: 600;
    margin-right: 5px;
}

/* Reusing global badge styles */
.status-badge, .risk-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.7em;
    font-weight: 600;
    text-transform: uppercase;
    display: inline-block;
    margin-left: 5px;
    white-space: nowrap;
}
.status-healthy { background-color: var(--primary-color); color: var(--text-light); }
.status-unhealthy { background-color: var(--alert-critical-border); color: var(--text-light); }

.risk-badge.critical { background-color: var(--alert-critical-border); color: var(--text-light); }
.risk-badge.high { background-color: var(--alert-high-border); color: var(--text-light); }
.risk-badge.medium { background-color: var(--alert-medium-border); color: var(--text-dark); }
.risk-badge.low-medium { background-color: var(--alert-low-medium-border); color: var(--text-light); }
.risk-badge.low { background-color: var(--alert-low-border); color: var(--text-light); }


/* Nested Alert List Styling */
.alert-list-nested {
    list-style: none;
    padding: 0;
    margin: 0;
}

.alert-item-nested {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    margin-bottom: 5px;
    border-radius: 6px;
    font-size: 0.9em;
    border: 1px solid rgba(0,0,0,0.08); /* Light border */
    background-color: rgba(255,255,255,0.9); /* Slightly transparent white */
}
.alert-item-nested:last-child {
    margin-bottom: 0;
}

.alert-item-nested i {
    margin-right: 10px;
    font-size: 1.1em;
    flex-shrink: 0;
}
.alert-item-nested span {
    color: var(--text-dark);
}

/* Colors for nested alerts */
.alert-critical { background-color: var(--alert-critical-bg); border-color: var(--alert-critical-border); color: var(--alert-critical-text); }
.alert-high { background-color: var(--alert-high-bg); border-color: var(--alert-high-border); color: var(--alert-high-text); }
.alert-medium { background-color: var(--alert-medium-bg); border-color: var(--alert-medium-border); color: var(--alert-medium-text); }
.alert-low-medium { background-color: var(--alert-low-medium-bg); border-color: var(--alert-low-medium-border); color: var(--alert-low-medium-text); }
.alert-low { background-color: var(--alert-low-bg); border-color: var(--alert-low-border); color: var(--alert-low-text); }
.alert-item-nested.alert-critical i { color: var(--alert-critical-border); }
.alert-item-nested.alert-high i { color: var(--alert-high-border); }
.alert-item-nested.alert-medium i { color: var(--alert-medium-border); }
.alert-item-nested.alert-low-medium i { color: var(--alert-low-medium-border); }
.alert-item-nested.alert-low i { color: var(--alert-low-border); }


/* Responsive grid for details */
@media (max-width: 768px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
</style>
