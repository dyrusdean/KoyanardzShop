// This file is loaded after GLTFLoader.js and ensures it's exposed globally
console.log('GLTFLoader wrapper loaded. Checking for THREE.GLTFLoader...');

// Wait a tick for the previous script to execute
setTimeout(() => {
    if (typeof THREE !== 'undefined' && typeof THREE.GLTFLoader !== 'undefined') {
        // Make it available as a global
        window.GLTFLoader = THREE.GLTFLoader;
        console.log('✓ GLTFLoader exposed to window');
    } else {
        console.warn('THREE.GLTFLoader not found in THREE namespace');
        console.log('THREE properties:', Object.keys(window.THREE || {}).slice(0, 20));
    }
}, 10);
