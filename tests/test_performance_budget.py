from __future__ import annotations

import performance_budget


def test_budget_policy_has_explicit_limits():
    assert performance_budget.BUDGETS["homepage_html"] == 256 * 1024
    assert performance_budget.BUDGETS["post_html_each"] == 512 * 1024
    assert performance_budget.BUDGETS["social_image_each"] == 2 * 1024 * 1024


def test_current_repository_is_within_performance_budget():
    failures, metrics = performance_budget.collect()
    assert failures == []
    assert metrics["homepage_html"] > 0
    assert metrics["post_html_max"] > 0
    assert metrics["fonts_total"] > 0
    assert metrics["social_images_total"] > 0


def test_artifact_kham_pha_deu_co_tran():
    """archive/search-index/learning-paths tăng tuyến tính theo số bài.

    Trước khi có ba trần này, không cổng nào canh chúng: `index.html` đã được
    phân trang và có trần từ trước, còn ba file kia cứ phình mãi. Hồi quy trên
    lịch sử git (#34 → #66) cho 479 / 575 / 1037 B mỗi bài, tức ở 1000 bài là
    474 / 565 / 1006 KiB.

    Bỏ bất kỳ trần nào ở đây là quay lại đúng trạng thái mù đó.
    """
    for key in ("archive_html", "search_index_json", "learning_paths_html"):
        assert performance_budget.BUDGETS[key] == 256 * 1024


def test_ba_artifact_kham_pha_that_su_duoc_do():
    """Trần chỉ có tác dụng nếu file thật sự được đưa vào `collect()`."""
    _, metrics = performance_budget.collect()
    for key in ("archive_html", "search_index_json", "learning_paths_html"):
        assert metrics[key] > 0, f"{key} không được đo — trần thành vô nghĩa"


def test_vuot_tran_thi_bao_do(tmp_path, monkeypatch):
    """Tamper test: phình learning-paths.html quá trần thì phải đỏ."""
    monkeypatch.setattr(performance_budget, "ROOT", tmp_path)
    (tmp_path / "index.html").write_bytes(b"x")
    (tmp_path / "learning-paths.html").write_bytes(
        b"x" * (performance_budget.BUDGETS["learning_paths_html"] + 1)
    )

    failures, _ = performance_budget.collect()

    assert [f.label for f in failures] == ["learning_paths_html"]


def test_moi_metric_co_tran_deu_in_phan_tram(capsys):
    """Cổng chỉ báo lúc đã vượt là báo quá muộn — phải thấy được dư địa."""
    performance_budget.main([])
    out = capsys.readouterr().out

    for line in out.splitlines():
        key = line.split(" ", 1)[0]
        if key in performance_budget.METRIC_LIMIT:
            assert "% ngân sách" in line, f"{key} thiếu phần trăm dư địa"
