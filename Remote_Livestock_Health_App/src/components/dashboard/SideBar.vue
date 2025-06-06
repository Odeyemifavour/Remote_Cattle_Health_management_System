<template>
    <div class="sidebar">
        <div class="sidebar-header">
            <img src="/src/assets/cattle-logo.jpg" alt="Cattle.360 Logo" class="logo" />
            <h3>Cattle.360</h3>
        </div>
        <ul class="sidebar-menu">
            <li>
                <router-link to="/dashboard" active-class="active" exact class="nav-link">
                    <i class="fa-solid fa-gauge fa-icon"></i> Overview/Home
                </router-link>
            </li>
            <li>
                <router-link to="/dashboard/herd-dashboard" active-class="active" class="nav-link">
                    <i class="fa-solid fa-paw fa-icon"></i> Herd Dashboard
                </router-link>
            </li>
            <li>
                <router-link to="/dashboard/cattle" active-class="active" class="nav-link">
                    <i class="fa-solid fa-info-circle fa-icon"></i> Cattle Information
                </router-link>
            </li>
            <li>
                <router-link to="/alerts" active-class="active" class="nav-link">
                    <i class="fa-solid fa-bell fa-icon"></i> Alerts & Notifications
                </router-link>
            </li>
            <li>
                <router-link to="/prediction-log" active-class="active" class="nav-link">
                    <i class="fa-solid fa-chart-line fa-icon"></i> Predictions Log
                </router-link>
            </li>
            <li>
                <router-link to="/dashboard/reports" active-class="active" class="nav-link">
                    <i class="fa-solid fa-file-alt fa-icon"></i> Reports
                </router-link>
            </li>
            <li>
                <router-link to="/dashboard/settings-and-help" active-class="active" class="nav-link">
                    <i class="fa-solid fa-cog fa-icon"></i> Settings/Help
                </router-link>
            </li>
            <li>
                <router-link to="/add-data" active-class="active" class="nav-link">
                    <i class="fa-solid fa-plus-circle fa-icon"></i> Add Cattle Data
                </router-link>
            </li>
            <!-- --- NEW LINK FOR CATTLE PREDICTION TOOL --- -->
            <li>
                <router-link to="/predict-cattle" active-class="active" class="nav-link">
                    <i class="fa-solid fa-stethoscope fa-icon"></i> Cattle Prediction
                </router-link>
            </li>
        </ul>
        <div class="user-info">
            User ID: <span class="user-id-text">{{ userId }}</span>
            <a href="#" @click.prevent="$emit('logout')" class="logout-link">
                <i class="fa-solid fa-sign-out-alt fa-icon"></i> Logout
            </a>
        </div>
    </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
    userId: String
});

const emit = defineEmits(['logout']);
</script>

<style scoped>
/* Sidebar Styles (from your provided CSS) */
.sidebar {
    width: 250px;
    background-color: var(--secondary-bg);
    color: var(--text-light);
    padding: 20px;
    box-shadow: 2px 0 10px rgba(0,0,0,0.15);
    display: flex;
    flex-direction: column;
    border-right: 1px solid rgba(0,0,0,0.1);
}

.sidebar-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 35px;
    padding-bottom: 15px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sidebar-header .logo {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    margin-bottom: 15px;
    object-fit: cover;
    border: 3px solid var(--primary-color);
    box-shadow: 0 0 15px rgba(76, 175, 80, 0.4);
}

.sidebar-header h3 {
    margin: 0;
    font-weight: 700;
    text-align: center;
    font-size: 1.3em;
    color: var(--text-light);
}

.sidebar-menu {
    list-style: none;
    padding: 0;
    width: 100%;
    flex-grow: 1;
}

.sidebar-menu li {
    margin-bottom: 8px;
}

.sidebar-menu li a,
.sidebar-menu li .logout-link {
    display: flex;
    align-items: center;
    padding: 12px 18px;
    text-decoration: none;
    color: rgba(255,255,255,0.8);
    transition: background-color 0.25s ease, color 0.25s ease, transform 0.1s ease;
    border-radius: 8px;
    font-size: 1.05em;
    font-weight: 500;
}

.sidebar-menu li a:hover,
.sidebar-menu li .logout-link:hover {
    background-color: rgba(76, 175, 80, 0.2);
    color: var(--primary-color);
    transform: translateX(5px);
}

/* Active Router Link Style (will be applied by Vue Router) */
.router-link-active {
    background-color: var(--primary-color) !important;
    color: var(--text-light) !important;
    box-shadow: 0 4px 10px rgba(76, 175, 80, 0.3);
    transform: translateX(0) !important;
}
.router-link-active:hover {
    background-color: var(--primary-dark) !important;
}

.sidebar-menu li a .fa-icon,
.sidebar-menu li .logout-link .fa-icon {
    margin-right: 15px;
    width: 20px;
    text-align: center;
    color: inherit;
}

.user-info {
    margin-top: auto;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.1);
    font-size: 14px;
    color: rgba(255,255,255,0.7);
    text-align: center;
}

.user-id-text {
    font-weight: bold;
    color: var(--text-light);
    word-break: break-all;
    display: block;
    margin-top: 5px;
    font-size: 0.9em;
}

.logout-link {
    cursor: pointer;
    width: 100%;
    margin-top: 15px;
    color: #FFCDD2;
}
.logout-link:hover {
    color: #EF5350;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .sidebar {
        width: 100%;
        padding: 15px;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        height: auto;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }
    .sidebar-header {
        width: auto;
        margin-bottom: 0;
        flex-direction: row;
        justify-content: flex-start;
        padding-bottom: 0;
        border-bottom: none;
    }
    .sidebar-header .logo {
        width: 45px;
        height: 45px;
        margin-right: 10px;
        margin-bottom: 0;
    }
    .sidebar-header h3 {
        font-size: 1.1em;
    }
    .sidebar-menu {
        display: flex;
        width: 100%;
        justify-content: space-around;
        flex-wrap: wrap;
        flex-grow: 0;
        margin-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 15px;
    }
    .sidebar-menu li {
        margin-bottom: 0;
        flex-basis: 30%;
        text-align: center;
    }
    .sidebar-menu li a,
    .sidebar-menu li .logout-link {
        padding: 10px 8px;
        font-size: 0.85em;
        flex-direction: column;
        text-align: center;
        border-radius: 6px;
    }
    .sidebar-menu li a .fa-icon,
    .sidebar-menu li .logout-link .fa-icon {
        margin-right: 0;
        margin-bottom: 5px;
        font-size: 1.2em;
    }
    .user-info {
        text-align: center;
        border-top: none;
        padding-top: 0;
        width: 100%;
        margin-top: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .user-id-text {
        margin-bottom: 10px;
    }
    .logout-link {
        margin-top: 0;
        padding-top: 0;
        border-top: none;
    }
}
</style>
