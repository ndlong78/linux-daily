# Historical Publication Timeline — July 2026

PR #79 chuẩn hóa corpus lịch sử ban đầu của Linux Daily thành một timeline liên tục, nhưng **không renumber issue và không đổi URL**.

## Canonical mapping

- `#001` → `2026-07-01`
- `#002` → `2026-07-02`
- …
- `#021` → `2026-07-21`

Công thức cho corpus lịch sử này là:

```text
date(issue) = 2026-07-01 + (issue - 1) ngày, với 1 <= issue <= 21
```

Sau khi migration hoàn tất, `state.json` phải là:

```json
{
  "last_issue": 21,
  "last_published_date": "2026-07-21",
  "last_generated_at": "2026-07-21T00:00:00+00:00"
}
```

`00:00 UTC` tương ứng `07:00 Asia/Ho_Chi_Minh` trong tháng 7/2026.

## Boundary

Migration chỉ đổi publication clock:

- `ld-meta.date` của `posts/post-001..021`;
- ngày hiển thị trong masthead của cùng các bài;
- `state.json`;
- các generated artifact được dựng lại từ post metadata bằng `tools/publish.py prepare`.

Migration **không** đổi:

- issue number;
- slug/URL;
- title/lede/nội dung kỹ thuật;
- learning prerequisite IDs;
- learning-path ordering;
- source review;
- lifecycle/freshness semantics.

## Migration command

Xem trước mapping:

```bash
python tools/normalize_publication_timeline.py
```

Áp dụng source migration:

```bash
python tools/normalize_publication_timeline.py --apply
python tools/publish.py prepare
python tools/normalize_publication_timeline.py --check
python tools/publish.py check
```

`--apply` cố ý không tự gọi generator. Source mutation và deterministic artifact generation được giữ thành hai bước rõ ràng để reviewer có thể phân biệt thay đổi timeline với output sinh lại.

## Sau PR #79

Backfill bắt đầu ở `#022 = 2026-07-22`. Corpus có thể tăng tuần tự đến `#040 = 2026-08-09`; cadence hằng ngày bình thường tiếp tục từ `#041 = 2026-08-10`.
