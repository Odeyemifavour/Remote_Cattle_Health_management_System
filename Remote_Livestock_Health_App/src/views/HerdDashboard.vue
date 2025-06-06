<template>
    <div class="content-area">
        <h2 class="card-title">Herd Dashboard</h2>

        <div v-if="store.loading" class="message-center">
            <i class="fa-solid fa-spinner fa-spin fa-2x"></i> Loading herd data...
        </div>
        <div v-else-if="store.error" class="error-message">
            <i class="fa-solid fa-circle-exclamation mr-2"></i> <span>{{ store.error }}</span>
        </div>
        <div v-else>
            <div class="card controls-card mb-8">
                <h3 class="card-title-small">Herd Management Filters</h3>
                <div class="controls-grid">
                    <div class="filter-group">
                        <label for="health-status-filter" class="control-label">Filter by Health Status:</label>
                        <select id="health-status-filter" v-model="healthStatusFilter" class="control-select">
                            <option value="">All</option>
                            <option value="Healthy">Healthy</option>
                            <option value="Unhealthy">Unhealthy</option>
                            <option value="Observation">Under Observation</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label for="animal-id-search" class="control-label">Search by Cattle ID:</label>
                        <input
                            type="text"
                            id="animal-id-search"
                            v-model="searchQuery"
                            placeholder="Enter Cattle ID"
                            class="control-input"
                        />
                    </div>

                    <div class="filter-group sort-group">
                        <label for="sort-by" class="control-label">Sort By:</label>
                        <select id="sort-by" v-model="sortBy" class="control-select">
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
                <h3 class="card-title-small px-6 pt-6">Cattle Roster ({{ filteredAndSortedLivestock.length }} entries)</h3>
                <table v-if="filteredAndSortedLivestock.length > 0" class="data-table">
                    <thead>
                        <tr>
                            <th>Cattle ID</th>
                            <th>Breed</th>
                            <th>Current Health Status</th>
                            <th>Risk Level</th>
                            <th>Last Update</th>
                            <th>Cattle Info</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="animal in filteredAndSortedLivestock" :key="animal.cattle_id">
                            <td>{{ animal.cattle_id }}</td>
                            <td>{{ animal.raw_data?.breed_type || 'N/A' }}</td>
                            <td>
                                <span :class="['status-badge', healthClass(animal.healthStatusDisplay)]">
                                    {{ animal.healthStatusDisplay }}
                                </span>
                            </td>
                            <td>
                                <span :class="['risk-badge', getRiskClass(animal.riskLevel)]">
                                    {{ animal.riskLevel }}
                                </span>
                            </td>
                            <td>{{ formatTimestamp(animal.timestamp) }}</td>
                            <td>
                                <!-- Link to Prediction Log for detailed view of this cattle ID -->
                                <router-link :to="`/prediction-log`" class="view-details-link">
                                    View Details <i class="fa-solid fa-arrow-right ml-1"></i>
                                </router-link>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <p v-else class="message-center p-6">No livestock data available or matching your criteria.</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { store } from '../main.js'; // Import the global store

// --- Filters and Sort States ---
const healthStatusFilter = ref('');
const searchQuery = ref('');
const sortBy = ref('cattle_id');
const sortDirection = ref('asc');

// --- Computed Property for Latest Cattle Data (similar to DashboardOverview's filteredCattle) ---
const latestCattleData = computed(() => {
    const latestEntries = {};
    store.cattleData.forEach(cattle => {
        // Only consider entries with monitoring results for the dashboard
        if (cattle.monitoring_results && cattle.monitoring_results.health_status && cattle.cattle_id) {
            if (!latestEntries[cattle.cattle_id] || new Date(cattle.timestamp) > new Date(latestEntries[cattle.cattle_id].timestamp)) {
                latestEntries[cattle.cattle_id] = cattle;
            }
        }
    });
    // Map the raw cattle data to a more convenient format for the table/filters
    return Object.values(latestEntries).map(cattle => {
        const healthStatus = cattle.monitoring_results.health_status.toLowerCase();
        const riskLevel = cattle.monitoring_results.risk_level.toLowerCase();

        let healthStatusDisplay = '';
        if (healthStatus === 'healthy' && riskLevel === 'low') {
            healthStatusDisplay = 'Healthy';
        } else if (healthStatus === 'unhealthy' && (riskLevel === 'critical' || riskLevel === 'high')) {
            healthStatusDisplay = 'Unhealthy';
        } else {
            healthStatusDisplay = 'Observation'; // All other cases for the filter dropdown
        }

        return {
            ...cattle, // Keep all original data
            healthStatusDisplay: healthStatusDisplay, // Custom display for filter
            riskLevel: cattle.monitoring_results.risk_level, // Keep original risk level for sorting/display
            timestamp: cattle.timestamp // Ensure timestamp is available for sorting
        };
    });
});


// --- Filtering Logic ---
const filteredLivestock = computed(() => {
    return latestCattleData.value.filter(animal => {
        // Filter by health status
        const healthMatch =
            !healthStatusFilter.value ||
            animal.healthStatusDisplay === healthStatusFilter.value;

        // Search by Cattle ID
        const searchMatch =
            !searchQuery.value ||
            animal.cattle_id.toLowerCase().includes(searchQuery.value.toLowerCase());

        return healthMatch && searchMatch;
    });
});

// --- Sorting Logic ---
const filteredAndSortedLivestock = computed(() => {
    const sorted = [...filteredLivestock.value];
    sorted.sort((a, b) => {
        let propA = a[sortBy.value];
        let propB = b[sortBy.value];

        // Custom sorting for riskLevel
        if (sortBy.value === 'riskLevel') {
            const levels = { 'Low': 1, 'Low-Medium': 2, 'Medium': 3, 'High': 4, 'Critical': 5 };
            propA = levels[propA] || 0;
            propB = levels[propB] || 0;
        } else if (sortBy.value === 'timestamp') {
            propA = new Date(propA);
            propB = new Date(propB);
        } else if (typeof propA === 'string') {
            propA = propA.toLowerCase();
            propB = propB.toLowerCase();
        }

        let comparison = 0;
        if (propA < propB) comparison = -1;
        else if (propA > propB) comparison = 1;

        return sortDirection.value === 'asc' ? comparison : comparison * -1;
    });
    return sorted;
});

// --- Utility Functions ---

// Returns CSS class for health status display in table
function healthClass(statusDisplay) {
    if (statusDisplay === 'Healthy') return 'status-healthy';
    if (statusDisplay === 'Unhealthy') return 'status-unhealthy';
    if (statusDisplay === 'Observation') return 'status-observation';
    return ''; // Default
}

// Returns CSS class for risk badge (reusing global styles)
const getRiskClass = (riskLevel) => {
    return `risk-${riskLevel.toLowerCase().replace(' ', '-')}`;
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
/* Base styles imported from global if you have a main.css */
/* Otherwise, ensure your global style variables are defined and accessible */

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

/* Livestock Table Styling (reusing global .data-table styles) */
.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    /* Box shadow is handled by parent .card */
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
    font-size: 0.8em;
    letter-spacing: 0.05em;
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
    transition: background-color 0.2s ease;
}

/* Status Badges in Table (reusing global styles) */
.status-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 700;
    display: inline-block;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    min-width: 90px;
}
.status-healthy { background-color: var(--primary-color); color: var(--text-light); }
.status-unhealthy { background-color: var(--alert-critical-border); color: var(--text-light); }
.status-observation { background-color: var(--alert-high-border); color: var(--text-light); } /* Orange for observation */

/* Risk Badges are globally defined and reused */

.view-details-link {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s ease;
    white-space: nowrap; /* Prevent wrapping */
}
.view-details-link:hover {
    color: var(--primary-dark);
    text-decoration: underline;
}

/* Responsive Table Adjustments */
@media (max-width: 768px) {
    .controls-grid {
        grid-template-columns: 1fr;
    }
    .filter-group, .sort-group {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
    .control-label {
        margin-bottom: 5px;
    }
    .control-select.ml-2 {
        margin-left: 0; /* Remove margin on small screens */
        margin-top: 5px; /* Add some vertical space */
    }

    /* Make table rows act like blocks on small screens */
    .data-table {
        display: block;
        width: 100%;
    }
    .data-table thead, .data-table tbody, .data-table th, .data-table td, .data-table tr {
        display: block;
    }
    .data-table thead tr {
        position: absolute;
        top: -9999px;
        left: -9999px;
    }
    .data-table tr {
        margin-bottom: 10px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
    }
    .data-table td {
        border: none;
        border-bottom: 1px solid var(--border-color);
        position: relative;
        padding-left: 50%;
        text-align: right;
        min-height: 40px; /* Ensure enough height for content */
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }
    .data-table td:last-child {
        border-bottom: none;
    }
    .data-table td:before {
        position: absolute;
        top: 0;
        left: 6px;
        width: 45%;
        padding-right: 10px;
        white-space: nowrap;
        text-align: left;
        font-weight: 600;
        color: var(--text-dark);
        content: attr(data-label); /* Use data-label for mobile headers */
        display: flex;
        align-items: center;
        height: 100%;
    }
    /* Specific content for :before pseudo-elements to display headers on mobile */
    .data-table td:nth-of-type(1):before { content: "Cattle ID:"; }
    .data-table td:nth-of-type(2):before { content: "Breed:"; }
    .data-table td:nth-of-type(3):before { content: "Health Status:"; }
    .data-table td:nth-of-type(4):before { content: "Risk Level:"; }
    .data-table td:nth-of-type(5):before { content: "Last Update:"; }
    .data-table td:nth-of-type(6):before { content: "Details:"; }

    /* Fix badge alignment on mobile */
    .data-table td span.status-badge,
    .data-table td span.risk-badge {
        margin-left: auto; /* Push to right */
    }
}
</style>
