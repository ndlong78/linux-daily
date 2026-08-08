# Linux Daily — Distro Coverage & Portability Matrix

> Báo cáo này được sinh deterministic từ nội dung bài viết. Presence coverage là guardrail cấu trúc, không thay thế technical review về tính đúng đắn của từng lệnh.

## Snapshot

- Published posts: **19**
- Complete Ubuntu/Xubuntu + Debian + Fedora + FreeBSD coverage: **19/19**
- Posts with explicit FreeBSD code blocks: **19/19**
- Linux-only command/path violations inside FreeBSD blocks: **0**

| Platform | Posts with explicit coverage |
|---|---:|
| Ubuntu / Xubuntu | 19/19 |
| Debian | 19/19 |
| Fedora | 19/19 |
| FreeBSD | 19/19 |

## Review queue

- Không có bài nào vi phạm baseline P7.1 hiện tại.

## Policy boundary

- Mỗi bài phải nhắc rõ Ubuntu/Xubuntu, Debian, Fedora và FreeBSD.
- Mỗi bài phải có ít nhất một code block FreeBSD được đánh dấu `class="bsd"` để tách semantics khỏi Linux.
- Gate chỉ hard-fail các Linux-only command/path rõ ràng trong block FreeBSD; nó không suy đoán portability từ mọi token CLI.
- Technical reviewer vẫn chịu trách nhiệm kiểm package name, service name, filesystem path, firewall model và behavior thực tế trên từng HĐH.
