"""
FADO CRM - Stable Production Version
Core functionality only với minimal dependencies
"""

import os
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Database setup
DATABASE_URL = "sqlite:///./fado_crm_stable.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    so_dien_thoai = Column(String(20))
    dia_chi = Column(Text)
    loai_khach_hang = Column(String(20), default="Mới")
    ngay_tao = Column(DateTime, default=datetime.now)
    trang_thai = Column(Boolean, default=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    ten_san_pham = Column(String(200), nullable=False)
    mo_ta = Column(Text)
    gia_goc = Column(Float, default=0)
    gia_ban = Column(Float, default=0)
    danh_muc = Column(String(100))
    xuat_xu = Column(String(100))
    link_goc = Column(String(500))
    hinh_anh = Column(String(500))
    ngay_tao = Column(DateTime, default=datetime.now)
    trang_thai = Column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    ma_don_hang = Column(String(50), unique=True, index=True)
    khach_hang_id = Column(Integer, nullable=False)
    tong_tien = Column(Float, default=0)
    trang_thai = Column(String(50), default="Chờ xác nhận")
    ngay_tao = Column(DateTime, default=datetime.now)
    ghi_chu = Column(Text)


# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic schemas
class CustomerCreate(BaseModel):
    ho_ten: str
    email: str
    so_dien_thoai: Optional[str] = None
    dia_chi: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    ho_ten: str
    email: str
    so_dien_thoai: Optional[str]
    dia_chi: Optional[str]
    loai_khach_hang: str
    ngay_tao: datetime
    trang_thai: bool


class ProductCreate(BaseModel):
    ten_san_pham: str
    mo_ta: Optional[str] = None
    gia_goc: float = 0
    gia_ban: float = 0
    danh_muc: Optional[str] = None
    xuat_xu: Optional[str] = None
    link_goc: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    ten_san_pham: str
    mo_ta: Optional[str]
    gia_goc: float
    gia_ban: float
    danh_muc: Optional[str]
    xuat_xu: Optional[str]
    link_goc: Optional[str]
    hinh_anh: Optional[str]
    ngay_tao: datetime
    trang_thai: bool


class OrderCreate(BaseModel):
    khach_hang_id: int
    tong_tien: float = 0
    ghi_chu: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    ma_don_hang: str
    khach_hang_id: int
    tong_tien: float
    trang_thai: str
    ngay_tao: datetime
    ghi_chu: Optional[str]


# FastAPI app
app = FastAPI(
    title="FADO CRM - Stable Version",
    description="Production-ready core CRM functionality",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Root endpoint
@app.get("/")
async def root():
    return {"message": "FADO CRM Stable Version", "status": "running", "version": "1.0.0"}


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "database": "connected"}


# Dashboard stats
@app.get("/api/dashboard/stats")
async def dashboard_stats(db: Session = Depends(get_db)):
    try:
        customer_count = db.query(Customer).filter(Customer.trang_thai == True).count()
        product_count = db.query(Product).filter(Product.trang_thai == True).count()
        order_count = db.query(Order).count()

        return {
            "customers": customer_count,
            "products": product_count,
            "orders": order_count,
            "revenue": db.query(Order).count() * 1000,  # Mock revenue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Customer endpoints
@app.get("/api/customers", response_model=List[CustomerResponse])
async def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = (
        db.query(Customer).filter(Customer.trang_thai == True).offset(skip).limit(limit).all()
    )
    return customers


@app.post("/api/customers", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.put("/api/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)
):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in customer.dict().items():
        setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.trang_thai = False
    db.commit()
    return {"message": "Customer deleted successfully"}


# Product endpoints
@app.get("/api/products", response_model=List[ProductResponse])
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.trang_thai == True).offset(skip).limit(limit).all()
    return products


@app.post("/api/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.dict().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.trang_thai = False
    db.commit()
    return {"message": "Product deleted successfully"}


# Order endpoints
@app.get("/api/orders", response_model=List[OrderResponse])
async def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders


@app.post("/api/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Generate unique order code
    order_count = db.query(Order).count() + 1
    ma_don_hang = f"DH{order_count:06d}"

    db_order = Order(ma_don_hang=ma_don_hang, **order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/api/orders/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, order: OrderCreate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in order.dict().items():
        if key != "ma_don_hang":  # Don't update order code
            setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order


@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}


# Order status update
@app.patch("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    valid_statuses = [
        "Chờ xác nhận",
        "Đã xác nhận",
        "Đang mua",
        "Đã mua",
        "Đang ship",
        "Đã nhận",
        "Hoàn thành",
    ]

    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    order.trang_thai = status
    db.commit()

    return {"message": f"Order status updated to {status}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
