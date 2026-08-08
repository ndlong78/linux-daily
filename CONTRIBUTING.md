# Contributing to Linux Daily

Cảm ơn bạn đã muốn đóng góp cho Linux Daily. Repo này là static site kèm bộ công cụ Python để sinh bài, kiểm tra metadata, cadence, social assets và source-backed technical review.

## Nguyên tắc đóng góp

- Không push trực tiếp vào `main`; mọi thay đổi đi qua pull request.
- Giữ diff nhỏ, có mục tiêu rõ ràng và tránh trộn nhiều nhóm thay đổi không liên quan trong cùng một PR.
- Với bài Linux/Unix mới hoặc bài cũ được technical-review lại, ưu tiên nguồn `official`/`upstream` và tuân thủ source-backed gate hiện có.
- FreeBSD phải được xử lý riêng: không áp lệnh `systemd`, `apt`, `dnf`, `nftables` hoặc đường dẫn Linux sang FreeBSD.
- Với networking, firewall, storage, backup/restore, auth/permissions và automation shell, luôn kiểm tra rollback path và destructive flags.
- Không commit secret, token, password, private key hoặc dữ liệu nhạy cảm.

## Quy trình đề xuất

1. Đồng bộ branch từ `main` hiện tại.
2. Tạo feature branch có tên mô tả thay đổi.
3. Thực hiện thay đổi và cập nhật test/tài liệu liên quan.
4. Chạy quality gate local.
5. Mở pull request vào `main` và chờ CI xanh trước khi merge.

## Quality gate local

```bash
python3 -m pip install -e ".[dev]"
ruff check tools/ tests/
pytest -q
python3 tools/build.py --check
python3 tools/repo_health.py
```

Nếu thay đổi URL/source, chạy thêm external checker:

```bash
python3 tools/check_links.py --external --workers 8
```

Nếu thay đổi liên quan source-backed technical review, có thể chạy riêng:

```bash
python3 tools/validate_sources.py
```

## Khi sửa hoặc thêm bài Linux Daily

- Giữ đúng metadata `ld-meta` và cấu trúc HTML/template hiện hành.
- Không tự ý thay cadence trong `state.json` hoặc logic của `tools/cadence.py` nếu PR không nhằm thay đổi cadence.
- Không sao chép claim kỹ thuật cũ sang bài mới nếu claim đó chưa được kiểm chứng lại.
- Metadata nguồn và section `Nguồn kỹ thuật` hiển thị phải khớp nhau.
- Social copy phải đồng bộ với nội dung bài sau technical review.
- Không thêm Google Fonts/CDN runtime dependency; typography public dùng self-hosted assets trong `assets/fonts/`.
- Giữ accessibility baseline: skip link, `main` landmark, heading hierarchy và accessible SVG.

## Khi sửa website/pipeline

- Public canonical origin lấy từ `site.json`; không hard-code GitHub Pages URL.
- Repository không dùng `CNAME`; production serving nằm trên Cloudflare Worker.
- Generated files phải được tạo bằng tool hiện có, không sửa tay nếu có generator tương ứng.
- Nếu thêm validator mới, ưu tiên deterministic local check; network check phải có timeout/retry/non-flaky policy.
- Cập nhật `docs/architecture.md`, `docs/ROADMAP.md` hoặc `CHANGELOG.md` nếu thay đổi kiến trúc/milestone đáng chú ý.

## Pull request

PR nên nêu rõ:

- mục tiêu;
- file/phạm vi thay đổi;
- các guardrail hoặc điều kiện không thay đổi;
- cách đã kiểm thử;
- rủi ro hoặc giới hạn còn lại nếu có.

Repository có `.github/pull_request_template.md` làm checklist mặc định. Không merge khi `quality-gate` chưa xanh.

## Release / production change

Với release/tag hoặc thay đổi production đáng kể, dùng `docs/release-checklist.md`. Rollback phải đi qua PR/revert có CI thay vì sửa trực tiếp `main`.
