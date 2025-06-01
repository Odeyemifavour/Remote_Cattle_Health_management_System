<template>
    <div class="card">
        <h2 class="card-title">Prediction Log</h2>
        <div v-if="store.loading" class="message-center">Loading prediction history...</div>
        <div v-else-if="store.error" class="error-message">
            <span>{{ store.error }}</span>
        </div>
        <div v-else-if="store.cattleData.length === 0" class="message-center">
            No prediction history available.
        </div>
        <div v-else class="overflow-x-auto">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Cattle ID</th>
                        <th>Timestamp</th>
                        <th>Health Status</th>
                        <th>Risk Level</th>
                        <th>Confidence</th>
                        <th>Diseases Detected</th>
                        <th>Alerts Count</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="log in sortedCattleData" :key="log.id">
                        <td>{{ log.cattle_id }}</td>
                        <td>{{ log.timestamp }}</td>
                        <td>
                            <span :class="['status-badge', getStatusClass(log.monitoring_results.health_status)]">
                                {{ log.monitoring_results.health_status }}
                            </span>
                        </td>
                        <td>
                            <span :class="['risk-badge', getRiskClass(log.monitoring_results.risk_level)]">
                                {{ log.monitoring_results.risk_level }}
                            </span>
                        </td>
                        <td>{{ log.monitoring_results.confidence }}</td>
                        <td>{{ log.specific_diseases_detected.join(', ') || 'None' }}</td>
                        <td>{{ log.alerts ? log.alerts.length : 0 }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { store } from '../../main.js';

const sortedCattleData = computed(() => {
    return [...store.cattleData].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
});

const getStatusClass = (status) => {
    return status.toLowerCase() === 'unhealthy' ? 'status-unhealthy' : 'status-healthy';
};

const getRiskClass = (risk) => {
    return risk.toLowerCase().replace(' ', '');
};
</script>

<style scoped>
/* Table Styles (Prediction Log) */
.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 20px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.data-table th, .data-table td {
    padding: 15px 20px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

.data-table th {
    background-color: #F0F0F0;
    font-weight: 600;
    color: var(--text-dark);
    text-transform: uppercase;
    font-size: 13px;
}
.data-table th:first-child { border-top-left-radius: 12px; }
.data-table th:last-child { border-top-right-radius: 12px; }

.data-table tbody tr:last-child td {
    border-bottom: none;
}
.data-table tbody tr:nth-child(even) {
    background-color: #FBFBFB;
}
.data-table tbody tr:hover {
    background-color: #F0F4F8;
}

/* Status & Risk Badges in Table */
.status-badge, .risk-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    display: inline-block;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.status-healthy { background-color: var(--alert-low-border); color: var(--text-light); }
.status-unhealthy { background-color: var(--alert-critical-border); color: var(--text-light); }

.risk-badge.critical { background-color: var(--alert-critical-border); color: var(--text-light); }
.risk-badge.high { background-color: var(--alert-high-border); color: var(--text-light); }
.risk-badge.medium { background-color: var(--alert-medium-border); color: var(--text-dark); }
.risk-badge.low-medium { background-color: var(--alert-low-medium-border); color: var(--text-light); }
.risk-badge.low { background-color: var(--alert-low-border); color: var(--text-light); }

/* Responsive Adjustments */
@media (max-width: 768px) {
    .overflow-x-auto {
        overflow-x: scroll;
    }
    .data-table {
        min-width: 700px;
    }
}
</style>