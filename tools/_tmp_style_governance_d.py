#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parents[1]
# validator
p=root/'tools/validate_style.py'; t=p.read_text()
t=t.replace('Historical posts are migrated in batches. Linux Daily #001-#030 have completed\nSTYLE.md backfill and are enforced together with all new posts #041+.', 'Historical backfill is complete. Linux Daily #001-#040 and every new post are\nenforced by the STYLE.md contract.')
t=t.replace('BACKFILLED_THROUGH = 30','BACKFILLED_THROUGH = 40')
t=t.replace('            f"OK: STYLE.md enforced cho #001-#{BACKFILLED_THROUGH:03d} và từ "\n            f"#{ENFORCED_FROM_ISSUE:03d}+.",','            "OK: STYLE.md enforced cho toàn bộ Linux Daily series.",')
p.write_text(t)
# tests: replace former legacy #040 test with enforced Batch D test
p=root/'tests/test_validate_style.py'; t=p.read_text()
old='''def test_unmigrated_legacy_post_is_audited_but_not_enforced(tmp_path: Path):\n    post = tmp_path / "post-040-style-test.html"\n    post.write_text(_post(40, valid=False), encoding="utf-8")\n    result = validate_style.audit_post(post)\n    assert not result.enforced\n    assert result.errors\n    assert validate_style.check([result]) == 0\n'''
new='''def test_batch_d_issue_40_is_enforced(tmp_path: Path):\n    post = tmp_path / "post-040-style-test.html"\n    post.write_text(_post(40, valid=False), encoding="utf-8")\n    result = validate_style.audit_post(post)\n    assert result.enforced\n    assert any("tested_on" in error for error in result.errors)\n    assert validate_style.check([result]) == 1\n'''
t=t.replace(old,new)
p.write_text(t)
# audit doc: close legacy baseline
p=root/'docs/STYLE-AUDIT.md'; t=p.read_text()
t=t.replace('Current enforcement: **#001–#030 và #041+**','Current enforcement: **toàn bộ series #001+**')
t=t.replace('PR Batch A đã backfill **#001–#010** và Batch B backfill **#011–#020** theo contract `STYLE.md`. Các bài #001–#020 không còn được grandfather: `tools/validate_style.py` sẽ fail CI nếu regress.\n\nCác bài **#031–#040** vẫn là legacy migration backlog. Legacy không có nghĩa nội dung kỹ thuật không hợp lệ; trạng thái này chỉ nói bài chưa đáp ứng đầy đủ contract mới về metadata, step structure, command context và code semantics.', 'Batch A–D đã backfill hoàn tất **#001–#040** theo contract `STYLE.md`. Không còn grandfather/legacy exemption: `tools/validate_style.py` sẽ fail CI nếu bất kỳ bài lịch sử hoặc bài mới nào regress.')
t=t.replace('- mặc định: fail CI nếu **#001–#030** hoặc **#041+** vi phạm;\n- `--audit`: in chi tiết trạng thái của toàn bộ lịch sử;\n- **#031–#040** tiếp tục được audit nhưng chưa fail cho tới khi batch tương ứng hoàn tất;\n- legacy exemption không áp dụng cho nội dung mới sao chép từ bài cũ.', '- mặc định: fail CI nếu **bất kỳ bài #001+** vi phạm;\n- `--audit`: in chi tiết trạng thái của toàn bộ series;\n- legacy exemption đã được đóng hoàn toàn sau Batch D.')
t=t.replace('| D | #031–#040 | Chờ | Chuẩn hóa các bài gần nhất và đóng legacy baseline |','| D | #031–#040 | **Hoàn tất trong PR #89** | Chuẩn hóa các bài gần nhất và đóng legacy baseline |')
t=t.replace('Batch B đã nâng `BACKFILLED_THROUGH` lên 20; Batch C sẽ nâng lên 30; Batch D lên 40. Khi #001–#040 đều đạt contract mới, có thể đơn giản hóa validator thành enforcement toàn bộ series.', 'Batch D nâng `BACKFILLED_THROUGH` lên 40. Vì #041+ vốn đã enforced, từ PR #89 STYLE.md áp dụng cho **toàn bộ series**, không còn legacy backlog.')
p.write_text(t)
