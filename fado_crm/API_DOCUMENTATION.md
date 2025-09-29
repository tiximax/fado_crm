# 📚 FADO CRM - API Documentation
*Complete REST API Reference for FADO Vietnam Cross-Border Shopping CRM*

## 🎯 Overview

FADO CRM API is a comprehensive RESTful API built with FastAPI for managing cross-border shopping operations. It provides complete CRUD operations for customers, products, orders, and contact history management.

### 🚀 Quick Start
- **Base URL**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)
- **API Version**: v1.0.0

### 🛡️ Security Features
- Custom error handling middleware
- Request logging and tracking
- Security headers (CORS, XSS Protection, etc.)
- Request ID tracking for debugging

---

## 📋 Table of Contents
1. [Authentication](#authentication)
2. [Error Handling](#error-handling)
3. [Customer Management](#customer-management)
4. [Product Management](#product-management)
5. [Order Management](#order-management)
6. [Contact History](#contact-history)
7. [Dashboard & Statistics](#dashboard--statistics)
8. [Data Models](#data-models)
9. [Response Formats](#response-formats)
10. [Performance Monitoring](#performance-monitoring)

---

## 🔐 Authentication

*Currently the API is in development mode without authentication. In production, implement JWT-based authentication.*

**Headers Required:**
```http
Content-Type: application/json
X-Request-ID: [Optional - Auto-generated if not provided]
```

---

## ⚠️ Error Handling

The API uses consistent error response format with detailed error information:

### Error Response Format
```json
{
  "error": true,
  "error_code": "ERROR_TYPE",
  "message": "Human readable error message",
  "timestamp": "2025-09-23T10:30:00Z",
  "details": {
    "additional": "error details"
  }
}
```

### Common Error Codes
- `NOT_FOUND` - Resource not found (404)
- `VALIDATION_ERROR` - Input validation failed (422)
- `CONFLICT_ERROR` - Resource conflict (409)
- `DATABASE_ERROR` - Database operation failed (500)

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## 👥 Customer Management

### Get All Customers
```http
GET /khach-hang/
```

**Query Parameters:**
- `skip` (int, optional): Records to skip for pagination (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 1000)
- `search` (string, optional): Search by name, email, or phone
- `loai_khach` (enum, optional): Filter by customer type (`MOI`, `THAN_THIET`, `VIP`)

**Response:**
```json
[
  {
    "id": 1,
    "ho_ten": "Nguyen Van A",
    "email": "nguyenvana@email.com",
    "so_dien_thoai": "0909123456",
    "dia_chi": "123 Le Loi, Q1, HCM",
    "loai_khach": "MOI",
    "ghi_chu": "Khách hàng mới",
    "ngay_tao": "2025-09-23T10:30:00Z",
    "tong_tien_da_mua": 0.0,
    "so_don_thanh_cong": 0
  }
]
```

### Get Customer by ID
```http
GET /khach-hang/{customer_id}
```

**Path Parameters:**
- `customer_id` (int): Customer ID

### Create New Customer
```http
POST /khach-hang/
```

**Request Body:**
```json
{
  "ho_ten": "Nguyen Van A",
  "email": "nguyenvana@email.com",
  "so_dien_thoai": "0909123456",
  "dia_chi": "123 Le Loi, Q1, HCM",
  "loai_khach": "MOI",
  "ghi_chu": "Khách hàng tiềm năng"
}
```

**Validation Rules:**
- `ho_ten`: 2-100 characters, required
- `email`: Valid email format, required, unique
- `so_dien_thoai`: Max 20 characters, optional
- `loai_khach`: Enum values: `MOI`, `THAN_THIET`, `VIP`

### Update Customer
```http
PUT /khach-hang/{customer_id}
```

**Request Body:** (All fields optional)
```json
{
  "ho_ten": "Updated Name",
  "email": "updated@email.com",
  "loai_khach": "THAN_THIET"
}
```

### Auto-Update Customer Type
```http
POST /khach-hang/{customer_id}/cap-nhat-loai
```

Automatically updates customer type based on purchase history:
- `VIP`: ≥ 50,000,000 VND
- `THAN_THIET`: ≥ 10,000,000 VND
- `MOI`: < 10,000,000 VND

---

## 🛍️ Product Management

### Get All Products
```http
GET /san-pham/
```

**Query Parameters:**
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Records limit (default: 100, max: 1000)
- `search` (string): Search by name, description, or category
- `danh_muc` (string): Filter by category
- `quoc_gia` (string): Filter by country of origin
- `gia_min` (float): Minimum price filter
- `gia_max` (float): Maximum price filter
- `sort_by` (string): Sort field (`ten_san_pham`, `gia_ban`, `ngay_tao`)
- `order` (string): Sort order (`asc`, `desc`)

**Response:**
```json
[
  {
    "id": 1,
    "ten_san_pham": "iPhone 15 Pro Max",
    "link_goc": "https://apple.com/iphone-15-pro",
    "gia_goc": 1199.0,
    "gia_ban": 30000000.0,
    "mo_ta": "Latest iPhone with advanced features",
    "hinh_anh_url": "https://images.apple.com/iphone.jpg",
    "trong_luong": 0.221,
    "kich_thuoc": "159.9 x 76.7 x 8.25 mm",
    "danh_muc": "Electronics",
    "quoc_gia_nguon": "USA",
    "ngay_tao": "2025-09-23T10:30:00Z"
  }
]
```

### Get Product Count
```http
GET /san-pham-count
```

Returns total count of products matching the same filters as the list endpoint.

**Response:**
```json
{
  "total": 150
}
```

### Get Product by ID
```http
GET /san-pham/{product_id}
```

### Create New Product
```http
POST /san-pham/
```

**Request Body:**
```json
{
  "ten_san_pham": "iPhone 15 Pro Max",
  "link_goc": "https://apple.com/iphone-15-pro",
  "gia_goc": 1199.0,
  "gia_ban": 30000000.0,
  "mo_ta": "Latest iPhone with advanced features",
  "hinh_anh_url": "https://images.apple.com/iphone.jpg",
  "trong_luong": 0.221,
  "kich_thuoc": "159.9 x 76.7 x 8.25 mm",
  "danh_muc": "Electronics",
  "quoc_gia_nguon": "USA"
}
```

**Validation Rules:**
- `ten_san_pham`: 2-200 characters, required
- `gia_goc`, `gia_ban`: ≥ 0, optional
- `trong_luong`: ≥ 0, optional
- `link_goc`, `hinh_anh_url`: Max 500 characters

### Update Product
```http
PUT /san-pham/{product_id}
```

### Delete Product
```http
DELETE /san-pham/{product_id}
```

**Response:**
```json
{
  "message": "🗑️ Đã xóa sản phẩm: iPhone 15 Pro Max",
  "success": true
}
```

---

## 📋 Order Management

### Get All Orders
```http
GET /don-hang/
```

**Query Parameters:**
- `skip` (int): Pagination offset
- `limit` (int): Records limit (max: 500)
- `trang_thai` (enum): Filter by status
- `khach_hang_id` (int): Filter by customer

**Order Status Values:**
- `CHO_XAC_NHAN` - Pending confirmation
- `DA_XAC_NHAN` - Confirmed
- `DANG_MUA` - In purchasing process
- `DA_MUA` - Purchased
- `DANG_SHIP` - Shipping
- `DA_NHAN` - Delivered
- `HUY` - Cancelled

### Get Order by ID
```http
GET /don-hang/{order_id}
```

**Response:**
```json
{
  "id": 1,
  "ma_don_hang": "FD250923ABC123",
  "khach_hang_id": 1,
  "trang_thai": "CHO_XAC_NHAN",
  "tong_gia_san_pham": 1199.0,
  "phi_mua_ho": 120.0,
  "phi_van_chuyen": 50.0,
  "phi_khac": 30.0,
  "tong_tien": 1399.0,
  "ngay_tao": "2025-09-23T10:30:00Z",
  "ngay_cap_nhat": "2025-09-23T10:30:00Z",
  "ngay_giao_hang": null,
  "ghi_chu_khach": "Giao hàng nhanh",
  "ghi_chu_noi_bo": "Khách VIP",
  "ma_van_don": null,
  "khach_hang": {
    "id": 1,
    "ho_ten": "Nguyen Van A",
    "email": "nguyenvana@email.com"
  },
  "chi_tiet_list": [
    {
      "id": 1,
      "don_hang_id": 1,
      "san_pham_id": 1,
      "so_luong": 1,
      "gia_mua": 1199.0,
      "ghi_chu": "Màu đen",
      "san_pham": {
        "id": 1,
        "ten_san_pham": "iPhone 15 Pro Max"
      }
    }
  ]
}
```

### Create New Order
```http
POST /don-hang/
```

**Request Body:**
```json
{
  "khach_hang_id": 1,
  "tong_gia_san_pham": 1199.0,
  "phi_mua_ho": 120.0,
  "phi_van_chuyen": 50.0,
  "phi_khac": 30.0,
  "ngay_giao_hang": "2025-10-15T00:00:00Z",
  "ghi_chu_khach": "Giao hàng nhanh",
  "ghi_chu_noi_bo": "Khách VIP",
  "chi_tiet_list": [
    {
      "san_pham_id": 1,
      "so_luong": 1,
      "gia_mua": 1199.0,
      "ghi_chu": "Màu đen"
    }
  ]
}
```

**Business Logic:**
- Auto-generates unique order code (format: `FD{YYMMDD}{RANDOM}`)
- Auto-calculates total amount
- Validates customer and products exist
- Requires at least one product in order

### Update Order
```http
PUT /don-hang/{order_id}
```

**Request Body:** (All fields optional)
```json
{
  "trang_thai": "DA_XAC_NHAN",
  "phi_van_chuyen": 75.0,
  "ma_van_don": "VN123456789",
  "ghi_chu_noi_bo": "Updated notes"
}
```

---

## 📞 Contact History

### Get Contact History
```http
GET /lich-su-lien-he/
```

**Query Parameters:**
- `khach_hang_id` (int, optional): Filter by customer
- `skip` (int): Pagination offset
- `limit` (int): Records limit (max: 500)

### Create Contact Record
```http
POST /lich-su-lien-he/
```

**Request Body:**
```json
{
  "khach_hang_id": 1,
  "loai_lien_he": "call",
  "noi_dung": "Tư vấn sản phẩm iPhone mới",
  "nhan_vien_xu_ly": "Nguyen Van B",
  "ket_qua": "Khách hàng quan tâm, sẽ đặt hàng"
}
```

**Contact Types:**
- `call` - Phone call
- `sms` - SMS message
- `email` - Email communication

---

## 📊 Dashboard & Statistics

### Get Dashboard Statistics
```http
GET /dashboard
```

**Response:**
```json
{
  "tong_khach_hang": 1250,
  "tong_don_hang": 3450,
  "doanh_thu_thang": 2450000000.0,
  "don_cho_xu_ly": 125,
  "khach_moi_thang": 67
}
```

**Metrics Explained:**
- `tong_khach_hang`: Total registered customers
- `tong_don_hang`: Total orders in system
- `doanh_thu_thang`: Revenue for current month (excluding cancelled orders)
- `don_cho_xu_ly`: Orders pending processing (confirmed, purchasing, purchased)
- `khach_moi_thang`: New customers registered this month

---

## 🗄️ Data Models

### Customer Types (LoaiKhachHang)
```python
MOI = "Mới"           # New customer
THAN_THIET = "Thân thiết"  # Loyal customer
VIP = "VIP"          # VIP customer
```

### Order Status (TrangThaiDonHang)
```python
CHO_XAC_NHAN = "Chờ xác nhận"    # Pending confirmation
DA_XAC_NHAN = "Đã xác nhận"      # Confirmed
DANG_MUA = "Đang mua"            # In purchasing process
DA_MUA = "Đã mua"                # Purchased
DANG_SHIP = "Đang ship"          # Shipping
DA_NHAN = "Đã nhận"              # Delivered
HUY = "Hủy"                      # Cancelled
```

### Data Validation Rules

**Customer (KhachHang):**
- `ho_ten`: 2-100 characters, required
- `email`: Valid email format, unique, required
- `so_dien_thoai`: Max 20 characters, optional

**Product (SanPham):**
- `ten_san_pham`: 2-200 characters, required
- `gia_goc`, `gia_ban`: ≥ 0, optional
- `trong_luong`: ≥ 0, optional

**Order (DonHang):**
- `chi_tiet_list`: Minimum 1 item required
- All fee fields: ≥ 0
- Auto-calculates `tong_tien` = sum of all fees

---

## 📝 Response Formats

### Success Response
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  "ngay_tao": "2025-09-23T10:30:00Z"
}
```

### Error Response
```json
{
  "error": true,
  "error_code": "NOT_FOUND",
  "message": "Không tìm thấy sản phẩm",
  "timestamp": "2025-09-23T10:30:00Z",
  "details": {
    "resource": "product",
    "resource_id": 999
  }
}
```

### Message Response
```json
{
  "message": "Operation completed successfully",
  "success": true
}
```

---

## 📈 Performance Monitoring

- Base path: `/performance`
- Yêu cầu bảo mật:
  - Public: `GET /performance/health`, `GET /performance/metrics`
  - Admin: `GET /performance/database/stats`, `GET /performance/database/indexes`, `GET /performance/database/slow-queries`, `GET /performance/database/optimize`, `POST /performance/cache/clear`

### Endpoints

- GET `/performance/health`
  - Mô tả: Kiểm tra nhanh tình trạng hệ thống (DB, cache)
  - Phản hồi mẫu:
  ```json
  {
    "overall_status": "healthy",
    "services": {
      "database": { "status": "healthy", "response_time_ms": 5.12 },
      "cache": { "status": "disabled" }
    },
    "timestamp": 1695888888.123
  }
  ```

- GET `/performance/metrics`
  - Mô tả: Xuất Prometheus metrics (text/plain)
  - Lưu ý: Nếu Prometheus không khả dụng, trả về dòng thông báo dạng `# metrics unavailable: ...`

- GET `/performance/database/stats` (Admin)
  - Mô tả: Thống kê hiệu năng truy vấn, pool kết nối, cache và hệ thống
  - Phản hồi mẫu (rút gọn):
  ```json
  {
    "query_performance": {
      "dashboard_stats": { "count": 10, "avg_time": 0.02 }
    },
    "connection_pool": { "pool_size": 5, "checked_in": 5, "checked_out": 0, "overflow": 0 },
    "cache_stats": { "connected_clients": 0 },
    "system_performance": { "cpu_percent": 12.5 },
    "timestamp": 1695888888.456
  }
  ```

- GET `/performance/database/indexes` (Admin)
  - Mô tả: Danh sách index theo bảng (SQLite dùng PRAGMA index_list/index_info)
  - Phản hồi mẫu:
  ```json
  {
    "khach_hang": [
      { "name": "idx_khach_hang_search", "columns": ["ho_ten", "email"], "is_unique": false, "is_auto": false }
    ]
  }
  ```

- GET `/performance/database/slow-queries` (Admin)
  - Mô tả: Mô phỏng phát hiện truy vấn chậm (dev với SQLite); trên PostgreSQL nên dùng `pg_stat_statements`

- GET `/performance/database/optimize` (Admin)
  - Mô tả: Chạy ANALYZE, VACUUM (SQLite), integrity_check và ước lượng kích thước DB
  - Phản hồi mẫu:
  ```json
  {
    "optimization_completed": true,
    "results": {
      "analyze_time": 0.02,
      "vacuum_time": 0.10,
      "integrity_check": { "status": "ok" },
      "database_size_mb": 12.34
    },
    "timestamp": 1695888888.789
  }
  ```

- POST `/performance/cache/clear` (Admin)
  - Body (tuỳ chọn):
  ```json
  { "pattern": "customers" }
  ```
  - Mô tả: Xoá cache (toàn bộ hoặc theo pattern)

### Gợi ý triển khai Production
- Dev: SQLite; Prod: PostgreSQL + QueuePool
- Cache qua Redis: đặt `REDIS_URL`, bật `ENABLE_QUERY_CACHE=true`
- Tinh chỉnh pool: `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`
- Bật log truy vấn chậm, gắn Prometheus vào middleware/DB để theo dõi chi tiết

---

## 🚀 Development Notes

### Request/Response Logging
Every API request is logged with:
- Unique Request ID (8-character UUID)
- Execution time
- HTTP method and path
- Response status code

### Business Event Logging
Important business events are logged:
- `PRODUCT_CREATED`, `PRODUCT_DELETED`
- `API_STARTUP`
- User actions (create, view, update, delete)

### Database Features
- Automatic timestamp fields (`ngay_tao`, `ngay_cap_nhat`)
- Relational integrity (foreign key constraints)
- Optimized queries with SQLAlchemy ORM

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'`

---

## 🎯 Testing

The API includes comprehensive test coverage:
- Unit tests for all endpoints
- Integration tests for error handling
- Database transaction testing
- Concurrent request testing

Run tests:
```bash
cd backend
python -m pytest tests/ -v --cov=. --cov-report=html
```

---

## 📧 Support

For API questions or issues:
- Check interactive documentation at `/docs`
- Review test cases in `tests/` directory
- Check application logs for debugging

*Last updated: September 23, 2025*