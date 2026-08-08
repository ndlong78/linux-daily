# Publish Pipeline

P5.1 chuẩn hóa quy trình local trước khi mở/cập nhật PR bằng `tools/publish.py`; các phase sau bổ sung deterministic quality gates vào cùng contract này thay vì tạo pipeline song song.

## Prepare

Sau khi thêm hoặc sửa bài:

```bash
python tools/publish.py prepare
```

Pipeline regenerate các artifact deterministic qua `tools/build.py`, gồm public Learning Paths page, rồi cập nhật content-mix report, taxonomy inventory, distro-coverage report và canonical P7 quality dashboard. Nó không commit, push, mở PR hay merge.

## Check

Trước khi push:

```bash
python tools/publish.py check
```

Mode này không ghi file. Nó kiểm build/artifact freshness, Learning Paths coverage/page drift, taxonomy, content mix, distro coverage/FreeBSD portability, command/config static quality, content freshness policy, P7 quality-dashboard consistency, release metadata, performance budget và repository health. Nếu một bước fail, pipeline dừng ngay tại lỗi đầu tiên để feedback rõ ràng.

External HTTP link checking không nằm trong local pipeline vì phụ thuộc mạng và website bên thứ ba; CI vẫn chạy policy retry/non-flaky riêng.

## P7.1 distro portability

`tools/distro_coverage.py --check` là một phần của publish contract. Nó kiểm explicit coverage của Ubuntu/Xubuntu, Debian, Fedora và FreeBSD, yêu cầu FreeBSD code block riêng và chặn các Linux-only command/path có tín hiệu cao nếu bị đặt trong block FreeBSD.

Chi tiết policy và false-positive boundary: `docs/distro-portability.md`.

## P7.2 command/config quality

`tools/command_quality.py` chạy read-only trong `publish.py check`. Gate không thực thi code block; nó static-scan các anti-pattern có tín hiệu cao, inventory privilege/destructive examples và áp enforcement chặt hơn cho bài mới từ #020.

Các bài lịch sử có finding context-sensitive được đưa vào review queue thay vì rewrite tự động. Repository-wide blocker như remote pipe-to-shell, `chmod 777` hoặc catastrophic recursive operations vẫn fail ngay.

Chi tiết policy: `docs/command-config-quality.md`.

## P7.3 content freshness

`tools/content_freshness.py` đọc `freshness.json` và tính trạng thái `current`, `review-due` hoặc `historically-valid` mà không sửa bài viết.

`review-due` được hiển thị như actionable queue nhưng không làm publish CI fail mặc định chỉ vì thời gian trôi qua. Policy/ledger inconsistency vẫn fail cứng. Khi cần audit nghiêm ngặt có thể chạy:

```bash
python3 tools/content_freshness.py --fail-review-due
```

Structured data cho audit/dashboard:

```bash
python3 tools/content_freshness.py --json
```

Chi tiết policy: `docs/content-freshness.md`.

## P7.4 quality dashboard

`tools/quality_dashboard.py` **import trực tiếp** kết quả của P7.1–P7.3 và source-backed gate; nó không định nghĩa lại rule kỹ thuật.

Canonical dashboard được regenerate bằng:

```bash
python3 tools/quality_dashboard.py
```

Committed `docs/quality-dashboard.md` dùng `state.json:last_published_date` làm `as-of`, vì vậy snapshot deterministic và không tự drift chỉ do đồng hồ chạy. `publish.py check` xác nhận snapshot này còn đồng bộ.

Khi cần xem quality tại một ngày thực tế khác:

```bash
python3 tools/quality_dashboard.py --as-of 2026-11-15
python3 tools/quality_dashboard.py --as-of 2026-11-15 --json
```

Weekly `tools/audit_report.py` gọi cùng aggregator với ngày audit thực tế, nên `review-due` vẫn xuất hiện đúng lúc mà không biến committed dashboard thành time-bomb.

Dashboard chỉ là derived view. Source of truth vẫn là post metadata/content, `freshness.json`, source gate và validators P7.1–P7.3.

## P8.1 learning paths

`tools/build.py` gọi `tools/learning_paths.py`, nên contributor không phải nhớ thêm một pipeline riêng. `learning-paths.json` chỉ lưu curriculum ordering bằng issue ID; generator resolve title/date/URL từ post metadata.

Regenerate trực tiếp khi đang chỉnh path:

```bash
python3 tools/learning_paths.py
```

Kiểm drift/schema/coverage:

```bash
python3 tools/learning_paths.py --check
```

Gate fail nếu path tham chiếu issue không tồn tại, lặp issue trong cùng path hoặc có bài published chưa thuộc learning path nào. Chi tiết: `docs/learning-paths.md`.

## Human control

Publish automation chỉ giảm thao tác lặp lại. Branch, PR review, merge và release vẫn giữ human approval; pipeline không có quyền tự push `main` hoặc bypass `quality-gate`.
