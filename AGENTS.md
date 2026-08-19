# Linux Daily — Agent Operating Contract

Tài liệu này là **nguồn quy tắc vận hành chính** cho mọi AI agent làm việc với repository `ndlong78/linux-daily`, gồm ChatGPT Scheduled Task và các phiên ChatGPT tương tác. `STYLE.md` là source of truth bắt buộc về biên tập và safety affordance.

## 1. Nguyên tắc vận hành

- `main` là nguồn sự thật của nội dung đã chấp nhận.
- Trước khi tạo/sửa bài, đọc `AGENTS.md` và `STYLE.md` trên `main` hiện tại.
- Không push trực tiếp vào `main`.
- Bài mới đi qua branch → PR → CI read-only → guarded post-CI squash merge.
- CI trên PR **không được sửa, commit hoặc push ngược branch**.
- `.github/workflows/linux-daily-auto-merge.yml` là ngoại lệ ghi hẹp: chỉ được gọi merge API sau khi CI của **exact head SHA** đã success; không checkout PR code, không self-mutation, không bypass protection.
- `state.json` là nguồn sự thật của cadence; `topics.md` là lịch sử nội dung, không dùng làm clock vận hành.
- Từ #019, claim/lệnh kỹ thuật chính phải có nguồn official/upstream kiểm chứng được.
- Từ #041, bài mới phải qua `tools/validate_style.py`; #001–#040 là legacy baseline và backfill theo PR riêng.
- Social output Facebook/X đang tạm dừng.
- Scheduled Task không được coi việc thiếu local writable checkout là blocker nếu GitHub connector vẫn có quyền ghi feature branch/PR an toàn. Khi đó dùng API-only fallback và để CI read-only làm remote validation authoritative.

## 2. Cadence hằng ngày

Linux Daily phát hành mặc định **1 bài/ngày**.

```bash
python3 tools/cadence.py gate
python3 tools/cadence.py next
```

- `cadence.py gate` exit `10`: chưa tới nhịp → dừng, không sửa state.
- exit `0`: tiếp tục issue kế tiếp.

Branch bài hằng ngày:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Prefix legacy để phát hiện duplicate:

```text
claude/linux-daily-<NNN>-<YYYYMMDD>
```

Trước khi tạo bài, kiểm tra branch/PR của đúng issue/date. Nếu đã tồn tại PR hợp lệ, **resume PR đó**, không tạo bản thứ hai.

Nếu branch chuẩn đã tồn tại nhưng chưa có PR và branch head vẫn bằng `main`, coi đó là **interrupted empty branch** do lần chạy trước bị gián đoạn. Resume chính branch đó và tiếp tục ghi bài; không tạo branch cùng issue khác.

## 3. Chu kỳ chủ đề

| `(issue - 1) mod 7` | Trục |
|---:|---|
| 0 | Networking |
| 1 | Bảo mật & phân quyền |
| 2 | Storage & hệ thống tệp |
| 3 | Công cụ/phần mềm mới |
| 4 | Monitoring & hiệu năng |
| 5 | Automation & scripting |
| 6 | Ôn tập — lab end-to-end |

Luôn kiểm tra `curriculum-plan.json` và `topics.md`; tránh trùng và ưu tiên progression/prerequisite hợp lý.

## 4. Phạm vi hệ điều hành

Mỗi bài phải nêu rõ khác biệt giữa:

- Ubuntu / Xubuntu: APT, systemd, netplan, UFW/nftables.
- Debian: APT, systemd, Debian stable hiện hành.
- Fedora: DNF, systemd, SELinux, NetworkManager/`nmcli`, firewalld.
- FreeBSD: pkg/ports, rc.d, `rc.conf`, pf/ipfw và công cụ BSD tương ứng.

**FreeBSD luôn tách riêng.** Không gán `systemctl`, `apt`, `dnf`, `nmcli`, `netplan` cho FreeBSD.

## 5. Source-backed technical review — bắt buộc từ #019

Ưu tiên nguồn:

1. upstream project/vendor documentation;
2. Ubuntu/Debian/Fedora/FreeBSD documentation/manpages chính thức;
3. tài liệu chính thức của package/tool.

Mỗi bài #019+ có ít nhất 2 nguồn primary:

```json
{
  "review_status": "reviewed",
  "sources": [
    {"title": "Tên tài liệu", "url": "https://...", "kind": "official"},
    {"title": "Tên upstream", "url": "https://...", "kind": "upstream"}
  ]
}
```

Quy tắc:

- URL HTTPS đầy đủ và không trùng.
- `kind` chỉ `official` hoặc `upstream` trong gate hiện tại.
- title/URL/thứ tự metadata phải khớp phần **Nguồn kỹ thuật**.
- `review_status="draft"` không được qua merge gate.
- Không dùng blog SEO/forum/AI-generated page làm bằng chứng chính.

Review sâu hơn với networking/firewall, storage/filesystem, backup/restore, auth/permissions và shell automation.

## 6. STYLE.md và cấu trúc bài

Dùng `templates/post.template.html`, `STYLE.md`, `assets/style.css`.

Từ #041, bài phải có:

1. metadata hiển thị `Tested on` + `Last verified`;
2. Mục tiêu;
3. Yêu cầu tiên quyết;
4. `01 Bối cảnh thực tế`;
5. `02 Kiến thức cốt lõi`;
6. `03 Các bước thực hiện` với `<ol class="steps">`;
7. `04 Kiểm chứng` với Expected Output/Kết quả mong đợi;
8. `Gỡ / Hoàn tác` nếu `changes_system=true`;
9. `05 Lưu ý & Khắc phục lỗi`;
10. `06 Bảo mật & vận hành`;
11. `07 Bài tập tự luyện`;
12. `Nguồn kỹ thuật` không đánh số.

Mỗi bài phải có:

- đúng 2 SVG nguyên bản, có `role="img"`, `aria-label`, `figcaption`;
- khối FreeBSD riêng;
- 2 link về trang chủ;
- metadata JSON `<script id="ld-meta">`;
- #019+: `review_status`, `sources`, `<section class="sources">`;
- #041+: `tested_on`, `last_verified`, `changes_system`;
- #041+: mọi `<pre><code>` có `language-*`;
- command shell có `data-run-as="user|sudo|root"`;
- không shell prompt `$`/`#`, không `curl | sh` mù, không placeholder legacy `YOUR_*`.

Code block nền tối phải giữ màu chữ sáng/high-contrast từ `assets/style.css`; không dùng inline CSS ghi đè `pre > code`.

## 7. Social output

Không tạo mới Facebook/X hoặc ảnh code social theo mặc định. File lịch sử trong `posts/social/` giữ nguyên.

## 8. Capability preflight, state, build và validation

Trước khi tạo branch mới, Scheduled Task phải xác định khả năng thực thi:

1. Có local writable checkout → dùng local one-pass flow.
2. Không có local writable checkout nhưng GitHub connector có write access → dùng API-only fallback.
3. Chỉ khi cả local write và GitHub remote write đều không khả dụng mới dừng vì capability blocker.

### Local one-pass flow

Sau khi nội dung hoàn chỉnh:

```bash
python3 tools/publish.py prepare
python3 tools/cadence.py record
python3 tools/pr_preflight.py
```

Trong local flow, `tools/pr_preflight.py` phải chạy sau khi deterministic artifacts đã materialize và trước commit/push.

### API-only fallback

API-only fallback là đường vận hành hợp lệ của Scheduled Task khi không có local writable checkout. Nó **không bypass validation**:

- chỉ ghi feature branch, tuyệt đối không ghi `main`;
- chuẩn bị article source + source-of-truth metadata trước khi tạo branch mới nếu có thể;
- ưu tiên Git Data API `create_blob` → `create_tree` → `create_commit` → `update_ref` để ghi một tree nhất quán; nếu không khả dụng có thể dùng Contents API tuần tự trên feature branch;
- không force-update ref;
- mở/resume PR để `CI` read-only chạy validators/generator checks từ xa;
- CI read-only **phát hiện** artifact stale nhưng không tự sửa; để materialize thì dispatch workflow `Materialize Artifacts` — xem bên dưới;
- nếu CI báo regression do source (STYLE, source-backed, cadence, state), sửa đúng source trên cùng branch rồi để CI chạy lại;
- không vô hiệu hóa/nới test, validator, workflow safety hoặc STYLE gate để ép xanh.

#### Materialize artifact khi không có Python runtime

Quality gate so khớp artifact **byte-exact** (`tools/build.py` so `current != expected`), nên nội dung artifact không thể suy đoán mà phải do generator sinh ra. Một bài mới luôn kéo theo cả cụm artifact render lại — `index.html`, `archive.html`, `feed.xml`, `sitemap.xml`, `search-index.json`, `learning-paths.html`, `learning-dashboard.html`, các report trong `docs/`, và related-navigation của những bài lân cận.

Agent API-only ghi được source core và metadata JSON nhưng **không chạy được `tools/publish.py prepare`**. Đường gỡ là dispatch workflow `Materialize Artifacts` bằng chính GitHub API mà agent đang dùng:

```text
POST /repos/{owner}/{repo}/actions/workflows/materialize-artifacts.yml/dispatches
{"ref": "main",
 "inputs": {"branch": "chatgpt/linux-daily-<NNN>-<YYYYMMDD>",
            "confirm": "materialize-artifacts"}}
```

Workflow checkout đúng branch đó, chạy `publish.py prepare`, verify `publish.py check`, rồi commit artifact và push. Head SHA đổi nên `CI` chạy lại, và `Linux Daily Auto Merge` vẫn kiểm exact-SHA như cũ — chuỗi bảo đảm không đổi.

Ràng buộc của đường này, do `tools/materialize_guard.py` và `tools/workflow_safety.py` cưỡng chế:

- `ref` của dispatch luôn là `main` (lấy định nghĩa workflow từ default branch); branch cần dựng nằm ở input `branch`;
- input `branch` phải khớp `^chatgpt/linux-daily-[0-9]{3}-[0-9]{8}$`; `main`/`master` bị từ chối;
- workflow abort nếu generator chạm vào source of truth (`topics.md`, `state.json`, `site.json`, `AGENTS.md`, …) hoặc `tools/`, `tests/`, `.github/`, `templates/`, `assets/`, `labs/`;
- workflow chỉ chạy qua `workflow_dispatch`, không bao giờ tự chạy theo `pull_request`/`push`.

Vì vậy khi không có local writable checkout, thứ tự bắt buộc là **ghi source → dispatch → chờ xong → mới mở PR**:

1. ghi source core lên feature branch;
2. kích hoạt `Materialize Artifacts` và **chờ run kết thúc**;
3. run xanh → mở PR rồi chuyển **Ready ngay** khi diff/state/duplicate/review sạch, không chờ CI;
4. run đỏ → **không mở PR**; đọc log của run và báo capability blocker kèm nguyên nhân.

Ở bước 3, Ready phải xảy ra **trước khi CI hoàn tất**. `linux-daily-auto-merge.yml` chạy theo
`workflow_run` của `CI` và kiểm `draft=false` tại đúng thời điểm đó; nếu PR còn Draft lúc CI
xanh thì auto-merge bỏ qua, và không có run CI mới nào tự phát sinh sau khi chuyển Ready.
Khi ordering bị lỡ, rerun CI trên cùng exact head SHA — không tạo commit rỗng.

Sau khi materialize xanh thì artifact đã đúng, nên không còn lý do giữ Draft. Draft chỉ dành
cho trường hợp chưa dispatch hoặc dispatch đỏ.

Thứ tự này quan trọng chứ không phải tiểu tiết. Nếu mở PR trước rồi mới dispatch, một lượt
chạy kết thúc sớm — hoặc một dispatch bị từ chối vì thiếu quyền `actions: write` — sẽ để lại
một Draft PR nằm im, CI đỏ, không ai được báo. Dispatch trước thì mọi thất bại đều lộ ra
trước khi có PR, và trạng thái "có PR" luôn đồng nghĩa "artifact đã dựng".

Ràng buộc kèm theo:

- không đoán nội dung artifact rồi commit để dò cho CI xanh.

#### Kích hoạt bằng rerun, không phải dispatch

GitHub connector của Scheduled Task **không expose verb `workflow_dispatch`**, nhưng **có**
`rerun_workflow_job` (đã kiểm chứng: rerun trả success, và run thực thi lại đủ 12 bước).
Đây là giới hạn của connector, không phải thiếu quyền `actions: write`.

Vì rerun phát lại đúng inputs của run gốc, input `branch` của workflow là **tuỳ chọn**. Để
trống thì workflow tự suy branch đích từ `state.json.last_issue` trên default branch rồi khớp
đúng một `chatgpt/linux-daily-<NNN+1>-<YYYYMMDD>`. Nhờ vậy một lần rerun luôn dựng đúng branch
của ngày hôm đó.

Cách agent kích hoạt:

1. lấy run gần nhất của `Materialize Artifacts` và job `materialize` trong đó;
2. gọi `rerun_workflow_job` cho job đó;
3. chờ run kết thúc rồi đọc conclusion.

Nếu connector về sau expose `workflow_dispatch`, dùng trực tiếp cũng được:

```text
POST /repos/{owner}/{repo}/actions/workflows/materialize-artifacts.yml/dispatches
{"ref": "main", "inputs": {"confirm": "materialize-artifacts"}}
```

`ref` là nơi đọc định nghĩa workflow (luôn `main`); bỏ trống `branch` để dùng discovery.

**Lưu ý vận hành:** rerun dùng định nghĩa workflow của run gốc. Sau mỗi lần sửa
`materialize-artifacts.yml`, phải dispatch tay **một lần** để tạo run gốc mới; từ đó agent
rerun hằng ngày.

Đường local vẫn nguyên: chạy `python3 tools/publish.py prepare` rồi commit như bình thường, không cần dispatch.

`state.json` phải khớp bài mới nhất trong `topics.md`; `last_generated_at` phản ánh thời điểm sinh thực tế.

## 9. Git workflow — local và API-only

### Local path

1. kiểm cadence + duplicate + capability trước khi tạo branch;
2. chuẩn bị source of truth và chạy generator deterministic;
3. materialize toàn bộ generated artifacts;
4. chạy `python3 tools/pr_preflight.py`;
5. tạo/resume feature branch từ `main` hiện tại;
6. review diff; commit subject mô tả rõ; push và mở/cập nhật PR;
7. kiểm duplicate/state/diff/review thread; khi sạch, chuyển PR bài hằng ngày sang Ready **ngay, không chờ CI success**;
8. `CI` chỉ đọc/validate exact head SHA;
9. nếu CI đỏ, sửa source/generator bằng commit bình thường rồi lặp preflight → push;
10. nếu CI xanh, `Linux Daily Auto Merge` kiểm lại exact SHA + PR contract và squash-merge.

### API-only path

1. kiểm cadence + duplicate + capability trước khi tạo branch;
2. chuẩn bị article/source-of-truth metadata trong agent trước;
3. tạo/resume branch chuẩn; branch rỗng tồn tại từ lần chạy trước phải được resume thay vì duplicate;
4. ghi source core (`posts/`, `topics.md`, `state.json`, metadata JSON) bằng GitHub API; không đoán nội dung artifact render;
5. kích hoạt `Materialize Artifacts` bằng `rerun_workflow_job` và chờ run kết thúc; run đỏ thì dừng và báo blocker, không mở PR;
6. run xanh thì mở PR; kiểm state/diff/duplicate/review rồi chuyển Ready **ngay, không chờ CI success** (auto-merge kiểm `draft=false` lúc CI hoàn tất);
7. dùng CI read-only làm remote preflight cho phần source; CI không thay được bước materialize artifact;
8. nếu CI đỏ vì source, self-fix trên cùng branch rồi dispatch lại; không commit đoán artifact;
9. khi exact-head CI xanh, post-CI workflow tự kiểm contract và squash-merge.

Nếu branch protection/review requirement chưa thỏa, merge API fail và PR giữ nguyên.

Không tạo/track:

- finalizer workflow **tự động** sửa/commit/push branch theo `pull_request`/`push`/`schedule`
  (`Materialize Artifacts` không thuộc nhóm này: chỉ chạy khi được dispatch tường minh kèm chuỗi xác nhận);
- helper gắn trực tiếp số PR kiểu `tools/pr93_*.py`/`.sh`;
- file `*.tmp`, `*.bak`, `*.orig`, `*.rej`;
- diagnostic artifact/no-op commit chỉ để kích hoạt workflow.

Không stage cả thư mục bằng `git add .`, `git add -A`, `git add --all`.

Commit bài hằng ngày:

```text
Linux Daily #<NNN>: <tên chủ đề>
```

Maintenance/feature dùng subject mô tả rõ. `tools/pr_hygiene.py` chặn subject rác như `x`, `tmp`, `test`, `wip`, `placeholder`, `fix`, `update`, `changes`.

Repo dùng **Squash and merge** cho workflow thường ngày.

## 10. CI read-only và post-CI auto-merge

`.github/workflows/ci.yml`:

- trigger PR và push `main`;
- `contents: read`;
- chạy PR hygiene, lint, pytest, workflow safety, STYLE.md, deterministic publish pipeline, link check, cadence/render smoke tests;
- không commit/push repository.

`.github/workflows/linux-daily-auto-merge.yml`:

- trigger **chỉ** bằng `workflow_run` của `CI` khi completed;
- job chỉ chạy nếu CI conclusion `success` và source event là `pull_request`;
- không checkout PR code;
- chỉ merge PR open, non-Draft, base `main`, head cùng repo;
- PR author phải là repository owner;
- branch phải đúng `chatgpt/linux-daily-<NNN>-<YYYYMMDD>`;
- current PR head SHA phải bằng `workflow_run.head_sha`;
- `CHANGES_REQUESTED` hoặc unresolved review thread chặn merge;
- dùng REST merge endpoint với `merge_method=squash` + exact `sha` precondition;
- không `gh pr merge`, không native auto-merge, không `--admin`, không sửa branch protection;
- chỉ cần `contents: write` + `pull-requests: read`;
- không stage/commit/push branch.

**Ordering bắt buộc:** PR bài hằng ngày phải chuyển non-Draft/Ready ngay khi structural/diff/review gate sạch, không đợi CI xanh. Nếu exact-head CI đã success khi PR còn Draft rồi mới chuyển Ready, phải rerun CI/quality-gate trên **cùng exact head SHA** để tạo một `workflow_run success` mới; không tạo no-op commit chỉ để kích hoạt auto-merge.

`tools/workflow_safety.py` phải enforce toàn bộ boundary trên.

## 11. Exact-head completion contract

Một PR không được coi là đã merge chỉ vì local PASS hoặc run xanh của SHA cũ.

- CI success phải thuộc exact head SHA được merge.
- Auto-merge workflow phải so `workflow_run.head_sha` với current PR head SHA ngay trước merge.
- Nếu có push mới sau CI, SHA mismatch làm merge dừng; CI mới phải chạy lại.
- `queued`, `pending`, `in_progress`, `failure`, `cancelled`, `timed_out` không được coi là success.
- Không skip/suppress/nới gate để ép xanh.

Scheduled Task **không cần polling tới lúc merge** sau khi PR đã Ready: post-CI workflow chịu trách nhiệm exact-head merge. Nếu CI fail, PR giữ mở để task/phiên sau resume và sửa.

## 12. Scheduled Task của ChatGPT

Task chạy 07:00 mỗi ngày, cadence 1 bài/ngày.

Mỗi lần chạy:

1. đọc `AGENTS.md`, `STYLE.md`, state/curriculum hiện hành;
2. kiểm cadence, duplicate branch/PR và capability **trước khi tạo branch mới**;
3. nếu có local writable checkout, dùng local one-pass flow; nếu không có nhưng GitHub connector ghi được, dùng API-only fallback;
4. nếu branch đúng issue đã tồn tại nhưng head == `main` và chưa có PR, resume như interrupted empty branch;
5. chuẩn bị bài + source-backed review + STYLE review;
6. local path: materialize artifacts + preflight; API-only path: ghi source/artifacts vào feature branch và dùng CI làm remote preflight;
7. commit/push/open PR theo quyền đã được người dùng ủy quyền;
8. chuyển PR sang Ready khi structural/diff/review gate sạch, **không chờ CI success**;
9. không cần chờ CI kết thúc để tự merge thủ công; GitHub post-CI workflow xử lý merge;
10. nếu CI đã success lúc PR còn Draft, rerun CI trên cùng SHA sau khi Ready;
11. nếu CI/merge thất bại, báo đúng blocker và resume ở lần sau.

Thiếu local checkout **không phải blocker** nếu GitHub connector vẫn có khả năng ghi feature branch/PR. Task không tạo social output mặc định và không thay đổi branch protection/repository settings để ép merge.
