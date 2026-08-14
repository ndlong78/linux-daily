# Linux Daily — Distro Coverage & Portability Matrix

> Báo cáo này được sinh deterministic từ nội dung bài viết. Presence coverage là guardrail cấu trúc, không thay thế technical review về tính đúng đắn của từng lệnh.

## Snapshot

- Published posts: **45**
- Complete Ubuntu/Xubuntu + Debian + Fedora + FreeBSD coverage: **40/45**
- Posts with explicit FreeBSD code blocks: **45/45**
- Linux-only command/path violations inside FreeBSD blocks: **0**
- Full coverage enforcement starts at issue: **#020**

| Platform | Posts with explicit coverage |
|---|---:|
| Ubuntu / Xubuntu | 40/45 |
| Debian | 44/45 |
| Fedora | 43/45 |
| FreeBSD | 45/45 |

## Historical review queue

- #007 thiếu distro coverage: Ubuntu / Xubuntu
- #008 thiếu distro coverage: Ubuntu / Xubuntu, Fedora
- #010 thiếu distro coverage: Ubuntu / Xubuntu
- #014 thiếu distro coverage: Ubuntu / Xubuntu
- #017 thiếu distro coverage: Ubuntu / Xubuntu, Debian, Fedora

## Policy boundary

- Các bài trước #020 được inventory như technical debt; thiếu coverage cũ xuất hiện trong review queue nhưng không làm CI đỏ.
- Từ #020, bài mới phải nhắc rõ Ubuntu/Xubuntu, Debian, Fedora và FreeBSD.
- Mọi bài phải có ít nhất một code block FreeBSD được đánh dấu `class="bsd"` để tách semantics khỏi Linux.
- Gate hard-fail các Linux-only command/path rõ ràng trong block FreeBSD; nó không suy đoán portability từ mọi token CLI.
- Technical reviewer vẫn chịu trách nhiệm kiểm package name, service name, filesystem path, firewall model và behavior thực tế trên từng HĐH.
