/**
 * 📊 FADO CRM - Enhanced Interactive Dashboard
 * Real-time dashboard với animated charts và live updates
 */

class EnhancedDashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.updateInterval = 30000; // 30 seconds
        this.charts = {};
        this.counters = {};
        this.isInitialized = false;

        this.init();
    }

    async init() {
        if (this.isInitialized) return;

        try {
            await this.loadData();
            this.setupRealTimeUpdates();
            this.setupAnimatedCounters();
            this.setupInteractiveCharts();
            this.setupQuickActions();
            this.isInitialized = true;

            console.log('📊 Enhanced Dashboard initialized successfully');
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showErrorState();
        }
    }

    async loadData() {
        try {
            const response = await window.authService.apiCall('/dashboard');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.updateStats(data);
            await this.loadRecentActivities();

        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            throw error;
        }
    }

    updateStats(data) {
        // Animate counter updates
        this.animateCounter('total-customers', data.customers || 0);
        this.animateCounter('total-orders', data.orders || 0);
        this.animateCounter('monthly-revenue', data.revenue || 0, true);
        this.animateCounter('pending-orders', data.orders || 0);

        // Update additional metrics
        this.updateStatCard('total-customers', data.customers, '👥 Tổng Khách Hàng');
        this.updateStatCard('total-orders', data.orders, '📋 Tổng Đơn Hàng');
        this.updateStatCard('monthly-revenue', data.revenue, '💰 Doanh Thu', true);
        this.updateStatCard('pending-orders', data.orders, '⏰ Đơn Chờ Xử Lý');
    }

    animateCounter(elementId, targetValue, isCurrency = false) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
        const duration = 2000; // 2 seconds
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function for smooth animation
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutCubic);

            if (isCurrency) {
                element.textContent = new Intl.NumberFormat('vi-VN', {
                    style: 'currency',
                    currency: 'VND'
                }).format(currentValue);
            } else {
                element.textContent = new Intl.NumberFormat().format(currentValue);
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    updateStatCard(elementId, value, label, isCurrency = false) {
        const card = document.querySelector(`#${elementId}`).closest('.stat-card');
        if (!card) return;

        // Add pulse animation for updates
        card.style.animation = 'pulse 0.6s ease-in-out';
        setTimeout(() => {
            card.style.animation = '';
        }, 600);

        // Update trend indicator (mock data for demo)
        const trend = Math.random() > 0.5 ? 'up' : 'down';
        const trendPercent = (Math.random() * 20).toFixed(1);

        let trendHtml = card.querySelector('.trend-indicator');
        if (!trendHtml) {
            trendHtml = document.createElement('div');
            trendHtml.className = 'trend-indicator';
            card.querySelector('.stat-content').appendChild(trendHtml);
        }

        trendHtml.innerHTML = `
            <small class="trend ${trend}">
                <i class="fas fa-arrow-${trend === 'up' ? 'up' : 'down'}"></i>
                ${trendPercent}% từ tháng trước
            </small>
        `;
    }

    async loadRecentActivities() {
        try {
            // Load recent orders
            const ordersResponse = await fetch(`${this.apiBaseUrl}/api/orders?limit=5`);
            if (ordersResponse.ok) {
                const orders = await ordersResponse.json();
                this.updateRecentOrders(orders);
            }

            // Load new customers
            const customersResponse = await fetch(`${this.apiBaseUrl}/api/customers?limit=5`);
            if (customersResponse.ok) {
                const customers = await customersResponse.json();
                this.updateNewCustomers(customers);
            }

        } catch (error) {
            console.error('Failed to load recent activities:', error);
        }
    }

    updateRecentOrders(orders) {
        const container = document.getElementById('recent-orders');
        if (!container) return;

        if (orders.length === 0) {
            container.innerHTML = '<div class="empty-state">Chưa có đơn hàng nào 📭</div>';
            return;
        }

        container.innerHTML = orders.map(order => `
            <div class="activity-item order-item" data-order-id="${order.id}">
                <div class="activity-icon">
                    <i class="fas fa-shopping-cart"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">Đơn hàng ${order.ma_don_hang}</div>
                    <div class="activity-subtitle">
                        Khách hàng ID: ${order.khach_hang_id} •
                        <span class="order-amount">$${order.tong_tien}</span>
                    </div>
                    <div class="activity-meta">
                        <span class="status-badge status-${this.getStatusClass(order.trang_thai)}">
                            ${order.trang_thai}
                        </span>
                        <span class="activity-time">${this.formatTime(order.ngay_tao)}</span>
                    </div>
                </div>
                <div class="activity-actions">
                    <button class="btn btn-sm btn-outline" onclick="viewOrderDetails(${order.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </div>
        `).join('');

        // Add hover animations
        this.addActivityAnimations(container);
    }

    updateNewCustomers(customers) {
        const container = document.getElementById('new-customers');
        if (!container) return;

        if (customers.length === 0) {
            container.innerHTML = '<div class="empty-state">Chưa có khách hàng mới 👤</div>';
            return;
        }

        container.innerHTML = customers.map(customer => `
            <div class="activity-item customer-item" data-customer-id="${customer.id}">
                <div class="activity-icon">
                    <i class="fas fa-user-plus"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${customer.ho_ten}</div>
                    <div class="activity-subtitle">
                        <i class="fas fa-envelope"></i> ${customer.email}
                    </div>
                    <div class="activity-meta">
                        <span class="type-badge type-${customer.loai_khach_hang}">
                            ${customer.loai_khach_hang}
                        </span>
                        <span class="activity-time">${this.formatTime(customer.ngay_tao)}</span>
                    </div>
                </div>
                <div class="activity-actions">
                    <button class="btn btn-sm btn-outline" onclick="viewCustomerDetails(${customer.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </div>
        `).join('');

        // Add hover animations
        this.addActivityAnimations(container);
    }

    addActivityAnimations(container) {
        const items = container.querySelectorAll('.activity-item');
        items.forEach((item, index) => {
            // Stagger animation
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';

            setTimeout(() => {
                item.style.transition = 'all 0.5s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);

            // Hover effects
            item.addEventListener('mouseenter', () => {
                item.style.transform = 'translateY(-2px) scale(1.02)';
                item.style.boxShadow = 'var(--shadow-lg)';
            });

            item.addEventListener('mouseleave', () => {
                item.style.transform = 'translateY(0) scale(1)';
                item.style.boxShadow = 'var(--shadow-sm)';
            });
        });
    }

    setupRealTimeUpdates() {
        // Update every 30 seconds
        setInterval(async () => {
            try {
                await this.loadData();
                this.showUpdateIndicator();
            } catch (error) {
                console.error('Real-time update failed:', error);
            }
        }, this.updateInterval);

        // Add visual indicator for updates
        this.createUpdateIndicator();
    }

    showUpdateIndicator() {
        const indicator = document.getElementById('update-indicator');
        if (indicator) {
            indicator.style.display = 'flex';
            indicator.style.animation = 'pulse 1s ease-in-out';

            setTimeout(() => {
                indicator.style.animation = 'fadeOut 0.5s ease-in-out';
                setTimeout(() => {
                    indicator.style.display = 'none';
                }, 500);
            }, 2000);
        }
    }

    createUpdateIndicator() {
        if (document.getElementById('update-indicator')) return;

        const indicator = document.createElement('div');
        indicator.id = 'update-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 8px 16px;
            border-radius: var(--border-radius);
            font-size: 12px;
            font-weight: 500;
            display: none;
            align-items: center;
            gap: 8px;
            z-index: 1000;
            box-shadow: var(--shadow-md);
        `;

        indicator.innerHTML = `
            <i class="fas fa-sync-alt fa-spin"></i>
            Đã cập nhật dữ liệu
        `;

        document.body.appendChild(indicator);
    }

    setupAnimatedCounters() {
        // Add counter animations on scroll
        const statCards = document.querySelectorAll('.stat-card');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target.querySelector('h3');
                    if (counter && !counter.dataset.animated) {
                        counter.dataset.animated = 'true';
                        const value = parseInt(counter.textContent.replace(/[^0-9]/g, '')) || 0;
                        this.animateCounter(counter.id || counter.textContent, value);
                    }
                }
            });
        }, { threshold: 0.5 });

        statCards.forEach(card => observer.observe(card));
    }

    setupInteractiveCharts() {
        // Add mini charts to stat cards
        this.addMiniCharts();

        // Setup chart hover effects
        document.querySelectorAll('.stat-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                const chart = card.querySelector('.mini-chart');
                if (chart) {
                    chart.style.transform = 'scale(1.05)';
                }
            });

            card.addEventListener('mouseleave', () => {
                const chart = card.querySelector('.mini-chart');
                if (chart) {
                    chart.style.transform = 'scale(1)';
                }
            });
        });
    }

    addMiniCharts() {
        const statCards = document.querySelectorAll('.stat-card');

        statCards.forEach((card, index) => {
            if (card.querySelector('.mini-chart')) return;

            const chartContainer = document.createElement('div');
            chartContainer.className = 'mini-chart';
            chartContainer.style.cssText = `
                position: absolute;
                top: 16px;
                right: 16px;
                width: 60px;
                height: 30px;
                opacity: 0.3;
                transition: var(--transition-normal);
            `;

            // Generate sample chart data
            const chartData = this.generateMiniChartData();
            chartContainer.innerHTML = this.createSVGChart(chartData);

            card.style.position = 'relative';
            card.appendChild(chartContainer);
        });
    }

    generateMiniChartData() {
        const points = [];
        for (let i = 0; i < 7; i++) {
            points.push(Math.random() * 100);
        }
        return points;
    }

    createSVGChart(data) {
        const max = Math.max(...data);
        const points = data.map((value, index) => {
            const x = (index / (data.length - 1)) * 60;
            const y = 30 - (value / max) * 30;
            return `${x},${y}`;
        }).join(' ');

        return `
            <svg width="60" height="30" viewBox="0 0 60 30">
                <polyline
                    points="${points}"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                />
            </svg>
        `;
    }

    setupQuickActions() {
        // Add floating quick action button
        this.createQuickActionButton();
    }

    createQuickActionButton() {
        if (document.getElementById('quick-actions-fab')) return;

        const fab = document.createElement('div');
        fab.id = 'quick-actions-fab';
        fab.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: var(--primary-color);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: var(--shadow-lg);
            transition: var(--transition-normal);
            z-index: 1000;
            transform: scale(0);
            animation: fabEnter 0.5s ease 1s forwards;
        `;

        fab.innerHTML = '<i class="fas fa-plus"></i>';

        fab.addEventListener('click', () => {
            this.showQuickActionsMenu();
        });

        fab.addEventListener('mouseenter', () => {
            fab.style.transform = 'scale(1.1)';
            fab.style.boxShadow = 'var(--shadow-xl)';
        });

        fab.addEventListener('mouseleave', () => {
            fab.style.transform = 'scale(1)';
            fab.style.boxShadow = 'var(--shadow-lg)';
        });

        document.body.appendChild(fab);

        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fabEnter {
                0% { transform: scale(0) rotate(180deg); }
                100% { transform: scale(1) rotate(0deg); }
            }
        `;
        document.head.appendChild(style);
    }

    showQuickActionsMenu() {
        // Implementation for quick actions menu
        console.log('Quick actions menu triggered');
    }

    // Utility methods
    getStatusClass(status) {
        const statusMap = {
            'Chờ xác nhận': 'pending',
            'Đã xác nhận': 'confirmed',
            'Đang mua': 'buying',
            'Đã mua': 'bought',
            'Đang ship': 'shipping',
            'Đã nhận': 'delivered',
            'Hoàn thành': 'completed'
        };
        return statusMap[status] || 'default';
    }

    formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;

        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days} ngày trước`;
        if (hours > 0) return `${hours} giờ trước`;
        if (minutes > 0) return `${minutes} phút trước`;
        return 'Vừa xong';
    }

    showErrorState() {
        const dashboard = document.getElementById('dashboard');
        if (dashboard) {
            dashboard.innerHTML = `
                <div class="error-state">
                    <div class="error-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h3>Không thể tải dữ liệu dashboard</h3>
                    <p>Vui lòng kiểm tra kết nối và thử lại.</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="fas fa-refresh"></i> Thử lại
                    </button>
                </div>
            `;
        }
    }

    // Public methods for external use
    refresh() {
        return this.loadData();
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this.isInitialized = false;
    }
}

// Initialize enhanced dashboard
window.enhancedDashboard = new EnhancedDashboard();

// Auto-refresh when tab becomes visible
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.enhancedDashboard) {
        window.enhancedDashboard.refresh();
    }
});

// Expose for external use
window.refreshDashboard = () => window.enhancedDashboard?.refresh();

console.log('📊 Enhanced Dashboard module loaded');