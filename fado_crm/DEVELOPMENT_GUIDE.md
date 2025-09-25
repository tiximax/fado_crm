# 🛠️ FADO CRM - Development Guide
*Complete guide for developers working on FADO Vietnam Cross-Border Shopping CRM*

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Project Architecture](#project-architecture)
3. [Development Environment](#development-environment)
4. [Database Management](#database-management)
5. [Testing Guidelines](#testing-guidelines)
6. [API Development](#api-development)
7. [Frontend Development](#frontend-development)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend development)
- SQLite (included with Python)
- Git

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd fado_crm

# Setup backend
cd backend
python -m pip install -r requirements.txt
python -m pip install -r requirements-test.txt  # For testing

# Setup database
python create_demo_data.py  # Creates demo data

# Start backend server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# In new terminal - Start frontend server
cd ../frontend
python -m http.server 3000

# Access application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## 🏗️ Project Architecture

### Directory Structure
```
fado_crm/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application entry point
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy data models
│   ├── schemas.py          # Pydantic schemas for validation
│   ├── exceptions.py       # Custom exception handling
│   ├── middleware.py       # Custom middleware
│   ├── logging_config.py   # Logging configuration
│   ├── requirements.txt    # Python dependencies
│   ├── requirements-test.txt # Testing dependencies
│   ├── pytest.ini         # Test configuration
│   └── tests/              # Test suite
│       ├── conftest.py     # Test fixtures
│       ├── unit/           # Unit tests
│       └── integration/    # Integration tests
├── frontend/               # Vanilla JS frontend
│   ├── index.html          # Main HTML file
│   ├── script.js           # JavaScript logic
│   └── style.css           # CSS styles
├── logs/                   # Application logs
├── API_DOCUMENTATION.md    # Complete API reference
├── DEVELOPMENT_GUIDE.md    # This file
└── README.md              # Project overview
```

### Technology Stack

**Backend:**
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **SQLite**: Development database
- **Pytest**: Testing framework
- **Uvicorn**: ASGI server

**Frontend:**
- **Vanilla JavaScript**: No framework dependencies
- **Bootstrap CSS**: UI components and styling
- **Fetch API**: HTTP client for API calls

**Development Tools:**
- **Git**: Version control
- **Pytest**: Unit and integration testing
- **Coverage.py**: Test coverage reporting

---

## 💻 Development Environment

### Python Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv fado_env
source fado_env/bin/activate  # Linux/Mac
# OR
fado_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### IDE Configuration

**VS Code Recommended Extensions:**
- Python
- Pylance
- Thunder Client (for API testing)
- SQLite Viewer

**PyCharm Setup:**
- Configure Python interpreter to virtual environment
- Enable FastAPI support
- Setup pytest as test runner

### Environment Variables
Create `.env` file in backend directory:
```bash
# Database
DATABASE_URL=sqlite:///./fado_crm.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Development
DEBUG=True
RELOAD=True
```

---

## 🗄️ Database Management

### Database Schema

**Core Tables:**
- `khach_hang` - Customers
- `san_pham` - Products
- `don_hang` - Orders
- `chi_tiet_don_hang` - Order items
- `lich_su_lien_he` - Contact history

### Database Operations

**Create/Reset Database:**
```bash
cd backend
python database.py  # Creates tables
python create_demo_data.py  # Adds sample data
```

**View Database:**
```bash
# Using SQLite CLI
sqlite3 fado_crm.db
.tables
.schema khach_hang
SELECT * FROM khach_hang LIMIT 5;
```

**Backup Database:**
```bash
# Backup
cp fado_crm.db fado_crm_backup_$(date +%Y%m%d).db

# Restore
cp fado_crm_backup_20250923.db fado_crm.db
```

### Model Relationships
```python
# Customer -> Orders (One-to-Many)
customer = session.query(KhachHang).first()
customer.don_hang_list  # All orders for customer

# Order -> Order Items (One-to-Many)
order = session.query(DonHang).first()
order.chi_tiet_don_hang  # All items in order

# Order Item -> Product (Many-to-One)
item = session.query(ChiTietDonHang).first()
item.san_pham  # Product details
```

---

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_api_customers.py
│   ├── test_api_products.py
│   ├── test_api_orders.py
│   └── test_basic.py
└── integration/             # Integration tests
    └── test_error_handling.py
```

### Running Tests
```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_api_products.py -v

# Run tests matching pattern
python -m pytest tests/ -k "test_create" -v
```

### Test Fixtures
Key fixtures available in `conftest.py`:
- `db_session` - Clean database session
- `async_client` - HTTP client for API testing
- `sample_customer` - Test customer data
- `sample_product` - Test product data
- `sample_order` - Test order with items
- `multiple_customers` - List of test customers
- `multiple_products` - List of test products

### Writing Tests
```python
# Example API test
async def test_create_product(async_client, db_session):
    product_data = {
        "ten_san_pham": "Test Product",
        "gia_ban": 100000.0,
        "danh_muc": "Test Category"
    }

    response = await async_client.post("/san-pham/", json=product_data)

    assert response.status_code == 200
    data = response.json()
    assert data["ten_san_pham"] == "Test Product"
    assert data["id"] is not None
```

### Test Coverage Goals
- **Unit Tests**: 85%+ coverage
- **API Endpoints**: 100% coverage
- **Error Handling**: 100% coverage
- **Business Logic**: 90%+ coverage

---

## 🔧 API Development

### Adding New Endpoints

1. **Define Schema** (in `schemas.py`):
```python
class NewResourceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class NewResource(NewResourceCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

2. **Create Database Model** (in `models.py`):
```python
class NewResource(Base):
    __tablename__ = "new_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

3. **Add API Endpoint** (in `main.py`):
```python
@app.post("/new-resource/", response_model=schemas.NewResource)
async def create_new_resource(
    resource: schemas.NewResourceCreate,
    db: Session = Depends(get_db)
):
    """Create new resource"""
    db_resource = NewResource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource
```

4. **Add Tests**:
```python
async def test_create_new_resource(async_client, db_session):
    data = {"name": "Test Resource", "description": "Test"}
    response = await async_client.post("/new-resource/", json=data)
    assert response.status_code == 200
```

### Error Handling
```python
# Use custom exceptions
from exceptions import NotFoundError, ValidationError

@app.get("/resource/{resource_id}")
async def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise NotFoundError(resource="resource", resource_id=resource_id)
    return resource
```

### Logging
```python
from logging_config import app_logger, log_user_action, log_business_event

# Log user actions
log_user_action(
    user_id="system",
    action="create",
    resource="product",
    resource_id=str(product.id)
)

# Log business events
log_business_event("PRODUCT_CREATED", {
    "product_id": product.id,
    "product_name": product.ten_san_pham
})
```

---

## 🎨 Frontend Development

### Architecture
The frontend uses vanilla JavaScript with a modular approach:
- `script.js` - Main application logic
- `style.css` - Custom styles (extends Bootstrap)
- `index.html` - Single page application

### Key Components

**API Client:**
```javascript
class APIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return response.json();
    }
}
```

**Modal Management:**
```javascript
class ModalManager {
    static show(modalId) {
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        modal.show();
    }

    static hide(modalId) {
        const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
        if (modal) modal.hide();
    }
}
```

### Adding New Features

1. **Add HTML Structure:**
```html
<div class="tab-pane fade" id="new-feature" role="tabpanel">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4>New Feature</h4>
        <button class="btn btn-primary" onclick="NewFeature.showCreateModal()">
            Add New
        </button>
    </div>
    <div id="new-feature-list"></div>
</div>
```

2. **Add JavaScript Class:**
```javascript
class NewFeature {
    static async loadList() {
        try {
            const data = await apiClient.request('/new-feature/');
            this.renderList(data);
        } catch (error) {
            showToast('Error loading data', 'error');
        }
    }

    static renderList(items) {
        const container = document.getElementById('new-feature-list');
        container.innerHTML = items.map(item => `
            <div class="card mb-2">
                <div class="card-body">
                    <h6>${item.name}</h6>
                    <p>${item.description}</p>
                </div>
            </div>
        `).join('');
    }
}
```

### UI Guidelines
- Use Bootstrap 5 components
- Follow existing color scheme and spacing
- Implement responsive design
- Add loading states for async operations
- Show success/error toast notifications

---

## 🚀 Deployment

### Development Deployment
```bash
# Backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (serve static files)
cd frontend
python -m http.server 3000
```

### Production Deployment

**Docker Setup** (Future):
```dockerfile
# Dockerfile for backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Configuration:**
```bash
# Production environment variables
DATABASE_URL=postgresql://user:pass@localhost/fado_crm
DEBUG=False
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://your-domain.com"]
```

**Database Migration:**
```bash
# Backup current data
python backup_data.py

# Update database schema
python migrate_database.py

# Restore data
python restore_data.py
```

### Performance Considerations
- Database indexing for frequently queried fields
- API response pagination for large datasets
- Frontend lazy loading for better UX
- Caching for dashboard statistics
- CDN for static assets

---

## 🔧 Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check database file exists
ls -la fado_crm.db

# Recreate database
rm fado_crm.db
python database.py
python create_demo_data.py
```

**API Server Won't Start:**
```bash
# Check port availability
netstat -an | grep 8000

# Start with different port
python -m uvicorn main:app --port 8001

# Check for syntax errors
python -m py_compile main.py
```

**Test Failures:**
```bash
# Run tests with more verbose output
python -m pytest tests/ -v -s

# Check test database
python -c "from conftest import *; print('Test setup OK')"

# Clear test cache
rm -rf .pytest_cache
```

**Frontend API Calls Failing:**
```javascript
// Check browser console for CORS errors
// Verify API server is running
fetch('http://localhost:8000/')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

### Debugging Tips

**Backend Debugging:**
```python
# Add debug prints
print(f"Debug: {variable_name}")

# Use logging
app_logger.debug(f"Processing request: {request_data}")

# Interactive debugging
import pdb; pdb.set_trace()
```

**Frontend Debugging:**
```javascript
// Browser console debugging
console.log('Debug:', data);
console.table(arrayData);

// Network tab to inspect API calls
// Use browser DevTools for responsive testing
```

### Log Analysis
```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# Filter by date
grep "2025-09-23" logs/app.log | grep "ERROR"
```

---

## 📚 Additional Resources

### Code Style Guidelines
- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Use ES6+ features, consistent naming
- **SQL**: Use descriptive table/column names
- **Comments**: Focus on why, not what

### Git Workflow
```bash
# Feature development
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature implementation"
git push origin feature/new-feature

# Create pull request for review
```

### Performance Monitoring
- Monitor API response times
- Track database query performance
- Log business metrics
- Set up alerts for errors

### Security Checklist
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using ORM)
- [ ] XSS protection headers
- [ ] HTTPS in production
- [ ] Rate limiting (future)
- [ ] Authentication/authorization (future)

---

## 🎯 Next Steps

### Phase 2 Roadmap
1. **Authentication System**
   - JWT-based authentication
   - Role-based access control
   - User management

2. **Advanced Features**
   - File upload for product images
   - Email notifications
   - Order tracking system
   - Inventory management

3. **Performance Optimization**
   - Database optimization
   - API caching
   - Frontend optimization

4. **Production Ready**
   - Docker containerization
   - CI/CD pipeline
   - Monitoring and alerts
   - Backup strategies

---

*This guide is continuously updated. Check git history for latest changes.*

**Last updated**: September 23, 2025