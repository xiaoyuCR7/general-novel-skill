#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_tracking_delta.py — 写后事实增量的证据核对。"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tracking_delta as td

CHAPTER = (
    "# 第3章 旧账\n\n"
    "陈墨把那枚铜扣压在账本底下，没有交给师兄。\n\n"
    "“你昨晚去过库房。”师兄说。\n\n"
    "他点了头，把库房钥匙放回桌上。\n"
)
LEDGER = "| F1-03 | 铜扣的来历 | 3 | 12 | 师兄认出 | 3 |\n"


def make_delta(**overrides):
    delta = {
        "version": 1,
        "chapter": 3,
        "title": "旧账",
        "summary": {
            "发生了什么": "陈墨承认去过库房，但藏下了铜扣。",
            "状态变化": "陈墨交还库房钥匙。",
            "伏笔进出": "埋 F1-03",
            "新登场": "N/A",
            "关键实体": ["陈墨", "铜扣", "库房"],
            "承上": "N/A",
            "启下": "师兄是否发现铜扣",
        },
        "claims": [
            {"table": "角色状态", "subject": "陈墨", "change": "不再持有库房钥匙",
             "evidence": "把库房钥匙放回桌上"},
            {"table": "伏笔台账", "subject": "F1-03 铜扣", "change": "新埋",
             "evidence": "把那枚铜扣压在账本底下，\n没有交给师兄"},
        ],
    }
    delta.update(overrides)
    return delta


class TestCheckDelta(unittest.TestCase):
    def codes(self, delta, ledger=LEDGER):
        errors, warnings = td.check_delta(delta, CHAPTER, ledger)
        return [c for c, _ in errors], [c for c, _ in warnings]

    def test_supported_delta_passes_and_ignores_whitespace_in_evidence(self):
        self.assertEqual(self.codes(make_delta()), ([], []))

    def test_invented_evidence_is_an_error(self):
        delta = make_delta()
        delta["claims"][0]["evidence"] = "他把钥匙扔进了井里"
        self.assertEqual(self.codes(delta)[0], ["evidence_not_found"])

    def test_too_short_evidence_cannot_locate_a_fact(self):
        delta = make_delta()
        delta["claims"][0]["evidence"] = "钥匙"
        self.assertEqual(self.codes(delta)[0], ["evidence_too_short"])

    def test_key_entity_must_appear_verbatim(self):
        delta = make_delta()
        delta["summary"]["关键实体"].append("藏经阁")
        self.assertEqual(self.codes(delta)[0], ["entity_not_in_chapter"])

    def test_ledger_claim_needs_registered_id(self):
        delta = make_delta()
        delta["claims"][1]["subject"] = "铜扣"
        self.assertEqual(self.codes(delta)[0], ["ledger_id_missing"])
        self.assertEqual(self.codes(make_delta(), ledger="")[0], ["ledger_id_not_registered"])

    def test_state_change_without_character_claim_is_only_a_warning(self):
        delta = make_delta()
        delta["claims"] = delta["claims"][1:]
        self.assertEqual(self.codes(delta), ([], ["state_change_without_claim"]))


class TestLoadDelta(unittest.TestCase):
    def load(self, delta):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "delta.json"
            path.write_text(json.dumps(delta, ensure_ascii=False), encoding="utf-8")
            return td.load_delta(str(path))

    def test_valid_delta_loads(self):
        self.assertEqual(self.load(make_delta())["chapter"], 3)

    def test_structural_problems_are_rejected(self):
        bad_table = make_delta()
        bad_table["claims"][0]["table"] = "人物小传"
        empty_field = make_delta()
        empty_field["summary"]["承上"] = ""
        for delta in (make_delta(version=2), make_delta(chapter=0), bad_table, empty_field):
            with self.subTest(delta=delta):
                with self.assertRaises(td.DeltaError):
                    self.load(delta)


class TestApplySummary(unittest.TestCase):
    BASE = "# 章节摘要\n\n## 卷级概述\n\n## 近 10 章详记\n\n### 第2章 夜探\n\n- 发生了什么：旧条目\n"

    def test_appends_new_chapter_inside_recent_section(self):
        text, action = td.apply_summary(make_delta(), self.BASE + "\n## 附录\n\n备注\n")
        self.assertEqual(action, "appended")
        self.assertLess(text.index("### 第2章"), text.index("### 第3章 旧账"))
        self.assertLess(text.index("### 第3章 旧账"), text.index("## 附录"))
        self.assertIn("- 关键实体：陈墨，铜扣，库房", text)

    def test_replaces_existing_entry_without_duplicating(self):
        existing = self.BASE + "\n### 第3章 旧稿\n\n- 发生了什么：过期内容\n\n### 第4章 后续\n\n- 发生了什么：保留\n"
        text, action = td.apply_summary(make_delta(), existing)
        self.assertEqual(action, "replaced")
        self.assertEqual(text.count("### 第3章"), 1)
        self.assertNotIn("过期内容", text)
        self.assertIn("### 第4章 后续", text)

    def test_chapter_number_prefix_does_not_match_longer_number(self):
        existing = self.BASE + "\n### 第30章 远期\n\n- 发生了什么：保留\n"
        text, action = td.apply_summary(make_delta(), existing)
        self.assertEqual(action, "appended")
        self.assertIn("### 第30章 远期", text)

    def test_missing_recent_section_is_an_error(self):
        with self.assertRaises(td.DeltaError):
            td.apply_summary(make_delta(), "# 章节摘要\n")


class TestCli(unittest.TestCase):
    def test_check_exit_codes_and_apply_writes_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "delta.json").write_text(json.dumps(make_delta(), ensure_ascii=False), encoding="utf-8")
            (root / "chapter.md").write_text(CHAPTER, encoding="utf-8")
            (root / "ledger.md").write_text(LEDGER, encoding="utf-8")
            (root / "summary.md").write_text(TestApplySummary.BASE, encoding="utf-8")
            check = ["check", str(root / "delta.json"), "--chapter-file", str(root / "chapter.md")]
            self.assertEqual(td.main(check + ["--ledger", str(root / "ledger.md")]), 0)
            (root / "chapter.md").write_text("# 第3章\n\n无关内容。\n", encoding="utf-8")
            self.assertEqual(td.main(check), 1)
            self.assertEqual(td.main(["check", str(root / "missing.json"), "--chapter-file",
                                      str(root / "chapter.md")]), 2)
            self.assertEqual(td.main(["apply-summary", str(root / "delta.json"),
                                      "--summary-file", str(root / "summary.md")]), 0)
            self.assertIn("### 第3章 旧账", (root / "summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
