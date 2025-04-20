// Wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners once the DOM is ready
    setTimeout(setupEventListeners, 1000);
});

function setupEventListeners() {
    // Get elements
    const signinButton = document.getElementById('signin-button');
    const signupButton = document.getElementById('signup-button');
    const signoutButton = document.getElementById('signout-button');
    const emailInput = document.getElementById('email-input');
    const passwordInput = document.getElementById('password-input');
    const authStatus = document.getElementById('auth-status');
    
    if (!signinButton || !signupButton || !signoutButton) {
        console.log("Firebase Auth elements not found yet, retrying...");
        setTimeout(setupEventListeners, 1000);
        return;
    }
    
    console.log("Firebase Auth elements found, setting up event listeners");
    
    // Set up authentication state listener
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            // User is signed in
            authStatus.innerHTML = `
                <p style="text-align: center; color: green;">
                    Signed in as ${user.email}
                </p>
            `;
        } else {
            // User is signed out
            authStatus.innerHTML = `
                <p style="text-align: center; color: #666;">
                    Not signed in
                </p>
            `;
        }
    });
    
    // Sign In
    signinButton.addEventListener('click', function() {
        const email = emailInput.value;
        const password = passwordInput.value;
        
        firebase.auth().signInWithEmailAndPassword(email, password)
            .then((userCredential) => {
                // Signed in
                const user = userCredential.user;
                console.log("User signed in:", user.email);
            })
            .catch((error) => {
                console.error("Error signing in:", error);
                authStatus.innerHTML = `
                    <p style="text-align: center; color: red;">
                        Error: ${error.message}
                    </p>
                `;
            });
    });
    
    // Sign Up
    signupButton.addEventListener('click', function() {
        const email = emailInput.value;
        const password = passwordInput.value;
        
        firebase.auth().createUserWithEmailAndPassword(email, password)
            .then((userCredential) => {
                // Signed up
                const user = userCredential.user;
                console.log("User signed up:", user.email);
            })
            .catch((error) => {
                console.error("Error signing up:", error);
                authStatus.innerHTML = `
                    <p style="text-align: center; color: red;">
                        Error: ${error.message}
                    </p>
                `;
            });
    });
    
    // Sign Out
    signoutButton.addEventListener('click', function() {
        firebase.auth().signOut()
            .then(() => {
                console.log("User signed out");
            })
            .catch((error) => {
                console.error("Error signing out:", error);
            });
    });
} 