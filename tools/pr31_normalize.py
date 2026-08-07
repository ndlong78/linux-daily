#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"
SOCIAL = POSTS / "social"

DATES = {
    1: "2026-07-02",
    2: "2026-07-04",
    3: "2026-07-06",
    4: "2026-07-08",
    5: "2026-07-10",
    6: "2026-07-12",
    7: "2026-07-14",
    8: "2026-07-16",
    9: "2026-07-18",
    10: "2026-07-20",
    11: "2026-07-22",
    12: "2026-07-24",
    13: "2026-07-26",
    14: "2026-07-28",
    15: "2026-07-30",
    16: "2026-08-01",
    17: "2026-08-03",
    18: "2026-08-05",
}


def normalize_historical_dates() -> None:
    for issue, date_s in DATES.items():
        matches = list(POSTS.glob(f"post-{issue:03d}-*.html"))
        if len(matches) != 1:
            raise SystemExit(f"expected exactly one post for #{issue:03d}, got {matches}")
        path = matches[0]
        text = path.read_text(encoding="utf-8")
        text, n_meta = re.subn(
            r'("date"\s*:\s*")\d{4}-\d{2}-\d{2}("\s*,?)',
            rf"\g<1>{date_s}\g<2>",
            text,
            count=1,
        )
        d = dt.date.fromisoformat(date_s)
        visible = f"#{issue:03d} · {d.day:02d}·{d.month:02d}·{d.year}"
        text, n_vis = re.subn(
            rf'<span class="issue">#{issue:03d} · \d{{2}}·\d{{2}}·\d{{4}}</span>',
            f'<span class="issue">{visible}</span>',
            text,
            count=1,
        )
        if n_meta != 1 or n_vis != 1:
            raise SystemExit(
                f"#{issue:03d}: date replacement failed (meta={n_meta}, visible={n_vis}) in {path}"
            )
        path.write_text(text, encoding="utf-8")


def normalize_topics() -> None:
    path = ROOT / "topics.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    seen: set[int] = set()
    rx = re.compile(r"^#(\d{3})\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*(.+)$")
    for line in lines:
        m = rx.match(line)
        if not m:
            out.append(line)
            continue
        issue = int(m.group(1))
        if issue <= 18:
            out.append(f"#{issue:03d} | {DATES[issue]} | {m.group(3).strip()} | {m.group(4).strip()}")
            seen.add(issue)
        elif issue == 19:
            continue
        else:
            out.append(line)
    if seen != set(DATES):
        raise SystemExit(f"topics.md missing historical issues: {sorted(set(DATES) - seen)}")
    out.append(
        "#019 | 2026-08-07 | Monitoring | Triage hiệu năng trong 5 phút: CPU, RAM và disk I/O bằng vmstat + iostat trên Ubuntu/Debian/Fedora/FreeBSD"
    )
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


POST_019 = r'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Triage hiệu năng với vmstat + iostat — Linux Daily #019</title>
<meta name="description" content="Workflow 5 phút để phân biệt CPU-bound, memory pressure và disk I/O trên Ubuntu, Debian, Fedora và FreeBSD bằng uptime, vmstat, iostat và systat.">
<link rel="stylesheet" href="../assets/style.css">
<script type="application/json" id="ld-meta">
{
  "issue": 19,
  "date": "2026-08-07",
  "axis": "Monitoring",
  "eyebrow": "Monitoring · Hiệu năng",
  "slug": "triage-hieu-nang-vmstat-iostat",
  "title": "Server chậm ở đâu? Triage CPU, RAM và disk I/O trong 5 phút",
  "lede": "Máy chủ 'chậm' không phải là một chẩn đoán. Trong vài phút đầu, mục tiêu là phân loại đúng nút thắt: CPU đang xếp hàng, RAM đang chịu áp lực, hay thiết bị lưu trữ đang có độ trễ cao. vmstat cho bức tranh hệ thống; iostat đi sâu vào I/O; FreeBSD có cùng tư duy nhưng bộ lệnh và trường số liệu khác Linux.",
  "review_status": "reviewed",
  "sources": [
    {"title": "procps-ng vmstat(8) — Linux manual page", "url": "https://man7.org/linux/man-pages/man8/vmstat.8@@procps-ng.html", "kind": "upstream"},
    {"title": "sysstat — Performance monitoring tools for Linux", "url": "https://github.com/sysstat/sysstat", "kind": "upstream"},
    {"title": "FreeBSD vmstat(8)", "url": "https://man.freebsd.org/cgi/man.cgi?query=vmstat&sektion=8", "kind": "official"},
    {"title": "FreeBSD iostat(8)", "url": "https://man.freebsd.org/cgi/man.cgi?query=iostat&sektion=8", "kind": "official"}
  ]
}
</script>
</head>
<body class="post">
<div class="wrap">
  <div class="masthead"><div class="brand"><a class="brand-home" href="../index.html">← Linux Daily</a><span class="issue">#019 · 07·08·2026</span></div></div>
  <header class="post">
    <p class="eyebrow">Monitoring · Hiệu năng</p>
    <h1>Server chậm ở đâu? Triage CPU, RAM và disk I/O trong 5 phút</h1>
    <p class="lede">Máy chủ 'chậm' không phải là một chẩn đoán. Trong vài phút đầu, mục tiêu là phân loại đúng nút thắt: CPU đang xếp hàng, RAM đang chịu áp lực, hay thiết bị lưu trữ đang có độ trễ cao. vmstat cho bức tranh hệ thống; iostat đi sâu vào I/O; FreeBSD có cùng tư duy nhưng bộ lệnh và trường số liệu khác Linux.</p>
    <div class="meta"><span class="tag axis">TRỤC · MONITORING</span><span class="tag">ĐỘ KHÓ · TRUNG CẤP</span><span class="tag">~10 PHÚT</span></div>
  </header>

  <figure>
    <svg viewBox="0 0 760 250" role="img" aria-label="Luồng triage hiệu năng: kiểm tải tổng thể, đo CPU và memory bằng vmstat, sau đó kiểm disk I/O bằng iostat trước khi kết luận nút thắt">
      <rect width="760" height="250" fill="#F7FAF9"/>
      <g font-family="Be Vietnam Pro, sans-serif" text-anchor="middle">
        <rect x="35" y="80" width="180" height="90" rx="8" fill="#FFFFFF" stroke="#14201D" stroke-width="2"/><text x="125" y="112" font-size="14" font-weight="700">1 · TẢI TỔNG THỂ</text><text x="125" y="140" font-family="JetBrains Mono" font-size="12">uptime</text>
        <rect x="290" y="80" width="180" height="90" rx="8" fill="#F4F8F6" stroke="#0C6E61" stroke-width="2"/><text x="380" y="112" font-size="14" font-weight="700">2 · CPU / RAM</text><text x="380" y="140" font-family="JetBrains Mono" font-size="12">vmstat 1 5</text>
        <rect x="545" y="80" width="180" height="90" rx="8" fill="#FBF1F0" stroke="#B23A2E" stroke-width="2"/><text x="635" y="112" font-size="14" font-weight="700">3 · DISK I/O</text><text x="635" y="140" font-family="JetBrains Mono" font-size="12">iostat -xz 1 5</text>
        <path d="M215 125H282" stroke="#0C6E61" stroke-width="3"/><path d="M470 125H537" stroke="#0C6E61" stroke-width="3"/>
      </g>
    </svg>
    <figcaption>Hình 1 — Triage theo lớp: nhìn tải trước, kiểm CPU/RAM bằng <code>vmstat</code>, rồi mới đi xuống từng thiết bị với <code>iostat</code>.</figcaption>
  </figure>

  <section>
    <h2><span class="num">01</span> Bối cảnh thực tế</h2>
    <p>Một ticket “server chậm” thường đến mà không có chỉ số. Sai lầm phổ biến là mở <code>top</code>, thấy một con số cao rồi kết luận ngay. Triage tốt phải lấy nhiều mẫu theo thời gian và trả lời ba câu: có hàng đợi CPU không, có paging/swap bất thường không, và thiết bị lưu trữ có độ trễ/hàng đợi tăng không.</p>
  </section>

  <section>
    <h2><span class="num">02</span> Kiến thức cốt lõi</h2>
    <ul class="clean">
      <li><strong><code>vmstat</code>:</strong> báo process/run queue, memory, paging, block I/O và CPU. Trên Linux, mẫu đầu tiên thường là trung bình kể từ lúc boot; các mẫu sau mới phản ánh khoảng lấy mẫu — vì vậy đừng kết luận từ dòng đầu.</li>
      <li><strong>CPU:</strong> nhìn <code>r</code> cùng <code>us/sy/id</code>. Run queue cao kéo dài so với số CPU khả dụng là tín hiệu cần điều tra thêm, không phải tự động đồng nghĩa “thiếu CPU”.</li>
      <li><strong>Memory pressure:</strong> ưu tiên xu hướng paging/swap (<code>si/so</code> trên Linux) hơn việc chỉ nhìn “free RAM thấp”; cache dùng RAM là bình thường.</li>
      <li><strong>Disk I/O:</strong> <code>iostat -x</code> cho extended statistics trên Linux. Đọc latency/queue/throughput cùng nhau; một cột <code>%util</code> đơn lẻ không đủ để kết luận mọi loại SSD/NVMe đã bão hòa.</li>
      <li><strong>iowait:</strong> là tín hiệu CPU chờ trong khi có I/O outstanding, không phải phép đo trực tiếp “đĩa chậm”. Luôn đối chiếu với số liệu thiết bị.</li>
    </ul>
  </section>

  <figure>
    <svg viewBox="0 0 760 270" role="img" aria-label="Bảng lệnh song song: Ubuntu Xubuntu và Debian dùng apt cài sysstat, Fedora dùng dnf; FreeBSD dùng vmstat iostat systat trong base và không dùng systemd">
      <rect width="760" height="270" fill="#FFFFFF"/>
      <g font-family="JetBrains Mono" font-size="10.5" text-anchor="middle">
        <rect x="20" y="35" width="170" height="190" rx="7" fill="#F4F8F6" stroke="#0C6E61"/><text x="105" y="62" font-family="Be Vietnam Pro" font-size="13" font-weight="700">Ubuntu / Xubuntu</text><text x="105" y="102">apt install sysstat</text><text x="105" y="132">vmstat 1 5</text><text x="105" y="162">iostat -xz 1 5</text>
        <rect x="205" y="35" width="170" height="190" rx="7" fill="#F4F8F6" stroke="#0C6E61"/><text x="290" y="62" font-family="Be Vietnam Pro" font-size="13" font-weight="700">Debian</text><text x="290" y="102">apt install sysstat</text><text x="290" y="132">vmstat 1 5</text><text x="290" y="162">iostat -xz 1 5</text>
        <rect x="390" y="35" width="170" height="190" rx="7" fill="#F4F8F6" stroke="#0C6E61"/><text x="475" y="62" font-family="Be Vietnam Pro" font-size="13" font-weight="700">Fedora</text><text x="475" y="102">dnf install sysstat</text><text x="475" y="132">vmstat 1 5</text><text x="475" y="162">iostat -xz 1 5</text>
        <rect x="575" y="35" width="165" height="190" rx="7" fill="#FBF1F0" stroke="#B23A2E"/><text x="657" y="62" font-family="Be Vietnam Pro" font-size="13" font-weight="700">FreeBSD</text><text x="657" y="102">vmstat -w 1 -c 5</text><text x="657" y="132">iostat -x -w 1 -c 5</text><text x="657" y="162">systat -vmstat 1</text>
      </g>
    </svg>
    <figcaption>Hình 2 — Linux cần gói <code>sysstat</code> để có <code>iostat</code>; FreeBSD dùng bộ công cụ BSD riêng trong base, không áp lệnh systemd/Linux sang.</figcaption>
  </figure>

  <section>
    <h2><span class="num">03</span> Thao tác từng HĐH</h2>
    <span class="code-label"><span class="dot"></span>Ubuntu / Xubuntu và Debian — APT</span>
    <pre><code>sudo apt update
sudo apt install -y sysstat
uptime
vmstat 1 5
iostat -xz 1 5</code></pre>

    <span class="code-label"><span class="dot"></span>Fedora — DNF</span>
    <pre><code>sudo dnf install -y sysstat
uptime
vmstat 1 5
iostat -xz 1 5</code></pre>

    <span class="code-label bsd"><span class="dot"></span>FreeBSD — công cụ base, không systemd</span>
    <pre class="bsd"><code>uptime
vmstat -w 1 -c 5
iostat -x -w 1 -c 5
systat -vmstat 1</code></pre>
    <p>Trên Linux, cài <code>sysstat</code> để lấy <code>iostat</code>; <code>vmstat</code> thuộc procps/procps-ng và thường đã có. Trên FreeBSD, cú pháp và cột khác Linux: đọc man page của chính hệ trước khi so ngưỡng.</p>
  </section>

  <section>
    <h2><span class="num">04</span> Kiểm chứng — workflow 5 phút</h2>
    <pre><code># 1. Xác nhận tải và thời gian máy đã chạy
uptime

# 2. Lấy nhiều mẫu; bỏ qua việc suy diễn từ mẫu đầu tiên
vmstat 1 5

# 3. Linux: xem từng block device trong 5 giây
iostat -xz 1 5

# 4. Ghi lại timestamp + workload đang xảy ra trước khi kết luận
date</code></pre>
    <p>Kết luận chỉ khi nhiều tín hiệu cùng hướng: ví dụ run queue tăng kéo dài + CPU gần hết idle; hoặc paging/swap tăng liên tục; hoặc application latency tăng đồng thời với device latency/queue. Nếu số liệu bình thường, mở rộng sang network, lock, database hoặc ứng dụng thay vì ép nguyên nhân vào CPU/RAM/disk.</p>
  </section>

  <section>
    <h2><span class="num">05</span> Cạm bẫy thường gặp</h2>
    <ul class="clean">
      <li><strong>Đọc dòng đầu của <code>vmstat</code>/<code>iostat</code> như “1 giây vừa rồi”:</strong> nhiều công cụ báo mẫu đầu trung bình từ boot; tập trung vào các mẫu sau.</li>
      <li><strong>Thấy RAM free thấp rồi kết luận thiếu RAM:</strong> Linux và FreeBSD dùng RAM cho cache; tìm paging/swap và áp lực thực tế.</li>
      <li><strong><code>wa</code> cao = chắc chắn disk hỏng:</strong> không đúng. Xem thiết bị cụ thể, latency, queue và workload.</li>
      <li><strong>So ngưỡng giữa HDD, SSD, NVMe như nhau:</strong> khả năng song song và latency nền khác nhau; lấy baseline của chính hệ thống.</li>
      <li><strong>Dùng lệnh Linux trên FreeBSD:</strong> FreeBSD có <code>vmstat/iostat/systat</code> riêng; tên cột và option không đồng nhất hoàn toàn.</li>
    </ul>
  </section>

  <section>
    <h2><span class="num">06</span> Bảo mật &amp; vận hành</h2>
    <ul class="clean">
      <li>Các lệnh quan sát trong bài chủ yếu là read-only; không chạy stress/load generator trên production chỉ để “thử xem biểu đồ có nhúc nhích”.</li>
      <li>Ghi timestamp, hostname, workload và khoảng lấy mẫu khi lưu evidence; một ảnh chụp không có bối cảnh rất dễ bị diễn giải sai.</li>
      <li>Nếu thu thập output gửi ra ngoài đội vận hành, rà hostname, device name và thông tin môi trường trước khi chia sẻ.</li>
      <li>Ưu tiên baseline bình thường của chính máy/dịch vụ thay vì áp một ngưỡng Internet cho mọi server.</li>
    </ul>
  </section>

  <div class="exercise">
    <h2><span class="num">07</span> Bài tập tự luyện</h2>
    <p>Trên một VM Linux và một VM FreeBSD đang có workload bình thường, lấy 5 mẫu <code>vmstat</code> và <code>iostat</code> cách nhau 1 giây. Ghi lại ba nhận xét: CPU có hàng đợi kéo dài không, có paging/swap đáng chú ý không, và thiết bị nào có I/O nổi bật. Không tạo tải nhân tạo; mục tiêu là luyện đọc baseline trước khi gặp incident.</p>
  </div>

  <section class="sources" aria-labelledby="technical-sources"><h2 id="technical-sources">Nguồn kỹ thuật</h2><ul class="clean">
    <li><a href="https://man7.org/linux/man-pages/man8/vmstat.8@@procps-ng.html">procps-ng vmstat(8) — Linux manual page</a></li>
    <li><a href="https://github.com/sysstat/sysstat">sysstat — Performance monitoring tools for Linux</a></li>
    <li><a href="https://man.freebsd.org/cgi/man.cgi?query=vmstat&amp;sektion=8">FreeBSD vmstat(8)</a></li>
    <li><a href="https://man.freebsd.org/cgi/man.cgi?query=iostat&amp;sektion=8">FreeBSD iostat(8)</a></li>
  </ul></section>
  <footer><a class="foot-home" href="../index.html">← Về trang chủ Linux Daily</a></footer>
</div>
</body>
</html>
'''

FB_019 = '''📊 “Server chậm” chưa phải là chẩn đoán. Trước khi chỉnh sysctl, tăng CPU hay đổ lỗi cho storage, hãy dành 5 phút để phân loại đúng nút thắt.

Linux Daily #019 đi theo workflow thực chiến:
• uptime → nhìn load và thời gian máy đã chạy.
• vmstat → xem run queue, CPU, paging/swap và block I/O theo nhiều mẫu.
• iostat -xz → đi xuống từng block device, đối chiếu latency, queue và throughput.

Ubuntu/Xubuntu và Debian cài iostat qua gói sysstat bằng APT; Fedora dùng DNF. FreeBSD tách riêng: vmstat, iostat và systat là bộ công cụ BSD, cú pháp/cột không được giả định giống Linux.

Điểm quan trọng nhất: đừng kết luận từ một con số. RAM free thấp không tự động nghĩa thiếu RAM; iowait cao không tự động nghĩa disk hỏng; %util cao cũng cần đặt trong ngữ cảnh loại thiết bị và workload. Lấy nhiều mẫu, ghi timestamp, so với baseline rồi mới đi sâu.

👉 Đọc đầy đủ: {{LINK}}

#LinuxDaily #SysAdmin #Performance #Monitoring #FreeBSD

[Đính kèm ảnh: post-019-code.png]
'''

X_019 = '''[Tweet 1] — đính kèm post-019-code.png
📊 “Server chậm” chưa phải chẩn đoán. Triage tốt cần phân loại: CPU đang xếp hàng, RAM chịu áp lực, hay disk I/O có độ trễ? Workflow 5 phút với vmstat + iostat. Thread 🧵

[Tweet 2]
Bắt đầu bằng nhiều mẫu, không bằng cảm giác:
uptime
vmstat 1 5
Trên Linux, mẫu đầu vmstat thường là trung bình từ boot; chú ý các mẫu sau theo interval.

[Tweet 3]
CPU: xem run queue r cùng us/sy/id.
Memory: đừng chỉ nhìn “free RAM thấp”; xem paging/swap và xu hướng. Cache dùng RAM là bình thường.

[Tweet 4]
Linux disk I/O:
iostat -xz 1 5
Đọc latency + queue + throughput cùng nhau. iowait hay %util đơn lẻ không đủ để kết luận mọi HDD/SSD/NVMe “đã nghẽn”.

[Tweet 5] — distro
Ubuntu/Xubuntu + Debian:
apt install sysstat
Fedora:
dnf install sysstat
vmstat thường thuộc procps/procps-ng; iostat thuộc sysstat.

[Tweet 6] — FreeBSD
FreeBSD không dùng systemd/sysstat kiểu Linux:
vmstat -w 1 -c 5
iostat -x -w 1 -c 5
systat -vmstat 1
Cùng tư duy triage, nhưng option/cột là BSD riêng.

[Tweet 7]
Nguyên tắc: lấy nhiều mẫu + timestamp + workload + baseline trước khi kết luận. Full bài và workflow copy-paste: {{LINK}}
#LinuxDaily #Performance #Monitoring #FreeBSD
'''

SNIPPET_019 = '''# Linux: Ubuntu / Debian / Fedora
uptime
vmstat 1 5
iostat -xz 1 5

# FreeBSD
uptime
vmstat -w 1 -c 5
iostat -x -w 1 -c 5
systat -vmstat 1
'''


def create_issue_019() -> None:
    (POSTS / "post-019-triage-hieu-nang-vmstat-iostat.html").write_text(POST_019, encoding="utf-8")
    (SOCIAL / "post-019-facebook.txt").write_text(FB_019, encoding="utf-8")
    (SOCIAL / "post-019-x.txt").write_text(X_019, encoding="utf-8")
    (ROOT / ".pr31-post-019-snippet.txt").write_text(SNIPPET_019, encoding="utf-8")


def update_state() -> None:
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    state = {
        "last_issue": 19,
        "last_published_date": "2026-08-07",
        "last_generated_at": now,
    }
    (ROOT / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    normalize_historical_dates()
    normalize_topics()
    create_issue_019()
    update_state()
    print("PR31 normalization prepared")


if __name__ == "__main__":
    main()
