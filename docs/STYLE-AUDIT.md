# STYLE.md — Historical Content Audit Baseline

Baseline date: **2026-08-09**  
Scope: **Linux Daily #001–#040**  
Current enforcement: **toàn bộ series #001+**

## Trạng thái

Batch A–D đã backfill hoàn tất **#001–#040** theo contract `STYLE.md`. Không còn grandfather/legacy exemption: `tools/validate_style.py` sẽ fail CI nếu bất kỳ bài lịch sử hoặc bài mới nào regress.

Một migration metadata riêng được áp dụng từ Linux Daily **#070** để sửa semantics verification mà không viết lại technical content. #001–#069 được đọc tương thích với schema cũ cho tới lần materialize #070; sau đó `tools/backfill_site_metadata.py` chuyển deterministic toàn series sang schema explicit.

## Contract được backfill

Contract cấu trúc lịch sử vẫn yêu cầu:

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

Từ #070, verification metadata được hiểu chính xác:

- `ld-meta.tested_on` = OS/version đã **runtime-test thật**;
- `ld-meta.documentation_verified_on` = OS/version đã review bằng tài liệu official/upstream;
- hai list có thể rỗng riêng lẻ nhưng ít nhất một phải có bằng chứng;
- không dùng sentinel `(documentation-verified)` trong `tested_on`;
- UI hiển thị riêng `Runtime tested`, `Documentation verified`, `Last verified`;
- `last_verified` và `changes_system` vẫn giữ nguyên contract.

Migration #001–#069 chỉ đổi representation/label của bằng chứng đã có: sentinel documentation cũ được chuyển sang `documentation_verified_on`. Nó **không** tự tạo runtime evidence.

## Enforcement policy

`tools/validate_style.py` chạy hai chế độ:

```bash
python3 tools/validate_style.py
python3 tools/validate_style.py --audit
```

- mặc định: fail CI nếu **bất kỳ bài #001+** vi phạm contract áp dụng cho schema hiện tại;
- `--audit`: in chi tiết trạng thái của toàn bộ series;
- legacy exemption cấu trúc đã được đóng hoàn toàn sau Batch D;
- schema verification cũ của #001–#069 chỉ là compatibility window tới materialize #070, không phải exemption khỏi validation.

## Kế hoạch backfill

| Batch | Bài | Trạng thái | Mục tiêu |
|---|---:|---|---|
| A | #001–#010 | **Hoàn tất trong PR #85** | Metadata + command semantics + rollback |
| B | #011–#020 | **Hoàn tất trong PR #87** | Metadata + step/verification + automation safety |
| C | #021–#030 | **Hoàn tất trong PR #88** | Incident/lab structure + Expected Output + placeholders |
| D | #031–#040 | **Hoàn tất trong PR #89** | Chuẩn hóa các bài gần nhất và đóng legacy baseline |
| Verification split | #001–#069 | **Kích hoạt deterministic khi materialize #070** | Tách runtime evidence khỏi documentation review |

Sau mỗi batch/migration, chạy:

```bash
python3 tools/validate_style.py --audit
python3 tools/publish.py check
```

Batch D nâng `BACKFILLED_THROUGH` lên 40. Vì #041+ vốn đã enforced, từ PR #89 STYLE.md áp dụng cho **toàn bộ series**, không còn legacy backlog.

## Nguyên tắc migration

Backfill style không phải technical rewrite. Ưu tiên giữ nguyên claim/lệnh đã được review, chỉ thay cấu trúc trình bày, command context, verification và rollback khi cần. Verification split cũng chỉ phân loại đúng loại bằng chứng đã tồn tại; không được biến documentation review thành runtime test. Nếu phát hiện claim kỹ thuật cần sửa, tách rõ trong diff/PR để review theo nguồn official/upstream thay vì âm thầm thay đổi trong style migration.