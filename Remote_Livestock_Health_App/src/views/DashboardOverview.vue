<template>
    <div class="card">
        <h2 class="card-title">Dashboard Overview</h2>
        <div v-if="store.loading" class="message-center">Loading cattle data...</div>
        <div v-else-if="store.error" class="error-message">
            <span>{{ store.error }}</span>
        </div>
        <div v-else-if="filteredCattle.length === 0" class="message-center">
            No cattle data available. Add some data using the "Add Cattle Data" section.
        </div>
        <div v-else class="cattle-grid">
            <div v-for="cattle in filteredCattle" :key="cattle.id"
                 :class="['cattle-card', getCardClass(cattle.monitoring_results.risk_level)]">
                <h3 class="text-lg font-semibold mb-1">{{ cattle.cattle_id }}</h3>
                <p class="text-sm text-gray-700 mb-1">Last Updated: {{ cattle.timestamp }}</p>
                <p class="text-md font-bold mb-1">Status: {{ cattle.monitoring_results.health_status }}</p>
                <p class="text-md font-bold mb-1">Risk: {{ cattle.monitoring_results.risk_level }}</p>
                <p class="text-sm text-gray-600">Confidence: {{ cattle.monitoring_results.confidence }}</p>
                <div v-if="cattle.alerts && cattle.alerts.length > 0" class="mt-2">
                    <h4 class="font-semibold text-gray-800">Active Alerts:</h4>
                    <ul class="list-disc list-inside text-sm text-gray-700">
                        <li v-for="(alert, index) in cattle.alerts.slice(0, 2)" :key="index" :class="getAlertTextClass(alert.severity)">
                            {{ alert.message }}
                        </li>
                        <li v-if="cattle.alerts.length > 2" class="text-gray-500">...and {{ cattle.alerts.length - 2 }} more.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { store } from '../main.js';

const getCardClass = (riskLevel) => {
    return `risk-${riskLevel.toLowerCase().replace(' ', '-')}`;
};

const getAlertTextClass = (severity) => {
    return `text-${severity.toLowerCase().replace(' ', '-')}`;
};

const filteredCattle = computed(() => {
    const latestCattle = {};
    store.cattleData.forEach(cattle => {
        if (!latestCattle[cattle.cattle_id] || new Date(cattle.timestamp) > new Date(latestCattle[cattle.cattle_id].timestamp)) {
            latestCattle[cattle.cattle_id] = cattle;
        }
    });
    return Object.values(latestCattle);
});
</script>

<style scoped>
/* Dashboard Overview Grid */
.cattle-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}

.cattle-card {
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    border-left: 6px solid;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.cattle-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* Cattle Card Colors based on Risk (using variables) */
.risk-critical { background-color: var(--alert-critical-bg); border-color: var(--alert-critical-border); }
.risk-high { background-color: var(--alert-high-bg); border-color: var(--alert-high-border); }
.risk-medium { background-color: var(--alert-medium-bg); border-color: var(--alert-medium-border); }
.risk-low-medium { background-color: var(--alert-low-medium-bg); border-color: var(--alert-low-medium-border); }
.risk-low { background-color: var(--alert-low-bg); border-color: var(--alert-low-border); }
.risk-default { background-color: var(--background-light); border-color: var(--border-color); }

.cattle-card h3 {
    font-size: 1.4em;
    font-weight: 700;
    margin-bottom: 8px;
    color: var(--text-dark);
}
.cattle-card p {
    margin-bottom: 5px;
    color: var(--text-secondary);
}
.cattle-card p.font-bold {
    font-weight: 700;
    color: var(--text-dark);
    font-size: 1.1em;
}
.cattle-card .mt-2 {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px dashed var(--border-color);
}
.cattle-card h4 {
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 8px;
}
.cattle-card ul {
    list-style: disc;
    padding-left: 20px;
    margin: 0;
}
.cattle-card ul li {
    margin-bottom: 3px;
    font-size: 0.95em;
}

/* Alert Text Colors (using variables) */
.text-critical { color: var(--alert-critical-text); font-weight: 600; }
.text-high { color: var(--alert-high-text); font-weight: 600; }
.text-medium { color: var(--alert-medium-text); }
.text-low-medium { color: var(--alert-low-medium-text); }
.text-low { color: var(--alert-low-text); }
.text-default { color: var(--text-dark); }

/* Responsive Adjustments */
@media (max-width: 768px) {
    .cattle-grid {
        grid-template-columns: 1fr;
    }
}
</style>
