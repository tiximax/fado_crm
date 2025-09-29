# -*- coding: utf-8 -*-
"""
FADO CRM - Database Optimization
Performance tuning and indexing strategy
"""

import logging

from backend.database import engine
from backend.models import *
from sqlalchemy import Index, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database performance optimization utilities"""

    def __init__(self):
        self.optimization_indexes = [
            # KhachHang table optimizations
            {
                "name": "idx_khach_hang_loai_khach",
                "table": "khach_hang",
                "columns": ["loai_khach"],
                "reason": "Filter customers by type (common in dashboard & reports)",
            },
            {
                "name": "idx_khach_hang_ngay_tao",
                "table": "khach_hang",
                "columns": ["ngay_tao"],
                "reason": "Date range filtering for new customer reports",
            },
            {
                "name": "idx_khach_hang_tong_tien",
                "table": "khach_hang",
                "columns": ["tong_tien_da_mua"],
                "reason": "Sort by purchase amount, VIP customer identification",
            },
            {
                "name": "idx_khach_hang_search",
                "table": "khach_hang",
                "columns": ["ho_ten", "email"],
                "reason": "Composite index for customer search functionality",
            },
            # DonHang table optimizations
            {
                "name": "idx_don_hang_trang_thai",
                "table": "don_hang",
                "columns": ["trang_thai"],
                "reason": "Filter orders by status (most common query)",
            },
            {
                "name": "idx_don_hang_khach_hang_id",
                "table": "don_hang",
                "columns": ["khach_hang_id"],
                "reason": "Foreign key lookup for customer orders",
            },
            {
                "name": "idx_don_hang_ngay_tao",
                "table": "don_hang",
                "columns": ["ngay_tao"],
                "reason": "Date range filtering for order reports",
            },
            {
                "name": "idx_don_hang_customer_status",
                "table": "don_hang",
                "columns": ["khach_hang_id", "trang_thai"],
                "reason": "Composite index for customer order status queries",
            },
            {
                "name": "idx_don_hang_date_status",
                "table": "don_hang",
                "columns": ["ngay_tao", "trang_thai"],
                "reason": "Dashboard queries: orders by date and status",
            },
            # SanPham table optimizations
            {
                "name": "idx_san_pham_danh_muc",
                "table": "san_pham",
                "columns": ["danh_muc"],
                "reason": "Filter products by category",
            },
            {
                "name": "idx_san_pham_active",
                "table": "san_pham",
                "columns": ["is_active"],
                "reason": "Filter active products (most queries only want active ones)",
            },
            {
                "name": "idx_san_pham_gia_ban",
                "table": "san_pham",
                "columns": ["gia_ban"],
                "reason": "Price range filtering and sorting",
            },
            {
                "name": "idx_san_pham_search_active",
                "table": "san_pham",
                "columns": ["ten_san_pham", "is_active"],
                "reason": "Product search with active filter",
            },
            # ChiTietDonHang table optimizations
            {
                "name": "idx_chi_tiet_don_hang_don_hang_id",
                "table": "chi_tiet_don_hang",
                "columns": ["don_hang_id"],
                "reason": "Foreign key lookup for order details",
            },
            {
                "name": "idx_chi_tiet_don_hang_san_pham_id",
                "table": "chi_tiet_don_hang",
                "columns": ["san_pham_id"],
                "reason": "Foreign key lookup for product order history",
            },
            # LichSuLienHe table optimizations
            {
                "name": "idx_lich_su_lien_he_khach_hang_id",
                "table": "lich_su_lien_he",
                "columns": ["khach_hang_id"],
                "reason": "Foreign key lookup for customer contact history",
            },
            {
                "name": "idx_lich_su_lien_he_ngay",
                "table": "lich_su_lien_he",
                "columns": ["ngay_lien_he"],
                "reason": "Date filtering for contact history reports",
            },
            {
                "name": "idx_lich_su_lien_he_loai",
                "table": "lich_su_lien_he",
                "columns": ["loai_lien_he"],
                "reason": "Filter contact history by type (call, email, sms)",
            },
            # NguoiDung table optimizations
            {
                "name": "idx_nguoi_dung_vai_tro",
                "table": "nguoi_dung",
                "columns": ["vai_tro"],
                "reason": "Filter users by role for admin functions",
            },
            {
                "name": "idx_nguoi_dung_active",
                "table": "nguoi_dung",
                "columns": ["is_active"],
                "reason": "Filter active users for authentication",
            },
            {
                "name": "idx_nguoi_dung_last_login",
                "table": "nguoi_dung",
                "columns": ["lan_dang_nhap_cuoi"],
                "reason": "User activity reports and inactive user cleanup",
            },
            # AuditLog table optimizations
            {
                "name": "idx_audit_log_action",
                "table": "audit_log",
                "columns": ["action"],
                "reason": "Filter audit logs by action type",
            },
            {
                "name": "idx_audit_log_resource",
                "table": "audit_log",
                "columns": ["resource", "resource_id"],
                "reason": "Track changes to specific resources",
            },
            {
                "name": "idx_audit_log_user_date",
                "table": "audit_log",
                "columns": ["user_id", "created_at"],
                "reason": "User activity tracking by date",
            },
            {
                "name": "idx_audit_log_date",
                "table": "audit_log",
                "columns": ["created_at"],
                "reason": "Date range filtering for audit reports",
            },
        ]

    def create_performance_indexes(self, db: Session):
        """Create performance indexes for common query patterns"""
        logger.info("Creating performance indexes...")

        created_count = 0
        skipped_count = 0

        for idx_config in self.optimization_indexes:
            try:
                # Check if index already exists
                result = db.execute(
                    text(
                        f"""
                    SELECT name FROM sqlite_master
                    WHERE type='index' AND name='{idx_config['name']}'
                """
                    )
                )

                if result.fetchone():
                    logger.debug(f"Index {idx_config['name']} already exists, skipping")
                    skipped_count += 1
                    continue

                # Create index
                columns_str = ", ".join(idx_config["columns"])
                create_sql = f"""
                    CREATE INDEX {idx_config['name']}
                    ON {idx_config['table']} ({columns_str})
                """

                db.execute(text(create_sql))
                db.commit()

                logger.info(f"Created index: {idx_config['name']} - {idx_config['reason']}")
                created_count += 1

            except Exception as e:
                logger.error(f"Failed to create index {idx_config['name']}: {e}")
                db.rollback()

        logger.info(f"Index creation complete: {created_count} created, {skipped_count} skipped")
        return created_count, skipped_count

    def analyze_query_performance(self, db: Session):
        """Analyze current query performance"""
        logger.info("Analyzing query performance...")

        # Common queries to analyze
        test_queries = [
            {
                "name": "Dashboard stats",
                "sql": 'SELECT COUNT(*) FROM khach_hang WHERE ngay_tao >= date("now", "-30 days")',
            },
            {
                "name": "Active orders by status",
                "sql": 'SELECT COUNT(*) FROM don_hang WHERE trang_thai = "cho_xac_nhan"',
            },
            {
                "name": "Customer orders",
                "sql": "SELECT COUNT(*) FROM don_hang WHERE khach_hang_id = 1",
            },
            {"name": "Active products", "sql": "SELECT COUNT(*) FROM san_pham WHERE is_active = 1"},
            {
                "name": "Recent contact history",
                "sql": 'SELECT COUNT(*) FROM lich_su_lien_he WHERE ngay_lien_he >= date("now", "-7 days")',
            },
        ]

        for query in test_queries:
            try:
                # Enable query plan analysis
                db.execute(text("EXPLAIN QUERY PLAN " + query["sql"]))
                result = db.fetchall()
                logger.info(f"Query: {query['name']}")
                for row in result:
                    logger.info(f"  Plan: {' '.join(str(x) for x in row)}")
            except Exception as e:
                logger.error(f"Failed to analyze query {query['name']}: {e}")

    def get_table_statistics(self, db: Session):
        """Get table statistics for optimization planning"""
        logger.info("Gathering table statistics...")

        stats = {}
        tables = [
            "khach_hang",
            "don_hang",
            "san_pham",
            "chi_tiet_don_hang",
            "lich_su_lien_he",
            "nguoi_dung",
            "audit_log",
            "system_setting",
            "payment_transaction",
        ]

        for table in tables:
            try:
                # Row count
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                row_count = result.fetchone()[0]

                # Table size (approximate)
                result = db.execute(text(f"PRAGMA table_info({table})"))
                column_count = len(result.fetchall())

                stats[table] = {
                    "rows": row_count,
                    "columns": column_count,
                    "estimated_size_kb": row_count * column_count * 10,  # Rough estimate
                }

                logger.info(f"Table {table}: {row_count} rows, {column_count} columns")

            except Exception as e:
                logger.error(f"Failed to get stats for table {table}: {e}")

        return stats

    def optimize_database(self, db: Session):
        """Run full database optimization"""
        logger.info("Starting database optimization...")

        try:
            # 1. Create performance indexes
            created, skipped = self.create_performance_indexes(db)

            # 2. Update table statistics (SQLite ANALYZE)
            logger.info("Updating table statistics...")
            db.execute(text("ANALYZE"))
            db.commit()

            # 3. Get current statistics
            stats = self.get_table_statistics(db)

            # 4. Analyze query performance
            self.analyze_query_performance(db)

            optimization_summary = {
                "indexes_created": created,
                "indexes_skipped": skipped,
                "table_stats": stats,
                "status": "success",
            }

            logger.info("Database optimization completed successfully")
            return optimization_summary

        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            db.rollback()
            raise


def run_database_optimization():
    """Run database optimization from command line"""
    from backend.database import SessionLocal

    db = SessionLocal()
    optimizer = DatabaseOptimizer()

    try:
        result = optimizer.optimize_database(db)
        print("Database optimization completed:")
        print(f"  - Indexes created: {result['indexes_created']}")
        print(f"  - Indexes skipped: {result['indexes_skipped']}")
        print(f"  - Tables analyzed: {len(result['table_stats'])}")
        return result
    finally:
        db.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    run_database_optimization()
