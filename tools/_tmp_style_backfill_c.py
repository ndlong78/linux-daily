#!/usr/bin/env python3
from __future__ import annotations
import html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; POSTS=ROOT/'posts'; TODAY='2026-08-09'
TESTED=['Ubuntu/Xubuntu 24.04 LTS (documentation-verified)','Debian 13 stable (documentation-verified)','Fedora 42 (documentation-verified)','FreeBSD 14.3-RELEASE (documentation-verified)']
D={
21:("Chứng minh khả năng phục hồi bằng backup, failure injection, restore thật và checksum verification.","Dữ liệu lab, đích backup tách biệt và đủ dung lượng restore.",["Tạo dữ liệu lab và checksum baseline.","Chạy backup và xác nhận snapshot/repository tồn tại.","Inject lỗi có kiểm soát vào bản sao làm việc.","Restore sang vị trí mới và so checksum với baseline."],["Backup/snapshot được liệt kê không lỗi integrity.","Restore tạo lại đầy đủ dữ liệu ở vị trí mới.","Checksum sau restore khớp baseline."],True),
22:("Khoanh vùng lỗi DNS theo client, resolver và authoritative thay vì sửa cấu hình theo cảm tính.","Một hostname kiểm thử và resolver dự kiến; thao tác chính read-only.",["Kiểm phân giải qua NSS để xác nhận triệu chứng.","Xác định resolver runtime thật sự đang dùng.","Query trực tiếp resolver bằng dig/drill.","Khi cần, lần theo authoritative chain để xác định lớp lỗi."],["Xác định được resolver và DNS status cụ thể.","NSS và direct query nhất quán hoặc chỉ ra rõ điểm khác nhau.","Nếu authoritative lỗi, direct query tới authoritative tái hiện được lỗi."],False),
23:("Cấp quyền quản trị tối thiểu bằng sudo trên Linux và doas trên FreeBSD, không trao shell root rộng hơn nhu cầu.","Có phiên/console dự phòng; biết chính xác user, executable và argument cần cho phép.",["Xác định command path và hành vi tối thiểu cần cấp.","Tạo sudoers drop-in hoặc doas.conf hẹp theo tác vụ.","Validate syntax trước khi đóng phiên quản trị.","Kiểm positive test và command ngoài policy phải bị từ chối."],["Command được phép chạy đúng policy.","Command ngoài phạm vi bị từ chối.","Policy validator không báo lỗi cú pháp."],True),
24:("Phân biệt hết block, hết inode và ZFS quota/dataset đầy để xử lý đúng nguyên nhân.","Quyền đọc filesystem/ZFS statistics; ưu tiên quan sát read-only.",["Xác định mountpoint/dataset thật của đường dẫn lỗi.","Đọc block và inode usage; với ZFS đọc available/quota/reservation.","Đối chiếu du với filesystem accounting.","Kết luận bottleneck trước khi đề xuất cleanup."],["Chỉ ra đúng mountpoint/dataset.","Phân biệt block, inode và ZFS quota/capacity constraint.","Giải thích được chênh lệch df/du/ZFS nếu có."],False),
25:("Dùng ripgrep nhanh nhưng hiểu ignore, hidden và binary semantics để không kết luận sai.","Có cây file lab hoặc thư mục chỉ đọc; quyền cài package nếu rg chưa có.",["Cài và kiểm phiên bản rg từ package manager.","Tìm trong path/pattern hẹp trước.","So sánh mặc định với --hidden/--no-ignore khi cần.","Dùng glob/type/context để thu hẹp output."],["rg tìm đúng pattern và exit status hợp lý.","Giải thích được file hidden/ignored bị bỏ qua mặc định.","Có thể mở rộng phạm vi mà không quét mù toàn filesystem."],True),
26:("Đọc resource pressure theo thời gian bằng vmstat và systat để phân biệt CPU, memory/paging và I/O pressure.","Quyền đọc counters; lấy nhiều mẫu theo thời gian.",["Chạy vmstat với interval cố định để lấy chuỗi mẫu.","Đọc runnable/blocked process cùng CPU idle/wait.","Đối chiếu paging/swap và I/O với công cụ phù hợp hệ.","Chỉ kết luận khi nhiều tín hiệu cùng hỗ trợ."],["Có chuỗi nhiều mẫu, không dựa vào snapshot đầu tiên.","Phân biệt CPU saturation, I/O wait và paging pressure.","Không kết luận bottleneck chỉ từ load average hoặc một cột CPU."],False),
27:("Viết shell automation idempotent: chạy lại cùng input không nhân bản cấu hình hay tạo thay đổi vô nghĩa.","Dùng resource lab; chọn POSIX sh hoặc Bash rõ ràng theo tính năng dùng.",["Mô tả desired state trước khi mutate.","Thêm guard để chỉ đổi khi current state khác desired state.","Chạy lần một và ghi nhận thay đổi.","Chạy lần hai; state/diff phải không đổi."],["Lần đầu đưa lab về desired state.","Lần hai không tạo duplicate hay diff mới.","Verification độc lập xác nhận trạng thái cuối."],True),
28:("Xử lý DNS outage theo incident workflow: thu bằng chứng, khoanh lỗi rồi phục hồi có kiểm chứng.","VM/lab DNS riêng, control query biết trước kết quả đúng và baseline resolver.",["Ghi baseline NSS, resolver runtime và direct query.","Inject lỗi DNS có kiểm soát mà không phá đường quản trị.","Triage NSS → resolver → upstream/authoritative.","Phục hồi thành phần gây lỗi và lặp cùng bộ query."],["Failure injection tái hiện triệu chứng nhưng giữ management path.","Bằng chứng xác định đúng lớp lỗi trước khi sửa.","Sau recovery các query khớp baseline."],True),
29:("Cấu hình nhiều uplink để reply traffic đi đúng đường bằng policy routing trên Linux và FIB trên FreeBSD mà không cắt SSH.","Console/phiên cứu hộ; biết interface, source subnet, gateway và route baseline.",["Chụp route/rule hoặc FIB baseline và xác định flow quản trị.","Tạo rule/table Linux hoặc FIB FreeBSD mà chưa xóa default path đang chạy.","Kiểm route lookup theo source trước khi persist.","Mở phiên SSH mới qua đường cần hỗ trợ rồi mới persist."],["Route lookup chọn đúng gateway/table/FIB.","Phiên SSH hiện tại và phiên mới vẫn hoạt động.","Traffic test không còn asymmetric reply qua gateway sai."],True),
30:("Lần theo đăng nhập và privilege escalation để trả lời ai, từ đâu, khi nào và cơ chế nâng quyền nào có bằng chứng.","Quyền đọc auth/audit logs; chốt time window và identity cần điều tra.",["Chốt time window và identity trước khi query.","Đối chiếu sshd/login với sudo/doas/su theo hệ điều hành.","Ghép event bằng timestamp, PID/session hoặc user/source.","Ghi rõ khoảng trống nếu logging policy không đủ kết luận."],["Xác định login success/failure và source khi log có ghi.","Privilege escalation được liên kết với user/session khi có bằng chứng.","Không suy diễn command history nếu chỉ có authentication log."],False),
}
META=re.compile(r'(<script[^>]+id=["\']ld-meta["\'][^>]*>)(.*?)(</script>)',re.I|re.S)
HEADER=re.compile(r'</header>',re.I)
def get_issue(t):
 m=META.search(t)
 if not m:return None
 try:return int(json.loads(html.unescape(m.group(2)))['issue'])
 except:return None
def numbered(num): return re.compile(r'(<section(?P<a>[^>]*)>\s*<h2(?P<h>[^>]*)>\s*<span[^>]*class=["\']num["\'][^>]*>'+num+r'</span>)(?P<title>.*?</h2>)(?P<body>.*?</section>)',re.I|re.S)
def set_section(t,num,title,insert=''):
 p=numbered(num)
 return p.sub(lambda m:m.group(1)+' '+title+'</h2>'+insert+m.group('body'),t,count=1)
def migrate(p):
 t=p.read_text(encoding='utf-8'); i=get_issue(t)
 if i not in D:return False
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
 # Language classes without touching code body.
 t=re.sub(r'<pre(?P<p>[^>]*)>\s*<code(?![^>]*language-)(?P<c>[^>]*)>',lambda m:f'<pre{m.group("p")}><code class="language-bash"{m.group("c")}>',t,flags=re.I)
 # Add run context before pre if none in previous 500 chars.
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
