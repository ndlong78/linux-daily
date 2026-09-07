# STYLE.md — Quy ước Ngôn ngữ & Văn phong · Linux Daily

> Tài liệu chuẩn cho mọi bài hướng dẫn kỹ thuật trong repo này.
> Nguyên tắc cốt lõi: **Tối giản – Chính xác – Hành động được – Định dạng chuẩn.**
> Áp dụng cho: Ubuntu/Xubuntu · Debian · Fedora · FreeBSD.

---

## 0. Triết lý một dòng

Mỗi bài phải trả lời được câu hỏi: *"Người đọc dán lệnh vào terminal, chạy đúng thứ tự, và ra kết quả — không cần đoán thêm ngữ cảnh."* Nếu một câu không phục vụ mục tiêu đó, xóa nó.

## 1. Bốn trụ cột văn phong

### 1.1. Trực diện & Mệnh lệnh

- Mở đầu mỗi bước bằng **động từ hành động**: *Cài đặt, Cấu hình, Khởi động, Tạo, Kiểm tra, Xóa*.
- Cấm từ hoa mỹ và dẫn dắt như “Như chúng ta đã biết”, “Thật tuyệt vời”, “Trong thế giới ngày nay”.
- Câu ngắn. Một câu = một ý. Không câu cảm thán.
- Viết ở ngôi mệnh lệnh, không dùng “chúng ta sẽ...”.

### 1.2. Chính xác & Minh bạch ngữ cảnh

- **Luôn ghi rõ quyền chạy lệnh**: user thường, `sudo`, hay root.
- **Luôn ghi rõ nhánh OS** khi lệnh khác nhau giữa các distro.
- **Luôn có Expected Output/Kết quả mong đợi** cho lệnh kiểm chứng.
- Không khẳng định “chắc chắn chạy”; chỉ ghi runtime-test khi thực sự đã chạy trên môi trường đó.
- Review tài liệu official/upstream phải ghi riêng là **Documentation verified**, không được đổi tên thành **Runtime tested**.

### 1.3. Có thể quét mắt

- Dùng danh sách đánh số cho quy trình tuyến tính.
- Dùng gạch đầu dòng cho prerequisite, lựa chọn, hoặc danh sách không có thứ tự.
- Một numbered step = một hành động/lệnh chính.

### 1.4. Quy chuẩn thị giác

- `Inline code` cho tên lệnh, đường dẫn, package, tham số, service.
- Code block chỉ chứa nội dung copy-paste được.
- Placeholder dùng duy nhất dạng `<...>`.

## 2. Cấu trúc chuẩn của bài Linux Daily

Linux Daily giữ 7 mục nội dung chuyên môn để bảo toàn cấu trúc series, đồng thời thêm metadata, mục tiêu và prerequisite của style contract. Thứ tự chuẩn:

1. Metadata `Runtime tested` + `Documentation verified` + `Last verified`.
2. **Mục tiêu** — một câu.
3. **Yêu cầu tiên quyết** — OS/version, quyền, mạng/cổng/dung lượng, dependency.
4. `01 Bối cảnh thực tế`.
5. `02 Kiến thức cốt lõi`.
6. `03 Các bước thực hiện` — numbered steps, quyền chạy, nhánh OS, command/config block.
7. `04 Kiểm chứng` — end-to-end verification + Expected Output.
8. **Gỡ / Hoàn tác** — bắt buộc nếu bài thay đổi hệ thống; mục này không đánh số.
9. `05 Lưu ý & Khắc phục lỗi`.
10. `06 Bảo mật & vận hành`.
11. `07 Bài tập tự luyện`.
12. **Nguồn kỹ thuật** — không đánh số.

Mục không áp dụng có thể bỏ, ngoại trừ metadata, Mục tiêu, Yêu cầu tiên quyết, Các bước thực hiện, Kiểm chứng, Lưu ý & Khắc phục lỗi và Bài tập tự luyện.

## 3. Metadata block

Từ Linux Daily **#070**, baseline OS hiện hành lấy từ `platform-baseline.json`. Không copy version từ bài lịch sử để dùng cho bài mới.

Baseline đã xác minh ngày **2026-09-07**:

```text
Runtime tested: —
Documentation verified: Ubuntu/Xubuntu 26.04 LTS · Debian 13 stable · Fedora 44 · FreeBSD 15.1-RELEASE
Last verified: 2026-09-07
```

Nếu có lab/runtime thật, thay `—` bằng đúng OS/version đã chạy. Không suy diễn từ tài liệu sang runtime.

Quy tắc:

- `Runtime tested` / `ld-meta.tested_on` chỉ liệt kê OS/version **thực sự đã chạy kiểm thử**.
- `Documentation verified` / `ld-meta.documentation_verified_on` chỉ liệt kê OS/version đã được đối chiếu với tài liệu official/upstream phù hợp.
- Với bài mới #070+, ưu tiên baseline hiện hành trong `platform-baseline.json`: `Ubuntu/Xubuntu 26.04 LTS`, `Debian 13 stable`, `Fedora 44`, `FreeBSD 15.1-RELEASE`.
- Nếu bài chủ động hướng dẫn một release cũ còn được hỗ trợ, ghi rõ đó là ngoại lệ và verify đúng release đó; không âm thầm hạ baseline chung.
- Hai trường máy đọc đều là list; list có thể rỗng riêng lẻ nhưng **ít nhất một trong hai phải có bằng chứng**.
- Cấm sentinel kiểu `(documentation-verified)` bên trong `tested_on`; loại bằng chứng phải nằm ở đúng field.
- `Last verified` cập nhật khi review lại bài.
- Metadata máy đọc từ #070 dùng các trường `tested_on`, `documentation_verified_on`, `last_verified`, `changes_system`.
- `changes_system` là boolean. Nếu `true`, bài bắt buộc có mục **Gỡ / Hoàn tác**.
- Nếu quá 6 tháng chưa verify, đưa vào freshness review.
- Bằng chứng lịch sử giữ nguyên version đã thật sự review/test. Không đổi #001–#069 thành release mới nếu chưa re-verify claim/lệnh tương ứng.
- #001–#069 được validator đọc tương thích với schema cũ cho tới lần materialize #070. Khi `state.json.last_issue >= 70`, `tools/backfill_site_metadata.py` chuyển deterministic toàn bộ sentinel lịch sử sang `documentation_verified_on` và sửa nhãn hiển thị; không backfill tay từng bài.

## 4. Code block & quyền chạy

### 4.1. Không nhúng prompt `$` / `#`

Không đặt shell prompt vào block lệnh. Khai báo quyền bằng câu dẫn hoặc thuộc tính wrapper `data-run-as="user|sudo|root"`.

```bash
ssh-keygen -t ed25519 -C "<email>"
```

```bash
sudo systemctl restart sshd
```

Không viết `$ ssh-keygen ...` hoặc `# systemctl ...`.

### 4.2. Ngôn ngữ block

Trong HTML, mọi `<pre><code>` phải có class `language-*`, ví dụ:

```html
<pre><code class="language-bash">...</code></pre>
<pre><code class="language-yaml">...</code></pre>
<pre><code class="language-text">...</code></pre>
```

Output mẫu dùng `language-text`, không dùng `language-bash`.

### 4.3. Expected Output

Đặt ngay sau lệnh kiểm chứng và gắn nhãn rõ **Expected Output** hoặc **Kết quả mong đợi**.

## 5. Xử lý nhánh OS

Phạm vi bắt buộc của Linux Daily:

| Nhóm | Hệ điều hành | Package | Service | Ghi chú |
|---|---|---|---|---|
| systemd | Ubuntu/Xubuntu 26.04 LTS | `apt` | `systemctl` | thường dùng Netplan/NetworkManager tùy môi trường |
| systemd | Debian 13 stable | `apt` | `systemctl` | Debian stable hiện hành; point release mới nhất được theo dõi trong baseline |
| systemd | Fedora 44 | `dnf` | `systemctl` | SELinux, NetworkManager/firewalld |
| BSD rc | FreeBSD 15.1-RELEASE | `pkg`/ports | `service` + `/etc/rc.conf` | không dùng systemd; `pf`/`ipfw` thay nftables |

- Nếu chỉ khác package manager, có thể gộp bằng sub-block theo distro.
- Nếu khác cơ chế systemd vs rc.d, tách hẳn khối FreeBSD.
- Không giả định `systemctl`, `apt`, `dnf`, `nmcli`, `netplan` tồn tại trên FreeBSD.
- Không mở rộng Arch/RHEL thành phạm vi bắt buộc nếu bài không chủ động đề cập.

### 5.1. Nhãn OS cho command block

Mỗi command block khác nhau theo OS phải có nhãn đặt **ngay trước** block, dùng class
`code-label <token>`. Thẻ mang nhãn có thể là `<p>` hoặc `<div>`.

| Token | Dùng cho |
|---|---|
| `bsd` | FreeBSD |
| `ubuntu` | Ubuntu/Xubuntu |
| `debian` | Debian |
| `fedora` | Fedora |
| `linux` | chung cho các distro Linux trong bài |
| `same` | lệnh giống hệt nhau trên mọi hệ |

```html
<p class="code-label ubuntu"><span class="dot"></span>Ubuntu/Debian</p>
<div class="code-wrap">
  <p class="run-context" data-run-as="sudo"><strong>Run as:</strong> sudo</p>
  <pre><code class="language-bash">sudo apt install -y ansible</code></pre>
</div>

<p class="code-label bsd"><span class="dot"></span>FreeBSD — KHÁC Linux</p>
<div class="code-wrap">
  <p class="run-context" data-run-as="root"><strong>Run as:</strong> root</p>
  <pre class="bsd"><code class="language-bash">pkg install -y py311-ansible</code></pre>
</div>
```

**Mỗi bài bắt buộc có ít nhất một khối FreeBSD gắn `code-label bsd`.**
`tools/validate_repo.py` chặn bài thiếu khối này; `tools/validate_style.py` chặn bài
không gắn nhãn nào hoặc dùng token ngoài bảng trên.

## 6. Placeholder

Dùng `<...>` cho giá trị bắt buộc thay:

- Đúng: `<username>`, `<domain>`, `<server-ip>`, `<email>`.
- Tránh: `YOUR_USERNAME`, `[username]`, `{{ username }}` trong nội dung bài.

Khi placeholder xuất hiện lần đầu, chú thích ngay sau block.

## 7. Quy ước an toàn

### 7.1. `curl | sh`

Không chạy script mạng bằng pipeline trực tiếp vào shell. Tải file, kiểm tra nội dung/chữ ký/checksum, rồi mới thực thi.

### 7.2. Lệnh phá hủy

Với `rm -rf`, `mkfs`, `dd`, `wipefs`, `zpool destroy` và thao tác tương đương:

> ⚠️ Cảnh báo rõ phạm vi dữ liệu bị xóa, yêu cầu kiểm tra thiết bị/đường dẫn và ưu tiên dry-run khi có.

Không dùng placeholder thiết bị trong lệnh phá hủy nếu chưa có bước inventory xác định đúng target.

### 7.3. Cleanup / Revert

Mọi bài có `changes_system=true` phải có mục **Gỡ / Hoàn tác** và đường lui thực tế: gỡ package, tắt service, khôi phục config backup hoặc rollback state.

## 8. Ngôn ngữ & thuật ngữ

- Prose tiếng Việt; code/config/tên lệnh giữ tiếng Anh.
- Giữ thuật ngữ kỹ thuật gốc khi dịch cưỡng ép làm giảm chính xác: *daemon, socket, mount, kernel, package, repository, firewall*.
- Lần đầu dùng viết tắt, mở ngoặc đầy đủ.
- Nhất quán một cách gọi trong toàn bài.

## 9. Checklist trước khi publish

- [ ] Có metadata `Runtime tested` + `Documentation verified` + `Last verified`.
- [ ] Bài mới dùng baseline OS trong `platform-baseline.json`, trừ khi có ngoại lệ release được giải thích và re-verify rõ.
- [ ] `ld-meta` có `tested_on`, `documentation_verified_on`, `last_verified`, `changes_system`.
- [ ] `tested_on` không chứa bằng chứng chỉ được review qua tài liệu.
- [ ] Ít nhất một trong `tested_on` / `documentation_verified_on` có OS/version thực tế.
- [ ] Mục tiêu gói trong 1 câu.
- [ ] Prerequisites đủ OS/version, quyền và dependency/ngữ cảnh cần thiết.
- [ ] Các bước tuyến tính dùng numbered steps.
- [ ] Lệnh shell ghi rõ quyền chạy.
- [ ] Không có shell prompt `$`/`#` trong command block.
- [ ] Mọi `<pre><code>` có `language-*`.
- [ ] Lệnh kiểm chứng có Expected Output/Kết quả mong đợi.
- [ ] FreeBSD không bị gán lệnh/cơ chế Linux.
- [ ] Placeholder theo chuẩn `<...>` và được giải thích lần đầu.
- [ ] Không có `curl | sh` chạy mù.
- [ ] Lệnh phá hủy có cảnh báo và inventory target.
- [ ] Có Gỡ / Hoàn tác khi `changes_system=true`.
- [ ] Nguồn official/upstream đáp ứng source-backed gate.

## 10. Enforcement trong repository

- `platform-baseline.json` là source of truth cho target OS/version hiện hành của bài mới.
- `AGENTS.md` là operating contract; `STYLE.md` là source of truth về ngôn ngữ, trình bày và safety affordance của bài.
- `tools/validate_style.py` audit và **enforce toàn bộ Linux Daily #001+**; schema verification split bắt buộc từ #070.
- Backfill #001–#040 đã hoàn tất; verification metadata #001–#069 được migrate deterministic khi materialize #070. Xem `docs/STYLE-AUDIT.md`.
- `python3 tools/publish.py check` phải chạy style gate trước khi PR được coi là sẵn sàng review.
