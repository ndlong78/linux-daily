# Vận hành Linux Daily bằng ChatGPT Plus

Linux Daily được vận hành theo mô hình **ChatGPT Plus + Scheduled Task + GitHub + GitHub Actions**. Không cần OpenAI API cho workflow hiện tại.

## Kiến trúc

```text
ChatGPT Plus Scheduled Task (07:00 Asia/Ho_Chi_Minh)
                 │
                 ▼
          đọc GitHub main
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
               source-backed review
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
                                 │
                                 ▼
                         website trên main
```

## Scheduled Task

Task chuẩn chạy **07:00 mỗi ngày** theo `Asia/Ho_Chi_Minh`.

Mỗi lần chạy, ChatGPT phải:

1. Đọc `AGENTS.md` và trạng thái mới nhất của `main`.
2. Đọc `state.json` và kiểm tra cadence mặc định 1 ngày.
3. Nếu chưa sang ngày phát hành kế tiếp: kết thúc, không tạo thay đổi.
4. Nếu tới nhịp: xác định issue kế tiếp, kiểm tra trục, tránh chủ đề trùng và ưu tiên progression hợp lý với các bài trước.
5. Kiểm tra branch/PR đang mở cho issue đó, bao gồm cả prefix `chatgpt/` và legacy `claude/`.
6. Chuẩn bị bài theo template/meta/validator hiện hành.
7. Từ #019: kiểm tra claim/lệnh bằng ít nhất 2 nguồn official/upstream, ghi `review_status` + `sources`, và tạo section **Nguồn kỹ thuật** khớp metadata.
8. Chạy structural quality gate + source-backed gate.
9. Không sinh Facebook/X hoặc ảnh code social trong giai đoạn social output đang tạm dừng.
10. Nếu chưa có quyền GitHub write rõ ràng trong phiên tự động, chỉ báo gói thay đổi cho người dùng; không tự push/merge.

## Source of truth

- `AGENTS.md`: hợp đồng vận hành của AI agent.
- `state.json`: trạng thái cadence.
- `topics.md`: lịch sử chủ đề và thứ tự series.
- `templates/post.template.html`: khung bài.
- `templates/index.template.html`: khung trang chủ.
- `tools/build.py`: build + quality gate tại local.
- `tools/validate_sources.py`: source-backed technical gate từ bài #019.
- `.github/workflows/ci.yml`: quality gate trên GitHub.

Không dùng prompt Scheduled Task làm nơi duy nhất giữ business rules. Prompt task chỉ là entrypoint; quy tắc bền vững nằm trong repository.

## Source-backed technical review

Với bài #019+, operator phải kiểm tra các claim chính trước khi đặt `review_status="reviewed"`. Tối thiểu 2 nguồn phải có `kind` là `official` hoặc `upstream`, dùng HTTPS và không trùng URL.

Các vùng cần review sâu hơn:

- networking/firewall: remote lockout, IPv4/IPv6, policy/port và rollback;
- storage/filesystem: device/path, destructive flags, resize direction;
- backup/restore: có kiểm chứng restore;
- auth/permissions: quyền root/sudo, đường lui khi hardening;
- shell automation: shell thực thi, PATH, quoting, exit-code semantics và portability.

Bài #001–#018 được grandfather trong source validator. Backfill lịch sử làm theo PR riêng để diff nhỏ và dễ audit.

## Social output

Facebook/X và ảnh code social đang **tạm dừng** để giảm khối lượng generation/review khi cadence tăng lên hằng ngày.

- Không tạo social artifact mới theo mặc định.
- Không coi thiếu social artifact của bài mới là lỗi CI.
- Giữ nguyên `posts/social/` lịch sử để audit và có thể tái sử dụng sau này.
- Nếu bật lại social publishing, cập nhật contract + validator bằng một PR riêng.

## Quyền ghi GitHub

ChatGPT có thể đọc repository, PR và CI khi connector cho phép. Các hành động ghi như commit, push, mở PR và merge phải tuân theo quyền/ủy quyền của người dùng trong phiên làm việc.

Nguyên tắc an toàn:

- không push trực tiếp `main`;
- không tự merge;
- không ghi state khi cadence chưa tới;
- không tạo issue trùng nếu branch/PR đã tồn tại;
- không bypass CI;
- không đặt `review_status="reviewed"` khi nguồn chưa được kiểm tra.

## Branch convention

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Prefix cũ `claude/linux-daily-...` chỉ được giữ để phát hiện duplicate trong thời gian chuyển đổi.

## Quy trình một bài mới

```bash
python3 tools/cadence.py gate
python3 tools/cadence.py next
# tạo HTML + technical sources; không tạo social theo mặc định
python3 tools/build_index.py
python3 tools/cadence.py record
python3 tools/build.py --check
```

`tools/build.py --check` gọi validator cấu trúc hiện có và `tools/validate_sources.py`; social artifact không còn là merge gate cho bài mới.

Nếu tất cả kiểm tra sạch và người dùng đã cấp quyền remote write, tạo branch `chatgpt/...`, commit chính xác các file liên quan, push và mở PR vào `main`.

## CI

PR phải đi qua `quality-gate`, gồm lint/test/validator/build/smoke tests theo workflow hiện hành. Do CI gọi `tools/build.py --check`, source-backed gate cũng là một phần của quality gate. CI xanh là điều kiện kỹ thuật để merge; người dùng vẫn là người quyết định cuối cùng.

## Self-fix CI loop

Sau khi push branch hoặc cập nhật một PR, ChatGPT phải coi CI là một vòng lặp có trạng thái, không phải bước kiểm tra một lần:

```text
push
  ↓
đọc lại PR → lấy exact head SHA
  ↓
kiểm push + pull_request checks của SHA đó
  ├─ pending/running → chưa được kết luận
  ├─ failed → đọc log → sửa → regenerate → local check → push lại
  └─ all success → kiểm diff không còn helper tạm → ready for review
```

Quy tắc kết thúc:

- local PASS không thay thế GitHub Actions PASS;
- run xanh của SHA cũ không có giá trị cho SHA mới;
- phải kiểm cả `push` và `pull_request` nếu workflow tạo cả hai;
- check đang chờ/chạy được coi là chưa hoàn tất;
- helper workflow dùng để chẩn đoán phải được xóa trước vòng CI cuối;
- không báo PR “xong”, “sạch” hoặc “sẵn sàng merge” khi chưa chứng minh exact head SHA không còn check đỏ/pending.

Nếu CI fail, agent tự sửa theo log đến khi xanh trong phạm vi branch đã được người dùng cho phép; không yêu cầu người dùng tự chẩn đoán những lỗi có thể xử lý bằng repository/CI hiện có. Tuyệt đối không sửa gate theo hướng bỏ kiểm tra chỉ để đạt PASS.

## Migration khỏi Claude Routine

Migration PR #23 đã merge ngày 2026-08-07. `AGENTS.md` là quy tắc AI chính; `.claude/skills/linux-daily/SKILL.md` và `routine-prompt.txt` đã được loại bỏ. `state.json`, cadence, structured pipeline và GitHub Actions được giữ độc lập với vendor AI.

## Khi cần rollback

Nếu Scheduled Task gặp vấn đề, chỉ cần disable task trong ChatGPT. Repository vẫn tự đủ để vận hành thủ công bằng `AGENTS.md`, `tools/cadence.py` và `tools/build.py`; không cần rollback dữ liệu nội dung.
