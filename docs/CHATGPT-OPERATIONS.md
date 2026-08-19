# Vận hành Linux Daily bằng ChatGPT Plus

Linux Daily vận hành theo mô hình **ChatGPT Plus + Scheduled Task + GitHub + GitHub Actions**. Không cần OpenAI API cho workflow hiện tại.

## Kiến trúc

```text
ChatGPT Plus Scheduled Task (07:00 Asia/Ho_Chi_Minh)
                 │
                 ▼
       đọc AGENTS.md + STYLE.md
                 │
        state.json / topics.md
                 │
          cadence đủ 1 ngày?
           │             │
          không          có
           │             │
         dừng            ▼
                    capability preflight
                     │            │
             local checkout   GitHub API-only
                     │            │
                     └──────┬─────┘
                            ▼
                      chuẩn bị bài
                            │
             source-backed + style review
                            │
                 duplicate branch/PR?
                     │              │
                    có             không
                     │              │
                 resume            tạo branch
                     └──────┬───────┘
                            ▼
                    materialize/write
                            │
                            ▼
                       PR → Ready
                            │
                            ▼
               GitHub Actions CI read-only
                    │               │
                   fail           success
                    │               │
               self-fix PR          ▼
                             Linux Daily Auto Merge
                                      │
                             exact-SHA safety gates
                                      │
                                 squash merge
                                      │
                                     main
```

## Scheduled Task

Task chuẩn chạy **07:00 mỗi ngày** theo `Asia/Ho_Chi_Minh`.

Mỗi lần chạy, ChatGPT phải:

1. Đọc `AGENTS.md` và `STYLE.md` từ `main` mới nhất.
2. Đọc `state.json`, kiểm cadence mặc định 1 ngày.
3. Nếu chưa sang ngày phát hành kế tiếp: kết thúc, không tạo thay đổi.
4. Nếu tới nhịp: xác định issue kế tiếp, kiểm tra trục, tránh chủ đề trùng và ưu tiên progression hợp lý.
5. Kiểm tra branch/PR đang mở cho issue đó, gồm prefix `chatgpt/` và legacy `claude/`.
6. Chạy **capability preflight trước khi tạo branch mới**: xác định có local writable checkout hay chỉ có GitHub connector write access.
7. Nếu có local writable checkout, dùng local one-pass flow: chuẩn bị source → materialize deterministic artifacts → `tools/pr_preflight.py` → branch/commit/push.
8. Nếu không có local writable checkout nhưng GitHub connector ghi được, dùng **API-only fallback**; không được dừng chỉ vì thiếu checkout.
8b. Trong API-only fallback, artifact dẫn xuất do workflow `Materialize Artifacts` dựng — dispatch nó **trước** khi mở PR, không commit source-only rồi chờ CI chỉ ra thiếu.
9. Nếu branch chuẩn của đúng issue đã tồn tại, chưa có PR và head vẫn bằng `main`, coi đó là interrupted empty branch và resume chính branch đó.
10. Chuẩn bị bài theo `templates/post.template.html`, `AGENTS.md`, `STYLE.md` và validators hiện hành.
11. Từ #019: kiểm tra claim/lệnh bằng ít nhất 2 nguồn official/upstream, ghi `review_status` + `sources`, tạo section **Nguồn kỹ thuật** khớp metadata.
12. Từ #041: ghi `tested_on`, `last_verified`, `changes_system`; khai báo quyền command block; dùng numbered steps; có verification output; thêm rollback khi thay đổi hệ thống.
13. Không tạo finalizer/self-mutating workflow để Actions sửa, commit hoặc push ngược branch.
14. Không sinh Facebook/X hoặc ảnh code social trong giai đoạn social output đang tạm dừng.
15. Khi đã có quyền GitHub write của Scheduled Task, được tạo branch/commit/push/PR theo contract. Không push trực tiếp `main`.
16. Với PR bài hằng ngày hợp lệ, chuyển PR sang **Ready for review ngay khi diff/state/duplicate/review gate sạch**, không chờ CI success.
17. Task không cần polling CI đến lúc merge. GitHub xử lý: `CI` validate exact head SHA; nếu success, `.github/workflows/linux-daily-auto-merge.yml` thực hiện guarded squash merge.
18. Nếu CI đã success khi PR còn Draft rồi mới chuyển Ready, rerun CI/quality-gate trên cùng exact head SHA; không tạo no-op commit chỉ để kích hoạt auto-merge.

## Source of truth

- `AGENTS.md`: hợp đồng vận hành của AI agent.
- `STYLE.md`: chuẩn ngôn ngữ, cấu trúc, code block và safety affordance.
- `curriculum-plan.json`: hàng đợi chủ đề. `tools/curriculum_planner.py` bắt
  `planning_horizon_days == len(topics)`, nên khi lấy một chủ đề ra để viết bài thì phải
  bổ sung một chủ đề mới ở cuối hàng đợi, đúng trục theo chu kỳ 7. Gỡ mà không bù là gate đỏ.
- `state.json`: trạng thái cadence.
- `topics.md`: lịch sử chủ đề và thứ tự series.
- `templates/post.template.html`: khung bài.
- `tools/publish.py`: entrypoint quality gate local.
- `tools/pr_preflight.py`: one-pass local PR preflight.
- `tools/pr_hygiene.py`: guard commit/path của PR.
- `tools/validate_sources.py`: source-backed technical gate.
- `tools/validate_style.py`: STYLE.md audit/enforcement.
- `tools/workflow_safety.py`: policy gate cho GitHub Actions.
- `.github/workflows/ci.yml`: read-only quality gate trên PR và remote preflight authoritative cho API-only fallback.
- `.github/workflows/linux-daily-auto-merge.yml`: post-CI exact-SHA squash merge cho PR bài hằng ngày.

Không dùng prompt Scheduled Task làm nơi duy nhất giữ business rules. Prompt task chỉ là entrypoint; quy tắc bền vững nằm trong repository.

## Capability preflight và hai đường vận hành

Scheduled Task có hai đường hợp lệ.

### 1. Local writable checkout

Đây là đường ưu tiên vì có thể chạy generator và validator trước khi push:

```bash
python3 tools/cadence.py gate
python3 tools/cadence.py next
# tạo HTML + technical sources + STYLE.md metadata
python3 tools/publish.py prepare
python3 tools/cadence.py record
python3 tools/pr_preflight.py
```

Chỉ sau khi preflight sạch mới commit/push source + deterministic artifacts.

### 2. API-only fallback

Dùng khi Scheduled Task không có local writable checkout nhưng GitHub connector vẫn có write access.

API-only fallback **không phải bypass** và không được ghi trực tiếp `main`:

- chuẩn bị article source + source-of-truth metadata trước khi tạo branch mới nếu có thể;
- ưu tiên Git Data API `create_blob` → `create_tree` → `create_commit` → `update_ref` để ghi một tree nhất quán;
- nếu Git Data API không khả dụng, dùng Contents API tuần tự trên feature branch;
- không force-push/update ref;
- mở/resume PR và dùng `CI` read-only làm remote preflight authoritative;
- đọc log CI và self-fix lỗi do branch trên cùng branch;
- không giảm/nới test, STYLE, source review, deterministic build hoặc workflow safety để ép xanh.

Chỉ khi **cả local writable checkout và GitHub remote write đều không khả dụng** mới báo capability blocker.

## STYLE.md review

Linux Daily #041+ phải đạt style contract:

- metadata hiển thị `Tested on` + `Last verified`;
- `ld-meta` có `tested_on`, `last_verified`, `changes_system`;
- Mục tiêu + Yêu cầu tiên quyết;
- các bước thực hiện dùng `<ol class="steps">`;
- mọi code block có `language-*`;
- command block shell có `data-run-as="user|sudo|root"`;
- command block khác nhau theo OS có nhãn `class="code-label <token>"` với token thuộc
  `bsd | ubuntu | debian | fedora | linux | same`; **mỗi bài bắt buộc có ít nhất một khối
  FreeBSD gắn `code-label bsd`** (xem STYLE.md mục 5.1). Thiếu nhãn là lỗi đã từng chặn
  bài #048;
- thân bài phải nhắc rõ cả `Ubuntu` lẫn `Xubuntu`; `tools/distro_coverage.py` bỏ qua vùng
  `Tested on` khi đếm, nên chỉ ghi ở banner là chưa đủ;
- verification có Expected Output/Kết quả mong đợi;
- `changes_system=true` thì có **Gỡ / Hoàn tác**;
- không shell prompt trong command block, không `curl | sh` chạy trực tiếp, không placeholder legacy kiểu `YOUR_*`.

#001–#040 được audit nhưng chưa fail CI. Không được tận dụng legacy exemption cho bài mới.

## Source-backed technical review

Với bài #019+, operator phải kiểm tra các claim chính trước khi đặt `review_status="reviewed"`. Tối thiểu 2 nguồn phải có `kind` là `official` hoặc `upstream`, dùng HTTPS và không trùng URL.

Review sâu hơn với networking/firewall, storage/filesystem, backup/restore, auth/permissions và shell automation.

## Social output

Facebook/X và ảnh code social đang **tạm dừng** để giảm khối lượng generation/review khi cadence tăng lên hằng ngày.

## Quyền ghi GitHub

Nguyên tắc an toàn:

- không push trực tiếp `main`;
- không ghi state khi cadence chưa tới;
- không tạo issue/branch/PR trùng;
- không bypass CI hoặc branch protection;
- không tạo workflow tự sửa/commit/push ngược feature branch;
- không đặt `review_status="reviewed"` khi nguồn chưa được kiểm tra;
- không giảm STYLE.md enforcement để CI xanh;
- API-only fallback chỉ ghi feature branch/PR, không ghi `main`;
- auto-merge chỉ áp dụng cho branch chuẩn `chatgpt/linux-daily-<NNN>-<YYYYMMDD>`;
- auto-merge chỉ chạy sau `CI` success của **exact head SHA**;
- auto-merge không checkout PR code với write token;
- merge method bắt buộc `squash`; không dùng `--admin` hoặc bypass protection;
- `CHANGES_REQUESTED` hoặc unresolved review thread phải chặn merge.

## Branch convention và interrupted run

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Prefix cũ `claude/linux-daily-...` chỉ dùng để phát hiện duplicate.

Nếu branch đúng issue/date đã tồn tại nhưng chưa có PR và head branch == head `main`, đây là **interrupted empty branch**. Scheduled Task phải resume branch đó và ghi bài tiếp; không tạo branch thứ hai cho cùng issue/date.

Capability phải được xác định trước khi tạo branch mới để tránh để lại branch rỗng.

## Quy trình một bài mới — local one pass

1. kiểm cadence, duplicate và capability;
2. chuẩn bị bài/source-backed review/STYLE metadata;
3. chạy `publish.py prepare`, `cadence.py record`, `pr_preflight.py`;
4. tạo/resume branch `chatgpt/linux-daily-<NNN>-<YYYYMMDD>` từ `main`;
5. commit chính xác source + generated artifacts đã materialize;
6. push và mở/resume PR vào `main`;
7. kiểm duplicate/state/diff/review thread rồi chuyển PR sang Ready **trước khi CI success**;
8. `CI` chạy read-only trên exact head SHA;
9. nếu CI fail, sửa source/generator bằng commit bình thường rồi lặp preflight → push;
10. nếu CI success, `Linux Daily Auto Merge` xác thực lại PR/head/review và gọi REST merge endpoint với exact SHA + `merge_method=squash`.

## Quy trình một bài mới — API-only fallback

Thứ tự bắt buộc là **ghi source → dispatch → chờ xong → mới mở PR**. Agent API-only không
chạy được generator, còn CI thì bị `workflow_safety` cấm commit, nên artifact chỉ có thể do
workflow `Materialize Artifacts` dựng.

1. kiểm cadence, duplicate và GitHub write capability trước khi tạo branch mới;
2. chuẩn bị nội dung + source-of-truth metadata trong agent;
3. resume interrupted branch nếu có; nếu không, tạo branch chuẩn từ `main`;
4. ghi source core (`posts/`, `topics.md`, `state.json`, metadata JSON) bằng GitHub API;
   không đoán nội dung artifact render;
5. dispatch `Materialize Artifacts` cho branch đó và **chờ run kết thúc**:

   ```text
   POST /repos/{owner}/{repo}/actions/workflows/materialize-artifacts.yml/dispatches
   {"ref": "main",
    "inputs": {"branch": "chatgpt/linux-daily-<NNN>-<YYYYMMDD>",
               "confirm": "materialize-artifacts"}}
   ```

   `ref` luôn là `main` (lấy định nghĩa workflow từ default branch); branch cần dựng nằm ở
   input `branch`. Dispatch cần quyền `actions: write`; 403 là capability blocker phải báo
   ngay, không im lặng bỏ qua;
6. run đỏ → **không mở PR**; đọc log run và báo blocker. Không commit đoán artifact để dò CI;
7. run xanh → mở PR, kiểm state/diff/duplicate/review thread, rồi chuyển Ready **ngay, không
   chờ CI success**. Sau khi materialize xanh thì artifact đã đúng nên không còn lý do giữ
   Draft; Draft chỉ dành cho trường hợp chưa dispatch hoặc dispatch đỏ;
8. dùng CI read-only làm remote re-validation cho phần source;
9. nếu CI fail, đọc log, sửa source trên cùng branch rồi **dispatch lại** trước khi chờ CI;
10. exact-head CI success sẽ kích `Linux Daily Auto Merge`;
11. nếu CI success xảy ra lúc PR còn Draft, chuyển Ready rồi rerun CI/quality-gate trên cùng SHA để tạo workflow_run success mới.

Không tạo helper/workflow one-shot kiểu `prNN_finalizer` hoặc `tools/prNN_*.py` rồi để Actions tự sửa repository. Không tạo no-op commit chỉ để kích hoạt auto-merge.

## CI và auto-merge

`CI` giữ `contents: read` và phải đi qua `quality-gate`: PR hygiene, lint/test/validator/build/link/smoke theo workflow hiện hành.

`linux-daily-auto-merge.yml` là ngoại lệ ghi hẹp cho bài hằng ngày:

- trigger `workflow_run` của `CI`;
- chỉ chạy khi CI conclusion `success` và source event là `pull_request`;
- không checkout PR code;
- chỉ branch chuẩn từ cùng repo và do repo owner mở;
- PR phải open và non-Draft tại lúc workflow validate;
- exact current PR head SHA phải bằng `workflow_run.head_sha`;
- không `CHANGES_REQUESTED`, không unresolved thread;
- gọi merge API với exact SHA precondition và squash;
- không stage/commit/push, không `--admin`, không sửa branch protection.

Vì auto-merge kiểm `draft=false`, PR bài hằng ngày phải Ready **trước khi CI success**. Nếu ordering bị lỡ, rerun CI trên cùng exact SHA sau khi Ready; không tạo commit rỗng.

`release.yml` vẫn là workflow release thủ công với confirmation + exact-main-SHA gate.

## Khi cần rollback

Nếu auto-merge gây vấn đề, disable hoặc xóa `.github/workflows/linux-daily-auto-merge.yml` bằng maintenance PR. Khi workflow này không tồn tại, PR vẫn đi qua CI bình thường và có thể squash-merge thủ công.

Nếu API-only fallback gây vấn đề, có thể tạm ép Scheduled Task chỉ dùng local flow bằng cách sửa contract qua maintenance PR; không cần thay CI hay branch protection.

Nếu Scheduled Task gặp vấn đề, disable task trong ChatGPT. Repository vẫn tự đủ để vận hành thủ công bằng `AGENTS.md`, `STYLE.md`, `tools/cadence.py`, `tools/pr_preflight.py` và `tools/publish.py`.
