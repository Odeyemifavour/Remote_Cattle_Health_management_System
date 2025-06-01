<template>
    <div class="card">
        <h2 class="card-title">Alerts & Notifications</h2>
        <div v-if="store.loading" class="message-center">Loading alerts...</div>
        <div v-else-if="store.error" class="error-message">
            <span>{{ store.error }}</span>
        </div>
        <div v-else-if="store.activeAlerts.length === 0" class="message-center">
            No active alerts at the moment.
        </div>
        <div v-else class="space-y-4">
            <div v-for="alert in store.activeAlerts" :key="alert.id"
                 :class="['alert-card', alert.severity.toLowerCase().replace(' ', '')]">
                <p class="font-semibold text-lg mb-1">Cattle ID: <span class="font-bold">{{ alert.cattleId }}</span></p>
                <p class="text-sm text-gray-700 mb-2">Time: {{ alert.timestamp }}</p>
                <p class="text-md font-medium" :class="getAlertTextClass(alert.severity)">
                    {{ alert.message }}
                </p>
                <p class="text-sm text-gray-600 mt-1">Severity: <span :class="getAlertTextClass(alert.severity)">{{ alert.severity }}</span></p>
                <p v-if="alert.disease" class="text-sm text-gray-600">Detected Disease: {{ alert.disease }}</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { store } from '../../main.js';

const getAlertCardClass = (severity) => {
    return severity.toLowerCase().replace(' ', '');
};
const getAlertTextClass = (severity) => {
    return `text-${severity.toLowerCase().replace(' ', '-')}`;
};
</script>

<style scoped>
/* Alert Card Styles */
.alert-card {
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-left: 6px solid;
    margin-bottom: 20px;
    transition: transform 0.2s ease;
}
.alert-card:hover {
    transform: translateY(-3px);
}

/* Alert Card Colors based on severity */
.alert-card.critical { background-color: var(--alert-critical-bg); border-color: var(--alert-critical-border); }
.alert-card.high { background-color: var(--alert-high-bg); border-color: var(--alert-high-border); }
.alert-card.medium { background-color: var(--alert-medium-bg); border-color: var(--alert-medium-border); }
.alert-card.low-medium { background-color: var(--alert-low-medium-bg); border-color: var(--alert-low-medium-border); }
.alert-card.low { background-color: var(--alert-low-bg); border-color: var(--alert-low-border); }

.alert-card p {
    margin-bottom: 5px;
}
.alert-card .font-semibold { font-weight: 600; color: var(--text-dark); }
.alert-card .font-bold { font-weight: 700; color: var(--text-dark); }
.alert-card .text-sm { font-size: 0.9em; color: var(--text-secondary); }
.alert-card .text-md { font-size: 1.05em; }
</style>
