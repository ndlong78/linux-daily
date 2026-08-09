# P9.4 — Monitoring & Automation Failure Lab

Trạng thái: **draft design / cadence-gated publication**.

Tài liệu này chuẩn bị technical contract cho P9.4 mà không tự ý phát hành Linux Daily #022 trước cadence trong `AGENTS.md`/`state.json`.

## Mục tiêu

P9.4 phải chứng minh đầy đủ chuỗi vận hành:

1. có baseline observability trước khi tạo lỗi;
2. failure injection có blast radius giới hạn trên tài nguyên lab;
3. metric/log/service-state cho thấy failure thật sự xảy ra;
4. automation phục hồi dịch vụ theo cơ chế riêng của từng HĐH;
5. probe chức năng xác nhận dịch vụ phục hồi;
6. cleanup đưa tài nguyên lab về trạng thái an toàn.

Lab không được coi `exit 0` của command là đủ evidence.

## Phạm vi failure injection

Các fault class dự kiến:

- CPU pressure có timeout cứng;
- RAM pressure có giới hạn thấp, không đẩy máy vào OOM có chủ đích;
- file-I/O pressure chỉ ghi vào thư mục lab disposable;
- service process failure trên dịch vụ lab, không đụng dịch vụ quản trị như SSH.

`stress-ng` chỉ dùng với worker count, memory size, path và timeout hữu hạn. Không dùng `--all`, không dùng raw-device stressor và không chạy lên host production/shared infrastructure.

## Topology dự kiến

- `admin`: máy quản trị/probe độc lập;
- `target`: VM Ubuntu/Xubuntu, Debian, Fedora hoặc FreeBSD đang chạy dịch vụ HTTP lab;
- `observer`: có thể cùng `admin`, thu thập probe latency/availability trước, trong và sau fault.

Dịch vụ HTTP chỉ bind vào mạng lab. Snapshot/console hypervisor là đường lui trước khi thử recovery automation.

## Distro boundary

### Ubuntu / Xubuntu

- package manager: APT;
- service manager: systemd;
- evidence: `systemctl status/show`, `journalctl`, `vmstat`, `iostat` khi package tương ứng có mặt;
- recovery service lab dựa trên unit có `Restart=on-failure` và giới hạn restart.

### Debian stable

- package manager: APT, ưu tiên package trong stable;
- service manager: systemd;
- cùng semantics systemd với Ubuntu nhưng không giả định package/version ngoài Debian stable;
- evidence/recovery phải dùng command có trong package set được khai báo.

### Fedora

- package manager: DNF;
- service manager: systemd;
- SELinux giữ enforcing; lab không tắt SELinux để “sửa nhanh” lỗi service;
- nếu dịch vụ lab dùng path/context ngoài mặc định thì phải kiểm tra label thay vì disable policy.

### FreeBSD

- package manager: `pkg`/ports;
- service manager: rc.d + `service`, **không có systemd**;
- service lab dùng rc.d script riêng; nếu cần supervise/restart child process thì dùng cơ chế FreeBSD phù hợp như `daemon(8)` supervision, không sao chép `Restart=` từ Linux;
- observability dùng công cụ BSD tương ứng (`service ... status`, `syslog`, `vmstat`, `iostat` nếu phù hợp), không dùng `journalctl`/`systemctl`.

## Contract P9.4

Lab published của P9.4 dự kiến khai báo:

```json
{
  "lab": {
    "version": 1,
    "profile": "advanced",
    "topology": ["admin", "target", "observer"],
    "risks": ["resource-pressure", "downtime"],
    "rollback_required": true,
    "cleanup_required": true,
    "failure_injection": true,
    "verification": ["functional", "negative", "recovery", "observability"]
  }
}
```

P9.4 sẽ tăng contract theo hướng: `resource-pressure` phải đi cùng failure injection, recovery evidence và observability evidence.

## Verification matrix

| Giai đoạn | Evidence tối thiểu |
|---|---|
| Baseline | HTTP probe thành công + service state + CPU/RAM/I/O snapshot |
| Fault | bounded stressor/service failure chạy trong scope lab |
| Detect | metric/log/state thay đổi đúng kỳ vọng |
| Recover | supervisor/automation đưa service trở lại |
| Functional | HTTP probe mới thành công sau recovery |
| Cleanup | stressor hết, temp data xóa, service lab dừng/gỡ nếu không giữ |

## Safety gate

Không chạy lab nếu thiếu một trong các điều kiện sau:

- VM/snapshot hoặc console cứu hộ;
- xác nhận target là lab resource;
- timeout cho mọi stressor;
- memory/file-I/O limit hữu hạn;
- probe quản trị độc lập với service bị thử;
- rollback + cleanup command đã chuẩn bị trước fault.

## Publication gate

`main` hiện có `last_issue = 21`, `last_published_date = 2026-08-09`. Theo `AGENTS.md`, bài mới phải qua cadence gate 2 ngày và dùng trục canonical của issue tiếp theo. Vì vậy PR này không tự ý sửa `state.json`, `topics.md` hoặc tạo #022 trong cùng nhịp chỉ để hoàn thành roadmap sớm.

Khi cadence mở, phần published lab sẽ bổ sung post/social/learning metadata/generated artifacts và chạy toàn bộ CI cho đến khi xanh.

## Nguồn primary dùng khi authoring bài

- systemd.service upstream manual — restart policy và rate limiting.
- FreeBSD Handbook — rc.d/service và syslog.
- FreeBSD `service(8)` / `daemon(8)` manpages — service control và process supervision.
- stress-ng upstream README/manual — bounded CPU/VM/I/O stressors và timeout.

Chỉ claim/lệnh đã đối chiếu official/upstream mới được đưa vào bài published.
