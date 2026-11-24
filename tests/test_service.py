"""0B 負責：商業規則層（service.py）的測試。

上面兩個是老師的範例；請在「第一輪」「第二輪」下面加上你的測試。
提示：service 的每個函式都回傳 {"ok": ..., "message": ..., "data": ...}，大多只要檢查 ["ok"]。
"""
import pytest

import service


# ---------------- 範例（老師提供）----------------
def test_report_found_normal(db):
    assert service.report_found(db, "雨傘", "圖書館")["ok"] is True


@pytest.mark.parametrize("item_id, claimer, expected_ok", [
    (1, "王小明", True),      # 正常：認領 1 號
    (99, "王小明", False),    # 錯誤：沒有 99 號
])
def test_claim(sample_db, item_id, claimer, expected_ok):
    assert service.claim(sample_db, item_id, claimer)["ok"] is expected_ok


# ---------------- 第一輪：請從這裡開始加 ----------------
@pytest.mark.parametrize("category, location, expected_ok", [
    ("雨傘", "圖書館", True),
    ("水壺", "餐廳", True),
    ("未知物品", "圖書館", False),
    ("雨傘", "火星", False),
    (None, "圖書館", False),
])
def test_report_found_cases(db, category, location, expected_ok):
    res = service.report_found(db, category, location, "測試描述")
    assert res["ok"] is expected_ok
    if expected_ok:
        assert "id" in res["data"]


def test_claim_without_item_id_fails(db):
    res = service.claim(db, None, "王小明")
    assert res["ok"] is False
    assert "編號" in res["message"]


def test_search_returns_matching_count(db):
    service.report_found(db, "雨傘", "圖書館", "藍色折疊傘")
    service.report_found(db, "水壺", "餐廳", "保溫瓶")

    res_umbrella = service.search(db, category="雨傘")
    assert res_umbrella["ok"] is True
    assert len(res_umbrella["data"]["items"]) == 1

    res_lib = service.search(db, location="圖書館")
    assert res_lib["ok"] is True
    assert len(res_lib["data"]["items"]) == 1


# ---------------- 第二輪：邊界與錯誤情況 ----------------
