# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## 🛍️ FADO CRM - Cross-Border Shopping Management System

**Hệ thống CRM chuyên dụng cho ngành mua hộ hàng nước ngoài** - A specialized CRM system for Vietnamese cross-border shopping businesses, built with FastAPI and vanilla JavaScript.

## 🚀 Development Commands

### Backend Development

```powershell
# Setup environment
cd backend
python -m pip install -r requirements.txt

# Create/reset database with demo data
python create_demo_data.py

# Start development server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Alternative simple server (minimal features)
python test_server.py

# Start full production-ready server
python complete_server.py
```

### Testing Commands

```powershell
cd backend

# Run all tests with coverage
python -m pytest tests/ -v --cov=. --cov-report=html:htmlcov

# Run specific test categories
python -m pytest tests/unit/ -v                    # Unit tests only
python -m pytest tests/integration/ -v             # Integration tests only

# Run single test file
python -m pytest tests/unit/test_api_customers.py -v

# Generate coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing

# Test E2E frontend (Playwright)
# Yêu cầu: Node.js và Playwright đã cài
cd e2e
npm install
npx playwright install
npx playwright test
```

### Database Management

```powershell
cd backend

# Create fresh database
python database.py

# Setup demo data
python simple_demo.py

# Create admin user
python create_admin.py

# Setup initial users (with different roles)
python setup_users.py

# Database migration (when using Alembic)
alembic upgrade head
```

### Development Tools

```powershell
# Code formatting and linting
black . --line-length=88
isort . --profile black
flake8 . --max-line-length=88

# Start frontend development server
cd frontend
python -m http.server 3000
```

## 🏗️ Architecture Overview

### Backend Architecture (FastAPI)
- **FastAPI Framework**: Modern async Python web framework with automatic API docs
- **SQLAlchemy 2.0**: Database ORM with relationship mapping
- **Pydantic**: Data validation and serialization
- **Modular Design**: Separated concerns with dedicated modules for auth, analytics, file handling
- **Professional Middleware**: Error handling, logging, security headers
- **WebSocket Support**: Real-time notifications via `websocket_service.py`

### Key Backend Modules
- `main.py`: Core API endpoints and application setup
- `auth.py`: JWT-based authentication with role-based access control
- `models.py`: SQLAlchemy database models for Vietnamese CRM domain
- `schemas.py`: Pydantic models for API validation
- `analytics_service.py`: Business intelligence and reporting
- `file_service.py`: File upload and image management
- `search_service.py`: Advanced search functionality
- `export_service.py`: Excel/CSV export capabilities
- `websocket_service.py`: Real-time notifications

### Frontend Architecture (Vanilla JavaScript)
- **No Framework Dependencies**: Pure JavaScript for maximum performance
- **Bootstrap 5**: Modern UI components and responsive design
- **Modular JavaScript**: Component-based architecture in `script.js`
- **API Integration**: Comprehensive REST API client with error handling
- **Real-time Features**: WebSocket integration for live updates

### Database Schema
Core entities optimized for Vietnamese cross-border shopping:
- **KhachHang** (Customers): Auto-classification (Mới/Thân thiết/VIP/Blacklist)
- **SanPham** (Products): Multi-currency pricing, origin tracking
- **DonHang** (Orders): 7-stage workflow (Chờ xác nhận → Hoàn thành)
- **ChiTietDonHang** (Order Items): Product-order relationship
- **LichSuLienHe** (Contact History): Multi-channel communication tracking
- **NguoiDung** (Users): Role-based system (Admin/Manager/Staff/Viewer)

## 🧪 Testing Strategy

### Test Structure
```
backend/tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/
│   ├── test_basic.py        # Basic functionality tests
│   ├── test_api_customers.py # Customer API endpoint tests
│   ├── test_api_products.py  # Product API endpoint tests
│   └── test_api_orders.py    # Order API endpoint tests
└── integration/
    └── test_error_handling.py # Error handling integration tests
```

### Test Configuration
- **pytest.ini**: Professional testing configuration with coverage requirements
- **Faker Integration**: Realistic Vietnamese test data generation
- **Database Isolation**: Each test uses isolated test database
- **Coverage Target**: 80% minimum coverage requirement

### Running Tests for New Features
According to user rules, only test new features during development - comprehensive testing when needed:
```powershell
# Test only specific new feature
python -m pytest tests/unit/test_api_customers.py::test_create_customer -v

# Test related functionality
python -m pytest tests/unit/test_api_customers.py -v
```

## 🔐 Authentication & Security

### JWT-Based Authentication
- **Login System**: `/auth/login` with JWT token generation
- **Role-Based Access**: Admin, Manager, Staff, Viewer roles
- **Token Refresh**: `/auth/refresh` for session management
- **Password Security**: bcrypt hashing with salt

### Security Features
- **CORS Configuration**: Controlled cross-origin access
- **Security Headers**: CSP, HSTS, and other security headers via middleware
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection attacks

## 🎯 Business Logic

### Vietnamese Cross-Border Shopping Workflow
1. **Order States**: 7-stage process from "Chờ xác nhận" to "Hoàn thành"
2. **Customer Classification**: Automatic tier assignment based on purchase history
3. **Multi-Currency**: USD pricing with VND conversion
4. **Fee Calculation**: Comprehensive cost breakdown (purchase fee, shipping, extras)

### Key Business Rules
- **Unique Order Codes**: Format `FD{YYMMDD}{6CHARS}` for tracking
- **Auto Customer Upgrade**: VIP ≥ 50M VND, Thân thiết ≥ 10M VND
- **Multi-Channel Contact**: Phone, SMS, Email tracking with staff assignment

## 📊 Data Export & Analytics

### Export Capabilities
- **Excel Export**: Customer, product, and order data via `export_service.py`
- **Business Reports**: Revenue trends, customer analytics, product performance
- **Advanced Analytics**: Powered by `analytics_service.py`

### Real-Time Dashboard
- **Live Metrics**: Customer count, pending orders, monthly revenue
- **Recent Activity**: Latest orders and new customers
- **Business Intelligence**: Charts and trends for decision-making

## 🔧 Development Patterns

### Code Standards
- **Vietnamese Comments**: Business logic comments in Vietnamese for domain clarity
- **English Code**: Variable names and functions in English for technical clarity  
- **Type Hints**: Comprehensive typing throughout codebase
- **Error Handling**: Custom exceptions with business-friendly messages
- **Logging**: Structured logging with user action tracking

### API Design
- **RESTful Endpoints**: Standard HTTP methods and status codes
- **Automatic Documentation**: Swagger UI at `/docs` and ReDoc at `/redoc`
- **Response Standardization**: Consistent JSON response format
- **Vietnamese Error Messages**: User-friendly error messages in Vietnamese

## 🚀 Deployment Notes

### Environment Setup
- **Python 3.8+** required
- **SQLite**: Development database (can migrate to PostgreSQL)
- **Environment Variables**: Use `.env` file for configuration
- **Static Files**: `/uploads` directory for file management

### Production Considerations
- **Database**: Migrate from SQLite to PostgreSQL for production
- **Authentication**: JWT tokens properly configured for production
- **File Storage**: Consider cloud storage for uploaded files
- **Monitoring**: Application logs in `logs/` directory

## 🎨 Frontend Development

### Component Architecture
- **Dashboard**: Real-time statistics and overview
- **Customer Management**: CRUD with search and classification
- **Product Catalog**: Grid layout with image support
- **Order Management**: 7-stage workflow tracking
- **Contact History**: Multi-channel communication logging

### UI/UX Patterns
- **Responsive Design**: Mobile-first Bootstrap 5 implementation
- **Loading States**: Skeleton loading and spinners
- **Error Handling**: Toast notifications and form validation
- **Real-Time Updates**: WebSocket integration for live data

## 📝 Important Files

### Core Documentation
- `README.md`: Complete project overview and setup instructions
- `QUICK_START.md`: Fast setup guide for immediate development
- `agent.md`: Development roadmap and implementation plan
- `API_DOCUMENTATION.md`: Complete REST API reference
- `DEVELOPMENT_GUIDE.md`: Comprehensive developer guidelines
- `CODE_STANDARDS.md`: Professional coding standards

### Configuration Files
- `backend/requirements.txt`: Python dependencies
- `backend/pytest.ini`: Test configuration
- `.env.example`: Environment variables template

### Key Implementation Files
- `backend/main.py`: Core application and API endpoints
- `backend/models.py`: Database schema for Vietnamese CRM
- `backend/schemas.py`: API validation schemas
- `frontend/script.js`: Frontend application logic
- `frontend/style.css`: Custom styling and responsive design

## 🌟 Vietnamese Business Context

This CRM is specifically designed for Vietnamese cross-border shopping (mua hộ) businesses with:
- **Vietnamese UI/UX**: User interface and error messages in Vietnamese
- **Local Business Rules**: Customer classification and order workflow optimized for Vietnamese market
- **Multi-Currency Support**: USD source pricing with VND customer pricing
- **Cross-Border Workflow**: Specialized order states for international shopping process

## 💡 Development Tips

- **Testing**: Follow user rule to test only new features during development
- **Commits**: Professional git messages without AI attribution per user rules  
- **Documentation**: All specs and progress tracked in `agent.md`
- **Vietnamese Context**: Maintain Vietnamese business terminology in comments and UI
- **Modular Design**: Each service module is independently testable and maintainable

---

Built with ❤️ for Vietnamese cross-border shopping businesses using modern Python and JavaScript technologies.