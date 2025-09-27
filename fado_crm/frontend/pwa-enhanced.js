// 📱 FADO CRM - PWA Enhanced JavaScript
// Advanced PWA features, offline support, and mobile optimizations

class PWAManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.installPrompt = null;
        this.registration = null;
        this.offlineData = new Map();
        this.syncQueue = [];

        this.init();
    }

    async init() {
        console.log('🚀 Initializing PWA Manager...');

        // Register service worker
        await this.registerServiceWorker();

        // Setup PWA install prompt
        this.setupInstallPrompt();

        // Setup offline detection
        this.setupOfflineDetection();

        // Setup background sync
        this.setupBackgroundSync();

        // Setup push notifications
        this.setupPushNotifications();

        // Setup mobile optimizations
        this.setupMobileOptimizations();

        // Setup update detection
        this.setupUpdateDetection();

        console.log('✅ PWA Manager initialized successfully');
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                this.registration = await navigator.serviceWorker.register('/service-worker.js', {
                    scope: '/'
                });

                console.log('✅ Service Worker registered:', this.registration.scope);

                // Handle service worker updates
                this.registration.addEventListener('updatefound', () => {
                    const newWorker = this.registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateAvailable();
                        }
                    });
                });

                // Listen for messages from service worker
                navigator.serviceWorker.addEventListener('message', (event) => {
                    this.handleServiceWorkerMessage(event.data);
                });

            } catch (error) {
                console.error('❌ Service Worker registration failed:', error);
            }
        }
    }

    setupInstallPrompt() {
        // PWA install prompt
        window.addEventListener('beforeinstallprompt', (event) => {
            event.preventDefault();
            this.installPrompt = event;

            // Show custom install prompt after delay
            setTimeout(() => {
                this.showInstallPrompt();
            }, 10000); // Show after 10 seconds
        });

        // Detect when PWA is installed
        window.addEventListener('appinstalled', () => {
            console.log('🎉 PWA installed successfully');
            this.hideInstallPrompt();
            this.showToast('Ứng dụng đã được cài đặt thành công!', 'success');
        });
    }

    showInstallPrompt() {
        if (!this.installPrompt || this.isPWAInstalled()) return;

        const promptHTML = `
            <div class="pwa-install-prompt" id="pwa-install-prompt">
                <div class="pwa-install-content">
                    <div class="pwa-install-icon">📱</div>
                    <div class="pwa-install-text">
                        <div class="pwa-install-title">Cài đặt FADO CRM</div>
                        <div class="pwa-install-description">Truy cập nhanh chóng từ màn hình chính</div>
                    </div>
                </div>
                <div class="pwa-install-buttons">
                    <button class="pwa-install-btn" onclick="pwaManager.hideInstallPrompt()">Bỏ qua</button>
                    <button class="pwa-install-btn primary" onclick="pwaManager.installPWA()">Cài đặt</button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', promptHTML);

        // Animate in
        setTimeout(() => {
            document.getElementById('pwa-install-prompt').classList.add('show');
        }, 100);
    }

    async installPWA() {
        if (!this.installPrompt) return;

        try {
            const result = await this.installPrompt.prompt();
            console.log('PWA install result:', result.outcome);

            if (result.outcome === 'accepted') {
                this.hideInstallPrompt();
            }

            this.installPrompt = null;
        } catch (error) {
            console.error('PWA installation error:', error);
        }
    }

    hideInstallPrompt() {
        const prompt = document.getElementById('pwa-install-prompt');
        if (prompt) {
            prompt.classList.remove('show');
            setTimeout(() => {
                prompt.remove();
            }, 300);
        }
    }

    isPWAInstalled() {
        return window.matchMedia('(display-mode: standalone)').matches ||
               window.navigator.standalone === true;
    }

    setupOfflineDetection() {
        // Online/offline detection
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.hideOfflineIndicator();
            this.syncOfflineData();
            this.showToast('Kết nối được khôi phục!', 'success');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showOfflineIndicator();
            this.showToast('Bạn đang offline. Một số tính năng có thể bị hạn chế.', 'warning');
        });

        // Show initial offline state
        if (!this.isOnline) {
            this.showOfflineIndicator();
        }
    }

    showOfflineIndicator() {
        let indicator = document.getElementById('offline-indicator');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.className = 'offline-indicator';
            indicator.innerHTML = `
                <i class="fas fa-wifi-slash"></i>
                <span>Offline</span>
            `;
            document.body.appendChild(indicator);
        }

        indicator.classList.add('show');
    }

    hideOfflineIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.classList.remove('show');
        }
    }

    setupUpdateDetection() {
        // Check for updates periodically
        setInterval(() => {
            if (this.registration) {
                this.registration.update();
            }
        }, 60000); // Check every minute
    }

    showUpdateAvailable() {
        let indicator = document.getElementById('update-indicator');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'update-indicator';
            indicator.className = 'update-indicator';
            indicator.innerHTML = `
                <i class="fas fa-download"></i>
                <span>Cập nhật có sẵn</span>
            `;
            indicator.onclick = () => this.applyUpdate();
            document.body.appendChild(indicator);
        }

        indicator.classList.add('show');
    }

    async applyUpdate() {
        if (this.registration && this.registration.waiting) {
            this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });

            // Reload page after service worker takes control
            navigator.serviceWorker.addEventListener('controllerchange', () => {
                window.location.reload();
            });
        }
    }

    setupBackgroundSync() {
        // Background sync for offline actions
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            console.log('✅ Background Sync is supported');
        } else {
            console.log('❌ Background Sync is not supported');
        }
    }

    async syncOfflineData() {
        if (!this.isOnline || this.syncQueue.length === 0) return;

        console.log('🔄 Syncing offline data...');

        const itemsToSync = [...this.syncQueue];
        this.syncQueue = [];

        for (const item of itemsToSync) {
            try {
                await this.syncItem(item);
            } catch (error) {
                console.error('❌ Failed to sync item:', item, error);
                // Re-add failed items to queue
                this.syncQueue.push(item);
            }
        }

        if (itemsToSync.length > 0) {
            this.showToast(`Đã đồng bộ ${itemsToSync.length - this.syncQueue.length} mục`, 'success');
        }
    }

    async syncItem(item) {
        const { type, method, url, data } = item;

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    setupPushNotifications() {
        // Push notifications setup
        if ('Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window) {
            console.log('✅ Push notifications are supported');

            // Request permission on user interaction
            document.addEventListener('click', () => {
                this.requestNotificationPermission();
            }, { once: true });

        } else {
            console.log('❌ Push notifications are not supported');
        }
    }

    async requestNotificationPermission() {
        if (Notification.permission === 'default') {
            try {
                const permission = await Notification.requestPermission();

                if (permission === 'granted') {
                    console.log('✅ Notification permission granted');
                    this.subscribeToNotifications();
                } else {
                    console.log('❌ Notification permission denied');
                }
            } catch (error) {
                console.error('Error requesting notification permission:', error);
            }
        }
    }

    async subscribeToNotifications() {
        if (!this.registration) return;

        try {
            const subscription = await this.registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.getVapidPublicKey()
            });

            console.log('✅ Push subscription:', subscription);

            // Send subscription to server
            await this.sendSubscriptionToServer(subscription);

        } catch (error) {
            console.error('Failed to subscribe to notifications:', error);
        }
    }

    getVapidPublicKey() {
        // In a real app, this would be your VAPID public key
        return 'YOUR_VAPID_PUBLIC_KEY_HERE';
    }

    async sendSubscriptionToServer(subscription) {
        try {
            await fetch('/api/notifications/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(subscription)
            });
        } catch (error) {
            console.error('Failed to send subscription to server:', error);
        }
    }

    setupMobileOptimizations() {
        // Viewport height fix for mobile browsers
        this.setupViewportHeight();

        // Touch optimizations
        this.setupTouchOptimizations();

        // Prevent zoom on form inputs (iOS)
        this.preventFormZoom();

        // Setup pull-to-refresh
        this.setupPullToRefresh();

        // Setup swipe gestures
        this.setupSwipeGestures();

        // Optimize scrolling
        this.optimizeScrolling();
    }

    setupViewportHeight() {
        // Fix viewport height issues on mobile
        function setVH() {
            let vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        }

        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', setVH);
    }

    setupTouchOptimizations() {
        // Add touch feedback to interactive elements
        document.addEventListener('touchstart', (e) => {
            const target = e.target.closest('.btn, .card, .list-item, [onclick], [data-bs-toggle]');
            if (target && !target.classList.contains('no-touch-feedback')) {
                target.style.transform = 'scale(0.98)';
                target.style.opacity = '0.8';
            }
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            const target = e.target.closest('.btn, .card, .list-item, [onclick], [data-bs-toggle]');
            if (target) {
                setTimeout(() => {
                    target.style.transform = '';
                    target.style.opacity = '';
                }, 150);
            }
        }, { passive: true });
    }

    preventFormZoom() {
        // Prevent zoom on form input focus (iOS)
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            document.addEventListener('focusin', (e) => {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                    const viewport = document.querySelector('meta[name="viewport"]');
                    if (viewport) {
                        viewport.content = 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no';
                    }
                }
            });

            document.addEventListener('focusout', () => {
                const viewport = document.querySelector('meta[name="viewport"]');
                if (viewport) {
                    viewport.content = 'width=device-width, initial-scale=1, user-scalable=yes';
                }
            });
        }
    }

    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let pulling = false;
        let refreshThreshold = 80;

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].pageY;
                pulling = false;
            }
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && startY) {
                currentY = e.touches[0].pageY;
                const pullDistance = currentY - startY;

                if (pullDistance > 10) {
                    pulling = true;
                    e.preventDefault();

                    const pullIndicator = this.getPullIndicator();

                    if (pullDistance < refreshThreshold) {
                        pullIndicator.style.transform = `translateY(${Math.min(pullDistance, 60)}px)`;
                        pullIndicator.style.opacity = pullDistance / refreshThreshold;
                        pullIndicator.innerHTML = '<i class="fas fa-arrow-down"></i> Kéo để làm mới';
                    } else {
                        pullIndicator.style.transform = `translateY(60px)`;
                        pullIndicator.style.opacity = '1';
                        pullIndicator.innerHTML = '<i class="fas fa-sync-alt"></i> Thả để làm mới';
                    }
                }
            }
        }, { passive: false });

        document.addEventListener('touchend', (e) => {
            if (pulling) {
                const pullDistance = currentY - startY;
                const pullIndicator = this.getPullIndicator();

                if (pullDistance >= refreshThreshold) {
                    this.refreshPage();
                }

                // Reset
                pullIndicator.style.transform = 'translateY(-100px)';
                pullIndicator.style.opacity = '0';
                pulling = false;
                startY = 0;
                currentY = 0;
            }
        }, { passive: true });
    }

    getPullIndicator() {
        let indicator = document.getElementById('pull-refresh-indicator');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'pull-refresh-indicator';
            indicator.style.cssText = `
                position: fixed;
                top: -50px;
                left: 50%;
                transform: translateX(-50%) translateY(-100px);
                background: #4A90E2;
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 14px;
                z-index: 1000;
                transition: all 0.3s ease;
                opacity: 0;
            `;
            document.body.appendChild(indicator);
        }

        return indicator;
    }

    async refreshPage() {
        const pullIndicator = this.getPullIndicator();
        pullIndicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang làm mới...';

        try {
            // Refresh data
            if (window.loadDashboard) {
                await window.loadDashboard();
            }
            if (window.loadCurrentTab) {
                await window.loadCurrentTab();
            }

            this.showToast('Dữ liệu đã được cập nhật', 'success');
        } catch (error) {
            console.error('Refresh failed:', error);
            this.showToast('Không thể làm mới dữ liệu', 'error');
        }
    }

    setupSwipeGestures() {
        let startX = 0;
        let startY = 0;
        let currentX = 0;
        let currentY = 0;

        document.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            startX = touch.pageX;
            startY = touch.pageY;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;

            const touch = e.touches[0];
            currentX = touch.pageX;
            currentY = touch.pageY;
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;

            const diffX = currentX - startX;
            const diffY = currentY - startY;

            // Only process significant swipes
            if (Math.abs(diffX) > 50 && Math.abs(diffY) < 100) {
                if (diffX > 0) {
                    // Swipe right
                    this.handleSwipeRight();
                } else {
                    // Swipe left
                    this.handleSwipeLeft();
                }
            }

            // Reset
            startX = 0;
            startY = 0;
            currentX = 0;
            currentY = 0;
        }, { passive: true });
    }

    handleSwipeRight() {
        // Navigate to previous tab or go back
        const activeTab = document.querySelector('.nav-link.active');
        if (activeTab && activeTab.previousElementSibling) {
            const prevTab = activeTab.previousElementSibling.querySelector('.nav-link');
            if (prevTab) {
                prevTab.click();
            }
        }
    }

    handleSwipeLeft() {
        // Navigate to next tab
        const activeTab = document.querySelector('.nav-link.active');
        if (activeTab && activeTab.nextElementSibling) {
            const nextTab = activeTab.nextElementSibling.querySelector('.nav-link');
            if (nextTab) {
                nextTab.click();
            }
        }
    }

    optimizeScrolling() {
        // Add momentum scrolling for iOS
        document.body.style.webkitOverflowScrolling = 'touch';

        // Optimize table scrolling on mobile
        const tables = document.querySelectorAll('.table-responsive');
        tables.forEach(table => {
            table.style.webkitOverflowScrolling = 'touch';
        });
    }

    handleServiceWorkerMessage(data) {
        switch (data.type) {
            case 'SW_ACTIVATED':
                console.log('Service Worker activated:', data.message);
                break;
            case 'CACHE_UPDATE':
                console.log('Cache updated:', data.message);
                break;
            case 'SYNC_COMPLETE':
                this.showToast('Dữ liệu đã được đồng bộ', 'success');
                break;
            default:
                console.log('Service Worker message:', data);
        }
    }

    // Offline data management
    saveOfflineData(key, data) {
        this.offlineData.set(key, {
            data: data,
            timestamp: Date.now()
        });

        // Also save to localStorage for persistence
        try {
            localStorage.setItem(`fado_offline_${key}`, JSON.stringify({
                data: data,
                timestamp: Date.now()
            }));
        } catch (error) {
            console.error('Failed to save offline data:', error);
        }
    }

    getOfflineData(key) {
        // Try memory first
        if (this.offlineData.has(key)) {
            return this.offlineData.get(key);
        }

        // Try localStorage
        try {
            const stored = localStorage.getItem(`fado_offline_${key}`);
            if (stored) {
                const parsed = JSON.parse(stored);
                this.offlineData.set(key, parsed);
                return parsed;
            }
        } catch (error) {
            console.error('Failed to get offline data:', error);
        }

        return null;
    }

    addToSyncQueue(type, method, url, data) {
        this.syncQueue.push({
            id: Date.now() + Math.random(),
            type: type,
            method: method,
            url: url,
            data: data,
            timestamp: Date.now()
        });

        console.log('Added to sync queue:', type, url);

        // Try to sync immediately if online
        if (this.isOnline) {
            setTimeout(() => this.syncOfflineData(), 1000);
        }
    }

    // Enhanced API call with offline support
    async apiCall(method, url, data = null) {
        if (!this.isOnline) {
            // Handle offline API calls
            return this.handleOfflineApiCall(method, url, data);
        }

        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(url, options);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            // Cache successful GET requests
            if (method === 'GET') {
                this.saveOfflineData(`api_${url}`, result);
            }

            return result;

        } catch (error) {
            console.error('API call failed:', error);

            // For POST/PUT requests, add to sync queue
            if (['POST', 'PUT', 'PATCH'].includes(method) && data) {
                this.addToSyncQueue('api', method, url, data);
                this.showToast('Đã lưu để đồng bộ khi online', 'info');
                return { success: true, queued: true };
            }

            // For GET requests, try offline cache
            if (method === 'GET') {
                const cached = this.getOfflineData(`api_${url}`);
                if (cached) {
                    this.showToast('Đang hiển thị dữ liệu offline', 'warning');
                    return cached.data;
                }
            }

            throw error;
        }
    }

    handleOfflineApiCall(method, url, data) {
        if (method === 'GET') {
            // Return cached data for GET requests
            const cached = this.getOfflineData(`api_${url}`);
            if (cached) {
                return Promise.resolve(cached.data);
            } else {
                return Promise.reject(new Error('No cached data available'));
            }
        } else {
            // Queue POST/PUT requests for later
            this.addToSyncQueue('api', method, url, data);
            this.showToast('Đã lưu để đồng bộ khi online', 'info');
            return Promise.resolve({ success: true, queued: true });
        }
    }

    showToast(message, type = 'info', duration = 3000) {
        const toastContainer = this.getToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast show align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'} border-0`;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);
    }

    getToastContainer() {
        let container = document.getElementById('toast-container');

        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        return container;
    }

    // Cache management
    async getCacheStatus() {
        if (this.registration) {
            return new Promise((resolve) => {
                const channel = new MessageChannel();

                channel.port1.onmessage = (event) => {
                    resolve(event.data);
                };

                this.registration.active.postMessage(
                    { type: 'GET_CACHE_STATUS' },
                    [channel.port2]
                );
            });
        }
        return null;
    }

    async clearCache(type = 'all') {
        if (this.registration) {
            return new Promise((resolve) => {
                const channel = new MessageChannel();

                channel.port1.onmessage = (event) => {
                    resolve(event.data);
                };

                this.registration.active.postMessage(
                    { type: 'CLEAR_CACHE', cacheType: type },
                    [channel.port2]
                );
            });
        }
    }
}

// Initialize PWA Manager
const pwaManager = new PWAManager();

// Global utilities
window.pwaManager = pwaManager;

// Enhanced API utility
window.api = {
    get: (url) => pwaManager.apiCall('GET', url),
    post: (url, data) => pwaManager.apiCall('POST', url, data),
    put: (url, data) => pwaManager.apiCall('PUT', url, data),
    delete: (url) => pwaManager.apiCall('DELETE', url)
};

// Mobile-specific event handlers
document.addEventListener('DOMContentLoaded', () => {
    // Add mobile classes
    if (window.innerWidth <= 768) {
        document.body.classList.add('mobile-device');
    }

    // Handle orientation changes
    window.addEventListener('orientationchange', () => {
        setTimeout(() => {
            // Force height recalculation
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);

            // Trigger resize event
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });

    // Add touch-friendly table handling
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        if (window.innerWidth <= 576) {
            table.closest('.table-responsive').classList.add('mobile-stack');

            // Add data-label attributes for mobile stacked view
            const headers = table.querySelectorAll('th');
            const cells = table.querySelectorAll('td');

            cells.forEach((cell, index) => {
                const columnIndex = index % headers.length;
                const headerText = headers[columnIndex]?.textContent || '';
                cell.setAttribute('data-label', headerText);
            });
        }
    });
});

// Performance monitoring
const perfObserver = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
        if (entry.entryType === 'navigation') {
            console.log(`Page load time: ${entry.loadEventEnd - entry.loadEventStart}ms`);
        }

        if (entry.entryType === 'paint') {
            console.log(`${entry.name}: ${entry.startTime}ms`);
        }
    }
});

try {
    perfObserver.observe({ entryTypes: ['navigation', 'paint'] });
} catch (e) {
    console.log('Performance Observer not supported');
}

console.log('📱 PWA Enhanced JavaScript loaded successfully!');