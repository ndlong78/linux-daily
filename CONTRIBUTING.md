# Contributing to Linux Daily

Cảm ơn bạn đã muốn đóng góp cho Linux Daily. Nếu đây là lần đầu làm việc với repository, bắt đầu tại **`docs/contributor-quickstart.md`**.

## Quick start

```bash
python3 tools/contributor.py doctor
python3 -m pip install -e ".[dev]"
python3 tools/publish.py check
```

`tools/contributor.py doctor` chỉ kiểm baseline môi trường/repository. `tools/publish.py` vẫn là entrypoint chính cho regenerate + validation, để contributor và CI dùng cùng quality contract.

## Issue trước hay PR trước?

Nếu mới phát hiện vấn đề hoặc muốn thảo luận scope, hãy mở issue bằng form phù hợp:

- **Bug report** cho website/tooling/CI/production behavior sai.
- **Content / technical correction** cho nội dung Linux/Unix cần sửa hoặc cập nhật.
- **Feature proposal** cho capability/cải tiến mới.

Xem `docs/issue-guidelines.md` để biết thông tin tối thiểu cần cung cấp. **Không báo lỗ hổng bảo mật bằng public issue**; dùng GitHub Security Policy / `SECURITY.md`.

Issue không bắt buộc trước mọi PR. Với thay đổi nhỏ, rõ scope, contributor có thể mở PR trực tiếp và mô tả đầy đủ trong PR template.

## Nguyên tắc đóng góp

- Không push trực tiếp vào `main`; mọi thay đổi đi qua pull request.
- Giữ diff nhỏ, có mục tiêu rõ ràng và tránh trộn nhiều nhóm thay đổi không liên quan.
- Không commit secret, token, password, private key hoặc dữ liệu nhạy cảm.
- Generated file phải được tạo bằng tool hiện có, không sửa tay nếu có generator tương ứng.
- Không tạo workflow/helper one-shot để GitHub Actions tự sửa, commit hoặc push ngược branch.
- Không track file tạm (`*.tmp`, `*.bak`, `*.orig`, `*.rej`) hoặc helper gắn trực tiếp số PR.
- Không merge khi `quality-gate` chưa xanh và không bypass branch protection.
- Normal PR dùng **Squash and merge** để `main` nhận một commit mô tả rõ thay đổi.

## Quy trình chuẩn — one pass

1. Đồng bộ `main`, tạo feature branch.
2. Thực hiện thay đổi + test/tài liệu liên quan.
3. Nếu thay bài/metadata, chạy `python3 tools/publish.py prepare` để materialize generated artifacts **trước commit**.
4. Chạy `python3 tools/pr_preflight.py`; preflight bao gồm PR hygiene, lint, test, workflow safety và publish check.
5. Review `git diff`, commit với subject mô tả rõ, push branch và mở/cập nhật PR.
6. CI chỉ đọc/validate branch. Nếu CI fail, sửa source/generator bình thường, chạy preflight lại rồi commit/push thêm; không dùng finalizer tự ghi repository.
7. Khi exact head SHA xanh và review xong, merge bằng **Squash and merge**.

Nếu PR thay URL/source, chạy thêm:

```bash
python3 tools/check_links.py --external --workers 8
```

Nếu PR thay workflow, `tools/pr_preflight.py` đã gọi `tools/workflow_safety.py`; có thể chạy riêng để debug:

```bash
python3 tools/workflow_safety.py
```

## Khi sửa hoặc thêm bài Linux Daily

- Giữ đúng metadata `ld-meta`, template hiện hành và canonical taxonomy.
- Bài mới/technical review phải dùng nguồn `official`/`upstream`; metadata nguồn và phần **Nguồn kỹ thuật** hiển thị phải khớp.
- FreeBSD luôn xử lý riêng; không áp `systemd`, `apt`, `dnf`, `nmcli`, `netplan`, `nftables` của Linux sang FreeBSD.
- Với networking/firewall/storage/backup/auth/automation, rà rollback path, destructive flags và restore evidence khi áp dụng.
- Không sao chép claim kỹ thuật cũ sang bài mới nếu chưa kiểm chứng lại.
- Không thêm Google Fonts/CDN runtime dependency; giữ accessibility baseline hiện có.
- Không tự ý thay cadence trong `state.json` nếu PR không nhằm thay cadence.

Nếu bạn là **technical reviewer**, dùng `docs/technical-review-guide.md` làm checklist độc lập cho source quality, distro portability, FreeBSD semantics, rollback/destructive operations và verification evidence. Reviewer không cần biết lịch sử repository để áp dụng guide này.

Xem `AGENTS.md` để hiểu operating contract chi tiết của AI agent. Contributor người thật không cần làm theo các bước scheduler riêng của agent, trừ khi đang tạo bài mới theo cadence.

## Khi sửa website/pipeline

- Public canonical origin lấy từ `site.json`; production nằm trên Cloudflare Worker.
- Validator mới nên deterministic local; network check phải có timeout/retry/non-flaky policy.
- Workflow phải qua `tools/workflow_safety.py`; release là workflow ghi duy nhất và vẫn yêu cầu human confirmation.
- Không thêm finalizer/self-mutating workflow để bù cho generator hoặc staging chưa deterministic; sửa generator/preflight thay vì tăng automation ghi.
- Cập nhật tài liệu/roadmap/changelog nếu thay đổi kiến trúc hoặc milestone đáng chú ý.

## Pull request

PR nên nêu rõ mục tiêu, scope, guardrails, cách kiểm thử và rủi ro/giới hạn còn lại. Repository có `.github/pull_request_template.md` làm checklist mặc định.

Commit subject không được dùng các message rác như `x`, `tmp`, `test`, `wip`, `placeholder`, `fix`, `update` hoặc `changes`; CI kiểm rule này trên commit range của PR.

## Release / production change

Với release/tag hoặc thay đổi production đáng kể, dùng `docs/release-checklist.md`. Rollback phải đi qua PR/revert có CI thay vì sửa trực tiếp `main`.
