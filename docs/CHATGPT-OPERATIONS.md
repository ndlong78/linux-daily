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
          cadence đủ 2 ngày?
           │             │
          không          có
           │             │
         dừng            ▼
                    chuẩn bị bài
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
2. Đọc `state.json` và kiểm tra cadence 2 ngày.
3. Nếu chưa tới nhịp: kết thúc, không tạo thay đổi.
4. Nếu tới nhịp: xác định issue kế tiếp, kiểm tra trục, tránh chủ đề trùng.
5. Kiểm tra branch/PR đang mở cho issue đó, bao gồm cả prefix `chatgpt/` và legacy `claude/`.
6. Chuẩn bị bài theo template/meta/validator hiện hành.
7. Kiểm tra claim có thể thay đổi bằng nguồn chính thức hiện hành.
8. Nếu chưa có quyền GitHub write rõ ràng trong phiên tự động, chỉ báo gói thay đổi cho người dùng; không tự push/merge.

## Source of truth

- `AGENTS.md`: hợp đồng vận hành của AI agent.
- `state.json`: trạng thái cadence.
- `topics.md`: lịch sử chủ đề và thứ tự series.
- `templates/post.template.html`: khung bài.
- `templates/index.template.html`: khung trang chủ.
- `tools/build.py`: build + quality gate tại local.
- `.github/workflows/ci.yml`: quality gate trên GitHub.

Không dùng prompt Scheduled Task làm nơi duy nhất giữ business rules. Prompt task chỉ là entrypoint; quy tắc bền vững nằm trong repository.

## Quyền ghi GitHub

ChatGPT có thể đọc repository, PR và CI khi connector cho phép. Các hành động ghi như commit, push, mở PR và merge phải tuân theo quyền/ủy quyền của người dùng trong phiên làm việc.

Nguyên tắc an toàn:

- không push trực tiếp `main`;
- không tự merge;
- không ghi state khi cadence chưa tới;
- không tạo issue trùng nếu branch/PR đã tồn tại;
- không bypass CI.

## Branch convention

Từ migration này, branch bài mới dùng:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

Prefix cũ `claude/linux-daily-...` chỉ được giữ để phát hiện duplicate trong thời gian chuyển đổi.

## Quy trình một bài mới

```bash
python3 tools/cadence.py gate
python3 tools/cadence.py next
# tạo HTML + social + ảnh code
python3 tools/build_index.py
python3 tools/cadence.py record
python3 tools/build.py --check
```

Nếu tất cả kiểm tra sạch và người dùng đã cấp quyền remote write, tạo branch `chatgpt/...`, commit chính xác các file liên quan, push và mở PR vào `main`.

## CI

PR phải đi qua `quality-gate`, gồm lint/test/validator/build/smoke tests theo workflow hiện hành. CI xanh là điều kiện kỹ thuật để merge; người dùng vẫn là người quyết định cuối cùng.

## Migration khỏi Claude Routine

Sau khi PR migration này được merge:

1. Tắt Claude Routine cũ để tránh hai scheduler cùng cạnh tranh.
2. Scheduled Task `Linux Daily Operator` trong ChatGPT Plus trở thành scheduler chính.
3. Xóa `.claude/skills/linux-daily/SKILL.md` và `routine-prompt.txt` khỏi repository.
4. `AGENTS.md` trở thành quy tắc AI chính.
5. `state.json`, cadence, structured content pipeline và GitHub Actions được giữ nguyên.

## Khi cần rollback

Nếu Scheduled Task gặp vấn đề, chỉ cần disable task trong ChatGPT. Repository vẫn tự đủ để vận hành thủ công bằng `AGENTS.md`, `tools/cadence.py` và `tools/build.py`; không cần rollback dữ liệu nội dung.
