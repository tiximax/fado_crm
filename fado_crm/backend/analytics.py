# -*- coding: utf-8 -*-
"""
Advanced Analytics & Reporting Module
Cung cấp báo cáo chuyên sâu và business intelligence cho FADO CRM
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from models import Customer, Product, Order, ContactHistory
from database import get_db
import json


class AdvancedAnalytics:
    """Lớp phân tích dữ liệu nâng cao cho business intelligence"""

    def __init__(self, db: Session):
        self.db = db

    def customer_segmentation_analysis(self) -> Dict[str, Any]:
        """Phân tích phân khúc khách hàng chi tiết"""

        # RFM Analysis (Recency, Frequency, Monetary)
        rfm_query = text("""
            WITH customer_metrics AS (
                SELECT
                    c.customer_id,
                    c.full_name,
                    c.customer_type,
                    JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) as recency_days,
                    COUNT(o.order_id) as frequency,
                    COALESCE(SUM(o.total_amount), 0) as monetary_value,
                    AVG(o.total_amount) as avg_order_value
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id, c.full_name, c.customer_type
            )
            SELECT
                customer_type,
                COUNT(*) as customer_count,
                AVG(recency_days) as avg_recency_days,
                AVG(frequency) as avg_frequency,
                AVG(monetary_value) as avg_monetary_value,
                AVG(avg_order_value) as avg_order_value,
                MIN(monetary_value) as min_spending,
                MAX(monetary_value) as max_spending
            FROM customer_metrics
            GROUP BY customer_type
        """)

        rfm_results = self.db.execute(rfm_query).fetchall()

        # Customer lifecycle analysis
        lifecycle_query = text("""
            SELECT
                CASE
                    WHEN order_count = 0 THEN 'New Prospect'
                    WHEN order_count = 1 THEN 'New Customer'
                    WHEN order_count BETWEEN 2 AND 5 THEN 'Developing'
                    WHEN order_count BETWEEN 6 AND 10 THEN 'Established'
                    ELSE 'Champion'
                END as lifecycle_stage,
                COUNT(*) as customer_count,
                AVG(total_spent) as avg_lifetime_value
            FROM (
                SELECT
                    c.customer_id,
                    COUNT(o.order_id) as order_count,
                    COALESCE(SUM(o.total_amount), 0) as total_spent
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id
            ) customer_summary
            GROUP BY lifecycle_stage
            ORDER BY customer_count DESC
        """)

        lifecycle_results = self.db.execute(lifecycle_query).fetchall()

        return {
            "rfm_analysis": [dict(row._mapping) for row in rfm_results],
            "lifecycle_analysis": [dict(row._mapping) for row in lifecycle_results],
            "generated_at": datetime.now().isoformat()
        }

    def sales_performance_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Phân tích hiệu suất bán hàng theo thời gian"""

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Daily sales trend
        daily_sales = self.db.execute(text("""
            SELECT
                DATE(order_date) as sale_date,
                COUNT(*) as order_count,
                SUM(total_amount) as daily_revenue,
                AVG(total_amount) as avg_order_value,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM orders
            WHERE order_date >= :start_date
            GROUP BY DATE(order_date)
            ORDER BY sale_date
        """), {"start_date": start_date}).fetchall()

        # Product category performance
        category_performance = self.db.execute(text("""
            SELECT
                p.category,
                COUNT(DISTINCT o.order_id) as orders_count,
                SUM(o.total_amount) as category_revenue,
                AVG(o.total_amount) as avg_order_value,
                COUNT(DISTINCT o.customer_id) as unique_customers
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.order_date >= :start_date
            GROUP BY p.category
            ORDER BY category_revenue DESC
        """), {"start_date": start_date}).fetchall()

        # Order status funnel
        status_funnel = self.db.execute(text("""
            SELECT
                order_status,
                COUNT(*) as order_count,
                SUM(total_amount) as revenue,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM orders
            WHERE order_date >= :start_date
            GROUP BY order_status
            ORDER BY
                CASE order_status
                    WHEN 'Chờ xác nhận' THEN 1
                    WHEN 'Đã xác nhận' THEN 2
                    WHEN 'Đang mua' THEN 3
                    WHEN 'Đã mua' THEN 4
                    WHEN 'Đang ship' THEN 5
                    WHEN 'Đã nhận' THEN 6
                    WHEN 'Hoàn thành' THEN 7
                END
        """), {"start_date": start_date}).fetchall()

        return {
            "daily_sales_trend": [dict(row._mapping) for row in daily_sales],
            "category_performance": [dict(row._mapping) for row in category_performance],
            "order_status_funnel": [dict(row._mapping) for row in status_funnel],
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            }
        }

    def product_intelligence_report(self) -> Dict[str, Any]:
        """Báo cáo thông minh về sản phẩm"""

        # Top performing products
        top_products = self.db.execute(text("""
            SELECT
                p.product_name,
                p.category,
                p.origin_country,
                COUNT(o.order_id) as order_count,
                SUM(o.total_amount) as total_revenue,
                AVG(o.total_amount) as avg_order_value,
                COUNT(DISTINCT o.customer_id) as unique_buyers,
                MAX(o.order_date) as last_ordered
            FROM products p
            JOIN orders o ON p.product_id = o.product_id
            GROUP BY p.product_id, p.product_name, p.category, p.origin_country
            ORDER BY total_revenue DESC
            LIMIT 20
        """)).fetchall()

        # Products by origin country performance
        country_performance = self.db.execute(text("""
            SELECT
                p.origin_country,
                COUNT(DISTINCT p.product_id) as product_count,
                COUNT(o.order_id) as total_orders,
                SUM(o.total_amount) as total_revenue,
                AVG(o.total_amount) as avg_order_value
            FROM products p
            LEFT JOIN orders o ON p.product_id = o.product_id
            GROUP BY p.origin_country
            ORDER BY total_revenue DESC
        """)).fetchall()

        # Slow-moving inventory
        slow_moving = self.db.execute(text("""
            SELECT
                p.product_name,
                p.category,
                p.origin_price,
                p.selling_price,
                COALESCE(order_count, 0) as order_count,
                COALESCE(last_ordered, 'Never') as last_ordered
            FROM products p
            LEFT JOIN (
                SELECT
                    product_id,
                    COUNT(*) as order_count,
                    MAX(order_date) as last_ordered
                FROM orders
                GROUP BY product_id
            ) o ON p.product_id = o.product_id
            WHERE COALESCE(order_count, 0) <= 2
            ORDER BY COALESCE(order_count, 0), p.selling_price DESC
        """)).fetchall()

        return {
            "top_performing_products": [dict(row._mapping) for row in top_products],
            "country_performance": [dict(row._mapping) for row in country_performance],
            "slow_moving_inventory": [dict(row._mapping) for row in slow_moving],
            "generated_at": datetime.now().isoformat()
        }

    def customer_communication_analysis(self) -> Dict[str, Any]:
        """Phân tích hiệu quả communication với khách hàng"""

        # Communication channel effectiveness
        channel_effectiveness = self.db.execute(text("""
            SELECT
                contact_type,
                COUNT(*) as total_contacts,
                COUNT(CASE WHEN result = 'Thành công' THEN 1 END) as successful_contacts,
                ROUND(COUNT(CASE WHEN result = 'Thành công' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM contact_history
            GROUP BY contact_type
            ORDER BY success_rate DESC
        """)).fetchall()

        # Customer responsiveness analysis
        customer_responsiveness = self.db.execute(text("""
            SELECT
                c.customer_type,
                COUNT(ch.contact_id) as total_contacts,
                COUNT(CASE WHEN ch.result = 'Thành công' THEN 1 END) as successful_contacts,
                ROUND(AVG(CASE WHEN ch.result = 'Thành công' THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate
            FROM customers c
            JOIN contact_history ch ON c.customer_id = ch.customer_id
            GROUP BY c.customer_type
            ORDER BY success_rate DESC
        """)).fetchall()

        # Recent communication trends
        recent_trends = self.db.execute(text("""
            SELECT
                DATE(contact_date) as contact_date,
                contact_type,
                COUNT(*) as contact_count,
                COUNT(CASE WHEN result = 'Thành công' THEN 1 END) as successful_count
            FROM contact_history
            WHERE contact_date >= DATE('now', '-30 days')
            GROUP BY DATE(contact_date), contact_type
            ORDER BY contact_date DESC, contact_count DESC
        """)).fetchall()

        return {
            "channel_effectiveness": [dict(row._mapping) for row in channel_effectiveness],
            "customer_responsiveness": [dict(row._mapping) for row in customer_responsiveness],
            "recent_communication_trends": [dict(row._mapping) for row in recent_trends],
            "generated_at": datetime.now().isoformat()
        }

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Tạo báo cáo tổng hợp cho leadership"""

        # Overall business metrics
        business_metrics = self.db.execute(text("""
            SELECT
                COUNT(DISTINCT c.customer_id) as total_customers,
                COUNT(DISTINCT p.product_id) as total_products,
                COUNT(o.order_id) as total_orders,
                SUM(o.total_amount) as total_revenue,
                AVG(o.total_amount) as avg_order_value,
                COUNT(CASE WHEN o.order_status = 'Hoàn thành' THEN 1 END) as completed_orders,
                ROUND(COUNT(CASE WHEN o.order_status = 'Hoàn thành' THEN 1 END) * 100.0 / COUNT(o.order_id), 2) as completion_rate
            FROM customers c
            CROSS JOIN products p
            LEFT JOIN orders o ON c.customer_id = o.customer_id
        """)).fetchone()

        # Growth trends (last 6 months)
        growth_trends = self.db.execute(text("""
            SELECT
                strftime('%Y-%m', order_date) as month,
                COUNT(*) as monthly_orders,
                SUM(total_amount) as monthly_revenue,
                COUNT(DISTINCT customer_id) as active_customers
            FROM orders
            WHERE order_date >= DATE('now', '-6 months')
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month
        """)).fetchall()

        # Key performance indicators
        current_month_performance = self.db.execute(text("""
            SELECT
                COUNT(*) as current_month_orders,
                SUM(total_amount) as current_month_revenue,
                COUNT(DISTINCT customer_id) as current_month_customers
            FROM orders
            WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now')
        """)).fetchone()

        return {
            "business_metrics": dict(business_metrics._mapping),
            "growth_trends": [dict(row._mapping) for row in growth_trends],
            "current_month_performance": dict(current_month_performance._mapping),
            "generated_at": datetime.now().isoformat(),
            "report_type": "Executive Summary"
        }


def get_analytics_service(db: Session = None) -> AdvancedAnalytics:
    """Factory function để tạo analytics service"""
    if db is None:
        db = next(get_db())
    return AdvancedAnalytics(db)