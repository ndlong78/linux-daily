# Publish Pipeline

P5.1 chuẩn hóa quy trình local trước khi mở/cập nhật PR bằng `tools/publish.py`; các phase sau có thể bổ sung deterministic quality gates vào cùng contract này thay vì tạo pipeline song song.

## Prepare

Sau khi thêm hoặc sửa bài:

```bash
python tools/publish.py prepare
```

Pipeline regenerate các artifact deterministic qua `tools/build.py`, cập nhật content-mix report, taxonomy inventory và distro-coverage report. Nó không commit, push, mở PR hay merge.

## Check

Trước khi push:

```bash
python tools/publish.py check
```

Mode này không ghi file. Nó kiểm build/artifact freshness, taxonomy, content mix, distro coverage/FreeBSD portability, command/config static quality, content freshness policy, release metadata, performance budget và repository health. Nếu một bước fail, pipeline dừng ngay tại lỗi đầu tiên để feedback rõ ràng.

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

## Human control

Publish automation chỉ giảm thao tác lặp lại. Branch, PR review, merge và release vẫn giữ human approval; pipeline không có quyền tự push `main` hoặc bypass `quality-gate`.
