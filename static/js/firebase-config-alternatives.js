// Firebase Configuration using CDN
// This is an alternative approach if npm bundling is not set up

// Add these script tags to your signup.html template instead:
/*
<script src="https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js"></script>

<script>
// Initialize Firebase
const firebaseConfig = {
  apiKey: "AIzaSyB-9sRA7dvMQIf3HFfnTuPkYhZBmo-FMYo",
  authDomain: "koyanardzshop-601f8.firebaseapp.com",
  projectId: "koyanardzshop-601f8",
  storageBucket: "koyanardzshop-601f8.firebasestorage.app",
  messagingSenderId: "86693055048",
  appId: "1:86693055048:web:8aea7ad0c67c54e68e667d",
  measurementId: "G-3KMJ3F79TZ"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);
</script>
*/

// Firebase Configuration Object (use if npm bundling works)
import { initializeApp } from "firebase/app";
import { getAuth, setPersistence, browserLocalPersistence } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyB-9sRA7dvMQIf3HFfnTuPkYhZBmo-FMYo",
  authDomain: "koyanardzshop-601f8.firebaseapp.com",
  projectId: "koyanardzshop-601f8",
  storageBucket: "koyanardzshop-601f8.firebasestorage.app",
  messagingSenderId: "86693055048",
  appId: "1:86693055048:web:8aea7ad0c67c54e68e667d",
  measurementId: "G-3KMJ3F79TZ"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

setPersistence(auth, browserLocalPersistence)
  .catch((error) => {
    console.error("Persistence setup failed:", error);
  });

export { auth, app };
