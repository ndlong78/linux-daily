## Mục tiêu

<!-- PR giải quyết vấn đề gì? -->

## Scope

<!-- Liệt kê ngắn gọn các file/nhóm thay đổi chính. -->

## Guardrails

<!-- Những gì PR cố ý KHÔNG thay đổi. -->

## Kiểm thử

- [ ] `python3 tools/publish.py check`
- [ ] External link check nếu PR thay URL/source
- [ ] `python3 tools/workflow_safety.py` nếu PR thay GitHub Actions
- [ ] Production smoke nếu PR ảnh hưởng serving/deploy

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
