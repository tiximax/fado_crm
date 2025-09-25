# FADO CRM Complete Server with Full CRUD Operations
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc, text
from typing import List, Optional
import uvicorn
from datetime import datetime

# Basic imports
from database import get_db, create_tables
from models import KhachHang, SanPham, DonHang, ChiTietDonHang, NguoiDung, TrangThaiDonHang, LoaiKhachHang
import schemas

# Auth imports
try:
    from auth import login_user, get_current_user, get_current_active_user
except ImportError as e:
    print(f"Warning: Could not import auth module: {e}")
    get_current_active_user = None

# Create FastAPI app
app = FastAPI(
    title="FADO.VN CRM Complete API",
    description="Full-featured Customer Relationship Management System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Helper function for pagination
def paginate_query(query, page: int = 1, per_page: int = 10):
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    # Convert SQLAlchemy objects to dictionaries
    serialized_items = []
    for item in items:
        item_dict = {}
        for column in item.__table__.columns:
            value = getattr(item, column.name)
            # Handle datetime objects
            if isinstance(value, datetime):
                value = value.isoformat()
            # Handle enum values
            elif hasattr(value, 'value'):
                value = value.value
            item_dict[column.name] = value
        serialized_items.append(item_dict)

    return {
        "items": serialized_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }

@app.get("/")
async def root():
    return {
        "message": "FADO CRM Complete API is running!",
        "version": "1.0.0",
        "features": ["Full CRUD", "Advanced Search", "Pagination", "Authentication"]
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected", "timestamp": datetime.utcnow()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow()}

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

# Authentication endpoints
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

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_active_user) if get_current_active_user else None):
    if current_user:
        return current_user
    else:
        raise HTTPException(status_code=401, detail="Authentication required")

# ===== KHÁCH HÀNG ENDPOINTS =====

@app.get("/khach-hang/", response_model=dict)
async def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    loai_khach: Optional[LoaiKhachHang] = Query(None, description="Filter by customer type"),
    sort_by: Optional[str] = Query("ngay_tao", description="Sort field"),
    order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(KhachHang)

        # Search filter
        if search:
            query = query.filter(
                or_(
                    KhachHang.ho_ten.ilike(f"%{search}%"),
                    KhachHang.email.ilike(f"%{search}%"),
                    KhachHang.so_dien_thoai.ilike(f"%{search}%")
                )
            )

        # Customer type filter
        if loai_khach:
            query = query.filter(KhachHang.loai_khach == loai_khach)

        # Sorting
        if hasattr(KhachHang, sort_by):
            sort_column = getattr(KhachHang, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        return paginate_query(query, page, per_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customers: {str(e)}")

@app.post("/khach-hang/", response_model=schemas.KhachHang)
async def create_customer(
    customer: schemas.KhachHangCreate,
    db: Session = Depends(get_db)
):
    try:
        # Check if email already exists
        existing = db.query(KhachHang).filter(KhachHang.email == customer.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already exists")

        db_customer = KhachHang(
            ho_ten=customer.ho_ten,
            email=customer.email,
            so_dien_thoai=customer.so_dien_thoai,
            dia_chi=customer.dia_chi,
            loai_khach=customer.loai_khach,
            ghi_chu=customer.ghi_chu,
            ngay_tao=datetime.utcnow()
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        db.rollback()
        if "Email already exists" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error creating customer: {str(e)}")

@app.get("/khach-hang/{customer_id}", response_model=schemas.KhachHang)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(KhachHang).filter(KhachHang.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/khach-hang/{customer_id}", response_model=schemas.KhachHang)
async def update_customer(
    customer_id: int,
    customer_update: schemas.KhachHangUpdate,
    db: Session = Depends(get_db)
):
    try:
        db_customer = db.query(KhachHang).filter(KhachHang.id == customer_id).first()
        if not db_customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Check email uniqueness if email is being updated
        if customer_update.email and customer_update.email != db_customer.email:
            existing = db.query(KhachHang).filter(
                KhachHang.email == customer_update.email,
                KhachHang.id != customer_id
            ).first()
            if existing:
                raise HTTPException(status_code=409, detail="Email already exists")

        # Update fields
        update_data = customer_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)

        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        db.rollback()
        if "not found" in str(e) or "already exists" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error updating customer: {str(e)}")

@app.delete("/khach-hang/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        db_customer = db.query(KhachHang).filter(KhachHang.id == customer_id).first()
        if not db_customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Check if customer has orders
        orders = db.query(DonHang).filter(DonHang.khach_hang_id == customer_id).first()
        if orders:
            raise HTTPException(status_code=409, detail="Cannot delete customer with existing orders")

        db.delete(db_customer)
        db.commit()
        return {"message": "Customer deleted successfully", "id": customer_id}
    except Exception as e:
        db.rollback()
        if "not found" in str(e) or "Cannot delete" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error deleting customer: {str(e)}")

# ===== SẢN PHẨM ENDPOINTS =====

@app.get("/san-pham/", response_model=dict)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by product name"),
    danh_muc: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    sort_by: Optional[str] = Query("ngay_tao", description="Sort field"),
    order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(SanPham).filter(SanPham.is_active == True)

        # Search filter
        if search:
            query = query.filter(
                or_(
                    SanPham.ten_san_pham.ilike(f"%{search}%"),
                    SanPham.mo_ta.ilike(f"%{search}%")
                )
            )

        # Category filter
        if danh_muc:
            query = query.filter(SanPham.danh_muc.ilike(f"%{danh_muc}%"))

        # Price range filter
        if min_price is not None:
            query = query.filter(SanPham.gia_ban >= min_price)
        if max_price is not None:
            query = query.filter(SanPham.gia_ban <= max_price)

        # Sorting
        if hasattr(SanPham, sort_by):
            sort_column = getattr(SanPham, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        return paginate_query(query, page, per_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@app.post("/san-pham/", response_model=schemas.SanPham)
async def create_product(
    product: schemas.SanPhamCreate,
    db: Session = Depends(get_db)
):
    try:
        db_product = SanPham(
            ten_san_pham=product.ten_san_pham,
            link_goc=product.link_goc,
            gia_goc=product.gia_goc,
            gia_ban=product.gia_ban,
            mo_ta=product.mo_ta,
            hinh_anh_url=product.hinh_anh_url,
            trong_luong=product.trong_luong,
            kich_thuoc=product.kich_thuoc,
            danh_muc=product.danh_muc,
            quoc_gia_nguon=product.quoc_gia_nguon,
            ngay_tao=datetime.utcnow(),
            is_active=True
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

@app.get("/san-pham/{product_id}", response_model=schemas.SanPham)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(SanPham).filter(SanPham.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/san-pham/{product_id}", response_model=schemas.SanPham)
async def update_product(
    product_id: int,
    product_update: schemas.SanPhamUpdate,
    db: Session = Depends(get_db)
):
    try:
        db_product = db.query(SanPham).filter(SanPham.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update fields
        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)

        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        if "not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")

@app.delete("/san-pham/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    try:
        db_product = db.query(SanPham).filter(SanPham.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Soft delete - mark as inactive
        db_product.is_active = False
        db.commit()
        return {"message": "Product deleted successfully (soft delete)", "id": product_id}
    except Exception as e:
        db.rollback()
        if "not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")

# ===== ĐƠN HÀNG ENDPOINTS =====

@app.get("/don-hang/", response_model=dict)
async def get_orders(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by order code or customer"),
    trang_thai: Optional[TrangThaiDonHang] = Query(None, description="Filter by status"),
    khach_hang_id: Optional[int] = Query(None, description="Filter by customer ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("ngay_tao", description="Sort field"),
    order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(DonHang).join(KhachHang)

        # Search filter
        if search:
            query = query.filter(
                or_(
                    DonHang.ma_don_hang.ilike(f"%{search}%"),
                    KhachHang.ho_ten.ilike(f"%{search}%")
                )
            )

        # Status filter
        if trang_thai:
            query = query.filter(DonHang.trang_thai == trang_thai)

        # Customer filter
        if khach_hang_id:
            query = query.filter(DonHang.khach_hang_id == khach_hang_id)

        # Date range filter
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(DonHang.ngay_tao >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(DonHang.ngay_tao <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

        # Sorting
        if hasattr(DonHang, sort_by):
            sort_column = getattr(DonHang, sort_by)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        return paginate_query(query, page, per_page)
    except Exception as e:
        if "Invalid" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")

@app.get("/don-hang/{order_id}", response_model=schemas.DonHang)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(DonHang).filter(DonHang.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/don-hang/{order_id}", response_model=schemas.DonHang)
async def update_order(
    order_id: int,
    order_update: schemas.DonHangUpdate,
    db: Session = Depends(get_db)
):
    try:
        db_order = db.query(DonHang).filter(DonHang.id == order_id).first()
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Update fields
        update_data = order_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)

        # Update timestamp
        db_order.ngay_cap_nhat = datetime.utcnow()

        # Recalculate total if cost components changed
        if any(field in update_data for field in ['tong_gia_san_pham', 'phi_mua_ho', 'phi_van_chuyen', 'phi_khac']):
            db_order.tong_tien = (
                (db_order.tong_gia_san_pham or 0) +
                (db_order.phi_mua_ho or 0) +
                (db_order.phi_van_chuyen or 0) +
                (db_order.phi_khac or 0)
            )

        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        if "not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error updating order: {str(e)}")

@app.put("/don-hang/{order_id}/trang-thai")
async def update_order_status(
    order_id: int,
    trang_thai: TrangThaiDonHang,
    db: Session = Depends(get_db)
):
    try:
        db_order = db.query(DonHang).filter(DonHang.id == order_id).first()
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")

        db_order.trang_thai = trang_thai
        db_order.ngay_cap_nhat = datetime.utcnow()

        db.commit()
        return {
            "message": "Order status updated successfully",
            "order_id": order_id,
            "new_status": trang_thai.value
        }
    except Exception as e:
        db.rollback()
        if "not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error updating order status: {str(e)}")

if __name__ == "__main__":
    print("Starting FADO CRM Complete Server...")
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)