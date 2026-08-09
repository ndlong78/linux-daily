# STYLE.md — Historical Content Audit Baseline

Baseline date: **2026-08-09**  
Scope: **Linux Daily #001–#040**  
Current enforcement: **#001–#030 và #041+**

## Trạng thái

PR Batch A đã backfill **#001–#010** và Batch B backfill **#011–#020** theo contract `STYLE.md`. Các bài #001–#020 không còn được grandfather: `tools/validate_style.py` sẽ fail CI nếu regress.

Các bài **#031–#040** vẫn là legacy migration backlog. Legacy không có nghĩa nội dung kỹ thuật không hợp lệ; trạng thái này chỉ nói bài chưa đáp ứng đầy đủ contract mới về metadata, step structure, command context và code semantics.

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

- mặc định: fail CI nếu **#001–#030** hoặc **#041+** vi phạm;
- `--audit`: in chi tiết trạng thái của toàn bộ lịch sử;
- **#031–#040** tiếp tục được audit nhưng chưa fail cho tới khi batch tương ứng hoàn tất;
- legacy exemption không áp dụng cho nội dung mới sao chép từ bài cũ.

## Kế hoạch backfill

| Batch | Bài | Trạng thái | Mục tiêu |
|---|---:|---|---|
| A | #001–#010 | **Hoàn tất trong PR #85** | Metadata + command semantics + rollback |
| B | #011–#020 | **Hoàn tất trong PR #87** | Metadata + step/verification + automation safety |
| C | #021–#030 | **Hoàn tất trong PR #88** | Incident/lab structure + Expected Output + placeholders |
| D | #031–#040 | Chờ | Chuẩn hóa các bài gần nhất và đóng legacy baseline |

Sau mỗi batch, chạy:

```bash
python3 tools/validate_style.py --audit
python3 tools/publish.py check
```

Batch B đã nâng `BACKFILLED_THROUGH` lên 20; Batch C sẽ nâng lên 30; Batch D lên 40. Khi #001–#040 đều đạt contract mới, có thể đơn giản hóa validator thành enforcement toàn bộ series.

## Nguyên tắc migration

Backfill style không phải technical rewrite. Ưu tiên giữ nguyên claim/lệnh đã được review, chỉ thay cấu trúc trình bày, command context, verification và rollback khi cần. Nếu phát hiện claim kỹ thuật cần sửa, tách rõ trong diff/PR để review theo nguồn official/upstream thay vì âm thầm thay đổi trong style migration.
