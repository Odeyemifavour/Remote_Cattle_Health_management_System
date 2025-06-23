<template>
    <div class="content-area">
        <h2 class="card-title">Dashboard Overview</h2> <!-- Changed title for consistency -->
        <div v-if="store.loading" class="message-center loading-message">
            <i class="fa-solid fa-spinner fa-spin fa-2x"></i> Loading herd data...
        </div>
        <div v-else-if="store.error" class="error-message">
            <i class="fa-solid fa-circle-exclamation mr-2"></i> <span>{{ store.error }}</span>
            <p>Please check your Flask API status and network connection.</p>
        </div>
        <div v-else>
            <!-- Herd Health Status Cards (Updated to remove Observation) -->
            <div class="health-status-grid mb-8">
                <div class="status-card health-healthy">
                    <h3>Healthy</h3>
                    <i class="fa-solid fa-seedling fa-2x"></i>
                    <p class="count">{{ herdHealth.healthy }}</p>
                    <span class="percentage">({{ herdHealth.healthyPercentage }}%)</span>
                </div>
                <div class="status-card health-unhealthy"> <!-- Changed class from health-at-risk -->
                    <h3>Unhealthy</h3> <!-- Changed title from At Risk -->
                    <i class="fa-solid fa-triangle-exclamation fa-2x"></i>
                    <p class="count">{{ herdHealth.unhealthy }}</p> <!-- Changed from herdHealth.atRisk -->
                    <span class="percentage">({{ herdHealth.unhealthyPercentage }}%)</span> <!-- Changed from herdHealth.atRiskPercentage -->
                </div>
                <!-- Removed: Observation Card
                <div class="status-card health-observation">
                    <h3>Under Observation</h3>
                    <i class="fa-solid fa-eye fa-2x"></i>
                    <p class="count">{{ herdHealth.underObservation }}</p>
                    <span class="percentage">({{ herdHealth.underObservationPercentage }}%)</span>
                </div>
                -->
            </div>

            <!-- Recent Critical Alerts Section -->
            <div class="card recent-alerts-card mb-8">
                <h3 class="card-title-small">Recent Critical Alerts</h3>
                <ul v-if="recentCriticalAlerts.length > 0" class="alert-list">
                    <li v-for="alert in recentCriticalAlerts" :key="alert.id" class="alert-item">
                        <!-- Navigates to Prediction Log where all details are available -->
                        <router-link :to="`/prediction-log`" class="alert-link">
                            <span class="alert-icon"><i class="fa-solid fa-skull-crossbones"></i></span>
                            <span class="alert-message-text">{{ alert.message }} (Cattle ID: {{ alert.cattleId }})</span>
                            <span class="alert-timestamp">{{ formatTimestamp(alert.timestamp) }}</span>
                        </router-link>
                    </li>
                </ul>
                <p v-else class="message-center no-alerts-message">No recent critical alerts.</p>
                <button @click="$router.push('/alerts')" class="view-all-alerts-button">
                    View All Alerts <i class="fa-solid fa-arrow-right ml-2"></i>
                </button>
            </div>

            <!-- Key Metric Trends Section -->
            <div class="metric-trends-grid mb-8">
                <div class="card trend-chart-card">
                    <h3 class="card-title-small">Overall Herd Risk Level</h3>
                    <div class="chart-container">
                        <canvas ref="riskLevelChartCanvas"></canvas>
                    </div>
                    <p class="chart-description">Trend of the overall herd health risk level.</p>
                </div>
                <div class="card trend-chart-card">
                    <h3 class="card-title-small">Average Fever Index</h3>
                    <div class="chart-container">
                        <canvas ref="feverIndexChartCanvas"></canvas>
                    </div>
                    <p class="chart-description">Average body temperature deviation indicating thermal stress.</p>
                </div>
                <div class="card trend-chart-card">
                    <h3 class="card-title-small">Average Productivity Score</h3>
                    <div class="chart-container">
                        <canvas ref="productivityScoreChartCanvas"></canvas>
                    </div>
                    <p class="chart-description">Herd's overall productivity based on milk production and activity.</p>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card quick-actions-card">
                <h3 class="card-title-small">Quick Actions</h3>
                <div class="quick-actions-grid">
                    <button @click="openAddAnimalModal" class="action-button primary-action">
                        <i class="fa-solid fa-plus-circle mr-2"></i> Add New Animal
                    </button>
                    <button @click="$router.push('/dashboard/herd-dashboard')" class="action-button secondary-action">
                        <i class="fa-solid fa-chart-bar mr-2"></i> View Herd Dashboard
                    </button>
                    <button @click="$router.push('/add-data')" class="action-button tertiary-action">
                        <i class="fa-solid fa-database mr-2"></i> Input Daily Data
                    </button>
                </div>
            </div>

            <!-- Add New Animal Modal -->
            <div v-if="showAddAnimalModal" class="modal-overlay">
                <div class="modal">
                    <span class="close-icon" @click="closeAddAnimalModal">×</span>
                    <h3>Add New Animal</h3>
                    <p class="modal-message">This feature is integrated into the "Add Cattle Data" page, where you can submit data for new or existing cattle IDs. For full cattle management, see the "Cattle Information" section.</p>
                    <button @click="closeAddAnimalModal" class="modal-close-button">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, reactive } from 'vue';
import { store } from '../main.js'; // Import the global store

// IMPORTANT: Chart.js is loaded via CDN in index.html, so it's available globally as window.Chart
// Do NOT import Chart from 'chart.js/auto'; here.

// Refs for Chart.js canvas elements
const riskLevelChartCanvas = ref(null);
const feverIndexChartCanvas = ref(null);
const productivityScoreChartCanvas = ref(null);

// Chart instances
let riskLevelChart = null;
let feverIndexChart = null;
let productivityScoreChart = null;

// Modal state
const showAddAnimalModal = ref(false);
const openAddAnimalModal = () => {
    showAddAnimalModal.value = true;
};
const closeAddAnimalModal = () => {
    showAddAnimalModal.value = false;
};

// Computed property for the latest entry for each cattle ID
const filteredCattle = computed(() => {
    const latestEntries = {};
    (store.cattleData || []).forEach(cattle => {
        if (cattle.monitoring_results && cattle.cattle_id) {
            if (!latestEntries[cattle.cattle_id] || new Date(cattle.timestamp) > new Date(latestEntries[cattle.cattle_id].timestamp)) {
                latestEntries[cattle.cattle_id] = cattle;
            }
        }
    });
    // Map to ensure healthStatusDisplay is capitalized "Healthy" or "Unhealthy"
    return Object.values(latestEntries).map(cattle => {
        const healthStatus = cattle.monitoring_results.health_status;
        return {
            ...cattle,
            healthStatusDisplay: healthStatus.charAt(0).toUpperCase() + healthStatus.slice(1).toLowerCase(), 
            riskLevel: cattle.monitoring_results.risk_level // Ensure riskLevel is also available
        };
    });
});

// --- Herd Health Summary (Computed from store.cattleData) - UPDATED ---
const herdHealth = computed(() => {
    let healthy = 0;
    let unhealthy = 0; // Changed 'atRisk' to 'unhealthy' for consistency
    const total = filteredCattle.value.length; // Use filteredCattle for latest unique cattle

    filteredCattle.value.forEach(cattle => {
        // Now directly use healthStatusDisplay which is already "Healthy" or "Unhealthy"
        if (cattle.healthStatusDisplay === 'Healthy') {
            healthy++;
        } else if (cattle.healthStatusDisplay === 'Unhealthy') {
            unhealthy++;
        }
    });

    return {
        healthy,
        unhealthy, // Renamed from atRisk
        total, // Renamed from totalHerdCount for clarity
        healthyPercentage: total > 0 ? ((healthy / total) * 100).toFixed(1) : 0,
        unhealthyPercentage: total > 0 ? ((unhealthy / total) * 100).toFixed(1) : 0, // Renamed
    };
});

// --- Recent Critical Alerts (Computed from store.activeAlerts) ---
const recentCriticalAlerts = computed(() => {
    return store.activeAlerts
        .filter(alert => alert.severity.toLowerCase() === 'critical')
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 3); // Display top 3 critical alerts
});

// --- Dummy Trend Data for Charts ---
const trendData = reactive({
    riskLevel: [10, 15, 12, 18, 16, 20, 17], // Example values, higher = worse
    feverIndex: [2.1, 2.3, 2.2, 2.5, 2.4, 2.6, 2.5], // Example values, higher = worse
    productivityScore: [85, 88, 86, 90, 89, 92, 91], // Example values, higher = better
    labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
});


// --- Chart Initialization and Update Functions ---

const createChart = (canvasRef, chartType, data, options) => {
    if (canvasRef && canvasRef.value) {
        const ctx = canvasRef.value.getContext('2d');
        if (window.Chart.getChart(ctx)) { // Use window.Chart
            window.Chart.getChart(ctx).destroy(); // Use window.Chart
        }
        return new window.Chart(ctx, { // Use window.Chart
            type: chartType,
            data: data,
            options: options
        });
    }
    return null;
};

const updateAllCharts = () => {
    // Overall Herd Risk Level Chart
    riskLevelChart = createChart(riskLevelChartCanvas, 'line', {
        labels: trendData.labels,
        datasets: [{
            label: 'Risk Level',
            data: trendData.riskLevel,
            borderColor: '#F57C00', // Matches alert-high-border
            backgroundColor: 'rgba(245, 124, 0, 0.2)',
            fill: true,
            tension: 0.3,
            pointBackgroundColor: '#F57C00',
            pointBorderColor: '#FFF',
            pointHoverBackgroundColor: '#FFF',
            pointHoverBorderColor: '#F57C00',
        }]
    }, {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            title: { display: false }
        },
        scales: {
            x: {
                title: { display: true, text: 'Day', color: 'var(--text-secondary)' },
                ticks: { color: 'var(--text-dark)' },
                grid: { color: 'rgba(0,0,0,0.05)' }
            },
            y: {
                title: { display: true, text: 'Risk Level (Score)', color: 'var(--text-secondary)' },
                beginAtZero: true,
                ticks: { color: 'var(--text-dark)' },
                grid: { color: 'rgba(0,0,0,0.05)' }
            }
        }
    });

    // Average Fever Index Chart
    feverIndexChart = createChart(feverIndexChartCanvas, 'line', {
        labels: trendData.labels,
        datasets: [{
            label: 'Fever Index',
            data: trendData.feverIndex,
            borderColor: '#D32F2F', // Matches alert-critical-border
            backgroundColor: 'rgba(211, 47, 47, 0.2)',
            fill: true,
            tension: 0.3,
            pointBackgroundColor: '#D32F2F',
            pointBorderColor: '#FFF',
            pointHoverBackgroundColor: '#FFF',
            pointHoverBorderColor: '#D32F2F',
        }]
    }, {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            title: { display: false }
        },
        scales: {
            x: {
                title: { display: true, text: 'Day', color: 'var(--text-secondary)' },
                ticks: { color: 'var(--text-dark)' },
                grid: { color: 'rgba(0,0,0,0.05)' }
            },
            y: {
                title: { display: true, text: 'Fever Index (Avg. Deviation)', color: 'var(--text-secondary)' },
                beginAtZero: true,
                ticks: { color: 'var(--text-dark)' },
                grid: { color: 'rgba(0,0,0,0.05)' }
            }
        }
    });

    // Average Productivity Score Chart
    productivityScoreChart = createChart(productivityScoreChartCanvas, 'line', {
        labels: trendData.labels,
        datasets: [{
            label: 'Productivity Score',
            data: trendData.productivityScore,
            borderColor: '#4CAF50', // Matches primary-color
            backgroundColor: 'rgba(76, 175, 80, 0.2)',
            fill: true,
            tension: 0.3,
            pointBackgroundColor: '#4CAF50',
            pointBorderColor: '#FFF',
            pointHoverBackgroundColor: '#FFF',
            pointHoverBorderColor: '#4CAF50',
        }]
    }, {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            title: { display: false }
        },
        scales: {
            x: {
                title: { display: true, text: 'Day', color: 'var(--text-secondary)' },
                ticks: { color: 'var(--text-dark)' },
                grid: { color: 'rgba(0,0,0,0.05)' }
            },
            y: {
                title: { display: true, text: 'Productivity (Score)', color: 'var(--text-secondary)' },
                beginAtZero: true,
                ticks: { color: 'var(--text-dark)' },
                grid: { color: 'rgba(0,0,0,0.05)' }
            }
        }
    });
};


// --- Lifecycle Hooks ---
onMounted(() => {
    updateAllCharts(); // Initial chart rendering

    // Watch for changes in store.cattleData or store.activeAlerts
    watch(() => store.cattleData.length, () => {
        // herdHealth and recentCriticalAlerts computed properties will react to changes
        // If trendData was dynamic based on store.cattleData, updateAllCharts would be needed here.
    });
    watch(() => store.activeAlerts.length, () => {
        // recentCriticalAlerts computed property will react to changes
    });
});

onUnmounted(() => {
    // Destroy charts when component unmounts to prevent memory leaks
    if (riskLevelChart) riskLevelChart.destroy();
    if (feverIndexChart) feverIndexChart.destroy();
    if (productivityScoreChart) productivityScoreChart.destroy();
});


// --- Utility Functions (also available to template) ---

// Formats timestamp for display (e.g., "Jun 5, 10:00 AM")
const formatTimestamp = (timestampString) => {
    if (!timestampString) return 'N/A';
    const date = new Date(timestampString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
};

// Utility function for alert severity class
const getAlertSeverityClass = (severity) => {
    return `alert-severity-${severity?.toLowerCase().replace(' ', '-')}`;
};

</script>

<style scoped>
/* Scoped styles for DashboardOverview component */
/* Using existing global variable names for consistency */

.health-status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 25px;
    margin-bottom: 25px;
}

.status-card {
    background-color: var(--card-bg);
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    text-align: center;
    border: 1px solid var(--border-color);
    transition: transform 0.2s ease;
}

.status-card:hover {
    transform: translateY(-5px);
}

.status-card h3 {
    margin-top: 0;
    margin-bottom: 10px;
    color: var(--text-dark);
    font-size: 1.15em;
    font-weight: 600;
}

.status-card i {
    font-size: 2.8em;
    margin-bottom: 15px;
}

.status-card .count {
    font-size: 2.2em;
    font-weight: 800;
    margin: 0;
}

.status-card .percentage {
    display: block;
    font-size: 1em;
    color: var(--text-secondary);
    margin-top: 5px;
}

/* Specific colors for status cards (UPDATED) */
.status-card.health-healthy i, .status-card.health-healthy .count { color: var(--success-color); }
.status-card.health-unhealthy i, .status-card.health-unhealthy .count { color: var(--danger-color); } /* Updated to use danger-color */
/* Removed: .status-card.health-at-risk and .status-card.health-observation styles */


/* Recent Alerts Card */
.recent-alerts-card {
    padding: 30px;
}
.recent-alerts-card .card-title-small {
    margin-bottom: 20px;
}

.alert-list {
    list-style: none;
    padding: 0;
    margin-top: 20px;
}

.alert-item {
    display: flex;
    align-items: flex-start;
    padding: 15px 20px;
    border-radius: 8px;
    margin-bottom: 12px;
    border: 1px solid var(--border-color);
    background-color: var(--card-bg); /* Default background */
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
}
.alert-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.alert-link {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: var(--text-dark);
    font-weight: 500;
    width: 100%; /* Ensure link takes full width */
}

.alert-icon {
    font-size: 1.4em;
    color: var(--alert-critical-border);
    margin-right: 15px;
    flex-shrink: 0;
}

.alert-message-text {
    flex-grow: 1;
    color: var(--alert-critical-text);
    font-weight: 600;
    font-size: 1.05em;
    line-height: 1.4;
}

.alert-timestamp {
    font-size: 0.85em;
    color: var(--text-secondary);
    margin-left: 20px;
    flex-shrink: 0;
    white-space: nowrap;
}

.view-all-alerts-button {
    background-color: var(--primary-color);
    color: var(--text-light);
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
    margin-top: 20px;
    font-size: 1em;
    font-weight: 600;
    display: block; /* Make it a block button */
    width: fit-content;
    margin-left: auto; /* Push to right */
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.view-all-alerts-button:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

/* No alerts message */
.no-alerts-message {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
    font-style: italic;
    font-size: 1.1em;
}


/* Metric Trends Grid */
.metric-trends-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 25px;
    margin-bottom: 25px;
}

.trend-chart-card {
    min-height: 350px; /* Ensure enough space for charts */
    display: flex;
    flex-direction: column;
}

.chart-container {
    flex-grow: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
    max-height: 300px; /* Max height to control chart size */
}
.chart-container canvas {
    max-width: 100%;
    max-height: 100%;
}

.chart-description {
    font-size: 0.9em;
    color: var(--text-secondary);
    text-align: center;
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px dashed var(--border-color);
}


/* Quick Actions Card */
.quick-actions-card {
    padding: 30px;
}
.quick-actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.action-button {
    padding: 15px 20px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1.05em;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border: none;
    transition: all 0.25s ease;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.action-button i {
    margin-right: 8px;
}

.primary-action {
    background-color: var(--primary-color);
    color: var(--text-light);
}
.primary-action:hover {
    background-color: var(--primary-dark);
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

.secondary-action {
    background-color: #ECEFF1; /* Light grey */
    color: var(--text-dark);
    border: 1px solid var(--border-color);
}
.secondary-action:hover {
    background-color: #CFD8DC; /* Darker grey */
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

.tertiary-action {
    background-color: #BBDEFB; /* Light blue */
    color: #1565C0; /* Darker blue */
    border: 1px solid #90CAF9;
}
.tertiary-action:hover {
    background-color: #90CAF9;
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}


/* Modal Styling */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal {
    background-color: var(--card-bg);
    padding: 40px 30px;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    text-align: center;
    position: relative;
    max-width: 500px;
    width: 90%;
    animation: fadeIn 0.3s ease-out;
}

.modal .close-icon {
    position: absolute;
    top: 15px;
    right: 20px;
    font-size: 2em;
    cursor: pointer;
    color: var(--text-secondary);
    transition: color 0.2s ease;
}
.modal .close-icon:hover {
    color: var(--text-dark);
}

.modal h3 {
    margin-top: 0;
    font-size: 1.8em;
    color: var(--text-dark);
    margin-bottom: 15px;
}
.modal-message {
    font-size: 1.1em;
    color: var(--text-secondary);
    margin-bottom: 30px;
}
.modal-close-button {
    background-color: var(--primary-color);
    color: var(--text-light);
    border: none;
    padding: 12px 25px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1.05em;
    font-weight: 600;
    transition: background-color 0.2s ease;
}
.modal-close-button:hover {
    background-color: var(--primary-dark);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}


/* Responsive Adjustments */
@media (max-width: 768px) {
    .health-status-grid, .metric-trends-grid, .quick-actions-grid {
        grid-template-columns: 1fr;
    }
    .status-card, .trend-chart-card {
        min-height: auto;
    }
    .alert-item {
        padding: 12px;
    }
    .alert-icon {
        font-size: 1.2em;
        margin-right: 10px;
    }
    .alert-message-text {
        font-size: 0.95em;
    }
    .alert-timestamp {
        font-size: 0.7em;
        margin-left: 10px;
    }
    .view-all-alerts-button {
        width: 100%;
        margin-right: auto;
        margin-left: auto;
    }
}
</style>
