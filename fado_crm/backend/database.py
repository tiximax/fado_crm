# 🗄️ FADO CRM - Database Connection Siêu Tốc!
# Code này nhanh như tia chớp và ổn định như một tảng đá! ⚡

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# 🚀 Database URL - Có thể dùng SQLite cho demo hoặc PostgreSQL cho production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fado_crm.db")

# 🔧 Tạo engine - Động cơ siêu mạnh của database!
engine = create_engine(
    DATABASE_URL,
    # Đặc biệt cho SQLite - enable foreign keys để database không bị lỗi
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 🏭 Session factory - Nhà máy tạo session như bánh quy!
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🎯 Dependency để lấy database session
def get_db():
    """
    🎪 Hàm magic để lấy database session!
    Dùng như dependency injection trong FastAPI - cực kỳ elegant!
    """
    db = SessionLocal()
    try:
        yield db  # 🎁 Trả về session như một món quà
    finally:
        db.close()  # 🚪 Luôn nhớ đóng cửa sau khi xong việc!

# 🏗️ Hàm tạo tất cả tables
def create_tables():
    """
    Tao tat ca bang trong database!
    Chay ham nay mot lan de setup database hoan chinh
    """
    print("Dang tao database tables...")
    Base.metadata.create_all(bind=engine)
    print("Hoan thanh! Database da san sang!")

# 🧹 Hàm xóa tất cả tables (cẩn thận khi dùng!)
def drop_tables():
    """
    NGUY HIEM! Ham nay xoa toan bo database!
    Chi dung khi muon reset lai tu dau
    """
    print("CANH BAO: Dang xoa tat ca tables...")
    Base.metadata.drop_all(bind=engine)
    print("Xong! Database da duoc reset!")

if __name__ == "__main__":
    # Chay script nay de tao database
    create_tables()