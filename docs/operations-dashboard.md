# Operations Dashboard

P3.1 cung cấp một operational report dễ đọc mà **không tạo source of truth mới**. Dashboard chỉ tổng hợp dữ liệu đã tồn tại trong repository và GitHub Actions.

## Tín hiệu hiển thị

- Publication freshness: latest issue, ngày xuất bản và tuổi bài so với cadence 2 ngày.
- Repository health: kết quả collector deterministic từ `tools/repo_health.py`.
- Artifact inventory: posts, generated pages, technical sources, social images, WOFF2 fonts, RSS items và sitemap URLs.
- CI state: workflow run mới nhất trên `main` của `CI`.
- Smoke state: workflow run mới nhất trên `main` của `Production Smoke`.

P3.1 **không** khẳng định production đang chạy commit nào. Deployment fingerprint, cache headers và stale-production detection thuộc P3.2.

## Chạy local

```bash
python3 tools/operations_dashboard.py
```

Local mode không gọi GitHub API nên CI và Production Smoke được hiển thị là `UNKNOWN / offline mode`. Đây là hành vi chủ ý; script không suy diễn trạng thái remote từ dữ liệu cũ.

Có thể cố định ngày để audit hoặc test deterministic:

```bash
python3 tools/operations_dashboard.py --as-of 2026-08-08
```

## Chạy với GitHub Actions state

Trong GitHub Actions, workflow `.github/workflows/operations-dashboard.yml` chạy:

```bash
python tools/operations_dashboard.py \
  --github \
  --output operations-dashboard.md
```

Script đọc `GITHUB_REPOSITORY` và `GITHUB_TOKEN`, sau đó truy vấn workflow run mới nhất trên `main`. Token chỉ cần quyền read cho repository contents và Actions.

Dashboard được xuất ở hai nơi:

1. GitHub Actions **Job Summary** để operator đọc nhanh.
2. Artifact `operations-dashboard` giữ 14 ngày để đối chiếu lịch sử gần.

Workflow chạy lúc 07:45 Asia/Ho_Chi_Minh, sau Production Smoke 07:30, và chạy lại khi Production Smoke hoàn tất.

## Failure semantics

- Repository health deterministic lỗi: script exit non-zero vì đây là lỗi local có thể tái hiện.
- GitHub API timeout/unavailable: workflow state hiển thị `UNKNOWN`; collector vẫn tạo report để operator thấy dashboard đang degraded thay vì mất toàn bộ report.
- CI/Production Smoke có conclusion `failure`: dashboard hiển thị `FAIL`, nhưng report vẫn là observability output, không thay thế quality gate của workflow gốc.

## Source-of-truth boundaries

| Tín hiệu | Source of truth |
|---|---|
| Latest issue / publication date | `posts/post-*.html` + `state.json` |
| Artifact counts / repository health | repository artifacts + `tools/repo_health.py` |
| CI state | GitHub Actions workflow `CI` |
| Production smoke state | GitHub Actions workflow `Production Smoke` |
| Deployment fingerprint | Chưa thuộc P3.1; triển khai ở P3.2 |

Không commit một file dashboard “latest” vào `main`, vì snapshot đó sẽ nhanh chóng stale và dễ bị hiểu nhầm là trạng thái thật của hệ thống.
