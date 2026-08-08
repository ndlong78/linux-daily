# Audit & Report Automation

P5.2 gom các tín hiệu vận hành hiện có thành một audit snapshot duy nhất mà không tạo source of truth mới. Từ P7.4, report cũng nhúng quality evidence từ dashboard aggregator dùng chung.

## Local audit

```bash
python tools/audit_report.py
```

Local mode dùng repository health, content mix, publication metadata và P7 quality aggregation; không gọi GitHub API hoặc production.

P7 quality section tái sử dụng:

- distro coverage / FreeBSD portability từ P7.1;
- command/config findings từ P7.2;
- freshness state từ P7.3;
- source-backed technical review evidence.

`ATTENTION` như historical distro debt hoặc `review-due` vẫn xuất hiện trong remediation queue nhưng không tự làm audit fail. Hard errors từ underlying validators/source gate mới làm audit fail.

## Full operational audit

```bash
GITHUB_REPOSITORY=ndlong78/linux-daily \
GITHUB_TOKEN=... \
python tools/audit_report.py --github --production --output audit-report.md
```

Full mode bổ sung latest CI/Production Smoke evidence và một lần production observability trực tiếp.

## Scheduled workflow

Workflow `Audit Report` chạy mỗi Thứ Hai lúc 08:15 Asia/Ho_Chi_Minh và có thể chạy thủ công. Report được đưa vào GitHub Actions Job Summary và lưu artifact 30 ngày.

Workflow chỉ có quyền `contents: read` và `actions: read`; P7.4 không cần thay permission. Workflow không commit report, không push branch, không merge PR và không release.

Audit fail khi repository/content-mix/P7 hard gate có lỗi, latest main CI/Production Smoke đang fail, hoặc production observability phát hiện serving drift/semantic error. Trạng thái UNKNOWN của GitHub evidence không làm local offline audit fail.

## Dashboard relationship

`docs/quality-dashboard.md` là canonical deterministic snapshot dùng ngày publication từ `state.json`. Weekly audit không đọc snapshot đó như source of truth; nó gọi `tools/quality_dashboard.py` APIs với ngày audit thực tế để freshness queue phản ánh đúng thời điểm.

Report và dashboard đều là derived evidence. Metadata/artifact trong repository, P7 validators, GitHub Actions và production serving state vẫn là nguồn dữ liệu gốc.
