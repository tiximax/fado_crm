// 🔔 FADO CRM - Real-time Notifications System
// Thông báo thời gian thực như Facebook! 🚀

class NotificationManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectInterval = 5000;
        this.maxReconnectAttempts = 5;
        this.reconnectAttempts = 0;
        this.token = localStorage.getItem('token');
        this.notifications = [];
        this.maxNotifications = 10;

        this.init();
    }

    init() {
        if (!this.token) {
            console.warn('🔔 No token found, WebSocket notifications disabled');
            return;
        }

        this.createNotificationContainer();
        this.connect();
        this.setupHeartbeat();
    }

    createNotificationContainer() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        // Add CSS if not already added
        if (!document.getElementById('notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    max-width: 400px;
                    pointer-events: none;
                }

                .notification {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    margin-bottom: 12px;
                    overflow: hidden;
                    transform: translateX(100%);
                    transition: all 0.3s ease;
                    pointer-events: auto;
                    border-left: 4px solid #667eea;
                }

                .notification.show {
                    transform: translateX(0);
                }

                .notification.hide {
                    transform: translateX(100%);
                    opacity: 0;
                }

                .notification.high {
                    border-left-color: #e53e3e;
                    animation: pulse 2s infinite;
                }

                .notification.medium {
                    border-left-color: #dd6b20;
                }

                .notification.low {
                    border-left-color: #38a169;
                }

                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }

                .notification-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 12px 16px 8px;
                }

                .notification-title {
                    font-weight: 600;
                    color: #2d3748;
                    font-size: 14px;
                    margin: 0;
                }

                .notification-close {
                    background: none;
                    border: none;
                    color: #a0aec0;
                    cursor: pointer;
                    font-size: 18px;
                    padding: 0;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: all 0.2s ease;
                }

                .notification-close:hover {
                    background: #f7fafc;
                    color: #4a5568;
                }

                .notification-body {
                    padding: 0 16px 12px;
                }

                .notification-message {
                    color: #4a5568;
                    font-size: 13px;
                    line-height: 1.4;
                    margin: 0 0 8px;
                }

                .notification-time {
                    color: #a0aec0;
                    font-size: 11px;
                    font-weight: 500;
                }

                .notification-badge {
                    position: fixed;
                    top: 20px;
                    right: 380px;
                    background: #667eea;
                    color: white;
                    border-radius: 50%;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 11px;
                    font-weight: bold;
                    z-index: 10000;
                    transform: scale(0);
                    transition: transform 0.3s ease;
                }

                .notification-badge.show {
                    transform: scale(1);
                }

                .notification-bell {
                    position: fixed;
                    top: 15px;
                    right: 420px;
                    background: rgba(255, 255, 255, 0.9);
                    border: 2px solid #667eea;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;
                    z-index: 9998;
                }

                .notification-bell:hover {
                    background: white;
                    transform: scale(1.1);
                }

                .notification-bell.new {
                    animation: shake 0.5s ease;
                }

                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    25% { transform: translateX(-5px); }
                    75% { transform: translateX(5px); }
                }

                .connection-status {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: rgba(255, 255, 255, 0.95);
                    padding: 8px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    color: #4a5568;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    backdrop-filter: blur(10px);
                    display: none;
                    align-items: center;
                    gap: 6px;
                    z-index: 9999;
                }

                .status-dot {
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                    background: #48bb78;
                }

                .status-dot.disconnected {
                    background: #e53e3e;
                }

                .status-dot.connecting {
                    background: #dd6b20;
                    animation: pulse 1s infinite;
                }
            `;
            document.head.appendChild(styles);
        }

        // Add notification bell
        if (!document.getElementById('notification-bell')) {
            const bell = document.createElement('div');
            bell.id = 'notification-bell';
            bell.className = 'notification-bell';
            bell.innerHTML = '🔔';
            bell.onclick = () => this.toggleNotificationHistory();
            document.body.appendChild(bell);
        }

        // Add connection status
        if (!document.getElementById('connection-status')) {
            const status = document.createElement('div');
            status.id = 'connection-status';
            status.className = 'connection-status';
            status.innerHTML = '<div class="status-dot"></div>Đã kết nối';
            document.body.appendChild(status);
        }
    }

    connect() {
        if (!this.token) {
            console.warn('🔔 Cannot connect: No token available');
            return;
        }

        try {
            const wsUrl = `ws://localhost:8000/ws/${this.token}`;
            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log('🔔 WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
                this.showNotification({
                    title: '🎉 Kết nối thành công',
                    message: 'Thông báo thời gian thực đã được kích hoạt',
                    priority: 'low',
                    timestamp: new Date().toISOString()
                });
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleNotification(data);
                } catch (error) {
                    console.error('🔔 Error parsing notification:', error);
                }
            };

            this.socket.onclose = () => {
                console.log('🔔 WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                this.scheduleReconnect();
            };

            this.socket.onerror = (error) => {
                console.error('🔔 WebSocket error:', error);
                this.updateConnectionStatus('disconnected');
            };

        } catch (error) {
            console.error('🔔 WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.updateConnectionStatus('connecting');

            setTimeout(() => {
                console.log(`🔔 Reconnection attempt ${this.reconnectAttempts}`);
                this.connect();
            }, this.reconnectInterval);
        } else {
            this.updateConnectionStatus('disconnected');
            this.showNotification({
                title: '❌ Mất kết nối',
                message: 'Không thể kết nối đến server thông báo',
                priority: 'high',
                timestamp: new Date().toISOString()
            });
        }
    }

    updateConnectionStatus(status) {
        const statusEl = document.getElementById('connection-status');
        const dot = statusEl.querySelector('.status-dot');

        if (status === 'connected') {
            statusEl.style.display = 'none';
            dot.className = 'status-dot';
        } else if (status === 'connecting') {
            statusEl.style.display = 'flex';
            statusEl.innerHTML = '<div class="status-dot connecting"></div>Đang kết nối...';
        } else {
            statusEl.style.display = 'flex';
            statusEl.innerHTML = '<div class="status-dot disconnected"></div>Mất kết nối';
        }
    }

    setupHeartbeat() {
        setInterval(() => {
            if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'ping',
                    timestamp: Date.now()
                }));
            }
        }, 30000); // 30 seconds
    }

    handleNotification(data) {
        console.log('🔔 Received notification:', data);

        // Handle system messages
        if (data.type === 'system') {
            if (data.event === 'connected') {
                return; // Already handled in onopen
            }
            return;
        }

        // Handle pong response
        if (data.type === 'pong') {
            return;
        }

        // Show notification
        this.showNotification(data);

        // Add to history
        this.addToHistory(data);

        // Play sound for high priority notifications
        if (data.priority === 'high') {
            this.playNotificationSound();
        }

        // Animate notification bell
        this.animateBell();
    }

    showNotification(data) {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');

        notification.className = `notification ${data.priority || 'medium'}`;
        notification.innerHTML = `
            <div class="notification-header">
                <h4 class="notification-title">${data.title || '🔔 Thông báo'}</h4>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="notification-body">
                <p class="notification-message">${data.message}</p>
                <div class="notification-time">${this.formatTime(data.timestamp)}</div>
            </div>
        `;

        container.appendChild(notification);

        // Show animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Auto-hide after 5 seconds (except high priority)
        if (data.priority !== 'high') {
            setTimeout(() => {
                notification.classList.add('hide');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }, 5000);
        }

        // Limit notifications count
        const notifications = container.querySelectorAll('.notification');
        if (notifications.length > this.maxNotifications) {
            notifications[0].remove();
        }
    }

    addToHistory(data) {
        this.notifications.unshift({
            ...data,
            id: Date.now(),
            read: false
        });

        // Limit history
        if (this.notifications.length > 50) {
            this.notifications = this.notifications.slice(0, 50);
        }

        // Update badge
        this.updateNotificationBadge();
    }

    updateNotificationBadge() {
        const unreadCount = this.notifications.filter(n => !n.read).length;

        let badge = document.getElementById('notification-badge');
        if (!badge && unreadCount > 0) {
            badge = document.createElement('div');
            badge.id = 'notification-badge';
            badge.className = 'notification-badge';
            document.body.appendChild(badge);
        }

        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
                badge.classList.add('show');
            } else {
                badge.classList.remove('show');
            }
        }
    }

    animateBell() {
        const bell = document.getElementById('notification-bell');
        bell.classList.add('new');
        setTimeout(() => {
            bell.classList.remove('new');
        }, 500);
    }

    playNotificationSound() {
        // Create audio context and play notification sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 800;
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.1);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.warn('🔔 Could not play notification sound:', error);
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) { // Less than 1 minute
            return 'Vừa xong';
        } else if (diff < 3600000) { // Less than 1 hour
            return `${Math.floor(diff / 60000)} phút trước`;
        } else if (diff < 86400000) { // Less than 1 day
            return `${Math.floor(diff / 3600000)} giờ trước`;
        } else {
            return date.toLocaleDateString('vi-VN');
        }
    }

    toggleNotificationHistory() {
        // Mark all as read
        this.notifications.forEach(n => n.read = true);
        this.updateNotificationBadge();

        // Show history modal (implement if needed)
        console.log('🔔 Notification history:', this.notifications);
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        this.isConnected = false;
        this.updateConnectionStatus('disconnected');
    }

    // Public methods for manual notifications
    success(title, message) {
        this.showNotification({
            title,
            message,
            priority: 'low',
            timestamp: new Date().toISOString()
        });
    }

    warning(title, message) {
        this.showNotification({
            title,
            message,
            priority: 'medium',
            timestamp: new Date().toISOString()
        });
    }

    error(title, message) {
        this.showNotification({
            title,
            message,
            priority: 'high',
            timestamp: new Date().toISOString()
        });
    }
}

// 🌟 Initialize notification manager
let notificationManager;

document.addEventListener('DOMContentLoaded', () => {
    notificationManager = new NotificationManager();
});

// 🔄 Reinitialize on token change
document.addEventListener('tokenChanged', () => {
    if (notificationManager) {
        notificationManager.disconnect();
        notificationManager = new NotificationManager();
    }
});

// 🚀 Export for global use
window.notifications = {
    success: (title, message) => notificationManager?.success(title, message),
    warning: (title, message) => notificationManager?.warning(title, message),
    error: (title, message) => notificationManager?.error(title, message)
};
