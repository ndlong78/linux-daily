## Mục tiêu

<!-- PR này giải quyết vấn đề gì? -->

## Thay đổi chính

<!-- Liệt kê ngắn gọn các thay đổi có chủ đích. -->

## Không thay đổi

<!-- Ghi rõ các phần nằm ngoài scope để reviewer dễ kiểm tra. -->

## Kiểm thử

- [ ] `ruff check tools/ tests/`
- [ ] `pytest -q`
- [ ] `python3 tools/build.py --check`
- [ ] `quality-gate` trên GitHub Actions xanh

## Review checklist

- [ ] Không có secret/credential trong diff.
- [ ] FreeBSD được xử lý riêng nếu nội dung có liên quan.
- [ ] Các thay đổi có khả năng phá hủy hệ thống có rollback/guardrail rõ ràng.
- [ ] Nguồn technical review là official/upstream nếu PR sửa/thêm bài Linux Daily.
