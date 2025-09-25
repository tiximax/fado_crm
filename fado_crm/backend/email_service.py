# 📧 FADO CRM - Email Notification System
# Hệ thống email thông minh như Jarvis! 🤖

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path
import json

from logging_config import app_logger
from models import DonHang, KhachHang, TrangThaiDonHang

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "your-email@gmail.com")
        self.email_password = os.getenv("EMAIL_PASSWORD", "your-app-password")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "FADO.VN CRM")

        # 📁 Templates directory
        self.templates_dir = Path(__file__).parent / "email_templates"
        self.templates_dir.mkdir(exist_ok=True)

        # 🎨 Create default templates if not exist
        self.create_default_templates()

        app_logger.info("📧 Email service initialized successfully")

    def create_default_templates(self):
        """🎨 Tạo các template email mặc định"""
        templates = {
            "order_created.html": self.get_order_created_template(),
            "order_confirmed.html": self.get_order_confirmed_template(),
            "order_shipped.html": self.get_order_shipped_template(),
            "order_delivered.html": self.get_order_delivered_template(),
            "welcome.html": self.get_welcome_template(),
        }

        for filename, content in templates.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """📤 Gửi email với HTML template đẹp mắt"""
        try:
            # Tạo message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.email_user}>"
            message["To"] = ", ".join(to_emails)

            # Add text part
            if text_body:
                text_part = MIMEText(text_body, "plain", "utf-8")
                message.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)

            # Gửi email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to_emails, message.as_string())

            app_logger.success(f"📧 Email sent successfully to {', '.join(to_emails)}")
            return True

        except Exception as e:
            app_logger.error(f"❌ Failed to send email to {', '.join(to_emails)}: {str(e)}")
            return False

    def send_order_notification(self, don_hang: DonHang, event_type: str) -> bool:
        """📋 Gửi thông báo đơn hàng theo trạng thái"""
        try:
            customer = don_hang.khach_hang
            if not customer or not customer.email:
                app_logger.warning(f"⚠️  No email found for order {don_hang.ma_don_hang}")
                return False

            # Tạo context cho template
            context = {
                "customer_name": customer.ho_ten,
                "order_code": don_hang.ma_don_hang,
                "order_total": don_hang.tong_tien,
                "order_date": don_hang.ngay_tao.strftime("%d/%m/%Y"),
                "order_status": don_hang.trang_thai.value,
                "customer_email": customer.email,
                "company_name": "FADO.VN",
                "company_phone": "0123-456-789",
                "company_email": "support@fado.vn"
            }

            # Chọn template và subject dựa trên event
            template_map = {
                "created": ("order_created.html", f"🎉 Đơn hàng #{don_hang.ma_don_hang} đã được tạo"),
                "confirmed": ("order_confirmed.html", f"✅ Đơn hàng #{don_hang.ma_don_hang} đã được xác nhận"),
                "shipped": ("order_shipped.html", f"🚚 Đơn hàng #{don_hang.ma_don_hang} đang được vận chuyển"),
                "delivered": ("order_delivered.html", f"📦 Đơn hàng #{don_hang.ma_don_hang} đã được giao thành công")
            }

            if event_type not in template_map:
                app_logger.warning(f"⚠️  Unknown event type: {event_type}")
                return False

            template_file, subject = template_map[event_type]
            html_body = self.render_template(template_file, context)

            return self.send_email(
                to_emails=[customer.email],
                subject=subject,
                html_body=html_body
            )

        except Exception as e:
            app_logger.error(f"❌ Failed to send order notification: {str(e)}")
            return False

    def send_welcome_email(self, customer: KhachHang) -> bool:
        """🎉 Gửi email chào mừng khách hàng mới"""
        try:
            if not customer.email:
                return False

            context = {
                "customer_name": customer.ho_ten,
                "customer_email": customer.email,
                "company_name": "FADO.VN",
                "company_phone": "0123-456-789",
                "company_email": "support@fado.vn"
            }

            html_body = self.render_template("welcome.html", context)

            return self.send_email(
                to_emails=[customer.email],
                subject="🎉 Chào mừng bạn đến với FADO.VN!",
                html_body=html_body
            )

        except Exception as e:
            app_logger.error(f"❌ Failed to send welcome email: {str(e)}")
            return False

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """🎨 Render email template với context data"""
        try:
            template_path = self.templates_dir / template_name

            if not template_path.exists():
                app_logger.error(f"❌ Template not found: {template_name}")
                return self.get_fallback_template(context)

            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()

            # Simple template rendering (replace {{variable}} với giá trị)
            for key, value in context.items():
                template = template.replace(f"{{{{{key}}}}}", str(value))

            return template

        except Exception as e:
            app_logger.error(f"❌ Error rendering template {template_name}: {str(e)}")
            return self.get_fallback_template(context)

    def get_fallback_template(self, context: Dict[str, Any]) -> str:
        """🛡️ Template dự phòng khi có lỗi"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #3498db;">Thông báo từ FADO.VN</h2>
                    <p>Xin chào {context.get('customer_name', 'Khách hàng')},</p>
                    <p>Cảm ơn bạn đã sử dụng dịch vụ của FADO.VN!</p>
                    <hr style="border: 1px solid #eee;">
                    <p style="font-size: 12px; color: #666;">
                        Email này được gửi tự động từ hệ thống FADO.VN CRM.
                    </p>
                </div>
            </body>
        </html>
        """

    def get_order_created_template(self) -> str:
        """🎨 Template đơn hàng được tạo"""
        return """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đơn hàng đã được tạo</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">🛍️ FADO.VN</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">Mua hộ chuyên nghiệp</p>
        </div>

        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">🎉 Đơn hàng đã được tạo thành công!</h2>

            <p>Xin chào <strong>{{customer_name}}</strong>,</p>

            <p>Cảm ơn bạn đã tin tưởng sử dụng dịch vụ mua hộ của FADO.VN. Đơn hàng của bạn đã được tạo thành công với thông tin sau:</p>

            <div style="background: #f8f9fa; border-left: 4px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span><strong>Mã đơn hàng:</strong></span>
                    <span style="color: #3498db; font-weight: bold;">{{order_code}}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span><strong>Ngày tạo:</strong></span>
                    <span>{{order_date}}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span><strong>Tổng tiền:</strong></span>
                    <span style="color: #e74c3c; font-weight: bold; font-size: 18px;">{{order_total:,.0f}} VND</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>Trạng thái:</strong></span>
                    <span style="background: #ffeaa7; color: #d63031; padding: 4px 12px; border-radius: 15px; font-size: 12px;">Chờ xác nhận</span>
                </div>
            </div>

            <p><strong>🔔 Bước tiếp theo:</strong></p>
            <ul style="color: #666; margin-left: 20px;">
                <li>Chúng tôi sẽ xem xét và xác nhận đơn hàng trong vòng 24 giờ</li>
                <li>Bạn sẽ nhận được email xác nhận khi đơn hàng được duyệt</li>
                <li>Quá trình mua hàng và vận chuyển sẽ được cập nhật thường xuyên</li>
            </ul>

            <div style="text-align: center; margin: 30px 0;">
                <a href="mailto:{{company_email}}" style="background: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">📧 Liên hệ hỗ trợ</a>
            </div>
        </div>

        <!-- Footer -->
        <div style="background: #2c3e50; color: white; padding: 20px; text-align: center; font-size: 14px;">
            <p style="margin: 0;">📞 Hotline: {{company_phone}} | 📧 Email: {{company_email}}</p>
            <p style="margin: 5px 0 0; opacity: 0.8;">© 2024 FADO.VN - Dịch vụ mua hộ uy tín #1 Việt Nam</p>
        </div>
    </div>
</body>
</html>
        """

    def get_order_confirmed_template(self) -> str:
        """✅ Template đơn hàng được xác nhận"""
        return """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đơn hàng đã được xác nhận</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">✅ Đơn hàng đã xác nhận</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">FADO.VN - Mua hộ chuyên nghiệp</p>
        </div>

        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">🎊 Tuyệt vời! Đơn hàng đã được xác nhận</h2>

            <p>Xin chào <strong>{{customer_name}}</strong>,</p>

            <p>Đơn hàng <strong>{{order_code}}</strong> của bạn đã được xác nhận thành công! Chúng tôi sẽ bắt đầu quá trình mua hàng ngay.</p>

            <div style="background: #d1f2eb; border-left: 4px solid #00b894; padding: 20px; margin: 20px 0; border-radius: 5px;">
                <div style="text-align: center;">
                    <div style="background: #00b894; color: white; padding: 8px 20px; border-radius: 20px; display: inline-block; margin-bottom: 15px;">
                        ✅ ĐÃ XÁC NHẬN
                    </div>
                    <h3 style="margin: 0; color: #00b894;">Đơn hàng: {{order_code}}</h3>
                    <p style="font-size: 18px; font-weight: bold; color: #e74c3c; margin: 5px 0;">{{order_total:,.0f}} VND</p>
                </div>
            </div>

            <p><strong>📅 Timeline dự kiến:</strong></p>
            <div style="margin: 20px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="width: 30px; height: 30px; background: #00b894; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">1</div>
                    <div>
                        <div style="font-weight: bold;">Đang mua hàng</div>
                        <div style="color: #666; font-size: 14px;">Ước tính 2-5 ngày</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="width: 30px; height: 30px; background: #ddd; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">2</div>
                    <div>
                        <div style="color: #666;">Vận chuyển quốc tế</div>
                        <div style="color: #666; font-size: 14px;">Ước tính 7-14 ngày</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 30px; height: 30px; background: #ddd; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">3</div>
                    <div>
                        <div style="color: #666;">Giao hàng tận nơi</div>
                        <div style="color: #666; font-size: 14px;">Ước tính 1-2 ngày</div>
                    </div>
                </div>
            </div>

            <p style="background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin: 20px 0;">
                💡 <strong>Lưu ý:</strong> Chúng tôi sẽ thường xuyên cập nhật trạng thái đơn hàng qua email và SMS.
            </p>
        </div>

        <!-- Footer -->
        <div style="background: #2c3e50; color: white; padding: 20px; text-align: center; font-size: 14px;">
            <p style="margin: 0;">📞 Hotline: {{company_phone}} | 📧 Email: {{company_email}}</p>
            <p style="margin: 5px 0 0; opacity: 0.8;">© 2024 FADO.VN - Cam kết chất lượng và uy tín</p>
        </div>
    </div>
</body>
</html>
        """

    def get_order_shipped_template(self) -> str:
        """🚚 Template đơn hàng đang vận chuyển"""
        return """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đơn hàng đang được vận chuyển</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">🚚 Đang vận chuyển</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">Hàng của bạn đang trên đường!</p>
        </div>

        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">📦 Đơn hàng đang được giao đến bạn!</h2>

            <p>Xin chào <strong>{{customer_name}}</strong>,</p>

            <p>Tin tốt! Đơn hàng <strong>{{order_code}}</strong> đã được đóng gói và đang trên đường đến địa chỉ của bạn.</p>

            <div style="background: #ffeaa7; border-left: 4px solid #fdcb6e; padding: 20px; margin: 20px 0; border-radius: 5px;">
                <div style="text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 15px;">🚚</div>
                    <h3 style="margin: 0; color: #d63031;">Đơn hàng: {{order_code}}</h3>
                    <p style="margin: 10px 0; color: #666;">Đang vận chuyển đến bạn</p>
                    <div style="background: #fdcb6e; color: white; padding: 8px 20px; border-radius: 20px; display: inline-block;">
                        🚛 ĐANG VẬN CHUYỂN
                    </div>
                </div>
            </div>

            <p><strong>📍 Thông tin giao hàng:</strong></p>
            <ul style="color: #666; margin-left: 20px;">
                <li>Thời gian dự kiến: 1-3 ngày làm việc</li>
                <li>Giao hàng trong giờ hành chính</li>
                <li>Shipper sẽ gọi điện trước khi giao</li>
                <li>Vui lòng chuẩn bị tiền mặt hoặc thẻ để thanh toán COD</li>
            </ul>

            <div style="text-align: center; margin: 30px 0;">
                <p style="margin-bottom: 15px; color: #666;">Có câu hỏi về đơn hàng?</p>
                <a href="tel:{{company_phone}}" style="background: #fd79a8; color: white; padding: 12px 25px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 5px;">📞 Gọi ngay</a>
                <a href="mailto:{{company_email}}" style="background: #74b9ff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 5px;">📧 Email</a>
            </div>
        </div>

        <!-- Footer -->
        <div style="background: #2c3e50; color: white; padding: 20px; text-align: center; font-size: 14px;">
            <p style="margin: 0;">📞 Hotline: {{company_phone}} | 📧 Email: {{company_email}}</p>
            <p style="margin: 5px 0 0; opacity: 0.8;">© 2024 FADO.VN - Giao hàng nhanh chóng, an toàn</p>
        </div>
    </div>
</body>
</html>
        """

    def get_order_delivered_template(self) -> str:
        """📦 Template đơn hàng đã giao"""
        return """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đơn hàng đã được giao thành công</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #00b894 0%, #55a3ff 100%); color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">🎉 Giao hàng thành công!</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">Cảm ơn bạn đã tin tưởng FADO.VN</p>
        </div>

        <!-- Content -->
        <div style="padding: 40px 30px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="font-size: 72px; margin-bottom: 20px;">🎊</div>
                <h2 style="color: #2c3e50; margin: 0;">Đơn hàng đã được giao thành công!</h2>
            </div>

            <p>Xin chào <strong>{{customer_name}}</strong>,</p>

            <p>Chúc mừng! Đơn hàng <strong>{{order_code}}</strong> đã được giao đến bạn thành công. Hy vọng bạn hài lòng với sản phẩm!</p>

            <div style="background: #d1f2eb; border-left: 4px solid #00b894; padding: 25px; margin: 25px 0; border-radius: 5px; text-align: center;">
                <div style="background: #00b894; color: white; padding: 10px 25px; border-radius: 25px; display: inline-block; margin-bottom: 15px;">
                    ✅ ĐÃ GIAO THÀNH CÔNG
                </div>
                <h3 style="margin: 10px 0; color: #00b894;">Đơn hàng: {{order_code}}</h3>
                <p style="margin: 0; color: #666; font-size: 14px;">Giao thành công vào {{order_date}}</p>
            </div>

            <div style="background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h4 style="margin: 0 0 15px; color: #856404;">💝 Đánh giá dịch vụ</h4>
                <p style="margin: 0;">Ý kiến của bạn rất quan trọng với chúng tôi! Vui lòng dành 2 phút để đánh giá chất lượng dịch vụ và sản phẩm.</p>
                <div style="text-align: center; margin-top: 15px;">
                    <a href="#" style="background: #f39c12; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">⭐ Đánh giá ngay</a>
                </div>
            </div>

            <p><strong>🎁 Ưu đãi đặc biệt:</strong></p>
            <div style="border: 2px dashed #3498db; padding: 20px; margin: 20px 0; border-radius: 8px; background: #f8f9ff; text-align: center;">
                <h4 style="color: #3498db; margin: 0 0 10px;">Mã giảm giá 10%</h4>
                <div style="background: #3498db; color: white; padding: 8px 15px; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 18px; letter-spacing: 2px;">
                    FADOVIP10
                </div>
                <p style="margin: 10px 0 0; font-size: 12px; color: #666;">Áp dụng cho đơn hàng tiếp theo. HSD: 30 ngày</p>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <p style="color: #666; margin-bottom: 15px;">Cần hỗ trợ gì khác?</p>
                <a href="tel:{{company_phone}}" style="background: #00b894; color: white; padding: 12px 25px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 5px;">📞 Liên hệ</a>
                <a href="https://fado.vn" style="background: #74b9ff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 5px;">🛍️ Mua tiếp</a>
            </div>
        </div>

        <!-- Footer -->
        <div style="background: #2c3e50; color: white; padding: 20px; text-align: center; font-size: 14px;">
            <p style="margin: 0 0 10px;">❤️ Cảm ơn bạn đã chọn FADO.VN!</p>
            <p style="margin: 0;">📞 Hotline: {{company_phone}} | 📧 Email: {{company_email}}</p>
            <p style="margin: 5px 0 0; opacity: 0.8;">© 2024 FADO.VN - Đối tác tin cậy cho mọi đơn hàng</p>
        </div>
    </div>
</body>
</html>
        """

    def get_welcome_template(self) -> str:
        """🎉 Template chào mừng khách hàng mới"""
        return """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chào mừng đến với FADO.VN</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #a29bfe 0%, #fd79a8 100%); color: white; padding: 40px 30px; text-align: center;">
            <div style="font-size: 64px; margin-bottom: 15px;">🎉</div>
            <h1 style="margin: 0; font-size: 32px;">Chào mừng đến với FADO.VN!</h1>
            <p style="margin: 15px 0 0; opacity: 0.9; font-size: 18px;">Dịch vụ mua hộ quốc tế #1 Việt Nam</p>
        </div>

        <!-- Content -->
        <div style="padding: 40px 30px;">
            <p style="font-size: 18px; color: #2c3e50; margin-bottom: 25px;">Xin chào <strong>{{customer_name}}</strong>,</p>

            <p>Chúc mừng bạn đã trở thành thành viên của cộng đồng FADO.VN! Chúng tôi rất vui mừng được phục vụ bạn.</p>

            <div style="background: #e8f4f8; border-left: 4px solid #3498db; padding: 25px; margin: 25px 0; border-radius: 8px;">
                <h3 style="color: #3498db; margin: 0 0 15px;">🌟 Tại sao chọn FADO.VN?</h3>
                <ul style="margin: 0; padding-left: 20px; color: #666;">
                    <li>✅ Mua hộ từ 200+ website quốc tế</li>
                    <li>💰 Phí dịch vụ cạnh tranh nhất thị trường</li>
                    <li>🚀 Vận chuyển nhanh chóng, an toàn</li>
                    <li>🔒 Cam kết 100% chính hãng</li>
                    <li>📞 Hỗ trợ 24/7 tận tình</li>
                </ul>
            </div>

            <h3 style="color: #2c3e50; margin: 30px 0 15px;">🎁 Ưu đãi chào mừng thành viên mới</h3>

            <div style="border: 2px dashed #fd79a8; padding: 25px; margin: 20px 0; border-radius: 10px; background: #fdf2f8; text-align: center;">
                <h4 style="color: #fd79a8; margin: 0 0 15px; font-size: 20px;">Giảm ngay 15% đơn hàng đầu tiên!</h4>
                <div style="background: #fd79a8; color: white; padding: 12px 20px; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 20px; letter-spacing: 3px; margin: 10px 0;">
                    WELCOME15
                </div>
                <p style="margin: 15px 0 0; font-size: 14px; color: #666;">
                    Áp dụng cho đơn hàng từ 500.000 VND. HSD: 15 ngày
                </p>
            </div>

            <h3 style="color: #2c3e50; margin: 30px 0 15px;">🚀 Bắt đầu mua hộ ngay</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 30px;">
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 32px; margin-bottom: 10px;">🇺🇸</div>
                    <strong>Amazon US</strong>
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">Siêu thị online lớn nhất</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 32px; margin-bottom: 10px;">🇯🇵</div>
                    <strong>Rakuten</strong>
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">Đồ Nhật chính hãng</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 32px; margin-bottom: 10px;">🇰🇷</div>
                    <strong>Gmarket</strong>
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">K-Beauty & Fashion</p>
                </div>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="https://fado.vn/order" style="background: linear-gradient(45deg, #fd79a8, #a29bfe); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold; font-size: 16px;">
                    🛍️ Tạo đơn hàng đầu tiên
                </a>
            </div>
        </div>

        <!-- Footer -->
        <div style="background: #2c3e50; color: white; padding: 25px; text-align: center; font-size: 14px;">
            <div style="margin-bottom: 15px;">
                <strong>📞 Liên hệ hỗ trợ:</strong>
            </div>
            <p style="margin: 5px 0;">Hotline: {{company_phone}} | Email: {{company_email}}</p>
            <p style="margin: 15px 0 5px; opacity: 0.8;">Kết nối với chúng tôi:</p>
            <div style="margin: 10px 0;">
                <a href="#" style="color: #74b9ff; text-decoration: none; margin: 0 10px;">📘 Facebook</a>
                <a href="#" style="color: #fd79a8; text-decoration: none; margin: 0 10px;">📷 Instagram</a>
                <a href="#" style="color: #00cec9; text-decoration: none; margin: 0 10px;">📺 YouTube</a>
            </div>
            <p style="margin: 15px 0 0; opacity: 0.7; font-size: 12px;">
                © 2024 FADO.VN - Kết nối thế giới, mua sắm không giới hạn
            </p>
        </div>
    </div>
</body>
</html>
        """

# 🌟 Global email service instance
email_service = EmailService()

# 🎯 Helper functions for easy usage
def send_order_created_email(don_hang: DonHang) -> bool:
    """📧 Gửi email khi tạo đơn hàng"""
    return email_service.send_order_notification(don_hang, "created")

def send_order_confirmed_email(don_hang: DonHang) -> bool:
    """✅ Gửi email khi xác nhận đơn hàng"""
    return email_service.send_order_notification(don_hang, "confirmed")

def send_order_shipped_email(don_hang: DonHang) -> bool:
    """🚚 Gửi email khi vận chuyển đơn hàng"""
    return email_service.send_order_notification(don_hang, "shipped")

def send_order_delivered_email(don_hang: DonHang) -> bool:
    """📦 Gửi email khi giao đơn hàng"""
    return email_service.send_order_notification(don_hang, "delivered")

def send_welcome_email(customer: KhachHang) -> bool:
    """🎉 Gửi email chào mừng khách hàng mới"""
    return email_service.send_welcome_email(customer)

print("📧 Email service module loaded successfully!")