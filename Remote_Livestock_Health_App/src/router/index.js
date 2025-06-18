// src/router/index.js
import { createRouter, createWebHashHistory } from 'vue-router'; 

// Import your components
import DashboardOverview from '../views/DashboardOverview.vue';
import HerdDashboard from '../views/HerdDashboard.vue';
import CattleInformation from '../views/CattleInformation.vue';
import AlertsNotifications from '../components/alerts/AlertsNotifications.vue';
import PredictionLog from '../components/predictions/PredictionLog.vue';
import Reports from '../views/Reports.vue';
import SettingsHelp from '../views/SettingsHelp.vue';
import AddCattleData from '../components/forms/AddCattleData.vue';
import CattlePredictionTool from '../views/CattlePredictionTool.vue'; 
// NEW: Import the RealtimeSimulator component
import RealtimeSimulator from '../views/RealtimeSimulator.vue'; 


const routes = [
    { path: '/dashboard', component: DashboardOverview },
    { path: '/dashboard/herd-dashboard', component: HerdDashboard },
    { path: '/dashboard/cattle', component: CattleInformation },
    { path: '/alerts', component: AlertsNotifications },
    { path: '/prediction-log', name: 'PredictionLogAll', component: PredictionLog },
    { path: '/prediction-log/:cattleId', name: 'PredictionLogSpecific', component: PredictionLog, props: true },
    { path: '/dashboard/reports', component: Reports },
    { path: '/dashboard/settings-and-help', component: SettingsHelp },
    { path: '/add-data', component: AddCattleData },
    { path: '/predict-cattle', component: CattlePredictionTool },
    // NEW: Route for the Real-time Data Simulator
    { path: '/realtime-simulation', component: RealtimeSimulator }, 
    { path: '/', redirect: '/dashboard' } // Default route
];

const router = createRouter({
    history: createWebHashHistory(), // Use hash history for easy deployment
    routes,
});

export default router;
