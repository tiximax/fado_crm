# 🚀 FADO CRM - E2E Tests (Playwright)

## Yêu cầu
- Node.js 18+ (khuyến nghị 20+)
- Backend đã chạy tại http://localhost:8000
- Frontend đang serve tĩnh tại http://localhost:3000 (ví dụ: `python -m http.server 3000` trong thư mục `frontend`)

## Cài đặt
```powershell
cd e2e
npm install
npm run install:browsers
```

## Chạy test
```powershell
# Chạy toàn bộ E2E
npm test

# Giao diện UI để debug
npm run test:ui

# Chạy 1 test đơn lẻ theo tên (không cần mở UI)
node ".\node_modules\@playwright\test\cli.js" test -c ".\playwright.config.js" -g "upload single product image via UI succeeds"
```

## Ghi chú
- Để chạy test upload, cần đăng nhập admin. Script test sẽ tự login bằng API (admin@fado.vn / admin123). Nếu chưa có, hãy tạo nhanh:
```powershell
python ..\backend\reset_admin_password.py
```
- Nếu dùng STORAGE_DRIVER=local, ảnh sau upload sẽ có URL dạng /uploads/... (được backend phục vụ trực tiếp).
- Nếu dùng S3/MinIO, URL public sẽ do endpoint/bucket của bạn quyết định.
- Test “dashboard loads when tokens are present (optional)” sẽ tự động bỏ qua nếu chưa có tài khoản demo trong DB.
- Để tạo tài khoản demo nhanh:
```powershell
# Tạo user mẫu (admin/manager/staff/viewer)
python backend/setup_users.py
```
- Sau khi có user mẫu, test authenticated sẽ pass nếu backend hoạt động ổn định.
