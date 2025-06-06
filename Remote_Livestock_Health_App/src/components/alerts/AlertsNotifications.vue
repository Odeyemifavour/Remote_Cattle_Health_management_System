<template>
    <div class="content-area">
        <h2 class="card-title">System Alerts</h2>
        <div v-if="store.loading" class="message-center">
            <i class="fa-solid fa-spinner fa-spin fa-2x"></i> Loading alerts...
        </div>
        <div v-else-if="store.error" class="error-message">
            <i class="fa-solid fa-circle-exclamation mr-2"></i> <span>{{ store.error }}</span>
        </div>
        <div v-else class="card p-0">
            <div v-if="sortedAlerts.length > 0" class="alert-list-container">
                <ul class="alert-list">
                    <li v-for="alert in sortedAlerts" :key="alert.id"
                        :class="['alert-item', getAlertCardClass(alert.severity)]">
                        <div class="alert-content">
                            <span class="alert-icon"><i :class="getAlertIconClass(alert.severity)"></i></span>
                            <div class="alert-text-details">
                                <strong class="alert-cattle-id">Cattle ID: {{ alert.cattleId }}</strong>
                                <span class="alert-message">{{ alert.message }}</span>
                                <span v-if="alert.disease && alert.disease !== 'N/A'" class="alert-disease">
                                    <i class="fa-solid fa-virus"></i> {{ alert.disease }}
                                </span>
                            </div>
                        </div>
                        <router-link to="/prediction-log" class="view-prediction-link">
                            View Details <i class="fa-solid fa-arrow-right ml-1"></i>
                        </router-link>
                    </li>
                </ul>
            </div>
            <div v-else class="message-center p-6">
                <i class="fa-solid fa-check-circle text-green-500 fa-2x mb-2"></i>
                <p class="font-bold">No active alerts at the moment. Your herd seems healthy!</p>
                <p class="text-sm mt-2 text-gray-500">Keep up the good work!</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
// Corrected path: go up two directories from src/components/alerts/ to reach src/
import { store } from '../../main.js';

// Computed property to sort alerts by severity (Critical > High > Medium > Low-Medium > Low)
const sortedAlerts = computed(() => {
    const severityOrder = {'Critical': 5, 'High': 4, 'Medium': 3, 'Low-Medium': 2, 'Low': 1}; // Increased Critical/High
    return [...store.activeAlerts].sort((a, b) => severityOrder[b.severity] - severityOrder[a.severity]);
});

// Utility function to get CSS class for alert card background/border
const getAlertCardClass = (severity) => {
    // Reusing the global alert-card color classes
    return severity.toLowerCase().replace(' ', '');
};

// Utility function to get CSS class for alert text color (if needed, global styles usually handle it)
const getAlertTextClass = (severity) => {
    return `text-${severity.toLowerCase().replace(' ', '-')}`;
};

// Utility function to get appropriate Font Awesome icon for alert severity
const getAlertIconClass = (severity) => {
    switch (severity.toLowerCase()) {
        case 'critical': return 'fa-solid fa-exclamation-circle'; // Strong warning icon
        case 'high': return 'fa-solid fa-exclamation-triangle';
        case 'medium': return 'fa-solid fa-info-circle';
        case 'low-medium': return 'fa-solid fa-bell';
        case 'low': return 'fa-solid fa-check'; // A softer indicator for low alerts
        default: return 'fa-solid fa-bell';
    }
};

// Formats timestamp for display (e.g., "Jun 5, 10:00 AM")
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
/* Scoped styles for AlertsNotifications component, overriding/extending global styles */

.alert-list-container {
    padding: 25px; /* Apply padding to the container inside the card */
}

.alert-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.alert-item {
    padding: 15px 20px;
    border-radius: 10px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08); /* Lighter shadow for list items */
    border-left: 6px solid; /* Thicker, colored border */
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.alert-item:last-child {
    margin-bottom: 0; /* No margin below the last item */
}

.alert-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

/* Reusing global color variables for alert items */
.alert-item.critical { background-color: var(--alert-critical-bg); border-color: var(--alert-critical-border); }
.alert-item.high { background-color: var(--alert-high-bg); border-color: var(--alert-high-border); }
.alert-item.medium { background-color: var(--alert-medium-bg); border-color: var(--alert-medium-border); }
.alert-item.low-medium { background-color: var(--alert-low-medium-bg); border-color: var(--alert-low-medium-border); }
.alert-item.low { background-color: var(--alert-low-bg); border-color: var(--alert-low-border); }


.alert-content {
    display: flex;
    align-items: center;
    flex-grow: 1;
    margin-right: 20px; /* Space before the link */
}

.alert-icon {
    font-size: 1.8em;
    margin-right: 18px;
    flex-shrink: 0;
    /* Color inherited from parent alert-item via border-color */
    color: inherit; /* Ensure icon color matches the card's theme */
}
.alert-item.critical .alert-icon { color: var(--alert-critical-border); }
.alert-item.high .alert-icon { color: var(--alert-high-border); }
.alert-item.medium .alert-icon { color: var(--alert-medium-border); }
.alert-item.low-medium .alert-icon { color: var(--alert-low-medium-border); }
.alert-item.low .alert-icon { color: var(--primary-color); } /* Use primary for low/healthy */


.alert-text-details {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

.alert-cattle-id {
    font-size: 1.05em;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 4px;
}

.alert-message {
    font-size: 0.95em;
    color: var(--text-secondary);
    line-height: 1.4;
}
.alert-item.critical .alert-message { color: var(--alert-critical-text); font-weight: 600; }
.alert-item.high .alert-message { color: var(--alert-high-text); font-weight: 600; }
.alert-item.medium .alert-message { color: var(--alert-medium-text); }
.alert-item.low-medium .alert-message { color: var(--alert-low-medium-text); }
.alert-item.low .alert-message { color: var(--alert-low-text); }

.alert-disease {
    font-size: 0.85em;
    color: var(--text-dark);
    margin-top: 5px;
    font-style: italic;
}
.alert-disease i {
    margin-right: 5px;
}


.view-prediction-link {
    background-color: var(--primary-color);
    color: var(--text-light);
    border: none;
    padding: 8px 15px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9em;
    display: flex;
    align-items: center;
    transition: background-color 0.2s ease, transform 0.2s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    flex-shrink: 0; /* Prevent shrinking */
}
.view-prediction-link:hover {
    background-color: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
}


/* Responsive Adjustments */
@media (max-width: 768px) {
    .alert-item {
        flex-direction: column;
        align-items: flex-start;
        padding: 15px;
    }
    .alert-content {
        margin-right: 0;
        margin-bottom: 10px;
        width: 100%;
        flex-direction: row;
        align-items: flex-start; /* Align icon and text details */
    }
    .alert-icon {
        margin-bottom: 0;
        margin-top: 5px; /* Adjust vertical alignment for icon */
        font-size: 1.5em; /* Slightly smaller for mobile */
    }
    .alert-text-details {
        margin-left: 10px; /* Space between icon and text */
        text-align: left;
    }
    .alert-cattle-id {
        width: 100%; /* Take full width */
        margin-bottom: 5px;
    }
    .alert-message {
        font-size: 0.9em; /* Smaller font on mobile */
    }
    .alert-disease {
        font-size: 0.8em;
    }
    .view-prediction-link {
        width: 100%;
        justify-content: center;
        margin-top: 10px;
        font-size: 0.85em;
    }
}

@media (max-width: 480px) {
    .alert-item {
        padding: 12px;
    }
    .alert-icon {
        font-size: 1.3em;
    }
    .alert-cattle-id {
        font-size: 0.95em;
    }
    .alert-message {
        font-size: 0.85em;
    }
}
</style>
