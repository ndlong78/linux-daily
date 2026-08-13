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

## 8. State, build và preflight

Sau khi nội dung hoàn chỉnh:

```bash
python3 tools/publish.py prepare
python3 tools/cadence.py record
python3 tools/pr_preflight.py
```

`tools/pr_preflight.py` phải chạy sau khi deterministic artifacts đã materialize và trước commit/push.

`state.json` phải khớp bài mới nhất trong `topics.md`; `last_generated_at` phản ánh thời điểm sinh thực tế.

## 9. Git workflow — one pass

Thứ tự bắt buộc:

1. tạo/resume feature branch từ `main` hiện tại;
2. sửa source of truth và chạy generator deterministic;
3. materialize toàn bộ generated artifacts trước commit;
4. chạy `python3 tools/pr_preflight.py`;
5. review diff; commit subject mô tả rõ; push và mở/cập nhật PR;
6. kiểm duplicate/state/diff/review thread; khi sạch, chuyển PR bài hằng ngày sang Ready;
7. `CI` chỉ đọc/validate exact head SHA;
8. nếu CI đỏ, sửa source/generator bằng commit bình thường rồi lặp preflight → push;
9. nếu CI xanh, `Linux Daily Auto Merge` kiểm lại exact SHA + PR contract và squash-merge;
10. nếu branch protection/review requirement chưa thỏa, merge API fail và PR giữ nguyên.

Không tạo/track:

- finalizer workflow tự sửa/commit/push branch;
- helper gắn trực tiếp số PR kiểu `tools/pr93_*.py`/`.sh`;
- file `*.tmp`, `*.bak`, `*.orig`, `*.rej`;
- diagnostic artifact chỉ để kích hoạt workflow.

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
2. kiểm cadence và duplicate;
3. tạo hoặc resume đúng branch/PR;
4. chuẩn bị bài + source-backed review + STYLE review;
5. materialize artifacts + preflight;
6. commit/push/open PR theo quyền đã được người dùng ủy quyền;
7. chuyển PR sang Ready khi structural/diff/review gate sạch;
8. không cần chờ CI kết thúc để tự merge thủ công; GitHub post-CI workflow xử lý merge;
9. nếu CI/merge thất bại, báo đúng blocker và resume ở lần sau.

Task không tạo social output mặc định và không thay đổi branch protection/repository settings để ép merge.
