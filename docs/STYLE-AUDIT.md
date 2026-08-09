# STYLE.md — Historical Content Audit Baseline

Baseline date: **2026-08-09**  
Scope: **Linux Daily #001–#040**  
Current enforcement: **toàn bộ series #001+**

## Trạng thái

Batch A–D đã backfill hoàn tất **#001–#040** theo contract `STYLE.md`. Không còn grandfather/legacy exemption: `tools/validate_style.py` sẽ fail CI nếu bất kỳ bài lịch sử hoặc bài mới nào regress.

## Contract được backfill

Mỗi bài đã migrate phải có:

- metadata hiển thị `Tested on` + `Last verified`;
- `ld-meta.tested_on`, `last_verified`, `changes_system`;
- Mục tiêu và Yêu cầu tiên quyết;
- mục `03 Các bước thực hiện` dùng `<ol class="steps">`;
- `language-*` cho mọi code block;
- `data-run-as="user|sudo|root"` cho shell command block;
- mục `04 Kiểm chứng` có Expected Output/Kết quả mong đợi;
- **Gỡ / Hoàn tác** khi `changes_system=true`;
- không có shell prompt `$`/`#` trong command block;
- placeholder theo dạng `<...>`;
- không chạy trực tiếp `curl | sh`;
- FreeBSD luôn tách riêng, không áp cơ chế Linux.

## Enforcement policy

`tools/validate_style.py` chạy hai chế độ:

```bash
python3 tools/validate_style.py
python3 tools/validate_style.py --audit
```

- mặc định: fail CI nếu **bất kỳ bài #001+** vi phạm;
- `--audit`: in chi tiết trạng thái của toàn bộ series;
- legacy exemption đã được đóng hoàn toàn sau Batch D.

## Kế hoạch backfill

| Batch | Bài | Trạng thái | Mục tiêu |
|---|---:|---|---|
| A | #001–#010 | **Hoàn tất trong PR #85** | Metadata + command semantics + rollback |
| B | #011–#020 | **Hoàn tất trong PR #87** | Metadata + step/verification + automation safety |
| C | #021–#030 | **Hoàn tất trong PR #88** | Incident/lab structure + Expected Output + placeholders |
| D | #031–#040 | **Hoàn tất trong PR #89** | Chuẩn hóa các bài gần nhất và đóng legacy baseline |

Sau mỗi batch, chạy:

```bash
python3 tools/validate_style.py --audit
python3 tools/publish.py check
```

Batch D nâng `BACKFILLED_THROUGH` lên 40. Vì #041+ vốn đã enforced, từ PR #89 STYLE.md áp dụng cho **toàn bộ series**, không còn legacy backlog.

## Nguyên tắc migration

Backfill style không phải technical rewrite. Ưu tiên giữ nguyên claim/lệnh đã được review, chỉ thay cấu trúc trình bày, command context, verification và rollback khi cần. Nếu phát hiện claim kỹ thuật cần sửa, tách rõ trong diff/PR để review theo nguồn official/upstream thay vì âm thầm thay đổi trong style migration.
