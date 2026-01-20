// Firebase Email Verification Handler
// Import Firebase pieces from our config and the CDN-based auth module
import { auth } from './firebase-config.js';
import {
  createUserWithEmailAndPassword,
  sendEmailVerification,
  onAuthStateChanged,
  signOut
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

class FirebaseSignupHandler {
  constructor() {
    this.currentUser = null;
    this.setupAuthStateListener();
  }

  setupAuthStateListener() {
    onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
      if (user) {
        console.log("User authenticated:", user.email);
        this.updateVerificationStatus(user);
        // Check email verification status periodically
        this.startVerificationCheck(user);
      }
    });
  }

  startVerificationCheck(user) {
    // Check email verification status every 2 seconds
    const checkInterval = setInterval(async () => {
      await user.reload();
      if (user.emailVerified) {
        clearInterval(checkInterval);
        this.updateVerificationStatus(user);
        console.log("Email verified!");
        
        // Submit to backend
        this.submitToBackend(user);
      } else {
        this.updateVerificationStatus(user);
      }
    }, 2000);

    // Stop checking after 10 minutes
    setTimeout(() => clearInterval(checkInterval), 600000);
  }

  async submitToBackend(user) {
    try {
      const response = await fetch('/api/firebase/signup-verify/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          uid: user.uid,
          email: user.email,
          email_verified: user.emailVerified,
          display_name: user.displayName || ''
        })
      });

      const data = await response.json();
      
      if (data.success) {
        // Show success message
        const messageDiv = document.querySelector('.signup_leftbody');
        const successDiv = document.createElement('div');
        successDiv.style.cssText = 'background: #e8f5e9; border: 1px solid #4caf50; border-radius: 8px; padding: 1rem; margin: 1rem 0; color: #2e7d32;';
        successDiv.innerHTML = `
          <h4 style="margin-top: 0;">✓ Email Verified!</h4>
          <p>Your account has been verified. Redirecting you to login...</p>
        `;
        messageDiv.appendChild(successDiv);
        
        // Redirect to home or dashboard after 2 seconds
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
      }
    } catch (error) {
      console.error('Backend submission error:', error);
    }
  }

  getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  }

  async signup(email, password) {
    try {
      // Create user in Firebase
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Send verification email
      await sendEmailVerification(user);
      
      return {
        success: true,
        message: "Account created! Please check your email to verify your account.",
        user: user
      };
    } catch (error) {
      return {
        success: false,
        message: this.getErrorMessage(error.code),
        error: error
      };
    }
  }

  async checkEmailVerification(user = null) {
    const currentUser = user || this.currentUser;
    if (!currentUser) return false;

    // Refresh to get latest email verification status
    await currentUser.reload();
    return currentUser.emailVerified;
  }

  updateVerificationStatus(user) {
    const verificationStatus = document.getElementById('firebase-verification-status');
    const submitBtn = document.querySelector('button[type="submit"]');
    
    if (verificationStatus && submitBtn) {
      if (user.emailVerified) {
        verificationStatus.innerHTML = '<span style="color: #28a745; font-weight: bold;">✓ Email Verified - Submitting...</span>';
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
        submitBtn.style.cursor = 'pointer';
      } else {
        verificationStatus.innerHTML = '<span style="color: #ff6b6b; font-weight: bold;">⏳ Waiting for email verification... Check your email</span>';
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.5';
        submitBtn.style.cursor = 'not-allowed';
      }
    }
  }

  getErrorMessage(errorCode) {
    const errors = {
      'auth/email-already-in-use': 'This email is already registered.',
      'auth/weak-password': 'Password should be at least 6 characters.',
      'auth/invalid-email': 'Please enter a valid email address.',
      'auth/operation-not-allowed': 'Email/password signup is not enabled.',
      'auth/user-disabled': 'This user account has been disabled.'
    };
    return errors[errorCode] || 'An error occurred during signup. Please try again.';
  }

  async signOutUser() {
    try {
      await signOut(auth);
      this.currentUser = null;
      return { success: true };
    } catch (error) {
      return { success: false, error: error };
    }
  }
}

// Export singleton instance
export const firebaseSignupHandler = new FirebaseSignupHandler();
// Also expose globally for non-module scripts
window.firebaseSignupHandler = firebaseSignupHandler;