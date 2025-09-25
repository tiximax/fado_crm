# 📐 FADO CRM - Code Standards & Guidelines
*Development standards for maintaining high-quality, consistent codebase*

## 🎯 Overview

This document establishes coding standards, best practices, and development guidelines for the FADO CRM project. Following these standards ensures code consistency, maintainability, and team collaboration efficiency.

---

## 📋 Table of Contents
1. [General Principles](#general-principles)
2. [Python/Backend Standards](#pythonbackend-standards)
3. [JavaScript/Frontend Standards](#javascriptfrontend-standards)
4. [Database Standards](#database-standards)
5. [API Design Standards](#api-design-standards)
6. [Testing Standards](#testing-standards)
7. [Documentation Standards](#documentation-standards)
8. [Git Workflow](#git-workflow)
9. [Code Review Guidelines](#code-review-guidelines)

---

## 🎯 General Principles

### Code Quality Pillars
1. **Readability**: Code should be self-documenting
2. **Consistency**: Follow established patterns
3. **Maintainability**: Easy to modify and extend
4. **Testability**: Write testable, modular code
5. **Performance**: Efficient but not at cost of readability
6. **Security**: Always consider security implications

### SOLID Principles
- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

---

## 🐍 Python/Backend Standards

### Code Style (PEP 8 Compliant)

**File Structure:**
```python
# File header with description
"""
📄 Module Description
Brief description of module purpose and functionality
"""

# Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Local imports
from .database import get_db
from .models import Customer
from .schemas import CustomerCreate
```

**Naming Conventions:**
```python
# Constants
MAX_RETRY_COUNT = 3
DATABASE_URL = "sqlite:///fado_crm.db"

# Classes (PascalCase)
class CustomerManager:
    pass

class OrderStatusEnum(Enum):
    PENDING = "pending"

# Functions and variables (snake_case)
def get_customer_by_id(customer_id: int) -> Customer:
    pass

customer_name = "Nguyen Van A"
total_amount = 1500000.0

# Private methods/attributes
def _validate_email(email: str) -> bool:
    pass

class Customer:
    def __init__(self):
        self._internal_id = None
```

**Type Hints (Required):**
```python
from typing import List, Optional, Dict, Union
from datetime import datetime

def create_customer(
    customer_data: CustomerCreate,
    db: Session
) -> Customer:
    """Create new customer with validation"""
    pass

def get_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[Customer]:
    """Get customers with pagination and search"""
    pass

# Complex type hints
CustomerDict = Dict[str, Union[str, int, float]]
OrderStatusType = Literal["pending", "confirmed", "shipped"]
```

**Error Handling:**
```python
# Use specific exceptions
from exceptions import NotFoundError, ValidationError

def get_customer(customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise NotFoundError(resource="customer", resource_id=customer_id)
    return customer

# Proper exception handling
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise DatabaseError(message="Failed to process request")
finally:
    cleanup_resources()
```

**Logging Standards:**
```python
from logging_config import app_logger

# Use appropriate log levels
app_logger.debug("Detailed debugging information")
app_logger.info("General application flow")
app_logger.warning("Something unexpected happened")
app_logger.error("Error occurred but application continues")
app_logger.critical("Serious error, application may stop")

# Include context in logs
app_logger.info(f"Customer {customer_id} created successfully")
app_logger.error(f"Failed to create customer: {error_details}")

# Use structured logging for business events
log_business_event("CUSTOMER_CREATED", {
    "customer_id": customer.id,
    "customer_type": customer.loai_khach.value
})
```

**FastAPI Endpoint Standards:**
```python
@app.post("/customers/", response_model=schemas.Customer)
async def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
) -> schemas.Customer:
    """
    Create new customer

    - **customer**: Customer data with required fields
    - **Returns**: Created customer with ID and timestamps
    """

    # Validate business rules
    existing_customer = db.query(Customer).filter(
        Customer.email == customer.email
    ).first()
    if existing_customer:
        raise ConflictError(message="Email already exists")

    # Create and save
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    # Log action
    log_user_action(
        user_id="system",
        action="create",
        resource="customer",
        resource_id=str(db_customer.id)
    )

    return db_customer
```

### Database Standards

**Model Definitions:**
```python
class Customer(Base):
    """Customer model with comprehensive tracking"""
    __tablename__ = "customers"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Required fields
    ho_ten = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)

    # Optional fields
    so_dien_thoai = Column(String(20), nullable=True)
    dia_chi = Column(Text, nullable=True)

    # Enums
    loai_khach = Column(Enum(LoaiKhachHang), default=LoaiKhachHang.MOI)

    # Timestamps (required for all models)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False)
    ngay_cap_nhat = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    don_hang_list = relationship("DonHang", back_populates="khach_hang")

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, email='{self.email}')>"
```

**Schema Definitions:**
```python
class CustomerBase(BaseModel):
    """Base customer schema with common fields"""
    ho_ten: str = Field(..., min_length=2, max_length=100, description="Customer full name")
    email: EmailStr = Field(..., description="Valid email address")
    so_dien_thoai: Optional[str] = Field(None, max_length=20, regex=r'^\+?[\d\s\-\(\)]+$')
    loai_khach: Optional[LoaiKhachHang] = Field(LoaiKhachHang.MOI)

class CustomerCreate(CustomerBase):
    """Schema for creating new customer"""
    pass

class CustomerUpdate(BaseModel):
    """Schema for updating customer (all optional)"""
    ho_ten: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    so_dien_thoai: Optional[str] = Field(None, max_length=20)

class Customer(CustomerBase):
    """Full customer schema with computed fields"""
    id: int
    ngay_tao: datetime
    tong_tien_da_mua: float = Field(0.0, description="Total amount spent")
    so_don_thanh_cong: int = Field(0, description="Successful orders count")

    class Config:
        from_attributes = True
```

---

## 🌐 JavaScript/Frontend Standards

### Code Organization
```javascript
// Use modules and classes for organization
class APIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.headers = {
            'Content-Type': 'application/json'
        };
    }

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: this.headers,
                ...options
            });

            if (!response.ok) {
                throw new APIError(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
}

// Use const/let appropriately
const API_BASE_URL = 'http://localhost:8000';
let currentPage = 1;
const itemsPerPage = 20;
```

### Naming Conventions
```javascript
// Constants (SCREAMING_SNAKE_CASE)
const MAX_RETRY_ATTEMPTS = 3;
const API_ENDPOINTS = {
    CUSTOMERS: '/khach-hang/',
    PRODUCTS: '/san-pham/',
    ORDERS: '/don-hang/'
};

// Classes (PascalCase)
class CustomerManager {
    constructor() {
        this.customers = [];
    }

    // Methods (camelCase)
    async loadCustomers() {
        // Implementation
    }

    renderCustomerList(customers) {
        // Implementation
    }
}

// Functions and variables (camelCase)
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

const customerData = await fetchCustomers();
```

### Error Handling
```javascript
// Custom error classes
class APIError extends Error {
    constructor(message, status = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
    }
}

// Proper async/await error handling
async function createCustomer(customerData) {
    try {
        const response = await apiClient.request('/khach-hang/', {
            method: 'POST',
            body: JSON.stringify(customerData)
        });

        showToast('Customer created successfully', 'success');
        return response;

    } catch (error) {
        if (error instanceof APIError) {
            showToast(`Failed to create customer: ${error.message}`, 'error');
        } else {
            showToast('Unexpected error occurred', 'error');
            console.error('Unexpected error:', error);
        }
        throw error;
    }
}

// Form validation
function validateCustomerForm(formData) {
    const errors = [];

    if (!formData.ho_ten || formData.ho_ten.length < 2) {
        errors.push('Name must be at least 2 characters');
    }

    if (!formData.email || !isValidEmail(formData.email)) {
        errors.push('Valid email is required');
    }

    return {
        isValid: errors.length === 0,
        errors
    };
}
```

### DOM Manipulation Standards
```javascript
// Use semantic selectors
class DOMUtils {
    static querySelector(selector) {
        const element = document.querySelector(selector);
        if (!element) {
            console.warn(`Element not found: ${selector}`);
        }
        return element;
    }

    static createElement(tag, attributes = {}, textContent = '') {
        const element = document.createElement(tag);

        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });

        if (textContent) {
            element.textContent = textContent;
        }

        return element;
    }

    static removeAllChildren(element) {
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
    }
}

// Use templates for complex HTML
function createCustomerCard(customer) {
    return `
        <div class="card mb-2" data-customer-id="${customer.id}">
            <div class="card-body">
                <h6 class="card-title">${escapeHtml(customer.ho_ten)}</h6>
                <p class="card-text">
                    <small class="text-muted">${escapeHtml(customer.email)}</small>
                </p>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-primary"
                            onclick="CustomerManager.edit(${customer.id})">
                        Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger"
                            onclick="CustomerManager.delete(${customer.id})">
                        Delete
                    </button>
                </div>
            </div>
        </div>
    `;
}

// XSS prevention
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

---

## 🗄️ Database Standards

### Table Design
```sql
-- Use descriptive, consistent naming
CREATE TABLE khach_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    so_dien_thoai VARCHAR(20),
    dia_chi TEXT,
    loai_khach VARCHAR(20) DEFAULT 'MOI',
    ghi_chu TEXT,
    tong_tien_da_mua DECIMAL(15,2) DEFAULT 0.00,
    so_don_thanh_cong INTEGER DEFAULT 0,
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create necessary indexes
CREATE INDEX idx_khach_hang_email ON khach_hang(email);
CREATE INDEX idx_khach_hang_loai ON khach_hang(loai_khach);
CREATE INDEX idx_khach_hang_ngay_tao ON khach_hang(ngay_tao);
```

### Query Standards
```python
# Use SQLAlchemy query patterns
# Good: Using ORM with proper filtering
customers = db.query(Customer).filter(
    Customer.loai_khach == LoaiKhachHang.VIP,
    Customer.ngay_tao >= start_date
).order_by(Customer.ngay_tao.desc()).limit(10).all()

# Good: Using proper joins
orders_with_customers = db.query(DonHang).join(
    KhachHang, DonHang.khach_hang_id == KhachHang.id
).filter(
    KhachHang.loai_khach == LoaiKhachHang.VIP
).all()

# Avoid: Raw SQL unless absolutely necessary
# If raw SQL needed, use parameterized queries
result = db.execute(
    text("SELECT * FROM khach_hang WHERE email = :email"),
    {"email": email}
)
```

---

## 🔌 API Design Standards

### RESTful Conventions
```
GET    /khach-hang/           # List customers
GET    /khach-hang/{id}       # Get specific customer
POST   /khach-hang/           # Create customer
PUT    /khach-hang/{id}       # Update customer
DELETE /khach-hang/{id}       # Delete customer

# Sub-resources
GET    /khach-hang/{id}/don-hang/  # Get customer's orders
POST   /khach-hang/{id}/cap-nhat-loai/  # Update customer type
```

### Request/Response Standards
```python
# Consistent request format
{
    "ho_ten": "Nguyen Van A",
    "email": "nguyenvana@email.com",
    "so_dien_thoai": "0909123456"
}

# Consistent response format
{
    "id": 1,
    "ho_ten": "Nguyen Van A",
    "email": "nguyenvana@email.com",
    "so_dien_thoai": "0909123456",
    "ngay_tao": "2025-09-23T10:30:00Z",
    "ngay_cap_nhat": "2025-09-23T10:30:00Z"
}

# Error response format
{
    "error": true,
    "error_code": "VALIDATION_ERROR",
    "message": "Email is required",
    "timestamp": "2025-09-23T10:30:00Z",
    "details": {
        "field": "email",
        "value": null
    }
}
```

### Status Code Usage
```python
# Use appropriate HTTP status codes
200 # OK - Successful GET, PUT
201 # Created - Successful POST
204 # No Content - Successful DELETE
400 # Bad Request - Invalid input
401 # Unauthorized - Authentication required
403 # Forbidden - Access denied
404 # Not Found - Resource doesn't exist
409 # Conflict - Resource conflict (duplicate email)
422 # Unprocessable Entity - Validation failed
500 # Internal Server Error - Server error
```

---

## 🧪 Testing Standards

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_models.py       # Model tests
│   ├── test_schemas.py      # Schema validation tests
│   └── test_utils.py        # Utility function tests
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   └── test_database.py
└── e2e/                     # End-to-end tests (future)
    └── test_user_flows.py
```

### Test Naming and Structure
```python
class TestCustomerAPI:
    """Test suite for customer API endpoints"""

    async def test_create_customer_success(self, async_client, db_session):
        """Test successful customer creation with valid data"""
        # Arrange
        customer_data = {
            "ho_ten": "Test Customer",
            "email": "test@example.com",
            "so_dien_thoai": "0909123456"
        }

        # Act
        response = await async_client.post("/khach-hang/", json=customer_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["ho_ten"] == customer_data["ho_ten"]
        assert data["email"] == customer_data["email"]
        assert "id" in data
        assert "ngay_tao" in data

    async def test_create_customer_duplicate_email(self, async_client, sample_customer):
        """Test customer creation fails with duplicate email"""
        # Arrange
        customer_data = {
            "ho_ten": "Another Customer",
            "email": sample_customer.email,  # Duplicate email
            "so_dien_thoai": "0909123457"
        }

        # Act
        response = await async_client.post("/khach-hang/", json=customer_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower()

    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "@example.com",
        "test@",
        "",
        None
    ])
    async def test_create_customer_invalid_email(self, async_client, invalid_email):
        """Test customer creation fails with invalid email formats"""
        customer_data = {
            "ho_ten": "Test Customer",
            "email": invalid_email,
        }

        response = await async_client.post("/khach-hang/", json=customer_data)
        assert response.status_code == 422
```

### Coverage Requirements
- **Unit Tests**: 85%+ coverage
- **Critical Paths**: 100% coverage
- **API Endpoints**: 100% coverage
- **Error Handling**: 100% coverage

---

## 📚 Documentation Standards

### Code Documentation
```python
def calculate_order_total(
    product_price: float,
    quantity: int,
    shipping_fee: float = 0.0,
    service_fee: float = 0.0
) -> float:
    """
    Calculate total order amount including all fees.

    Args:
        product_price: Unit price of the product in VND
        quantity: Number of items ordered
        shipping_fee: Shipping cost in VND (default: 0.0)
        service_fee: Service fee in VND (default: 0.0)

    Returns:
        Total order amount in VND

    Raises:
        ValueError: If any price or quantity is negative

    Example:
        >>> calculate_order_total(100000, 2, 50000, 20000)
        270000.0
    """
    if product_price < 0 or quantity < 0:
        raise ValueError("Price and quantity must be non-negative")

    subtotal = product_price * quantity
    total = subtotal + shipping_fee + service_fee

    return total
```

### API Documentation
```python
@app.post("/khach-hang/", response_model=schemas.Customer)
async def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer in the system.

    This endpoint creates a new customer with the provided information.
    Email must be unique across all customers.

    - **ho_ten**: Customer's full name (2-100 characters)
    - **email**: Valid email address (unique)
    - **so_dien_thoai**: Phone number (optional, max 20 chars)
    - **loai_khach**: Customer type (default: MOI)

    Returns the created customer with assigned ID and timestamps.
    """
```

---

## 🔄 Git Workflow

### Branch Naming
```bash
# Feature branches
feature/customer-management
feature/order-tracking
feature/api-authentication

# Bug fixes
bugfix/email-validation
bugfix/order-total-calculation

# Hotfixes
hotfix/security-patch
hotfix/critical-bug-fix

# Release branches
release/v1.0.0
release/v1.1.0
```

### Commit Messages
```bash
# Format: <type>(<scope>): <description>
# Types: feat, fix, docs, style, refactor, test, chore

feat(api): add customer type auto-update endpoint
fix(frontend): resolve pagination bug in product list
docs(api): update authentication documentation
test(orders): add integration tests for order creation
refactor(database): optimize customer query performance
style(frontend): improve mobile responsive design
chore(deps): update FastAPI to version 0.104.0

# Breaking changes
feat(api)!: change customer schema structure

BREAKING CHANGE: Customer schema now requires 'loai_khach' field
```

### Pull Request Template
```markdown
## Description
Brief description of changes made

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes without version bump
```

---

## 👀 Code Review Guidelines

### Review Checklist

**Functionality:**
- [ ] Does the code do what it's supposed to do?
- [ ] Are edge cases handled?
- [ ] Is error handling appropriate?
- [ ] Are there any potential performance issues?

**Code Quality:**
- [ ] Is the code readable and well-structured?
- [ ] Are naming conventions followed?
- [ ] Is the code DRY (Don't Repeat Yourself)?
- [ ] Are functions and classes appropriately sized?

**Testing:**
- [ ] Are there adequate tests?
- [ ] Do tests cover edge cases?
- [ ] Are tests readable and maintainable?

**Security:**
- [ ] Are there any security vulnerabilities?
- [ ] Is input validation adequate?
- [ ] Are secrets properly handled?

**Documentation:**
- [ ] Is code documented appropriately?
- [ ] Are API changes documented?
- [ ] Are breaking changes clearly marked?

### Review Comments
```markdown
# Constructive feedback format

## Issues
1. **Security**: This endpoint is missing input validation
   ```python
   # Current code
   def create_user(email):
       # No validation

   # Suggested fix
   def create_user(email: EmailStr):
       if not email:
           raise ValidationError("Email is required")
   ```

2. **Performance**: Consider adding database index for frequent queries
   ```sql
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   ```

## Suggestions
- Consider extracting this logic into a separate utility function
- This could be simplified using list comprehension

## Praise
- Great error handling implementation
- Clean and readable code structure
```

---

## 🔧 Tools and Automation

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

### IDE Configuration

**VS Code Settings (.vscode/settings.json):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

---

## 📊 Quality Metrics

### Code Quality Goals
- **Test Coverage**: ≥85%
- **Code Complexity**: Cyclomatic complexity ≤10
- **Documentation**: All public APIs documented
- **Performance**: API response time <200ms (95th percentile)
- **Security**: No critical vulnerabilities

### Monitoring and Reporting
```bash
# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Code complexity analysis
flake8 --max-complexity=10 .

# Security scan
bandit -r .

# Performance testing
pytest tests/performance/ --benchmark-only
```

---

## 🚀 Continuous Improvement

### Regular Reviews
- **Weekly**: Code review metrics
- **Monthly**: Test coverage analysis
- **Quarterly**: Architecture review
- **Annually**: Technology stack evaluation

### Learning and Development
- Stay updated with FastAPI best practices
- Follow Python community standards (PEPs)
- Participate in code review discussions
- Share knowledge through documentation

---

*These standards are living documents and should be updated as the project evolves.*

**Last updated**: September 23, 2025