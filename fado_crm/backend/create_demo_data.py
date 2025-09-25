# -*- coding: utf-8 -*-
# FADO CRM Demo Data Creator - Tao du lieu mau sieu cool!
# Script nay se tao du lieu demo de test he thong nhu mot pro!

import sys
import os

# Thiet lap UTF-8 encoding cho Windows
if os.name == 'nt':  # Windows
    os.system('chcp 65001 > nul')
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from database import engine, create_tables
from models import *

# 🏭 Tạo session
Session = sessionmaker(bind=engine)

def create_demo_customers():
    """Tao khach hang demo voi data that nhu the"""
    session = Session()

    customers_data = [
        {
            "ho_ten": "Nguyễn Văn Anh",
            "email": "nguyenvananh@gmail.com",
            "so_dien_thoai": "0987654321",
            "dia_chi": "123 Đường ABC, Quận 1, TP.HCM",
            "loai_khach": LoaiKhachHang.VIP,
            "tong_tien_da_mua": 50000000.0,
            "so_don_thanh_cong": 15,
            "ghi_chu": "Khách VIP từ 2022, rất uy tín"
        },
        {
            "ho_ten": "Trần Thị Bình",
            "email": "tranthibinh@yahoo.com",
            "so_dien_thoai": "0912345678",
            "dia_chi": "456 Đường XYZ, Quận 3, TP.HCM",
            "loai_khach": LoaiKhachHang.THAN_THIET,
            "tong_tien_da_mua": 25000000.0,
            "so_don_thanh_cong": 8,
            "ghi_chu": "Khách thường xuyên mua mỹ phẩm"
        },
        {
            "ho_ten": "Lê Minh Cường",
            "email": "leminhcuong@hotmail.com",
            "so_dien_thoai": "0909123456",
            "dia_chi": "789 Đường DEF, Quận 7, TP.HCM",
            "loai_khach": LoaiKhachHang.MOI,
            "tong_tien_da_mua": 3500000.0,
            "so_don_thanh_cong": 2,
            "ghi_chu": "Khách mới, quan tâm đến đồ công nghệ"
        },
        {
            "ho_ten": "Phạm Thu Hà",
            "email": "phamthuha@gmail.com",
            "so_dien_thoai": "0976543210",
            "dia_chi": "321 Đường GHI, Quận Bình Thạnh, TP.HCM",
            "loai_khach": LoaiKhachHang.THAN_THIET,
            "tong_tien_da_mua": 18000000.0,
            "so_don_thanh_cong": 6,
            "ghi_chu": "Thích mua quần áo và phụ kiện"
        },
        {
            "ho_ten": "Hoàng Văn Đức",
            "email": "hoangvanduc@gmail.com",
            "so_dien_thoai": "0931234567",
            "dia_chi": "654 Đường JKL, Quận 2, TP.HCM",
            "loai_khach": LoaiKhachHang.MOI,
            "tong_tien_da_mua": 1200000.0,
            "so_don_thanh_cong": 1,
            "ghi_chu": "Khách mới, lần đầu mua hộ"
        }
    ]

    customers = []
    for data in customers_data:
        customer = KhachHang(**data)
        session.add(customer)
        customers.append(customer)

    session.commit()
    print(f"✅ Đã tạo {len(customers)} khách hàng demo!")
    return customers

def create_demo_products():
    """📦 Tạo sản phẩm demo với đa dạng loại hàng"""
    session = Session()

    products_data = [
        {
            "ten_san_pham": "iPhone 15 Pro Max 256GB",
            "link_goc": "https://www.apple.com/iphone-15-pro/",
            "gia_goc": 1199.0,
            "gia_ban": 32000000.0,
            "mo_ta": "iPhone mới nhất với chip A17 Pro, camera titanium",
            "hinh_anh_url": "https://example.com/iphone15.jpg",
            "trong_luong": 0.2,
            "kich_thuoc": "159.9 x 76.7 x 8.25 mm",
            "danh_muc": "Điện thoại",
            "quoc_gia_nguon": "Mỹ"
        },
        {
            "ten_san_pham": "Nike Air Jordan 1 High",
            "link_goc": "https://www.nike.com/air-jordan-1",
            "gia_goc": 170.0,
            "gia_ban": 4500000.0,
            "mo_ta": "Giày sneaker iconic của Jordan Brand",
            "hinh_anh_url": "https://example.com/jordan1.jpg",
            "trong_luong": 0.8,
            "kich_thuoc": "Size 42",
            "danh_muc": "Giày dép",
            "quoc_gia_nguon": "Mỹ"
        },
        {
            "ten_san_pham": "Chanel No.5 Eau de Parfum",
            "link_goc": "https://www.chanel.com/perfume",
            "gia_goc": 132.0,
            "gia_ban": 3800000.0,
            "mo_ta": "Nước hoa iconic của Chanel, mùi hương sang trọng",
            "hinh_anh_url": "https://example.com/chanel5.jpg",
            "trong_luong": 0.1,
            "kich_thuoc": "50ml",
            "danh_muc": "Mỹ phẩm",
            "quoc_gia_nguon": "Pháp"
        },
        {
            "ten_san_pham": "MacBook Pro M3 14 inch",
            "link_goc": "https://www.apple.com/macbook-pro-14/",
            "gia_goc": 1999.0,
            "gia_ban": 52000000.0,
            "mo_ta": "Laptop Pro với chip M3, hiệu năng đỉnh cao",
            "hinh_anh_url": "https://example.com/macbook.jpg",
            "trong_luong": 1.6,
            "kich_thuoc": "31.26 x 22.12 x 1.55 cm",
            "danh_muc": "Laptop",
            "quoc_gia_nguon": "Mỹ"
        },
        {
            "ten_san_pham": "Louis Vuitton Speedy 30",
            "link_goc": "https://us.louisvuitton.com/speedy-30",
            "gia_goc": 1570.0,
            "gia_ban": 42000000.0,
            "mo_ta": "Túi xách nữ iconic của LV, da monogram",
            "hinh_anh_url": "https://example.com/lvspeedy.jpg",
            "trong_luong": 0.5,
            "kich_thuoc": "30 x 21 x 17 cm",
            "danh_muc": "Túi xách",
            "quoc_gia_nguon": "Pháp"
        },
        {
            "ten_san_pham": "Sony WH-1000XM5 Headphones",
            "link_goc": "https://www.sony.com/headphones",
            "gia_goc": 399.0,
            "gia_ban": 10500000.0,
            "mo_ta": "Tai nghe chống ồn tốt nhất thế giới",
            "hinh_anh_url": "https://example.com/sony.jpg",
            "trong_luong": 0.25,
            "kich_thuoc": "Foldable design",
            "danh_muc": "Âm thanh",
            "quoc_gia_nguon": "Nhật Bản"
        }
    ]

    products = []
    for data in products_data:
        product = SanPham(**data)
        session.add(product)
        products.append(product)

    session.commit()
    print(f"✅ Đã tạo {len(products)} sản phẩm demo!")
    return products

def create_demo_orders(customers, products):
    """📋 Tạo đơn hàng demo với các trạng thái khác nhau"""
    session = Session()

    # Danh sách trạng thái để random
    statuses = list(TrangThaiDonHang)

    orders = []
    for i in range(10):
        # Random chọn khách hàng
        customer = random.choice(customers)

        # Random chọn 1-3 sản phẩm
        selected_products = random.sample(products, random.randint(1, 3))

        # Tính tổng giá sản phẩm
        tong_gia_san_pham = sum(p.gia_ban or 0 for p in selected_products)

        # Random các loại phí
        phi_mua_ho = tong_gia_san_pham * 0.05  # 5% phí mua hộ
        phi_van_chuyen = random.randint(200000, 800000)  # 200k-800k
        phi_khac = random.randint(0, 300000)  # 0-300k

        tong_tien = tong_gia_san_pham + phi_mua_ho + phi_van_chuyen + phi_khac

        # Tạo mã đơn hàng
        ma_don_hang = f"FD{datetime.now().strftime('%y%m%d')}{i+1:03d}"

        # Random thời gian tạo (trong 30 ngày qua)
        ngay_tao = datetime.now() - timedelta(days=random.randint(0, 30))

        order = DonHang(
            ma_don_hang=ma_don_hang,
            khach_hang_id=customer.id,
            tong_gia_san_pham=tong_gia_san_pham,
            phi_mua_ho=phi_mua_ho,
            phi_van_chuyen=phi_van_chuyen,
            phi_khac=phi_khac,
            tong_tien=tong_tien,
            trang_thai=random.choice(statuses),
            ngay_tao=ngay_tao,
            ngay_cap_nhat=ngay_tao + timedelta(hours=random.randint(1, 48)),
            ghi_chu_khach=f"Ghi chú từ khách hàng cho đơn {ma_don_hang}",
            ghi_chu_noi_bo=f"Ghi chú nội bộ cho đơn {ma_don_hang}"
        )

        session.add(order)
        session.flush()  # Để lấy ID của order

        # Tạo chi tiết đơn hàng
        for product in selected_products:
            chi_tiet = ChiTietDonHang(
                don_hang_id=order.id,
                san_pham_id=product.id,
                so_luong=random.randint(1, 2),
                gia_mua=product.gia_ban,
                ghi_chu=f"Chi tiết cho sản phẩm {product.ten_san_pham}"
            )
            session.add(chi_tiet)

        orders.append(order)

    session.commit()
    print(f"✅ Đã tạo {len(orders)} đơn hàng demo!")
    return orders

def create_demo_contact_history(customers):
    """📞 Tạo lịch sử liên hệ demo"""
    session = Session()

    contact_types = ["call", "sms", "email"]
    nhan_vien_list = ["Nguyễn Thị A", "Trần Văn B", "Lê Thị C", "Phạm Văn D"]

    contacts = []
    for i in range(20):
        customer = random.choice(customers)
        loai_lien_he = random.choice(contact_types)

        # Nội dung mẫu theo loại liên hệ
        noi_dung_mau = {
            "call": [
                "Gọi xác nhận đơn hàng, khách đồng ý thanh toán",
                "Tư vấn sản phẩm cho khách, giải đáp thắc mắc",
                "Thông báo hàng về kho, hẹn giao hàng",
                "Xử lý khiếu nại về chất lượng sản phẩm"
            ],
            "sms": [
                "Gửi SMS xác nhận đơn hàng và thông tin thanh toán",
                "Thông báo trạng thái đơn hàng qua SMS",
                "Gửi mã tracking cho khách theo dõi",
                "SMS nhắc nhở thanh toán đơn hàng"
            ],
            "email": [
                "Gửi email báo giá chi tiết cho khách hàng",
                "Email xác nhận đơn hàng và hướng dẫn thanh toán",
                "Gửi hóa đơn và thông tin giao hàng",
                "Email cảm ơn và khuyến mãi cho lần mua tiếp theo"
            ]
        }

        ket_qua_mau = [
            "Thành công, khách hài lòng",
            "Cần follow up thêm",
            "Khách yêu cầu thêm thông tin",
            "Đã giải quyết xong vấn đề",
            "Chuyển cho bộ phận khác xử lý"
        ]

        ngay_lien_he = datetime.now() - timedelta(days=random.randint(0, 30))

        contact = LichSuLienHe(
            khach_hang_id=customer.id,
            loai_lien_he=loai_lien_he,
            noi_dung=random.choice(noi_dung_mau[loai_lien_he]),
            nhan_vien_xu_ly=random.choice(nhan_vien_list),
            ket_qua=random.choice(ket_qua_mau),
            ngay_lien_he=ngay_lien_he
        )

        session.add(contact)
        contacts.append(contact)

    session.commit()
    print(f"✅ Đã tạo {len(contacts)} lịch sử liên hệ demo!")
    return contacts

def main():
    """🎯 Hàm chính - Tạo toàn bộ demo data"""
    print("🎭 FADO CRM Demo Data Creator")
    print("=" * 40)

    try:
        # 1. Tạo tables nếu chưa có
        print("🏗️ Đang tạo database tables...")
        create_tables()

        # 2. Tạo demo data
        print("👥 Đang tạo khách hàng demo...")
        customers = create_demo_customers()

        print("📦 Đang tạo sản phẩm demo...")
        products = create_demo_products()

        print("📋 Đang tạo đơn hàng demo...")
        orders = create_demo_orders(customers, products)

        print("📞 Đang tạo lịch sử liên hệ demo...")
        contacts = create_demo_contact_history(customers)

        print("\n" + "=" * 40)
        print("🎉 HOÀN THÀNH TẠO DEMO DATA!")
        print("=" * 40)
        print(f"👥 Khách hàng: {len(customers)}")
        print(f"📦 Sản phẩm: {len(products)}")
        print(f"📋 Đơn hàng: {len(orders)}")
        print(f"📞 Lịch sử liên hệ: {len(contacts)}")
        print("\n🚀 Giờ có thể khởi động server và test CRM!")

    except Exception as e:
        print(f"❌ Lỗi khi tạo demo data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()