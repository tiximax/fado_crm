/**
 * 🌙✨ FADO CRM - Theme Management System
 * Professional dark/light mode switcher với localStorage persistence
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || 'auto';
        this.themes = ['light', 'dark', 'auto'];
        this.themeIcons = {
            light: 'fas fa-sun',
            dark: 'fas fa-moon',
            auto: 'fas fa-adjust'
        };
        this.themeLabels = {
            light: 'Light Mode',
            dark: 'Dark Mode',
            auto: 'Auto Mode'
        };

        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createThemeToggle();
        this.bindEvents();
        this.detectSystemThemeChange();
    }

    /**
     * Get stored theme from localStorage
     */
    getStoredTheme() {
        try {
            return localStorage.getItem('fado-crm-theme');
        } catch (error) {
            console.warn('localStorage not available, using default theme');
            return null;
        }
    }

    /**
     * Store theme in localStorage
     */
    storeTheme(theme) {
        try {
            localStorage.setItem('fado-crm-theme', theme);
        } catch (error) {
            console.warn('Could not store theme preference');
        }
    }

    /**
     * Apply theme to document
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.storeTheme(theme);
        this.updateThemeToggleUI();
    }

    /**
     * Get next theme in cycle
     */
    getNextTheme() {
        const currentIndex = this.themes.indexOf(this.currentTheme);
        return this.themes[(currentIndex + 1) % this.themes.length];
    }

    /**
     * Toggle to next theme
     */
    toggleTheme() {
        const nextTheme = this.getNextTheme();
        this.applyTheme(nextTheme);
        this.showThemeChangeNotification(nextTheme);
    }

    /**
     * Create theme toggle button
     */
    createThemeToggle() {
        // Check if toggle already exists
        if (document.getElementById('themeToggle')) return;

        const toggle = document.createElement('button');
        toggle.id = 'themeToggle';
        toggle.className = 'theme-toggle';
        toggle.innerHTML = `
            <i class="${this.themeIcons[this.currentTheme]}"></i>
            <span class="theme-label">${this.themeLabels[this.currentTheme]}</span>
        `;
        toggle.title = 'Switch theme (Light / Dark / Auto)';
        toggle.setAttribute('aria-label', 'Toggle theme');

        // Add to navigation user section
        const navUser = document.querySelector('.nav-user');
        if (navUser) {
            navUser.insertBefore(toggle, navUser.firstChild);
        } else {
            // Fallback: add to nav-links
            const navLinks = document.querySelector('.nav-links');
            if (navLinks) {
                navLinks.appendChild(toggle);
            }
        }
    }

    /**
     * Update theme toggle UI
     */
    updateThemeToggleUI() {
        const toggle = document.getElementById('themeToggle');
        if (!toggle) return;

        const icon = toggle.querySelector('i');
        const label = toggle.querySelector('.theme-label');

        if (icon) {
            icon.className = this.themeIcons[this.currentTheme];
        }

        if (label) {
            label.textContent = this.themeLabels[this.currentTheme];
        }

        toggle.title = `Current: ${this.themeLabels[this.currentTheme]}. Click to switch.`;
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Theme toggle click
        document.addEventListener('click', (e) => {
            if (e.target.closest('#themeToggle')) {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Keyboard shortcut: Ctrl+Shift+T
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Alt+T shortcut (alternative)
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key.toLowerCase() === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    /**
     * Detect system theme changes (for auto mode)
     */
    detectSystemThemeChange() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

            mediaQuery.addEventListener('change', (e) => {
                if (this.currentTheme === 'auto') {
                    // Re-apply auto theme to trigger updates
                    this.applyTheme('auto');
                    this.showThemeChangeNotification('auto', 'System theme changed');
                }
            });
        }
    }

    /**
     * Show theme change notification
     */
    showThemeChangeNotification(theme, customMessage = null) {
        const message = customMessage || `Switched to ${this.themeLabels[theme]}`;

        // Try to use existing notification system
        if (window.showNotification) {
            window.showNotification(message, 'info', 2000);
        } else {
            // Fallback: simple toast
            this.showSimpleToast(message);
        }
    }

    /**
     * Simple toast notification fallback
     */
    showSimpleToast(message) {
        // Remove existing toast
        const existingToast = document.getElementById('themeToast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.id = 'themeToast';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary-color);
            color: white;
            padding: 12px 20px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            animation: slideInRight 0.3s ease;
            font-size: 14px;
            font-weight: 500;
        `;

        toast.innerHTML = `
            <i class="fas fa-palette" style="margin-right: 8px;"></i>
            ${message}
        `;

        document.body.appendChild(toast);

        // Add slide animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        // Auto remove after 2 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
                if (style.parentNode) {
                    style.remove();
                }
            }, 300);
        }, 2000);
    }

    /**
     * Get current effective theme (resolves 'auto' to actual theme)
     */
    getEffectiveTheme() {
        if (this.currentTheme === 'auto') {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                return 'dark';
            }
            return 'light';
        }
        return this.currentTheme;
    }

    /**
     * Set specific theme
     */
    setTheme(theme) {
        if (this.themes.includes(theme)) {
            this.applyTheme(theme);
            this.showThemeChangeNotification(theme);
        }
    }

    /**
     * Get theme information for external use
     */
    getThemeInfo() {
        return {
            current: this.currentTheme,
            effective: this.getEffectiveTheme(),
            available: this.themes,
            labels: this.themeLabels
        };
    }

    /**
     * Initialize theme from URL parameter (for demo/testing)
     */
    initFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const themeParam = urlParams.get('theme');

        if (themeParam && this.themes.includes(themeParam)) {
            this.applyTheme(themeParam);
        }
    }

    /**
     * Add theme to specific element
     */
    applyThemeToElement(element, theme = null) {
        const targetTheme = theme || this.currentTheme;
        element.setAttribute('data-theme', targetTheme);
    }

    /**
     * Check if dark mode is active
     */
    isDarkMode() {
        return this.getEffectiveTheme() === 'dark';
    }

    /**
     * Check if light mode is active
     */
    isLightMode() {
        return this.getEffectiveTheme() === 'light';
    }
}

// Global theme manager instance
window.themeManager = new ThemeManager();

// Initialize theme from URL if present
window.themeManager.initFromURL();

// Expose theme functions globally for easy access
window.toggleTheme = () => window.themeManager.toggleTheme();
window.setTheme = (theme) => window.themeManager.setTheme(theme);
window.getTheme = () => window.themeManager.getThemeInfo();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Theme manager is already initialized in constructor
        console.log('🎨 Theme Manager initialized:', window.themeManager.getThemeInfo());
    });
} else {
    console.log('🎨 Theme Manager initialized:', window.themeManager.getThemeInfo());
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}