# Learning Paths — operating model

P8.1 thêm một lớp điều hướng học tập theo **mục tiêu kỹ năng**, không thay taxonomy, thứ tự xuất bản hay metadata kỹ thuật của từng bài.

## Source of truth

`learning-paths.json` là cấu hình duy nhất của learning paths. Mỗi path khai:

- `slug`: định danh kebab-case, duy nhất;
- `title`: tên lộ trình;
- `goal`: năng lực người học hướng tới;
- `audience`: nhóm người học phù hợp;
- `steps`: danh sách **issue number** theo thứ tự học.

Title, ngày, eyebrow và URL của từng step được resolve từ `ld-meta` trong bài tương ứng. Không copy các trường này vào `learning-paths.json`, nhờ đó đổi title/file mà metadata không đồng bộ sẽ bị generator hoặc repository gate bắt thay vì âm thầm drift.

## Coverage contract

`tools/learning_paths.py` áp các rule deterministic:

1. config version hiện tại phải là `1`;
2. slug phải hợp lệ và không trùng;
3. mỗi path có title/goal/audience và tối thiểu 3 step;
4. issue không được lặp trong cùng một path;
5. mọi issue được tham chiếu phải tồn tại;
6. **mọi bài published phải thuộc ít nhất một learning path**;
7. một bài được phép thuộc nhiều path nếu phục vụ nhiều mục tiêu học tập.

Rule số 6 có chủ đích: khi thêm #020 trở đi, contributor phải quyết định bài đó đứng ở đâu trong trải nghiệm học, thay vì để kho nội dung tăng nhưng navigation học tập bị bỏ quên.

## Baseline P8.1

Hiện có 4 path, phủ 19/19 bài:

| Path | Mục tiêu | Step |
|---|---|---:|
| Nền tảng quản trị server | Vận hành, truy cập và chẩn đoán một server an toàn | 7 |
| Networking & Security | Kết nối, troubleshooting, access control, firewall/VPN | 7 |
| Storage & Backup | Disk/filesystem → snapshot → backup/restore → cloud copy | 8 |
| Automation & Operations | Scripting, scheduling, config management và observability | 7 |

Overlap là intentional. Ví dụ #001 là nền tảng server đồng thời là bước đầu của Networking & Security; #014 vừa là lab backup vừa là integration exercise cho automation/operations.

## Public page

`learning-paths.html` được generate từ config + post metadata và có canonical:

```text
https://linux.no.id.vn/learning-paths.html
```

Trang nằm trong sitemap, dùng font/style self-hosted của site và chịu website/SEO + accessibility gates. P8.4 sẽ là nơi hợp nhất learning navigation/dashboard rộng hơn; P8.1 chỉ chịu trách nhiệm data model, path ordering và public path page.

## Lệnh vận hành

Regenerate page sau khi sửa `learning-paths.json` hoặc post metadata:

```bash
python3 tools/learning_paths.py
```

Kiểm tra deterministic drift:

```bash
python3 tools/learning_paths.py --check
```

Xem inventory có cấu trúc:

```bash
python3 tools/learning_paths.py --json
```

`python3 tools/build.py` đã gọi generator/check này, vì vậy `tools/publish.py prepare/check` tự động bao phủ Learning Paths.

## Boundary với P8.2/P8.3

P8.1 **không** suy đoán difficulty hoặc prerequisite từ vị trí trong path. Thứ tự path là curriculum ordering có chủ đích, nhưng difficulty/prerequisite metadata sẽ được chuẩn hóa riêng ở P8.2; P8.3 mới dùng các tín hiệu đó để đánh giá topic progression và knowledge gaps.
