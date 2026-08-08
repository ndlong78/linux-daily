# Topic Progression — operating model

P8.3 kiểm tra **thứ tự học** bằng cách kết hợp hai source of truth đã có:

- `learning-paths.json`: curriculum ordering theo từng learning path;
- `learning-metadata.json`: difficulty + prerequisite DAG của từng bài.

`tools/topic_progression.py` chỉ tổng hợp hai lớp này; nó không định nghĩa lại prerequisite validity/cycle rules của P8.2 và không đoán kiến thức ngầm từ nội dung prose.

## Các signal

### 1. Prerequisite ordering violation — hard fail

Nếu một prerequisite **có mặt trong cùng learning path** nhưng đứng sau bài phụ thuộc, path không còn tự nhất quán.

Ví dụ sai:

```text
step 2: #020 cần #010
step 5: #010
```

Finding `prerequisite-after-dependent` làm `tools/topic_progression.py` trả exit code khác 0 và chặn publish CI.

### 2. External prerequisite — informational

Một bài có thể cần prerequisite hợp lệ nhưng prerequisite đó không nằm trong path hiện tại. Trường hợp này **không phải ordering violation** vì public Learning Paths đã hiển thị link `Học trước` để người học rẽ sang bài cần thiết.

P8.3 vẫn inventory các reference này để P8.4 có thể hiển thị dependency cross-path và để maintainer biết path nào phụ thuộc nhiều vào kiến thức ngoài lộ trình.

### 3. Difficulty jump — hard fail

Difficulty có thứ tự:

```text
basic < intermediate < advanced
```

Hai step liên tiếp được phép giữ nguyên, tăng một bậc hoặc giảm bậc khi curriculum cố ý quay lại một công cụ nền tảng. Chỉ bước nhảy tăng **hơn một bậc** bị chặn, hiện tại tương đương `basic -> advanced`.

Rule này là signal có độ chắc chắn cao; P8.3 không cố chấm điểm khoảng cách kiến thức bằng heuristic mơ hồ.

### 4. Missing difficulty tier — ATTENTION

Nếu toàn bộ corpus chưa có một tier hợp lệ nào đó, analyzer surface như curriculum gap nhưng **không làm CI đỏ mặc định**. Baseline hiện tại thiếu `advanced`, nên P8 vẫn có chỗ phát triển mà không buộc phải gắn nhãn Nâng cao giả cho bài hiện có.

Khi cần audit nghiêm ngặt:

```bash
python3 tools/topic_progression.py --fail-gaps
```

## Baseline P8.3

Với 4 path / 19 bài hiện tại:

- prerequisite references theo các path: **23**;
- prerequisite nằm trong cùng path và đã đứng trước đúng chỗ: **17**;
- external prerequisite references: **6**;
- ordering violations: **0**;
- difficulty jumps > 1 tier: **0**;
- missing difficulty tier: **advanced**;
- overall progression status: **ATTENTION**, không có hard finding.

`ATTENTION` ở đây chỉ phản ánh curriculum chưa có bài Nâng cao. Nó không đồng nghĩa path đang sai.

## Lệnh vận hành

Kiểm progression:

```bash
python3 tools/topic_progression.py
```

Structured evidence cho tooling/dashboard:

```bash
python3 tools/topic_progression.py --json
```

Audit muốn fail nếu còn missing difficulty tier:

```bash
python3 tools/topic_progression.py --fail-gaps
```

Normal `tools/publish.py check` **không** bật `--fail-gaps`; nó chỉ fail khi source upstream invalid, prerequisite đứng sai thứ tự trong cùng path hoặc có difficulty jump vượt một bậc.

## Boundary với P8.4

P8.3 tạo progression evidence, không tạo dashboard/UI mới. P8.4 sẽ tổng hợp:

- learning-path coverage từ P8.1;
- difficulty/prerequisite graph từ P8.2;
- progression status, external dependencies và curriculum gaps từ P8.3;

thành một derived Learning Dashboard mà không thay các source of truth ở trên.
