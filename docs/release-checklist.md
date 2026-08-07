# Linux Daily — Release Checklist

Dùng checklist này trước một release/tag hoặc thay đổi production đáng kể. Bài Linux Daily thường ngày vẫn đi theo quy trình PR + quality gate chuẩn.

## Repository

- [ ] Branch được tạo từ `main` mới nhất.
- [ ] Không có secret/token/private key trong diff.
- [ ] Diff chỉ chứa scope đã mô tả trong PR.
- [ ] `CHANGELOG.md` được cập nhật nếu thay đổi đáng chú ý.

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

## Production

- [ ] Pull request đã được review và merge sau khi CI xanh.
- [ ] Cloudflare Worker deploy commit mới.
- [ ] Production smoke xanh cho homepage, feed, sitemap, robots, latest post và social image.
- [ ] Canonical origin vẫn là `https://linux.no.id.vn/`.

## Rollback

Nếu production regression sau merge:

1. Xác định commit/PR gây lỗi.
2. Revert bằng PR mới thay vì sửa trực tiếp `main`.
3. Đợi `quality-gate` xanh.
4. Merge revert và xác nhận Cloudflare deploy.
5. Chạy lại production smoke.
