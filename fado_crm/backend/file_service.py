# 📁 FADO CRM - File Upload & Management Service
# Hệ thống quản lý file siêu xịn như Dropbox! ☁️

import os
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import hashlib
from datetime import datetime
import json
import mimetypes
from io import BytesIO

from logging_config import app_logger
from models import NguoiDung
from storage import get_storage_driver

class FileService:
    def __init__(self):
        # 📁 File storage configuration
        self.base_upload_dir = Path("uploads")
        self.product_images_dir = self.base_upload_dir / "product_images"
        self.temp_dir = self.base_upload_dir / "temp"
        self.thumbnails_dir = self.base_upload_dir / "thumbnails"

        # ☁️ Pluggable storage driver
        self.storage = get_storage_driver()

        # 🎯 File configuration
        self.allowed_image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        self.allowed_document_extensions = {'.pdf', '.doc', '.docx', '.xlsx', '.csv'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_image_size = 5 * 1024 * 1024   # 5MB
        self.thumbnail_sizes = [(150, 150), (300, 300), (800, 600)]

        # 🏗️ Create directories
        self.setup_directories()

        app_logger.info("File service initialized successfully")

    def setup_directories(self):
        """🏗️ Tạo các thư mục cần thiết"""
        directories = [
            self.base_upload_dir,
            self.product_images_dir,
            self.temp_dir,
            self.thumbnails_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            app_logger.info(f"Directory ready: {directory}")

    def generate_filename(self, original_filename: str, user_id: int = None) -> str:
        """🎲 Tạo tên file unique"""
        # Get file extension
        extension = Path(original_filename).suffix.lower()

        # Create unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        user_prefix = f"user_{user_id}_" if user_id else ""

        return f"{user_prefix}{timestamp}_{unique_id}{extension}"

    def get_file_hash(self, file_content: bytes) -> str:
        """🔐 Tạo hash để kiểm tra file trùng lặp"""
        return hashlib.md5(file_content).hexdigest()

    def validate_file(self, file: UploadFile, file_type: str = "image") -> Dict[str, Any]:
        """✅ Validate file upload"""
        validation_result = {
            "valid": False,
            "error": None,
            "file_info": {}
        }

        try:
            # Check file size
            max_size = self.max_image_size if file_type == "image" else self.max_file_size
            if file.size > max_size:
                validation_result["error"] = f"File quá lớn. Tối đa {max_size / (1024*1024):.1f}MB"
                return validation_result

            # Check file extension
            file_extension = Path(file.filename).suffix.lower()
            allowed_extensions = (self.allowed_image_extensions if file_type == "image"
                                else self.allowed_document_extensions)

            if file_extension not in allowed_extensions:
                validation_result["error"] = f"Định dạng file không được hỗ trợ: {file_extension}"
                return validation_result

            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file.filename)

            validation_result.update({
                "valid": True,
                "file_info": {
                    "filename": file.filename,
                    "size": file.size,
                    "extension": file_extension,
                    "mime_type": mime_type,
                    "type": file_type
                }
            })

            return validation_result

        except Exception as e:
            validation_result["error"] = f"Lỗi validate file: {str(e)}"
            return validation_result

    async def save_product_image(
        self,
        file: UploadFile,
        user: NguoiDung,
        product_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """📸 Lưu hình ảnh sản phẩm với thumbnails"""
        try:
            # Validate file
            validation = self.validate_file(file, "image")
            if not validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=validation["error"]
                )

            # Read file content
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer

            # Generate filename
            filename = self.generate_filename(file.filename, user.id)

            # Check for duplicate files
            file_hash = self.get_file_hash(file_content)

            # Save original image to configured storage
            self.storage.save_bytes("product_images", filename, file_content)

            # Process image and create thumbnails (store via storage driver)
            thumbnails = await self.create_thumbnails(file_content, filename)

            # Get image dimensions from bytes
            try:
                with Image.open(BytesIO(file_content)) as img:
                    width, height = img.size
            except Exception as e:
                width, height = 0, 0
                app_logger.warning(f"⚠️ Could not get image dimensions: {str(e)}")

            # Create file record
            file_record = {
                "id": str(uuid.uuid4()),
                "original_filename": file.filename,
                "stored_filename": filename,
                "file_path": f"product_images/{filename}",
                "file_size": file.size,
                "file_hash": file_hash,
                "mime_type": validation["file_info"]["mime_type"],
                "width": width,
                "height": height,
                "thumbnails": thumbnails,
                "uploaded_by": user.id,
                "uploaded_at": datetime.utcnow().isoformat(),
                "product_id": product_id,
                "file_type": "product_image"
            }

            # Log successful upload
            app_logger.success(
                f"📸 Product image uploaded successfully: {filename} by user {user.id}"
            )

            return {
                "success": True,
                "file_info": file_record,
                "url": self.storage.public_url("product_images", filename),
                "thumbnails": {
                    size_name: self.storage.public_url("thumbnails", thumb_filename)
                    for size_name, thumb_filename in thumbnails.items()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            app_logger.error(f"❌ Error uploading product image: {str(e)}")
            # Clean up any partial files
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink(missing_ok=True)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lỗi khi upload hình ảnh"
            )

    async def create_thumbnails(self, file_bytes: bytes, filename: str) -> Dict[str, str]:
        """🖼️ Tạo thumbnails cho hình ảnh và lưu qua storage driver"""
        thumbnails = {}

        try:
            with Image.open(BytesIO(file_bytes)) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                for size in self.thumbnail_sizes:
                    size_name = f"{size[0]}x{size[1]}"
                    thumb_filename = f"thumb_{size_name}_{filename}"

                    # Create thumbnail
                    img_copy = img.copy()
                    img_copy.thumbnail(size, Image.Resampling.LANCZOS)

                    # Save to bytes with high quality
                    out = BytesIO()
                    img_copy.save(out, "JPEG", quality=85, optimize=True)
                    out.seek(0)

                    # Store via storage driver
                    self.storage.save_bytes("thumbnails", thumb_filename, out.getvalue())

                    thumbnails[size_name] = thumb_filename

            app_logger.info(f"🖼️ Created {len(thumbnails)} thumbnails for {filename}")
            return thumbnails

        except Exception as e:
            app_logger.error(f"❌ Error creating thumbnails: {str(e)}")
            return {}

    async def upload_multiple_files(
        self,
        files: List[UploadFile],
        user: NguoiDung,
        file_type: str = "image",
        product_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """📁 Upload nhiều file cùng lúc"""
        results = []

        for file in files:
            try:
                if file_type == "image":
                    result = await self.save_product_image(file, user, product_id)
                else:
                    result = await self.save_document(file, user)

                results.append(result)

            except Exception as e:
                results.append({
                    "success": False,
                    "filename": file.filename,
                    "error": str(e)
                })

        return results

    async def save_document(self, file: UploadFile, user: NguoiDung) -> Dict[str, Any]:
        """📄 Lưu tài liệu (PDF, Excel, etc.)"""
        try:
            # Validate file
            validation = self.validate_file(file, "document")
            if not validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=validation["error"]
                )

            # Generate filename
            filename = self.generate_filename(file.filename, user.id)

            # Save file via storage driver
            content = await file.read()
            self.storage.save_bytes("documents", filename, content)

            file_record = {
                "id": str(uuid.uuid4()),
                "original_filename": file.filename,
                "stored_filename": filename,
                "file_path": f"documents/{filename}",
                "file_size": file.size,
                "file_hash": self.get_file_hash(content),
                "mime_type": validation["file_info"]["mime_type"],
                "uploaded_by": user.id,
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_type": "document"
            }

            return {
                "success": True,
                "file_info": file_record,
                "url": self.storage.public_url("documents", filename)
            }

        except HTTPException:
            raise
        except Exception as e:
            app_logger.error(f"❌ Error uploading document: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lỗi khi upload tài liệu"
            )

    def delete_file(self, filename: str, file_type: str = "image") -> bool:
        """🗑️ Xóa file và thumbnails"""
        try:
            if file_type == "image":
                # Delete main image via storage
                self.storage.delete("product_images", filename)

                # Delete thumbnails
                for size in self.thumbnail_sizes:
                    size_name = f"{size[0]}x{size[1]}"
                    thumb_filename = f"thumb_{size_name}_{filename}"
                    self.storage.delete("thumbnails", thumb_filename)

            else:  # document
                self.storage.delete("documents", filename)

            app_logger.info(f"🗑️ File deleted successfully: {filename}")
            return True

        except Exception as e:
            app_logger.error(f"❌ Error deleting file {filename}: {str(e)}")
            return False

    def get_file_info(self, filename: str, file_type: str = "image") -> Optional[Dict[str, Any]]:
        """ℹ️ Lấy thông tin file"""
        try:
            category = "product_images" if file_type == "image" else "documents"

            # Check existence via storage driver
            if not self.storage.exists(category, filename):
                return None

            info: Dict[str, Any] = {
                "filename": filename,
                "file_type": file_type,
                "url": self.storage.public_url(category, filename)
            }

            # Nếu là local driver, cung cấp thêm thông tin từ filesystem
            if os.getenv("STORAGE_DRIVER", "local").lower() == "local":
                if file_type == "image":
                    file_path = self.product_images_dir / filename
                else:
                    file_path = (self.base_upload_dir / "documents") / filename
                if file_path.exists():
                    stat = file_path.stat()
                    info.update({
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
                    if file_type == "image":
                        try:
                            with Image.open(file_path) as img:
                                info.update({
                                    "width": img.width,
                                    "height": img.height,
                                    "format": img.format
                                })
                        except Exception:
                            pass

            return info

        except Exception as e:
            app_logger.error(f"❌ Error getting file info: {str(e)}")
            return None

    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """🧹 Dọn dẹp file tạm"""
        try:
            cutoff_time = datetime.utcnow().timestamp() - (older_than_hours * 3600)
            deleted_count = 0

            for file_path in self.temp_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1

            if deleted_count > 0:
                app_logger.info(f"🧹 Cleaned up {deleted_count} temp files")

            return deleted_count

        except Exception as e:
            app_logger.error(f"❌ Error cleaning temp files: {str(e)}")
            return 0

    def get_storage_stats(self) -> Dict[str, Any]:
        """📊 Thống kê storage"""
        try:
            def get_dir_size(path: Path) -> Tuple[int, int]:
                """Get directory size and file count"""
                total_size = 0
                file_count = 0

                if path.exists():
                    for file_path in path.rglob('*'):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                            file_count += 1

                return total_size, file_count

            # Get stats for each directory
            product_images_size, product_images_count = get_dir_size(self.product_images_dir)
            thumbnails_size, thumbnails_count = get_dir_size(self.thumbnails_dir)
            documents_size, documents_count = get_dir_size(self.base_upload_dir / "documents")
            temp_size, temp_count = get_dir_size(self.temp_dir)

            total_size = product_images_size + thumbnails_size + documents_size + temp_size
            total_files = product_images_count + thumbnails_count + documents_count + temp_count

            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_files": total_files,
                "breakdown": {
                    "product_images": {
                        "size_bytes": product_images_size,
                        "size_mb": round(product_images_size / (1024 * 1024), 2),
                        "file_count": product_images_count
                    },
                    "thumbnails": {
                        "size_bytes": thumbnails_size,
                        "size_mb": round(thumbnails_size / (1024 * 1024), 2),
                        "file_count": thumbnails_count
                    },
                    "documents": {
                        "size_bytes": documents_size,
                        "size_mb": round(documents_size / (1024 * 1024), 2),
                        "file_count": documents_count
                    },
                    "temp": {
                        "size_bytes": temp_size,
                        "size_mb": round(temp_size / (1024 * 1024), 2),
                        "file_count": temp_count
                    }
                }
            }

        except Exception as e:
            app_logger.error(f"❌ Error getting storage stats: {str(e)}")
            return {}

    def list_files(self, category: str, limit: int = 100):
        """📃 Liệt kê file trong 1 category thông qua storage driver"""
        try:
            return self.storage.list(category, limit=limit)
        except Exception as e:
            app_logger.error(f"❌ Error listing files for category {category}: {str(e)}")
            return []

# 🌟 Global file service instance
file_service = FileService()

# 🎯 Helper functions
async def upload_product_image(file: UploadFile, user: NguoiDung, product_id: int = None):
    """📸 Helper để upload hình sản phẩm"""
    return await file_service.save_product_image(file, user, product_id)

async def upload_multiple_images(files: List[UploadFile], user: NguoiDung, product_id: int = None):
    """📁 Helper để upload nhiều hình"""
    return await file_service.upload_multiple_files(files, user, "image", product_id)

def delete_product_image(filename: str) -> bool:
    """🗑️ Helper để xóa hình sản phẩm"""
    return file_service.delete_file(filename, "image")

print("File service module loaded successfully!")