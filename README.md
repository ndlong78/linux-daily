# Linux Daily

Linux Daily là website tự sinh bài học Linux/Unix system administration bằng tiếng Việt theo **nhịp 1 bài/ngày**. Workflow hiện tại dùng **ChatGPT Plus Scheduled Task** để điều phối, GitHub để lưu mã nguồn/PR và GitHub Actions làm quality gate.

Website public được phục vụ qua **Cloudflare Worker** tại `https://linux.no.id.vn/`. Repository không dùng GitHub Pages làm lớp hosting public.

## Kiến trúc vận hành

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
                  technical review
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
- `state.json` — trạng thái cadence (`last_issue`, `last_generated_at`, `last_published_date`).
- `topics.md` — lịch sử chủ đề và thứ tự series.
- `site.json` — metadata website và public base URL `https://linux.no.id.vn/`.
- `templates/post.template.html` — khung bài.
- `templates/index.template.html` — khung trang chủ.
- `tools/build.py` — build + quality gate local.
- `tools/validate_sources.py` — source-backed technical gate cho bài mới.
- `.github/workflows/ci.yml` — quality gate trên PR/push.

## Cấu trúc repo

```text
.
├── AGENTS.md
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
│   └── style.css
├── templates/
│   ├── post.template.html
│   └── index.template.html
├── posts/
│   ├── post-001-static-ip.html
│   └── social/              # artifact lịch sử; hiện không sinh mới mặc định
├── tools/
│   ├── cadence.py
│   ├── build.py
│   ├── build_index.py
│   ├── build_feed.py
│   ├── build_sitemap.py
│   ├── postmeta.py
│   ├── validate_sources.py
│   └── render_code.py
├── tests/
├── docs/
│   ├── CHATGPT-OPERATIONS.md
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
python3 tools/build.py --check
```

## Source-backed Technical Review

Từ **Linux Daily #019**, mỗi bài mới phải có tối thiểu **2 nguồn official/upstream**. Metadata `ld-meta` bổ sung:

```json
{
  "review_status": "reviewed",
  "sources": [
    {"title": "Official documentation", "url": "https://...", "kind": "official"},
    {"title": "Upstream documentation", "url": "https://...", "kind": "upstream"}
  ]
}
```

Cùng danh sách đó phải được hiển thị trong `<section class="sources">` với title/URL/thứ tự khớp metadata. `tools/validate_sources.py` kiểm tra:

- ít nhất 2 nguồn primary;
- URL HTTPS đầy đủ, không trùng;
- `kind` là `official` hoặc `upstream`;
- nguồn hiển thị khớp metadata;
- `review_status` phải là `reviewed` hoặc `published` để qua merge gate.

Bài #001–#018 được grandfather để không phải backfill toàn bộ series trong cùng một PR. Claim cũ không được sao chép sang bài mới nếu chưa kiểm chứng lại.

## Quy trình bài mới

1. ChatGPT đọc `AGENTS.md`, `state.json`, `topics.md` và trạng thái GitHub hiện tại.
2. Kiểm tra cadence hằng ngày và duplicate branch/PR cho issue kế tiếp.
3. Chọn trục theo chu kỳ 7 và tránh chủ đề trùng.
4. Tạo HTML theo template, metadata `ld-meta` và 2 SVG.
5. Kiểm tra claim kỹ thuật bằng tài liệu official/upstream hiện hành; ghi `sources` và `review_status`.
6. Cập nhật `topics.md`, `state.json` và learning metadata/path nếu cần.
7. Chạy `python3 tools/build.py` để regenerate các artifact site deterministic.
8. Chạy `python3 tools/build.py --check`.
9. Dùng branch:

```text
chatgpt/linux-daily-<NNN>-<YYYYMMDD>
```

10. Mở PR vào `main`; đợi `quality-gate` xanh; người dùng review và merge.

**Facebook/X đang tạm dừng.** Bài mới không cần tạo `posts/social/post-<NNN>-facebook.txt`, `post-<NNN>-x.txt` hoặc ảnh code social. Các artifact lịch sử vẫn được giữ nguyên.

Trong thời gian migration, agent vẫn phải phát hiện prefix cũ `claude/linux-daily-...` để tránh sinh trùng, nhưng **không tạo branch Claude mới**.

## ChatGPT Plus Scheduled Task

Task vận hành chính là **Linux Daily Operator**, chạy lúc **07:00 hằng ngày** theo giờ Việt Nam. Task đọc repository mỗi lần chạy; business rules lâu dài nằm trong `AGENTS.md`, không nằm duy nhất trong prompt của task.

Khi chưa tới cadence, task không tạo bài. Khi tới cadence, task chuẩn bị bài và technical review; remote write trên GitHub phải tuân theo quyền/ủy quyền hiện hành của người dùng.

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
python3 tools/build.py --check
```

Có thể chạy source gate riêng:

```bash
python3 tools/validate_sources.py
```

`tools/render_code.py` và social validators vẫn được giữ để audit/tái sử dụng artifact lịch sử nhưng không còn nằm trong contract tạo bài mới mặc định.

## Website

Repo là source của static site; lớp public hosting nằm trên **Cloudflare Worker**. Public URL chuẩn được khai báo duy nhất trong `site.json`:

```text
https://linux.no.id.vn/
```

`index.html`, `feed.xml`, `sitemap.xml` và `robots.txt` đều được build từ metadata trong repo. Không dùng file `CNAME` và không phụ thuộc GitHub Pages để phục vụ domain public.

## An toàn vận hành

- Không commit secret/API key vào repository.
- Không push trực tiếp `main`.
- Không merge khi CI chưa xanh.
- Không dùng `topics.md` làm clock cadence.
- Không tạo bài nếu branch/PR cho issue kế tiếp đã tồn tại.
- FreeBSD luôn được xử lý riêng, không áp lệnh Linux cho FreeBSD.
- Với networking, firewall, storage, backup/restore, auth/permissions và automation shell: luôn rà rollback, destructive flags và khác biệt phiên bản trước khi `reviewed`.

## Migration khỏi Claude Routine

Từ 2026-08-07, Linux Daily đã chuyển sang ChatGPT Plus làm bộ điều phối. Các entrypoint Claude (`.claude/skills/...` và `routine-prompt.txt`) đã được loại bỏ; `AGENTS.md` là hợp đồng vận hành chính trong repo.
