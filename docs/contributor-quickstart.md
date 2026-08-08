# Contributor Quickstart

Mục tiêu của tài liệu này là đưa một contributor mới từ **clone repo → sửa nội dung/code → PR xanh** mà không cần biết lịch sử dự án.

## 1. Chuẩn bị môi trường

Yêu cầu tối thiểu:

- Git.
- Python 3.11+.
- Một fork/branch có thể mở Pull Request vào `main`.

Kiểm tra nhanh:

```bash
python3 tools/contributor.py doctor
```

Cài dependency phát triển:

```bash
python3 -m pip install -e ".[dev]"
```

## 2. Tạo branch

Luôn bắt đầu từ `main` mới nhất và không push trực tiếp vào `main`.

```bash
git switch main
git pull --ff-only
git switch -c contributor/<short-topic>
```

## 3. Chọn loại đóng góp

### Sửa code / website / tài liệu

Giữ diff nhỏ, cập nhật test khi thay đổi hành vi, và không sửa generated artifact bằng tay nếu đã có generator tương ứng.

### Thêm hoặc sửa bài Linux Daily

Đọc trước `CONTRIBUTING.md` và phần source-backed review trong `AGENTS.md`. Bài mới phải giữ metadata `ld-meta`, taxonomy hiện có, khác biệt Ubuntu/Debian/Fedora/FreeBSD và nguồn official/upstream cho claim kỹ thuật chính.

Không tự chọn axis tùy ý: chạy:

```bash
python3 tools/content_mix.py --check
```

để thấy issue/axis kế tiếp theo cadence hiện hành.

## 4. Regenerate artifact

Sau khi sửa bài hoặc metadata:

```bash
python3 tools/publish.py prepare
```

Lệnh này regenerate các artifact/report deterministic. Review `git diff` sau khi chạy; không commit file ngoài scope mà bạn không hiểu.

## 5. Chạy validation trước khi push

```bash
python3 tools/publish.py check
```

Nếu PR thay URL/source, chạy thêm:

```bash
python3 tools/check_links.py --external --workers 8
```

Nếu thay GitHub Actions workflow:

```bash
python3 tools/workflow_safety.py
```

## 6. Mở Pull Request

PR phải mô tả mục tiêu, scope, guardrails và cách test. Dùng checklist mặc định trong `.github/pull_request_template.md`.

Không merge khi `quality-gate` chưa xanh. Không dùng `--admin`, auto-merge workflow hoặc cách khác để bypass branch protection.

## 7. Khi CI fail

Đọc **step đầu tiên fail**, sửa nguyên nhân gốc rồi push commit mới. Không nới lỏng validator chỉ để làm CI xanh nếu validator đang phản ánh regression thật.

Các nhóm lỗi thường gặp:

- `Ruff` / `Pytest`: lỗi code/test.
- `Deterministic publish pipeline`: generated artifact hoặc metadata chưa đồng bộ.
- `Workflow safety policy`: quyền/trigger workflow vượt safety boundary.
- `External link check`: URL/source lỗi; phân biệt lỗi mạng tạm thời với URL thực sự hỏng.

## 8. Definition of done

Một contribution sẵn sàng review khi:

- diff chỉ chứa scope dự kiến;
- test mới có nếu thay đổi hành vi;
- `python3 tools/publish.py check` pass;
- external/workflow checks bổ sung pass nếu áp dụng;
- PR giải thích rõ rủi ro/giới hạn;
- GitHub Actions `quality-gate` xanh.

`CONTRIBUTING.md` là policy cho contributor; `AGENTS.md` là operating contract dành cho AI agent. Contributor người thật không cần làm theo các bước scheduler/cadence orchestration dành riêng cho agent, trừ khi đang tạo bài mới.
