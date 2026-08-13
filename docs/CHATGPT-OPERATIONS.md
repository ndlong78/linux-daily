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
                    chuẩn bị bài
                         │
          source-backed + style review
                         │
              duplicate branch/PR?
                  │              │
                 có             không
                  │              │
              resume PR          ▼
                        chatgpt/linux-daily-...
                                 │
                       generate + preflight
                                 │
                                 ▼
                            PR → Ready
                                 │
                                 ▼
                    GitHub Actions CI read-only
                         │               │
                        fail           success
                         │               │
                    giữ PR mở            ▼
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
5. Kiểm tra branch/PR đang mở cho issue đó, gồm prefix `chatgpt/` và legacy `claude/`. Nếu đã có PR đúng issue thì resume, không tạo bản trùng.
6. Chuẩn bị bài theo `templates/post.template.html`, `AGENTS.md`, `STYLE.md` và validators hiện hành.
7. Từ #019: kiểm tra claim/lệnh bằng ít nhất 2 nguồn official/upstream, ghi `review_status` + `sources`, tạo section **Nguồn kỹ thuật** khớp metadata.
8. Từ #041: ghi `tested_on`, `last_verified`, `changes_system`; khai báo quyền command block; dùng numbered steps; có verification output; thêm rollback khi thay đổi hệ thống.
9. Materialize generated artifacts trong feature branch và chạy `python3 tools/pr_preflight.py` trước commit/push.
10. Không tạo finalizer/self-mutating workflow để Actions sửa, commit hoặc push ngược branch.
11. Không sinh Facebook/X hoặc ảnh code social trong giai đoạn social output đang tạm dừng.
12. Khi đã có quyền GitHub write của Scheduled Task, được tạo branch/commit/push/PR theo contract. Không push trực tiếp `main`.
13. Với PR bài hằng ngày hợp lệ, chuyển PR sang **Ready for review** sau khi diff/state/duplicate/review gate sạch. Task không cần polling CI đến lúc merge.
14. Sau đó GitHub tự xử lý: `CI` validate exact head SHA; nếu success, `.github/workflows/linux-daily-auto-merge.yml` thực hiện guarded squash merge.

## Source of truth

- `AGENTS.md`: hợp đồng vận hành của AI agent.
- `STYLE.md`: chuẩn ngôn ngữ, cấu trúc, code block và safety affordance.
- `state.json`: trạng thái cadence.
- `topics.md`: lịch sử chủ đề và thứ tự series.
- `templates/post.template.html`: khung bài.
- `tools/publish.py`: entrypoint quality gate local.
- `tools/pr_preflight.py`: one-pass PR preflight.
- `tools/pr_hygiene.py`: guard commit/path của PR.
- `tools/validate_sources.py`: source-backed technical gate.
- `tools/validate_style.py`: STYLE.md audit/enforcement.
- `tools/workflow_safety.py`: policy gate cho GitHub Actions.
- `.github/workflows/ci.yml`: read-only quality gate trên PR.
- `.github/workflows/linux-daily-auto-merge.yml`: post-CI exact-SHA squash merge cho PR bài hằng ngày.

Không dùng prompt Scheduled Task làm nơi duy nhất giữ business rules. Prompt task chỉ là entrypoint; quy tắc bền vững nằm trong repository.

## STYLE.md review

Linux Daily #041+ phải đạt style contract:

- metadata hiển thị `Tested on` + `Last verified`;
- `ld-meta` có `tested_on`, `last_verified`, `changes_system`;
- Mục tiêu + Yêu cầu tiên quyết;
- các bước thực hiện dùng `<ol class="steps">`;
- mọi code block có `language-*`;
- command block shell có `data-run-as="user|sudo|root"`;
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
- auto-merge chỉ áp dụng cho branch chuẩn `chatgpt/linux-daily-<NNN>-<YYYYMMDD>`;
- auto-merge chỉ chạy sau `CI` success của **exact head SHA**;
- auto-merge không checkout PR code với write token;
- merge method bắt buộc `squash`; không dùng `--admin` hoặc bypass protection;
- `CHANGES_REQUESTED` hoặc unresolved review thread phải chặn merge.

## Branch convention

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Prefix cũ `claude/linux-daily-...` chỉ dùng để phát hiện duplicate.

## Quy trình một bài mới — one pass

```bash
python3 tools/cadence.py gate
python3 tools/cadence.py next
# tạo HTML + technical sources + STYLE.md metadata
python3 tools/publish.py prepare
python3 tools/cadence.py record
python3 tools/pr_preflight.py
```

Nếu tất cả local/preflight gate sạch và Scheduled Task đã có quyền remote write:

1. tạo/resume branch `chatgpt/linux-daily-<NNN>-<YYYYMMDD>` từ `main`;
2. commit chính xác source + generated artifacts đã materialize;
3. push và mở/resume PR vào `main`;
4. kiểm duplicate/state/diff/review thread rồi chuyển PR sang Ready;
5. `CI` chạy read-only trên exact head SHA;
6. nếu CI fail, PR giữ nguyên để operator sửa ở lần chạy/phiên tiếp theo;
7. nếu CI success, `Linux Daily Auto Merge` xác thực lại PR/head/review và gọi REST merge endpoint với exact SHA + `merge_method=squash`;
8. nếu branch protection/review requirement khác chưa đạt, merge API fail và PR vẫn mở.

Không tạo helper/workflow one-shot kiểu `prNN_finalizer` hoặc `tools/prNN_*.py` rồi để Actions tự sửa repository.

## CI và auto-merge

`CI` giữ `contents: read` và phải đi qua `quality-gate`: PR hygiene, lint/test/validator/build/link/smoke theo workflow hiện hành.

`linux-daily-auto-merge.yml` là ngoại lệ ghi hẹp cho bài hằng ngày:

- trigger `workflow_run` của `CI`;
- chỉ chạy khi CI conclusion `success` và source event là `pull_request`;
- không checkout PR code;
- chỉ branch chuẩn từ cùng repo và do repo owner mở;
- exact current PR head SHA phải bằng `workflow_run.head_sha`;
- không `CHANGES_REQUESTED`, không unresolved thread;
- gọi merge API với exact SHA precondition và squash;
- không stage/commit/push, không `--admin`, không sửa branch protection.

`release.yml` vẫn là workflow release thủ công với confirmation + exact-main-SHA gate.

## Khi cần rollback

Nếu auto-merge gây vấn đề, disable hoặc xóa `.github/workflows/linux-daily-auto-merge.yml` bằng maintenance PR. Khi workflow này không tồn tại, PR vẫn đi qua CI bình thường và có thể squash-merge thủ công.

Nếu Scheduled Task gặp vấn đề, disable task trong ChatGPT. Repository vẫn tự đủ để vận hành thủ công bằng `AGENTS.md`, `STYLE.md`, `tools/cadence.py`, `tools/pr_preflight.py` và `tools/publish.py`.
