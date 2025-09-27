// 🚀 FADO CRM JavaScript - Code siêu mạnh như Thor's hammer! ⚡
// Được viết bởi AI với tình yêu JavaScript và nhiều cafein! ☕

// 🔧 Configuration - Cấu hình API như một pro!
// Luôn đồng bộ với authService.API_BASE (mặc định http://localhost:8000)
const API_BASE_URL = (window.authService && window.authService.API_BASE) ? window.authService.API_BASE : 'http://localhost:8000';

// 🎯 Global variables - Biến toàn cục như siêu anh hùng!
let currentTab = 'dashboard';
let customersData = [];
let productsData = [];
let ordersData = [];

// 🎬 DOM Content Loaded - Khi trang web sẵn sàng!
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 FADO CRM Starting up...');

    // Wait a bit for authService to initialize, then check authentication
    setTimeout(() => {
        if (!window.authService || !window.authService.isAuthenticated()) {
            console.log('🔒 User not authenticated, redirecting to login...');
            window.location.href = 'login.html';
            return;
        }

        console.log('✅ User authenticated, proceeding with app initialization...');
        proceedWithAppInitialization();
    }, 100);
});

function proceedWithAppInitialization() {

    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js').then(() => {
            console.log('✅ Service Worker registered');
        }).catch(err => {
            console.warn('⚠️ Service Worker registration failed:', err);
        });
    }

    initializeApp();
    // Load public settings (brand name, etc.)
    loadPublicSettings();
    setupEventListeners();
    loadDashboard();
}

// 🏗️ Initialize App - Khởi tạo ứng dụng
function initializeApp() {
    console.log('🎨 Initializing FADO CRM...');

    // Display current user info
    const currentUser = window.authService.getCurrentUser();
    if (currentUser) {
        console.log(`👤 Logged in as: ${currentUser.ho_ten} (${currentUser.vai_tro})`);

        // Update any user display elements if they exist
        const userNameEl = document.getElementById('currentUserName');
        if (userNameEl) {
            userNameEl.textContent = currentUser.ho_ten;
        }
    }

    // Set active tab
    showTab('dashboard');

    // Load initial data
    checkAPIConnection();
}

// 🔌 Check API Connection - Kiểm tra kết nối API
async function checkAPIConnection() {
    try {
        showLoading(true);
        const response = await window.authService.apiCall('/');
        const data = await response.json();

        if (data.success) {
            showToast('🎉 Kết nối API thành công!', 'success');
            console.log('✅ API Connection successful:', data.message);
        }
    } catch (error) {
        console.error('❌ API Connection failed:', error);
        showToast('⚠️ Không thể kết nối tới API server!', 'error');
    } finally {
        showLoading(false);
    }
}

// 🎛️ Setup Event Listeners - Thiết lập sự kiện như một DJ!
function setupEventListeners() {
    // Tab navigation events
    document.querySelectorAll('.nav-item').forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            showTab(tabName);
        });
    });

    // Search events với debounce để tối ưu performance
    const customerSearch = document.getElementById('customer-search');
    if (customerSearch) {
        customerSearch.addEventListener('input', debounce(searchCustomers, 300));
    }

    const productSearch = document.getElementById('product-search');
    if (productSearch) {
        productSearch.addEventListener('input', debounce(searchProducts, 300));
    }

    // Filter events
    const customerTypeFilter = document.getElementById('customer-type-filter');
    if (customerTypeFilter) {
        customerTypeFilter.addEventListener('change', filterCustomers);
    }

    const orderStatusFilter = document.getElementById('order-status-filter');
    if (orderStatusFilter) {
        orderStatusFilter.addEventListener('change', filterOrders);
    }

    // Form submit events
    const addCustomerForm = document.getElementById('addCustomerForm');
    if (addCustomerForm) {
        addCustomerForm.addEventListener('submit', handleAddCustomer);
    }

    const addProductForm = document.getElementById('addProductForm');
    if (addProductForm) {
        addProductForm.addEventListener('submit', handleAddProduct);
    }

    const editProductForm = document.getElementById('editProductForm');
    if (editProductForm) {
        editProductForm.addEventListener('submit', handleEditProduct);
    }

    // Modal events
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target.id);
        }
    });

    console.log('🎛️ Event listeners setup complete!');
}

// 🔄 Debounce function - Tối ưu performance như Formula 1!
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 📋 Tab Management - Quản lý tabs như switching TV channels!
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    const selectedNavItem = document.querySelector(`[data-tab="${tabName}"]`);

    if (selectedTab && selectedNavItem) {
        selectedTab.classList.add('active');
        selectedNavItem.classList.add('active');
        currentTab = tabName;

        // Load data for specific tab
        switch(tabName) {
            case 'dashboard':
                loadDashboard();
                break;
            case 'customers':
                loadCustomers();
                break;
            case 'products':
                loadProducts();
                break;
            case 'orders':
                loadOrders();
                break;
            case 'contact-history':
                loadContactHistory();
                break;
            case 'system-settings':
                loadSystemSettings();
                break;
        }

        console.log(`📋 Switched to tab: ${tabName}`);
    }
}

// 📊 Dashboard Functions - Dashboard siêu cool!
async function loadDashboard() {
    try {
        showLoading(true);

        console.log('📊 Loading dashboard data...');

        // Check authentication first
        if (!window.authService.isAuthenticated()) {
            console.error('❌ Not authenticated for dashboard');
            showToast('⚠️ Vui lòng đăng nhập lại!', 'error');
            window.location.href = 'login.html';
            return;
        }

        // Load dashboard statistics with authentication
        const response = await window.authService.apiCall('/dashboard');

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const stats = await response.json();
        console.log('📊 Dashboard stats received:', stats);

        // Update stats cards với animation
        updateStatCard('total-customers', stats.tong_khach_hang);
        updateStatCard('total-orders', stats.tong_don_hang);
        updateStatCard('monthly-revenue', formatCurrency(stats.doanh_thu_thang));
        updateStatCard('pending-orders', stats.don_cho_xu_ly);

        // Load recent orders và new customers
        await Promise.all([
            loadRecentOrders(),
            loadNewCustomers()
        ]);

        console.log('📊 Dashboard loaded successfully!');

    } catch (error) {
        console.error('❌ Error loading dashboard:', error);
        showToast('⚠️ Lỗi khi tải dashboard!', 'error');
    } finally {
        showLoading(false);
    }
}

function updateStatCard(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        // Animation counter effect
        const startValue = parseInt(element.textContent) || 0;
        const endValue = typeof value === 'string' ? value : parseInt(value);

        if (typeof endValue === 'number') {
            animateCounter(element, startValue, endValue);
        } else {
            element.textContent = value;
        }
    }
}

function animateCounter(element, start, end, duration = 1000) {
    const increment = (end - start) / (duration / 16); // 60fps
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

async function loadRecentOrders() {
    try {
        const response = await window.authService.apiCall('/orders/?limit=5');
        const orders = await response.json();

        const container = document.getElementById('recent-orders');
        if (orders.length === 0) {
            container.innerHTML = '<div class="text-muted">📭 Chưa có đơn hàng nào!</div>';
            return;
        }

        container.innerHTML = orders.map(order => `
            <div class="contact-item">
                <div class="contact-header">
                    <strong>📋 ${order.ma_don_hang}</strong>
                    <span class="status-badge status-${order.trang_thai}">${getStatusText(order.trang_thai)}</span>
                </div>
                <div class="contact-content">
                    💰 ${formatCurrency(order.tong_tien)}
                </div>
                <div class="contact-meta">
                    <span>📅 ${formatDate(order.ngay_tao)}</span>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('❌ Error loading recent orders:', error);
        document.getElementById('recent-orders').innerHTML = '<div class="text-muted">⚠️ Lỗi khi tải đơn hàng!</div>';
    }
}

async function loadNewCustomers() {
    try {
        const response = await window.authService.apiCall('/customers/?limit=5');
        const customers = await response.json();

        const container = document.getElementById('new-customers');
        if (customers.length === 0) {
            container.innerHTML = '<div class="text-muted">👤 Chưa có khách hàng nào!</div>';
            return;
        }

        container.innerHTML = customers.map(customer => `
            <div class="contact-item">
                <div class="contact-header">
                    <strong>👤 ${customer.ho_ten}</strong>
                    <span class="status-badge status-${customer.loai_khach}">${getCustomerTypeText(customer.loai_khach)}</span>
                </div>
                <div class="contact-content">
                    📧 ${customer.email}
                </div>
                <div class="contact-meta">
                    <span>📅 ${formatDate(customer.ngay_tao)}</span>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('❌ Error loading new customers:', error);
        document.getElementById('new-customers').innerHTML = '<div class="text-muted">⚠️ Lỗi khi tải khách hàng!</div>';
    }
}

// 👥 Customer Management Functions
async function loadCustomers() {
    try {
        showLoading(true);
        const response = await window.authService.apiCall('/customers/');
        customersData = await response.json();

        displayCustomers(customersData);
        console.log('👥 Customers loaded successfully!');

    } catch (error) {
        console.error('❌ Error loading customers:', error);
        showToast('⚠️ Lỗi khi tải danh sách khách hàng!', 'error');
    } finally {
        showLoading(false);
    }
}

function displayCustomers(customers) {
    const tbody = document.getElementById('customers-tbody');

    if (customers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">📭 Chưa có khách hàng nào!</td></tr>';
        return;
    }

    tbody.innerHTML = customers.map(customer => `
        <tr class="clickable" onclick="viewCustomerDetail(${customer.id})">
            <td>${customer.id}</td>
            <td><strong>${customer.ho_ten}</strong></td>
            <td>${customer.email}</td>
            <td>${customer.so_dien_thoai || '📱 Chưa có'}</td>
            <td><span class="status-badge status-${customer.loai_khach}">${getCustomerTypeText(customer.loai_khach)}</span></td>
            <td>${formatCurrency(customer.tong_tien_da_mua)}</td>
            <td>${formatDate(customer.ngay_tao)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); editCustomer(${customer.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-warning" onclick="event.stopPropagation(); autoUpdateCustomerType(${customer.id})">
                    <i class="fas fa-magic"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

async function searchCustomers() {
    const searchTerm = document.getElementById('customer-search').value;
    const typeFilter = document.getElementById('customer-type-filter').value;

    let url = `/customers/?`;
    if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;
    if (typeFilter) url += `loai_khach=${typeFilter}&`;

    try {
        const response = await window.authService.apiCall(url);
        const customers = await response.json();
        displayCustomers(customers);
    } catch (error) {
        console.error('❌ Error searching customers:', error);
        showToast('⚠️ Lỗi khi tìm kiếm khách hàng!', 'error');
    }
}

function filterCustomers() {
    searchCustomers(); // Reuse search function with filter
}

// 📦 Product Management Functions
async function loadProducts() {
    try {
        showLoading(true);
        const response = await window.authService.apiCall('/products/');
        productsData = await response.json();

        displayProducts(productsData);
        console.log('📦 Products loaded successfully!');

    } catch (error) {
        console.error('❌ Error loading products:', error);
        showToast('⚠️ Lỗi khi tải danh sách sản phẩm!', 'error');
    } finally {
        showLoading(false);
    }
}

function displayProducts(products) {
    const container = document.getElementById('products-grid');

    if (products.length === 0) {
        container.innerHTML = '<div class="loading-card">📭 Chưa có sản phẩm nào!</div>';
        return;
    }

    container.innerHTML = products.map(product => `
        <div class="product-card">
            <div class="product-image" onclick="viewProductDetail(${product.id})">
                ${product.hinh_anh_url ?
                    `<img src="${product.hinh_anh_url}" alt="${product.ten_san_pham}" style="width:100%;height:100%;object-fit:cover;">` :
                    '📦'
                }
            </div>
            <div class="product-info">
                <div class="product-title" onclick="viewProductDetail(${product.id})">${product.ten_san_pham}</div>
                <div class="product-price">
                    ${product.gia_ban ? formatCurrency(product.gia_ban) : '💰 Liên hệ'}
                </div>
                <div class="product-meta">
                    📂 ${product.danh_muc || 'Chưa phân loại'}<br>
                    🌍 ${product.quoc_gia_nguon || 'Chưa rõ'}
                    ${product.trong_luong ? `<br>⚖️ ${product.trong_luong}kg` : ''}
                </div>
                <div class="product-actions">
                    <button class="btn btn-sm btn-primary" onclick="viewProductDetail(${product.id})" title="Xem chi tiết">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="editProduct(${product.id})" title="Chỉnh sửa">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

async function searchProducts() {
    const searchTerm = document.getElementById('product-search').value;

    let url = `/products/?`;
    if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}`;

    try {
        const response = await window.authService.apiCall(url);
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('❌ Error searching products:', error);
        showToast('⚠️ Lỗi khi tìm kiếm sản phẩm!', 'error');
    }
}

// 📋 Order Management Functions
async function loadOrders() {
    try {
        showLoading(true);
        const response = await window.authService.apiCall('/orders/');
        ordersData = await response.json();

        displayOrders(ordersData);
        console.log('📋 Orders loaded successfully!');

    } catch (error) {
        console.error('❌ Error loading orders:', error);
        showToast('⚠️ Lỗi khi tải danh sách đơn hàng!', 'error');
    } finally {
        showLoading(false);
    }
}

function displayOrders(orders) {
    const tbody = document.getElementById('orders-tbody');

    if (orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">📭 Chưa có đơn hàng nào!</td></tr>';
        return;
    }

    tbody.innerHTML = orders.map(order => `
        <tr class="clickable" onclick="viewOrderDetail(${order.id})">
            <td><strong>${order.ma_don_hang}</strong></td>
            <td>${order.khach_hang ? order.khach_hang.ho_ten : 'N/A'}</td>
            <td>${formatCurrency(order.tong_tien)}</td>
            <td><span class="status-badge status-${order.trang_thai}">${getStatusText(order.trang_thai)}</span></td>
            <td>${formatDate(order.ngay_tao)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); editOrder(${order.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-success" onclick="event.stopPropagation(); updateOrderStatus(${order.id})">
                    <i class="fas fa-arrow-up"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

async function filterOrders() {
    const statusFilter = document.getElementById('order-status-filter').value;

    let url = `${API_BASE_URL}/orders/?`;
    if (statusFilter) url += `trang_thai=${statusFilter}`;

    try {
        const response = await fetch(url);
        const orders = await response.json();
        displayOrders(orders);
    } catch (error) {
        console.error('❌ Error filtering orders:', error);
        showToast('⚠️ Lỗi khi lọc đơn hàng!', 'error');
    }
}

// 📞 Contact History Functions
async function loadContactHistory() {
    try {
        showLoading(true);
        const response = await window.authService.apiCall('/contact-history/');
        const contacts = await response.json();

        displayContactHistory(contacts);
        console.log('📞 Contact history loaded successfully!');

    } catch (error) {
        console.error('❌ Error loading contact history:', error);
        showToast('⚠️ Lỗi khi tải lịch sử liên hệ!', 'error');
    } finally {
        showLoading(false);
    }
}

function displayContactHistory(contacts) {
    const container = document.getElementById('contact-history-list');

    if (contacts.length === 0) {
        container.innerHTML = '<div class="loading-card">📞 Chưa có lịch sử liên hệ nào!</div>';
        return;
    }

    container.innerHTML = contacts.map(contact => `
        <div class="contact-item">
            <div class="contact-header">
                <div>
                    <span class="contact-type ${contact.loai_lien_he}">
                        ${getContactTypeIcon(contact.loai_lien_he)} ${contact.loai_lien_he.toUpperCase()}
                    </span>
                    <strong>👤 Khách hàng ID: ${contact.khach_hang_id}</strong>
                </div>
                <span class="text-muted">${formatDate(contact.ngay_lien_he)}</span>
            </div>
            <div class="contact-content">
                ${contact.noi_dung}
            </div>
            <div class="contact-meta">
                <span>👨‍💼 ${contact.nhan_vien_xu_ly}</span>
                ${contact.ket_qua ? `<span>✅ ${contact.ket_qua}</span>` : ''}
            </div>
        </div>
    `).join('');
}

// 🎭 Modal Management Functions
function showAddCustomerModal() {
    showModal('addCustomerModal');
}

function showAddProductModal() {
    showModal('addProductModal');
}

// 📦 Order Management Functions
async function showAddOrderModal() {
    try {
        // Load customers and products for dropdowns
        await loadCustomersAndProducts();
        showModal('addOrderModal');
        resetAddOrderForm();
    } catch (error) {
        console.error('Error showing add order modal:', error);
        showToast('❌ Lỗi khi mở modal tạo đơn hàng', 'error');
    }
}

function showAddContactModal() {
    showToast('🚧 Tính năng ghi nhận liên hệ sẽ được hoàn thiện trong phiên bản tiếp theo!', 'warning');
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scroll
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restore scroll

        // Reset form if exists
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    }
}

// 📝 Form Handlers - Xử lý form như một ninja!
async function handleAddCustomer(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const customerData = Object.fromEntries(formData.entries());

    try {
        showLoading(true);

        const response = await window.authService.apiCall('/customers/', {
            method: 'POST',
            body: JSON.stringify(customerData)
        });

        if (response.ok) {
            const newCustomer = await response.json();
            showToast('🎉 Thêm khách hàng thành công!', 'success');
            closeModal('addCustomerModal');

            // Reload customers if on customers tab
            if (currentTab === 'customers') {
                loadCustomers();
            }
        } else {
            const error = await response.json();
            showToast(`⚠️ Lỗi: ${error.detail}`, 'error');
        }

    } catch (error) {
        console.error('❌ Error adding customer:', error);
        showToast('⚠️ Lỗi khi thêm khách hàng!', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleAddProduct(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const productData = Object.fromEntries(formData.entries());

    // Convert number fields
    ['gia_goc', 'gia_ban', 'trong_luong'].forEach(field => {
        if (productData[field] && productData[field] !== '') {
            productData[field] = parseFloat(productData[field]);
        } else {
            delete productData[field]; // Remove empty fields
        }
    });

    try {
        showLoading(true);

        const response = await window.authService.apiCall('/products/', {
            method: 'POST',
            body: JSON.stringify(productData)
        });

        if (response.ok) {
            const newProduct = await response.json();
            showToast('🎉 Thêm sản phẩm thành công!', 'success');
            closeModal('addProductModal');

            // Reload products if on products tab
            if (currentTab === 'products') {
                loadProducts();
            }
        } else {
            const error = await response.json();
            showToast(`⚠️ Lỗi: ${error.detail}`, 'error');
        }

    } catch (error) {
        console.error('❌ Error adding product:', error);
        showToast('⚠️ Lỗi khi thêm sản phẩm!', 'error');
    } finally {
        showLoading(false);
    }
}

// 🔧 Action Functions - Các hành động chính
async function autoUpdateCustomerType(customerId) {
    try {
        // TODO: Implement customer type auto-update via PUT /customers/{id}
        showToast('🔄 Auto-update customer type feature needs implementation', 'info');
        return;

        /*
        showLoading(true);

        const response = await window.authService.apiCall(`/customers/${customerId}`, {
            method: 'PUT',
            body: JSON.stringify({ auto_update_type: true })
        });

        const result = await response.json();
        showToast(result.message, result.success ? 'success' : 'warning');
        */

        // Reload customers to see updated status
        if (currentTab === 'customers') {
            loadCustomers();
        }

    } catch (error) {
        console.error('❌ Error updating customer type:', error);
        showToast('⚠️ Lỗi khi cập nhật loại khách hàng!', 'error');
    } finally {
        showLoading(false);
    }
}

function viewCustomerDetail(customerId) {
    showToast(`🔍 Xem chi tiết khách hàng ID: ${customerId}`, 'info');
    // TODO: Implement detailed view modal
}

function editCustomer(customerId) {
    showToast(`✏️ Chỉnh sửa khách hàng ID: ${customerId}`, 'info');
    // TODO: Implement edit customer modal
}

async function viewProductDetail(productId) {
    try {
        showLoading(true);

        const response = await window.authService.apiCall(`/products/${productId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch product details');
        }

        const product = await response.json();

        // Populate product detail modal
        const content = `
            <div class="product-detail-grid">
                <div class="product-detail-section">
                    <h3>📋 Thông Tin Cơ Bản</h3>
                    <div class="detail-row">
                        <span class="detail-label">🏷️ Tên sản phẩm:</span>
                        <span class="detail-value">${product.ten_san_pham}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">📂 Danh mục:</span>
                        <span class="detail-value">${product.danh_muc || 'Chưa phân loại'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">🌍 Quốc gia:</span>
                        <span class="detail-value">${product.quoc_gia_nguon || 'Chưa rõ'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">📅 Ngày tạo:</span>
                        <span class="detail-value">${formatDate(product.ngay_tao)}</span>
                    </div>
                </div>

                <div class="product-detail-section">
                    <h3>💰 Thông Tin Giá</h3>
                    <div class="detail-row">
                        <span class="detail-label">💵 Giá gốc:</span>
                        <span class="detail-value">${product.gia_goc ? '$' + product.gia_goc : 'Chưa có'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">💰 Giá bán:</span>
                        <span class="detail-value">${product.gia_ban ? formatCurrency(product.gia_ban) : 'Liên hệ'}</span>
                    </div>
                </div>

                <div class="product-detail-section">
                    <h3>📏 Thông Tin Vật Lý</h3>
                    <div class="detail-row">
                        <span class="detail-label">⚖️ Trọng lượng:</span>
                        <span class="detail-value">${product.trong_luong ? product.trong_luong + ' kg' : 'Chưa có'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">📏 Kích thước:</span>
                        <span class="detail-value">${product.kich_thuoc || 'Chưa có'}</span>
                    </div>
                </div>

                ${product.mo_ta ? `
                <div class="product-detail-section">
                    <h3>📋 Mô Tả</h3>
                    <p class="product-description">${product.mo_ta}</p>
                </div>
                ` : ''}

                ${product.link_goc ? `
                <div class="product-detail-section">
                    <h3>🔗 Link Gốc</h3>
                    <a href="${product.link_goc}" target="_blank" class="external-link">
                        <i class="fas fa-external-link-alt"></i> Xem sản phẩm gốc
                    </a>
                </div>
                ` : ''}

                ${product.hinh_anh_url ? `
                <div class="product-detail-section">
                    <h3>🖼️ Hình Ảnh</h3>
                    <img src="${product.hinh_anh_url}" alt="${product.ten_san_pham}"
                         class="product-detail-image" style="max-width: 100%; border-radius: 8px;">
                </div>
                ` : ''}
            </div>
        `;

        document.getElementById('productDetailContent').innerHTML = content;

        // Store product ID for edit button
        document.getElementById('productDetailModal').setAttribute('data-product-id', productId);

        showModal('productDetailModal');

    } catch (error) {
        console.error('❌ Error loading product details:', error);
        showToast('⚠️ Lỗi khi tải chi tiết sản phẩm!', 'error');
    } finally {
        showLoading(false);
    }
}

async function viewOrderDetail(orderId) {
    try {
        showLoading(true);
        const response = await window.authService.apiCall(`/orders/${orderId}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const order = await response.json();
        displayOrderDetail(order);
        showModal('orderDetailModal');
    } catch (error) {
        console.error('Error loading order detail:', error);
        showToast('❌ Lỗi khi tải chi tiết đơn hàng', 'error');
    } finally {
        showLoading(false);
    }
}

async function editOrder(orderId) {
    try {
        showLoading(true);

        // Load order data and populate edit form
        const response = await window.authService.apiCall(`/orders/${orderId}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const order = await response.json();
        await loadCustomersAndProducts();
        populateEditOrderForm(order);
        showModal('editOrderModal');
    } catch (error) {
        console.error('Error loading order for edit:', error);
        showToast('❌ Lỗi khi tải đơn hàng để chỉnh sửa', 'error');
    } finally {
        showLoading(false);
    }
}

async function updateOrderStatus(orderId) {
    try {
        showLoading(true);

        const response = await window.authService.apiCall(`/orders/${orderId}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const order = await response.json();
        populateStatusUpdateForm(order);
        showModal('updateOrderStatusModal');
    } catch (error) {
        console.error('Error loading order for status update:', error);
        showToast('❌ Lỗi khi tải đơn hàng để cập nhật trạng thái', 'error');
    } finally {
        showLoading(false);
    }
}

// 🎨 UI Helper Functions - Các hàm tiện ích UI
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = getToastIcon(type);
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);

    console.log(`📢 Toast: ${message} (${type})`);
}

function getToastIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

// 🎯 Text Helper Functions - Format text như master!
function getStatusText(status) {
    const statusMap = {
        'cho_xac_nhan': '📋 Chờ xác nhận',
        'da_xac_nhan': '✅ Đã xác nhận',
        'dang_mua': '🛒 Đang mua',
        'da_mua': '💰 Đã mua',
        'dang_ship': '🚚 Đang ship',
        'da_nhan': '📦 Đã nhận',
        'huy': '❌ Đã hủy'
    };
    return statusMap[status] || status;
}

function getCustomerTypeText(type) {
    const typeMap = {
        'moi': '🆕 Khách mới',
        'than_thiet': '💎 Thân thiết',
        'vip': '👑 VIP',
        'blacklist': '🚫 Blacklist'
    };
    return typeMap[type] || type;
}

function getContactTypeIcon(type) {
    const iconMap = {
        'call': '📞',
        'sms': '💬',
        'email': '📧'
    };
    return iconMap[type] || '📞';
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '0₫';

    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
        minimumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    return new Intl.DateTimeFormat('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// 🎯 Console greeting - Chào mừng developer!
console.log(`
🚀 FADO.VN CRM JavaScript Loaded!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Dashboard: Thống kê realtime
👥 Customers: Quản lý khách hàng
📦 Products: Quản lý sản phẩm
📋 Orders: Quản lý đơn hàng
📞 Contact: Lịch sử liên hệ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 Built with ❤️ by AI
`);

// 🌐 Public settings loader
async function loadPublicSettings() {
    try {
        // Skip settings loading for now - endpoint not implemented
        return;
        // const resp = await fetch(`${API_BASE_URL}/settings/public`);
        // if (!resp.ok) return;
        // const data = await resp.json();
        // const appNameEl = document.getElementById('appName');
        // if (appNameEl && data.app_name) {
        //     appNameEl.textContent = data.app_name;
            document.title = `🛍️ ${data.app_name} - Quản Lý Mua Hộ Siêu Đỉnh!`;
        }
    } catch (e) {
        console.warn('Không thể tải public settings:', e);
    }
}

// 🔧 Product Edit Functions
async function editProduct(productId) {
    try {
        showLoading(true);

        const response = await window.authService.apiCall(`/products/${productId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch product details');
        }

        const product = await response.json();

        // Populate edit form with existing data
        document.getElementById('editProductId').value = product.id;
        document.getElementById('editTenSanPham').value = product.ten_san_pham || '';
        document.getElementById('editLinkGoc').value = product.link_goc || '';
        document.getElementById('editGiaGoc').value = product.gia_goc || '';
        document.getElementById('editGiaBan').value = product.gia_ban || '';
        document.getElementById('editMoTa').value = product.mo_ta || '';
        document.getElementById('editHinhAnhUrl').value = product.hinh_anh_url || '';
        document.getElementById('editTrongLuong').value = product.trong_luong || '';
        document.getElementById('editKichThuoc').value = product.kich_thuoc || '';
        document.getElementById('editDanhMuc').value = product.danh_muc || '';
        document.getElementById('editQuocGiaNguon').value = product.quoc_gia_nguon || '';

        showModal('editProductModal');

    } catch (error) {
        console.error('❌ Error loading product for edit:', error);
        showToast('⚠️ Lỗi khi tải thông tin sản phẩm!', 'error');
    } finally {
        showLoading(false);
    }
}

function editProductFromDetail() {
    const productId = document.getElementById('productDetailModal').getAttribute('data-product-id');
    closeModal('productDetailModal');
    editProduct(productId);
}

async function handleEditProduct(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const productId = formData.get('product_id');
    const productData = Object.fromEntries(formData.entries());

    // Remove product_id from update data
    delete productData.product_id;

    // Convert number fields
    ['gia_goc', 'gia_ban', 'trong_luong'].forEach(field => {
        if (productData[field] && productData[field] !== '') {
            productData[field] = parseFloat(productData[field]);
        } else {
            delete productData[field]; // Remove empty fields
        }
    });

    try {
        showLoading(true);

        const response = await window.authService.apiCall(`/products/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData)
        });

        if (response.ok) {
            const updatedProduct = await response.json();
            showToast('🎉 Cập nhật sản phẩm thành công!', 'success');
            closeModal('editProductModal');

            // Reload products if on products tab
            if (currentTab === 'products') {
                loadProducts();
            }
        } else {
            const error = await response.json();
            showToast(`⚠️ Lỗi: ${error.detail}`, 'error');
        }

    } catch (error) {
        console.error('❌ Error updating product:', error);
        showToast('⚠️ Lỗi khi cập nhật sản phẩm!', 'error');
    } finally {
        showLoading(false);
    }
}

// 📦 Order Management Helper Functions
async function loadCustomersAndProducts() {
    try {
        const [customersResponse, productsResponse] = await Promise.all([
            window.authService.apiCall('/customers/'),
            window.authService.apiCall('/products/')
        ]);

        if (customersResponse.ok && productsResponse.ok) {
            const customers = await customersResponse.json();
            const products = await productsResponse.json();

            populateCustomerDropdowns(customers);
            populateProductDropdowns(products);
        } else {
            throw new Error('Failed to load customers or products');
        }
    } catch (error) {
        console.error('Error loading customers and products:', error);
        showToast('❌ Lỗi khi tải dữ liệu khách hàng và sản phẩm', 'error');
    }
}

function populateCustomerDropdowns(customers) {
    const dropdowns = ['addKhachHangId', 'editKhachHangId'];

    dropdowns.forEach(dropdownId => {
        const dropdown = document.getElementById(dropdownId);
        if (!dropdown) return;

        // Clear existing options except first one
        dropdown.innerHTML = '<option value="">Chọn khách hàng...</option>';

        customers.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer.id;
            option.textContent = `${customer.ho_ten} - ${customer.email}`;
            dropdown.appendChild(option);
        });
    });
}

function populateProductDropdowns(products) {
    const container = document.querySelector('.order-items-container');
    if (!container) return;

    const productSelects = container.querySelectorAll('select[name^="san_pham_id"]');

    productSelects.forEach(select => {
        // Clear existing options except first one
        select.innerHTML = '<option value="">Chọn sản phẩm...</option>';

        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.setAttribute('data-price', product.gia_goc || 0);
            option.textContent = `${product.ten_san_pham} - $${product.gia_goc || 0}`;
            select.appendChild(option);
        });
    });
}

function resetAddOrderForm() {
    const form = document.getElementById('add-order-form');
    if (!form) return;

    form.reset();

    // Reset order items to just one item
    const container = document.querySelector('.order-items-container');
    if (container) {
        const firstItem = container.querySelector('.order-item');
        container.innerHTML = '';
        if (firstItem) {
            firstItem.querySelector('button').disabled = true; // Disable remove button for first item
            container.appendChild(firstItem);
        }
    }

    calculateOrderTotal();
}

function updateProductPrice(itemIndex) {
    const select = document.querySelector(`select[name="san_pham_id_${itemIndex}"]`);
    const priceInput = document.querySelector(`input[name="gia_mua_${itemIndex}"]`);

    if (select && priceInput) {
        const selectedOption = select.options[select.selectedIndex];
        const price = selectedOption.getAttribute('data-price') || 0;
        priceInput.value = parseFloat(price).toFixed(2);
        calculateOrderTotal();
    }
}

let orderItemIndex = 0;

function addOrderItem() {
    orderItemIndex++;
    const container = document.querySelector('.order-items-container');

    const newItem = document.createElement('div');
    newItem.className = 'order-item';
    newItem.setAttribute('data-item-index', orderItemIndex);

    newItem.innerHTML = `
        <div class="form-row">
            <div class="form-group flex-2">
                <label>🛍️ Sản Phẩm *</label>
                <select name="san_pham_id_${orderItemIndex}" required onchange="updateProductPrice(${orderItemIndex})">
                    <option value="">Chọn sản phẩm...</option>
                </select>
            </div>
            <div class="form-group">
                <label>💰 Giá (USD)</label>
                <input type="number" name="gia_mua_${orderItemIndex}" step="0.01" min="0" readonly>
            </div>
            <div class="form-group">
                <label>📦 Số Lượng *</label>
                <input type="number" name="so_luong_${orderItemIndex}" min="1" value="1" required onchange="calculateOrderTotal()">
            </div>
            <div class="form-group">
                <button type="button" class="btn btn-danger btn-sm" onclick="removeOrderItem(${orderItemIndex})">🗑️</button>
            </div>
        </div>
    `;

    container.appendChild(newItem);

    // Populate product dropdown for new item
    populateProductDropdownsForNewItem(newItem);

    // Enable remove button for first item if more than one item
    updateRemoveButtonStates();
}

function removeOrderItem(itemIndex) {
    const item = document.querySelector(`[data-item-index="${itemIndex}"]`);
    if (item) {
        item.remove();
        calculateOrderTotal();
        updateRemoveButtonStates();
    }
}

function updateRemoveButtonStates() {
    const items = document.querySelectorAll('.order-items-container .order-item');
    items.forEach((item, index) => {
        const removeButton = item.querySelector('.btn-danger');
        if (removeButton) {
            removeButton.disabled = items.length === 1;
        }
    });
}

function populateProductDropdownsForNewItem(itemElement) {
    const select = itemElement.querySelector('select[name^="san_pham_id"]');
    if (!select) return;

    // Copy options from first dropdown
    const firstSelect = document.querySelector('select[name^="san_pham_id"]');
    if (firstSelect) {
        select.innerHTML = firstSelect.innerHTML;
    }
}

function calculateOrderTotal() {
    const items = document.querySelectorAll('.order-items-container .order-item');
    let total = 0;

    items.forEach(item => {
        const priceInput = item.querySelector('input[name^="gia_mua_"]');
        const quantityInput = item.querySelector('input[name^="so_luong_"]');

        if (priceInput && quantityInput) {
            const price = parseFloat(priceInput.value) || 0;
            const quantity = parseInt(quantityInput.value) || 0;
            total += price * quantity;
        }
    });

    const totalElement = document.getElementById('orderTotalAmount');
    if (totalElement) {
        totalElement.textContent = total.toFixed(2);
    }
}

async function handleAddOrder(event) {
    event.preventDefault();

    try {
        showLoading(true);

        const formData = new FormData(event.target);
        const orderData = {
            khach_hang_id: parseInt(formData.get('khach_hang_id')),
            trang_thai: formData.get('trang_thai') || 'cho_xac_nhan',
            ghi_chu: formData.get('ghi_chu') || '',
            chi_tiet_don_hang: []
        };

        // Collect order items
        const items = document.querySelectorAll('.order-items-container .order-item');
        items.forEach(item => {
            const itemIndex = item.getAttribute('data-item-index') || '0';
            const sanPhamId = formData.get(`san_pham_id_${itemIndex}`);
            const giaMua = formData.get(`gia_mua_${itemIndex}`);
            const soLuong = formData.get(`so_luong_${itemIndex}`);

            if (sanPhamId && soLuong) {
                orderData.chi_tiet_don_hang.push({
                    san_pham_id: parseInt(sanPhamId),
                    gia_mua: parseFloat(giaMua) || 0,
                    so_luong: parseInt(soLuong)
                });
            }
        });

        if (orderData.chi_tiet_don_hang.length === 0) {
            showToast('❌ Vui lòng thêm ít nhất một sản phẩm vào đơn hàng', 'error');
            return;
        }

        const response = await window.authService.apiCall('/orders/', {
            method: 'POST',
            body: JSON.stringify(orderData)
        });

        if (response.ok) {
            showToast('🎉 Tạo đơn hàng thành công!', 'success');
            closeModal('addOrderModal');

            if (currentTab === 'orders') {
                loadOrders();
            }
        } else {
            const error = await response.json();
            showToast(`❌ Lỗi: ${error.message || error.detail}`, 'error');
        }

    } catch (error) {
        console.error('Error creating order:', error);
        showToast('❌ Lỗi khi tạo đơn hàng', 'error');
    } finally {
        showLoading(false);
    }
}

function displayOrderDetail(order) {
    const content = document.getElementById('orderDetailContent');
    const statusClass = `status-${order.trang_thai}`;

    // Store order ID for actions
    document.getElementById('orderDetailModal').setAttribute('data-order-id', order.id);

    content.innerHTML = `
        <div class="order-detail-grid">
            <div class="order-detail-section">
                <h3>📋 Thông Tin Đơn Hàng</h3>
                <div class="detail-row">
                    <span class="detail-label">Mã Đơn:</span>
                    <span class="detail-value">#${order.id}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Khách Hàng:</span>
                    <span class="detail-value">${order.khach_hang?.ho_ten || 'N/A'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">${order.khach_hang?.email || 'N/A'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Số Điện Thoại:</span>
                    <span class="detail-value">${order.khach_hang?.so_dien_thoai || 'N/A'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Trạng Thái:</span>
                    <span class="detail-value">
                        <span class="order-status-badge ${statusClass}">
                            ${getStatusIcon(order.trang_thai)} ${getStatusText(order.trang_thai)}
                        </span>
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Ngày Tạo:</span>
                    <span class="detail-value">${formatDate(order.ngay_tao)}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Ghi Chú:</span>
                    <span class="detail-value">${order.ghi_chu || 'Không có'}</span>
                </div>
            </div>

            <div class="order-detail-section">
                <h3>💰 Thông Tin Thanh Toán</h3>
                <div class="detail-row">
                    <span class="detail-label">Tổng Tiền:</span>
                    <span class="detail-value"><strong>$${order.tong_tien.toFixed(2)}</strong></span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Tiền VND:</span>
                    <span class="detail-value">${formatCurrency(order.tong_tien * 24000)}</span>
                </div>
            </div>
        </div>

        <div class="order-detail-section">
            <h3>🛍️ Chi Tiết Sản Phẩm</h3>
            <div class="order-items-list">
                ${order.chi_tiet_don_hang.map(item => `
                    <div class="order-item-row">
                        <div class="item-name">${item.san_pham?.ten_san_pham || 'Sản phẩm không xác định'}</div>
                        <div class="item-price">$${item.gia_mua.toFixed(2)}</div>
                        <div class="item-quantity">x${item.so_luong}</div>
                        <div class="item-subtotal">$${(item.gia_mua * item.so_luong).toFixed(2)}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function populateEditOrderForm(order) {
    document.getElementById('editOrderId').value = order.id;
    document.getElementById('editKhachHangId').value = order.khach_hang_id;
    document.getElementById('editTrangThai').value = order.trang_thai;
    document.getElementById('editGhiChu').value = order.ghi_chu || '';

    // Populate order items
    const container = document.getElementById('editOrderItemsContainer');
    container.innerHTML = order.chi_tiet_don_hang.map(item => `
        <div class="order-item">
            <div class="detail-row">
                <span class="detail-label">Sản phẩm:</span>
                <span class="detail-value">${item.san_pham?.ten_san_pham || 'N/A'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Giá:</span>
                <span class="detail-value">$${item.gia_mua.toFixed(2)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Số lượng:</span>
                <span class="detail-value">${item.so_luong}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Thành tiền:</span>
                <span class="detail-value"><strong>$${(item.gia_mua * item.so_luong).toFixed(2)}</strong></span>
            </div>
        </div>
    `).join('');

    // Update total
    document.getElementById('editOrderTotalAmount').textContent = order.tong_tien.toFixed(2);
}

function populateStatusUpdateForm(order) {
    document.getElementById('statusOrderId').value = order.id;
    document.getElementById('currentOrderStatus').innerHTML = `
        <span class="order-status-badge status-${order.trang_thai}">
            ${getStatusIcon(order.trang_thai)} ${getStatusText(order.trang_thai)}
        </span>
    `;
}

async function handleEditOrder(event) {
    event.preventDefault();

    try {
        showLoading(true);

        const formData = new FormData(event.target);
        const orderId = formData.get('order_id');
        const orderData = {
            trang_thai: formData.get('trang_thai'),
            ghi_chu: formData.get('ghi_chu')
        };

        const response = await window.authService.apiCall(`/orders/${orderId}`, {
            method: 'PUT',
            body: JSON.stringify(orderData)
        });

        if (response.ok) {
            showToast('🎉 Cập nhật đơn hàng thành công!', 'success');
            closeModal('editOrderModal');

            if (currentTab === 'orders') {
                loadOrders();
            }
        } else {
            const error = await response.json();
            showToast(`❌ Lỗi: ${error.message || error.detail}`, 'error');
        }

    } catch (error) {
        console.error('Error updating order:', error);
        showToast('❌ Lỗi khi cập nhật đơn hàng', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleUpdateOrderStatus(event) {
    event.preventDefault();

    try {
        showLoading(true);

        const formData = new FormData(event.target);
        const orderId = formData.get('order_id');
        const statusData = {
            trang_thai: formData.get('trang_thai'),
            ghi_chu: formData.get('ghi_chu')
        };

        const response = await window.authService.apiCall(`/orders/${orderId}/status?new_status=${statusData.trang_thai}`, {
            method: 'PUT'
        });

        if (response.ok) {
            showToast('🎉 Cập nhật trạng thái thành công!', 'success');
            closeModal('updateOrderStatusModal');

            if (currentTab === 'orders') {
                loadOrders();
            }
        } else {
            const error = await response.json();
            showToast(`❌ Lỗi: ${error.message || error.detail}`, 'error');
        }

    } catch (error) {
        console.error('Error updating order status:', error);
        showToast('❌ Lỗi khi cập nhật trạng thái', 'error');
    } finally {
        showLoading(false);
    }
}

function editOrderFromDetail() {
    const orderId = document.getElementById('orderDetailModal').getAttribute('data-order-id');
    closeModal('orderDetailModal');
    editOrder(orderId);
}

function updateOrderStatusFromDetail() {
    const orderId = document.getElementById('orderDetailModal').getAttribute('data-order-id');
    closeModal('orderDetailModal');
    updateOrderStatus(orderId);
}

function getStatusIcon(status) {
    const icons = {
        'cho_xac_nhan': '📋',
        'da_xac_nhan': '✅',
        'dang_mua': '🛒',
        'da_mua': '💰',
        'dang_ship': '🚚',
        'da_nhan': '📦',
        'huy': '❌'
    };
    return icons[status] || '❓';
}

function getStatusText(status) {
    const texts = {
        'cho_xac_nhan': 'Chờ xác nhận',
        'da_xac_nhan': 'Đã xác nhận',
        'dang_mua': 'Đang mua',
        'da_mua': 'Đã mua',
        'dang_ship': 'Đang ship',
        'da_nhan': 'Đã nhận',
        'huy': 'Đã hủy'
    };
    return texts[status] || 'Không xác định';
}

// 🛠️ System Settings (Admin only)
async function loadSystemSettings() {
    try {
        if (!hasRole('admin')) {
            showToast('Bạn cần quyền admin để truy cập cấu hình', 'warning');
            return;
        }
        showLoading(true);
        const resp = await window.authService.apiCall('/admin/system-settings');
        if (!resp.ok) {
            const err = await resp.text();
            showToast(`⚠️ Lỗi tải cấu hình: ${err}`, 'error');
            return;
        }
        const settings = await resp.json();
        renderSystemSettings(settings);
    } catch (e) {
        console.error('Error loading system settings:', e);
        showToast('⚠️ Lỗi khi tải cấu hình hệ thống', 'error');
    } finally {
        showLoading(false);
    }
}

function renderSystemSettings(settings) {
    const tbody = document.getElementById('settings-table-body');
    if (!tbody) return;

    if (!settings || settings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">📭 Chưa có cấu hình nào!</td></tr>';
        return;
    }

    tbody.innerHTML = settings.map(s => `
        <tr>
            <td><code>${s.key}</code></td>
            <td>
                <input type="text" id="setting-value-${s.key}" value="${(s.value ?? '').toString().replace(/"/g,'&quot;')}">
            </td>
            <td>
                <input type="text" id="setting-desc-${s.key}" value="${(s.description ?? '').toString().replace(/"/g,'&quot;')}">
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="saveSetting('${s.key}')">
                    <i class="fas fa-save"></i> Lưu
                </button>
            </td>
        </tr>
    `).join('');
}

async function saveSetting(key) {
    try {
        if (!hasRole('admin')) {
            showToast('Bạn cần quyền admin', 'warning');
            return;
        }
        const valueEl = document.getElementById(`setting-value-${key}`);
        const descEl = document.getElementById(`setting-desc-${key}`);
        const payload = {
            value: valueEl ? valueEl.value : '',
            description: descEl ? descEl.value : null
        };
        const resp = await window.authService.apiCall(`/admin/system-settings/${encodeURIComponent(key)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (resp.ok) {
            showToast('✅ Đã lưu cấu hình', 'success');
            await loadSystemSettings();
        } else {
            const err = await resp.text();
            showToast(`❌ Lỗi lưu cấu hình: ${err}`, 'error');
        }
    } catch (e) {
        console.error('Error saving setting:', e);
        showToast('❌ Lỗi khi lưu cấu hình', 'error');
    }
}

async function createSetting(event) {
    event.preventDefault();
    try {
        if (!hasRole('admin')) {
            showToast('Bạn cần quyền admin', 'warning');
            return;
        }
        const key = document.getElementById('settingKey').value.trim();
        const value = document.getElementById('settingValue').value;
        const description = document.getElementById('settingDescription').value;
        if (!key) {
            showToast('Vui lòng nhập key', 'warning');
            return;
        }
        const resp = await window.authService.apiCall(`/admin/system-settings/${encodeURIComponent(key)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value, description })
        });
        if (resp.ok) {
            showToast('✅ Đã thêm/cập nhật cấu hình', 'success');
            document.getElementById('addSettingForm').reset();
            await loadSystemSettings();
        } else {
            const err = await resp.text();
            showToast(`❌ Lỗi: ${err}`, 'error');
        }
    } catch (e) {
        console.error('Error creating setting:', e);
        showToast('❌ Lỗi khi tạo/cập nhật cấu hình', 'error');
    }
}

// 🗑️ Delete Product Function
async function deleteProduct(productId) {
    if (!confirm('⚠️ Bạn có chắc chắn muốn xóa sản phẩm này?\nViệc này sẽ thực hiện soft delete (ẩn sản phẩm).')) {
        return;
    }

    try {
        showLoading(true);

        const response = await window.authService.apiCall(`/products/${productId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            showToast('🎉 Xóa sản phẩm thành công!', 'success');

            // Reload products if on products tab
            if (currentTab === 'products') {
                loadProducts();
            }
        } else {
            const error = await response.json();
            showToast(`⚠️ Lỗi: ${error.detail || error.message}`, 'error');
        }

    } catch (error) {
        console.error('❌ Error deleting product:', error);
        showToast('⚠️ Lỗi khi xóa sản phẩm!', 'error');
    } finally {
        showLoading(false);
    }
}

// 🗑️ Delete Customer Function
async function deleteCustomer(customerId) {
    if (!confirm('⚠️ Bạn có chắc chắn muốn xóa khách hàng này?\nTất cả đơn hàng liên quan sẽ bị ảnh hưởng!')) {
        return;
    }

    try {
        showLoading(true);

        const response = await window.authService.apiCall(`/customers/${customerId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            showToast('🎉 Xóa khách hàng thành công!', 'success');

            // Reload customers if on customers tab
            if (currentTab === 'customers') {
                loadCustomers();
            }
        } else {
            const error = await response.json();
            showToast(`⚠️ Lỗi: ${error.detail || error.message}`, 'error');
        }

    } catch (error) {
        console.error('❌ Error deleting customer:', error);
        showToast('⚠️ Lỗi khi xóa khách hàng!', 'error');
    } finally {
        showLoading(false);
    }
}

// 🗑️ Delete Order Function
async function deleteOrder(orderId) {
    if (!confirm('⚠️ Bạn có chắc chắn muốn xóa đơn hàng này?\nViệc này không thể hoàn tác!')) {
        return;
    }

    try {
        showLoading(true);

        const response = await window.authService.apiCall(`/orders/${orderId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('🎉 Xóa đơn hàng thành công!', 'success');

            // Reload orders if on orders tab
            if (currentTab === 'orders') {
                loadOrders();
            }
        } else {
            const error = await response.json();
            showToast(`⚠️ Lỗi: ${error.detail || error.message}`, 'error');
        }

    } catch (error) {
        console.error('❌ Error deleting order:', error);
        showToast('⚠️ Lỗi khi xóa đơn hàng!', 'error');
    } finally {
        showLoading(false);
    }
}

// 💻 Enhanced Product Grid Rendering with CRUD Actions
function renderProductGrid(products) {
    const productsGrid = document.getElementById('products-grid');

    if (!products || products.length === 0) {
        productsGrid.innerHTML = '<div class="empty-state">📦 Chưa có sản phẩm nào được thêm!</div>';
        return;
    }

    productsGrid.innerHTML = products.map(product => `
        <div class="product-card" data-product-id="${product.id}">
            <div class="product-image">
                <img src="${product.hinh_anh_url || 'https://via.placeholder.com/200x200?text=No+Image'}"
                     alt="${product.ten_san_pham}" onerror="this.src='https://via.placeholder.com/200x200?text=No+Image'">
            </div>
            <div class="product-content">
                <h3 class="product-name">${product.ten_san_pham}</h3>
                <div class="product-price">
                    <span class="original-price">💵 $${product.gia_goc || 0}</span>
                    <span class="sell-price">💰 ${formatCurrency(product.gia_ban || 0)}</span>
                </div>
                <div class="product-meta">
                    <span class="category">📂 ${product.danh_muc || 'N/A'}</span>
                    <span class="country">🌍 ${product.quoc_gia_nguon || 'N/A'}</span>
                </div>
                <div class="product-actions">
                    <button class="btn btn-sm btn-info" onclick="viewProductDetail(${product.id})" title="Xem chi tiết">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="editProduct(${product.id})" title="Chỉnh sửa">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})" title="Xóa">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// 📋 Enhanced Customer Table Rendering with CRUD Actions
function renderCustomerTable(customers) {
    const tbody = document.getElementById('customers-tbody');

    if (!customers || customers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">👥 Chưa có khách hàng nào!</td></tr>';
        return;
    }

    tbody.innerHTML = customers.map(customer => `
        <tr data-customer-id="${customer.id}">
            <td>${customer.id}</td>
            <td>${customer.ho_ten}</td>
            <td>${customer.email}</td>
            <td>${customer.so_dien_thoai || 'N/A'}</td>
            <td><span class="customer-type-badge ${customer.loai_khach}">${getCustomerTypeText(customer.loai_khach)}</span></td>
            <td>${formatCurrency(customer.tong_tien_da_mua || 0)}</td>
            <td>${formatDate(customer.ngay_tao)}</td>
            <td class="actions">
                <button class="btn btn-sm btn-info" onclick="viewCustomerDetail(${customer.id})" title="Xem chi tiết">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-primary" onclick="editCustomer(${customer.id})" title="Chỉnh sửa">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteCustomer(${customer.id})" title="Xóa">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// 📋 Enhanced Order Table Rendering with CRUD Actions
function renderOrderTable(orders) {
    const tbody = document.getElementById('orders-tbody');

    if (!orders || orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">📋 Chưa có đơn hàng nào!</td></tr>';
        return;
    }

    tbody.innerHTML = orders.map(order => `
        <tr data-order-id="${order.id}">
            <td><strong>${order.ma_don_hang}</strong></td>
            <td>${order.khach_hang?.ho_ten || 'N/A'}</td>
            <td><strong>$${order.tong_tien.toFixed(2)}</strong></td>
            <td>
                <span class="order-status-badge status-${order.trang_thai}">
                    ${getStatusIcon(order.trang_thai)} ${getStatusText(order.trang_thai)}
                </span>
            </td>
            <td>${formatDate(order.ngay_tao)}</td>
            <td class="actions">
                <button class="btn btn-sm btn-info" onclick="viewOrderDetail(${order.id})" title="Xem chi tiết">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-primary" onclick="editOrder(${order.id})" title="Chỉnh sửa">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-warning" onclick="updateOrderStatus(${order.id})" title="Cập nhật trạng thái">
                    <i class="fas fa-clipboard-check"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteOrder(${order.id})" title="Xóa">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function getCustomerTypeText(type) {
    const types = {
        'moi': '🆕 Khách mới',
        'than_thiet': '💎 Thân thiết',
        'vip': '👑 VIP',
        'blacklist': '🚫 Blacklist'
    };
    return types[type] || type;
}

// 🚀 JavaScript magic hoàn thành!
// Giờ có thể tương tác với CRM như một siêu anh hùng! ⚡
