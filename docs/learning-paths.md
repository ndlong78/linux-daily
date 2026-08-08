# Learning Paths — operating model

P8.1 thêm một lớp điều hướng học tập theo **mục tiêu kỹ năng**, không thay taxonomy, thứ tự xuất bản hay metadata kỹ thuật của từng bài. P8.2 bổ sung difficulty + prerequisite graph làm learning signal độc lập.

## Source of truth

`learning-paths.json` là cấu hình duy nhất của learning-path ordering. Mỗi path khai:

- `slug`: định danh kebab-case, duy nhất;
- `title`: tên lộ trình;
- `goal`: năng lực người học hướng tới;
- `audience`: nhóm người học phù hợp;
- `steps`: danh sách **issue number** theo thứ tự học.

Title, ngày, eyebrow và URL của từng step được resolve từ `ld-meta` trong bài tương ứng. Difficulty + prerequisites được resolve từ `learning-metadata.json`; learning path không copy các trường đó.

## Coverage contract

`tools/learning_paths.py` áp các rule deterministic:

1. config version hiện tại phải là `1`;
2. slug phải hợp lệ và không trùng;
3. mỗi path có title/goal/audience và tối thiểu 3 step;
4. issue không được lặp trong cùng một path;
5. mọi issue được tham chiếu phải tồn tại;
6. **mọi bài published phải thuộc ít nhất một learning path**;
7. một bài được phép thuộc nhiều path nếu phục vụ nhiều mục tiêu học tập;
8. P8.2 learning metadata phải hợp lệ trước khi path được render.

Rule số 6 có chủ đích: khi thêm bài mới, contributor phải quyết định bài đó đứng ở đâu trong trải nghiệm học, thay vì để kho nội dung tăng nhưng navigation học tập bị bỏ quên.

## Baseline

Hiện có 4 path, phủ 19/19 bài:

| Path | Mục tiêu | Step |
|---|---|---:|
| Nền tảng quản trị server | Vận hành, truy cập và chẩn đoán một server an toàn | 7 |
| Networking & Security | Kết nối, troubleshooting, access control, firewall/VPN | 7 |
| Storage & Backup | Disk/filesystem → snapshot → backup/restore → cloud copy | 8 |
| Automation & Operations | Scripting, scheduling, config management và observability | 7 |

P8.2 bổ sung trên cùng public page:

- difficulty badge cho từng step;
- “Học trước” với link trực tiếp tới prerequisite;
- dependency graph do `tools/learning_metadata.py` validate, không do template suy đoán.

Overlap giữa path là intentional. Ví dụ #001 vừa là nền tảng server vừa là bước đầu của Networking & Security; #014 vừa là lab backup vừa là integration exercise cho automation/operations.

## Public page

`learning-paths.html` được generate từ path config + post metadata + P8.2 learning metadata và có canonical:

```text
https://linux.no.id.vn/learning-paths.html
```

Trang nằm trong sitemap, dùng font/style self-hosted của site và chịu website/SEO + accessibility gates. P8.4 sẽ là nơi hợp nhất learning navigation/dashboard rộng hơn.

## Lệnh vận hành

Regenerate page sau khi sửa path/post/learning metadata:

```bash
python3 tools/learning_paths.py
```

Kiểm deterministic drift:

```bash
python3 tools/learning_paths.py --check
```

Xem inventory có cấu trúc:

```bash
python3 tools/learning_paths.py --json
```

`python3 tools/build.py` gọi generator/check này, vì vậy `tools/publish.py prepare/check` tự động bao phủ public Learning Paths page. P8.2 metadata còn có gate riêng:

```bash
python3 tools/learning_metadata.py
```

## Boundary với P8.3

Path ordering là curriculum ordering có chủ đích; prerequisite là dependency DAG; difficulty là node attribute. P8.1/P8.2 **không** tự kết luận một path có bước nhảy kiến thức. P8.3 mới kết hợp ba tín hiệu đó để phát hiện topic progression gap.
