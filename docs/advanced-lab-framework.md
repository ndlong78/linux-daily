# Advanced Lab Framework

P9.1 chuẩn hóa cách Linux Daily viết và review lab end-to-end mới. Mục tiêu là biến các yêu cầu an toàn vốn chỉ nằm trong prose thành một contract machine-readable đủ nhỏ để CI kiểm được, nhưng không duplicate nội dung kỹ thuật của bài.

## Phạm vi

- Hai lab lịch sử #007 và #014 được giữ nguyên như **legacy reference**.
- Từ **issue #020**, mọi bài mang semantics lab (`axis = Ôn tập`, eyebrow có `Lab`, hoặc có `ld-meta.lab`) phải khai báo contract mới.
- Không backfill giả metadata vào bài cũ chỉ để làm đẹp baseline.
- Distro coverage vẫn do P7.1 kiểm. Advanced Lab contract không định nghĩa lại Ubuntu/Debian/Fedora/FreeBSD command semantics.

## Contract trong `ld-meta`

Ví dụ cho một Advanced Lab có nguy cơ tự khóa SSH:

```json
{
  "lab": {
    "version": 1,
    "profile": "advanced",
    "topology": ["admin", "target"],
    "risks": ["lockout", "network-isolation"],
    "rollback_required": true,
    "cleanup_required": true,
    "failure_injection": true,
    "verification": ["functional", "negative", "recovery", "persistence"]
  }
}
```

### `profile`

- `standard`: lab nhỏ nhưng vẫn có topology/safety/verification/cleanup rõ ràng.
- `advanced`: ít nhất 2 topology roles và ít nhất 2 verification classes; rollback luôn bắt buộc.

P9 Advanced Labs dùng `profile = advanced`.

### `topology`

Danh sách **role**, không phải hostname/IP production. Ví dụ:

```json
["admin", "linux-server", "freebsd-peer"]
```

Advanced Lab cần ít nhất hai role để tránh biến một chuỗi command local thành “lab end-to-end”.

### `risks`

Allowed values:

- `none`
- `lockout`
- `network-isolation`
- `downtime`
- `destructive-storage`
- `credential-exposure`
- `resource-pressure`

`none` phải đứng một mình. Nếu có bất kỳ risk thực tế nào, `rollback_required` phải là `true`.

### `verification`

Allowed values:

- `functional` — chức năng chính hoạt động;
- `negative` — điều không được phép thực sự bị chặn/fail;
- `persistence` — trạng thái còn đúng sau reload/reboot theo scope;
- `recovery` — khôi phục thành công sau failure/rollback;
- `restore` — dữ liệu được restore và kiểm chứng;
- `observability` — metric/log/state evidence chứng minh behavior.

Nếu `failure_injection = true`, phải có `recovery`. Nếu risk có `destructive-storage`, phải có `restore`.

Nếu risk có `resource-pressure`, contract chặt hơn:

- `failure_injection` phải là `true`;
- `verification` phải có `observability` để chứng minh pressure/failure bằng metric, log hoặc service state;
- `verification` phải có `recovery` để chứng minh hệ thống trở lại trạng thái phục vụ được.

Mục đích là ngăn một “monitoring lab” chỉ chạy stressor rồi kết thúc mà không có evidence hoặc recovery.

## Semantic section markers

Bài lab mới dùng `<section data-lab-section="...">` để CI kiểm đúng cấu trúc mà không parse câu chữ tiếng Việt.

Tối thiểu:

```html
<section data-lab-section="scenario">...</section>
<section data-lab-section="topology">...</section>
<section data-lab-section="safety">...</section>
<section data-lab-section="execution">...</section>
<section data-lab-section="verification">...</section>
<section data-lab-section="rollback">...</section>
<section data-lab-section="cleanup">...</section>
```

Nếu `failure_injection = true`, thêm:

```html
<section data-lab-section="failure-injection">...</section>
```

Marker phải unique trong một bài.

## Authoring skeleton

Một Advanced Lab nên đi theo flow:

1. **Scenario:** mục tiêu vận hành và tiêu chí thành công.
2. **Topology:** role, network/storage boundary và nơi chạy từng lệnh.
3. **Safety:** snapshot/backup/console/session cứu hộ, placeholder và blast radius.
4. **Execution:** triển khai từng bước, tách rõ Linux và FreeBSD.
5. **Failure injection:** chủ động làm hỏng một thành phần nếu scope yêu cầu.
6. **Verification:** functional + negative + persistence/recovery/restore/observability evidence phù hợp.
7. **Rollback:** đưa hệ thống về trạng thái trước lab hoặc trạng thái safe đã định nghĩa.
8. **Cleanup:** xóa lab resources, temporary rules, snapshots/test data nếu không cần giữ.

Không coi “command exit 0” là verification đủ cho lab production-style.

## Distro boundary

P9.1 không thay P7.1. Bài mới từ #020 vẫn phải explicit coverage Ubuntu/Xubuntu, Debian, Fedora và FreeBSD theo policy hiện có.

Advanced Lab phải đặc biệt tránh:

- dùng `systemctl`, `journalctl`, `nftables`, `nmcli`, `apt` hoặc `dnf` trong block FreeBSD;
- giả định `/etc/systemd`, Linux device names hoặc Linux firewall semantics trên FreeBSD;
- mô tả `pf`/`ipfw` như alias của nftables/firewalld.

FreeBSD dùng `pkg`/ports, rc.d + `/etc/rc.conf`, `service`, pf/ipfw và path/layout riêng khi phù hợp.

## Safety invariants

### Networking / firewall / auth

Nếu lab có `lockout` hoặc `network-isolation`:

- giữ console/phiên quản trị dự phòng;
- validate runtime/temporary state trước persistence khi tool hỗ trợ;
- có negative test và recovery/rollback evidence phù hợp.

### Storage

Nếu lab có `destructive-storage`:

- target device/pool/dataset phải là lab resource rõ ràng;
- backup/snapshot phải tồn tại trước thao tác destructive;
- `verification` bắt buộc có `restore`;
- restore phải vào safe target trước khi cân nhắc overwrite.

### Resource pressure / monitoring

Nếu lab có `resource-pressure`:

- chỉ dùng CPU/RAM/I/O target thuộc lab và phải giới hạn worker/size/path/thời gian;
- không cố ý tạo OOM, raw-device pressure hoặc saturation không có timeout;
- baseline observability phải được ghi trước failure injection;
- fault phải tạo evidence quan sát được;
- automation/supervisor recovery phải được kiểm lại bằng service-state và functional probe;
- cleanup phải xác nhận stressor không còn chạy và temporary I/O data đã được xóa.

### Failure injection

Failure injection phải có:

- blast radius giới hạn;
- expected failure state;
- recovery evidence;
- cleanup sau test.

Không inject failure vào production/shared infrastructure trong hướng dẫn copy-paste.

## Validator

Chạy trực tiếp:

```bash
python3 tools/lab_contract.py
python3 tools/lab_contract.py --json
```

`tools/publish.py check` chạy validator này như deterministic local gate.

Hard-fail gồm:

- lab mới thiếu `ld-meta.lab`;
- version/profile/risk/verification value không hợp lệ;
- duplicate topology/risk/verification/section marker;
- Advanced Lab có dưới 2 topology roles hoặc dưới 2 verification classes;
- risk thực tế nhưng không yêu cầu rollback;
- destructive storage không có restore evidence class;
- failure injection không có recovery class/section;
- resource pressure không bật failure injection hoặc thiếu observability/recovery evidence;
- thiếu semantic section bắt buộc.

## Baseline khi mở P9

- lab posts lịch sử: **2** (#007, #014);
- legacy labs: **2**;
- enforced labs: **0**;
- advanced labs: **0**;
- contract errors: **0**.

Baseline 0 Advanced Lab là đúng ở P9.1: framework được dựng trước, lab thực tế sẽ vào các PR P9 tiếp theo.

## Roadmap áp dụng contract

- **P9.2:** Security & Networking Advanced Lab.
- **P9.3:** Storage & Backup/Restore Advanced Lab.
- **P9.4:** Monitoring & Automation Failure Lab.
- **P9.5:** Linux ↔ FreeBSD Interoperability Lab.

Mỗi PR lab phải vẫn đi qua source-backed review, distro coverage, command quality, learning metadata/progression và Advanced Lab contract; P9 không bypass các gate đã có.
