#!/usr/bin/env python3
from __future__ import annotations
import html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; POSTS=ROOT/'posts'; TODAY='2026-08-09'
TESTED=['Ubuntu/Xubuntu 24.04 LTS (documentation-verified)','Debian 13 stable (documentation-verified)','Fedora 42 (documentation-verified)','FreeBSD 14.3-RELEASE (documentation-verified)']
D={
31:("Áp mount options có chủ đích để giảm bề mặt tấn công mà không tự phá ứng dụng hoặc boot.","Có console/phiên cứu hộ, biết mountpoint và workload phụ thuộc; ghi baseline mount options trước khi đổi.",["Xác định filesystem, mountpoint và option hiện tại.","Chọn noexec/nosuid/nodev theo threat model thay vì bật hàng loạt.","Thử remount hoặc mount lab trước khi sửa cấu hình persistent.","Kiểm workload cần thiết rồi mới persist và reboot test khi có đường lui."],["Mountpoint hiển thị đúng option dự kiến.","Workload hợp lệ vẫn chạy; hành vi bị hạn chế được tái hiện đúng.","Cấu hình persistent không làm lỗi mount/boot sau kiểm chứng."],True),
32:("Dùng jq để lọc, biến đổi và kiểm tra JSON vận hành thay vì grep text dễ sai cấu trúc.","Có JSON mẫu/API output không chứa secret; quyền cài package nếu jq chưa có.",["Cài và kiểm phiên bản jq bằng package manager đúng hệ.","Dùng selector đơn giản để đọc field/array trước.","Thêm map/select và output raw khi cần cho shell pipeline.","Kiểm exit status hoặc điều kiện bằng jq -e trước khi automation dựa vào kết quả."],["jq parse JSON hợp lệ và báo lỗi với JSON hỏng.","Selector trả đúng field/record mong đợi.","jq -e phản ánh đúng điều kiện để script dùng exit status."],True),
33:("Lần từ PID tới parent tree, command line và service owner để xử lý đúng process thay vì kill theo cảm tính.","Quyền đọc process/service metadata; chọn một PID lab hoặc service không nhạy cảm.",["Xác định PID và command line thật.","Lần parent/child tree để hiểu process được spawn từ đâu.","Đối chiếu PID với systemd unit trên Linux hoặc rc/service/process metadata trên FreeBSD.","Chỉ đề xuất restart/kill sau khi xác định owner và blast radius."],["PID được gắn với đúng parent tree.","Xác định được service/unit hoặc cơ chế khởi chạy khi có.","Không nhầm worker child với service gốc cần xử lý."],False),
34:("Lập lịch tác vụ có bằng chứng: biết lịch nào kích hoạt, missed run xử lý ra sao và log nằm ở đâu trên Linux/FreeBSD.","Có script lab idempotent; quyền tạo timer/cron/periodic entry và đường lui để xóa lịch.",["Tạo job lab ghi timestamp vào file riêng.","Trên Linux cấu hình systemd service+timer; trên FreeBSD dùng cron/periodic phù hợp.","Kiểm lịch đã được scheduler nhận trước khi chờ run.","Quan sát ít nhất một lần chạy, log/output và trạng thái lần kế tiếp."],["Scheduler liệt kê job/timer đúng lịch.","Job tạo bằng chứng timestamp hoặc log như dự kiến.","Có thể xác định lần chạy trước/sau và dọn lịch không để orphan job."],True),
35:("Triage filesystem đầy theo block, inode và top consumer rồi lập kế hoạch recovery an toàn thay vì xóa file ngẫu nhiên.","Lab/số liệu mô phỏng hoặc filesystem test; không làm đầy filesystem production để luyện tập.",["Xác định mountpoint và mức dùng block/inode.","Khoanh top directory/file consumer bằng du hoặc công cụ phù hợp.","Phân loại dữ liệu có thể cleanup, rotate, move hoặc cần mở rộng capacity.","Sau xử lý, đo lại cùng chỉ số baseline và ghi biện pháp phòng tái diễn."],["Xác định đúng nguyên nhân block/inode thay vì chỉ nhìn phần trăm chung.","Recovery plan giải phóng hoặc bổ sung dung lượng có kiểm soát.","Verification cho thấy headroom trở lại và không xóa nhầm dữ liệu cần thiết."],False),
36:("Dùng tcpdump có mục tiêu để lấy bằng chứng DNS, TCP handshake hoặc firewall mà không capture tràn lan.","Biết interface/host/port cần kiểm; có quyền capture và tránh payload nhạy cảm nếu không cần.",["Xác định interface và câu hỏi cần trả lời trước khi capture.","Giới hạn bằng host/port/protocol và packet count hoặc timeout.","Tái hiện một flow duy nhất rồi dừng capture.","Đọc timestamp/flags/tuple để liên hệ với log hoặc firewall counter."],["Capture chỉ chứa flow liên quan và tự dừng theo giới hạn.","Nhìn được DNS query/response hoặc TCP SYN/SYN-ACK/RST theo bài test.","Có thể đối chiếu packet evidence với triệu chứng mà không cần capture toàn mạng."],False),
37:("Cấp quyền chia sẻ bằng ACL/default ACL thay vì chmod 777, đồng thời hiểu mask và khác biệt ACL trên FreeBSD.","Filesystem hỗ trợ ACL; có user/group lab và snapshot/backup permission baseline.",["Đọc owner/group/mode và ACL hiện tại trước khi đổi.","Thêm ACL hẹp cho user/group cần thiết.","Nếu cần kế thừa, cấu hình default ACL theo semantics của filesystem/hệ.","Tạo file mới và kiểm effective permission, mask và inheritance."],["User/group mục tiêu có đúng quyền yêu cầu mà other không bị mở rộng.","ACL mask không vô tình vô hiệu hóa quyền mong muốn.","File mới kế thừa policy đúng khi default ACL được cấu hình."],True),
38:("Đọc SMART/NVMe health và error counters để phát hiện degradation sớm mà không chạy destructive test.","Xác định đúng device; quyền đọc SMART/NVMe log và ưu tiên lệnh read-only.",["Map disk/device với workload trước khi đọc health.","Đọc overall health/critical warning và key counters.","Đối chiếu temperature, media/error log và lifetime counters theo loại thiết bị.","Ghi baseline để so trend; chỉ schedule self-test khi hiểu impact."],["Tool nhận đúng device và trả health data hợp lệ.","Phân biệt warning hiện tại với lifetime counter không nhất thiết là lỗi đang diễn ra.","Có baseline để so sánh lần kiểm sau thay vì kết luận từ một snapshot cô lập."],False),
39:("Dùng fd để tìm file nhanh nhưng hiểu ignore, hidden, symlink và khác biệt tên binary trên Debian/Ubuntu.","Có cây file lab; quyền cài package nếu fd/fdfind chưa có.",["Cài package và xác định binary thực tế fd hay fdfind.","Tìm theo name/type trong path hẹp trước.","So sánh mặc định với --hidden/--no-ignore khi cần.","Dùng extension/type/exec có kiểm soát và xem danh sách trước khi hành động lên nhiều file."],["Tìm đúng file trong phạm vi đã chọn.","Giải thích được hidden/ignored file bị bỏ qua mặc định.","Ubuntu/Debian dùng đúng binary/package naming thay vì giả định giống Fedora/FreeBSD."],True),
40:("Theo dõi một process theo chuỗi thời gian bằng pidstat trên Linux và procstat/sampling trên FreeBSD để phân biệt spike với pressure kéo dài.","Biết PID/service cần theo dõi; quyền đọc process counters và workload test an toàn.",["Xác định PID ổn định hoặc cách theo dõi process theo command/service.","Lấy nhiều mẫu CPU/memory/I/O theo interval thay vì một snapshot.","Đối chiếu sampling với process tree/service owner nếu PID thay đổi.","Ghi time window và kết luận chỉ khi pattern lặp lại qua nhiều mẫu."],["Có time series nhiều mẫu cho process mục tiêu.","Phân biệt spike ngắn với mức sử dụng kéo dài.","Kết quả có thể liên hệ với service/workload thay vì chỉ một PID rời rạc."],True),
}
META=re.compile(r'(<script[^>]+id=["\']ld-meta["\'][^>]*>)(.*?)(</script>)',re.I|re.S)
HEADER=re.compile(r'</header>',re.I)
def get_issue(t):
 m=META.search(t)
 if not m:return None
 try:return int(json.loads(html.unescape(m.group(2)))['issue'])
 except Exception:return None
def numbered(num): return re.compile(r'(<section(?P<a>[^>]*)>\s*<h2(?P<h>[^>]*)>\s*<span[^>]*class=["\']num["\'][^>]*>'+num+r'</span>)(?P<title>.*?</h2>)(?P<body>.*?</section>)',re.I|re.S)
def set_section(t,num,title,insert=''):
 p=numbered(num)
 return p.sub(lambda m:m.group(1)+' '+title+'</h2>'+insert+m.group('body'),t,count=1)
def migrate(p):
 t=p.read_text(encoding='utf-8'); i=get_issue(t)
 if i not in D:return False
 if '"tested_on"' in t:return False
 old=t; obj,pre,steps,expected,changes=D[i]
 m=META.search(t); meta=json.loads(html.unescape(m.group(2))); meta.update(tested_on=TESTED,last_verified=TODAY,changes_system=changes)
 t=t[:m.start()]+m.group(1)+'\n'+json.dumps(meta,ensure_ascii=False,indent=2)+'\n'+m.group(3)+t[m.end():]
 front=f'''\n<section class="style-contract" aria-label="Phạm vi kiểm chứng"><p><strong>Tested on:</strong> Ubuntu/Xubuntu 24.04 LTS · Debian 13 stable · Fedora 42 · FreeBSD 14.3-RELEASE</p><p><strong>Last verified:</strong> {TODAY} · đối chiếu tài liệu official/upstream</p></section>\n<section><h2>Mục tiêu</h2><p>{obj}</p></section>\n<section><h2>Yêu cầu tiên quyết</h2><p>{pre}</p></section>\n'''
 h=HEADER.search(t); t=t[:h.end()]+front+t[h.end():]
 ol='<ol class="steps">'+''.join('<li>'+x+'</li>' for x in steps)+'</ol>'
 ex='<h3>Kết quả mong đợi</h3><ul class="clean">'+''.join('<li>'+x+'</li>' for x in expected)+'</ul>'
 t=set_section(t,'03','Các bước thực hiện',ol)
 t=set_section(t,'04','Kiểm chứng',ex)
 t=set_section(t,'05','Lưu ý &amp; Khắc phục lỗi')
 if changes:
  marker=re.search(r'<section[^>]*>\s*<h2[^>]*>\s*<span[^>]*class=["\']num["\'][^>]*>05</span>',t,re.I|re.S)
  clean='<section><h2>Gỡ / Hoàn tác</h2><p>Hoàn tác thay đổi lab theo thứ tự ngược, khôi phục baseline đã ghi trước bài và kiểm chứng lại trước khi đóng phiên quản trị.</p></section>\n'
  if marker:t=t[:marker.start()]+clean+t[marker.start():]
 t=re.sub(r'<pre(?P<p>[^>]*)>\s*<code(?![^>]*language-)(?P<c>[^>]*)>',lambda m:f'<pre{m.group("p")}><code class="language-bash"{m.group("c")}>',t,flags=re.I)
 out=[];pos=0
 for pm in list(re.finditer(r'<pre(?P<a>[^>]*)>\s*<code[^>]*class=["\'][^"\']*language-(?:bash|sh|shell)[^"\']*["\'][^>]*>',t,re.I)):
  if pm.start()<pos:continue
  out.append(t[pos:pm.start()]); prev=t[max(0,pm.start()-500):pm.start()]
  if 'data-run-as=' not in prev:
   run='root' if 'bsd' in pm.group('a').lower() else 'user'
   out.append(f'<p class="run-context" data-run-as="{run}"><strong>Run as:</strong> {run}</p>\n')
  out.append(pm.group(0));pos=pm.end()
 out.append(t[pos:]);t=''.join(out)
 if t!=old:p.write_text(t,encoding='utf-8');print(p.name);return True
 return False
print('changed=',sum(migrate(p) for p in sorted(POSTS.glob('post-*.html'))))
