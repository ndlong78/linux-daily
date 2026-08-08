# Issue guidelines

Linux Daily dùng GitHub Issue Forms để thu thập đủ thông tin ngay từ đầu và giảm vòng hỏi lại khi triage.

## Chọn đúng form

- **Bug report**: website, tooling, CI, workflow hoặc production serving hoạt động sai so với mong đợi.
- **Content / technical correction**: bài Linux/Unix có lệnh, cấu hình, distro semantics, FreeBSD handling, nguồn kỹ thuật hoặc operational warning cần sửa.
- **Feature proposal**: đề xuất capability hoặc cải tiến mới cho content discovery, website, tooling, automation, operations hoặc contributor experience.

Không dùng public issue để báo lỗ hổng bảo mật. Chọn liên kết **Security vulnerability** trong issue chooser và làm theo `SECURITY.md` / GitHub Security Policy.

## Nội dung tối thiểu để triage

Bug nên có hiện tượng thực tế, kết quả mong đợi và cách tái hiện. Nếu liên quan CI/production, thêm SHA, PR, workflow run hoặc URL khi có thể.

Content correction nên chỉ ra bài/phần có vấn đề, correction đề xuất và ưu tiên kèm tài liệu official/upstream hiện hành. Nếu correction liên quan networking, storage, auth hoặc automation, nêu cả rollback/destructive impact nếu có.

Feature proposal nên bắt đầu từ vấn đề cần giải quyết, sau đó mới mô tả outcome mong muốn. Đề xuất không được dựa trên việc bypass CI, branch protection hoặc human approval cho merge/release.

## Từ issue đến contribution

Issue không bắt buộc phải có PR ngay. Nếu muốn triển khai thay đổi:

1. Đọc `docs/contributor-quickstart.md`.
2. Chạy `python3 tools/contributor.py doctor`.
3. Tạo feature branch từ `main` mới nhất.
4. Với generated artifacts, dùng `python3 tools/publish.py prepare` thay vì sửa tay.
5. Chạy `python3 tools/publish.py check` và các check bổ sung phù hợp.
6. Mở PR nhỏ, nêu rõ issue liên quan và chờ `quality-gate` xanh.

Issue Forms chỉ phục vụ intake/triage; chúng không thay source of truth trong repository và không kích hoạt workflow ghi/auto-merge nào.
