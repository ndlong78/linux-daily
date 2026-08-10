# Linux Daily — Safe Workflow Automation

P5.3 bổ sung guardrail cho GitHub Actions để tăng automation mà không tăng quyền ngoài ý muốn. Sau PR #94, policy được siết theo nguyên tắc **CI read-only, generation trước push**: GitHub Actions kiểm tra repository, không tự sửa rồi commit ngược trở lại branch.

## Policy

Chạy local:

```bash
python tools/workflow_safety.py
python tools/pr_hygiene.py
```

CI chạy cùng validator trên mọi PR. `tools/pr_hygiene.py` kiểm lịch sử commit/path của PR; local preflight cũng chạy hygiene trước các quality gate.

Validator workflow hiện kiểm:

- mọi workflow phải khai báo `permissions` ở top-level;
- workflow không phải release phải khai báo rõ `contents: read`;
- `pull_request_target` bị cấm;
- `contents: write` chỉ được phép ở `release.yml`;
- `actions/pull-requests/issues/packages/deployments: write` bị cấm;
- workflow không phải release không được chạy `git add`, `git commit` hoặc `git push`;
- `ci.yml` phải checkout full history và chạy PR commit/path hygiene;
- workflow release chỉ được chạy qua `workflow_dispatch`;
- release phải giữ explicit confirmation, checkout `main` và exact-main-SHA gate;
- command auto-merge hoặc branch-protection bypass bị cấm.

## PR hygiene

`tools/pr_hygiene.py` chặn các dấu hiệu đã từng gây nhiễu lịch sử repository:

- commit subject không mô tả như `x`, `tmp`, `test`, `wip`, `placeholder`, `fix`, `update`;
- file tạm kiểu `*.tmp`, `*.bak`, `*.orig`, `*.rej` bị track;
- workflow có tên `finalize`/`finalizer` dùng để tự ghi ngược branch;
- helper migration gắn trực tiếp số PR kiểu `tools/pr93_*.py` hoặc `.sh`.

Nếu cần migration/backfill, generator phải là tool bền vững theo capability, chạy **trước commit** và output deterministic phải được review trong cùng PR. Không tạo one-shot workflow/helper rồi tự xóa bằng GitHub Actions.

## One-pass development flow

```text
sync main
  ↓
tạo feature branch
  ↓
sửa source + chạy generator deterministic
  ↓
python tools/pr_preflight.py
  ↓
commit mô tả rõ → push → PR
  ↓
CI read-only
  ├─ fail → sửa source bình thường → preflight → commit/push mới
  └─ pass → review → Squash and merge
```

CI không phải build agent có quyền ghi. Nó chỉ chứng minh branch hiện tại đã chứa đầy đủ source + generated artifacts cần thiết.

## Safety boundary

Automation được phép build, validate, audit, quan sát production và tạo report. Automation không được tự merge PR, bypass branch protection hoặc tự phát hành release. `release.yml` là workflow ghi duy nhất và vẫn là thao tác thủ công có confirmation + exact-SHA evidence gate.
