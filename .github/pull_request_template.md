## Mục tiêu

<!-- PR giải quyết vấn đề gì? -->

## Scope

<!-- Liệt kê ngắn gọn các file/nhóm thay đổi chính. -->

## Guardrails

<!-- Những gì PR cố ý KHÔNG thay đổi. -->

## Kiểm thử

`tools/pr_preflight.py` đã bao gồm `publish.py prepare`, `pr_hygiene.py`, `ruff`,
`pytest`, `workflow_safety.py` và `publish.py check` — chạy nó là đủ cho các gate local.

- [ ] `python3 tools/pr_preflight.py`
- [ ] `quality-gate` trên GitHub Actions xanh
- [ ] External link check nếu PR thay URL/source (`python3 tools/check_links.py --external`)
- [ ] Production smoke nếu PR ảnh hưởng serving/deploy

<!-- Đánh dấu "không áp dụng" thay vì bỏ trống nếu một mục không liên quan tới PR. -->

## Git / CI hygiene

- [ ] Branch được tạo từ `main`; không push trực tiếp `main`
- [ ] Không track file tạm hoặc helper gắn số PR
- [ ] Commit subject mô tả rõ thay đổi; không dùng `x/tmp/test/wip/placeholder/...`
- [ ] CI chỉ validate; generated artifacts đã được tạo trước commit/push
- [ ] Không có secret/credential trong diff
- [ ] Khi merge, dùng **Squash and merge**

Workflow tự commit/push ngược branch bị cấm, trừ `release.yml` và
`materialize-artifacts.yml` — cả hai chỉ chạy qua `workflow_dispatch` có chuỗi xác nhận
và được `tools/workflow_safety.py` cưỡng chế. PR nào chạm vào ranh giới này phải nói rõ
trong Review notes.

- [ ] PR không thêm workflow tự commit/push ngược branch, hoặc đã giải thích ở Review notes

## Content / technical review

<!-- Reviewer kỹ thuật có thể dùng docs/technical-review-guide.md. -->

- [ ] Không áp dụng (không sửa bài)
- [ ] Sources official/upstream đã được kiểm chứng và hỗ trợ đúng claim
- [ ] Ubuntu/Xubuntu, Debian, Fedora và FreeBSD được phân biệt đúng nơi cần thiết
- [ ] FreeBSD được xử lý riêng, không gán command/path/service model của Linux
- [ ] Rollback/destructive semantics/restore evidence đã được rà soát nếu có
- [ ] Verification steps đủ để chứng minh trạng thái sau thay đổi

## Website

- [ ] Không áp dụng
- [ ] Canonical/OG/RSS/sitemap vẫn nhất quán
- [ ] Accessibility không regression
- [ ] Không thêm external font/runtime dependency mới

## Review notes

<!-- Rủi ro, giới hạn hoặc điểm reviewer cần chú ý. -->
