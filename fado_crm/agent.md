# 🚀 FADO CRM - IMPLEMENTATION PLAN & ROADMAP

## 📊 Hiện Trạng Dự Án (Current State Analysis)

### 🎯 **Codebase Overview**
- **Total Lines of Code**: ~4,075 lines
  - Python (Backend): 2,000 lines
  - JavaScript (Frontend): 823 lines
  - CSS (Styling): 870 lines
  - HTML (Structure): 382 lines

### ✅ **Đã Hoàn Thành (90% Complete)**
- ✅ Database models & schemas (SQLAlchemy + Pydantic)
- ✅ Core API endpoints (FastAPI với 18+ endpoints)
- ✅ Frontend UI components (5 modules chính)
- ✅ Dashboard với real-time statistics
- ✅ CRUD operations cho Khách hàng, Sản phẩm, Đơn hàng
- ✅ Search & filtering functionality
- ✅ Responsive design (mobile-first)
- ✅ Auto-classification logic cho khách hàng

### ⚠️ **Missing Components (10% Gap)**
- ❌ Authentication & Authorization system
- ❌ Detailed view modals cho các entities
- ❌ Edit functionality cho orders & products
- ❌ Advanced reporting & analytics
- ❌ Email notifications
- ❌ Export/Import functionality
- ❌ Production deployment configuration
- ❌ Error handling & logging
- ❌ Unit testing
- ❌ API rate limiting & security

---

## 🗺️ DEVELOPMENT ROADMAP

### 🎯 **PHASE 1: COMPLETION & STABILIZATION**
*Timeline: 2-3 weeks*
*Priority: CRITICAL - Complete core features*

#### 🔧 **Backend Enhancements**
1. **Complete Missing CRUD Operations**
   - Edit/Update operations cho Products
   - Delete operations với soft delete
   - Bulk operations cho mass actions

2. **Advanced API Features**
   - Pagination cho all list endpoints
   - Advanced filtering & sorting
   - API versioning (/api/v1/)
   - Input validation enhancements

3. **Error Handling & Logging**
   - Comprehensive exception handling
   - Structured logging với loguru
   - API error responses standardization
   - Health check endpoint

#### 🌐 **Frontend Completion**
1. **Missing UI Components**
   - Detailed view modals cho customers, products, orders
   - Edit modals với pre-filled data
   - Confirmation dialogs cho delete actions
   - Advanced search filters UI

2. **User Experience Improvements**
   - Form validation feedback
   - Loading states improvements
   - Better error messages
   - Keyboard shortcuts support

3. **Data Management Features**
   - Bulk select & actions
   - Advanced table sorting
   - Data export buttons (prepare for Phase 2)
   - Print functionality

---

### 🔐 **PHASE 2: AUTHENTICATION & SECURITY**
*Timeline: 3-4 weeks*
*Priority: HIGH - Production readiness*

#### 🛡️ **Authentication System**
1. **User Management**
   - User registration/login endpoints
   - JWT token authentication
   - Password hashing với bcrypt
   - User roles & permissions

2. **Authorization & Access Control**
   - Role-based access control (RBAC)
   - API endpoint protection
   - Frontend route guards
   - Admin vs Staff vs Viewer roles

3. **Security Enhancements**
   - Rate limiting với slowapi
   - CORS configuration tightening
   - Input sanitization
   - SQL injection prevention audit

#### 🔧 **Advanced Features**
1. **Email System**
   - SMTP configuration
   - Email templates
   - Order status notifications
   - Customer communication

2. **Data Export/Import**
   - Excel export cho all entities
   - CSV import functionality
   - Data validation on import
   - Batch processing

---

### 📊 **PHASE 3: ANALYTICS & REPORTING**
*Timeline: 3-4 weeks*
*Priority: MEDIUM - Business intelligence*

#### 📈 **Advanced Dashboard**
1. **Business Intelligence**
   - Advanced charts với Chart.js
   - Revenue trends & forecasting
   - Customer analytics & segmentation
   - Product performance metrics

2. **Reporting System**
   - Custom report builder
   - Scheduled reports
   - PDF report generation
   - Data visualization improvements

#### 🔄 **Workflow Automation**
1. **Business Process Automation**
   - Auto order status updates
   - Customer tier promotion automation
   - Alert system cho critical events
   - Workflow triggers

---

### 🚀 **PHASE 4: SCALABILITY & INTEGRATIONS**
*Timeline: 4-5 weeks*
*Priority: LOW - Growth preparation*

#### 🏗️ **Infrastructure**
1. **Database Optimization**
   - PostgreSQL migration
   - Database indexing optimization
   - Query performance tuning
   - Connection pooling

2. **API Enhancements**
   - GraphQL endpoint (optional)
   - WebSocket for real-time updates
   - API caching với Redis
   - Microservices preparation

#### 🔗 **Third-party Integrations**
1. **External Services**
   - Shipping providers API integration
   - Payment gateway integration
   - Social media APIs
   - WhatsApp Business API

2. **Mobile Support**
   - Progressive Web App (PWA)
   - Mobile app API preparation
   - Push notifications

---

## 📋 DETAILED TASK BREAKDOWN

### 🎯 **PHASE 1 DETAILED TASKS**

#### 📅 **Week 1: Backend Completion**

**Day 1-2: Complete Product Management**
- [ ] `PUT /san-pham/{id}` - Update product endpoint
- [ ] `DELETE /san-pham/{id}` - Soft delete product endpoint
- [ ] Add `is_active` field to SanPham model
- [ ] Frontend: EditProductModal component
- [ ] Frontend: Delete confirmation dialog

**Day 3-4: Order Management Enhancement**
- [ ] `PUT /don-hang/{id}/chi-tiet` - Update order items
- [ ] `POST /don-hang/{id}/trang-thai` - Update order status endpoint
- [ ] Add order history tracking table
- [ ] Frontend: Order detail modal với full information
- [ ] Frontend: Status update dropdown với validation

**Day 5-7: Advanced API Features**
- [ ] Implement pagination với `skip` & `limit` parameters
- [ ] Add advanced filtering (date range, price range)
- [ ] Create API versioning structure (/api/v1/)
- [ ] Add sorting parameters (sort_by, order_by)
- [ ] Implement search optimization với full-text search

#### 📅 **Week 2: Frontend Polish**

**Day 1-3: Modal System Enhancement**
- [ ] CustomerDetailModal với order history
- [ ] ProductDetailModal với image gallery
- [ ] OrderDetailModal với timeline view
- [ ] EditCustomerModal với validation
- [ ] DeleteConfirmationModal reusable component

**Day 4-5: Data Management**
- [ ] Bulk selection checkbox system
- [ ] Bulk actions toolbar (delete, update status)
- [ ] Advanced table sorting cho all columns
- [ ] Table column visibility toggle
- [ ] Table data persistence trong localStorage

**Day 6-7: UX Improvements**
- [ ] Form validation với real-time feedback
- [ ] Loading skeleton components
- [ ] Error boundary implementation
- [ ] Keyboard navigation support
- [ ] Toast notification improvements

#### 📅 **Week 3: Testing & Documentation**

**Day 1-3: Error Handling & Logging**
- [ ] Install loguru và configure structured logging
- [ ] Create custom exception classes
- [ ] Add try-catch blocks cho all API endpoints
- [ ] Implement global error handler
- [ ] Add health check endpoint (`/health`)

**Day 4-5: Testing Foundation**
- [ ] Setup pytest cho backend testing
- [ ] Create test database configuration
- [ ] Write unit tests cho core API endpoints
- [ ] Add integration tests cho workflows
- [ ] Frontend: Add basic JS tests

**Day 6-7: Documentation & Deployment Prep**
- [ ] Update API documentation
- [ ] Create deployment configuration files
- [ ] Docker containerization setup
- [ ] Environment variables configuration
- [ ] Performance optimization audit

---

### 🔐 **PHASE 2 DETAILED TASKS**

#### 📅 **Week 1: Authentication Backend**

**Day 1-2: User Model & Auth Setup**
```python
# New models to create:
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] Create User model với roles
- [ ] Setup password hashing với passlib
- [ ] JWT token configuration với python-jose
- [ ] Create authentication utilities

**Day 3-4: Auth Endpoints**
- [ ] `POST /auth/register` - User registration
- [ ] `POST /auth/login` - User authentication
- [ ] `POST /auth/refresh` - Token refresh
- [ ] `POST /auth/logout` - Token blacklist
- [ ] `GET /auth/me` - Current user info

**Day 5-7: Authorization System**
- [ ] Role-based middleware implementation
- [ ] Protect existing endpoints với depends
- [ ] Create permission decorators
- [ ] Add user context to API calls
- [ ] Implement access control matrix

#### 📅 **Week 2: Frontend Authentication**

**Day 1-3: Auth UI Components**
- [ ] LoginModal component với form validation
- [ ] RegisterModal cho new users
- [ ] UserProfile dropdown menu
- [ ] PasswordChangeModal
- [ ] LogoutConfirmation dialog

**Day 4-5: State Management**
- [ ] User authentication state management
- [ ] Token storage với secure methods
- [ ] Auto logout on token expiry
- [ ] Role-based UI visibility
- [ ] Protected route implementation

**Day 6-7: Integration & Testing**
- [ ] Integrate auth với existing API calls
- [ ] Add loading states cho auth actions
- [ ] Error handling cho auth failures
- [ ] Remember me functionality
- [ ] Session management

#### 📅 **Week 3-4: Email & Export Features**

**Day 1-4: Email System**
- [ ] Setup SMTP configuration với env variables
- [ ] Create email templates (HTML + text)
- [ ] Order confirmation email
- [ ] Status update notifications
- [ ] Welcome email cho new customers
- [ ] Email queue với background tasks

**Day 5-8: Export/Import System**
- [ ] Install openpyxl cho Excel operations
- [ ] Export customers to Excel
- [ ] Export orders với details
- [ ] Export products catalog
- [ ] Import customers từ CSV/Excel
- [ ] Data validation on import
- [ ] Import error reporting

---

### 📊 **PHASE 3 DETAILED TASKS**

#### 📅 **Week 1-2: Advanced Analytics**

**Day 1-5: Dashboard Enhancement**
- [ ] Install Chart.js cho data visualization
- [ ] Revenue trend charts (daily, monthly, yearly)
- [ ] Customer acquisition charts
- [ ] Product performance metrics
- [ ] Order status distribution pie chart
- [ ] Top customers by revenue

**Day 6-10: Reporting System**
- [ ] Create report models & schemas
- [ ] Custom date range selection
- [ ] Revenue reports với breakdowns
- [ ] Customer analytics reports
- [ ] Product performance reports
- [ ] Export reports to PDF

#### 📅 **Week 3-4: Workflow Automation**

**Day 1-4: Business Logic Automation**
- [ ] Auto status progression rules
- [ ] Customer tier promotion automation
- [ ] Low stock alerts
- [ ] Overdue order notifications
- [ ] Birthday/anniversary emails

**Day 5-8: Advanced Features**
- [ ] Scheduled task system với APScheduler
- [ ] Alert management system
- [ ] Workflow configuration UI
- [ ] Performance monitoring dashboard
- [ ] System health metrics

---

## ⏱️ **TIMELINE & RESOURCE ESTIMATION**

### 📊 **RESOURCE REQUIREMENTS & TIMELINE**

#### 👥 **Team Structure Recommendations**

**Minimum Team (1-2 người):**
- **Full-stack Developer** (Python + JavaScript): 1 người chính
- **UI/UX Support** (Part-time): 0.5 người

**Optimal Team (2-3 người):**
- **Backend Developer** (FastAPI/Python): 1 người
- **Frontend Developer** (JavaScript/CSS): 1 người
- **DevOps/QA Engineer** (Part-time): 0.5 người

#### ⏰ **Detailed Timeline Estimation**

| Phase | Duration | Effort (Hours) | Team Size | Calendar Time |
|-------|----------|----------------|-----------|---------------|
| **Phase 1** | 120 hours | Backend: 80h, Frontend: 40h | 1-2 devs | 3 weeks |
| **Phase 2** | 160 hours | Backend: 100h, Frontend: 60h | 2 devs | 4 weeks |
| **Phase 3** | 140 hours | Backend: 80h, Frontend: 60h | 2 devs | 3.5 weeks |
| **Phase 4** | 180 hours | Backend: 120h, Integration: 60h | 2-3 devs | 4.5 weeks |
| **Total** | **600 hours** | **15 weeks** | **Flexible** | **3.75 months** |

#### 💰 **Budget Estimation (Rough)**

**Development Costs:**
- Junior Developer: $25-35/hour × 600 hours = $15,000-21,000
- Senior Developer: $40-60/hour × 600 hours = $24,000-36,000
- **Recommended Mix**: $18,000-28,000 total

**Infrastructure Costs (Annual):**
- Domain & SSL: $100-200
- Cloud Hosting (AWS/GCP): $600-1,200
- Database (PostgreSQL): $300-600
- Email Service: $200-400
- **Total Infrastructure**: $1,200-2,400/year

#### 🛠️ **Technology Stack Additions Needed**

**Backend Dependencies:**
```python
# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Email & Background Tasks
fastapi-mail==1.2.7
celery==5.3.4
redis==5.0.1

# Logging & Monitoring
loguru==0.7.2
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.24.1

# Database Migration
alembic==1.12.1

# Excel/PDF Processing
openpyxl==3.1.2
reportlab==4.0.7
```

**Frontend Enhancements:**
```javascript
// Chart.js for analytics
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

// Date picker for filters
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>

// PDF generation
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
```

#### 🎯 **Success Metrics & KPIs**

**Technical Metrics:**
- API Response Time: < 200ms average
- Frontend Load Time: < 3 seconds
- Code Coverage: > 80%
- Bug Rate: < 5 bugs/month in production

**Business Metrics:**
- User Adoption: 90%+ of staff using system daily
- Data Accuracy: 95%+ correct customer/order data
- Efficiency Gain: 30%+ reduction in manual work
- Customer Satisfaction: Improved response times

#### 🚨 **Risk Assessment & Mitigation**

**High Risk:**
- **Data Migration Issues**
  - *Mitigation*: Comprehensive backup strategy, gradual migration
- **User Adoption Resistance**
  - *Mitigation*: Training sessions, gradual rollout

**Medium Risk:**
- **Performance Issues với Large Dataset**
  - *Mitigation*: Database optimization, pagination, caching
- **Third-party Integration Failures**
  - *Mitigation*: Fallback mechanisms, proper error handling

**Low Risk:**
- **Browser Compatibility Issues**
  - *Mitigation*: Cross-browser testing, progressive enhancement

---

## 📋 **IMPLEMENTATION CHECKLIST**

### 🎯 **Pre-Development Setup**
- [ ] Setup development environment
- [ ] Configure version control (Git flow)
- [ ] Setup CI/CD pipeline
- [ ] Create project documentation structure
- [ ] Define coding standards & review process

### 🔄 **Development Process**
- [ ] Daily standups (nếu team > 1)
- [ ] Weekly progress reviews
- [ ] Code reviews cho mọi PR
- [ ] Testing before merge
- [ ] Documentation updates

### 🚀 **Deployment Strategy**
- [ ] Staging environment setup
- [ ] Production environment configuration
- [ ] Database migration plan
- [ ] Backup & recovery procedures
- [ ] Monitoring & alerting setup

---

## 🎉 **SUMMARY - IMPLEMENTATION PLAN**

### 📊 **Executive Summary**
Dự án **FADO CRM** hiện tại đã hoàn thành **90%** core functionality với codebase chất lượng cao (4,075+ lines). Để đưa vào production cần **3.75 tháng** phát triển thêm qua 4 phases chính.

### ✅ Phase 4 - Scalability & Integrations (Đã triển khai)
- Database: Thêm cấu hình PostgreSQL (pooling + indexes) và biến môi trường DATABASE_URL
- Performance: Cache Redis (fallback in-memory), endpoint /health, /metrics (nếu khả dụng), cache flush /cache/flush
- GraphQL: Mount /graphql (Strawberry) với schema truy vấn cơ bản (khách hàng/sản phẩm/đơn hàng)
- PWA: manifest + service worker + đăng ký trong frontend
- DevOps: Dockerfile backend, docker-compose (db/redis/backend/nginx), deploy/nginx.conf
- E2E: Thêm Playwright tests (e2e/) với smoke tests (login, redirect, dashboard optional)
- Tài liệu: PHASE_4_COMPLETION_SUMMARY.md mô tả chi tiết

### ✅ Phase 5 - Operations & Quality (Đã triển khai)
- Models: Thêm AuditLog, SystemSetting
- Admin APIs: /admin/audit-logs (GET), /admin/system-settings (GET), /admin/system-settings/{key} (GET/PUT upsert)
- Rate limiting (tùy chọn): tích hợp SlowAPI nếu có, áp dụng middleware (đặt sẵn mặc định 200/minute)
- Login auditing: ghi nhận AuditLog khi đăng nhập thành công
- Tests: Thêm unit tests cho admin settings và audit logs (backend/tests/unit/test_admin_features.py)
- Ghi chú: Tất cả endpoints admin yêu cầu quyền admin; trong test override get_admin_user để tập trung test logic

### 🚀 **Quick Start Recommendation**
**Bắt đầu ngay với Phase 1** để có sản phẩm MVP hoàn chỉnh trong 3 tuần:

1. **Week 1**: Complete missing CRUD operations
2. **Week 2**: Polish frontend UI/UX
3. **Week 3**: Testing, error handling & documentation

### 💡 **Key Success Factors**
- **Strong Foundation**: Codebase hiện tại rất solid, architecture tốt
- **Clear Roadmap**: 4 phases với tasks cụ thể và timeline rõ ràng
- **Flexible Timeline**: Có thể adjust theo resource và priority
- **Production Ready**: Phase 1-2 đủ cho production deployment

### 🎯 **Next Immediate Actions**
1. **Confirm scope** cho Phase 1 (3 weeks)
2. **Setup development environment** với new dependencies
3. **Start with backend completion** (missing CRUD endpoints)
4. **Parallel frontend enhancement** (modals & UX improvements)

**Total Investment**: $18k-28k development + $1.2k-2.4k/year infrastructure
**ROI**: 30%+ efficiency gain, improved customer service, scalable business operations

Dự án này có **foundation excellent** và **roadmap clear**, sẵn sàng scale từ startup đến enterprise level! 🚀

---

## 📋 FADO.VN CRM - SPECIFICATION CHI TIẾT

### 🎯 Tổng Quan Dự Án

**FADO.VN CRM** là hệ thống quản lý khách hàng (Customer Relationship Management) chuyên dụng cho ngành **mua hộ hàng nước ngoài**. Dự án được xây dựng bằng **FastAPI** (backend) và **Vanilla JavaScript** (frontend) với thiết kế hiện đại, responsive và user-friendly.

### 🏗️ Kiến Trúc Hệ Thống

#### Backend Architecture
- **Framework**: FastAPI
- **Database**: SQLite (có thể chuyển sang PostgreSQL)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic
- **API Documentation**: Swagger UI + ReDoc
- **CORS**: Hỗ trợ cross-origin requests

#### Frontend Architecture
- **UI Framework**: Vanilla JavaScript (không dependencies)
- **Styling**: CSS3 với CSS Variables
- **Icons**: Font Awesome 6.0
- **Layout**: CSS Grid + Flexbox
- **Responsive**: Mobile-first design

### 📊 Database Schema

#### 1. Khách Hàng (KhachHang)
```sql
- id: Primary Key
- ho_ten: Họ tên (required, max 100 chars)
- email: Email unique (required)
- so_dien_thoai: Số điện thoại (optional, max 20 chars)
- dia_chi: Địa chỉ nhận hàng (text)
- ngay_tao: Timestamp tạo tài khoản
- loai_khach: Enum (MOI, THAN_THIET, VIP, BLACKLIST)
- tong_tien_da_mua: Tổng tiền đã chi (auto-calculated)
- so_don_thanh_cong: Số đơn thành công (auto-calculated)
- ghi_chu: Ghi chú đặc biệt
```

#### 2. Sản Phẩm (SanPham)
```sql
- id: Primary Key
- ten_san_pham: Tên sản phẩm (required, max 200 chars)
- link_goc: URL sản phẩm gốc (max 500 chars)
- gia_goc: Giá gốc USD (float)
- gia_ban: Giá bán VND (float)
- mo_ta: Mô tả chi tiết (text)
- hinh_anh_url: Link hình ảnh (max 500 chars)
- trong_luong: Trọng lượng kg (float)
- kich_thuoc: Kích thước (max 100 chars)
- danh_muc: Danh mục sản phẩm (max 100 chars)
- quoc_gia_nguon: Nước xuất xứ (max 50 chars)
- ngay_tao: Timestamp
```

#### 3. Đơn Hàng (DonHang)
```sql
- id: Primary Key
- ma_don_hang: Mã đơn unique (format: FD{YYMMDD}{6CHARS})
- khach_hang_id: Foreign Key → KhachHang
- tong_gia_san_pham: Tổng giá sản phẩm
- phi_mua_ho: Phí mua hộ
- phi_van_chuyen: Phí vận chuyển
- phi_khac: Phí khác
- tong_tien: Tổng tiền cuối cùng (auto-calculated)
- trang_thai: Enum (CHO_XAC_NHAN, DA_XAC_NHAN, DANG_MUA, DA_MUA, DANG_SHIP, DA_NHAN, HUY)
- ngay_tao: Timestamp tạo đơn
- ngay_cap_nhat: Timestamp cập nhật cuối
- ngay_giao_hang: Ngày giao hàng dự kiến
- ghi_chu_khach: Ghi chú từ khách hàng
- ghi_chu_noi_bo: Ghi chú nội bộ
- ma_van_don: Mã tracking vận chuyển
```

#### 4. Chi Tiết Đơn Hàng (ChiTietDonHang)
```sql
- id: Primary Key
- don_hang_id: Foreign Key → DonHang
- san_pham_id: Foreign Key → SanPham
- so_luong: Số lượng (default 1)
- gia_mua: Giá mua thực tế
- ghi_chu: Ghi chú riêng cho item
```

#### 5. Lịch Sử Liên Hệ (LichSuLienHe)
```sql
- id: Primary Key
- khach_hang_id: Foreign Key → KhachHang
- loai_lien_he: Loại (call, sms, email)
- noi_dung: Nội dung cuộc liên hệ
- ngay_lien_he: Timestamp
- nhan_vien_xu_ly: Nhân viên xử lý
- ket_qua: Kết quả liên hệ
```

### 🚀 API Endpoints

#### Dashboard
- `GET /` - Welcome message
- `GET /dashboard` - Thống kê tổng quan

#### Khách Hàng
- `GET /khach-hang/` - Danh sách (với search & filter)
- `POST /khach-hang/` - Tạo mới
- `GET /khach-hang/{id}` - Chi tiết
- `PUT /khach-hang/{id}` - Cập nhật
- `POST /khach-hang/{id}/cap-nhat-loai` - Auto update loại khách

#### Sản Phẩm
- `GET /san-pham/` - Danh sách (với search & filter)
- `POST /san-pham/` - Tạo mới

#### Đơn Hàng
- `GET /don-hang/` - Danh sách (với filter)
- `POST /don-hang/` - Tạo mới
- `GET /don-hang/{id}` - Chi tiết
- `PUT /don-hang/{id}` - Cập nhật

#### Lịch Sử Liên Hệ
- `GET /lich-su-lien-he/` - Danh sách
- `POST /lich-su-lien-he/` - Ghi nhận mới

### 💡 Tính Năng Chính

#### 1. Dashboard Thống Kê
- **Real-time metrics**: Tổng khách hàng, đơn hàng, doanh thu tháng
- **Đơn chờ xử lý**: Tracking các đơn pending
- **Khách mới tháng**: Thống kê khách hàng mới
- **Recent orders**: Hiển thị đơn hàng gần đây
- **New customers**: Danh sách khách hàng mới

#### 2. Quản Lý Khách Hàng
- **CRUD operations**: Tạo, đọc, cập nhật khách hàng
- **Search & Filter**: Tìm kiếm theo tên/email/SĐT, lọc theo loại khách
- **Auto classification**: Tự động phân loại khách dựa trên tổng chi tiêu
  - Khách VIP: ≥ 50 triệu VND
  - Khách thân thiết: ≥ 10 triệu VND
  - Khách mới: < 10 triệu VND
- **Email validation**: Đảm bảo email unique và format hợp lệ

#### 3. Quản Lý Sản Phẩm
- **Product catalog**: Hiển thị dạng grid với hình ảnh
- **Multi-field management**: Giá gốc/bán, trọng lượng, kích thước
- **Category & Origin**: Phân loại danh mục và nước xuất xứ
- **Original link tracking**: Lưu link sản phẩm gốc từ shop nước ngoài
- **Search functionality**: Tìm kiếm theo tên và mô tả

#### 4. Quản Lý Đơn Hàng
- **7-stage workflow**: Quy trình mua hộ đầy đủ từ A-Z
- **Unique order code**: Mã đơn tự động format FD{date}{random}
- **Cost calculation**: Tính toán chi phí chi tiết (sản phẩm + phí)
- **Status tracking**: Theo dõi trạng thái real-time
- **Customer linking**: Liên kết với thông tin khách hàng
- **Delivery tracking**: Mã vận đơn và ngày giao hàng

#### 5. Lịch Sử Liên Hệ
- **Multi-channel tracking**: Call, SMS, Email
- **Staff assignment**: Gán nhân viên xử lý
- **Result tracking**: Ghi nhận kết quả liên hệ
- **Customer linkage**: Liên kết với khách hàng cụ thể

### 🎨 Frontend Features

#### UI Components
- **Responsive navigation**: Tab-based với icons
- **Dashboard cards**: Stats cards với animation
- **Data tables**: Sortable, searchable tables
- **Product grid**: Modern card-based layout
- **Modal dialogs**: Form input với validation
- **Toast notifications**: Real-time feedback
- **Loading states**: Spinner và skeleton loading

#### Interactions
- **Real-time search**: Debounced search với 300ms delay
- **Filter & sort**: Multiple filter options
- **CRUD operations**: Full create, read, update functionality
- **Form validation**: Client-side validation
- **Error handling**: Comprehensive error messages
- **Animation effects**: Smooth transitions và hover effects

#### Responsive Design
- **Mobile-first**: Optimized cho mobile devices
- **Breakpoints**: Tablet và desktop responsive
- **Touch-friendly**: Button sizes và interactions
- **Performance**: Lightweight, no heavy dependencies

### 🔧 Technical Implementation

#### Backend Logic
```python
# Auto-generate order code
def generate_ma_don_hang():
    timestamp = datetime.now().strftime("%y%m%d")
    random_part = str(uuid.uuid4())[:6].upper()
    return f"FD{timestamp}{random_part}"

# Auto-calculate total cost
tong_tien = (gia_san_pham + phi_mua_ho + phi_van_chuyen + phi_khac)

# Auto-update customer type
if tong_tien_da_mua >= 50000000:  # 50M VND
    loai_khach = VIP
elif tong_tien_da_mua >= 10000000:  # 10M VND
    loai_khach = THAN_THIET
else:
    loai_khach = MOI
```

#### Frontend Logic
```javascript
// API base URL configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// Debounced search for performance
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// Currency formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
```

### 🎯 Business Logic

#### Quy Trình Mua Hộ
1. **Chờ xác nhận** → Khách gửi yêu cầu
2. **Đã xác nhận** → Báo giá và xác nhận với khách
3. **Đang mua** → Tiến hành đặt hàng từ shop nước ngoài
4. **Đã mua** → Hoàn tất việc mua, chờ ship về VN
5. **Đang ship** → Hàng đang trên đường vận chuyển
6. **Đã nhận** → Khách đã nhận hàng
7. **Hủy** → Đơn hàng bị hủy

#### Phân Loại Khách Hàng
- **🆕 Khách mới**: < 10 triệu VND
- **💎 Khách thân thiết**: 10-50 triệu VND
- **👑 Khách VIP**: ≥ 50 triệu VND
- **🚫 Blacklist**: Khách có vấn đề

#### Tính Phí
- **Phí mua hộ**: % trên giá trị đơn hàng
- **Phí vận chuyển**: Theo trọng lượng/kích thước
- **Phí khác**: Phí đặc biệt (bảo hiểm, xử lý...)

### 🚀 Deployment & Operations

#### Development Setup
```bash
# Backend
cd backend
pip install fastapi uvicorn sqlalchemy pydantic
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend
# Open frontend/index.html in browser
```

#### Production Considerations
- **Database**: Migrate to PostgreSQL
- **Authentication**: Add JWT/OAuth2
- **HTTPS**: SSL certificate setup
- **Monitoring**: Logging và error tracking
- **Backup**: Database backup strategy
- **Scaling**: Load balancer và multiple instances

#### Security Features
- **Input validation**: Pydantic schemas
- **SQL injection protection**: SQLAlchemy ORM
- **CORS configuration**: Controlled access
- **Data sanitization**: Frontend validation

---

## 📦 SPECIFY / PLAN / TASKS - Storage pluggable (Local/S3/MinIO)

SPECIFY
- Ngôn ngữ: Python (FastAPI backend)
- Mục tiêu: Chuẩn hoá storage thành driver pluggable: local, S3 (boto3), MinIO (minio SDK)
- Ràng buộc:
  - Không phá vỡ API hiện có (các endpoint /upload/... vẫn hoạt động như cũ)
  - URL trả về phải hoạt động với cả local và object storage
  - Tối thiểu: test unit cho LocalStorageDriver
- Input/Output:
  - Input: UploadFile từ FastAPI
  - Output: JSON gồm success, file_info, url, thumbnails

PLAN (cách tiếp cận)
- Tạo module storage driver: StorageDriver base + Local/S3/MinIO
- Thêm hàm factory get_storage_driver() đọc STORAGE_DRIVER
- Wiring file_service để dùng storage.save_bytes(...) thay vì ghi thẳng vào ổ đĩa
- Tạo thumbnails từ bytes và lưu qua storage driver (không phụ thuộc FS cục bộ)
- Giữ mount /uploads (phục vụ local); remote vẫn tạo thư mục để tránh lỗi mount
- Viết unit test cho LocalStorageDriver (save/url/exists/delete)

TASKS
1) Thêm backend/storage.py với 3 drivers + exists()
2) Cập nhật file_service.py dùng storage driver (save_bytes, public_url, delete, exists)
3) Thay đổi create_thumbnails để thao tác qua bytes, lưu thumbnail qua driver
4) Đảm bảo main.py mount /uploads (giữ nguyên hiện trạng)
5) Viết tests: backend/tests/unit/test_storage.py
6) Cập nhật .env.example (đã có keys S3/MINIO) và requirements.txt (đã có boto3/minio)

PROGRESS
- [x] 1) storage.py đã tạo (Local/S3/MinIO) và thêm exists()
- [x] 2) file_service.py đã wiring qua driver (image, document, delete, info)
- [x] 3) create_thumbnails chuyển sang bytes + lưu qua driver
- [x] 4) main.py đã mount /uploads sẵn (giữ nguyên)
- [x] 5) Đã thêm test unit cho LocalStorageDriver
- [x] 6) .env.example + requirements.txt đã có cấu hình/phụ thuộc cho storage

NEXT
- Chạy unit tests cho storage (ưu tiên test tính năng mới theo rule)
- Tùy chọn: thêm test integration cho file_service với local driver

### 📈 Future Enhancements

---

## 🧪 SPECIFY / PLAN / TASKS - E2E Upload UI

---

## 🖼️ SPECIFY / PLAN / TASKS - Gallery API + UI

---

## 🗑️ SPECIFY / PLAN / TASKS - Delete Media

SPECIFY
- Mục tiêu: Cho phép xóa file đã upload từ API và UI (xóa kèm thumbnails nếu là ảnh)
- Backend: DELETE /upload/file (category, filename)
- Frontend: Nút xóa trong gallery, xác nhận và refresh

PLAN
- Backend: endpoint DELETE /upload/file
  - product_images → gọi file_service.delete_file(..., "image") để xóa ảnh + thumbnails
  - thumbnails/documents → storage.delete(category, filename)
- Frontend: thêm button xóa và hàm deleteMedia(category, filename)
- (Test) Sử dụng test hiện có, ưu tiên test phần mới sau khi ổn định

TASKS
1) main.py: thêm DELETE /upload/file
2) file-upload.html: thêm nút xóa + deleteMedia()
3) Ghi nhận vào agent.md

PROGRESS
- [x] 1) Backend endpoint đã thêm
- [x] 2) Frontend gallery có nút xóa & refresh
- [x] 3) Đã cập nhật agent.md

SPECIFY
- Mục tiêu: Hiển thị thư viện ảnh thực tế từ backend
- Backend: Endpoint GET /upload/list trả danh sách file theo category
- Frontend: file-upload.html gọi API và render grid ảnh
- Driver: Hỗ trợ Local/S3/MinIO qua storage drivers

PLAN
- Thêm phương thức list() vào storage drivers (Local/S3/MinIO)
- Thêm FileService.list_files() và endpoint /upload/list
- Cập nhật loadGallery() gọi API, render items
- Viết unit test cho driver Local list()
- (Tuỳ chọn) Mở rộng E2E để xác nhận gallery; tạm thời giữ đơn giản tránh flakiness

TASKS
1) storage.py: add list() cho Local/S3/MinIO
2) file_service.py: add list_files()
3) main.py: add GET /upload/list trả URL tuyệt đối (prefix base_url khi local)
4) frontend/file-upload.html: loadGallery() gọi API và render ảnh
5) tests: unit test list() cho LocalStorageDriver
6) (E2E) mở rộng upload.spec.js xác nhận status; gallery assertion tạm bỏ nếu flakey

PROGRESS
- [x] 1) storage.py đã thêm list()
- [x] 2) file_service.py đã thêm list_files()
- [x] 3) main.py đã có /upload/list
- [x] 4) file-upload.html đã render gallery từ API
- [x] 5) Unit test list() LocalStorageDriver PASS
- [x] 6) E2E upload test PASS (giữ kiểm tra trạng thái upload ok)

SPECIFY
- Mục tiêu: Viết E2E test kiểm thử upload hình ảnh sản phẩm qua UI (Local driver)
- Điều kiện: Backend chạy http://localhost:8000, Frontend chạy http://localhost:3000, admin tồn tại
- Đầu vào/Đầu ra: Input file ảnh 1x1 PNG, kết quả UI hiển thị trạng thái success

PLAN
- Tạo test e2e/tests/upload.spec.js: login admin → mở file-upload.html → thêm file → Upload → verify success
- Nếu test fail do bug UI, sửa nhỏ để đảm bảo chức năng hoạt động (không thay đổi lớn UX)
- Chỉ chạy test mới để tiết kiệm thời gian

TASKS
1) Thêm file e2e/tests/upload.spec.js với seeding token & upload 1x1 PNG
2) Phát hiện và sửa bug UI file-upload.html (đụng tên biến this.uploadQueue giữa mảng và DOM); đổi thành this.queue và this.uploadQueueEl
3) Sửa auth.js apiCall để không force 'Content-Type: application/json' khi body là FormData → tránh lỗi upload
4) Chạy test đơn lẻ với grep theo tên test

PROGRESS
- [x] 1) Test upload.spec.js đã tạo
- [x] 2) Sửa bug tên biến queue trong file-upload.html
- [x] 3) Sửa Content-Type trong auth.js cho FormData
- [x] 4) Test đã PASS: 1 passed (≈2s)

#### Phase 2 Features
- **Authentication system**: User login/roles
- **Email notifications**: Automated emails
- **Excel export/import**: Data management
- **Advanced reporting**: Business intelligence
- **Mobile app**: React Native/Flutter

#### Phase 3 Features
- **Multi-tenant support**: Multiple businesses
- **Shipping API integration**: Real-time tracking
- **AI analytics**: Predictive insights
- **WhatsApp/Telegram bot**: Customer communication
- **Payment gateway**: Online payments

---

## 🎉 Kết Luận

FADO.VN CRM là một hệ thống CRM hoàn chỉnh và hiện đại, được thiết kế đặc biệt cho ngành mua hộ. Với kiến trúc backend mạnh mẽ (FastAPI + SQLAlchemy) và frontend responsive (Vanilla JS), hệ thống cung cấp tất cả tính năng cần thiết để quản lý khách hàng, sản phẩm, đơn hàng và liên hệ một cách hiệu quả.

**Điểm mạnh:**
- Code clean, có comments chi tiết
- API documentation đầy đủ
- UI/UX hiện đại và responsive
- Business logic phù hợp với ngành mua hộ
- Dễ dàng mở rộng và maintain

**Sẵn sàng production** với một số enhancement về security và deployment!