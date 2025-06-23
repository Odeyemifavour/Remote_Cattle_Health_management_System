<template>
    <div v-if="!store.isAuthReady" class="message-center loading-message">
        <p>Initializing authentication...</p>
    </div>
    <div v-else class="dashboard-root">
        <SideBar :user-id="store.userId" @logout="handleLogout" />

        <div class="main-content">
            <TopNavbar :farm-name="'My Awesome Farm'" :user-id="store.userId" />
            
            <div class="content-area">
                <router-view></router-view>
            </div>
        </div>
    </div>
</template>

<script setup>
import { store, handleLogout } from './main.js';
import SideBar from './components/dashboard/SideBar.vue';
import TopNavbar from './components/dashboard/TopNavbar.vue';
</script>

<style>
/* Global CSS variables and styles can go here, or in a separate global.css imported in main.js */
/* For simplicity, I'll put the root CSS variables here and common styles */
:root {
    /* PRIMARY THEME COLORS - Adjusted for higher contrast with white text */
    --primary-color: #2E7D32; /* Darker Green: Ensures white text is highly legible on headers/buttons */
    --primary-dark: #1B5E20; /* Even darker for strong hover states */
    --primary-light: #4CAF50; /* A slightly lighter variant for gradients/accents */
    
    /* NEUTRAL COLORS */
    --secondary-bg: #263238; /* Deep blue-gray for sidebar/dark elements */
    --text-dark: #000000;    /* Pure Black for maximum contrast on light backgrounds */
    --text-light: #FFFFFF;   /* Pure White for maximum contrast on dark backgrounds */
    --text-secondary: #757575; /* Secondary text color, still clear */
    --background-light: #F8F8F8; /* Overall light background, slightly off-white */
    --card-bg: #FFFFFF;      /* White for card backgrounds */
    --border-color: #E0E0E0; /* Light border for separation */

    /* STATUS & ACTION COLORS - Adjusted for higher contrast */
    --success-color: #388E3C; /* Dark Green for Healthy status - paired with white text */
    --danger-color: #C62828;  /* Dark Red for Unhealthy status - paired with white text */
    --info-color: #1976D2;    /* Dark Blue for info/action buttons - paired with white text */
    --info-dark: #1565C0;     /* Even darker blue for info button hover state */
    --warning-color: #FFC107; /* Amber Yellow for warnings/observation - requires dark text */
    --accent-color: #00BCD4;  /* Cyan for other accents */
    --accent-dark: #00838F;   /* Darker cyan for hover states (for accent-color) */
    --secondary-color: #607D8B; /* Blue-grey for pagination/minor elements - typically paired with light text */
    --text-muted: #9E9E9E;    /* Muted text for subtle info */

    /* ALERT COLORS - Adjusted values for consistency and contrast */
    --alert-critical-bg: #FFEBEE; /* Light Red */
    --alert-critical-border: #D32F2F; /* Red border - paired with white text for severity badges */
    --alert-critical-text: #B71C1C; /* Darker red text for messages */

    --alert-high-bg: #FFF3E0; /* Light Orange */
    --alert-high-border: #F57C00; /* Dark Orange border - paired with white text */
    --alert-high-text: #E65100; /* Darker orange text */

    --alert-medium-bg: #FFFDE7; /* Light Yellow */
    --alert-medium-border: #FFD600; /* Yellow border - paired with dark text */
    --alert-medium-text: #FFAB00; /* Darker yellow text */

    --alert-low-medium-bg: #E3F2FD; /* Light Blue */
    --alert-low-medium-border: #2196F3; /* Standard Blue border - paired with white text */
    --alert-low-medium-text: #1565C0; /* Darker blue text */

    --alert-low-bg: #E8F5E9; /* Light Green */
    --alert-low-border: #4CAF50; /* Standard Green border - paired with dark text */
    --alert-low-text: #388E3C; /* Darker green text */
}

/* Global Styles */
body {
    margin: 0;
    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: var(--background-light);
    color: var(--text-dark);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

#app-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.dashboard-root {
    display: flex;
    flex-grow: 1;
    min-height: 100vh;
}

.main-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.content-area {
    padding: 30px;
    flex-grow: 1;
}

/* General Card Styles */
.card {
    background-color: var(--card-bg);
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 30px;
    border: 1px solid var(--border-color);
}

.card-title {
    font-size: 26px;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 25px;
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 12px;
    position: relative;
}
.card-title::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -2px;
    width: 60px;
    height: 4px;
    background-color: var(--primary-color);
    border-radius: 2px;
}

/* Messages */
.message-center {
    text-align: center;
    color: var(--text-secondary);
    padding: 30px;
    font-size: 1.1em;
}
.loading-message {
    /* Styles for the loading message when auth is not ready */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh; /* Occupy full viewport height */
    color: var(--text-secondary); /* Corrected from --secondary-dark */
    font-weight: 500;
}
.loading-message i {
    margin-bottom: 15px;
}

.error-message {
    background-color: var(--alert-critical-bg);
    border: 1px solid var(--alert-critical-border);
    color: var(--alert-critical-text);
    padding: 18px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-weight: 500;
}
.success-message {
    background-color: var(--alert-low-bg);
    border: 1px solid var(--alert-low-border);
    color: var(--alert-low-text);
    padding: 18px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-weight: 500;
}

/* Responsive Adjustments (common to all components) */
@media (max-width: 768px) {
    .dashboard-root {
        flex-direction: column;
    }
    .main-content {
        padding: 20px;
    }
    .content-area {
        padding: 20px; /* Adjusted padding for small screens */
    }
    .card {
        padding: 20px;
    }
    .card-title {
        font-size: 22px;
    }
}
</style>

