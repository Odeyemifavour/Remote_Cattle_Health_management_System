// src/main.js
import { createApp, reactive, watch, onMounted, onUnmounted, computed } from 'vue';
import App from './App.vue';
import router from './router'; // Import your router
import { initializeApp } from "firebase/app";
import { getAuth, signInAnonymously, signInWithCustomToken, signOut, onAuthStateChanged } from "firebase/auth";
import { getFirestore, doc, setDoc, onSnapshot, collection, query, orderBy } from "firebase/firestore";

// --- Global Variables (Canvas specific, adapt for local env) ---
// In a real app, firebaseConfig would come from a .env file or a config.js
// For local development, you'll need to replace these with your actual Firebase project config.
// Go to your Firebase project -> Project settings -> Your apps -> Web app -> Config
const appId = "1:545517570920:web:1572f2641566dd113de4dd"; // Replace with your actual Firebase App ID
const firebaseConfig = {
  apiKey: "AIzaSyBqxr9y5dL80uuhO6b-QhJwl8l_sfTvCn8",
  authDomain: "remotelivestockhealthapp.firebaseapp.com",
  projectId: "remotelivestockhealthapp",
  storageBucket: "remotelivestockhealthapp.firebasestorage.app",
  messagingSenderId: "545517570920",
  appId: "1:545517570920:web:1572f2641566dd113de4dd"
};

const initialAuthToken = null; // Not used in local anonymous login, keep as null

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const db = getFirestore(firebaseApp);

// --- Global State Management ---
export const store = reactive({
    user: null,
    userId: null,
    isAuthReady: false,
    db: db,
    auth: auth,
    appId: appId,
    cattleData: [],
    activeAlerts: [],
    loading: false,
    error: null,
    flaskApiUrl: 'http://localhost:5000/predict_and_alert', // Your Flask API URL
});

// --- Authentication State Listener ---
onAuthStateChanged(auth, async (user) => {
    if (user) {
        store.user = user;
        store.userId = user.uid;
        console.log('User logged in:', user.uid);
    } else {
        store.user = null;
        store.userId = null;
        console.log('No user logged in.');
    }
    store.isAuthReady = true;
});

// --- Initial Sign-in Function (Anonymous) ---
async function initialSignIn() {
    try {
        if (initialAuthToken) {
            await signInWithCustomToken(auth, initialAuthToken);
            console.log('Signed in with custom token.');
        } else {
            await signInAnonymously(auth);
            console.log('Signed in anonymously.');
        }
    } catch (error) {
        console.error('Initial sign-in error:', error.message);
        store.error = `Authentication error: ${error.message}`;
    }
}

// --- Logout Handler ---
export const handleLogout = async () => {
    store.error = null;
    try {
        await signOut(store.auth);
        console.log('User logged out successfully!');
    } catch (error) {
        console.error('Logout error:', error.message);
        store.error = `Logout failed: ${error.message}`;
    }
};

// --- Firestore Listener Setup ---
watch(() => store.userId, (newUserId) => {
    if (newUserId) {
        console.log("User ID available, setting up Firestore listener.");
        store.loading = true;
        store.error = null;
        const cattleCollectionRef = collection(store.db, `artifacts/${store.appId}/users/${newUserId}/cattle_data`);
        const q = query(cattleCollectionRef, orderBy("timestamp", "desc"));

        const unsubscribe = onSnapshot(q, (snapshot) => {
            const cattleData = [];
            const activeAlerts = [];
            snapshot.forEach(doc => {
                const data = doc.data();
                cattleData.push({ id: doc.id, ...data });

                if (data.alerts && data.alerts.length > 0) {
                    data.alerts.forEach(alert => {
                        activeAlerts.push({
                            id: `${doc.id}-${alert.rule_triggered || Math.random().toString(36).substring(7)}`,
                            cattleId: doc.id,
                            timestamp: data.timestamp,
                            message: alert.message,
                            severity: alert.severity,
                            disease: alert.disease || (data.specific_diseases_detected ? data.specific_diseases_detected.join(', ') : 'N/A')
                        });
                    });
                }
            });
            store.cattleData = cattleData;
            const severityOrder = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low-Medium': 1.5, 'Low': 1};
            store.activeAlerts = activeAlerts.sort((a, b) => severityOrder[b.severity] - severityOrder[a.severity]);
            store.loading = false;
            console.log('Cattle data and alerts updated from Firestore.');
        }, (error) => {
            console.error("Error listening to Firestore:", error);
            store.error = `Failed to load data: ${error.message}`;
            store.loading = false;
        });

        onUnmounted(() => {
            unsubscribe();
            console.log("Firestore listener unsubscribed.");
        });
    } else {
        store.cattleData = [];
        store.activeAlerts = [];
    }
}, { immediate: true });

onMounted(() => {
    initialSignIn();
});

// Create and mount the Vue app
const appInstance = createApp(App);
appInstance.use(router);
appInstance.mount('#app');