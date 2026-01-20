// This file is loaded after OrbitControls.js and ensures it's exposed globally
console.log('OrbitControls wrapper loaded. Checking for THREE.OrbitControls...');

// Wait a tick for the previous script to execute
setTimeout(() => {
    if (typeof THREE !== 'undefined' && typeof THREE.OrbitControls !== 'undefined') {
        // Make it available as a global
        window.OrbitControls = THREE.OrbitControls;
        console.log('✓ OrbitControls exposed to window');
    } else {
        console.warn('THREE.OrbitControls not found in THREE namespace');
        // Try to find it in window
        for (let key in window) {
            if (key.includes('Orbit')) {
                console.log('Found:', key);
            }
        }
    }
}, 10);
