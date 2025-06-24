<template>
    <div class="content-area">
        <h2 class="card-title">Herd Dashboard</h2>
        <div v-if="store.loading" class="message-center loading-message">
            <i class="fa-solid fa-spinner fa-spin fa-2x"></i> Loading herd data...
        </div>
        <div v-else-if="store.error" class="error-message">
            <p><strong>Error:</strong> {{ store.error }}</p>
            <p>Please check your Flask API status and network connection.</p>
        </div>

        <div v-else>
            <!-- Summary Statistics Section (Removed Observation) -->
            <div class="card summary-card mb-8">
                <h3 class="card-title-small">Herd Overview</h3>
                <div class="summary-grid">
                    <div class="summary-item">
                        <i class="fa-solid fa-cow summary-icon"></i>
                        <span class="summary-value">{{ filteredAndSortedCattle.length }}</span>
                        <span class="summary-label">Total Cattle</span>
                    </div>
                    <div class="summary-item status-healthy-bg">
                        <i class="fa-solid fa-heart-pulse summary-icon"></i>
                        <span class="summary-value">{{ healthyCattleCount }}</span>
                        <span class="summary-label">Healthy</span>
                    </div>
                    <div class="summary-item status-unhealthy-bg">
                        <i class="fa-solid fa-skull-crossbones summary-icon"></i>
                        <span class="summary-value">{{ unhealthyCattleCount }}</span>
                        <span class="summary-label">Unhealthy</span>
                    </div>
                    <!-- REMOVED: The "Under Observation" summary item completely -->
                </div>
            </div>

            <div class="card controls-card mb-8">
                <h3 class="card-title-small">Herd Management Filters</h3>
                <div class="controls-grid">
                    <div class="filter-group">
                        <label for="health-status-filter" class="control-label">Filter by Health Status:</label>
                        <select id="health-status-filter" v-model="filterStatus" class="control-select">
                            <option value="">All</option>
                            <option value="Healthy">Healthy</option>
                            <option value="Unhealthy">Unhealthy</option>
                            <!-- REMOVED: <option value="Observation">Under Observation</option> -->
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="animal-id-search" class="control-label">Search by Cattle ID:</label>
                        <input type="text" id="animal-id-search" v-model="searchTerm" placeholder="Enter Cattle ID" class="control-input" />
                    </div>
                    <div class="filter-group sort-group">
                        <label for="sort-by" class="control-label">Sort By:</label>
                        <select id="sort-by" v-model="sortByField" class="control-select">
                            <option value="cattle_id">Cattle ID</option>
                            <option value="healthStatusDisplay">Health Status</option>
                            <option value="riskLevel">Risk Level</option>
                            <option value="breedTypeDisplay">Breed Type</option>
                            <option value="timestamp">Last Updated</option>
                            <!-- REMOVED: Alerts option from sorting -->
                        </select>
                        <select v-model="sortDirection" class="control-select ml-2">
                            <option value="asc">Ascending</option>
                            <option value="desc">Descending</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="card p-0 overflow-x-auto">
                <h3 class="card-title-small px-6 pt-6">Cattle Roster ({{ filteredAndSortedCattle.length }} entries)</h3>
                <table v-if="filteredAndSortedCattle.length > 0" class="data-table">
                    <thead>
                        <tr>
                            <th @click="sortBy('cattle_id')">Cattle ID <i :class="getSortIcon('cattle_id')"></i></th>
                            <th @click="sortBy('healthStatusDisplay')">Health Status <i :class="getSortIcon('healthStatusDisplay')"></i></th>
                            <th @click="sortBy('riskLevel')">Risk Level <i :class="getSortIcon('riskLevel')"></i></th>
                            <th @click="sortBy('breedTypeDisplay')">Breed Type <i :class="getSortIcon('breedTypeDisplay')"></i></th>
                            <th @click="sortBy('timestamp')">Last Updated <i :class="getSortIcon('timestamp')"></i></th>
                            <th>Actions</th>
                            <!-- REMOVED: Alerts count column -->
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="cattle in paginatedCattle" :key="cattle.id" @click="openDetailsModal(cattle)" class="data-row-clickable">
                            <td data-label="Cattle ID">{{ cattle.cattle_id }}</td>
                            <td data-label="Health Status">
                                <span :class="['status-badge', healthClass(cattle.healthStatusDisplay)]">
                                    {{ cattle.healthStatusDisplay }}
                                </span>
                            </td>
                            <td data-label="Risk Level">
                                <span :class="['risk-badge', getRiskClass(cattle.riskLevel)]">
                                    {{ cattle.riskLevel }}
                                </span>
                            </td>
                            <td data-label="Breed Type">{{ cattle.breedTypeDisplay }}</td>
                            <td data-label="Last Updated">{{ formatTimestamp(cattle.timestamp) }}</td>
                            <td data-label="Actions">
                                <button @click.stop="openDetailsModal(cattle)" class="action-btn">View Details</button>
                            </td>
                            <!-- REMOVED: Alerts count column -->
                        </tr>
                    </tbody>
                </table>
                <div v-else class="message-center no-data-message">
                    <i class="fa-solid fa-cow fa-3x mb-4"></i>
                    <p>No cattle data available. Start the real-time simulator or add data manually!</p>
                    <p class="text-secondary">Once data arrives, it will appear here instantly.</p>
                </div>
            </div>

            <div class="pagination-controls mt-6">
                <button @click="prevPage" :disabled="currentPage === 1" class="pagination-button">Previous</button>
                <span>Page {{ currentPage }} of {{ totalPages }}</span>
                <button @click="nextPage" :disabled="currentPage === totalPages" class="pagination-button">Next</button>
            </div>
        </div>

        <!-- Cattle Details Modal -->
        <div v-if="showDetailsModal && selectedCattleDetails" class="modal-overlay" @click.self="closeDetailsModal">
            <div class="modal-content">
                <button class="modal-close-button" @click="closeDetailsModal">
                    <i class="fa-solid fa-xmark"></i>
                </button>
                <!-- FIXED: Modal Title -->
                <h3 class="modal-title">Details for {{ selectedCattleDetails.cattle_id }}</h3>
                <div class="modal-body">
                    <div class="modal-info-grid">
                        <p><strong>Last Updated: </strong> <span>{{ formatTimestamp(selectedCattleDetails.timestamp) }}</span></p>
                        <p><strong>Health Status: </strong> 
                            <span :class="['status-badge', healthClass(selectedCattleDetails.healthStatusDisplay)]">
                                {{ selectedCattleDetails.healthStatusDisplay }}
                            </span>
                        </p>
                        <p><strong>Risk Level:</strong> 
                            <span :class="['risk-badge', getRiskClass(selectedCattleDetails.riskLevel)]">
                                {{ selectedCattleDetails.riskLevel }}
                            </span>
                        </p>
                        <p><strong>Breed Type: </strong> <span>{{ selectedCattleDetails.breedTypeDisplay }}</span></p>
                        <p><strong>Confidence: </strong> <span>{{ selectedCattleDetails.monitoring_results?.confidence || 'N/A' }}</span></p>
                    </div>

                    <!-- RE-ADDED: Detected Diseases section -->
                    <h4 v-if="selectedCattleDetails.specific_diseases_detected?.length > 0">Detected Diseases:</h4>
                    <ul v-if="selectedCattleDetails.specific_diseases_detected?.length > 0" class="disease-list">
                        <li v-for="disease in selectedCattleDetails.specific_diseases_detected" :key="disease">
                            <i class="fa-solid fa-virus"></i> {{ disease }}
                        </li>
                    </ul>
                    <p v-else class="no-disease-message">No specific diseases detected.</p>

                    <!-- RE-ADDED & FIXED: Observations from animal data (alerts) -->
                    <h4 v-if="selectedCattleDetails.alerts?.length > 0">Observations from animal data:</h4>
                    <div v-if="selectedCattleDetails.alerts?.length > 0" class="alerts-observations-list">
                        <div v-for="alert in selectedCattleDetails.alerts" :key="alert.message" :class="getAlertClass(alert.severity)">
                            <p> {{ alert.message }}</p>
                            <p v-if="alert.indicator"><strong>Indicator: </strong> {{ alert.indicator }}</p>
                        </div>
                    </div>
                    <p v-else class="no-alert-message">No specific observations for this cattle.</p>

                    <h4>Raw Input Data: </h4>
                    <pre class="raw-data-display">{{ JSON.stringify(selectedCattleDetails.input_data_snapshot, null, 2) }}</pre>
                    <button @click="goToCattleInformation(selectedCattleDetails.cattle_id)" class="modal-action-btn mt-4">
                        Go to Detailed Log <i class="fa-solid fa-arrow-right icon-margin-left"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { store } from '../main.js'; // Import the global store
import { useRouter } from 'vue-router';

const router = useRouter();

const searchTerm = ref('');
const filterStatus = ref('');
const sortByField = ref('timestamp');
const sortDirection = ref('desc'); // 'asc' or 'desc'
const itemsPerPage = 10;
const currentPage = ref(1);

// Modal state
const showDetailsModal = ref(false);
const selectedCattleDetails = ref(null);
// REMOVED: predictionResult = ref(null); // No longer needed as we use selectedCattleDetails directly


console.log('HerdDashboard: Component loaded.');
watch(() => store.cattleData, (newValue) => {
    console.log('HerdDashboard: store.cattleData updated!', newValue.length, 'items.');
}, { immediate: true });


// Computed properties for summary statistics (UPDATED for breed type and removed Observation)
const latestCattleDataProcessed = computed(() => {
    const latestEntries = new Map(); // Use Map for correct unique key handling and robustness
    // Ensure store.cattleData is an array before iterating
    (store.cattleData || []).forEach(cattle => {
        if (cattle.monitoring_results && cattle.monitoring_results.health_status && cattle.cattle_id) {
            const existing = latestEntries.get(cattle.cattle_id); // Get existing entry from Map
            if (!existing || new Date(cattle.timestamp) > new Date(existing.timestamp)) {
                latestEntries.set(cattle.cattle_id, cattle); // Use Map.set for correct update
            }
        }
    });

    return Array.from(latestEntries.values()).map(cattle => { // Ensure return is an array from map values
        const healthStatus = cattle.monitoring_results.health_status;
        const riskLevel = cattle.monitoring_results.risk_level;
        const rawBreedType = cattle.input_data_snapshot?.breed_type;

        // Logic to categorize breed type - No "N/A", always "Normal Breed" or "Cross Breed"
        let breedTypeDisplay = 'Normal Breed'; // Default to Normal Breed
        if (rawBreedType) {
            const lowerBreed = rawBreedType.toLowerCase();
            // If it contains "cross" or has more than one word, categorize as "Cross Breed"
            // Example: "Jersey Cross", "Holstein Friesian", "Mixed Breed" -> "Cross Breed"
            if (lowerBreed.includes('cross') || lowerBreed.split(' ').length > 1) {
                breedTypeDisplay = 'Cross Breed';
            } else {
                breedTypeDisplay = 'Normal Breed';
            }
        }

        return {
            ...cattle,
            healthStatusDisplay: healthStatus.charAt(0).toUpperCase() + healthStatus.slice(1).toLowerCase(), 
            riskLevel: riskLevel,
            breedTypeDisplay: breedTypeDisplay, // Now always "Normal Breed" or "Cross Breed"
            timestamp: cattle.timestamp
        };
    });
});

const healthyCattleCount = computed(() => {
    // Defensive check: Ensure latestCattleDataProcessed.value is an array
    return (latestCattleDataProcessed.value || []).filter(c => c.healthStatusDisplay === 'Healthy').length;
});

const unhealthyCattleCount = computed(() => {
    // Defensive check: Ensure latestCattleDataProcessed.value is an array
    return (latestCattleDataProcessed.value || []).filter(c => c.healthStatusDisplay === 'Unhealthy').length;
});



// Filter and sort cattle data (UPDATED for breed type and removed Observation & Alerts.length)
const filteredAndSortedCattle = computed(() => {
    // DEFENSIVE FIX: Ensure data is always an array before starting operations
    let data = [...(latestCattleDataProcessed.value || [])];

    // 1. Filter
    if (searchTerm.value) {
        const lowerSearchTerm = searchTerm.value.toLowerCase();
        data = data.filter(cattle =>
            cattle.cattle_id.toLowerCase().includes(lowerSearchTerm) ||
            cattle.breedTypeDisplay.toLowerCase().includes(lowerSearchTerm) // Search simplified breed
        );
    }

    if (filterStatus.value) {
        data = data.filter(cattle =>
            cattle.healthStatusDisplay === filterStatus.value
        );
    }

    // 2. Sort
    data.sort((a, b) => {
        let valA, valB;

        const getNestedValue = (obj, path) => {
            return path.split('.').reduce((acc, part) => acc && acc[part], obj);
        };

        // Special handling for `healthStatusDisplay`, `riskLevel`, and `breedTypeDisplay` for proper ordering
        if (sortByField.value === 'healthStatusDisplay') {
            // Define explicit order for sorting: Healthy before Unhealthy
            const statusOrder = {'Healthy': 1, 'Unhealthy': 2}; 
            valA = statusOrder[a.healthStatusDisplay] || 99; // Fallback for unexpected status
            valB = statusOrder[b.healthStatusDisplay] || 99;
        } else if (sortByField.value === 'riskLevel') {
            const levels = { 'Low': 1, 'Low-Medium': 2, 'Medium': 3, 'High': 4, 'Critical': 5 };
            valA = levels[a.riskLevel] || 0;
            valB = levels[b.riskLevel] || 0;
        } else if (sortByField.value === 'breedTypeDisplay') { // Custom sort for breed type
            const breedOrder = {'Normal Breed': 1, 'Cross Breed': 2}; // Only these two
            valA = breedOrder[a.breedTypeDisplay] || 99;
            valB = breedOrder[b.breedTypeDisplay] || 99;
        } 
        // REMOVED: Alerts.length sorting
        else {
            valA = getNestedValue(a, sortByField.value);
            valB = getNestedValue(b, sortByField.value);
        }

        if (valA === undefined || valA === null) valA = sortDirection.value === 'asc' ? Infinity : -Infinity;
        if (valB === undefined || valB === null) valB = sortDirection.value === 'asc' ? Infinity : -Infinity;

        if (typeof valA === 'string') {
            return sortDirection.value === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
        } else {
            return sortDirection.value === 'asc' ? valA - valB : valB - valA;
        }
    });

    return data;
});

// Pagination and other functions remain the same
const totalPages = computed(() => Math.ceil(filteredAndSortedCattle.value.length / itemsPerPage));

const paginatedCattle = computed(() => {
    // Defensive check for paginatedCattle too
    const dataToPaginate = filteredAndSortedCattle.value || [];
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return dataToPaginate.slice(start, end);
});

const prevPage = () => {
    if (currentPage.value > 1) {
        currentPage.value--;
    }
};

const nextPage = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value++;
    }
};

watch([searchTerm, filterStatus], () => {
    currentPage.value = 1;
});

const sortBy = (field) => {
    if (sortByField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
    } else {
        sortByField.value = field;
        sortDirection.value = 'asc';
    }
};

const getSortIcon = (field) => {
    if (sortByField.value === field) {
        return sortDirection.value === 'asc' ? 'fa-solid fa-sort-up' : 'fa-solid fa-sort-down';
    }
    return 'fa-solid fa-sort';
};

function healthClass(statusDisplay) {
    if (statusDisplay === 'Healthy') return 'status-healthy';
    if (statusDisplay === 'Unhealthy') return 'status-unhealthy';
    return ''; 
}

const getRiskClass = (risk) => {
    return `risk-${risk?.toLowerCase().replace(' ', '-')}`;
};

// NEW/FIXED: Function to get specific alert class for observations
const getAlertClass = (severity) => {
    return `alert-observation-${severity?.toLowerCase().replace(' ', '-')}`;
};


// Modals functions remain the same
const openDetailsModal = (cattle) => {
    selectedCattleDetails.value = cattle;
    showDetailsModal.value = true;
};

const closeDetailsModal = () => {
    showDetailsModal.value = false;
    selectedCattleDetails.value = null;
};

const goToCattleInformation = (cattleId) => {
    closeDetailsModal();
    router.push({ name: 'CattleInformation', params: { id: cattleId } });
};

const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
};

</script>

<style scoped>
/* Define spacing classes explicitly */
.mb-8 { margin-bottom: 2rem; }
.mb-4 { margin-bottom: 1rem; }
.mt-6 { margin-top: 1.5rem; }
.mr-2 { margin-right: 0.5rem; }
.px-6 { padding-left: 1.5rem; padding-right: 1.5rem; }
.pt-6 { padding-top: 1.5rem; }
.p-0 { padding: 0 !important; }
.ml-2 { margin-left: 0.5rem; }
.icon-margin-left { margin-left: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }


/* General component styling */
.card-title-small {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
    position: relative;
}
.card-title-small::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -1px;
    width: 40px;
    height: 3px;
    background-color: var(--primary-color);
    border-radius: 1.5px;
}

/* Summary Card Styles */
.summary-card {
    padding: 30px;
    text-align: center;
    background: linear-gradient(135deg, #e0f7fa, #e8f5e9);
    border: 1px solid #c8e6c9;
}
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
    margin-top: 20px;
}
.summary-item {
    background-color: var(--card-bg);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid var(--border-color);
}
.summary-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}
.summary-icon {
    font-size: 2.2em;
    color: var(--primary-color);
    margin-bottom: 10px;
}
.summary-value {
    font-size: 2.5em;
    font-weight: 800;
    color: var(--text-dark);
    line-height: 1;
}
.summary-label {
    font-size: 0.95em;
    color: var(--text-secondary);
    margin-top: 5px;
    font-weight: 500;
}
.summary-item.status-healthy-bg { background-color: var(--success-color); }
.summary-item.status-healthy-bg .summary-icon,
.summary-item.status-healthy-bg .summary-value,
.summary-item.status-healthy-bg .summary-label { color: var(--text-light); }

.summary-item.status-unhealthy-bg { background-color: var(--danger-color); }
.summary-item.status-unhealthy-bg .summary-icon,
.summary-item.status-unhealthy-bg .summary-value,
.summary-item.status-unhealthy-bg .summary-label { color: var(--text-light); }

/* No .summary-item.status-observation-bg related styles anymore */


/* Controls Card & Grid */
.controls-card {
    padding: 30px;
}
.controls-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 20px;
}
.filter-group, .sort-group {
    display: flex;
    align-items: center;
    gap: 10px;
}
.control-label {
    font-weight: 600;
    color: var(--text-dark);
    white-space: nowrap;
    font-size: 0.95em;
}
.control-input, .control-select {
    flex-grow: 1;
    padding: 10px 15px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background-color: var(--card-bg);
    color: var(--text-dark);
    font-size: 1em;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.control-input:focus, .control-select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
}

/* Table Specific Styles */
.table-controls {
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
    flex-wrap: wrap;
    justify-content: flex-end;
}
.search-input, .filter-select {
    padding: 10px 15px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-size: 1em;
    color: var(--text-dark);
    background-color: var(--background-light);
    flex: 1;
    min-width: 150px;
}
.search-input:focus, .filter-select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
}
.overflow-x-auto {
    overflow-x: auto;
    width: 100%;
}
.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    background-color: var(--background-light);
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border-radius: 12px;
    overflow: hidden;
}
.data-table th, .data-table td {
    padding: 15px 20px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}
.data-table thead {
    background-color: var(--primary-color);
    color: var(--text-light);
}
.data-table th {
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: background-color 0.2s ease;
}
.data-table th:hover {
    background-color: var(--primary-dark);
}
.data-table tbody tr:last-child td {
    border-bottom: none;
}
.data-table tbody tr:nth-child(even) {
    background-color: #F8F8F8;
}

.data-row-clickable {
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.1s ease;
}
.data-row-clickable:hover {
    background-color: #F0F4F7;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.data-row-clickable:active {
    transform: translateY(0);
    box-shadow: none;
}


/* Badges for status and risk */
.status-badge, .risk-badge {
    padding: 6px 12px;
    border-radius: 18px;
    font-size: 0.8em;
    font-weight: 600;
    text-transform: uppercase;
    display: inline-block;
    min-width: 80px;
    text-align: center;
}
/* Health Status Badges - Explicit text color for contrast */
.status-healthy { background-color: var(--success-color); color: var(--text-light); }
.status-unhealthy { background-color: var(--danger-color); color: var(--text-light); }
/* No .status-observation related styling anymore */


/* Risk Badges */
.risk-badge.critical { background-color: var(--alert-critical-border); color: var(--text-light); }
.risk-badge.high { background-color: var(--alert-high-border); color: var(--text-light); }
.risk-badge.medium { background-color: var(--alert-medium-border); color: var(--text-dark); }
.risk-badge.low-medium { background-color: var(--alert-low-medium-border); color: var(--text-light); }
.risk-badge.low { background-color: var(--alert-low-border); color: var(--text-dark); }

/* REMOVED: .badge-count, .badge-none, .badge-alerts styles */


/* Action Button - PRESERVED USER'S STYLES */
.action-btn {
    background: green; /* User's requested background */
    color: var(--text-light);
    padding: 8px 15px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
    font-weight: 600;
    transition: all 0.25s ease;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
.action-btn:hover {
    /* User's requested hover, without explicit background change */
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.2);
}
.action-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* Pagination Styles */
.pagination-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: var(--background-light);
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.pagination-button {
    background-color: var(--secondary-color);
    color: var(--text-light);
    padding: 10px 18px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s ease;
}
.pagination-button:hover:not(:disabled) {
    background-color: #B0BEC5;
}
.pagination-button:disabled {
    background-color: #CFD8DC;
    cursor: not-allowed;
    opacity: 0.6;
}

.no-data-message {
    padding: 30px;
    font-size: 1.1em;
    color: var(--text-muted);
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.no-data-message .fa-cow {
    color: var(--text-secondary);
    margin-bottom: 10px;
}
.no-data-message .text-secondary {
    color: var(--text-secondary);
    font-size: 0.9em;
    margin-top: 5px;
}

/* Modal Styles */
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
.modal-content {
    background-color: var(--card-bg);
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    width: 90%;
    max-width: 750px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
    animation: fadeInScale 0.3s ease-out forwards;
}
.modal-close-button {
    position: absolute;
    top: 15px;
    right: 15px;
    background: none;
    border: none;
    font-size: 1.5em;
    color: var(--text-secondary);
    cursor: pointer;
    transition: color 0.2s ease;
}
.modal-close-button:hover {
    color: var(--danger-color);
}
.modal-title {
    font-size: 1.8em;
    font-weight: 700;
    color: var(--primary-dark);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-color);
}
.modal-body p {
    margin-bottom: 10px;
    font-size: 1em;
    color: var(--text-dark);
}
.modal-body strong {
    color: var(--primary-dark);
}
.modal-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px 30px;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px dashed var(--border-color);
}
.modal-info-grid p {
    margin: 0;
}
.modal-info-grid span {
    font-weight: 500;
    color: var(--text-dark);
}

.raw-data-display {
    background-color: #eceff1;
    padding: 15px;
    border-radius: 8px;
    white-space: pre-wrap;
    word-break: break-all;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
    font-size: 0.85em;
    color: #37474F;
    border: 1px solid #CFD8DC;
    max-height: 250px;
    overflow-y: auto;
    margin-top: 10px;
    margin-bottom: 20px;
}
.modal-body h4 { /* Now only applies to "Raw Input Data" header and future headers */
    font-size: 1.25em;
    font-weight: 600;
    color: var(--primary-color);
    margin-top: 25px;
    margin-bottom: 12px;
}
/* Re-added disease list styles */
.disease-list, .alerts-observations-list { /* Combined style for consistency */
    list-style: none;
    padding-left: 0;
    margin-bottom: 20px;
}
.disease-list li {
    background-color: #fcfcfc;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    border: 1px solid #e0e0e0;
    color: var(--text-dark);
    font-size: 0.95em;
}
.disease-list li i.fa-virus {
    color: var(--danger-color);
    font-size: 1.1em;
    margin-top: 2px;
}
.no-disease-message, .no-alert-message {
    color: var(--text-secondary);
    font-style: italic;
    margin-left: 10px;
    font-size: 0.95em;
    margin-bottom: 20px;
}

/* Styles for the "Observations from animal data" section based on alert severity */
.alerts-observations-list div {
    padding: 12px 15px;
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.95em;
    line-height: 1.4;
    border: 1px solid; /* Generic border for these observation boxes */
}
.alerts-observations-list p {
    margin: 0; /* Reset default paragraph margin */
}

/* Specific alert severity classes for Observations section */
.alert-observation-critical { 
    background-color: var(--alert-critical-bg); 
    color: var(--alert-critical-text); 
    border-color: var(--alert-critical-border);
}
.alert-observation-high { 
    background-color: var(--alert-high-bg); 
    color: var(--alert-high-text); 
    border-color: var(--alert-high-border);
}
.alert-observation-medium { 
    background-color: var(--alert-medium-bg); 
    color: var(--alert-medium-text); 
    border-color: var(--alert-medium-border);
}
.alert-observation-low-medium { 
    background-color: var(--alert-low-medium-bg); 
    color: var(--alert-low-medium-text); 
    border-color: var(--alert-low-medium-border);
}
.alert-observation-low { 
    background-color: var(--alert-low-bg); 
    color: var(--alert-low-text); 
    border-color: var(--alert-low-border);
}


/* Modal Action Button - PRESERVED USER'S STYLES */
.modal-action-btn {
    background: linear-gradient(145deg, var(--primary-color), var(--primary-dark)); /* User's requested gradient */
    color: var(--text-light);
    padding: 12px 25px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 600;
    transition: all 0.25s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.modal-action-btn:hover {
    background: linear-gradient(145deg, var(--primary-dark), var(--primary-color)); /* User's requested hover gradient */
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.2);
}
.modal-action-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* Animations */
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Responsive Table */
@media (max-width: 768px) {
    .summary-grid {
        grid-template-columns: 1fr;
    }
    .table-controls {
        flex-direction: column;
        gap: 10px;
    }
    .data-table thead {
        display: none;
    }
    .data-table, .data-table tbody, .data-table tr, .data-table td {
        display: block;
        width: 100%;
    }
    .data-table tr {
        margin-bottom: 15px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background-color: var(--background-light);
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .data-table td {
        text-align: right;
        padding-left: 50%;
        position: relative;
        border-bottom: 1px dashed var(--border-color);
    }
    .data-table td:last-child {
        border-bottom: none;
    }
    .data-table td::before {
        content: attr(data-label);
        position: absolute;
        left: 15px;
        width: calc(50% - 30px);
        padding-right: 10px;
        white-space: nowrap;
        font-weight: 600;
        text-align: left;
        color: var(--text-dark);
    }
    .pagination-controls {
        flex-direction: column;
        gap: 15px;
    }
    .modal-content {
        padding: 20px;
    }
    .modal-title {
        font-size: 1.5em;
    }
    .modal-close-button {
        font-size: 1.2em;
    }
    .modal-info-grid {
        grid-template-columns: 1fr;
        gap: 10px;
    }
}
</style>
