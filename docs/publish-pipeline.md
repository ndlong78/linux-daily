# Publish Pipeline

P5.1 chuẩn hóa quy trình local trước khi mở/cập nhật PR bằng `tools/publish.py`.

## Prepare

Sau khi thêm hoặc sửa bài:

```bash
python tools/publish.py prepare
```

Pipeline regenerate các artifact deterministic qua `tools/build.py`, cập nhật content-mix report và kiểm taxonomy. Nó không commit, push, mở PR hay merge.

## Check

Trước khi push:

```bash
python tools/publish.py check
```

Mode này không ghi file. Nó kiểm build/artifact freshness, taxonomy, content mix, release metadata, performance budget và repository health. Nếu một bước fail, pipeline dừng ngay tại lỗi đầu tiên để feedback rõ ràng.

External HTTP link checking không nằm trong local pipeline vì phụ thuộc mạng và website bên thứ ba; CI vẫn chạy policy retry/non-flaky riêng.

## Human control

Publish automation chỉ giảm thao tác lặp lại. Branch, PR review, merge và release vẫn giữ human approval; pipeline không có quyền tự push `main` hoặc bypass `quality-gate`.
