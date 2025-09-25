# -*- coding: utf-8 -*-
"""
Advanced Export/Import Service
Xuất dữ liệu Excel và PDF reports chuyên nghiệp cho FADO CRM
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import text
import io
import base64
from pathlib import Path
import json

# Optional dependencies - sẽ fallback nếu không có
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from models import Customer, Product, Order, ContactHistory
from database import get_db
from logging_config import app_logger


class AdvancedExportService:
    """Service xuất dữ liệu nâng cao"""

    def __init__(self, db: Session):
        self.db = db

    def export_customers_excel(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """📊 Xuất danh sách khách hàng ra Excel"""

        if not PANDAS_AVAILABLE:
            return {
                "error": "Pandas library không khả dụng. Cài đặt: pip install pandas openpyxl"
            }

        try:
            # Build query with filters
            query = """
                SELECT
                    c.customer_id,
                    c.full_name,
                    c.phone,
                    c.email,
                    c.address,
                    c.customer_type,
                    c.created_at,
                    COUNT(o.order_id) as total_orders,
                    COALESCE(SUM(o.total_amount), 0) as lifetime_value,
                    MAX(o.order_date) as last_order_date,
                    COUNT(ch.contact_id) as total_contacts
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                LEFT JOIN contact_history ch ON c.customer_id = ch.customer_id
                GROUP BY c.customer_id, c.full_name, c.phone, c.email, c.address, c.customer_type, c.created_at
                ORDER BY lifetime_value DESC
            """

            results = self.db.execute(text(query)).fetchall()

            # Convert to DataFrame
            data = [dict(row._mapping) for row in results]
            df = pd.DataFrame(data)

            # Format columns
            if not df.empty:
                df['lifetime_value'] = df['lifetime_value'].apply(lambda x: f"{x:,.0f} VND")
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
                df['last_order_date'] = pd.to_datetime(df['last_order_date']).dt.strftime('%d/%m/%Y')

                # Rename columns to Vietnamese
                df.columns = [
                    'ID Khách hàng', 'Họ tên', 'Số điện thoại', 'Email', 'Địa chỉ',
                    'Loại khách hàng', 'Ngày tạo', 'Tổng đơn hàng', 'Giá trị lifetime',
                    'Đơn hàng cuối', 'Lần liên hệ'
                ]

            # Save to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Danh sách khách hàng', index=False)

                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Danh sách khách hàng']

                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            output.seek(0)
            excel_data = base64.b64encode(output.read()).decode('utf-8')

            return {
                "success": True,
                "filename": f"khach_hang_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "data": excel_data,
                "total_records": len(df),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            app_logger.error(f"❌ Error exporting customers Excel: {str(e)}")
            return {"error": f"Lỗi khi xuất Excel: {str(e)}"}

    def export_orders_excel(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """📋 Xuất danh sách đơn hàng ra Excel"""

        if not PANDAS_AVAILABLE:
            return {
                "error": "Pandas library không khả dụng. Cài đặt: pip install pandas openpyxl"
            }

        try:
            # Default date range (last 3 months)
            if not date_from:
                date_from = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            if not date_to:
                date_to = datetime.now().strftime('%Y-%m-%d')

            query = """
                SELECT
                    o.order_id,
                    o.order_code,
                    c.full_name as customer_name,
                    c.phone as customer_phone,
                    p.product_name,
                    p.category,
                    p.origin_country,
                    o.quantity,
                    o.unit_price,
                    o.service_fee,
                    o.shipping_fee,
                    o.additional_fee,
                    o.total_amount,
                    o.order_status,
                    o.order_date,
                    o.estimated_delivery,
                    o.notes
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN products p ON o.product_id = p.product_id
                WHERE DATE(o.order_date) BETWEEN :date_from AND :date_to
                ORDER BY o.order_date DESC
            """

            results = self.db.execute(text(query), {
                "date_from": date_from,
                "date_to": date_to
            }).fetchall()

            # Convert to DataFrame
            data = [dict(row._mapping) for row in results]
            df = pd.DataFrame(data)

            if not df.empty:
                # Format money columns
                money_columns = ['unit_price', 'service_fee', 'shipping_fee', 'additional_fee', 'total_amount']
                for col in money_columns:
                    df[col] = df[col].apply(lambda x: f"{x:,.0f} VND" if pd.notna(x) else "0 VND")

                # Format date columns
                df['order_date'] = pd.to_datetime(df['order_date']).dt.strftime('%d/%m/%Y %H:%M')
                df['estimated_delivery'] = pd.to_datetime(df['estimated_delivery']).dt.strftime('%d/%m/%Y')

                # Rename columns
                df.columns = [
                    'ID Đơn hàng', 'Mã đơn hàng', 'Tên khách hàng', 'SĐT khách hàng',
                    'Tên sản phẩm', 'Danh mục', 'Xuất xứ', 'Số lượng',
                    'Giá đơn vị', 'Phí dịch vụ', 'Phí vận chuyển', 'Phí phụ',
                    'Tổng tiền', 'Trạng thái', 'Ngày đặt', 'Dự kiến giao', 'Ghi chú'
                ]

            # Save to Excel with multiple sheets
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Main sheet
                df.to_excel(writer, sheet_name='Danh sách đơn hàng', index=False)

                # Summary sheet
                if not df.empty:
                    summary_data = {
                        'Tổng số đơn hàng': [len(df)],
                        'Tổng doanh thu': [f"{df['Tổng tiền'].str.replace(' VND', '').str.replace(',', '').astype(float).sum():,.0f} VND"],
                        'Đơn hàng hoàn thành': [len(df[df['Trạng thái'] == 'Hoàn thành'])],
                        'Đơn hàng đang xử lý': [len(df[df['Trạng thái'] != 'Hoàn thành'])],
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Tổng quan', index=False)

                # Auto-adjust column widths
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            output.seek(0)
            excel_data = base64.b64encode(output.read()).decode('utf-8')

            return {
                "success": True,
                "filename": f"don_hang_{date_from}_{date_to}.xlsx",
                "data": excel_data,
                "total_records": len(df),
                "date_range": {"from": date_from, "to": date_to},
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            app_logger.error(f"❌ Error exporting orders Excel: {str(e)}")
            return {"error": f"Lỗi khi xuất Excel: {str(e)}"}

    def generate_analytics_pdf_report(self, report_type: str = "monthly") -> Dict[str, Any]:
        """📄 Tạo báo cáo PDF analytics chuyên nghiệp"""

        if not REPORTLAB_AVAILABLE:
            return {
                "error": "ReportLab library không khả dụng. Cài đặt: pip install reportlab"
            }

        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#34495E'),
                spaceAfter=12
            )

            # Title
            story.append(Paragraph("🛍️ BÁO CÁO PHÂN TÍCH FADO CRM", title_style))
            story.append(Paragraph(f"Báo cáo {report_type} - {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
            story.append(Spacer(1, 20))

            # Business Overview
            story.append(Paragraph("📊 Tổng quan kinh doanh", heading_style))

            # Get business metrics
            metrics = self.db.execute(text("""
                SELECT
                    COUNT(DISTINCT c.customer_id) as total_customers,
                    COUNT(DISTINCT p.product_id) as total_products,
                    COUNT(o.order_id) as total_orders,
                    SUM(o.total_amount) as total_revenue
                FROM customers c
                CROSS JOIN products p
                LEFT JOIN orders o ON c.customer_id = o.customer_id
            """)).fetchone()

            metrics_data = [
                ['Chỉ số', 'Giá trị'],
                ['Tổng khách hàng', f"{metrics.total_customers:,}"],
                ['Tổng sản phẩm', f"{metrics.total_products:,}"],
                ['Tổng đơn hàng', f"{metrics.total_orders:,}"],
                ['Tổng doanh thu', f"{metrics.total_revenue:,.0f} VND"],
            ]

            metrics_table = Table(metrics_data)
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(metrics_table)
            story.append(Spacer(1, 20))

            # Top Categories
            story.append(Paragraph("🏆 Top danh mục sản phẩm", heading_style))

            categories = self.db.execute(text("""
                SELECT p.category, COUNT(o.order_id) as orders, SUM(o.total_amount) as revenue
                FROM products p
                LEFT JOIN orders o ON p.product_id = o.product_id
                GROUP BY p.category
                ORDER BY revenue DESC
                LIMIT 5
            """)).fetchall()

            category_data = [['Danh mục', 'Đơn hàng', 'Doanh thu']]
            for cat in categories:
                category_data.append([
                    cat.category or 'N/A',
                    f"{cat.orders or 0:,}",
                    f"{cat.revenue or 0:,.0f} VND"
                ])

            category_table = Table(category_data)
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(category_table)
            story.append(Spacer(1, 20))

            # Customer Types
            story.append(Paragraph("👥 Phân bổ khách hàng", heading_style))

            customer_types = self.db.execute(text("""
                SELECT customer_type, COUNT(*) as count,
                       AVG(
                           SELECT SUM(total_amount)
                           FROM orders
                           WHERE customer_id = c.customer_id
                       ) as avg_value
                FROM customers c
                GROUP BY customer_type
                ORDER BY count DESC
            """)).fetchall()

            customer_data = [['Loại khách hàng', 'Số lượng', 'Giá trị TB']]
            for ctype in customer_types:
                customer_data.append([
                    ctype.customer_type,
                    f"{ctype.count:,}",
                    f"{ctype.avg_value or 0:,.0f} VND"
                ])

            customer_table = Table(customer_data)
            customer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(customer_table)
            story.append(Spacer(1, 30))

            # Footer
            story.append(Paragraph("---", styles['Normal']))
            story.append(Paragraph(
                f"📅 Báo cáo được tạo tự động bởi FADO CRM vào {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                styles['Italic']
            ))

            # Build PDF
            doc.build(story)
            buffer.seek(0)
            pdf_data = base64.b64encode(buffer.read()).decode('utf-8')

            return {
                "success": True,
                "filename": f"bao_cao_fado_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "data": pdf_data,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            app_logger.error(f"❌ Error generating PDF report: {str(e)}")
            return {"error": f"Lỗi khi tạo báo cáo PDF: {str(e)}"}

    def export_business_intelligence_excel(self) -> Dict[str, Any]:
        """🧠 Xuất báo cáo Business Intelligence toàn diện"""

        if not PANDAS_AVAILABLE:
            return {
                "error": "Pandas library không khả dụng. Cài đặt: pip install pandas openpyxl"
            }

        try:
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='openpyxl') as writer:

                # Sheet 1: Customer Analysis
                customer_analysis = self.db.execute(text("""
                    WITH customer_metrics AS (
                        SELECT
                            c.customer_id,
                            c.full_name,
                            c.customer_type,
                            COUNT(o.order_id) as order_count,
                            SUM(o.total_amount) as lifetime_value,
                            AVG(o.total_amount) as avg_order_value,
                            MIN(o.order_date) as first_order,
                            MAX(o.order_date) as last_order,
                            JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) as days_since_last_order
                        FROM customers c
                        LEFT JOIN orders o ON c.customer_id = o.customer_id
                        GROUP BY c.customer_id, c.full_name, c.customer_type
                    )
                    SELECT * FROM customer_metrics ORDER BY lifetime_value DESC
                """)).fetchall()

                customer_df = pd.DataFrame([dict(row._mapping) for row in customer_analysis])
                customer_df.to_excel(writer, sheet_name='Phân tích khách hàng', index=False)

                # Sheet 2: Product Performance
                product_performance = self.db.execute(text("""
                    SELECT
                        p.product_name,
                        p.category,
                        p.origin_country,
                        COUNT(o.order_id) as total_orders,
                        SUM(o.quantity) as total_quantity,
                        SUM(o.total_amount) as total_revenue,
                        AVG(o.total_amount) as avg_order_value,
                        MAX(o.order_date) as last_sold
                    FROM products p
                    LEFT JOIN orders o ON p.product_id = o.product_id
                    GROUP BY p.product_id, p.product_name, p.category, p.origin_country
                    ORDER BY total_revenue DESC
                """)).fetchall()

                product_df = pd.DataFrame([dict(row._mapping) for row in product_performance])
                product_df.to_excel(writer, sheet_name='Hiệu suất sản phẩm', index=False)

                # Sheet 3: Sales Trends
                sales_trends = self.db.execute(text("""
                    SELECT
                        DATE(order_date) as order_date,
                        COUNT(*) as daily_orders,
                        SUM(total_amount) as daily_revenue,
                        COUNT(DISTINCT customer_id) as unique_customers
                    FROM orders
                    WHERE order_date >= DATE('now', '-90 days')
                    GROUP BY DATE(order_date)
                    ORDER BY order_date
                """)).fetchall()

                trends_df = pd.DataFrame([dict(row._mapping) for row in sales_trends])
                trends_df.to_excel(writer, sheet_name='Xu hướng bán hàng', index=False)

                # Sheet 4: Communication Effectiveness
                comm_analysis = self.db.execute(text("""
                    SELECT
                        contact_type,
                        result,
                        COUNT(*) as contact_count,
                        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY contact_type) as success_rate
                    FROM contact_history
                    GROUP BY contact_type, result
                    ORDER BY contact_type, contact_count DESC
                """)).fetchall()

                comm_df = pd.DataFrame([dict(row._mapping) for row in comm_analysis])
                comm_df.to_excel(writer, sheet_name='Hiệu quả liên hệ', index=False)

                # Auto-adjust all columns
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            output.seek(0)
            excel_data = base64.b64encode(output.read()).decode('utf-8')

            return {
                "success": True,
                "filename": f"business_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "data": excel_data,
                "sheets_included": [
                    "Phân tích khách hàng", "Hiệu suất sản phẩm",
                    "Xu hướng bán hàng", "Hiệu quả liên hệ"
                ],
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            app_logger.error(f"❌ Error exporting BI Excel: {str(e)}")
            return {"error": f"Lỗi khi xuất BI Excel: {str(e)}"}


def get_advanced_export_service(db: Session = None) -> AdvancedExportService:
    """Factory function để tạo advanced export service"""
    if db is None:
        db = next(get_db())
    return AdvancedExportService(db)