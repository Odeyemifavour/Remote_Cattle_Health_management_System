<template>
    <div class="content-area">
        <div class="card">
            <h2 class="card-title">Real-time Data Simulator</h2>
            <p>Simulate continuous livestock data input and observe real-time predictions and alerts.</p>

            <div class="simulator-controls mb-6">
                <button @click="startSimulation" :disabled="isSimulating" class="action-button primary-action mr-4">
                    <i class="fa-solid fa-play-circle mr-2"></i> Start Simulation
                </button>
                <button @click="stopSimulation" :disabled="!isSimulating" class="action-button secondary-action">
                    <i class="fa-solid fa-stop-circle mr-2"></i> Stop Simulation
                </button>
            </div>

            <div v-if="simulationLoading" class="message-center loading-message">
                <i class="fa-solid fa-spinner fa-spin fa-2x"></i> Sending data...
            </div>
            <div v-if="simulationError" class="error-message">
                <p><strong>Simulation Error:</strong> {{ simulationError }}</p>
                <p>Ensure your Flask API is running and accessible at <code>{{ store.flaskApiUrl }}</code>.</p>
            </div>

            <div v-if="latestSimulationResult" class="card mt-6 p-4">
                <h3 class="card-title-small">Latest Simulation Output</h3>
                <pre class="json-output">{{ JSON.stringify(latestSimulationResult, null, 2) }}</pre>
            </div>

            <div class="card mt-6 p-4">
                <h3 class="card-title-small">Simulation Log (Last 5 Entries)</h3>
                <div v-if="simulationLog.length > 0">
                    <div v-for="entry in simulationLog" :key="entry.timestamp" class="log-entry">
                        <p><strong>Time:</strong> {{ formatTimestamp(entry.timestamp) }}</p>
                        <p><strong>Cattle ID:</strong> {{ entry.cattle_id }}</p>
                        <p><strong>Health Status:</strong> <span :class="['status-badge', getStatusClass(entry.monitoring_results?.health_status)]">{{ entry.monitoring_results?.health_status || 'N/A' }}</span></p>
                        <p><strong>Risk Level:</strong> <span :class="['risk-badge', getRiskClass(entry.monitoring_results?.risk_level)]">{{ entry.monitoring_results?.risk_level || 'N/A' }}</span></p>
                        <!-- REMOVED: Alerts information from simulation log -->
                        <hr class="log-divider"/>
                    </div>
                </div>
                <p v-else class="message-center">No simulation data sent yet.</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue';
import { store } from '../main.js'; // Import the global store

const isSimulating = ref(false);
const simulationInterval = ref(null);
const simulationLoading = ref(false);
const simulationError = ref(null);
const latestSimulationResult = ref(null);
const simulationLog = reactive([]); // Store a log of recent results

const cattleIdCounter = ref(1); // To generate unique cattle IDs for simulation

// Helper functions for dynamic styling
const getStatusClass = (status) => {
    // Only healthy and unhealthy status classes are needed
    return status?.toLowerCase() === 'unhealthy' ? 'status-unhealthy' : 'status-healthy';
};

const getRiskClass = (risk) => {
    return `risk-${risk?.toLowerCase().replace(' ', '-')}`;
};

// Function to generate random-ish dummy data (UPDATED for breed_type)
const generateDummyData = () => {
    const currentCattleId = `SIM_CATTLE_${String(cattleIdCounter.value).padStart(3, '0')}`;
    cattleIdCounter.value++;

    // Generate data that can sometimes trigger 'unhealthy' or specific alerts
    const isUnhealthyScenario = Math.random() < 0.3; // 30% chance to simulate an unhealthy scenario

    const data = {
        cattle_id: currentCattleId,
        body_temperature: isUnhealthyScenario ? (39.5 + Math.random() * 1.5) : (38.0 + Math.random() * 1.5), // Higher if unhealthy
        breed_type: Math.random() < 0.5 ? 'Normal Breed' : 'Cross Breed', // Only Normal Breed or Cross Breed
        milk_production: isUnhealthyScenario ? (5 + Math.random() * 5) : (15 + Math.random() * 10), // Lower if unhealthy
        respiratory_rate: isUnhealthyScenario ? Math.floor(40 + Math.random() * 20) : Math.floor(20 + Math.random() * 15), // Higher if unhealthy
        walking_capacity: isUnhealthyScenario ? Math.floor(5000 + Math.random() * 4000) : Math.floor(10000 + Math.random() * 10000), // Lower if unhealthy
        sleeping_duration: (5 + Math.random() * 3),
        body_condition_score: isUnhealthyScenario ? (1.5 + Math.random() * 1.5) : (3.0 + Math.random() * 1.5), // Lower if unhealthy
        heart_rate: isUnhealthyScenario ? Math.floor(75 + Math.random() * 20) : Math.floor(50 + Math.random() * 20), // Higher if unhealthy
        eating_duration: (2 + Math.random() * 2),
        lying_down_duration: (10 + Math.random() * 4),
        ruminating: (4 + Math.random() * 2),
        rumen_fill: Math.floor(1 + Math.random() * 5),
        faecal_consistency: ['ideal', 'watery', 'Black faece', 'extremely firm', 'firm', 'Fresh blood in faeces', 'very liquid faeces'][Math.floor(Math.random() * 7)], // Added more consistencies
    };

    // Ensure numerical values are actual numbers (not strings from toFixed if used)
    for (const key in data) {
        if (typeof data[key] === 'string' && !isNaN(parseFloat(data[key]))) {
            data[key] = parseFloat(data[key]);
        }
        // Round floats for cleaner display, but keep as numbers
        if (typeof data[key] === 'number' && !Number.isInteger(data[key])) {
            data[key] = parseFloat(data[key].toFixed(1));
        }
    }

    // Add specific triggers for rule-based alerts to appear more often in simulation
    // NOTE: Alerts are removed from display, but simulator can still generate data that might trigger them in backend.
    if (Math.random() < 0.2) { // 20% chance for critical temp/resp
        data.body_temperature = parseFloat((40.0 + Math.random() * 1.0).toFixed(1));
        data.respiratory_rate = Math.floor(48 + Math.random() * 10);
        data.heart_rate = Math.floor(85 + Math.random() * 15);
    }
    if (Math.random() < 0.1) { // 10% chance for abnormal faeces
        data.faecal_consistency = ['watery', 'Black faece', 'Fresh blood in faeces', 'very liquid faeces'][Math.floor(Math.random() * 4)];
    }
    if (Math.random() < 0.05) { // 5% chance for low milk production
        data.milk_production = parseFloat((3 + Math.random() * 4).toFixed(1));
    }


    return data;
};


// Function to send data to Flask API
const sendDataToFlask = async () => {
    const dataToSend = generateDummyData();
    simulationLoading.value = true;
    simulationError.value = null;

    try {
        // Check if userId is available from the store
        if (!store.userId) {
            console.warn("User ID not available in store, cannot send data to Flask for specific user.");
            // Option: You can still send, and Flask will use 'anonymous_flask_user'
            // Or you can return here and wait for auth to be ready
            // For this simulator, let's proceed and let Flask handle it as anonymous if needed.
        }

        const response = await fetch(store.flaskApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': store.userId || 'anonymous_simulator' // Pass userId from store
            },
            body: JSON.stringify(dataToSend),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to get prediction from Flask API: ${response.statusText}`);
        }

        const result = await response.json();
        latestSimulationResult.value = result;

        // Add to log, keep only last 5 entries
        simulationLog.unshift(result);
        if (simulationLog.length > 5) {
            simulationLog.pop();
        }
        console.log('Simulation data sent and response received:', result);

    } catch (error) {
        simulationError.value = error.message;
        console.error('Simulation failed:', error);
        // Stop simulation on error to prevent continuous errors
        stopSimulation();
    } finally {
        simulationLoading.value = false;
    }
};

const startSimulation = () => {
    if (!isSimulating.value) {
        console.log('Starting simulation...');
        isSimulating.value = true;
        cattleIdCounter.value = 1; // Reset counter for new simulation run
        simulationLog.splice(0); // Clear previous log
        // Send initial data immediately, then set interval
        sendDataToFlask();
        simulationInterval.value = setInterval(sendDataToFlask, 5000); // Send data every 5 seconds
    }
};

const stopSimulation = () => {
    if (isSimulating.value) {
        console.log('Stopping simulation.');
        isSimulating.value = false;
        clearInterval(simulationInterval.value);
        simulationInterval.value = null;
    }
};

const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
};

// Cleanup on component unmount
onUnmounted(() => {
    stopSimulation();
});
</script>

<style scoped>
.simulator-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 25px;
}

.action-button {
    padding: 12px 25px;
    border-radius: 8px;
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

.action-button:disabled {
    background-color: #B0BEC5;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
    opacity: 0.7;
}

.primary-action {
    background-color: var(--primary-color);
    color: var(--text-light);
}
.primary-action:hover:not(:disabled) {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

.secondary-action {
    background-color: #ECEFF1; /* Light grey */
    color: var(--text-dark);
    border: 1px solid var(--border-color);
}
.secondary-action:hover:not(:disabled) {
    background-color: #CFD8DC; /* Darker grey */
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.15);
}

.json-output {
    background-color: #eceff1;
    padding: 15px;
    border-radius: 8px;
    white-space: pre-wrap;
    word-break: break-all;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
    font-size: 0.9em;
    color: #37474F;
    border: 1px solid #CFD8DC;
    max-height: 400px; /* Limit height for long JSON */
    overflow-y: auto; /* Add scroll for long content */
}

.log-entry {
    background-color: var(--background-light);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.log-entry p {
    margin-bottom: 5px;
    font-size: 0.9em;
}
.log-entry strong {
    color: var(--text-dark);
}
.log-divider {
    border: 0;
    border-top: 1px dashed var(--border-color);
    margin-top: 15px;
    margin-bottom: 0;
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

/* REMOVED: All .alert-severity-badge and specific alert badge styles as they are no longer used */
/* REMOVED: .badge-count, .badge-none, .badge-alerts as they were related to alert display */

/* Responsive Adjustments */
@media (max-width: 768px) {
    .simulator-controls {
        flex-direction: column;
        gap: 15px;
    }
    .action-button {
        width: 100%;
    }
    .action-button.mr-4 {
        margin-right: 0; /* Remove horizontal margin for stacking */
    }
}
</style>
