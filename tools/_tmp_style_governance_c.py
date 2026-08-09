#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parents[1]
# validator
p=root/'tools/validate_style.py'; t=p.read_text()
t=t.replace('Linux Daily #001-#020 have completed','Linux Daily #001-#030 have completed')
t=t.replace('BACKFILLED_THROUGH = 20','BACKFILLED_THROUGH = 30')
p.write_text(t)
# tests
p=root/'tests/test_validate_style.py'; t=p.read_text()
needle='''def test_issue_41_requires_style_metadata(tmp_path: Path):\n'''
block='''def test_batch_c_issue_30_is_enforced(tmp_path: Path):\n    post = tmp_path / "post-030-style-test.html"\n    post.write_text(_post(30, valid=False), encoding="utf-8")\n    result = validate_style.audit_post(post)\n    assert result.enforced\n    assert any("tested_on" in error for error in result.errors)\n    assert validate_style.check([result]) == 1\n\n\n'''
if 'test_batch_c_issue_30_is_enforced' not in t:t=t.replace(needle,block+needle)
p.write_text(t)
# audit doc
p=root/'docs/STYLE-AUDIT.md'; t=p.read_text()
t=t.replace('Current enforcement: **#001–#020 và #041+**','Current enforcement: **#001–#030 và #041+**')
t=t.replace('PR Batch A và Batch B đã backfill **#001–#020**','PR Batch A, Batch B và Batch C đã backfill **#001–#030**')
t=t.replace('Các bài **#021–#040** vẫn là legacy migration backlog.','Các bài **#031–#040** vẫn là legacy migration backlog.')
t=t.replace('mặc định: fail CI nếu **#001–#020** hoặc **#041+** vi phạm;','mặc định: fail CI nếu **#001–#030** hoặc **#041+** vi phạm;')
t=t.replace('**#021–#040** tiếp tục được audit','**#031–#040** tiếp tục được audit')
t=t.replace('| C | #021–#030 | Chờ |','| C | #021–#030 | **Hoàn tất trong PR #88** |')
p.write_text(t)
