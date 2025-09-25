# 🚀 FADO CRM - QUICK START GUIDE

Hệ thống CRM cho ngành mua hộ - Được tạo bởi AI với tình yêu Việt Nam! 💖

## ⚡ Khởi Chạy Nhanh (Quick Start)

### 1. Cài Đặt Dependencies

```bash
cd fado_crm
python -m pip install fastapi uvicorn sqlalchemy pydantic
```

### 2. Tạo Demo Data

```bash
cd backend
python simple_demo.py
```

### 3. Khởi Động Server

**Cách 1: Test Server (Đơn giản)**
```bash
cd backend
python test_server.py
```

**Cách 2: Full Server (Đầy đủ tính năng)**
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Mở Frontend

Mở file `frontend/index.html` trong trình duyệt

### 5. Test API

- **API Documentation**: http://127.0.0.1:8000/docs
- **Root Endpoint**: http://127.0.0.1:8000/
- **Dashboard**: http://127.0.0.1:8000/dashboard

## 📋 Cấu Trúc Dự Án

```
fado_crm/
├── backend/              # FastAPI Backend
│   ├── main.py          # API chính
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database connection
│   ├── simple_demo.py   # Tạo demo data
│   └── test_server.py   # Test server
├── frontend/            # Web Interface
│   ├── index.html       # Giao diện chính
│   ├── style.css        # CSS styles
│   └── script.js        # JavaScript
└── README.md           # Documentation đầy đủ
```

## 🎯 Tính Năng Chính

### 👥 Quản Lý Khách Hàng
- Thêm, sửa, xóa khách hàng
- Phân loại: Mới, Thân thiết, VIP
- Tìm kiếm và lọc
- Tự động cập nhật loại khách

### 📦 Quản Lý Sản Phẩm
- Catalog sản phẩm với hình ảnh
- Quản lý giá gốc/giá bán
- Phân loại danh mục
- Link sản phẩm gốc

### 📋 Quản Lý Đơn Hàng
- 7 trạng thái đơn hàng
- Tính toán chi phí chi tiết
- Mã đơn hàng tự động
- Theo dõi tiến trình

### 📊 Dashboard Thống Kê
- Thống kê realtime
- Doanh thu tháng
- Đơn chờ xử lý
- Khách hàng mới

### 📞 Lịch Sử Liên Hệ
- Ghi nhận tương tác
- Nhiều kênh: Call, SMS, Email
- Theo dõi nhân viên xử lý

## 🔧 API Endpoints

### Dashboard
- `GET /` - Welcome message
- `GET /dashboard` - Thống kê tổng quan

### Khách Hàng
- `GET /khach-hang/` - Danh sách khách hàng
- `POST /khach-hang/` - Thêm khách hàng
- `GET /khach-hang/{id}` - Chi tiết khách hàng
- `PUT /khach-hang/{id}` - Cập nhật khách hàng

### Sản Phẩm
- `GET /san-pham/` - Danh sách sản phẩm
- `POST /san-pham/` - Thêm sản phẩm

### Đơn Hàng
- `GET /don-hang/` - Danh sách đơn hàng
- `POST /don-hang/` - Tạo đơn hàng
- `PUT /don-hang/{id}` - Cập nhật đơn hàng

### Lịch Sử Liên Hệ
- `GET /lich-su-lien-he/` - Danh sách liên hệ
- `POST /lich-su-lien-he/` - Ghi nhận liên hệ

## 🛠️ Troubleshooting

### Lỗi Unicode (Windows)
Nếu gặp lỗi Unicode, chạy:
```bash
chcp 65001
```

### Lỗi Module Not Found
Cài đặt dependencies:
```bash
python -m pip install fastapi uvicorn sqlalchemy pydantic
```

### Server Không Chạy
Thử test server trước:
```bash
python test_server.py
```

### Database Lỗi
Reset database:
```bash
del fado_crm.db  # Windows
rm fado_crm.db   # Linux/Mac
python simple_demo.py
```

## 🎮 Demo Data

Demo data bao gồm:
- 3 khách hàng mẫu
- 3 sản phẩm (iPhone, Nike, MacBook)
- 5 đơn hàng với các trạng thái khác nhau
- 10 lịch sử liên hệ

## 🚀 Next Steps

1. **Production Setup**:
   - Thêm authentication
   - Sử dụng PostgreSQL
   - Setup HTTPS
   - Environment variables

2. **Features Enhancement**:
   - Email notifications
   - Export Excel
   - Advanced reporting
   - Mobile responsive

3. **Integration**:
   - Payment gateways
   - Shipping APIs
   - WhatsApp/Telegram bot

## 📞 Hỗ Trợ

- **Issues**: Tạo issue trên GitHub
- **Documentation**: Xem README.md chi tiết
- **API Docs**: http://127.0.0.1:8000/docs

---

**🎉 Chúc bạn code vui vẻ với FADO CRM! 🛍️**

Built with ❤️ by AI và tinh thần Việt Nam 🇻🇳