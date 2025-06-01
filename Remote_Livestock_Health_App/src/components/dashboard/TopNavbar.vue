<template>
    <header class="top-navbar">
        <div class="logo-name">
            <img src="/src/assets/cattle-logo.jpg" alt="Cattle.360 Logo" class="logo" />
            <h1>Cattle.360</h1>
        </div>
        <div class="farm-info">
            <i class="fa-solid fa-cow fa-icon"></i> <span>{{ farmName }}</span>
        </div>
        <div class="user-info">
            <i class="fa-solid fa-user-circle fa-icon"></i>
            <span>Welcome, User ({{ userId ? userId.substring(0, 8) + '...' : 'Guest' }})</span>
        </div>
        <div class="date-time">
            <span>{{ currentTime }}</span>
        </div>
    </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineProps } from 'vue';

const props = defineProps({
    farmName: String,
    userId: String
});

const currentTime = ref('');

const updateTime = () => {
    const now = new Date();
    currentTime.value = now.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) + ' ' + now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

onMounted(() => {
    updateTime();
    const intervalId = setInterval(updateTime, 1000);
    onUnmounted(() => clearInterval(intervalId));
});
</script>

<style scoped>
/* Top Navbar Styles (from your provided CSS) */
.top-navbar {
    background-color: var(--card-bg);
    color: var(--text-dark);
    padding: 18px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.top-navbar .logo-name {
    display: flex;
    align-items: center;
}

.top-navbar .logo-name .logo {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    margin-right: 12px;
    object-fit: cover;
    border: 2px solid var(--primary-color);
}

.top-navbar .logo-name h1 {
    margin: 0;
    font-size: 1.6em;
    font-weight: 600;
    color: var(--text-dark);
}

.top-navbar .farm-info,
.top-navbar .user-info,
.top-navbar .date-time {
    display: flex;
    align-items: center;
    font-size: 0.9em;
    color: var(--text-secondary);
    font-weight: 500;
}

.top-navbar .farm-info .fa-icon,
.top-navbar .user-info .fa-icon {
    margin-right: 8px;
    color: var(--primary-color);
}

.top-navbar .user-info {
    margin-left: 25px;
}

.top-navbar .date-time {
    margin-left: 25px;
}

/* Responsive Layout */
@media (max-width: 768px) {
    .top-navbar {
        flex-direction: column;
        align-items: flex-start;
        padding: 15px 20px;
    }
    .top-navbar .logo-name {
        margin-bottom: 10px;
    }
    .top-navbar .farm-info,
    .top-navbar .user-info,
    .top-navbar .date-time {
        margin: 5px 0;
        font-size: 0.8em;
    }
}
</style>
