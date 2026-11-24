"""0A 負責：資料存取層（repository.py）的測試。

上面兩個是老師的範例；請在「第一輪」「第二輪」下面加上你的測試。
提示：sample_db 裡有 1 號雨傘（圖書館）、2 號水壺（餐廳）、3 號雨傘（教室）。
"""
import pytest

import repository


# ---------------- 範例（老師提供）----------------
def test_add_item_returns_new_id(db):
    assert repository.add_item(db, "雨傘", "圖書館", "黑傘") == 1


def test_get_item_not_found_returns_none(db):
    assert repository.get_item(db, 99) is None


# ---------------- 第一輪：請從這裡開始加 ----------------
def test_get_item_returns_expected_fields(sample_db):
    item = repository.get_item(sample_db, 2)
    assert item is not None
    assert item["category"] == "水壺"
    assert item["location"] == "餐廳"
    assert item["status"] == "待認領"
    assert item["claimer"] is None


def test_find_items_by_category_umbrella(sample_db):
    items = repository.find_items(sample_db, category="雨傘")
    assert [it["id"] for it in items] == [1, 3]


def test_mark_claimed_updates_status(sample_db):
    assert repository.mark_claimed(sample_db, 1, "王小明") is True
    item = repository.get_item(sample_db, 1)
    assert item["status"] == "已認領"


# ---------------- 第二輪：邊界與錯誤情況 ----------------
# 測試 P-R1 與想一想：統計表必須保留沒有物品的類別（如鑰匙），且雨傘的總件數/待認領/已認領統計正確
def test_category_stats_keeps_empty_categories_and_counts(sample_db):
    repository.mark_claimed(sample_db, 1, "王小明")
    stats = {row["類別"]: row for row in repository.category_stats(sample_db)}
    assert "鑰匙" in stats
    assert stats["鑰匙"] == {"類別": "鑰匙", "總件數": 0, "待認領": 0, "已認領": 0}
    assert stats["雨傘"] == {"類別": "雨傘", "總件數": 2, "待認領": 1, "已認領": 1}


# 測試 P-R2 與想一想：已經被認領的物品，在查詢時必須被排除
def test_find_items_excludes_claimed_items(sample_db):
    repository.mark_claimed(sample_db, 1, "王小明")
    items = repository.find_items(sample_db, category="雨傘")
    assert [it["id"] for it in items] ==[3]



# 測試 P-R3 與想一想：同一件已認領的物品不能再次被標記為已認領
def test_mark_claimed_twice_returns_false(sample_db):
    assert repository.mark_claimed(sample_db, 1, "王小明") is True
    assert repository.mark_claimed(sample_db, 1, "李小華") is False
    assert repository.get_item(sample_db, 1)["claimer"] == "王小明"


# 測試想一想：同時指定類別與地點進行複合查詢
def test_find_items_by_category_and_location(sample_db):
    items = repository.find_items(sample_db, category="雨傘", location="教室")
    assert [it["id"] for it in items] ==[3]



# 測試想一想：count_claimed_by 對有認領過的人與沒認領過的人回傳正確件數
def test_count_claimed_by_user(sample_db):
    assert repository.count_claimed_by(sample_db, "王小明") == 0
    repository.mark_claimed(sample_db, 1, "王小明")
    repository.mark_claimed(sample_db, 2, "王小明")
    assert repository.count_claimed_by(sample_db, "王小明") == 2
    assert repository.count_claimed_by(sample_db, "沒認領過的人") == 0
