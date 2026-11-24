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
