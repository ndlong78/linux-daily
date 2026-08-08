# Production Incident & Rollback Runbook

Runbook này áp dụng khi workflow **Production Smoke** báo production của `https://linux.no.id.vn/` không còn khớp với serving state mong đợi từ `main`.

## Tín hiệu cần xử lý

`tools/check_production.py` phân biệt ba nhóm tín hiệu:

1. **Availability/content correctness** — HTTP status, content type, canonical/OG/RSS/sitemap/robots.
2. **Serving freshness** — SHA-256 từng endpoint và aggregate site fingerprint khác artifact trong checkout `main`.
3. **Cache observability** — `cache-control: private` hoặc `no-store` trên static public response là lỗi; thiếu `cache-control` chỉ là warning để tránh phụ thuộc semantics riêng của Cloudflare.

Fingerprint là fingerprint của **nội dung public đang serve**, không phải Git commit SHA. Nếu hai commit tạo cùng public artifacts thì fingerprint có thể giống nhau; đây là chủ ý vì gate kiểm serving state chứ không suy diễn deployment metadata không tồn tại.

## Triage nhanh

1. Mở workflow run `Production Smoke`, ghi nhận endpoint lỗi và hai fingerprint được in trong log.
2. Xác nhận `CI` trên commit `main` gần nhất đã xanh.
3. Chạy local từ checkout đúng `main`:

```bash
python3 tools/site_fingerprint.py
python3 tools/check_production.py --attempts 1 --delay 0 --timeout 12
```

4. Nếu chỉ một endpoint mismatch, so SHA-256 endpoint đó trước; nếu nhiều endpoint mismatch cùng lúc, ưu tiên nghi ngờ deploy chưa hoàn tất hoặc production đang serve release cũ.
5. Không sửa trực tiếp generated artifact để làm fingerprint khớp. Source of truth vẫn là repo + deterministic build.

## Phân loại sự cố

### A. Production stale sau merge

Dấu hiệu: CI xanh, local fingerprint mới, production fingerprint vẫn cũ.

Hành động:

- kiểm tra trạng thái deployment phía Cloudflare;
- chờ/retry trong cửa sổ retry của workflow nếu deployment vẫn đang tiến hành;
- nếu deployment đã báo thành công nhưng fingerprint vẫn cũ, xem như deploy drift và thực hiện redeploy release/commit đã được CI xác nhận.

### B. Production trả nội dung khác repo

Dấu hiệu: endpoint HTTP 200 nhưng SHA-256 mismatch kéo dài, có thể chỉ một file.

Hành động:

- kiểm tra cache/CDN và đường dẫn asset;
- purge cache có mục tiêu nếu xác nhận cache stale;
- chạy lại Production Smoke;
- không purge toàn bộ cache theo phản xạ nếu chưa xác định phạm vi.

### C. Header/cache regression

Dấu hiệu: content đúng nhưng `content-type` sai hoặc static public response mang `private`/`no-store`.

Hành động:

- kiểm tra Worker/Cloudflare response-header policy;
- sửa cấu hình qua PR bình thường;
- giữ warning `cache-control missing` ở mức quan sát cho tới khi repository quản lý explicit cache policy.

### D. Nội dung main có regression thật

Dấu hiệu: production đã khớp fingerprint của `main`, nhưng smoke semantic check vẫn lỗi hoặc site có regression đã xác nhận.

Hành động: rollback bằng Git, không chỉnh nóng production làm lệch source of truth.

## Rollback chuẩn

1. Xác định merge commit/release tốt gần nhất trên `main`.
2. Tạo **revert PR** cho thay đổi gây lỗi; không force-push `main` và không bypass branch protection.
3. Chờ `quality-gate` xanh.
4. Merge revert PR theo quy trình human approval bình thường.
5. Chờ Cloudflare deploy commit revert.
6. Xác nhận Production Smoke trả cùng expected/production fingerprint và các semantic checks đều PASS.
7. Ghi lại nguyên nhân, phạm vi ảnh hưởng và corrective action trong PR/issue liên quan.

## Khi nào không rollback

Không rollback chỉ vì Git SHA production không thể quan sát trực tiếp. P3.2 xác minh **public serving equivalence** bằng deterministic fingerprint. Chỉ rollback khi có bằng chứng production stale, response regression hoặc deploy lỗi thực tế.

## Recovery evidence

Một incident được coi là đóng khi có đủ:

- `CI` xanh trên `main` hiện hành;
- `Production Smoke` xanh;
- expected fingerprint = production fingerprint;
- endpoint semantic checks không còn lỗi;
- nếu có rollback, revert PR và nguyên nhân được ghi nhận.
