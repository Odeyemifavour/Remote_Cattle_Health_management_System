<template>
    <div class="content-area">
        <div class="card">
            <h2 class="card-title">Herd Dashboard</h2>
            <div v-if="store.loading" class="message-center loading-message">
                <i class="fa-solid fa-spinner fa-spin fa-2x"></i> Loading herd data...
            </div>
            <div v-if="store.error" class="error-message">
                <p><strong>Error:</strong> {{ store.error }}</p>
            </div>

            <!-- FIX: Added optional chaining and nullish coalescing to ensure filteredCattle is always an array -->
            <div v-if="filteredCattle?.length > 0">
                <div class="table-controls mb-4">
                    <input type="text" v-model="searchTerm" placeholder="Search by Cattle ID or Breed" class="search-input">
                    <select v-model="filterStatus" class="filter-select">
                        <option value="">All Health Statuses</option>
                        <option value="Healthy">Healthy</option>
                        <option value="Unhealthy">Unhealthy</option>
                    </select>
                </div>

                <div class="overflow-x-auto">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th @click="sortBy('cattle_id')">Cattle ID <i :class="getSortIcon('cattle_id')"></i></th>
                                <th @click="sortBy('monitoring_results.health_status')">Health Status <i :class="getSortIcon('monitoring_results.health_status')"></i></th>
                                <th @click="sortBy('monitoring_results.risk_level')">Risk Level <i :class="getSortIcon('monitoring_results.risk_level')"></i></th>
                                <th @click="sortBy('input_data_snapshot.breed_type')">Breed Type <i :class="getSortIcon('input_data_snapshot.breed_type')"></i></th>
                                <th @click="sortBy('alerts.length')">Alerts <i :class="getSortIcon('alerts.length')"></i></th>
                                <th @click="sortBy('timestamp')">Last Updated <i :class="getSortIcon('timestamp')"></i></th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="cattle in paginatedCattle" :key="cattle.id">
                                <td data-label="Cattle ID">{{ cattle.cattle_id }}</td>
                                <td data-label="Health Status">
                                    <span :class="['status-badge', getStatusClass(cattle.monitoring_results?.health_status)]">
                                        {{ cattle.monitoring_results?.health_status || 'N/A' }}
                                    </span>
                                </td>
                                <td data-label="Risk Level">
                                    <span :class="['risk-badge', getRiskClass(cattle.monitoring_results?.risk_level)]">
                                        {{ cattle.monitoring_results?.risk_level || 'N/A' }}
                                    </span>
                                </td>
                                <td data-label="Breed Type">{{ cattle.input_data_snapshot?.breed_type || 'N/A' }}</td>
                                <td data-label="Alerts">
                                    <span v-if="cattle.alerts && cattle.alerts.length > 0" class="badge-count">
                                        {{ cattle.alerts.length }}
                                    </span>
                                    <span v-else class="badge-count badge-none">0</span>
                                </td>
                                <td data-label="Last Updated">{{ formatTimestamp(cattle.timestamp) }}</td>
                                <td data-label="Actions">
                                    <button @click="viewDetails(cattle.id)" class="action-btn">View Details</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="pagination-controls flex justify-between items-center mt-6">
                    <button @click="prevPage" :disabled="currentPage === 1" class="pagination-button">Previous</button>
                    <span>Page {{ currentPage }} of {{ totalPages }}</span>
                    <button @click="nextPage" :disabled="currentPage === totalPages" class="pagination-button">Next</button>
                </div>
            </div>
            <!-- If filteredCattle is empty (or undefined/null initially) -->
            <div v-else class="message-center no-data-message">
                <p>No cattle data available. Start the real-time simulator or add data manually!</p>
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

// Filter and sort cattle data
const filteredAndSortedCattle = computed(() => {
    // Ensure store.cattleData is always an array, even if it's null/undefined initially
    let data = [...(store.cattleData || [])]; // Added nullish coalescing for robustness

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
            cattle.monitoring_results?.health_status?.toLowerCase() === filterStatus.value.toLowerCase()
        );
    }

    // 2. Sort
    data.sort((a, b) => {
        let valA, valB;

        // Helper to get nested property value
        const getNestedValue = (obj, path) => {
            return path.split('.').reduce((acc, part) => acc && acc[part], obj);
        };

        valA = getNestedValue(a, sortByField.value);
        valB = getNestedValue(b, sortByField.value);

        // Special handling for alert count (alerts.length)
        if (sortByField.value === 'alerts.length') {
            valA = (valA || []).length;
            valB = (valB || []).length;
        }

        // Handle undefined/null values for sorting
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

const getRiskClass = (risk) => {
    return `risk-${risk?.toLowerCase().replace(' ', '-')}`;
};

const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    // Assuming timestamp is in "YYYY-MM-DD HH:MM:SS" format from Flask
    return new Date(timestamp).toLocaleString();
};

const viewDetails = (cattleId) => {
    router.push({ name: 'CattleInformation', params: { id: cattleId } });
};
</script>

<style scoped>
/* Table Specific Styles */
.table-controls {
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
    flex-wrap: wrap; /* Allow wrapping on small screens */
    justify-content: flex-end; /* Align to right on larger screens */
}

.search-input,
.filter-select {
    padding: 10px 15px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-size: 1em;
    color: var(--text-dark);
    background-color: var(--background-light);
    flex: 1; /* Allow inputs to grow */
    min-width: 150px; /* Minimum width for inputs */
}

.search-input:focus,
.filter-select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
}

.overflow-x-auto {
    overflow-x: auto; /* Enables horizontal scrolling for the table on small screens */
    width: 100%;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    background-color: var(--background-light);
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border-radius: 12px;
    overflow: hidden; /* Ensures rounded corners apply to table content */
}

.data-table th,
.data-table td {
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
    white-space: nowrap; /* Prevent wrapping of column headers */
}

.data-table th:hover {
    background-color: var(--primary-dark);
}

.data-table tbody tr:last-child td {
    border-bottom: none;
}

.data-table tbody tr:nth-child(even) {
    background-color: #F8F8F8; /* Light stripe for readability */
}

.data-table tbody tr:hover {
    background-color: #F0F4F7; /* Hover effect */
}

/* Badges for status and risk */
.status-badge,
.risk-badge {
    padding: 6px 12px;
    border-radius: 18px;
    font-size: 0.8em;
    font-weight: 600;
    text-transform: uppercase;
    display: inline-block;
    min-width: 80px; /* Ensure consistent width */
    text-align: center;
}
.status-healthy { background-color: var(--success-color); color: var(--text-light); }
.status-unhealthy { background-color: var(--danger-color); color: var(--text-light); }

.risk-badge.critical { background-color: var(--alert-critical-border); color: var(--text-light); }
.risk-badge.high { background-color: var(--alert-high-border); color: var(--text-light); }
.risk-badge.medium { background-color: var(--alert-medium-border); color: var(--text-dark); }
.risk-badge.low-medium { background-color: var(--alert-low-medium-border); color: var(--text-light); }
.risk-badge.low { background-color: var(--alert-low-border); color: var(--text-light); }

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
    background-color: #CFD8DC; /* Light grey for 0 alerts */
}

.action-btn {
    background-color: var(--accent-color);
    color: var(--text-light);
    padding: 8px 15px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
    transition: background-color 0.2s ease;
}

.action-btn:hover {
    background-color: var(--accent-dark);
}

/* Pagination Styles */
.pagination-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
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
    background-color: var(--secondary-dark);
}

.pagination-button:disabled {
    background-color: #B0BEC5;
    cursor: not-allowed;
    opacity: 0.7;
}

.no-data-message {
    padding: 30px;
    font-size: 1.1em;
    color: var(--text-muted);
}

/* Responsive Table */
@media (max-width: 768px) {
    .table-controls {
        flex-direction: column;
        gap: 10px;
    }

    .data-table thead {
        display: none; /* Hide table headers on small screens */
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
        padding-left: 50%; /* Space for pseudo-element label */
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
}
</style>
