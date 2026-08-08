# Audit & Report Automation

P5.2 gom các tín hiệu vận hành hiện có thành một audit snapshot duy nhất mà không tạo source of truth mới.

## Local audit

```bash
python tools/audit_report.py
```

Local mode dùng repository health, content mix và publication metadata; không gọi GitHub API hoặc production.

## Full operational audit

```bash
GITHUB_REPOSITORY=ndlong78/linux-daily \
GITHUB_TOKEN=... \
python tools/audit_report.py --github --production --output audit-report.md
```

Full mode bổ sung latest CI/Production Smoke evidence và một lần production observability trực tiếp.

## Scheduled workflow

Workflow `Audit Report` chạy mỗi Thứ Hai lúc 08:15 Asia/Ho_Chi_Minh và có thể chạy thủ công. Report được đưa vào GitHub Actions Job Summary và lưu artifact 30 ngày.

Workflow chỉ có quyền `contents: read` và `actions: read`; nó không commit report, không push branch, không merge PR và không release.

Audit fail khi repository/content-mix có lỗi, latest main CI/Production Smoke đang fail, hoặc production observability phát hiện serving drift/semantic error. Trạng thái UNKNOWN của GitHub evidence không làm local offline audit fail.

Report là evidence dẫn xuất. Metadata/artifact trong repository, GitHub Actions và production serving state vẫn là nguồn dữ liệu gốc.
