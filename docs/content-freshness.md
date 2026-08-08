# Content Freshness & Technical Drift

P7.3 tách **technical review** khỏi **freshness review**. `review_status=reviewed/published` chứng minh bài đã được review tại một thời điểm; nó không có nghĩa nội dung sẽ đúng mãi mãi.

## Source of truth

`freshness.json` định nghĩa:

- review window theo mức volatility (`high`, `medium`, `low`);
- volatility mặc định theo axis;
- issue bắt đầu áp contract mới;
- override có chủ đích cho `last_reviewed` hoặc `historically-valid`.

Không backfill trường freshness vào 19 file HTML lịch sử chỉ để thêm metadata. Publication date là mốc review ban đầu nếu chưa có override.

## Ba trạng thái

### `current`

Ngày chạy chưa vượt `review_due_on`. Đây là trạng thái mặc định, không cần ghi cứng vào từng bài.

### `review-due`

Được tính tự động khi:

```text
as_of > last_reviewed + review_window
```

`review-due` là **queue cần hành động**, không phải build failure mặc định. Nếu CI hard-fail theo thời gian, một `main` không đổi cũng có thể tự đỏ chỉ vì sang ngày mới. Vì vậy publish gate vẫn pass nhưng in rõ review queue.

Audit/manual strict mode có thể dùng:

```bash
python3 tools/content_freshness.py --fail-review-due
```

### `historically-valid`

Chỉ được khai báo thủ công trong `freshness.json` khi nội dung không còn là guidance hiện hành nhưng vẫn có giá trị lịch sử.

Ví dụ:

```json
{
  "overrides": {
    "12": {
      "state": "historically-valid",
      "last_reviewed": "2026-11-01",
      "reason": "Giữ lại để mô tả workflow cũ; cách hiện hành đã chuyển sang bài mới.",
      "replacement_issue": 40
    }
  }
}
```

`reason` là bắt buộc. `replacement_issue` là tùy chọn nhưng nếu có phải trỏ tới issue đang tồn tại. Không được khai báo `review-due` thủ công vì trạng thái này phải được tính theo thời gian.

## Review windows

Policy hiện tại:

- **high — 90 ngày:** Bảo mật, Công cụ mới;
- **medium — 180 ngày:** Networking, Storage, Monitoring, Automation, Ôn tập;
- **low — 365 ngày:** dành cho nội dung rất ổn định khi roadmap sau này cần.

Đây là cadence **review**, không phải tuyên bố rằng nội dung tự hết hạn sau đúng số ngày.

## Ghi nhận một lần re-review

Khi reviewer kiểm lại nguồn official/upstream và xác nhận guidance vẫn đúng, chỉ cập nhật ledger:

```json
{
  "overrides": {
    "19": {
      "last_reviewed": "2026-10-20"
    }
  }
}
```

Không sửa ngày xuất bản và không rewrite bài chỉ để làm nó trông mới hơn.

## CLI

```bash
python3 tools/content_freshness.py
python3 tools/content_freshness.py --as-of 2026-08-08
python3 tools/content_freshness.py --json
python3 tools/content_freshness.py --fail-review-due
```

`--as-of` giúp audit/test reproducible. `--json` cung cấp structured output để P7.4 Quality Dashboard tái sử dụng mà không parse text console.

## Hard failures

Validator fail khi policy/ledger không đáng tin, ví dụ:

- axis chưa có policy;
- review window không hợp lệ;
- override trỏ issue không tồn tại;
- `last_reviewed` trước ngày xuất bản;
- `historically-valid` thiếu lý do;
- `replacement_issue` không tồn tại;
- bài mới từ #020 chưa có `review_status=reviewed/published`.

## Boundary

Freshness gate không tự xác minh rằng package/service/API vẫn hoạt động và không thay thế source-backed technical review. Khi một bài tới hạn, reviewer phải kiểm lại claim có khả năng drift bằng nguồn official/upstream, rồi chọn một trong ba hướng:

1. vẫn đúng → cập nhật `last_reviewed`;
2. cần sửa → sửa bài + nguồn, rồi cập nhật `last_reviewed`;
3. không còn là guidance hiện hành nhưng đáng giữ → đánh dấu `historically-valid` kèm lý do/replacement nếu có.
