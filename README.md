# Linux Daily

Repo tự sinh bài học Linux/Unix admin bằng tiếng Việt theo **nhịp 2 ngày/bài**,
xuất file HTML sẵn sàng đăng web, chạy tự động trên cloud qua **Claude Code Routine**.
Bài mới được commit vào nhánh `claude/…` để bạn duyệt rồi merge — không tự đăng.

## Cấu trúc repo
```
.
├── index.html              # TRANG CHỦ (tự dựng lại từ posts/)
├── assets/
│   └── style.css           # ⭐ CSS chung — template CỐ ĐỊNH của cả site
├── templates/
│   ├── post.template.html  # khung chuẩn cho mỗi bài (có khối meta + link về trang chủ)
│   └── index.template.html # template Jinja2 của trang chủ
├── .claude/skills/linux-daily/
│   └── SKILL.md            # hướng dẫn Claude (file chính)
├── posts/
│   ├── post-001-static-ip.html   # bài (có <script id="ld-meta"> + link ../assets/style.css)
│   └── social/                   # khối Facebook / X + ảnh code
│       ├── post-001-facebook.txt
│       ├── post-001-x.txt
│       └── post-001-code.png
├── tools/
│   ├── build.py            # MỘT lệnh: dựng index.html + quality gate
│   ├── build_index.py      # dựng trang chủ từ meta qua Jinja2
│   ├── postmeta.py         # đọc khối metadata & text hiển thị (không regex)
│   ├── render_code.py      # tạo ảnh code cho FB/X
│   ├── cadence.py          # cổng nhịp + state.json (số bài, mốc sinh thực)
│   └── fonts/              # JetBrains Mono (Vietnamese)
├── topics.md               # nhật ký chủ đề + mốc giữ nhịp 2 ngày
├── state.json              # trạng thái nhịp (last_issue, last_generated_at…)
├── routine-prompt.txt      # câu lệnh dán vào Routine
├── .nojekyll               # phục vụ HTML nguyên trạng trên Pages
└── README.md
```

## Template cố định (một nguồn duy nhất)
Toàn bộ giao diện nằm ở **`assets/style.css`**. Mọi trang (trang chủ + các bài)
đều liên kết tới file này, nên **đổi một chỗ là cả site đổi theo** — không còn CSS
lặp trong từng bài. Khung HTML của một bài là `templates/post.template.html`; skill
copy khung này rồi điền nội dung, giữ nguyên các link `assets/style.css` và
`index.html`.

Mỗi trang bài có **hai link về trang chủ**: ở header (`← Linux Daily`) và ở footer
(`← Về trang chủ Linux Daily`).

Đổi màu/typography toàn site: sửa `assets/style.css`. Đổi bố cục bài: sửa
`templates/post.template.html`.

Lưu ý xem thử: vì CSS đã tách chung, mở lẻ một file `posts/*.html` bằng trình duyệt
mà thiếu `assets/style.css` bên cạnh sẽ hiển thị mộc. Cứ giữ nguyên cấu trúc thư mục
(hoặc xem qua GitHub Pages) là hiển thị đúng.

## 1. Đẩy lên GitHub
```bash
cd linux-daily-repo
git init && git add . && git commit -m "Linux Daily: khởi tạo"
git branch -M main
git remote add origin git@github.com:<bạn>/<repo>.git
git push -u origin main
```

## 2. Tạo Routine dạng Cloud
1. Vào https://claude.ai/code/routines (hoặc app Desktop → Routines → New routine → **Cloud**).
2. **Kết nối repo** vừa push.
3. Dán nội dung `routine-prompt.txt` làm prompt.
4. Trigger: **Schedule → Daily**, chọn giờ (ví dụ 07:00, giờ địa phương của bạn).

> Vì sao Daily mà lại ra 2 ngày/bài? Lịch của Routines chỉ có hourly/daily/
> weekday/weekly, không có "2 ngày". Nên skill tự đặt **cổng nhịp 2 ngày** trong
> `SKILL.md` (Bước 0): mỗi ngày routine chạy, nhưng chỉ thực sự tạo bài nếu lần
> sinh gần nhất đã cách ≥ 2 ngày. Cổng này đọc `state.json` (`last_generated_at` —
> mốc THỰC do máy ghi, không phải ngày AI tự điền) qua `tools/cadence.py gate`, nên
> quyết định nhịp đáng tin hơn. Cách này giữ nhịp chuẩn và tự bù nếu lỡ một hôm.
> (Nếu giao diện cho nhập cron tùy chỉnh, có thể thử `0 7 */2 * *`, nhưng nó lệch ở
> ranh giới cuối tháng — nên cổng trong skill vẫn là cách chắc ăn.)

## 3. Sau mỗi lần chạy
- Bài mới nằm ở `posts/post-<số>-<slug>.html`, trên nhánh `claude/linux-daily-<ngày>`.
- Mở PR đó, **đọc lướt phần lệnh 30 giây**, rồi merge vào `main`.
- CI/deploy của site (Netlify/GitHub Pages/Hugo…) tự xuất bản khi `main` cập nhật.

## Ghi chú
- Routines chạy trên cloud của Anthropic, **laptop đóng vẫn chạy**. Đang là
  research preview nên giới hạn có thể đổi — xem https://code.claude.com/docs/en/routines.
- Trên Pro, hạn mức đếm **số lần chạy/ngày** (khoảng 5). Một routine chạy Daily
  chỉ tốn 1 lần/ngày; những ngày "bỏ qua" vẫn tính là một lần chạy nhẹ.
- Mặc định Claude chỉ push được lên nhánh tiền tố `claude/` — giữ `main` an toàn.
- Đổi nhịp: sửa số ngày trong Bước 0 của `SKILL.md` (2 → 3 để 3 ngày/bài, v.v.).
- Xoay trục theo **số bài** (tuần tự), không theo thứ, nên nhịp nào cũng không lệch.

## Xem nội dung bằng website (GitHub Pages)
Repo có sẵn trang chủ `index.html` (liệt kê bài, mới nhất lên đầu) và các bài trong
`posts/`. Bật GitHub Pages là có website miễn phí:

1. Push repo lên GitHub.
2. Repo → **Settings → Pages**.
3. **Source: Deploy from a branch** → chọn nhánh `main`, thư mục `/ (root)` → Save.
4. Chờ ~1 phút, URL hiện ở ngay mục Pages, dạng `https://<bạn>.github.io/<repo>/`.

Trang chủ ở `/`, mỗi bài ở `/posts/post-00N-....html`. File `.nojekyll` (đã có sẵn)
báo GitHub phục vụ HTML nguyên trạng, không qua Jekyll.

Trang chủ tự cập nhật: mỗi lần routine thêm bài, nó chạy `tools/build_index.py`
để dựng lại `index.html`. Trang chủ **không** bới HTML — nó đọc khối metadata có cấu
trúc `<script id="ld-meta">` trong mỗi bài (qua `tools/postmeta.py`) rồi render bằng
Jinja2 từ `templates/index.template.html`. Muốn dựng tay: `python3 tools/build_index.py`;
hoặc một lệnh gộp cả kiểm định: `python3 tools/build.py` (thêm `--check` để chỉ kiểm tra).
Cần Jinja2 (`pip install -e ".[dev]"` hoặc `pip install jinja2`).

⚠️ Lưu ý gói & quyền riêng tư:
- **Public repo** dùng Pages **miễn phí**. **Private repo** cần **GitHub Pro** (cá nhân)
  hoặc Team/Enterprise.
- Dù repo private, **trang xuất bản vẫn công khai** (ai cũng tải được HTML/asset),
  trừ khi dùng Enterprise Cloud có kiểm soát truy cập.
- Repo này **không chứa secret** (API key nằm trong môi trường Routine, không commit),
  nên đăng công khai an toàn — nhưng đừng bao giờ commit khóa/mật khẩu vào đây.

Muốn tên miền riêng hoặc chuyển sang Hugo/Jekyll sau này thì vẫn giữ nguyên
`posts/` được — chỉ đổi lớp trình bày.
Mỗi bài có sẵn ba file trong `posts/social/`:
- `post-<số>-facebook.txt` — caption. Dán vào FB, **đính kèm** `post-<số>-code.png`,
  thay `{{LINK}}` bằng URL bài trên website.
- `post-<số>-x.txt` — thread đánh số `[Tweet n]`. Đăng lần lượt; đính ảnh code vào
  tweet 1; thay `{{LINK}}`.
- `post-<số>-code.png` — ảnh lệnh (vì FB/X hiển thị monospace rất xấu).

Vì sao là ảnh? FB/X không có code block, dán lệnh thô sẽ vỡ khoảng trắng và dễ sai.
`tools/render_code.py` render lệnh thành ảnh nền tối khớp tông website.

Tự tạo/đổi ảnh code thủ công:
```bash
python3 tools/render_code.py --in snippet.txt \
  --out posts/social/post-004-code.png --title "Linux Daily #004 · ..."
```
Cần Pillow (`pip install pillow`); font JetBrains Mono đã nằm trong `tools/fonts/`.

## Muốn đổi thêm nữa?
Bảo Claude "đổi nhịp / thêm trục / chỉnh phong cách ảnh code" — skill sẽ được cập nhật.
