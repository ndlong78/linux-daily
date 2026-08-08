# Linux Daily — Safe Workflow Automation

P5.3 bổ sung guardrail cho GitHub Actions để tăng automation mà không tăng quyền ngoài ý muốn.

## Policy

Chạy local:

```bash
python tools/workflow_safety.py
```

CI cũng chạy cùng validator trên mọi PR.

Validator hiện kiểm:

- mọi workflow phải khai báo `permissions` ở top-level;
- `pull_request_target` bị cấm;
- `contents: write` chỉ được phép ở `release.yml`;
- `actions/pull-requests/issues/packages/deployments: write` bị cấm;
- workflow release chỉ được chạy qua `workflow_dispatch`;
- release phải giữ explicit confirmation, checkout `main` và exact-main-SHA gate;
- command auto-merge hoặc branch-protection bypass bị cấm.

## Safety boundary

Automation được phép build, validate, audit, quan sát production và tạo report. Automation không được tự merge PR, bypass branch protection hoặc tự phát hành release. Release vẫn là thao tác thủ công có confirmation và evidence gate.
