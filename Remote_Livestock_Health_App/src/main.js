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
// const appId = "1:545517570920:web:1572f2641566dd113de4dd"; // Original Firebase App ID
// FIX: Use the same app ID string that your Flask backend is using for local development
const appId = "default_app_id_for_local"; // <<<--- THIS IS THE CRITICAL CHANGE

const firebaseConfig = {
  apiKey: "AIzaSyBqxr9y5dL80uuhO6b-QhJwl8l_sfTvCn8",
  authDomain: "remotelivestockhealthapp.firebaseapp.com",
  projectId: "remotelivestockhealthapp",
  storageBucket: "remotelivestockhealthapp.firebasestorage.app",
  messagingSenderId: "545517570920",
  appId: "1:545517570920:web:1572f2641566dd113de4dd" // This is your *actual* web app ID, but for the Firestore collection path, we need to match Flask.
                                                    // This appId within firebaseConfig is primarily for Firebase client-side functions.
                                                    // The 'appId' const above is used for the Firestore collection path.
};

const initialAuthToken = null; // Not used in local anonymous login, keep as null

// Initialize Firebase
console.log('Firebase: Initializing app...');
const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const db = getFirestore(firebaseApp);
console.log('Firebase: App and services initialized.');

// --- Global State Management ---
export const store = reactive({
    user: null,
    userId: null,
    isAuthReady: false,
    db: db,
    auth: auth,
    appId: appId, // This 'appId' is now 'default_app_id_for_local'
    cattleData: [],
    activeAlerts: [],
    loading: false,
    error: null,
    flaskApiUrl: 'http://localhost:5000/predict',
    training_features_for_model: [
        'body_temperature',
        'breed_type_enc',
        'milk_production',
        'respiratory_rate',
        'walking_capacity',
        'sleeping_duration',
        'body_condition_score',
        'heart_rate',
        'eating_duration',
        'lying_down_duration',
        'ruminating',
        'rumen_fill',
        'faecal_consistency_enc',
        'activity_ratio',
        'eating_efficiency',
        'vital_sign_index'
    ],
});

// --- Authentication State Listener ---
console.log('Firebase: Setting up onAuthStateChanged listener...');
onAuthStateChanged(auth, async (user) => {
    console.log('Firebase Auth State Changed: User object received:', user ? user.uid : 'null');
    if (user) {
        store.user = user;
        store.userId = user.uid;
        console.log('Firebase Auth: User logged in, userId set to:', store.userId);
    } else {
        store.user = null;
        store.userId = null;
        console.log('Firebase Auth: No user logged in (or logged out).');
    }
    store.isAuthReady = true;
    console.log('Firebase Auth: isAuthReady set to true.');
});

// --- Initial Sign-in Function (Anonymous) ---
async function initialSignIn() {
    console.log('Firebase Auth: Attempting initial sign-in...');
    try {
        if (initialAuthToken) {
            console.log('Firebase Auth: Attempting custom token sign-in...');
            await signInWithCustomToken(auth, initialAuthToken);
            console.log('Firebase Auth: Signed in with custom token successfully.');
        } else {
            console.log('Firebase Auth: Attempting anonymous sign-in...');
            await signInAnonymously(auth);
            console.log('Firebase Auth: Signed in anonymously successfully.');
        }
    } catch (error) {
        console.error('Firebase Auth ERROR: Initial sign-in failed:', error.code, error.message);
        store.error = `Authentication error: ${error.message}`;
        store.isAuthReady = true;
    }
}

// --- Logout Handler ---
export const handleLogout = async () => {
    store.error = null;
    try {
        console.log('Firebase Auth: Attempting logout...');
        await signOut(store.auth);
        console.log('Firebase Auth: User logged out successfully!');
    } catch (error) {
        console.error('Firebase Auth ERROR: Logout error:', error.message);
        store.error = `Logout failed: ${error.message}`;
    }
};

// --- Firestore Listener Setup ---
watch(() => store.userId, (newUserId) => {
    console.log('Firestore: User ID watcher triggered. New User ID:', newUserId);
    if (newUserId) {
        console.log("Firestore: User ID available, setting up Firestore listener.");
        store.loading = true;
        store.error = null;
        // Correct Firestore path to match where Flask is saving
        const cattleCollectionRef = collection(store.db, `artifacts/${store.appId}/users/${newUserId}/cattle_data`);
        const q = query(cattleCollectionRef, orderBy("timestamp", "desc"));

        const unsubscribe = onSnapshot(q, (snapshot) => {
            console.log('Firestore: onSnapshot data received.');
            const cattleData = [];
            const activeAlerts = [];
            snapshot.forEach(doc => {
                const data = doc.data();
                cattleData.push({ id: doc.id, ...data });

                // Ensure data.alerts exists, is an array, and has items
                if (data.alerts && Array.isArray(data.alerts) && data.alerts.length > 0) {
                    data.alerts.forEach(alert => {
                        // Ensure alert.rule_triggered is present, fallback to random ID
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
            console.log('Firestore: Cattle data and alerts updated from Firestore. Total cattle:', store.cattleData.length);
        }, (error) => {
            console.error("Firestore ERROR: Error listening to Firestore:", error.code, error.message);
            store.error = `Failed to load data: ${error.message}`;
            store.loading = false;
        });
        // You might want to store 'unsubscribe' if you need to manually stop listening later
        // e.g., onUnmounted in a component that consumes this global store if it needs to specifically unsubscribe
        // For a global listener that runs for the app's lifetime, it's often not explicitly unsubscribed unless needed for hot-reloading logic or multi-app scenarios.
    } else {
        console.log("Firestore: No User ID, clearing cattle data and alerts.");
        store.cattleData = [];
        store.activeAlerts = [];
    }
}, { immediate: true });

// --- IMPORTANT FIX: Call initialSignIn directly, not in onMounted for global scope ---
console.log('App: Calling initialSignIn directly...');
initialSignIn();

// Create and mount the Vue app
const appInstance = createApp(App);
appInstance.use(router);
appInstance.mount('#app');
console.log('App: Vue app created and mounted.');
