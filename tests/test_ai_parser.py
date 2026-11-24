"""0C 負責：AI 解讀層（ai_parser.py）的測試。

這一層不呼叫真的 AI：直接把「AI 可能的回覆」交給 parse_reply()，檢查整理出來的欄位。
上面兩個是老師的範例；請在「第一輪」「第二輪」下面加上你的測試。
"""
import pytest

import ai_parser


# ---------------- 範例（老師提供）----------------
def test_parse_standard_reply():
    result = ai_parser.parse_reply("登記|雨傘|圖書館", "我在圖書館撿到一把傘")
    assert result["action"] == "登記"
    assert result["category"] == "雨傘"


@pytest.mark.parametrize("reply, user_text, field, expected", [
    ("", "隨便說說", "action", "未知"),          # AI 沒回覆
])
def test_parse_reply_fields(reply, user_text, field, expected):
    assert ai_parser.parse_reply(reply, user_text)[field] == expected


# ---------------- 第一輪：請從這裡開始加 ----------------
@pytest.mark.parametrize("reply, user_text, expected", [
    # 1. 標準查詢回覆，包含地點與類別
    ("查詢|水壺|餐廳", "我的水壺好像掉在餐廳",
     {"action": "查詢", "category": "水壺", "location": "餐廳", "item_id": None}),
    # 2. 不在允許清單的值（如「飛機」、「火星」）一律轉為「未知」
    ("登記|飛機|火星", "我在火星撿到一台飛機",
     {"action": "登記", "category": "未知", "location": "未知", "item_id": None}),
    # 3. 安全網：item_id 只從 user_text 抓，不採用 AI 回覆中的數字
    ("認領|耳機|教室|99", "我要認領第 3 號耳機",
     {"action": "認領", "category": "耳機", "location": "教室", "item_id": 3}),
    # 4. 格式不完整（少於三欄）時，缺少的欄位補「未知」
    ("查詢", "我想找東西",
     {"action": "查詢", "category": "未知", "location": "未知", "item_id": None}),
])
def test_round1_parse_reply_cases(reply, user_text, expected):
    assert ai_parser.parse_reply(reply, user_text) == expected


# ---------------- 第二輪：邊界與錯誤情況 ----------------
"""0C 負責：AI 解讀層（ai_parser.py）的測試。

這一層不呼叫真的 AI：直接把「AI 可能的回覆」交給 parse_reply()，檢查整理出來的欄位。
上面兩個是老師的範例；請在「第一輪」「第二輪」下面加上你的測試。
"""
import pytest

import ai_parser


# ---------------- 範例（老師提供）----------------
def test_parse_standard_reply():
    result = ai_parser.parse_reply("登記|雨傘|圖書館", "我在圖書館撿到一把傘")
    assert result["action"] == "登記"
    assert result["category"] == "雨傘"


@pytest.mark.parametrize("reply, user_text, field, expected", [
    ("", "隨便說說", "action", "未知"),          # AI 沒回覆
])
def test_parse_reply_fields(reply, user_text, field, expected):
    assert ai_parser.parse_reply(reply, user_text)[field] == expected


# ---------------- 第一輪：請從這裡開始加 ----------------
@pytest.mark.parametrize("reply, user_text, expected", [
    # 1. 標準查詢回覆，包含地點與類別
    ("查詢|水壺|餐廳", "我的水壺好像掉在餐廳",
     {"action": "查詢", "category": "水壺", "location": "餐廳", "item_id": None}),
    # 2. 不在允許清單的值（如「飛機」、「火星」）一律轉為「未知」
    ("登記|飛機|火星", "我在火星撿到一台飛機",
     {"action": "登記", "category": "未知", "location": "未知", "item_id": None}),
    # 3. 安全網：item_id 只從 user_text 抓，不採用 AI 回覆中的數字
    ("認領|耳機|教室|99", "我要認領第 3 號耳機",
     {"action": "認領", "category": "耳機", "location": "教室", "item_id": 3}),
    # 4. 格式不完整（少於三欄）時，缺少的欄位補「未知」
    ("查詢", "我想找東西",
     {"action": "查詢", "category": "未知", "location": "未知", "item_id": None}),
])
def test_round1_parse_reply_cases(reply, user_text, expected):
    assert ai_parser.parse_reply(reply, user_text) == expected


# ---------------- 第二輪：邊界與錯誤情況 ----------------
@pytest.mark.parametrize("reply, user_text, expected", [
    # 1. AI 回傳 None 時，不崩潰且全部回傳「未知」
    (None, "我的學生證不見了",
     {"action": "未知", "category": "未知", "location": "未知", "item_id": None}),
    # 2. AI 多話夾雜廢話或換行時，仍能從欄位中抽出允許清單內的關鍵字
    ("好的，這應該是登記沒錯|是一張學生證喔|好像在體育館\n", "在體育館撿到學生證",
     {"action": "登記", "category": "學生證", "location": "體育館", "item_id": None}),
    # 3. 使用者原話包含多個數字時，安全網抓第一個數字作為 item_id
    ("認領|雨傘|未知", "我是大2學生，要認領 15 號雨傘",
     {"action": "認領", "category": "雨傘", "location": "未知", "item_id": 2}),
])
def test_round2_edge_cases(reply, user_text, expected):
    assert ai_parser.parse_reply(reply, user_text) == expected


def test_round2_parse_message_with_fake_and_keyword_ask():
    # 測試 make_fake_ask 與 parse_message 串接
    fake_ask = ai_parser.make_fake_ask({"我要認領 7 號水壺": "認領|水壺|未知"})
    assert ai_parser.parse_message("我要認領 7 號水壺", fake_ask) == {
        "action": "認領",
        "category": "水壺",
        "location": "未知",
        "item_id": 7,
    }
    # 不在對照表內的輸入會回空字串，整理後全為「未知」
    assert ai_parser.parse_message("完全沒看過的句子", fake_ask)["action"] == "未知"

