// 🔐 FADO CRM - Authentication Module
// Quản lý xác thực JWT siêu bảo mật! 🛡️

class AuthService {
    constructor() {
        try {
            const storedBase = (typeof localStorage !== 'undefined') ? localStorage.getItem('api_base') : null;
            this.API_BASE = storedBase || 'http://127.0.0.1:8003';
        } catch (e) {
            this.API_BASE = 'http://127.0.0.1:8003';
        }
        this.token = null;
        this.user = null;
        this.refreshToken = null;
        this.init();
    }

    init() {
        // Load stored tokens
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');

        // Load user info
        const userInfo = localStorage.getItem('user_info');
        if (userInfo) {
            try {
                this.user = JSON.parse(userInfo);
            } catch (e) {
                console.error('Error parsing user info:', e);
                this.clearAuth();
            }
        }

        // Setup automatic token refresh
        if (this.token) {
            this.setupTokenRefresh();
        }
    }

    // 🎫 Check if user is authenticated
    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    // 👤 Get current user
    getCurrentUser() {
        return this.user;
    }

    // 🎭 Check user role
    hasRole(role) {
        return this.user && this.user.vai_tro === role;
    }

    // 🎯 Check if user has any of the specified roles
    hasAnyRole(roles) {
        return this.user && roles.includes(this.user.vai_tro);
    }

    // 🔑 Get authorization header
    getAuthHeader() {
        return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
    }

    // 🌐 Make authenticated API call
    async apiCall(endpoint, options = {}) {
        const url = `${this.API_BASE}${endpoint}`;
        const isFormData = (typeof FormData !== 'undefined') && options && options.body instanceof FormData;
        const baseHeaders = this.getAuthHeader();
        const headers = {
            ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
            ...baseHeaders,
            ...(options.headers || {})
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Handle token expiration
            if (response.status === 401 && this.refreshToken) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry the original request
                    return await fetch(url, {
                        ...options,
                        headers: {
                            ...headers,
                            ...this.getAuthHeader()
                        }
                    });
                } else {
                    // Refresh failed, redirect to login
                    this.redirectToLogin();
                    throw new Error('Authentication failed');
                }
            }

            return response;
        } catch (error) {
            console.error('API call error:', error);
            throw error;
        }
    }

    // 🔄 Refresh access token
    async refreshAccessToken() {
        if (!this.refreshToken) {
            return false;
        }

        try {
            const response = await fetch(`${this.API_BASE}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                localStorage.setItem('access_token', this.token);
                return true;
            } else {
                // Refresh token is invalid
                this.clearAuth();
                return false;
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            this.clearAuth();
            return false;
        }
    }

    // ⏰ Setup automatic token refresh
    setupTokenRefresh() {
        // Refresh token every 25 minutes (tokens expire in 30 minutes)
        setInterval(async () => {
            if (this.isAuthenticated()) {
                await this.refreshAccessToken();
            }
        }, 25 * 60 * 1000); // 25 minutes
    }

    // 🗑️ Clear authentication data
    clearAuth() {
        this.token = null;
        this.refreshToken = null;
        this.user = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_info');
    }

    // 🚪 Logout user
    logout() {
        this.clearAuth();
        this.redirectToLogin();
    }

    // 🔄 Redirect to login page
    redirectToLogin() {
        if (window.location.pathname !== '/login.html') {
            window.location.href = 'login.html';
        }
    }

    // ✅ Validate authentication and redirect if needed
    requireAuth() {
        if (!this.isAuthenticated()) {
            this.redirectToLogin();
            return false;
        }
        return true;
    }

    // 🎭 Require specific role
    requireRole(role, showError = true) {
        if (!this.requireAuth()) {
            return false;
        }

        if (!this.hasRole(role)) {
            if (showError) {
                this.showError(`Bạn cần quyền ${role} để thực hiện thao tác này`);
            }
            return false;
        }
        return true;
    }

    // 🎯 Require any of the specified roles
    requireAnyRole(roles, showError = true) {
        if (!this.requireAuth()) {
            return false;
        }

        if (!this.hasAnyRole(roles)) {
            if (showError) {
                this.showError(`Bạn cần một trong các quyền: ${roles.join(', ')}`);
            }
            return false;
        }
        return true;
    }

    // 📧 Get current user email
    getUserEmail() {
        return this.user ? this.user.email : null;
    }

    // 📛 Get current user name
    getUserName() {
        return this.user ? this.user.ho_ten : 'User';
    }

    // 🎭 Get current user role display name
    getUserRoleDisplay() {
        if (!this.user) return '';

        const roleNames = {
            'admin': '👑 Admin',
            'manager': '👨‍💼 Manager',
            'staff': '👨‍💻 Staff',
            'viewer': '👁️ Viewer'
        };

        return roleNames[this.user.vai_tro] || this.user.vai_tro;
    }

    // 🚨 Show error message (to be implemented in UI)
    showError(message) {
        // This will be implemented in the main app
        console.error('Auth Error:', message);

        // Try to show toast if available
        if (window.showToast) {
            window.showToast(message, 'error');
        } else {
            alert(message);
        }
    }

    // 📊 Get user permissions
    getPermissions() {
        if (!this.user) return [];

        const permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users', 'manage_system'],
            'manager': ['read', 'write', 'delete', 'manage_data'],
            'staff': ['read', 'write'],
            'viewer': ['read']
        };

        return permissions[this.user.vai_tro] || [];
    }

    // 🔒 Check specific permission
    hasPermission(permission) {
        return this.getPermissions().includes(permission);
    }
}

// 🌟 Global auth service instance
window.authService = new AuthService();

// 🎯 Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthService;
}

// 🔧 Helper functions for easy access
window.isAuthenticated = () => window.authService.isAuthenticated();
window.getCurrentUser = () => window.authService.getCurrentUser();
window.hasRole = (role) => window.authService.hasRole(role);
window.hasAnyRole = (roles) => window.authService.hasAnyRole(roles);
window.requireAuth = () => window.authService.requireAuth();
window.requireRole = (role) => window.authService.requireRole(role);
window.logout = () => window.authService.logout();

console.log('🔐 Auth service initialized successfully!');