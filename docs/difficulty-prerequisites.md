# Difficulty & Prerequisites — operating model

P8.2 chuẩn hóa hai tín hiệu học tập độc lập với ngày xuất bản và taxonomy:

- **difficulty**: mức độ kiến thức/kỹ năng mà bài yêu cầu;
- **prerequisites**: các bài cần học trước để có nền tảng trực tiếp cho bài hiện tại.

## Source of truth

`learning-metadata.json` là source of truth duy nhất cho learning metadata. Mỗi entry gồm:

```json
{"issue": 16, "difficulty": "intermediate", "prerequisites": [2, 5]}
```

Title, URL và nội dung bài vẫn lấy từ `ld-meta`; learning metadata không copy các trường bibliographic đó.

## Difficulty contract

Chỉ có ba giá trị hợp lệ:

| Giá trị | Hiển thị | Ý nghĩa |
|---|---|---|
| `basic` | Cơ bản | Có thể bắt đầu trực tiếp với kiến thức sysadmin nền tảng |
| `intermediate` | Trung cấp | Cần ghép nhiều khái niệm hoặc thao tác có operational risk đáng kể |
| `advanced` | Nâng cao | Kiến thức chuyên sâu, nhiều layer hoặc yêu cầu chẩn đoán/thiết kế phức tạp |

Không bắt buộc repository phải có đủ cả ba mức. Baseline hiện tại không có bài `advanced`; validator không tạo mức khó giả chỉ để cân distribution.

## Prerequisite contract

Prerequisite là **dependency thật**, không phải danh sách “bài liên quan”. Rule:

1. prerequisite phải là issue đã published;
2. không được trỏ chính nó;
3. không được lặp trong cùng entry;
4. toàn bộ graph phải **acyclic**;
5. mọi bài published phải có một learning-metadata entry, kể cả khi `prerequisites` rỗng;
6. prerequisite không bị ràng buộc bởi thứ tự publication.

Rule 6 là quan trọng: #003 ZFS snapshots có thể phụ thuộc #010 “thêm đĩa mới” dù #010 được xuất bản sau. Curriculum order và publication order là hai khái niệm khác nhau.

## Baseline P8.2

- Published posts: **19**
- Cơ bản: **8**
- Trung cấp: **11**
- Nâng cao: **0**
- Prerequisite edges: **16**
- Cycle: **0**

Một số dependency điển hình:

- #008 → #001: troubleshooting mạng cần hiểu cấu hình IP/interface/route cơ bản;
- #006 → #002 + #009: Ansible qua SSH và privilege escalation;
- #016 → #002 + #005: fail2ban dựa trên SSH hardening + hiểu log;
- #017 → #010: mở rộng storage cần hiểu disk/partition/filesystem trước;
- #014 → #009 + #010 + #012 + #013: lab backup tích hợp user quyền tối thiểu, storage, scheduling và scripting.

## Validator

Chạy:

```bash
python3 tools/learning_metadata.py
python3 tools/learning_metadata.py --json
```

Gate hard-fail khi:

- thiếu metadata cho một bài published;
- có entry trỏ issue không tồn tại;
- difficulty ngoài ba giá trị chuẩn;
- prerequisite không tồn tại, tự tham chiếu hoặc bị lặp;
- prerequisite graph có cycle.

`tools/publish.py check` chạy gate này trực tiếp. `tools/learning_paths.py` cũng import cùng result để render difficulty + “Học trước” trên public Learning Paths page; không reimplement validation rule.

## Boundary với P8.3

P8.2 chỉ định nghĩa **node attributes + dependency DAG**. Nó chưa kết luận một learning path có bước nhảy quá lớn hay prerequisite nằm sai vị trí. P8.3 Topic Progression sẽ kết hợp:

- path ordering từ `learning-paths.json`;
- difficulty/prerequisite graph từ `learning-metadata.json`;
- taxonomy/axis hiện có;

để phát hiện progression gap mà không sửa source metadata tự động.
