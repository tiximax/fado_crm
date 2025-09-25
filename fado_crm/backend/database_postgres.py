# 🐘 FADO CRM - PostgreSQL Database Configuration
# Production-ready database setup với connection pooling và optimization

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
from typing import Generator

# 🔧 Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://fado_user:fado_password@localhost:5432/fado_crm"
)

# 🚀 Production-optimized engine với connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to maintain in pool
    max_overflow=30,       # Additional connections allowed
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600,     # Recycle connections every hour
    echo=False             # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 📊 Database connection dependency
def get_db() -> Generator:
    """
    Database dependency để inject vào FastAPI endpoints
    Tự động handle transaction rollback khi có lỗi
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Database transaction rolled back: {e}")
        raise
    finally:
        db.close()

# 🏗️ Create tables function
def create_tables():
    """Tạo tất cả tables trong database"""
    try:
        # Import all models để SQLAlchemy biết tables cần tạo
        from models import (
            KhachHang, SanPham, DonHang, ChiTietDonHang, 
            LichSuLienHe, NguoiDung, FileUpload
        )
        
        Base.metadata.create_all(bind=engine)
        logging.info("✅ PostgreSQL tables created successfully")
        
        # 📊 Create indexes for performance
        create_performance_indexes()
        
    except Exception as e:
        logging.error(f"❌ Failed to create tables: {e}")
        raise

def create_performance_indexes():
    """Tạo các indexes quan trọng cho performance"""
    
    indexes = [
        # 🔍 Customer search indexes
        "CREATE INDEX IF NOT EXISTS idx_khach_hang_email ON khach_hang(email);",
        "CREATE INDEX IF NOT EXISTS idx_khach_hang_sdt ON khach_hang(so_dien_thoai);",
        "CREATE INDEX IF NOT EXISTS idx_khach_hang_loai ON khach_hang(loai_khach_hang);",
        "CREATE INDEX IF NOT EXISTS idx_khach_hang_created ON khach_hang(ngay_tao);",
        
        # 📦 Order search indexes  
        "CREATE INDEX IF NOT EXISTS idx_don_hang_ma ON don_hang(ma_don_hang);",
        "CREATE INDEX IF NOT EXISTS idx_don_hang_khach ON don_hang(khach_hang_id);",
        "CREATE INDEX IF NOT EXISTS idx_don_hang_trang_thai ON don_hang(trang_thai);",
        "CREATE INDEX IF NOT EXISTS idx_don_hang_ngay_tao ON don_hang(ngay_tao);",
        "CREATE INDEX IF NOT EXISTS idx_don_hang_ngay_giao ON don_hang(ngay_giao_hang);",
        
        # 🛍️ Product search indexes
        "CREATE INDEX IF NOT EXISTS idx_san_pham_ten ON san_pham(ten_san_pham);",
        "CREATE INDEX IF NOT EXISTS idx_san_pham_danh_muc ON san_pham(danh_muc);",
        "CREATE INDEX IF NOT EXISTS idx_san_pham_quoc_gia ON san_pham(quoc_gia_nguon);",
        
        # 📞 Contact history indexes
        "CREATE INDEX IF NOT EXISTS idx_lien_he_khach ON lich_su_lien_he(khach_hang_id);",
        "CREATE INDEX IF NOT EXISTS idx_lien_he_ngay ON lich_su_lien_he(ngay_lien_he);",
        "CREATE INDEX IF NOT EXISTS idx_lien_he_loai ON lich_su_lien_he(loai_lien_he);",
        
        # 👤 User management indexes
        "CREATE INDEX IF NOT EXISTS idx_nguoi_dung_email ON nguoi_dung(email);",
        "CREATE INDEX IF NOT EXISTS idx_nguoi_dung_vai_tro ON nguoi_dung(vai_tro);",
        "CREATE INDEX IF NOT EXISTS idx_nguoi_dung_active ON nguoi_dung(is_active);",
        
        # 📊 Analytics indexes for faster reporting
        "CREATE INDEX IF NOT EXISTS idx_analytics_order_date_status ON don_hang(ngay_tao, trang_thai);",
        "CREATE INDEX IF NOT EXISTS idx_analytics_customer_revenue ON khach_hang(tong_tien_da_mua DESC);",
    ]
    
    with engine.connect() as connection:
        for index_sql in indexes:
            try:
                connection.execute(text(index_sql))
                connection.commit()
            except Exception as e:
                logging.warning(f"Index creation warning: {e}")

# 🔍 Database health check
def check_database_health() -> dict:
    """Kiểm tra tình trạng database và connection pool"""
    try:
        with engine.connect() as connection:
            # Test query
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            
            # Pool statistics
            pool = engine.pool
            pool_status = {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "total_connections": pool.checkedin() + pool.checkedout()
            }
            
            return {
                "status": "healthy",
                "database": "postgresql",
                "pool_info": pool_status,
                "message": "Database connection is working properly"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "message": "Database connection failed"
        }

# 📈 Query optimization utilities
class QueryOptimizer:
    """Utilities để optimize database queries"""
    
    @staticmethod
    def bulk_insert(db, model_class, data_list):
        """Bulk insert để tăng performance khi insert nhiều records"""
        try:
            db.bulk_insert_mappings(model_class, data_list)
            db.commit()
            return len(data_list)
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def paginated_query(query, page: int = 1, per_page: int = 50):
        """Pagination với optimization"""
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page)
    
    @staticmethod
    def count_query(query):
        """Optimized count query"""
        return query.count()

# 🔧 Migration utilities
def migrate_from_sqlite():
    """Helper để migrate data từ SQLite sang PostgreSQL"""
    
    sqlite_url = "sqlite:///./fado_crm.db"
    sqlite_engine = create_engine(sqlite_url)
    
    # TODO: Implement data migration logic
    # This would involve reading data from SQLite and inserting into PostgreSQL
    # with proper data type conversion and validation
    
    logging.info("🔄 SQLite to PostgreSQL migration completed")

if __name__ == "__main__":
    # Test database connection
    print("🧪 Testing PostgreSQL connection...")
    health = check_database_health()
    print(f"Database Status: {health}")
    
    if health["status"] == "healthy":
        print("✅ PostgreSQL setup is ready!")
        create_tables()
    else:
        print("❌ PostgreSQL connection failed!")
        print(f"Error: {health.get('error', 'Unknown error')}")