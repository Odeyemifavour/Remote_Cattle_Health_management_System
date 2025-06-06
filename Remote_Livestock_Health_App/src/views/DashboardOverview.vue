<template>
    <div class="content-area">
        <h2 class="card-title">Dashboard Overview</h2>
        <div v-if="store.loading" class="message-center">Loading cattle data...</div>
        <div v-else-if="store.error" class="error-message">
            <span>{{ store.error }}</span>
        </div>
        <div v-else-if="filteredCattle.length === 0" class="message-center">
            No cattle data available. Add some data using the "Add Cattle Data" section or the "Cattle Prediction" tool.
        </div>
        <div v-else>
            <!-- Summary Statistics Cards -->
            <div class="summary-grid mb-8">
                <div class="summary-card total-cattle">
                    <i class="fa-solid fa-cow fa-2x"></i>
                    <h3>Total Cattle</h3>
                    <p class="metric">{{ totalCattleCount }}</p>
                </div>
                <div class="summary-card healthy-cattle">
                    <i class="fa-solid fa-heart fa-2x"></i>
                    <h3>Healthy Cattle</h3>
                    <p class="metric">{{ healthyCattleCount }}</p>
                </div>
                <div class="summary-card unhealthy-cattle">
                    <i class="fa-solid fa-skull-crossbones fa-2x"></i>
                    <h3>Unhealthy Cattle</h3>
                    <p class="metric">{{ unhealthyCattleCount }}</p>
                </div>
                <div class="summary-card critical-alerts">
                    <i class="fa-solid fa-exclamation-triangle fa-2x"></i>
                    <h3>Critical Alerts</h3>
                    <p class="metric">{{ criticalAlertsCount }}</p>
                </div>
            </div>

            <!-- Top Alerts Section -->
            <div class="card mb-8">
                <h3 class="card-title-small">Top 5 Recent Alerts</h3>
                <div v-if="store.activeAlerts.length === 0" class="message-center">
                    No recent alerts to display.
                </div>
                <div v-else class="space-y-4">
                    <div v-for="alert in topRecentAlerts" :key="alert.id"
                         :class="['alert-card-small', alert.severity.toLowerCase().replace(' ', '')]">
                        <p class="font-semibold mb-1">Cattle ID: <span class="font-bold">{{ alert.cattleId }}</span></p>
                        <p class="text-sm text-gray-700 mb-1">Time: {{ alert.timestamp }}</p>
                        <p class="text-md font-medium" :class="getAlertTextClass(alert.severity)">
                            {{ alert.message }}
                        </p>
                        <p class="text-sm text-gray-600 mt-1">Severity: <span :class="getAlertTextClass(alert.severity)">{{ alert.severity }}</span></p>
                    </div>
                </div>
                <router-link to="/alerts" class="view-more-link">View All Alerts <i class="fa-solid fa-arrow-right"></i></router-link>
            </div>

            <!-- Latest Predictions Section -->
            <div class="card">
                <h3 class="card-title-small">Latest 5 Predictions</h3>
                <div v-if="filteredCattle.length === 0" class="message-center">
                    No recent predictions to display.
                </div>
                <div v-else class="space-y-4">
                    <div v-for="cattle in latestPredictions" :key="cattle.id"
                         :class="['prediction-summary-card', getCardClass(cattle.monitoring_results.risk_level)]">
                        <p class="font-semibold mb-1">Cattle ID: <span class="font-bold">{{ cattle.cattle_id }}</span></p>
                        <p class="text-sm text-gray-700 mb-1">Last Updated: {{ cattle.timestamp }}</p>
                        <p class="text-md font-bold mb-1">Status: {{ cattle.monitoring_results.health_status }}</p>
                        <p class="text-md font-bold mb-1">Risk: {{ cattle.monitoring_results.risk_level }}</p>
                        <p class="text-sm text-gray-600">Confidence: {{ cattle.monitoring_results.confidence }}</p>
                    </div>
                </div>
                <router-link to="/prediction-log" class="view-more-link">View All Predictions <i class="fa-solid fa-arrow-right"></i></router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { store } from '../main.js'; // Assuming store is exported from main.js

const getCardClass = (riskLevel) => {
    return `risk-${riskLevel.toLowerCase().replace(' ', '-')}`;
};

const getAlertTextClass = (severity) => {
    return `text-${severity.toLowerCase().replace(' ', '-')}`;
};

// Computes the latest entry for each unique cattle ID
const filteredCattle = computed(() => {
    const latestCattle = {};
    store.cattleData.forEach(cattle => {
        // Ensure that monitoring_results and health_status exist
        if (cattle.monitoring_results && cattle.monitoring_results.health_status) {
            if (!latestCattle[cattle.cattle_id] || new Date(cattle.timestamp) > new Date(latestCattle[cattle.cattle_id].timestamp)) {
                latestCattle[cattle.cattle_id] = cattle;
            }
        }
    });
    return Object.values(latestCattle);
});

// Summary Statistics
const totalCattleCount = computed(() => filteredCattle.value.length);
const healthyCattleCount = computed(() => filteredCattle.value.filter(c => c.monitoring_results.health_status.toLowerCase() === 'healthy').length);
const unhealthyCattleCount = computed(() => filteredCattle.value.filter(c => c.monitoring_results.health_status.toLowerCase() === 'unhealthy').length);
const criticalAlertsCount = computed(() => store.activeAlerts.filter(alert => alert.severity.toLowerCase() === 'critical').length);

// Top 5 Recent Alerts (already sorted by severity in main.js, so just take top 5)
const topRecentAlerts = computed(() => store.activeAlerts.slice(0, 5));

// Latest 5 Predictions (sort by timestamp, take top 5)
const latestPredictions = computed(() => {
    return [...filteredCattle.value]
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 5);
});
</script>

<style scoped>
/* Main card container handled by global styles */

.card-title-small {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 25px;
    margin-bottom: 25px;
}

.summary-card {
    background-color: var(--card-bg);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    border: 1px solid var(--border-color);
    transition: transform 0.2s ease;
}

.summary-card:hover {
    transform: translateY(-5px);
}

.summary-card i {
    font-size: 2.5em;
    margin-bottom: 15px;
    color: var(--primary-color); /* Default icon color */
}

.summary-card h3 {
    font-size: 1.1em;
    font-weight: 600;
    margin-bottom: 10px;
    color: var(--text-dark);
}

.summary-card .metric {
    font-size: 2.5em;
    font-weight: 800;
    color: var(--primary-dark);
    margin: 0;
}

/* Specific colors for summary cards */
.summary-card.total-cattle i { color: #1976D2; } /* Blue */
.summary-card.healthy-cattle i { color: var(--primary-color); } /* Green */
.summary-card.unhealthy-cattle i { color: var(--alert-critical-border); } /* Red */
.summary-card.critical-alerts i { color: var(--alert-high-border); } /* Orange/Warning */


/* Alert Card Small (reused for top alerts) */
.alert-card-small {
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    border-left: 5px solid;
    margin-bottom: 10px;
}

.alert-card-small.critical { background-color: var(--alert-critical-bg); border-color: var(--alert-critical-border); }
.alert-card-small.high { background-color: var(--alert-high-bg); border-color: var(--alert-high-border); }
.alert-card-small.medium { background-color: var(--alert-medium-bg); border-color: var(--alert-medium-border); }
.alert-card-small.low-medium { background-color: var(--alert-low-medium-bg); border-color: var(--alert-low-medium-border); }
.alert-card-small.low { background-color: var(--alert-low-bg); border-color: var(--alert-low-border); }

.alert-card-small p { margin-bottom: 3px; }
.alert-card-small .font-semibold { font-weight: 600; color: var(--text-dark); }
.alert-card-small .font-bold { font-weight: 700; color: var(--text-dark); }
.alert-card-small .text-sm { font-size: 0.85em; color: var(--text-secondary); }
.alert-card-small .text-md { font-size: 0.95em; }


/* Prediction Summary Card */
.prediction-summary-card {
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    border-left: 5px solid;
    margin-bottom: 10px;
    background-color: var(--card-bg); /* Use card background for consistency */
}
/* Re-use risk-based colors from global styles */
.prediction-summary-card.risk-critical { border-color: var(--alert-critical-border); }
.prediction-summary-card.risk-high { border-color: var(--alert-high-border); }
.prediction-summary-card.risk-medium { border-color: var(--alert-medium-border); }
.prediction-summary-card.risk-low-medium { border-color: var(--alert-low-medium-border); }
.prediction-summary-card.risk-low { border-color: var(--alert-low-border); }
.prediction-summary-card.risk-default { border-color: var(--border-color); }


.prediction-summary-card p { margin-bottom: 3px; }
.prediction-summary-card .font-semibold { font-weight: 600; color: var(--text-dark); }
.prediction-summary-card .font-bold { font-weight: 700; color: var(--text-dark); }
.prediction-summary-card .text-sm { font-size: 0.85em; color: var(--text-secondary); }
.prediction-summary-card .text-md { font-size: 0.95em; }


.view-more-link {
    display: block;
    text-align: right;
    margin-top: 15px;
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s ease;
}
.view-more-link:hover {
    color: var(--primary-dark);
    text-decoration: underline;
}
.view-more-link i {
    margin-left: 5px;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .summary-grid {
        grid-template-columns: 1fr;
    }
}
</style>