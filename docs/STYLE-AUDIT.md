# STYLE.md — Historical Content Audit Baseline

Baseline date: **2026-08-09**  
Scope: **Linux Daily #001–#040**  
Enforcement boundary: **#041+**

## Kết luận

Toàn bộ 40 bài hiện có được tạo trước khi `STYLE.md` trở thành enforceable contract. Code search trên `main` tại thời điểm baseline không tìm thấy `Tested on` hoặc `last_verified`; vì vậy **#001–#040 chưa đạt đầy đủ STYLE.md mới** và được phân loại `legacy`.

Legacy không có nghĩa là nội dung kỹ thuật không hợp lệ. Nhiều bài đã có source-backed review, FreeBSD separation, rollback hoặc verification. Trạng thái `legacy` chỉ nói rằng bài chưa đáp ứng đầy đủ contract mới về metadata, step structure, command context và visual/code semantics.

## Những khoảng trống áp dụng cho baseline

Các bài lịch sử cần được rà lần lượt theo các tiêu chí sau:

- thêm metadata hiển thị `Tested on` + `Last verified`;
- thêm `ld-meta.tested_on`, `last_verified`, `changes_system`;
- bổ sung Mục tiêu và Yêu cầu tiên quyết rõ ràng;
- chuyển quy trình tuyến tính thành `<ol class="steps">`;
- thêm `language-*` cho mọi code block;
- khai báo `data-run-as="user|sudo|root"` cho shell command block;
- bảo đảm verification có Expected Output/Kết quả mong đợi;
- thêm **Gỡ / Hoàn tác** cho bài thay đổi hệ thống;
- loại shell prompt `$`/`#` khỏi command block;
- chuẩn hóa placeholder sang `<...>`;
- loại `curl | sh` trực tiếp và tăng cảnh báo cho thao tác phá hủy;
- giữ FreeBSD tách riêng, không áp cơ chế Linux.

## Enforcement policy

`tools/validate_style.py` chạy hai chế độ:

```bash
python3 tools/validate_style.py
python3 tools/validate_style.py --audit
```

- mặc định: audit toàn bộ posts nhưng chỉ fail CI nếu bài **#041+** vi phạm;
- `--audit`: in chi tiết lỗi style của tất cả bài, kể cả legacy;
- legacy exemption không áp dụng cho nội dung mới sao chép từ bài cũ.

## Kế hoạch backfill

Backfill chia thành 4 PR/batch để diff nhỏ và review kỹ thuật được:

| Batch | Bài | Mục tiêu |
|---|---:|---|
| A | #001–#010 | Metadata + command semantics + rollback |
| B | #011–#020 | Metadata + step/verification + automation safety |
| C | #021–#030 | Incident/lab structure + Expected Output + placeholders |
| D | #031–#040 | Chuẩn hóa các bài gần nhất và đóng legacy baseline |

Sau mỗi batch, chạy:

```bash
python3 tools/validate_style.py --audit
python3 tools/publish.py check
```

Khi #001–#040 đều đạt contract mới, bỏ legacy boundary hoặc đặt enforcement từ #001 bằng một PR governance riêng.

## Không làm trong PR enforcement

PR đưa `STYLE.md` vào pipeline **không rewrite đồng thời 40 bài**. Lý do:

- tránh diff nội dung quá lớn;
- tách thay đổi governance/tooling khỏi technical content review;
- không làm mất dấu claim đã source-backed;
- dễ rollback nếu validator cần tinh chỉnh.
