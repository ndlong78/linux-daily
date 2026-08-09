# Vận hành Linux Daily bằng ChatGPT Plus

Linux Daily được vận hành theo mô hình **ChatGPT Plus + Scheduled Task + GitHub + GitHub Actions**. Không cần OpenAI API cho workflow hiện tại.

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
                dừng             ▼
                        chatgpt/linux-daily-...
                                 │
                                 ▼
                                PR
                                 │
                                 ▼
                         GitHub Actions CI
                                 │
                                 ▼
                           người dùng merge
```

## Scheduled Task

Task chuẩn chạy **07:00 mỗi ngày** theo `Asia/Ho_Chi_Minh`.

Mỗi lần chạy, ChatGPT phải:

1. Đọc `AGENTS.md` **và `STYLE.md`** từ `main` mới nhất.
2. Đọc `state.json` và kiểm tra cadence mặc định 1 ngày.
3. Nếu chưa sang ngày phát hành kế tiếp: kết thúc, không tạo thay đổi.
4. Nếu tới nhịp: xác định issue kế tiếp, kiểm tra trục, tránh chủ đề trùng và ưu tiên progression hợp lý với các bài trước.
5. Kiểm tra branch/PR đang mở cho issue đó, bao gồm cả prefix `chatgpt/` và legacy `claude/`.
6. Chuẩn bị bài theo `templates/post.template.html`, `AGENTS.md`, `STYLE.md` và validators hiện hành.
7. Từ #019: kiểm tra claim/lệnh bằng ít nhất 2 nguồn official/upstream, ghi `review_status` + `sources` và tạo section **Nguồn kỹ thuật** khớp metadata.
8. Từ #041: ghi `tested_on`, `last_verified`, `changes_system`; khai báo quyền command block; dùng numbered steps; có verification output; thêm rollback khi thay đổi hệ thống.
9. Chạy structural gate + source-backed gate + STYLE.md gate thông qua `python3 tools/publish.py check`.
10. Không sinh Facebook/X hoặc ảnh code social trong giai đoạn social output đang tạm dừng.
11. Nếu chưa có quyền GitHub write rõ ràng trong phiên tự động, chỉ báo gói thay đổi cho người dùng; không tự push/merge.

## Source of truth

- `AGENTS.md`: hợp đồng vận hành của AI agent.
- `STYLE.md`: chuẩn ngôn ngữ, cấu trúc trình bày, code block và safety affordance.
- `state.json`: trạng thái cadence.
- `topics.md`: lịch sử chủ đề và thứ tự series.
- `templates/post.template.html`: khung bài.
- `tools/publish.py`: entrypoint quality gate local.
- `tools/validate_sources.py`: source-backed technical gate.
- `tools/validate_style.py`: STYLE.md audit/enforcement.
- `.github/workflows/ci.yml`: quality gate trên GitHub.

Không dùng prompt Scheduled Task làm nơi duy nhất giữ business rules. Prompt task chỉ là entrypoint; quy tắc bền vững nằm trong repository.

## STYLE.md review

Linux Daily #041+ phải đạt style contract trước khi được coi là ready for review:

- metadata hiển thị `Tested on` + `Last verified`;
- `ld-meta` có `tested_on`, `last_verified`, `changes_system`;
- Mục tiêu + Yêu cầu tiên quyết;
- Các bước thực hiện dùng `<ol class="steps">`;
- mọi code block có `language-*`;
- command block shell có `data-run-as="user|sudo|root"`;
- verification có Expected Output/Kết quả mong đợi;
- `changes_system=true` thì có **Gỡ / Hoàn tác**;
- không shell prompt trong command block, không `curl | sh` chạy trực tiếp, không placeholder legacy kiểu `YOUR_*`.

#001–#040 được audit nhưng chưa fail CI. Không được tận dụng legacy exemption cho bài mới. Backfill theo batch riêng.

```bash
python3 tools/validate_style.py
python3 tools/validate_style.py --audit
```

## Source-backed technical review

Với bài #019+, operator phải kiểm tra các claim chính trước khi đặt `review_status="reviewed"`. Tối thiểu 2 nguồn phải có `kind` là `official` hoặc `upstream`, dùng HTTPS và không trùng URL.

Các vùng cần review sâu hơn:

- networking/firewall: remote lockout, IPv4/IPv6, policy/port và rollback;
- storage/filesystem: device/path, destructive flags, resize direction;
- backup/restore: có kiểm chứng restore;
- auth/permissions: quyền root/sudo, đường lui khi hardening;
- shell automation: shell thực thi, PATH, quoting, exit-code semantics và portability.

## Social output

Facebook/X và ảnh code social đang **tạm dừng** để giảm khối lượng generation/review khi cadence tăng lên hằng ngày.

## Quyền ghi GitHub

ChatGPT có thể đọc repository, PR và CI khi connector cho phép. Các hành động ghi như commit, push, mở PR và merge phải tuân theo quyền/ủy quyền của người dùng trong phiên làm việc.

Nguyên tắc an toàn:

- không push trực tiếp `main`;
- không tự merge;
- không ghi state khi cadence chưa tới;
- không tạo issue trùng nếu branch/PR đã tồn tại;
- không bypass CI;
- không đặt `review_status="reviewed"` khi nguồn chưa được kiểm tra;
- không giảm STYLE.md enforcement chỉ để CI xanh.

## Branch convention

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Prefix cũ `claude/linux-daily-...` chỉ được giữ để phát hiện duplicate trong thời gian chuyển đổi.

## Quy trình một bài mới

```bash
python3 tools/cadence.py gate
python3 tools/cadence.py next
# tạo HTML + technical sources + STYLE.md metadata
python3 tools/build_index.py
python3 tools/cadence.py record
python3 tools/publish.py check
```

Nếu tất cả kiểm tra sạch và người dùng đã cấp quyền remote write, tạo branch `chatgpt/...`, commit chính xác các file liên quan, push và mở PR vào `main`.

## CI

PR phải đi qua `quality-gate`, gồm lint/test/validator/build/smoke tests theo workflow hiện hành. `tools/publish.py check` bao gồm STYLE.md gate; CI xanh là điều kiện kỹ thuật để merge.

## Self-fix CI loop

Sau khi push branch hoặc cập nhật một PR, ChatGPT phải coi CI là một vòng lặp có trạng thái:

```text
push
  ↓
đọc lại PR → lấy exact head SHA
  ↓
kiểm checks của SHA đó
  ├─ pending/running → chưa được kết luận
  ├─ failed → đọc log → sửa → regenerate → local check → push lại
  └─ all success → kiểm diff → ready for review
```

- local PASS không thay thế GitHub Actions PASS;
- run xanh của SHA cũ không có giá trị cho SHA mới;
- check đang chờ/chạy được coi là chưa hoàn tất;
- không báo PR sẵn sàng merge khi chưa chứng minh exact head SHA sạch.

## Migration khỏi Claude Routine

Migration PR #23 đã merge ngày 2026-08-07. `AGENTS.md` + `STYLE.md` là contract AI chính; entrypoint Claude cũ đã được loại bỏ.

## Khi cần rollback

Nếu Scheduled Task gặp vấn đề, disable task trong ChatGPT. Repository vẫn tự đủ để vận hành thủ công bằng `AGENTS.md`, `STYLE.md`, `tools/cadence.py` và `tools/publish.py`.
