<template>
    <div v-if="!store.isAuthReady" class="message-center">
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
    --primary-color: #4CAF50; /* A friendly green for actions/highlights */
    --primary-dark: #388E3C;
    --secondary-bg: #263238; /* Deep blue-gray for sidebar/dark elements */
    --text-dark: #424242; /* Main text color */
    --text-light: #FAFAFA; /* Light text for dark backgrounds */
    --text-secondary: #757575; /* Secondary text color */
    --background-light: #F5F5F5; /* Overall light background */
    --card-bg: #FFFFFF;
    --border-color: #E0E0E0; /* Light border for separation */

    /* Alert Colors */
    --alert-critical-bg: #FFEBEE; /* Light Red */
    --alert-critical-border: #D32F2F; /* Dark Red */
    --alert-critical-text: #C62828;

    --alert-high-bg: #FFF3E0; /* Light Orange */
    --alert-high-border: #F57C00; /* Dark Orange */
    --alert-high-text: #EF6C00;

    --alert-medium-bg: #FFFDE7; /* Light Yellow */
    --alert-medium-border: #FFD600; /* Dark Yellow */
    --alert-medium-text: #FFAB00;

    --alert-low-medium-bg: #E3F2FD; /* Light Blue */
    --alert-low-medium-border: #2196F3; /* Standard Blue */
    --alert-low-medium-text: #1976D2;

    --alert-low-bg: #E8F5E9; /* Light Green */
    --alert-low-border: #4CAF50; /* Standard Green */
    --alert-low-text: #388E3C;
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
    .card {
        padding: 20px;
    }
    .card-title {
        font-size: 22px;
    }
}
</style>