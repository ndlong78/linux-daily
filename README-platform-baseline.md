# Current platform baseline

Linux Daily dùng `platform-baseline.json` làm source of truth cho target OS/version của bài mới từ #070.

Baseline xác minh ngày **2026-09-07**:

- Ubuntu/Xubuntu 26.04 LTS
- Debian 13 stable (point release hiện tại: 13.6, codename `trixie`)
- Fedora 44
- FreeBSD 15.1-RELEASE

Bằng chứng lịch sử không được đổi sang release mới nếu claim/lệnh của bài chưa được re-verify trên tài liệu hoặc runtime phù hợp.

Khi một OS phát hành bản mới, cập nhật `platform-baseline.json`, `STYLE.md` và regression test trong cùng một maintenance PR; không sửa tay `tested_on`/`documentation_verified_on` của bài cũ chỉ để đồng bộ version.
