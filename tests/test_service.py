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
from config import MAX_CLAIMS_PER_PERSON


def test_search_requires_filter(db):
    res = service.search(db)
    assert res["ok"] is False


def test_search_no_match_returns_empty_list(db):
    res = service.search(db, category="雨傘", location="圖書館")
    assert res["ok"] is True
    assert res["data"]["items"] == []


@pytest.mark.parametrize("bad_claimer", [None, "", "   "])
def test_claim_empty_claimer_fails(db, bad_claimer):
    r = service.report_found(db, "雨傘", "圖書館", "黑傘")
    res = service.claim(db, r["data"]["id"], bad_claimer)
    assert res["ok"] is False


def test_claim_already_claimed_fails(db):
    r = service.report_found(db, "雨傘", "圖書館", "黑傘")
    item_id = r["data"]["id"]
    assert service.claim(db, item_id, "王小明")["ok"] is True
    res2 = service.claim(db, item_id, "李大華")
    assert res2["ok"] is False
    assert "已經被認領" in res2["message"]


def test_claim_exceeds_max_limit(db):
    for i in range(MAX_CLAIMS_PER_PERSON):
        r = service.report_found(db, "雨傘", "圖書館", f"傘{i}")
        assert service.claim(db, r["data"]["id"], "王小明")["ok"] is True

    extra = service.report_found(db, "水壺", "餐廳", "多出來的水壺")
    res = service.claim(db, extra["data"]["id"], "王小明")
    assert res["ok"] is False
    assert "上限" in res["message"]


def test_stats_returns_rows(db):
    service.report_found(db, "雨傘", "圖書館", "藍傘")
    res = service.stats(db)
    assert res["ok"] is True
    assert "rows" in res["data"]


@pytest.mark.parametrize("empty_text", [None, "", "   "])
def test_handle_message_empty_input_fails(db, empty_text):
    res = service.handle_message(db, empty_text, "王小明", lambda p: "")
    assert res["ok"] is False


def test_handle_message_routes_with_mock_ai(db):
    # 1. 登記路線
    fake_report_ai = lambda prompt: '{"action": "登記", "category": "雨傘", "location": "圖書館", "item_id": null}'
    r1 = service.handle_message(db, "我在圖書館撿到雨傘", "王小明", fake_report_ai)
    assert r1["ok"] is True
    item_id = r1["data"]["id"]

    # 2. 查詢路線
    fake_search_ai = lambda prompt: '{"action": "查詢", "category": "雨傘", "location": "未知", "item_id": null}'
    r2 = service.handle_message(db, "找雨傘", "王小明", fake_search_ai)
    assert r2["ok"] is True
    assert len(r2["data"]["items"]) == 1

    # 3. 認領路線
    fake_claim_ai = lambda prompt: f'{{"action": "認領", "category": "未知", "location": "未知", "item_id": {item_id}}}'
    r3 = service.handle_message(db, f"我要認領 {item_id} 號", "王小明", fake_claim_ai)
    assert r3["ok"] is True

    # 4. 看不懂路線
    fake_unknown_ai = lambda prompt: '{"action": "其他", "category": "未知", "location": "未知", "item_id": null}'
    r4 = service.handle_message(db, "今天天氣真好", "王小明", fake_unknown_ai)
    assert r4["ok"] is False
