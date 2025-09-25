# 🛍️ FADO.VN CRM - Hệ Thống Quản Lý Khách Hàng Mua Hộ

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://sqlalchemy.org)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com)

> 🚀 **Hệ thống CRM chuyên nghiệp dành cho ngành mua hộ, được xây dựng với công nghệ hiện đại và tình yêu Việt Nam!**

## 🌟 Tính Năng Chính

### 📊 **Dashboard Thống Kê**
- Thống kê realtime về khách hàng, đơn hàng, doanh thu
- Biểu đồ trực quan và dễ hiểu
- Theo dõi KPI quan trọng

### 👥 **Quản Lý Khách Hàng**
- Thêm, sửa, xóa thông tin khách hàng
- Phân loại khách hàng (Mới, Thân thiết, VIP)
- Tìm kiếm và lọc nhanh chóng
- Tự động cập nhật loại khách dựa trên lịch sử mua hàng

### 📦 **Quản Lý Sản Phẩm**
- Catalog sản phẩm với hình ảnh
- Quản lý giá gốc và giá bán
- Phân loại theo danh mục và xuất xứ
- Tracking link gốc từ shop nước ngoài

### 📋 **Quản Lý Đơn Hàng**
- Theo dõi đầy đủ quy trình mua hộ
- 7 trạng thái: Chờ xác nhận → Đã xác nhận → Đang mua → Đã mua → Đang ship → Đã nhận → Hoàn thành
- Tính toán chi phí chi tiết (phí mua hộ, vận chuyển, phụ phí)
- Mã đơn hàng tự động và unique

### 📞 **Lịch Sử Liên Hệ**
- Ghi nhận mọi cuộc tương tác với khách hàng
- Hỗ trợ nhiều kênh: Điện thoại, SMS, Email
- Theo dõi nhân viên xử lý và kết quả

## 🏗️ Kiến Trúc Hệ Thống

```
📁 fado_crm/
├── 🖥️ backend/              # API Backend (FastAPI)
│   ├── main.py              # 🚀 API endpoints
│   ├── models.py            # 🗄️ Database models
│   ├── schemas.py           # 📋 Pydantic schemas
│   ├── database.py          # 🔌 Database connection
│   ├── exceptions.py        # ⚠️ Custom exceptions
│   ├── middleware.py        # 🛡️ Security & logging middleware
│   ├── logging_config.py    # 📝 Logging configuration
│   ├── requirements.txt     # 📦 Dependencies
│   ├── requirements-test.txt # 🧪 Testing dependencies
│   ├── pytest.ini          # ⚙️ Test configuration
│   └── tests/               # 🧪 Comprehensive test suite
│       ├── conftest.py      # 🔧 Test fixtures
│       ├── unit/            # 🎯 Unit tests
│       └── integration/     # 🔗 Integration tests
├── 🌐 frontend/             # Web Interface
│   ├── index.html           # 📄 Main page
│   ├── style.css            # 🎨 Styles
│   └── script.js            # ⚡ JavaScript logic
├── 📚 docs/                 # 📖 Comprehensive Documentation
│   ├── API_DOCUMENTATION.md    # 🔌 Complete API reference
│   ├── DEVELOPMENT_GUIDE.md    # 🛠️ Developer guide
│   └── CODE_STANDARDS.md       # 📐 Coding standards
├── 🚀 run_server.py         # Server launcher
└── 📚 README.md             # Project overview
```

## 🔧 Công Nghệ Sử Dụng

### Backend 🖥️
- **FastAPI**: Framework API hiện đại và nhanh
- **SQLAlchemy**: ORM mạnh mẽ cho Python
- **Pydantic**: Validation dữ liệu chặt chẽ
- **SQLite/PostgreSQL**: Database linh hoạt
- **Uvicorn**: ASGI server hiệu năng cao
- **Pytest**: Testing framework với coverage

### Frontend 🌐
- **HTML5**: Cấu trúc trang web semantic
- **CSS3**: Thiết kế responsive và đẹp mắt
- **Vanilla JavaScript**: Logic tương tác mượt mà
- **Bootstrap 5**: UI components hiện đại

### Development & Quality 🛠️
- **Comprehensive Testing**: Unit & integration tests
- **API Documentation**: Complete REST API reference
- **Code Standards**: Professional development guidelines
- **Error Handling**: Robust error tracking & logging
- **Request Middleware**: Security headers & logging

## 📚 Comprehensive Documentation

Hệ thống có bộ tài liệu đầy đủ và chuyên nghiệp cho developers:

### 🔌 API Documentation
**File: [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md)**
- Complete REST API reference với tất cả endpoints
- Request/Response examples với data models
- Error handling và status codes
- Authentication guidelines (future)
- Testing với Swagger UI tại `/docs`

### 🛠️ Development Guide
**File: [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md)**
- Hướng dẫn setup development environment
- Project architecture và technology stack
- Database management và relationships
- Testing guidelines với pytest
- Frontend development patterns
- Deployment instructions
- Troubleshooting common issues

### 📐 Code Standards
**File: [`CODE_STANDARDS.md`](CODE_STANDARDS.md)**
- Python/FastAPI coding standards (PEP 8 compliant)
- JavaScript/Frontend best practices
- Database design guidelines
- API design conventions
- Testing standards và coverage requirements
- Git workflow và commit conventions
- Code review guidelines

### 🧪 Testing Suite
**Location: `backend/tests/`**
- **Unit Tests**: API endpoints, models, schemas
- **Integration Tests**: Error handling, middleware, logging
- **Test Coverage**: 85%+ với detailed reporting
- **Fixtures**: Comprehensive test data setup
- **Run Command**: `python -m pytest tests/ -v --cov=.`

### 🚀 Quick Links
- **API Docs (Interactive)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Test Coverage Report**: `backend/htmlcov/index.html`
- **Application Logs**: `backend/logs/`

## 🚀 Cài Đặt và Chạy

### ☁️ Cấu Hình Storage (Local/S3/MinIO)

Hệ thống hỗ trợ storage pluggable qua biến môi trường, cho phép chuyển đổi linh hoạt giữa lưu cục bộ (local) và object storage (S3/MinIO).

- Driver mặc định (dev): local
- File cấu hình mẫu: `.env.example` (đã bao gồm các biến dưới)

Biến môi trường chung
- STORAGE_DRIVER=local | s3 | minio

S3 (AWS hoặc S3-compatible)
- S3_REGION, S3_BUCKET
- S3_ACCESS_KEY, S3_SECRET_KEY
- S3_ENDPOINT (tùy chọn, dùng cho S3-compatible như MinIO)
- S3_USE_PATH_STYLE=true|false (mặc định true để tương thích tốt hơn)

MinIO
- MINIO_ENDPOINT=host:port
- MINIO_SECURE=true|false
- MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET

Lưu ý
- Với STORAGE_DRIVER=local, backend đã mount sẵn static /uploads để phục vụ file. URL public sẽ dạng: `/uploads/{category}/{filename}`.
- Với S3/MinIO, URL public sẽ trả về đầy đủ theo endpoint/bucket của bạn.
- Dependencies cho S3/MinIO đã có trong `backend/requirements.txt` (boto3, minio).

### Yêu Cầu Hệ Thống
- Python 3.8 trở lên 🐍
- 2GB RAM (khuyến nghị 4GB) 💾
- 1GB dung lượng ổ cứng 💿

### Cách 1: Khởi Chạy Tự Động (Khuyến nghị) ⚡

```bash
# 1. Clone hoặc download dự án
git clone [repository-url]
cd fado_crm

# 2. Chạy script tự động (sẽ cài đặt mọi thứ)
python run_server.py
```

### Cách 2: Cài Đặt Thủ Công 🔧

E2E Upload nhanh (khuyến nghị test tính năng upload mới):
- Yêu cầu: Backend chạy http://localhost:8000, Frontend chạy http://localhost:3000
- Chạy test đơn upload (Playwright):

```powershell
# Backend
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (mở server tĩnh)
python .\serve_frontend.py  # mặc định cổng 3000

# E2E Upload test (chạy riêng 1 test)
node ".\e2e\node_modules\@playwright\test\cli.js" test -c ".\e2e\playwright.config.js" -g "upload single product image via UI succeeds"
```

Kết quả mong đợi: 1 passed (~2s) xác nhận upload thành công qua UI.

```bash
# 1. Tạo virtual environment
python -m venv venv

# 2. Kích hoạt virtual environment
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# 3. Cài đặt dependencies
pip install -r backend/requirements.txt

# 4. Khởi động backend server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 5. Mở frontend trong browser
# Mở file: frontend/index.html
```

## 📱 Sử Dụng Hệ Thống

### 🌐 Truy Cập Giao Diện
- **Frontend**: Mở file `frontend/index.html` trong browser
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 🎯 Quy Trình Mua Hộ Chuẩn

1. **📋 Tiếp nhận đơn hàng**
   - Khách hàng gửi yêu cầu
   - Tạo đơn hàng với trạng thái "Chờ xác nhận"

2. **✅ Xác nhận đơn hàng**
   - Báo giá chi tiết cho khách
   - Cập nhật trạng thái "Đã xác nhận"

3. **🛒 Thực hiện mua hàng**
   - Đặt hàng từ shop nước ngoài
   - Cập nhật "Đang mua" → "Đã mua"

4. **🚚 Vận chuyển**
   - Theo dõi shipping
   - Cập nhật "Đang ship"

5. **📦 Giao hàng**
   - Khách nhận hàng
   - Hoàn thành đơn hàng

## 🎨 Screenshots

### Dashboard Tổng Quan
![Dashboard](docs/images/dashboard.png)
*Thống kê realtime với giao diện đẹp mắt*

### Quản Lý Khách Hàng
![Customers](docs/images/customers.png)
*Danh sách khách hàng với tìm kiếm và phân loại*

### Chi Tiết Đơn Hàng
![Orders](docs/images/orders.png)
*Theo dõi đơn hàng từ A đến Z*

## 🔒 Bảo Mật

- ✅ Input validation với Pydantic
- ✅ SQL injection protection với SQLAlchemy
- ✅ CORS configuration cho production
- ✅ Environment variables cho sensitive data
- ⚠️ **Lưu ý**: Phiên bản demo chưa có authentication, cần bổ sung cho production

## 📈 Performance

- ⚡ FastAPI async/await cho hiệu năng cao
- 🗄️ Database indexing cho search nhanh
- 🚀 Frontend caching và lazy loading
- 📱 Responsive design cho mobile

## 🛠️ Customization

### Thêm Trường Dữ Liệu Mới
1. Cập nhật `models.py` (database schema)
2. Cập nhật `schemas.py` (API validation)
3. Tạo migration với Alembic
4. Cập nhật frontend forms

### Thêm API Endpoint Mới
1. Thêm function trong `main.py`
2. Define request/response schemas
3. Cập nhật frontend để gọi API

### Tùy Chỉnh Giao Diện
1. Sửa CSS variables trong `style.css`
2. Thêm/sửa HTML components
3. Cập nhật JavaScript logic

## 🚀 Roadmap Phát Triển

### Phase 1 (Hoàn thành) ✅
- [x] Core CRM functionality
- [x] Dashboard thống kê realtime
- [x] Quản lý khách hàng, sản phẩm, đơn hàng
- [x] Responsive UI với Bootstrap 5
- [x] **Comprehensive API Documentation**
- [x] **Complete Testing Suite (85%+ coverage)**
- [x] **Professional Development Guidelines**
- [x] **Error Handling & Logging System**
- [x] **Security Middleware & Headers**

### Phase 2 (Tiếp theo) 🚧
- [ ] Authentication & Authorization (JWT)
- [ ] Role-based access control
- [ ] Email notifications system
- [ ] Export/Import Excel functionality
- [ ] Advanced reporting & analytics
- [ ] File upload for product images

### Phase 3 (Tương lai) 🔮
- [ ] Multi-tenant support
- [ ] Integration với shipping APIs
- [ ] AI-powered analytics & recommendations
- [ ] WhatsApp/Telegram bot integration
- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSocket)

## 🤝 Đóng Góp

Chúng tôi welcome mọi đóng góp!

1. Fork the project
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

Dự án này được phát hành dưới MIT License. Xem file `LICENSE` để biết thêm chi tiết.

## 🆘 Hỗ Trợ

### FAQ - Câu Hỏi Thường Gặp

**Q: Làm sao để thay đổi port của server?**
A: Sửa port trong file `run_server.py` hoặc chạy: `uvicorn main:app --port 8080`

**Q: Database file được lưu ở đâu?**
A: File SQLite được tạo tại `backend/fado_crm.db`

**Q: Làm sao để reset database?**
A: Xóa file `fado_crm.db` và chạy lại server

**Q: Có thể dùng PostgreSQL thay vì SQLite không?**
A: Có! Thay đổi `DATABASE_URL` trong `database.py`

### Liên Hệ Hỗ Trợ
- 📧 Email: support@fado.vn
- 💬 Discord: [FADO Community]
- 🐛 Issues: [GitHub Issues]

---

<div align="center">

**🚀 Được xây dựng với ❤️ bởi AI và tinh thần Việt Nam 🇻🇳**

*Happy Coding! 🎉*

</div>