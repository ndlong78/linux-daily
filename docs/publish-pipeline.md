# Publish Pipeline

P5.1 chuẩn hóa quy trình local trước khi mở/cập nhật PR bằng `tools/publish.py`; các phase sau bổ sung deterministic quality gates vào cùng contract này thay vì tạo pipeline song song.

## Prepare

Sau khi thêm hoặc sửa bài:

```bash
python tools/publish.py prepare
```

Pipeline regenerate các artifact deterministic qua `tools/build.py`, sau đó regenerate public Learning Dashboard và cập nhật content-mix report, taxonomy inventory, distro-coverage report cùng canonical P7 quality dashboard. Nó không commit, push, mở PR hay merge.

## Check

Trước khi push:

```bash
python tools/publish.py check
```

Mode này không ghi file. Nó kiểm build/artifact freshness, taxonomy/content mix, P10 curriculum planner + publication readiness + coverage intelligence, distro/command quality, freshness + lifecycle, P7 quality dashboard, P8 learning metadata/progression/dashboard, P9 Advanced Lab + Linux ↔ FreeBSD interoperability, **P10.5 Daily Operations Dashboard input consistency**, release metadata, performance budget và repository health. Nếu một bước fail, pipeline dừng ngay tại lỗi đầu tiên để feedback rõ ràng.

External HTTP link checking không nằm trong local pipeline vì phụ thuộc mạng và website bên thứ ba; CI vẫn chạy policy retry/non-flaky riêng.

## P7 quality foundation

- `tools/distro_coverage.py --check`: explicit Ubuntu/Xubuntu, Debian, Fedora, FreeBSD coverage + FreeBSD portability.
- `tools/command_quality.py`: static command/config safety.
- `tools/content_freshness.py`: `current` / `review-due` / `historically-valid` / `superseded` policy.
- `tools/quality_dashboard.py --check`: canonical P7 derived snapshot.

Chi tiết: `docs/distro-portability.md`, `docs/command-config-quality.md`, `docs/content-freshness.md`, `docs/quality-dashboard.md`.

## P8 learning experience

- `tools/learning_metadata.py`: difficulty + prerequisite DAG.
- `tools/topic_progression.py`: prerequisite ordering + difficulty progression.
- `tools/learning_dashboard.py --check`: public derived learning dashboard.

Chi tiết: `docs/learning-paths.md`, `docs/difficulty-prerequisites.md`, `docs/topic-progression.md`, `docs/learning-dashboard.md`.

## P9 advanced labs

- `tools/lab_contract.py`: topology/risk/rollback/failure/verification contract.
- `tools/interoperability_lab.py`: Linux ↔ FreeBSD real-role interoperability artifact contract.

Chi tiết: `docs/advanced-lab-framework.md`, `docs/linux-freebsd-interoperability-lab.md`.

## P10 sustainable daily publishing

### Curriculum planner

```bash
python3 tools/curriculum_planner.py --json
```

`curriculum-plan.json` là planning intent 14 ngày; planner resolve issue number runtime và không sửa `state.json`.

### Publication readiness

```bash
python3 tools/publication_readiness.py --json
```

Readiness kiểm prerequisite, semantic collision, 4-platform review scope và minimum primary sources. Nó trả lời “topic có sẵn sàng để authoring chưa”, không trả lời “đã tới cadence chưa”.

### Coverage intelligence

```bash
python3 tools/coverage_intelligence.py --json
```

Coverage Intelligence derive capability gap từ catalog + corpus + learning paths + plan nhưng không tự chỉnh queue.

### Content lifecycle

```bash
python3 tools/content_lifecycle.py --json
```

Lifecycle resolve replacement lineage và canonical guidance; invalid replacement graph hard-fail.

### P10.5 Daily Operations Dashboard

```bash
python3 tools/daily_operations_dashboard.py
python3 tools/daily_operations_dashboard.py --json
python3 tools/daily_operations_dashboard.py --check
```

Dashboard import trực tiếp cadence/planner/readiness/P7/P8/lifecycle/coverage signals thành daily decision view. `publish.py check` chạy `--check` như gate read-only; dashboard không nằm trong `prepare` và không tự ghi artifact canonical.

Muốn lưu một snapshot vận hành theo nhu cầu:

```bash
python3 tools/daily_operations_dashboard.py --output /tmp/linux-daily-operations.md
```

Mặc định các signal phụ thuộc thời gian dùng `state.last_published_date` để deterministic. Operator có thể truyền `--as-of YYYY-MM-DD` khi cần xem trạng thái ở ngày khác.

Operating model: `docs/daily-operations-dashboard.md`.

## Human control

Publish automation chỉ giảm thao tác lặp lại. Branch, PR review, merge và release vẫn giữ human approval; pipeline không có quyền tự push `main` hoặc bypass `quality-gate`.
