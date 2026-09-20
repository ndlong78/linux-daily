# Linux Daily — Agent Operating Contract

Tài liệu này là **nguồn quy tắc vận hành chính** cho mọi AI agent làm việc với repository `ndlong78/linux-daily`, gồm ChatGPT Scheduled Task và các phiên ChatGPT tương tác. `STYLE.md` là source of truth bắt buộc về biên tập và safety affordance.

## 1. Nguyên tắc vận hành

- `main` là nguồn sự thật của nội dung đã chấp nhận.
- Trước khi tạo/sửa bài, đọc `AGENTS.md` và `STYLE.md` trên `main` hiện tại.
- Không push trực tiếp vào `main`.
- Bài mới đi qua branch → PR → CI read-only → guarded post-CI squash merge.
- CI trên PR **không được sửa, commit hoặc push ngược branch**.
- `.github/workflows/linux-daily-auto-merge.yml` là ngoại lệ ghi hẹp: gọi merge API sau khi CI của **exact head SHA** đã success, rồi dispatch CI và Production Smoke để kiểm chứng commit sau merge; không checkout PR code, không self-mutation, không bypass protection.
- `state.json` là nguồn sự thật của cadence; `topics.md` là lịch sử nội dung, không dùng làm clock vận hành.
- Từ #019, claim/lệnh kỹ thuật chính phải có nguồn official/upstream kiểm chứng được.
- **Mọi URL nguồn mới phải được HTTP-check trước khi mở PR.** "Kiểm chứng được" nghĩa là
  đã thật sự gọi thử và nhận 2xx — không phải trông có vẻ đúng. URL không tồn tại là lỗi
  nặng hơn thiếu nguồn: nó tạo ra vẻ ngoài của bằng chứng ở nơi không có bằng chứng nào.
  Ưu tiên URL đã có sẵn trong repo cho cùng công cụ, vì chúng đã qua link check.
- Toàn bộ #001+ phải qua `tools/validate_style.py`; backfill #001–#040 đã hoàn tất và không còn legacy exemption.
- Social output Facebook/X đang tạm dừng.
- Scheduled Task không được coi việc thiếu local writable checkout là blocker nếu GitHub connector vẫn có quyền ghi feature branch/PR an toàn. Khi đó dùng API-only fallback và để CI read-only làm remote validation authoritative.

## 2. Cadence hằng ngày

Linux Daily phát hành mặc định **1 bài/ngày**.

```bash
python3 tools/cadence.py gate
python3 tools/cadence.py next
python3 tools/cadence.py backlog
```

- `cadence.py gate` exit `10`: chưa tới nhịp → dừng, không sửa state.
- exit `0`: tiếp tục issue kế tiếp.

### Bù bài khi đã lỡ nhịp

Một lượt chạy hỏng làm `last_published_date` tụt lại sau lịch. Nếu mỗi lượt chỉ ra đúng
một bài thì khoảng tụt đó **không bao giờ co lại**: ra một bài đẩy ngày lên một ngày,
trong khi hôm nay cũng trôi đi một ngày. Vì vậy khi đang tụt, một lượt chạy được phép ra
nhiều bài.

`cadence.py backlog` là nguồn quyết định, không phải phán đoán của agent:

```bash
python3 tools/cadence.py backlog
# tụt sau lịch     : 3 ngày
# trần mỗi lượt    : 3
# được ra lượt này : 3
#   #080 | 2026-09-18
#   #081 | 2026-09-19
#   #082 | 2026-09-20
```

- exit `0` = còn bài được phép ra; exit `10` = đã đúng nhịp, dừng.
- Ra **đúng** số bài và **đúng** cặp (số hiệu, ngày) mà lệnh in ra. Không tự chọn ngày,
  không ra thêm bài thứ N+1 vì "còn thời gian".
- Trần mặc định `CATCHUP_MAX_PER_RUN = 3`. Gián đoạn dài hơn được bù dần qua nhiều lượt,
  không đổ một lần — vượt trần là vượt khả năng review của cả người lẫn agent.
- Ngày bài cuối cùng nhiều nhất là hôm nay (giờ VN). `validate_repo` chặn ngày ở tương lai,
  và allowance luôn ≤ backlog nên ràng buộc đó không bao giờ bị chạm.

**Mỗi bài vẫn là một branch và một PR riêng, chạy tuần tự.** Không gộp nhiều bài vào một
branch. Lý do là ràng buộc có thật chứ không phải thẩm mỹ:

- `materialize-artifacts.yml` suy branch đích từ `state.json.last_issue + 1` trên `main`,
  nên bài #N+1 chỉ tìm được branch của nó sau khi #N đã merge vào `main`;
- mỗi bài có cổng CI riêng, nên #081 đỏ không chặn #080 đã xong;
- tên branch `chatgpt/linux-daily-<NNN>-<YYYYMMDD>` mang đúng một số hiệu.

Trình tự khi bù: `backlog` → viết #080 → materialize → PR → chờ merge → `backlog` lại →
#081 → … Đọc lại `backlog` sau mỗi lần merge thay vì dùng danh sách cũ; ngày có thể đã
sang ngày mới trong lúc chạy.

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

Từ Linux Daily **#070**, metadata verification phải tách loại bằng chứng rõ ràng:

1. `Runtime tested` — chỉ OS/version đã thực sự chạy kiểm thử;
2. `Documentation verified` — chỉ OS/version đã đối chiếu tài liệu official/upstream;
3. `Last verified` — ngày review gần nhất;
4. Mục tiêu;
5. Yêu cầu tiên quyết;
6. `01 Bối cảnh thực tế`;
7. `02 Kiến thức cốt lõi`;
8. `03 Các bước thực hiện` với `<ol class="steps">`;
9. `04 Kiểm chứng` với Expected Output/Kết quả mong đợi;
10. `Gỡ / Hoàn tác` nếu `changes_system=true`;
11. `05 Lưu ý & Khắc phục lỗi`;
12. `06 Bảo mật & vận hành`;
13. `07 Bài tập tự luyện`;
14. `Nguồn kỹ thuật` không đánh số.

#001–#069 được validator đọc tương thích với schema cũ cho tới lần materialize #070. Khi `state.json.last_issue >= 70`, `tools/backfill_site_metadata.py` migrate deterministic toàn bộ sentinel lịch sử `(documentation-verified)` sang `documentation_verified_on` và đổi nhãn hiển thị. Không sửa tay từng bài lịch sử.

Mỗi bài phải có:

- đúng 2 SVG nguyên bản, có `role="img"`, `aria-label`, `figcaption`;
- khối FreeBSD riêng;
- 2 link về trang chủ;
- metadata JSON `<script id="ld-meta">`;
- #019+: `review_status`, `sources`, `<section class="sources">`;
- #070+: `tested_on`, `documentation_verified_on`, `last_verified`, `changes_system`; hai list verification có thể rỗng riêng lẻ nhưng ít nhất một phải có bằng chứng;
- #070+: `tested_on` không được chứa `(documentation-verified)` hoặc bất kỳ documentation-only evidence nào;
- #001+: mọi `<pre><code>` có `language-*`;
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

Trong local flow, `tools/pr_preflight.py` phải chạy sau khi deterministic artifacts đã materialize và trước commit/push. Ở mốc #070, `publish.py prepare` còn thực hiện một lần migration verification metadata cho #001–#069; diff nhiều file `posts/post-*.html` ở đúng ngày đó là artifact deterministic theo contract, không phải lý do bỏ qua hoặc sửa tay generator.

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

#### Link check có cache — điều đó đổi gì với agent

`check_links.py --cache` bỏ qua URL đã nhận 2xx trong 7 ngày gần nhất. CI chỉ ĐỌC
cache **trên PR**; `push: main` chạy với `--cache-ttl-days 0`, tức vẫn hỏi lại đủ
100% URL như trước, chỉ ghi lại kết quả để gieo cache cho các PR sau (cache của
Actions bị khoá theo ref — PR chỉ đọc được cache từ nhánh mặc định).

Điều agent cần biết:

- **URL nguồn MỚI luôn bị hỏi thật, không lấy từ cache.** Cache không phải đường
  lách contract "mọi URL nguồn mới phải nhận 2xx trước khi mở PR" — nó chỉ bỏ
  qua URL đã có sẵn và còn hạn.
- Dòng `↺ Cache: N URL bỏ qua` trong log là bình thường, không phải cảnh báo.
- Chạy tay ở máy thì **không** truyền `--cache`; hỏi lại toàn bộ mới là thứ bạn
  muốn khi đang kiểm một bài mới.
- `.link-cache.json` do `actions/cache` quản lý, **không commit vào git**. Thấy nó
  trong `git status` là sai — nó đã nằm trong `.gitignore`.

#### Ngân sách kích thước artifact khám phá

`performance_budget.py` (nằm trong `publish.py check`, tức cổng CI) canh trần
**256 KiB** cho `archive.html`, `search-index.json` và `learning-paths.html`.
Ba file này tăng tuyến tính theo số bài — hồi quy trên lịch sử git #34 → #66:

| file | B/bài | nay (#66) | chạm 256 KiB |
|---|---:|---:|---:|
| `archive.html` | 479 | 37,4 KiB | bài #533 |
| `search-index.json` | 575 | 41,0 KiB | bài #449 |
| `learning-paths.html` | 1037 | 59,8 KiB | **bài #259** |

Điều agent cần biết:

- Chạy `python3 tools/performance_budget.py` sẽ in **% ngân sách đã dùng** cho
  mỗi metric. Vì ba file trên tăng tuyến tính, % chính là dư địa còn lại quy ra
  số bài — đọc nó trước khi lo, đừng đợi CI đỏ.
- Khi một file chạm trần, cách xử lý là **phân trang hoặc tách file** như đã làm
  với `index.html` ở PR #144 — **không nới trần**. Nới trần là bỏ cổng chứ không
  phải sửa vấn đề.
- `learning-paths.html` là file sẽ chạm trước, và còn cách khá xa (~193 bài).
  Chưa cần làm gì, nhưng đừng thêm nội dung theo bài vào nó mà không đo lại.

#### Trang chủ đã phân trang — `trang-N.html`

Danh sách bài **không còn nằm hết trong `index.html`**. `index.html` là trang 1 với
20 bài mới nhất; phần còn lại ở `trang-2.html`, `trang-3.html`… do
`tools/build_index.py` sinh ra.

Vì sao: `index.html` cũ liệt kê mọi bài và tăng **0.570 KiB/bài** (đo trên 5 mốc git
từ #044 tới #065). Ngân sách `homepage_html` là 256 KiB và `performance_budget.py`
nằm trong `publish.py check`, nên quanh **bài #435** nó sẽ chặn cứng việc ra bài.

Điều agent cần biết:

- **Không sửa tay `index.html` hay `trang-N.html`.** Chúng là artifact dẫn xuất,
  gác byte-exact. Sinh lại bằng `python3 tools/publish.py prepare`, hoặc dispatch
  `Materialize Artifacts` nếu không có Python runtime.
- **Số trang đổi theo số bài.** Cứ 20 bài là thêm một trang, nên có ngày commit
  bài sẽ kèm một file `trang-N.html` HOÀN TOÀN MỚI. Đó là bình thường, không phải
  file lạc.
- Trang 1 vẫn là `index.html` và canonical vẫn là gốc site — URL trang chủ không đổi.
- Nếu số bài giảm, `build.py` tự **xoá** `trang-N.html` thừa; commit cả phần xoá đó.

Ba gate canh phần này, không được nới:

| Gate | Bắt gì |
|---|---|
| `validate_site.py` | mọi bài phải được **một** trang danh sách liên kết; chuỗi trang không được đứt mắt |
| `build.py --check` | trang phân trang stale hoặc thừa |
| `performance_budget.py` | **từng** trang danh sách phải dưới 256 KiB |

#### Materialize artifact khi không có Python runtime

Quality gate so khớp artifact **byte-exact** (`tools/build.py` so `current != expected`), nên nội dung artifact không thể suy đoán mà phải do generator sinh ra. Một bài mới luôn kéo theo cả cụm artifact render lại — `index.html` **và các trang phân trang `trang-N.html`**, `archive.html`, `feed.xml`, `sitemap.xml`, `search-index.json`, `learning-paths.html`, `learning-dashboard.html`, các report trong `docs/`, và related-navigation của những bài lân cận.

Agent API-only ghi được source core và metadata JSON nhưng **không chạy được `tools/publish.py prepare`**.

**Từ nay agent không phải tự kích hoạt gì cả.** `materialize-dispatch.yml` chạy theo `push`
vào branch khớp `chatgpt/linux-daily-*` và gọi `Materialize Artifacts` thay cho bạn. Push
source core lên branch là đủ; việc còn lại là **chờ** run kết thúc rồi mới mở PR.

Vì sao là workflow riêng chứ không phải thêm `on: push` thẳng vào `materialize-artifacts.yml`:
với `workflow_dispatch` + `ref: main`, định nghĩa workflow luôn được lấy từ default branch.
Thêm `push` vào chính nó thì định nghĩa lấy từ branch vừa push — tức branch tự quyết luật chạy
của chính nó, và mọi guard bên trong (`materialize_guard.py`, regex branch, cổng xác nhận) đều
nằm trong tay thứ đang cần được kiểm. Tách đôi giữ nguyên tính chất đó:

| | `materialize-dispatch.yml` | `materialize-artifacts.yml` |
|---|---|---|
| Trigger | `push` nhánh bài | chỉ `workflow_dispatch`, `ref: main` |
| Định nghĩa đọc từ | branch vừa push | **luôn là `main`** |
| Quyền | `contents: read` + `actions: write` | `contents: write` |
| Checkout code branch | **không bao giờ** | có, tại SHA đã pin |
| Chạy code của branch | **không** | có, sau khi `materialize_guard` từ main duyệt |

Dispatcher không checkout, không chạy một dòng nào của branch, không có quyền ghi nội dung —
`tools/workflow_safety.py::_validate_materialize_dispatch` cưỡng chế từng điểm, và
`tests/test_workflow_safety_materialize_dispatch.py` bắt mọi lần nới.

Không có vòng lặp: materialize đẩy artifact bằng `GITHUB_TOKEN`, mà sự kiện sinh bởi
`GITHUB_TOKEN` không tạo workflow run mới (đã đo trên 4/4 commit auto-merge). Dispatcher còn
có guard `github.actor != 'github-actions[bot]'` làm lớp thứ hai, để tính chất an toàn này
không treo vào một hành vi ngầm của nền tảng.

Đường dispatch tay vẫn còn nguyên cho maintenance và khi cần dựng lại một branch cũ:

```text
POST /repos/{owner}/{repo}/actions/workflows/materialize-artifacts.yml/dispatches
{"ref": "main",
 "inputs": {"branch": "chatgpt/linux-daily-<NNN>-<YYYYMMDD>",
            "confirm": "materialize-artifacts"}}
```

Workflow pin SHA của branch đích và main hiện tại. Trước khi cài dependency, bản
`materialize_guard.py` lấy từ SHA main kiểm toàn bộ tree của branch: chỉ dữ liệu
bài và artifact được khác main; tooling, dependency/config, template và workflow
phải khớp. Branch cũ có tooling khác main phải cập nhật từ main rồi chạy lại.
Checkout không lưu credential; token chỉ cấp cho bước đọc API và bước commit/push.
Sau `publish.py prepare` và `publish.py check`, guard từ main kiểm đầu ra lần nữa;
HEAD local và remote phải còn khớp SHA đã pin trước khi ghi. Push không force.
Head SHA đổi thành artifact head; agent chỉ mở PR sau khi run materialize xanh. Khi PR
được mở bằng owner connector, `CI` chạy trên exact head và `Linux Daily Auto Merge`
vẫn kiểm exact-SHA.

Ràng buộc của đường này, do `tools/materialize_guard.py` và `tools/workflow_safety.py` cưỡng chế:

- `ref` của dispatch luôn là `main` (lấy định nghĩa workflow từ default branch); branch cần dựng nằm ở input `branch`;
- input `branch` phải khớp `^chatgpt/linux-daily-[0-9]{3}-[0-9]{8}$`; `main`/`master` bị từ chối;
- workflow abort nếu generator chạm vào source of truth (`topics.md`, `state.json`, `site.json`, `AGENTS.md`, …) hoặc `tools/`, `tests/`, `.github/`, `templates/`, `assets/`, `labs/`;
- workflow chỉ chạy qua `workflow_dispatch`, không bao giờ tự chạy theo `pull_request`/`push`.

Vì vậy khi không có local writable checkout, thứ tự là **ghi source → materialize → mở PR**:

1. ghi source core lên feature branch (push này tự kích hoạt materialize);
2. **chờ run kết thúc** — theo dõi `Materialize Dispatch` rồi tới `Materialize Artifacts`;
   branch head đổi sang commit `Dựng lại artifact site cho <branch>` là dấu hiệu artifact đã được push;
3. run xanh → agent kiểm exact branch head, duplicate PR và diff rồi **mở PR non-Draft bằng
   GitHub connector của repository owner**; không dùng `GITHUB_TOKEN` của workflow để mở PR;
4. PR owner-authored kích `pull_request:opened`; CI read-only kiểm exact head rồi post-CI
   auto-merge xử lý như bình thường;
5. run đỏ → đọc log, sửa source-of-truth trên cùng branch và để materialize chạy lại; chưa mở PR.

Lý do owner connector là contract bắt buộc đã được đo trực tiếp ngày 2026-09-20 trên #081:
`Materialize Artifacts` run `35521048520` mở PR #174 bằng `GITHUB_TOKEN`; GitHub tạo CI
run `35521115720` nhưng kết thúc ngay với `action_required`, không có quality-gate chạy.
Cùng exact head `a94edced…` được repository owner mở lại thành PR #175 thì CI run
`35521176728` chạy đầy đủ và xanh. Vì vậy "có CI run ID" không đủ để chứng minh
`pull_request:opened` usable khi PR do `GITHUB_TOKEN` tạo.

Materialize **không có `pull-requests: write`** và không gọi API tạo PR. Ranh giới này được
`workflow_safety.py` và test gác để tránh regression. Agent phải kiểm branch/PR trùng trước
khi mở; nếu PR owner-authored đã tồn tại cho branch thì resume PR đó thay vì tạo bản thứ hai.

Ready phải xảy ra **trước khi CI hoàn tất**. Agent mở daily PR non-Draft ngay sau materialize
xanh; `linux-daily-auto-merge.yml` chạy theo `workflow_run` của `CI` và kiểm exact head.
Không tạo no-op commit để kích workflow.

Thứ tự này quan trọng: mở PR **trước** khi materialize xong có thể để CI đọc artifact stale;
để workflow tự mở PR bằng `GITHUB_TOKEN` lại có thể rơi vào `action_required`. Chờ
materialize xanh rồi để owner connector mở PR giữ cả hai invariant: artifact đã đúng và CI
thật sự runnable.

Ràng buộc kèm theo:

- không đoán nội dung artifact rồi commit để dò cho CI xanh.

#### Đường dự phòng: kích hoạt bằng rerun

Mục này chỉ còn dùng khi cần dựng lại một branch mà **không** có push mới — ví dụ branch cũ
bị bỏ dở, hoặc `Materialize Dispatch` đỏ và bạn muốn thử lại mà không tạo commit. Đường
thường ngày là push rồi chờ; không cần làm gì trong mục này.

GitHub connector của Scheduled Task **không expose verb `workflow_dispatch`**, nhưng **có**
`rerun_workflow_job` (đã kiểm chứng: rerun trả success, và run thực thi lại đủ 12 bước).
Đây là giới hạn của connector, không phải thiếu quyền `actions: write` — và cũng chính là
lý do `materialize-dispatch.yml` tồn tại: nó gọi dispatch bằng `GITHUB_TOKEN` từ bên trong
Actions, nơi verb đó luôn có.

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

Khi rollout thay đổi ranh giới tin cậy của materialize:

1. CI của maintenance PR phải xanh trên đúng head SHA, không có review đang chặn.
2. Chuẩn bị khả năng dispatch mới trước khi merge workflow; rerun cũ không kiểm chứng YAML mới.
3. Sau merge, dispatch từ main với `confirm=materialize-artifacts`, bỏ trống `branch`,
   trên branch bài kế tiếp có source hợp lệ; đọc log để xác nhận source guard chạy trước pip.
4. Kiểm artifact, CI trên head mới và chu kỳ bài tiếp theo. Chưa có run thành công thì
   không tuyên bố đường API-only đã được kiểm chứng; giữ khả năng chạy local preflight.

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
5. push đó tự kích hoạt `Materialize Dispatch` → `Materialize Artifacts`; **chờ run kết thúc**;
   run đỏ thì dừng và báo blocker;
6. run xanh thì kiểm exact branch head/diff/duplicate rồi mở PR non-Draft bằng owner connector;
7. dùng CI read-only làm remote preflight cho exact artifact head; CI không thay bước materialize;
8. nếu CI đỏ vì source, sửa source trên cùng branch, chờ materialize xanh lại rồi để PR synchronize;
9. khi exact-head CI xanh, post-CI workflow tự kiểm contract và squash-merge.

Nếu branch protection/review requirement chưa thỏa, merge API fail và PR giữ nguyên.

Không tạo/track:

- finalizer workflow **tự động** sửa/commit/push branch theo `pull_request`/`push`/`schedule`.
  `Materialize Artifacts` không thuộc nhóm này: nó vẫn chỉ chạy qua `workflow_dispatch` kèm
  chuỗi xác nhận, với định nghĩa đọc từ `main`. `Materialize Dispatch` chạy theo `push` nhưng
  cũng không thuộc nhóm này: nó không có `contents: write`, không checkout, không sửa gì —
  nó chỉ bấm nút. Ranh giới cần giữ là **workflow nào ghi vào branch**, chứ không phải
  workflow nào tự chạy; gộp hai thứ đó lại thì hoặc cấm nhầm, hoặc bỏ lọt;
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
- với daily PR, current base SHA phải là ancestor của head; branch stale phải cập nhật từ `main` và materialize lại;
- không commit/push repository.

`.github/workflows/linux-daily-auto-merge.yml`:

- trigger **chỉ** bằng `workflow_run` của `CI` khi completed;
- chỉ xét CI conclusion `success` từ source event `pull_request`;
- maintenance/non-daily, PR đã đóng hoặc daily PR còn Draft là **ineligible** và kết thúc sạch, không tạo failure giả;
- không checkout PR code;
- chỉ merge PR open, non-Draft, base `main`, head cùng repo;
- PR author phải là repository owner; PR do `github-actions[bot]`/`GITHUB_TOKEN` mở không thuộc contract vì `pull_request:opened` có thể bị GitHub giữ ở `action_required`;
- branch phải đúng `chatgpt/linux-daily-<NNN>-<YYYYMMDD>`;
- current PR head SHA phải bằng `workflow_run.head_sha`;
- `CHANGES_REQUESTED` hoặc unresolved review thread chặn merge;
- dùng REST merge endpoint với `merge_method=squash` + exact `sha` precondition;
- không `gh pr merge`, không native auto-merge, không `--admin`, không sửa branch protection;
- quyền `contents: write` + `pull-requests: read` cho merge; `actions: write` chỉ để dispatch CI và Production Smoke sau merge;
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
2. kiểm cadence, duplicate branch/PR và capability **trước khi tạo branch mới**; chạy
   `cadence.py backlog` để biết lượt này được ra bao nhiêu bài và mỗi bài mang ngày nào;
3. nếu có local writable checkout, dùng local one-pass flow; nếu không có nhưng GitHub connector ghi được, dùng API-only fallback;
4. nếu branch đúng issue đã tồn tại nhưng head == `main` và chưa có PR, resume như interrupted empty branch;
5. chuẩn bị bài + source-backed review + STYLE review, gồm phân loại đúng runtime/documentation verification evidence từ #070;
6. local path: materialize artifacts + preflight; API-only path: push source core lên feature
   branch rồi chờ `Materialize Artifacts` (tự kích hoạt) xong, dùng CI làm remote preflight;
7. local path: commit/push/open PR theo quyền đã được ủy quyền. API-only path: sau khi
   `Materialize Artifacts` xanh, agent mở PR non-Draft bằng owner connector trên exact artifact head;
8. PR bài hằng ngày phải non-Draft khi structural/diff/review gate sạch, **không chờ CI success**;
9. không cần chờ CI kết thúc để tự merge thủ công; GitHub post-CI workflow xử lý merge;
10. nếu CI đã success lúc PR còn Draft, rerun CI trên cùng SHA sau khi Ready;
11. nếu CI/merge thất bại, báo đúng blocker và resume ở lần sau;
12. nếu `backlog` còn bài chưa ra và bài vừa rồi đã merge vào `main`, chạy lại `backlog`
    và lặp từ bước 5 cho bài kế tiếp; dừng khi `backlog` trả exit `10` hoặc khi một bài
    trong lượt gặp blocker.

Thiếu local checkout **không phải blocker** nếu GitHub connector vẫn có khả năng ghi feature branch/PR. Task không tạo social output mặc định và không thay đổi branch protection/repository settings để ép merge.