# Simple FastAPI Server for FADO CRM
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

# Basic imports
from database import get_db, create_tables
from models import KhachHang, SanPham, DonHang, ChiTietDonHang, NguoiDung
import schemas

# Auth imports
try:
    from auth import login_user, get_current_user, get_current_active_user
except ImportError as e:
    print(f"Warning: Could not import auth module: {e}")

# Create FastAPI app
app = FastAPI(
    title="FADO.VN CRM API",
    description="Customer Relationship Management System for FADO.VN",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

@app.get("/")
async def root():
    return {"message": "FADO CRM API is running!", "version": "2.0.0"}

@app.get("/dashboard")
async def dashboard(db: Session = Depends(get_db)):
    try:
        total_customers = db.query(KhachHang).count()
        total_products = db.query(SanPham).count()
        total_orders = db.query(DonHang).count()
        total_users = db.query(NguoiDung).count()

        return {
            "total_customers": total_customers,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_users": total_users,
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Login endpoint
@app.post("/auth/login")
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        result = login_user(db, login_data.email, login_data.password)
        if result:
            return result
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

# Get current user
@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_active_user)):
    return current_user

# Basic CRUD endpoints
@app.get("/khach-hang/")
async def get_customers(db: Session = Depends(get_db)):
    customers = db.query(KhachHang).all()
    return customers

@app.get("/san-pham/")
async def get_products(db: Session = Depends(get_db)):
    products = db.query(SanPham).all()
    return products

@app.get("/don-hang/")
async def get_orders(db: Session = Depends(get_db)):
    orders = db.query(DonHang).all()
    return orders

if __name__ == "__main__":
    print("Starting FADO CRM Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)