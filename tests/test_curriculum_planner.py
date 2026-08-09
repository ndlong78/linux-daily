import curriculum_planner


AXES = ["Networking", "Bảo mật", "Storage", "Công cụ mới", "Monitoring", "Automation", "Ôn tập"]


def topic(axis: str, name: str = "Chủ đề quản trị hệ thống đủ dài") -> dict:
    return {
        "axis": axis,
        "topic": name,
        "difficulty": "intermediate",
        "goal": "Mục tiêu kỹ thuật đủ dài để mô tả kết quả học tập.",
    }


def test_repository_plan_is_valid():
    assert curriculum_planner.validate() == []


def test_axis_rotation_starts_after_published_count(monkeypatch):
    monkeypatch.setattr(curriculum_planner.taxonomy, "load_taxonomy", lambda: {"axes": {axis: {} for axis in AXES}})
    posts = [{"issue": index + 1, "axis": AXES[index % 7], "title": f"Bài {index + 1}"} for index in range(8)]
    queue = [topic(AXES[(1 + index) % 7], f"Chủ đề {index} quản trị hệ thống") for index in range(7)]
    plan = {"version": 1, "policy": {"planning_horizon_days": 7}, "topics": queue}
    assert curriculum_planner.validate(plan, posts) == []


def test_duplicate_queue_topic_is_rejected(monkeypatch):
    monkeypatch.setattr(curriculum_planner.taxonomy, "load_taxonomy", lambda: {"axes": {axis: {} for axis in AXES}})
    queue = [topic(axis, f"Chủ đề {index} quản trị hệ thống") for index, axis in enumerate(AXES)]
    queue[6]["topic"] = queue[0]["topic"]
    plan = {"version": 1, "policy": {"planning_horizon_days": 7}, "topics": queue}
    errors = curriculum_planner.validate(plan, [])
    assert any("trùng trong queue" in error for error in errors)


def test_snapshot_resolves_future_issue_numbers():
    plan = {"version": 1, "policy": {"planning_horizon_days": 1}, "topics": [topic("Networking")]}
    posts = [{"issue": 21, "axis": "Ôn tập", "title": "Bài 21"}]
    result = curriculum_planner.snapshot(plan, posts)
    assert result["next_issue"] == 22
    assert result["topics"][0]["issue"] == 22
