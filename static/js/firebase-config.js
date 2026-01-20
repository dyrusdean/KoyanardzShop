// Firebase Configuration
// Import the functions you need from the Firebase CDN as ES modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getAuth,
  setPersistence,
  browserLocalPersistence
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyB-9sRA7dvMQIf3HFfnTuPkYhZBmo-FMYo",
  authDomain: "koyanardzshop-601f8.firebaseapp.com",
  projectId: "koyanardzshop-601f8",
  storageBucket: "koyanardzshop-601f8.firebasestorage.app",
  messagingSenderId: "86693055048",
  appId: "1:86693055048:web:8aea7ad0c67c54e68e667d",
  measurementId: "G-3KMJ3F79TZ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Set persistence to LOCAL so user stays logged in
setPersistence(auth, browserLocalPersistence).catch((error) => {
  console.error("Persistence setup failed:", error);
});

export { auth, app };
