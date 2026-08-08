# Learning Dashboard — operating model

P8.4 tạo một public dashboard **derived** từ ba lớp Learning Experience đã có; dashboard không trở thành source of truth mới và không lưu tiến độ cá nhân.

## Nguồn dữ liệu

`tools/learning_dashboard.py` đọc trực tiếp kết quả từ:

1. `tools/learning_paths.py` — path membership/order và 19/19 curriculum coverage;
2. `tools/learning_metadata.py` — difficulty + prerequisite DAG;
3. `tools/topic_progression.py` — ordering/difficulty progression health và curriculum gaps.

Không có `learning-dashboard.json`. Nếu path, difficulty hoặc prerequisite thay đổi thì renderer mới là nơi tính lại dashboard.

## Public page

Dashboard public:

```text
https://linux.no.id.vn/learning-dashboard.html
```

Trang hiển thị:

- tổng số bài và learning paths;
- difficulty mix;
- prerequisite-edge inventory;
- progression status + hard-finding count;
- local/cross-path prerequisite references;
- missing difficulty tiers;
- summary từng path và link thẳng tới anchor tương ứng trên `learning-paths.html`.

Dashboard không dùng account/cookie/local storage để ghi completed step. Đây là curriculum/learning-navigation dashboard, không phải LMS progress tracker.

## Status semantics

Dashboard kế thừa status từ P8.3:

- `FAIL`: upstream P8 lỗi, prerequisite ordering violation hoặc difficulty jump hard finding;
- `ATTENTION`: không có hard finding nhưng còn curriculum gap như thiếu difficulty tier;
- `PASS`: không có hard finding và không còn gap P8.3 đang theo dõi.

Baseline P8.4:

| Signal | Giá trị |
|---|---:|
| Published posts | 19 |
| Learning paths | 4 |
| Covered posts | 19/19 |
| Difficulty | 8 basic / 11 intermediate / 0 advanced |
| Prerequisite DAG edges | 16 |
| Path-level prerequisite refs | 23 |
| Local / cross-path refs | 17 / 6 |
| Hard findings | 0 |
| Missing tier | advanced |
| Dashboard status | ATTENTION |

`ATTENTION` là evidence thật, không phải lý do relabel bài cũ thành Nâng cao.

## Deterministic contract

Regenerate dashboard:

```bash
python3 tools/learning_dashboard.py
```

Kiểm artifact drift:

```bash
python3 tools/learning_dashboard.py --check
```

Structured data:

```bash
python3 tools/learning_dashboard.py --json
```

`tools/publish.py prepare` regenerate page; `tools/publish.py check` chạy `--check`. Test còn so sánh committed `learning-dashboard.html` byte-for-byte với renderer.

## Public-quality contract

Dashboard là first-class public page:

- canonical trên custom domain;
- nằm trong `sitemap.xml`;
- tính vào repository generated-page inventory;
- dùng self-hosted fonts;
- chịu accessibility gate;
- internal-link checker kiểm các anchor tới Learning Paths;
- website/SEO gate kiểm canonical/page inventory và navigation tới homepage, Learning Paths, Search & Archive.

## Boundary sau P8

P8.4 đóng Learning Experience bằng một derived view có thể dùng trực tiếp cho người học và làm evidence cho maintainer. Các phase sau có thể thêm nội dung/lab mới; dashboard sẽ tự phản ánh chúng khi `learning-paths.json` và `learning-metadata.json` được cập nhật đúng contract.
