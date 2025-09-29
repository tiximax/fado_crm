# -*- coding: utf-8 -*-
# FADO CRM - Full Application (app_full)
# Hợp nhất server ổn định cho dev/test (auth + dashboard + CRUD cơ bản) + một số module nâng cao

import hashlib
import hmac
import os
import urllib.parse
from typing import Any, Dict, List, Optional

from backend.main_working import app  # Tái sử dụng toàn bộ app đã ổn định trong main_working

# ===== Advanced Modules: Minimal Payments (VNPay) =====
from fastapi import Depends, File, Form, HTTPException, Query, Request, UploadFile

EXCLUDED_FIELDS = {"vnp_SecureHash", "vnp_SecureHashType"}

# Auth & models for permission checks
from auth import get_admin_user, get_current_active_user, get_manager_user
from models import NguoiDung
from models import SystemSetting as SystemSettingModel

# File service (optional); provide graceful fallback if unavailable
try:
    from file_service import file_service as _fs
except Exception:
    _fs = None


def _sorted_query_string(params: Dict[str, Any]) -> str:
    items = [(k, v) for k, v in params.items() if k not in EXCLUDED_FIELDS and v is not None]
    items.sort(key=lambda kv: kv[0])
    return "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in items)


def _sign_params(params: Dict[str, Any], secret: str) -> str:
    data = _sorted_query_string(params)
    return hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha512).hexdigest()


@app.get("/payments/return")
async def vnpay_return(request: Request):
    try:
        params = dict(request.query_params)
        secret = os.getenv("VNPAY_HASH_SECRET", "secret")
        provided = str(params.get("vnp_SecureHash", "")).lower()
        calculated = _sign_params(params, secret).lower()
        if provided != calculated:
            raise HTTPException(status_code=400, detail="Chu ky khong hop le")
        txn_ref = params.get("vnp_TxnRef")
        resp_code = params.get("vnp_ResponseCode")
        status = "success" if resp_code == "00" else "failed"
        return {"success": True, "status": status, "txn_ref": txn_ref}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi xu ly return: {e}")


@app.post("/payments/webhook")
async def vnpay_webhook(payload: Dict[str, Any], request: Request):
    try:
        data: Dict[str, Any] = payload or {}
        if not data and request.headers.get("content-type", "").startswith(
            "application/x-www-form-urlencoded"
        ):
            form = await request.form()
            data = dict(form)
        secret = os.getenv("VNPAY_HASH_SECRET", "secret")
        provided = str(data.get("vnp_SecureHash", "")).lower()
        calculated = _sign_params(data, secret).lower()
        if provided != calculated:
            raise HTTPException(status_code=400, detail="Chu ky khong hop le")
        return {"RspCode": "00", "Message": "Confirm Success"}
    except HTTPException:
        raise
    except Exception as e:
        return {"RspCode": "99", "Message": f"system error: {e}"}


# ===== Upload & Storage Endpoints =====
@app.post("/upload/product-image")
async def upload_product_image_endpoint(
    file: UploadFile = File(..., description="Hinh anh san pham"),
    product_id: Optional[int] = Form(None, description="ID san pham (optional)"),
    current_user: NguoiDung = Depends(get_current_active_user),
):
    try:
        if _fs is not None:
            result = await _fs.save_product_image(file, current_user, product_id)
            return {"success": True, "message": "Upload hinh anh thanh cong", "data": result}
        # Fallback: save locally under uploads/product_images
        from pathlib import Path

        content = await file.read()
        uploads_dir = Path("uploads") / "product_images"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        import datetime
        import uuid

        stored = f"{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{file.filename}"
        out_path = uploads_dir / stored
        with open(out_path, "wb") as f:
            f.write(content)
        return {
            "success": True,
            "message": "Upload hinh anh thanh cong",
            "data": {
                "file_info": {"stored_filename": stored},
                "url": f"/uploads/product_images/{stored}",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi khi upload hinh anh: {e}")


@app.post("/upload/multiple-images")
async def upload_multiple_images_endpoint(
    files: List[UploadFile] = File(..., description="Nhieu hinh anh san pham"),
    product_id: Optional[int] = Form(None, description="ID san pham (optional)"),
    current_user: NguoiDung = Depends(get_current_active_user),
):
    try:
        results = []
        if _fs is not None:
            results = await _fs.upload_multiple_files(files, current_user, "image", product_id)
        else:
            for f in files:
                try:
                    # reuse single upload fallback
                    res = await upload_product_image_endpoint(f, product_id, current_user)
                    results.append(res)
                except Exception as e:
                    results.append({"success": False, "error": str(e)})
        success_count = sum(1 for r in results if r.get("success"))
        fail_count = len(results) - success_count
        return {
            "success": True,
            "message": f"Upload hoan thanh: {success_count} thanh cong, {fail_count} that bai",
            "data": {"results": results},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi khi upload nhieu hinh anh: {e}")


@app.delete("/upload/image/{filename}")
async def delete_image_endpoint(
    filename: str, current_user: NguoiDung = Depends(get_current_active_user)
):
    try:
        if _fs is not None:
            ok = _fs.delete_file(filename, "image")
            if not ok:
                raise HTTPException(status_code=500, detail="Xoa file that bai")
        else:
            from pathlib import Path

            path = Path("uploads") / "product_images" / filename
            if path.exists():
                path.unlink()
        return {"success": True, "message": f"Da xoa hinh anh: {filename}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi khi xoa file: {e}")


@app.get("/upload/list")
async def list_uploaded_files(
    category: str = Query(..., description="Danh muc: product_images | thumbnails | documents"),
    limit: int = Query(50, ge=1, le=1000),
    current_user: NguoiDung = Depends(get_current_active_user),
    request: Request = None,
):
    try:
        base = str(request.base_url).rstrip("/") if request else ""
        items = []
        if _fs is not None:
            items = _fs.list_files(category, limit=limit)
            driver = os.getenv("STORAGE_DRIVER", "local").lower()
            for it in items:
                url = it.get("url", "")
                if driver == "local" and url.startswith("/"):
                    it["url"] = f"{base}{url}"
        else:
            from pathlib import Path

            if category == "product_images":
                for p in (Path("uploads") / "product_images").glob("*"):
                    if p.is_file():
                        items.append(
                            {"filename": p.name, "url": f"{base}/uploads/product_images/{p.name}"}
                        )
        return {"success": True, "category": category, "total": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi khi liet ke file: {e}")


@app.get("/upload/storage-stats")
async def get_storage_stats(current_user: NguoiDung = Depends(get_admin_user)):
    try:
        if _fs is not None:
            stats = _fs.get_storage_stats()
        else:
            from pathlib import Path

            imgs = list((Path("uploads") / "product_images").glob("*"))
            total = sum(p.stat().st_size for p in imgs if p.is_file()) if imgs else 0
            stats = {"total_files": len(imgs), "total_size_bytes": total}
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi khi lay thong ke storage: {e}")


@app.post("/upload/cleanup-temp")
async def cleanup_temp_files(
    older_than_hours: int = Query(24, ge=1, le=168, description="Xoa file cu hon (gio)"),
    current_user: NguoiDung = Depends(get_admin_user),
):
    try:
        if _fs is not None:
            deleted_count = _fs.cleanup_temp_files(older_than_hours)
        else:
            deleted_count = 0
        return {"success": True, "message": f"Da xoa {deleted_count} file tam"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi khi don dep file tam: {e}")


# ===== Additional Upload Delete Endpoint (by category & filename) =====
@app.delete("/upload/file")
async def delete_uploaded_file(
    category: str = Query(..., description="Danh muc: product_images | thumbnails | documents"),
    filename: str = Query(..., description="Ten file can xoa"),
    current_user: NguoiDung = Depends(get_admin_user),
):
    try:
        if _fs is not None:
            if category == "product_images":
                ok = _fs.delete_file(filename, "image")
            elif category in ("thumbnails", "documents"):
                ok = _fs.storage.delete(category, filename)
            else:
                raise HTTPException(status_code=400, detail="Category khong hop le")
        else:
            from pathlib import Path

            if category == "product_images":
                p = Path("uploads") / "product_images" / filename
            elif category == "thumbnails":
                p = Path("uploads") / "thumbnails" / filename
            elif category == "documents":
                p = Path("uploads") / "documents" / filename
            else:
                raise HTTPException(status_code=400, detail="Category khong hop le")
            ok = False
            if p.exists():
                p.unlink()
                ok = True
        if not ok:
            raise HTTPException(status_code=500, detail="Xoa file that bai")
        return {"success": True, "message": f"Da xoa {filename} khoi {category}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi khi xoa file: {e}")


from database import get_db

# ===== System Settings (Admin) =====
from sqlalchemy.orm import Session


@app.get("/admin/system-settings")
async def list_settings(
    current_user: NguoiDung = Depends(get_admin_user), db: Session = Depends(get_db)
):
    rows = db.query(SystemSettingModel).order_by(SystemSettingModel.key.asc()).all()
    return [
        {
            "key": r.key,
            "value": r.value,
            "description": getattr(r, "description", None),
            "updated_at": getattr(r, "updated_at", None),
        }
        for r in rows
    ]


@app.get("/admin/system-settings/{key}")
async def get_setting(
    key: str, current_user: NguoiDung = Depends(get_admin_user), db: Session = Depends(get_db)
):
    r = db.query(SystemSettingModel).filter(SystemSettingModel.key == key).first()
    if not r:
        raise HTTPException(status_code=404, detail="Khong tim thay cau hinh")
    return {
        "key": r.key,
        "value": r.value,
        "description": getattr(r, "description", None),
        "updated_at": getattr(r, "updated_at", None),
    }


@app.put("/admin/system-settings/{key}")
async def upsert_setting(
    key: str,
    payload: Dict[str, Any],
    current_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    r = db.query(SystemSettingModel).filter(SystemSettingModel.key == key).first()
    if not r:
        r = SystemSettingModel(
            key=key, value=str(payload.get("value", "")), description=payload.get("description")
        )
        db.add(r)
    else:
        r.value = str(payload.get("value", ""))
        if "description" in payload:
            r.description = payload.get("description")
    try:
        from datetime import datetime as _dt

        r.updated_at = _dt.utcnow()
    except Exception:
        pass
    db.commit()
    db.refresh(r)
    return {
        "key": r.key,
        "value": r.value,
        "description": getattr(r, "description", None),
        "updated_at": getattr(r, "updated_at", None),
    }
