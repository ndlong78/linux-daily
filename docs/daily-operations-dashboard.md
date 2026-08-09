# P10.5 — Daily Operations Dashboard

P10.5 hợp nhất các tín hiệu vận hành của Linux Daily thành **một derived view read-only**. Dashboard không tạo thêm source of truth và không tự sửa `state.json`, `curriculum-plan.json`, learning metadata, freshness/lifecycle policy hoặc backlog.

## Mục tiêu

Operator cần trả lời nhanh các câu hỏi hằng ngày:

- bài gần nhất là bài nào và cadence 1 ngày đã tới nhịp chưa;
- topic kế tiếp trong curriculum plan là gì;
- topic đó đã qua Publication Readiness Gate chưa;
- P7 quality còn hard error/remediation nào;
- learning paths có phủ toàn bộ corpus không;
- lifecycle có bài `review-due`, `historically-valid` hoặc `superseded` nào;
- coverage intelligence đang thấy capability gap nào nên đưa vào backlog.

## Chạy dashboard

Human-readable snapshot:

```bash
python3 tools/daily_operations_dashboard.py
```

Structured output:

```bash
python3 tools/daily_operations_dashboard.py --json
```

Ghi một snapshot theo nhu cầu operator/audit:

```bash
python3 tools/daily_operations_dashboard.py \
  --output /tmp/linux-daily-operations.md
```

Kiểm tính nhất quán của toàn bộ input:

```bash
python3 tools/daily_operations_dashboard.py --check
```

`tools/publish.py check` gọi `--check` như một gate read-only. Dashboard không được đưa vào `publish.py prepare` vì output vận hành theo thời điểm không phải public-site artifact canonical.

## Nguồn dữ liệu

Dashboard import trực tiếp các module hiện hành thay vì reimplement rule:

| Tín hiệu | Source of truth / validator |
|---|---|
| publication + cadence | `state.json`, post metadata, `tools/cadence.py` |
| next planned topic | `curriculum-plan.json`, `tools/curriculum_planner.py` |
| authoring readiness | `tools/publication_readiness.py` |
| content quality | `tools/quality_dashboard.py` và P7 validators |
| learning coverage/progression | `tools/learning_dashboard.py` và P8 validators |
| lifecycle/canonical guidance | `freshness.json`, `tools/content_lifecycle.py` |
| backlog/capability gaps | `coverage-catalog.json`, `tools/coverage_intelligence.py` |

Nếu upstream validator hard-fail, Daily Operations Dashboard cũng fail. `ATTENTION`/remediation queue vẫn được surface nhưng không bị đổi nhãn thành hard failure.

## Deterministic behavior

Nếu không truyền `--as-of`, dashboard dùng `state.last_published_date` cho các signal phụ thuộc ngày. Điều này giữ `publish.py check` deterministic và không biến CI thành time-bomb chỉ vì đồng hồ chạy.

Operator muốn xem trạng thái ở ngày khác có thể chạy:

```bash
python3 tools/daily_operations_dashboard.py --as-of 2026-09-01
```

Cadence trong dashboard dùng `cadence.DEFAULT_INTERVAL_DAYS`; không hard-code một nhịp riêng. Vì vậy thay đổi cadence hợp lệ sẽ tự phản ánh trong operational view.

## Boundary

P10.5 không:

- tự sinh hoặc publish bài;
- tự sửa curriculum queue;
- tự đánh dấu bài `superseded`;
- tự tạo remediation PR;
- gọi GitHub/production network API trong deterministic publish gate;
- thay thế `tools/operations_dashboard.py`/weekly audit dùng cho workflow và production evidence.

`tools/operations_dashboard.py` tiếp tục phục vụ repository/GitHub Actions operational evidence. P10.5 tập trung vào **daily publishing decision layer**: cadence → plan → readiness → quality/learning/lifecycle → backlog.
