#!/usr/bin/env python3
"""Self-check for gh_project.py's pure logic (no subprocess/network)."""

from gh_project import UsageError, find_item_id, find_status_option, pick_active_project

FIELDS = [
    {"id": "PVTF_1", "name": "Title", "type": "ProjectV2Field"},
    {
        "id": "PVTSSF_1",
        "name": "Status",
        "type": "ProjectV2SingleSelectField",
        "options": [
            {"id": "f75ad846", "name": "Backlog"},
            {"id": "61e4505c", "name": "Ready"},
            {"id": "47fc9ee4", "name": "In progress"},
            {"id": "df73e18b", "name": "In review"},
            {"id": "98236657", "name": "Done"},
        ],
    },
]

ITEMS = [
    {"id": "PVTI_1", "content": {"number": 2, "type": "Issue"}, "status": "Done"},
    {"id": "PVTI_2", "content": {"number": 1, "type": "Issue"}, "status": "Done"},
]

ONE_OPEN = [{"number": 1, "title": "Roadmap", "closed": False, "id": "PVT_1"}]
NONE_OPEN = [{"number": 1, "title": "Old", "closed": True, "id": "PVT_1"}]
TWO_OPEN = [
    {"number": 1, "title": "A", "closed": False, "id": "PVT_1"},
    {"number": 2, "title": "B", "closed": False, "id": "PVT_2"},
]


def expect_usage_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except UsageError as e:
        return str(e)
    raise AssertionError(f"expected UsageError from {fn.__name__}{args}")


def test_pick_active_project():
    assert pick_active_project(ONE_OPEN)["number"] == 1
    expect_usage_error(pick_active_project, NONE_OPEN)
    expect_usage_error(pick_active_project, TWO_OPEN)
    assert pick_active_project(TWO_OPEN, explicit_number=2)["title"] == "B"
    expect_usage_error(pick_active_project, ONE_OPEN, explicit_number=99)


def test_find_status_option():
    field_id, option_id = find_status_option(FIELDS, "ready")
    assert field_id == "PVTSSF_1"
    assert option_id == "61e4505c"
    msg = expect_usage_error(find_status_option, FIELDS, "nope")
    assert "Backlog" in msg


def test_find_item_id():
    assert find_item_id(ITEMS, 2) == "PVTI_1"
    expect_usage_error(find_item_id, ITEMS, 999)


def main():
    test_pick_active_project()
    test_find_status_option()
    test_find_item_id()
    print("ok")


if __name__ == "__main__":
    main()
