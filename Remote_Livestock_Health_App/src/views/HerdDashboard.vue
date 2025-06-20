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
            <!-- New: Summary Statistics Section -->
            <div class="card summary-card mb-8">
                <h3 class="card-title-small">Herd Overview</h3>
                <div class="summary-grid">
                    <div class="summary-item">
                        <i class="fa-solid fa-cow summary-icon"></i>
                        <span class="summary-value">{{ filteredAndSortedCattle.length }}</span>
                        <span class="summary-label">Total Cattle</span>
                    </div>
                    <div class="summary-item ">
                        <i class="fa-solid fa-heart-pulse summary-icon"></i>
                        <span class="summary-value">{{ healthyCattleCount }}</span>
                        <span class="summary-label">Healthy</span>
                    </div>
                    <div class="summary-item ">
                        <i class="fa-solid fa-skull-crossbones summary-icon"></i>
                        <span class="summary-value">{{ unhealthyCattleCount }}</span>
                        <span class="summary-label">Unhealthy</span>
                    </div>
                    <div class="summary-item ">
                        <i class="fa-solid fa-eye summary-icon"></i>
                        <span class="summary-value">{{ observationCattleCount }}</span>
                        <span class="summary-label">Under Observation</span>
                    </div>
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
                            <option value="Observation">Under Observation</option>
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
                            <option value="timestamp">Last Updated</option>
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
                            <th @click="sortBy('riskLevel')">Risk Level <i :class="classSortIcon('riskLevel')"></i></th>
                            <th @click="sortBy('input_data_snapshot.breed_type')">Breed Type <i :class="getSortIcon('input_data_snapshot.breed_type')"></i></th>
                            <th @click="sortBy('alerts.length')">Alerts <i :class="getSortIcon('alerts.length')"></i></th>
                            <th @click="sortBy('timestamp')">Last Updated <i :class="getSortIcon('timestamp')"></i></th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Added @click to trigger modal on row click -->
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
                            <td data-label="Breed Type">{{ cattle.input_data_snapshot?.breed_type || 'N/A' }}</td>
                            <td data-label="Alerts">
                                <span v-if="cattle.alerts && cattle.alerts.length > 0" class="badge-count badge-alerts">
                                    {{ cattle.alerts.length }}
                                </span>
                                <span v-else class="badge-count badge-none">0</span>
                            </td>
                            <td data-label="Last Updated">{{ formatTimestamp(cattle.timestamp) }}</td>
                            <td data-label="Actions">
                                <!-- Kept the button for explicit click, though row is also clickable -->
                                <button @click.stop="openDetailsModal(cattle)" class="action-btn">View Details</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <!-- Enhanced no-data message -->
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
                <h3 class="modal-title">Details for {{ selectedCattleDetails.cattle_id }}</h3>
                <div class="modal-body">
                    <div class="modal-info-grid">
                        <p><strong>Last Updated:</strong> <span>{{ formatTimestamp(selectedCattleDetails.timestamp) }}</span></p>
                        <p><strong>Health Status:</strong> 
                            <span :class="['status-badge', healthClass(selectedCattleDetails.healthStatusDisplay)]">
                                {{ selectedCattleDetails.healthStatusDisplay }}
                            </span>
                        </p>
                        <p><strong>Risk Level:</strong> 
                            <span :class="['risk-badge', getRiskClass(selectedCattleDetails.riskLevel)]">
                                {{ selectedCattleDetails.riskLevel }}
                            </span>
                        </p>
                        <p><strong>Breed Type:</strong> <span>{{ selectedCattleDetails.input_data_snapshot?.breed_type || 'N/A' }}</span></p>
                        <p><strong>Confidence:</strong> <span>{{ selectedCattleDetails.monitoring_results?.confidence || 'N/A' }}</span></p>
                    </div>

                    <h4>Raw Input Data:</h4>
                    <pre class="raw-data-display">{{ JSON.stringify(selectedCattleDetails.input_data_snapshot, null, 2) }}</pre>

                    <h4 v-if="selectedCattleDetails.specific_diseases_detected?.length > 0">Detected Diseases:</h4>
                    <ul v-if="selectedCattleDetails.specific_diseases_detected?.length > 0" class="disease-list">
                        <li v-for="disease in selectedCattleDetails.specific_diseases_detected" :key="disease">
                            <i class="fa-solid fa-virus"></i> {{ disease }}
                        </li>
                    </ul>
                    <p v-else class="no-disease-message">No specific diseases detected.</p>

                    <h4 v-if="selectedCattleDetails.alerts?.length > 0">Active Alerts:</h4>
                    <ul v-if="selectedCattleDetails.alerts?.length > 0" class="alerts-list">
                        <li v-for="alert in selectedCattleDetails.alerts" :key="alert.id">
                            <span :class="['alert-severity-badge', getAlertSeverityClass(alert.severity)]">
                                {{ alert.severity }}
                            </span>
                            {{ alert.message }}
                        </li>
                    </ul>
                    <p v-else class="no-alert-message">No active alerts for this cattle.</p>
                    
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
import { store } from '../main.js';
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

// Debug logs!
console.log('HerdDashboard: Component loaded.');
watch(() => store.cattleData, (newValue) => {
    console.log('HerdDashboard: store.cattleData updated!', newValue.length, 'items.');
    // console.log('HerdDashboard: Full cattleData:', JSON.parse(JSON.stringify(newValue))); // Keep this commented for cleaner console unless debugging specific data issues
}, { immediate: true });


// Computed properties for summary statistics
const latestCattleDataProcessed = computed(() => {
    const latestEntries = {};
    (store.cattleData || []).forEach(cattle => {
        if (cattle.monitoring_results && cattle.monitoring_results.health_status && cattle.cattle_id) {
            if (!latestEntries[cattle.cattle_id] || new Date(cattle.timestamp) > new Date(latestEntries[cattle.cattle_id].timestamp)) {
                latestEntries[cattle.cattle_id] = cattle;
            }
        }
    });

    return Object.values(latestEntries).map(cattle => {
        const healthStatus = cattle.monitoring_results.health_status.toLowerCase();
        const riskLevel = cattle.monitoring_results.risk_level.toLowerCase();

        let healthStatusDisplay = '';
        if (healthStatus === 'healthy' && (riskLevel === 'low' || riskLevel === 'low-medium')) {
            healthStatusDisplay = 'Healthy';
        } else if (healthStatus === 'unhealthy' && (riskLevel === 'critical' || riskLevel === 'high')) {
            healthStatusDisplay = 'Unhealthy';
        } else {
            healthStatusDisplay = 'Observation'; // All other cases for the filter dropdown
        }

        return {
            ...cattle,
            healthStatusDisplay: healthStatusDisplay,
            riskLevel: cattle.monitoring_results.risk_level, // Keep original risk level for sorting/display
            timestamp: cattle.timestamp
        };
    });
});


const healthyCattleCount = computed(() => {
    return latestCattleDataProcessed.value.filter(c => c.healthStatusDisplay === 'Healthy').length;
});

const unhealthyCattleCount = computed(() => {
    return latestCattleDataProcessed.value.filter(c => c.healthStatusDisplay === 'Unhealthy').length;
});

const observationCattleCount = computed(() => {
    return latestCattleDataProcessed.value.filter(c => c.healthStatusDisplay === 'Observation').length;
});


// Filter and sort cattle data
const filteredAndSortedCattle = computed(() => {
    let data = [...latestCattleDataProcessed.value]; // Use the already processed data

    // 1. Filter
    if (searchTerm.value) {
        const lowerSearchTerm = searchTerm.value.toLowerCase();
        data = data.filter(cattle =>
            cattle.cattle_id.toLowerCase().includes(lowerSearchTerm) ||
            cattle.input_data_snapshot?.breed_type?.toLowerCase().includes(lowerSearchTerm)
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

        // Special handling for `healthStatusDisplay` and `riskLevel` for proper ordering
        if (sortByField.value === 'healthStatusDisplay') {
            const statusOrder = {'Healthy': 1, 'Observation': 2, 'Unhealthy': 3};
            valA = statusOrder[a.healthStatusDisplay] || 99;
            valB = statusOrder[b.healthStatusDisplay] || 99;
        } else if (sortByField.value === 'riskLevel') {
            const levels = { 'Low': 1, 'Low-Medium': 2, 'Medium': 3, 'High': 4, 'Critical': 5 };
            valA = levels[a.riskLevel] || 0;
            valB = levels[b.riskLevel] || 0;
        } else if (sortByField.value === 'alerts.length') {
            valA = (a.alerts || []).length;
            valB = (b.alerts || []).length;
        } else {
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

// Pagination
const totalPages = computed(() => Math.ceil(filteredAndSortedCattle.value.length / itemsPerPage));

const paginatedCattle = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return filteredAndSortedCattle.value.slice(start, end);
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

// Reset page to 1 when filters or search change
watch([searchTerm, filterStatus], () => {
    currentPage.value = 1;
});

// Sorting logic
const sortBy = (field) => {
    if (sortByField.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
    } else {
        sortByField.value = field;
        sortDirection.value = 'asc'; // Default to ascending when changing field
    }
};

const getSortIcon = (field) => {
    if (sortByField.value === field) {
        return sortDirection.value === 'asc' ? 'fa-solid fa-sort-up' : 'fa-solid fa-sort-down';
    }
    return 'fa-solid fa-sort'; // Default icon
};

// Styling helpers
const getStatusClass = (status) => {
    return status?.toLowerCase() === 'unhealthy' ? 'status-unhealthy' : 'status-healthy';
};
function healthClass(statusDisplay) { // This function is used by the template
    if (statusDisplay === 'Healthy') return 'status-healthy';
    if (statusDisplay === 'Unhealthy') return 'status-unhealthy';
    if (statusDisplay === 'Observation') return 'status-observation';
    return ''; // Default
}

const getRiskClass = (risk) => {
    return `risk-${risk?.toLowerCase().replace(' ', '-')}`;
};

const getAlertSeverityClass = (severity) => {
    return `alert-severity-${severity?.toLowerCase().replace(' ', '-')}`;
};

// Modals
const openDetailsModal = (cattle) => {
    selectedCattleDetails.value = cattle;
    showDetailsModal.value = true;
};

const closeDetailsModal = () => {
    showDetailsModal.value = false;
    selectedCattleDetails.value = null;
};

const goToCattleInformation = (cattleId) => {
    closeDetailsModal(); // Close modal before navigating
    router.push({ name: 'CattleInformation', params: { id: cattleId } });
};


const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    // Assuming timestamp is in "YYYY-MM-DD HH:MM:SS" format from Flask
    return new Date(timestamp).toLocaleString();
};

</script>

<style scoped>
/* Define spacing classes explicitly */
.mb-8 { margin-bottom: 2rem; } /* Equivalent to mb-8 */
.mb-4 { margin-bottom: 1rem; } /* Equivalent to mb-4 */
.mt-6 { margin-top: 1.5rem; } /* Equivalent to mt-6 */
.mr-2 { margin-right: 0.5rem; } /* Equivalent to mr-2 */
.px-6 { padding-left: 1.5rem; padding-right: 1.5rem; } /* Equivalent to px-6 */
.pt-6 { padding-top: 1.5rem; } /* Equivalent to pt-6 */
.p-0 { padding: 0 !important; } /* Equivalent to p-0, !important to override .card's default padding */
.ml-2 { margin-left: 0.5rem; } /* For the sort direction select */
.icon-margin-left { margin-left: 0.25rem; } /* For icons like in action button, replacing ml-1 */
.mb-4 { margin-bottom: 1rem; } /* Added for consistency */
.mb-2 { margin-bottom: 0.5rem; } /* Added for consistency */


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

/* Summary Card Styles (New) */
.summary-card {
    padding: 30px;
    text-align: center;
    background: linear-gradient(135deg, #e0f7fa, #e8f5e9); /* Softer, inviting gradient */
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
    justify-content: center; /* Center content vertically too */
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid var(--border-color); /* Added subtle border */
}
.summary-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}
.summary-icon {
    font-size: 2.2em;
    color: var(--primary-color); /* Default icon color */
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
/* Backgrounds for specific summary items - Ensure Text is Light for Dark BGs */
.summary-item.status-healthy-bg { background-color: var(--success-color); }
.summary-item.status-healthy-bg .summary-icon,
.summary-item.status-healthy-bg .summary-value,
.summary-item.status-healthy-bg .summary-label { color: var(--text-light); }

.summary-item.status-unhealthy-bg { background-color: var(--danger-color); }
.summary-item.status-unhealthy-bg .summary-icon,
.summary-item.status-unhealthy-bg .summary-value,
.summary-item.status-unhealthy-bg .summary-label { color: var(--text-light); }

.summary-item.status-observation-bg { background-color: var(--warning-color); } /* Light background */
.summary-item.status-observation-bg .summary-icon,
.summary-item.status-observation-bg .summary-value,
.summary-item.status-observation-bg .summary-label { color: var(--text-dark); } /* Dark text for light background */


/* Controls Card & Grid (existing) */
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

/* Table Specific Styles (existing, with badge contrast fix) */
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
    transition: background-color 0.2s ease; /* Added transition for hover */
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

/* IMPROVED: Clickable rows with hover effect */
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


/* Badges for status and risk - IMPROVED CONTRAST */
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
/* Health Status Badges - Text color explicitly set for contrast */
.status-healthy { background-color: var(--success-color); color: #FFFFFF; }
.status-unhealthy { background-color: var(--danger-color); color: #FFFFFF; }
.status-observation { background-color: var(--warning-color); color: var(--text-dark); }


/* Risk Badges (your existing colors, good contrast) */
.risk-badge.critical { background-color: var(--alert-critical-border); color: #FFFFFF; }
.risk-badge.high { background-color: var(--alert-high-border); color: #FFFFFF; }
.risk-badge.medium { background-color: var(--alert-medium-border); color: var(--text-dark); }
.risk-badge.low-medium { background-color: var(--alert-low-medium-border); color: #FFFFFF; }
.risk-badge.low { background-color: var(--alert-low-border); color: var(--text-dark); } /* Changed to dark text on light green */

.badge-count {
    background-color: var(--secondary-color);
    color: var(--text-light);
    padding: 4px 8px;
    border-radius: 10px;
    font-size: 0.75em;
    font-weight: bold;
    display: inline-block;
    min-width: 25px;
    text-align: center;
}
.badge-none {
    background-color: #CFD8DC;
}
.badge-alerts {
    background-color: var(--danger-color); /* Highlight for actual alerts */
    color: white;
}


/* Action Button - FURTHER IMPROVED STYLING */
.action-btn {
    background: linear-gradient(145deg, var(--info-color), var(--accent-dark)); /* Subtle gradient */
    color: var(--text-light);
    padding: 8px 15px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
    font-weight: 600;
    transition: all 0.25s ease; /* Smoother transition */
    box-shadow: 0 4px 10px rgba(0,0,0,0.15); /* More pronounced shadow */
    display: inline-flex; /* For icon alignment if needed */
    align-items: center;
    justify-content: center;
}
.action-btn:hover {
    background: linear-gradient(145deg, var(--accent-dark), var(--info-color)); /* Reverse gradient on hover */
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.2);
}
.action-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* Pagination Styles (existing, with disabled fix) */
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

/* Modal Styles (New & Refined) */
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
    max-width: 750px; /* Slightly wider modal */
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
.modal-info-grid { /* New grid for basic info in modal */
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
.modal-info-grid span { /* Style for the values in the info grid */
    font-weight: 500;
    color: var(--text-dark);
}

.raw-data-display {
    background-color: #eceff1;
    padding: 15px; /* Slightly more padding */
    border-radius: 8px;
    white-space: pre-wrap;
    word-break: break-all;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
    font-size: 0.85em;
    color: #37474F;
    border: 1px solid #CFD8DC;
    max-height: 250px; /* Increased height */
    overflow-y: auto;
    margin-top: 10px;
    margin-bottom: 20px;
}
.modal-body h4 {
    font-size: 1.25em; /* Slightly larger heading */
    font-weight: 600;
    color: var(--primary-color); /* Primary color for headings */
    margin-top: 25px; /* More space */
    margin-bottom: 12px;
}
.disease-list, .alerts-list {
    list-style: none;
    padding-left: 0;
    margin-bottom: 20px;
}
.disease-list li, .alerts-list li {
    background-color: #fcfcfc;
    padding: 10px 15px; /* More padding */
    border-radius: 8px;
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start; /* Align icon to top if text wraps */
    gap: 10px;
    border: 1px solid #e0e0e0;
    color: var(--text-dark);
    font-size: 0.95em;
}
.disease-list li i.fa-virus { /* Icon for disease list */
    color: var(--danger-color);
    font-size: 1.1em;
    margin-top: 2px;
}
.alerts-list li span.alert-severity-badge { /* Ensure badge has margin */
    margin-right: 5px;
}
/* No data messages in modal */
.no-disease-message, .no-alert-message {
    color: var(--text-secondary);
    font-style: italic;
    margin-left: 10px;
    font-size: 0.95em;
    margin-bottom: 20px;
}

.alert-severity-badge { /* Reusing existing styles for severity badges */
    padding: 4px 8px;
    border-radius: 10px;
    font-size: 0.7em;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-block;
    min-width: 60px;
    text-align: center;
}
/* Specific text colors for alert severity badges */
.alert-severity-critical { background-color: var(--alert-critical-border); color: #FFFFFF; }
.alert-severity-high { background-color: var(--alert-high-border); color: #FFFFFF; }
.alert-severity-medium { background-color: var(--alert-medium-border); color: var(--text-dark); }
.alert-severity-low-medium { background-color: var(--alert-low-medium-border); color: #FFFFFF; }
.alert-severity-low { background-color: var(--alert-low-border); color: var(--text-dark); }


.modal-action-btn {
    background: linear-gradient(145deg, var(--primary-color), var(--primary-dark)); /* Use primary colors for modal actions */
    color: var(--text-light);
    padding: 12px 25px; /* More padding */
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
    background: linear-gradient(145deg, var(--primary-dark), var(--primary-color));
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

/* Responsive Table (existing, no changes except modal adjustments) */
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
