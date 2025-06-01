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

const routes = [
    { path: '/dashboard', component: DashboardOverview },
    { path: '/dashboard/herd-dashboard', component: HerdDashboard },
    { path: '/dashboard/cattle', component: CattleInformation },
    { path: '/alerts', component: AlertsNotifications },
    { path: '/prediction-log', component: PredictionLog },
    { path: '/dashboard/reports', component: Reports },
    { path: '/dashboard/settings-and-help', component: SettingsHelp },
    { path: '/add-data', component: AddCattleData },
    { path: '/', redirect: '/dashboard' }
];

const router = createRouter({
    history: createWebHashHistory(), // Use hash history for easy deployment
    routes,
});

export default router;
