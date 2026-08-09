# Linux Daily

Linux Daily là website tự sinh bài học Linux/Unix system administration bằng tiếng Việt theo **nhịp 1 bài/ngày**. Workflow hiện tại dùng **ChatGPT Plus Scheduled Task** để điều phối, GitHub để lưu mã nguồn/PR và GitHub Actions làm quality gate.

Website public được phục vụ qua **Cloudflare Worker** tại `https://linux.no.id.vn/`. Repository không dùng GitHub Pages làm lớp hosting public.

## Kiến trúc vận hành

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
            technical + style review
                         │
                         ▼
                chatgpt/... branch
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
                Cloudflare Worker
                         │
                         ▼
                https://linux.no.id.vn/
```

**GitHub Actions là cổng kỹ thuật cuối cùng; ChatGPT không được bypass CI hoặc push thẳng vào `main`.**

## Source of truth

- `AGENTS.md` — hợp đồng vận hành cho ChatGPT/AI agent.
- `STYLE.md` — chuẩn bắt buộc về ngôn ngữ, cấu trúc trình bày, code block và safety affordance.
- `state.json` — trạng thái cadence (`last_issue`, `last_generated_at`, `last_published_date`).
- `topics.md` — lịch sử chủ đề và thứ tự series.
- `site.json` — metadata website và public base URL `https://linux.no.id.vn/`.
- `templates/post.template.html` — khung bài.
- `templates/index.template.html` — khung trang chủ.
- `tools/build.py` — build + structural/source quality gate local.
- `tools/validate_sources.py` — source-backed technical gate.
- `tools/validate_style.py` — audit STYLE.md toàn lịch sử và enforce từ bài #041.
- `.github/workflows/ci.yml` — quality gate trên PR/push.

## Cấu trúc repo

```text
.
├── AGENTS.md
├── STYLE.md
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── site.json
├── state.json
├── topics.md
├── index.html
├── feed.xml
├── sitemap.xml
├── robots.txt
├── assets/
├── templates/
│   ├── post.template.html
│   └── index.template.html
├── posts/
├── tools/
│   ├── cadence.py
│   ├── build.py
│   ├── publish.py
│   ├── validate_sources.py
│   ├── validate_style.py
│   └── ...
├── tests/
├── docs/
│   ├── CHATGPT-OPERATIONS.md
│   ├── STYLE-AUDIT.md
│   └── ROADMAP.md
└── .github/
    ├── CODEOWNERS
    ├── BRANCH-PROTECTION.md
    └── workflows/ci.yml
```

## Repository governance

- License: MIT (`LICENSE`).
- Hướng dẫn đóng góp: `CONTRIBUTING.md`.
- Chính sách báo cáo vấn đề bảo mật: `SECURITY.md`.
- Default reviewer/owner: `.github/CODEOWNERS`.
- Baseline bảo vệ `main`: `.github/BRANCH-PROTECTION.md`.

Các thay đổi vào `main` phải đi qua pull request và `quality-gate` phải xanh trước khi merge.

## Cadence hằng ngày

Scheduler chạy mỗi ngày và **không dùng ngày trong bài làm clock**. Quyết định cadence dựa trên `state.json.last_generated_at`; mặc định `tools/cadence.py` dùng interval **1 ngày**.

```bash
python3 tools/cadence.py status
python3 tools/cadence.py gate
python3 tools/cadence.py next
```

- `gate` exit `0`: đã tới ngày phát hành kế tiếp, có thể tạo bài.
- `gate` exit `10`: vẫn trong cùng ngày cadence, không thay đổi gì.

Sau khi sinh bài hoàn chỉnh:

```bash
python3 tools/build.py
python3 tools/cadence.py record
python3 tools/publish.py check
```

## STYLE.md quality gate

Từ **Linux Daily #041**, bài mới phải đáp ứng `STYLE.md` trước khi merge. Gate kiểm tra các contract máy đọc được, gồm:

- `ld-meta.tested_on`, `last_verified`, `changes_system`;
- metadata `Tested on` / `Last verified` hiển thị trong bài;
- Mục tiêu, Yêu cầu tiên quyết, Các bước thực hiện, Kiểm chứng, Lưu ý & Khắc phục lỗi, Bài tập;
- `<ol class="steps">` cho quy trình tuyến tính;
- `language-*` cho mọi code block;
- `data-run-as="user|sudo|root"` cho command block shell;
- Expected Output/Kết quả mong đợi trong verification;
- Gỡ / Hoàn tác khi `changes_system=true`;
- chặn shell prompt trong command block, placeholder legacy và `curl | sh` chạy trực tiếp.

Bài #001–#040 là **legacy baseline**: vẫn được audit nhưng chưa làm CI fail. Xem `docs/STYLE-AUDIT.md`.

```bash
python3 tools/validate_style.py
python3 tools/validate_style.py --audit
```

## Source-backed Technical Review

Từ **Linux Daily #019**, mỗi bài mới phải có tối thiểu **2 nguồn official/upstream**. Metadata `ld-meta` bổ sung `review_status` và `sources`; danh sách nguồn hiển thị phải khớp metadata.

`tools/validate_sources.py` kiểm tra URL, loại nguồn, số lượng và trạng thái review. Claim cũ không được sao chép sang bài mới nếu chưa kiểm chứng lại.

## Quy trình bài mới

1. ChatGPT đọc `AGENTS.md`, `STYLE.md`, `state.json`, `topics.md` và trạng thái GitHub hiện tại.
2. Kiểm tra cadence hằng ngày và duplicate branch/PR cho issue kế tiếp.
3. Chọn trục theo chu kỳ 7 và tránh chủ đề trùng.
4. Tạo HTML theo template, metadata `ld-meta` và 2 SVG.
5. Kiểm tra claim kỹ thuật bằng tài liệu official/upstream hiện hành; ghi `sources` và `review_status`.
6. Kiểm tra STYLE.md: metadata môi trường test, quyền lệnh, step ordering, verification output, rollback và FreeBSD portability.
7. Cập nhật `topics.md`, `state.json` và learning metadata/path nếu cần.
8. Chạy generator deterministic.
9. Chạy `python3 tools/publish.py check`.
10. Dùng branch `chatgpt/linux-daily-<NNN>-<YYYYMMDD>`.
11. Mở PR vào `main`; đợi `quality-gate` xanh; người dùng review và merge.

**Facebook/X đang tạm dừng.** Bài mới không cần tạo social artifact mặc định.

## ChatGPT Plus Scheduled Task

Task vận hành chính là **Linux Daily Operator**, chạy lúc **07:00 hằng ngày** theo giờ Việt Nam. Task đọc repository mỗi lần chạy; business rules lâu dài nằm trong `AGENTS.md` và `STYLE.md`, không nằm duy nhất trong prompt của task.

Khi chưa tới cadence, task không tạo bài. Khi tới cadence, task chuẩn bị bài, technical review và STYLE.md review; remote write trên GitHub phải tuân theo quyền/ủy quyền hiện hành của người dùng.

Chi tiết: `docs/CHATGPT-OPERATIONS.md`.

## Build và kiểm tra local

Cài dependency:

```bash
python3 -m pip install -e ".[dev]"
```

Chạy quality gate:

```bash
ruff check tools/ tests/
pytest -q
python3 tools/publish.py check
```

Có thể chạy riêng:

```bash
python3 tools/validate_sources.py
python3 tools/validate_style.py --audit
```

## Website

Repo là source của static site; lớp public hosting nằm trên **Cloudflare Worker**. Public URL chuẩn được khai báo duy nhất trong `site.json` là `https://linux.no.id.vn/`.

## An toàn vận hành

- Không commit secret/API key vào repository.
- Không push trực tiếp `main`.
- Không merge khi CI chưa xanh.
- Không dùng `topics.md` làm clock cadence.
- Không tạo bài nếu branch/PR cho issue kế tiếp đã tồn tại.
- FreeBSD luôn được xử lý riêng, không áp lệnh Linux cho FreeBSD.
- Với networking, firewall, storage, backup/restore, auth/permissions và automation shell: luôn rà rollback, destructive flags và khác biệt phiên bản trước khi `reviewed`.
- Không bypass STYLE.md gate bằng cách giảm enforcement hoặc đổi metadata giả.

## Migration khỏi Claude Routine

Từ 2026-08-07, Linux Daily đã chuyển sang ChatGPT Plus làm bộ điều phối. Các entrypoint Claude đã được loại bỏ; `AGENTS.md` + `STYLE.md` là contract chính trong repo.
