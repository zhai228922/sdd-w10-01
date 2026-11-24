"""0B è² è²¬ï¼šå•†æ¥­è¦å‰‡å±¤ï¼ˆservice.pyï¼‰çš„æ¸¬è©¦ã€‚

ä¸Šé¢å…©å€‹æ˜¯è€å¸«çš„ç¯„ä¾‹ï¼›è«‹åœ¨ã€Œç¬¬ä¸€è¼ªã€ã€Œç¬¬äºŒè¼ªã€ä¸‹é¢åŠ ä¸Šä½ çš„æ¸¬è©¦ã€‚
æç¤ºï¼šservice çš„æ¯å€‹å‡½å¼éƒ½å›žå‚³ {"ok": ..., "message": ..., "data": ...}ï¼Œå¤§å¤šåªè¦æª¢æŸ¥ ["ok"]ã€‚
"""
import pytest

import service


# ---------------- ç¯„ä¾‹ï¼ˆè€å¸«æä¾›ï¼‰----------------
def test_report_found_normal(db):
    assert service.report_found(db, "é›¨å‚˜", "åœ–æ›¸é¤¨")["ok"] is True


@pytest.mark.parametrize("item_id, claimer, expected_ok", [
    (1, "çŽ‹å°æ˜Ž", True),      # æ­£å¸¸ï¼šèªé ˜ 1 è™Ÿ
    (99, "çŽ‹å°æ˜Ž", False),    # éŒ¯èª¤ï¼šæ²’æœ‰ 99 è™Ÿ
])
def test_claim(sample_db, item_id, claimer, expected_ok):
    assert service.claim(sample_db, item_id, claimer)["ok"] is expected_ok


# ---------------- ç¬¬ä¸€è¼ªï¼šè«‹å¾žé€™è£¡é–‹å§‹åŠ  ----------------
@pytest.mark.parametrize("category, location, expected_ok", [
    ("é›¨å‚˜", "åœ–æ›¸é¤¨", True),
    ("æ°´å£º", "é¤å»³", True),
    ("æœªçŸ¥ç‰©å“", "åœ–æ›¸é¤¨", False),
    ("é›¨å‚˜", "ç«æ˜Ÿ", False),
    (None, "åœ–æ›¸é¤¨", False),
])
def test_report_found_cases(db, category, location, expected_ok):
    res = service.report_found(db, category, location, "æ¸¬è©¦æè¿°")
    assert res["ok"] is expected_ok
    if expected_ok:
        assert "id" in res["data"]


def test_claim_without_item_id_fails(db):
    res = service.claim(db, None, "çŽ‹å°æ˜Ž")
    assert res["ok"] is False
    assert "ç·¨è™Ÿ" in res["message"]


def test_search_returns_matching_count(db):
    service.report_found(db, "é›¨å‚˜", "åœ–æ›¸é¤¨", "è—è‰²æŠ˜ç–Šå‚˜")
    service.report_found(db, "æ°´å£º", "é¤å»³", "ä¿æº«ç“¶")

    res_umbrella = service.search(db, category="é›¨å‚˜")
    assert res_umbrella["ok"] is True
    assert len(res_umbrella["data"]["items"]) == 1

    res_lib = service.search(db, location="åœ–æ›¸é¤¨")
    assert res_lib["ok"] is True
    assert len(res_lib["data"]["items"]) == 1


# ---------------- ç¬¬äºŒè¼ªï¼šé‚Šç•Œèˆ‡éŒ¯èª¤æƒ…æ³ ----------------
from config import MAX_CLAIMS_PER_PERSON


def test_search_requires_filter(db):
    res = service.search(db)
    assert res["ok"] is False


def test_search_no_match_returns_empty_list(db):
    res = service.search(db, category="é›¨å‚˜", location="åœ–æ›¸é¤¨")
    assert res["ok"] is True
    assert res["data"]["items"] == []


@pytest.mark.parametrize("bad_claimer", [None, "", "   "])
def test_claim_empty_claimer_fails(db, bad_claimer):
    r = service.report_found(db, "é›¨å‚˜", "åœ–æ›¸é¤¨", "é»‘å‚˜")
    res = service.claim(db, r["data"]["id"], bad_claimer)
    assert res["ok"] is False


def test_claim_already_claimed_fails(db):
    r = service.report_found(db, "é›¨å‚˜", "åœ–æ›¸é¤¨", "é»‘å‚˜")
    item_id = r["data"]["id"]
    assert service.claim(db, item_id, "çŽ‹å°æ˜Ž")["ok"] is True
    res2 = service.claim(db, item_id, "æŽå¤§è¯")
    assert res2["ok"] is False
    assert "å·²ç¶“è¢«èªé ˜" in res2["message"]


def test_claim_exceeds_max_limit(db):
    for i in range(MAX_CLAIMS_PER_PERSON):
        r = service.report_found(db, "é›¨å‚˜", "åœ–æ›¸é¤¨", f"å‚˜{i}")
        assert service.claim(db, r["data"]["id"], "çŽ‹å°æ˜Ž")["ok"] is True

    extra = service.report_found(db, "æ°´å£º", "é¤å»³", "å¤šå‡ºä¾†çš„æ°´å£º")
    res = service.claim(db, extra["data"]["id"], "çŽ‹å°æ˜Ž")
    assert res["ok"] is False
    assert "ä¸Šé™" in res["message"]


def test_stats_returns_rows(db):
    service.report_found(db, "é›¨å‚˜", "åœ–æ›¸é¤¨", "è—å‚˜")
    res = service.stats(db)
    assert res["ok"] is True
    assert "rows" in res["data"]


@pytest.mark.parametrize("empty_text", [None, "", "   "])
def test_handle_message_empty_input_fails(db, empty_text):
    res = service.handle_message(db, empty_text, "çŽ‹å°æ˜Ž", lambda p: "")
    assert res["ok"] is False


def test_handle_message_routes_with_mock_ai(db):
    # 1. ç™»è¨˜è·¯ç·š
    r1 = service.handle_message(db, "æˆ‘åœ¨åœ–æ›¸é¤¨æ’¿åˆ°é›¨å‚˜", "çŽ‹å°æ˜Ž", lambda p: "ç™»è¨˜|é›¨å‚˜|åœ–æ›¸é¤¨")
    assert r1["ok"] is True
    item_id = r1["data"]["id"]

    # 2. æŸ¥è©¢è·¯ç·š
    r2 = service.handle_message(db, "æ‰¾é›¨å‚˜", "çŽ‹å°æ˜Ž", lambda p: "æŸ¥è©¢|é›¨å‚˜|æœªçŸ¥")
    assert r2["ok"] is True
    assert len(r2["data"]["items"]) == 1

    # 3. èªé ˜è·¯ç·š
    r3 = service.handle_message(db, f"æˆ‘è¦èªé ˜ {item_id} è™Ÿ", "çŽ‹å°æ˜Ž", lambda p: "èªé ˜|æœªçŸ¥|æœªçŸ¥")
    assert r3["ok"] is True

    # 4. çœ‹ä¸æ‡‚è·¯ç·š
    r4 = service.handle_message(db, "ä»Šå¤©å¤©æ°£çœŸå¥½", "çŽ‹å°æ˜Ž", lambda p: "æœªçŸ¥|æœªçŸ¥|æœªçŸ¥")
    assert r4["ok"] is False

