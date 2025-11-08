/**
 * Authentication Manager
 * Handles user authentication, session management, and API token handling
 */

class AuthManager {
    constructor() {
        this.user = null;
        this.session = null;
        this.token = null;
        this.loadSession();
    }

    /**
     * Load session from localStorage
     */
    loadSession() {
        const sessionData = localStorage.getItem('studymate_session');
        if (sessionData) {
            try {
                const { user, session, token } = JSON.parse(sessionData);
                this.user = user;
                this.session = session;
                this.token = token || session?.access_token;
                
                // Verify token is still valid
                this.verifyToken();
            } catch (e) {
                console.error('Error loading session:', e);
                this.clearSession();
            }
        }
    }

    /**
     * Save session to localStorage
     */
    saveSession(user, session) {
        this.user = user;
        this.session = session;
        this.token = session?.access_token;
        
        localStorage.setItem('studymate_session', JSON.stringify({
            user,
            session,
            token: this.token
        }));
        
        this.updateUI();
    }

    /**
     * Clear session
     */
    clearSession() {
        this.user = null;
        this.session = null;
        this.token = null;
        localStorage.removeItem('studymate_session');
        this.updateUI();
    }

    /**
     * Check authentication and enforce login
     */
    checkAuthAndEnforce() {
        if (!this.isAuthenticated()) {
            this.showLoginRequired();
            return false;
        } else {
            this.showAppContent();
            return true;
        }
    }

    /**
     * Show login required (hide app, show auth modal)
     */
    showLoginRequired() {
        // Hide main app content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.display = 'none';
        }
        
        // Update UI to show "Sign In" button in sidebar
        this.updateUI();
        
        // Show auth modal
        showAuthModal();
    }

    /**
     * Show app content (hide auth modal)
     */
    showAppContent() {
        // Show main app content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.display = 'block';
        }
        
        // Hide auth modal
        const authModal = document.getElementById('authModal');
        if (authModal) {
            authModal.classList.add('hidden');
        }

        // Update UI to show user info in sidebar
        this.updateUI();

        // Reinitialize all features after successful login
        this.initializeFeatures();
    }

    /**
     * Initialize all app features
     */
    initializeFeatures() {
        // Initialize dashboard
        if (window.dashboardInstance) {
            window.dashboardInstance.init();
        }

        // Initialize chat
        if (window.chatInstance) {
            window.chatInstance.init();
        }

        // Initialize quiz
        if (window.quizInstance) {
            window.quizInstance.init();
        }

        // Initialize calendar
        if (window.calendarInstance) {
            window.calendarInstance.init();
        }

        // Initialize profile
        if (window.profileInstance) {
            window.profileInstance.init();
        }

        // Don't auto-start analytics, it starts when user navigates to analytics page
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return this.user !== null && this.token !== null;
    }

    /**
     * Get authorization header for API calls
     */
    getAuthHeader() {
        return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
    }

    /**
     * Sign up new user
     */
    async signup(email, password, fullName) {
        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email,
                    password,
                    full_name: fullName
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Signup failed');
            }

            if (data.user && data.session) {
                this.saveSession(data.user, data.session);
                this.showAppContent(); // Show app after successful signup
                return { success: true, message: data.message };
            }

            return { success: true, message: data.message };
        } catch (error) {
            console.error('Signup error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Login user
     */
    async login(email, password) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email,
                    password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Login failed');
            }

            this.saveSession(data.user, data.session);
            this.showAppContent(); // Show app after successful login
            return { success: true };
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            if (this.token) {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        ...this.getAuthHeader(),
                        'Content-Type': 'application/json'
                    }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearSession();
            // Show login modal and hide app content
            this.showLoginRequired();
        }
    }

    /**
     * Verify token is still valid
     */
    async verifyToken() {
        if (!this.token) {
            this.clearSession();
            return false;
        }

        try {
            const response = await fetch('/api/auth/user', {
                headers: this.getAuthHeader()
            });

            if (!response.ok) {
                this.clearSession();
                return false;
            }

            const data = await response.json();
            this.user = data.user;
            return true;
        } catch (error) {
            console.error('Token verification error:', error);
            this.clearSession();
            return false;
        }
    }

    /**
     * Get user profile
     */
    async getProfile() {
        try {
            const response = await fetch('/api/auth/profile', {
                headers: this.getAuthHeader()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch profile');
            }

            return await response.json();
        } catch (error) {
            console.error('Get profile error:', error);
            return null;
        }
    }

    /**
     * Update user profile
     */
    async updateProfile(data) {
        try {
            const response = await fetch('/api/auth/profile', {
                method: 'PUT',
                headers: {
                    ...this.getAuthHeader(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Failed to update profile');
            }

            return await response.json();
        } catch (error) {
            console.error('Update profile error:', error);
            return null;
        }
    }

    /**
     * Update UI based on auth state
     */
    updateUI() {
        // Update user display in sidebar
        const userDisplay = document.getElementById('userDisplay');
        if (userDisplay) {
            if (this.isAuthenticated()) {
                const userName = this.user?.user_metadata?.full_name || this.user?.email || 'User';
                userDisplay.innerHTML = `
                    <div class="user-profile">
                        <div class="user-avatar">${userName.charAt(0).toUpperCase()}</div>
                        <div class="user-info">
                            <div class="user-name">${userName}</div>
                            <div class="user-email">${this.user?.email || ''}</div>
                        </div>
                    </div>
                    <button class="btn-ghost btn-sm" onclick="authManager.logout()">Logout</button>
                `;
            } else {
                userDisplay.innerHTML = `
                    <button class="btn-primary btn-sm" onclick="showAuthModal()">Sign In</button>
                `;
            }
        }

        // Show/hide protected content
        const protectedElements = document.querySelectorAll('[data-requires-auth]');
        protectedElements.forEach(el => {
            if (this.isAuthenticated()) {
                el.style.display = '';
            } else {
                el.style.display = 'none';
            }
        });
    }

    /**
     * Make authenticated API call
     */
    async apiCall(url, options = {}) {
        if (!this.isAuthenticated()) {
            showAuthModal();
            throw new Error('Authentication required');
        }

        const headers = {
            ...options.headers,
            ...this.getAuthHeader()
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        // If unauthorized, clear session and show login
        if (response.status === 401) {
            this.clearSession();
            showAuthModal();
            throw new Error('Session expired. Please login again.');
        }

        return response;
    }
}

// Global auth manager instance
const authManager = new AuthManager();

// Auth Modal Functions
function showAuthModal() {
    document.getElementById('authModal').style.display = 'block';
    switchToLogin();
}

function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
    clearAuthErrors();
}

function switchToLogin() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('signupForm').style.display = 'none';
    clearAuthErrors();
}

function switchToSignup() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signupForm').style.display = 'block';
    clearAuthErrors();
}

function clearAuthErrors() {
    document.getElementById('loginError').classList.remove('show');
    document.getElementById('signupError').classList.remove('show');
}

function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.classList.add('show');
}

// Login Form Handler
async function handleLogin(event) {
    event.preventDefault();
    clearAuthErrors();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    const result = await authManager.login(email, password);

    if (result.success) {
        closeAuthModal();
        // Reload page to refresh data
        window.location.reload();
    } else {
        showError('loginError', result.error || 'Login failed. Please check your credentials.');
    }
}

// Signup Form Handler
async function handleSignup(event) {
    event.preventDefault();
    clearAuthErrors();

    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const passwordConfirm = document.getElementById('signupPasswordConfirm').value;

    // Validate password match
    if (password !== passwordConfirm) {
        showError('signupError', 'Passwords do not match');
        return;
    }

    const result = await authManager.signup(email, password, name);

    if (result.success) {
        showError('signupError', result.message || 'Account created! Signing you in...');
        // Auto-login after successful signup
        setTimeout(() => {
            closeAuthModal();
            window.location.reload();
        }, 2000);
    } else {
        showError('signupError', result.error || 'Signup failed. Please try again.');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('authModal');
    if (event.target === modal) {
        closeAuthModal();
    }
};

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', () => {
    authManager.updateUI();
});
