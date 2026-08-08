# Linux Daily — Release Checklist

Dùng checklist này trước một release/tag hoặc thay đổi production đáng kể. Bài Linux Daily thường ngày vẫn đi theo quy trình PR + quality gate chuẩn.

## Repository & version

- [ ] Branch được tạo từ `main` mới nhất.
- [ ] Không có secret/token/private key trong diff.
- [ ] Diff chỉ chứa scope đã mô tả trong PR.
- [ ] `VERSION` dùng strict SemVer `X.Y.Z`.
- [ ] `CHANGELOG.md` có section đúng version, đã review qua PR.
- [ ] Tag dự kiến là `vX.Y.Z` và chưa tồn tại.

Kiểm metadata release:

```bash
python3 tools/release.py validate
python3 tools/release.py notes
```

## Build & tests

```bash
python3 -m pip install -e ".[dev]"
ruff check tools/ tests/
pytest -q
python3 tools/build.py --check
python3 tools/check_links.py --external --workers 8
python3 tools/repo_health.py
```

- [ ] Ruff xanh.
- [ ] Pytest xanh.
- [ ] Generated artifacts đồng bộ.
- [ ] Source-backed gate xanh.
- [ ] Website/SEO gate xanh.
- [ ] Accessibility gate xanh.
- [ ] Self-host font gate xanh.
- [ ] Internal/external link check xanh.

## Website artifacts

- [ ] `index.html` phản ánh đúng post inventory.
- [ ] RSS chứa các bài mới nhất đúng canonical URL.
- [ ] Sitemap khớp page inventory.
- [ ] `robots.txt` trỏ đúng sitemap public.
- [ ] Social image metadata trỏ tới asset tồn tại.
- [ ] Không có `CNAME` hoặc GitHub Pages hostname trong public artifacts.

## Production evidence

- [ ] Pull request release metadata đã review và merge sau khi CI xanh.
- [ ] Cloudflare Worker đã deploy `main` mới.
- [ ] `Production Smoke` xanh trên chính SHA hiện tại của `main`.
- [ ] Expected fingerprint = production fingerprint.
- [ ] Canonical origin vẫn là `https://linux.no.id.vn/`.

## Publish release

Release **không chạy tự động sau merge**. Từ GitHub Actions, chạy workflow `Release` bằng `workflow_dispatch`:

1. Nhập version đúng bằng nội dung `VERSION`, ví dụ `0.4.0`.
2. Nhập chuỗi xác nhận `release-v0.4.0`.
3. Workflow xác minh `CI` và `Production Smoke` đều `success` trên exact `main` SHA.
4. Workflow từ chối nếu tag/release đã tồn tại.
5. Curated notes được lấy từ CHANGELOG; GitHub bổ sung merged-PR notes.
6. Chỉ sau tất cả gate trên workflow mới tạo tag `vX.Y.Z` và GitHub Release.

Không dùng workflow release để sửa CHANGELOG hoặc `VERSION` trực tiếp trên `main`; các file này luôn phải đi qua PR.

## Rollback

Nếu production regression sau merge/release:

1. Xác định commit/PR gây lỗi.
2. Revert bằng PR mới thay vì sửa trực tiếp `main`.
3. Đợi `quality-gate` xanh.
4. Merge revert và xác nhận Cloudflare deploy.
5. Chạy lại Production Smoke và xác nhận serving fingerprint.
6. Không xóa/rewrite tag đã phát hành để che lịch sử; nếu cần phát hành bản sửa, tăng patch version và tạo release mới.
