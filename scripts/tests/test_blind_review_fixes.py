#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_blind_review_fixes.py — 匿名盲评测试暴露问题的回归用例。"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import chapter_transaction as transaction
import check_text
from context_manager import extract_mentioned_characters


class TestCastParsing(unittest.TestCase):
    def cast(self, line):
        with tempfile.TemporaryDirectory() as directory:
            outline = "# 第1章\n\n## 出场人物\n\n" + line + "\n\n## 硬约束\n"
            return extract_mentioned_characters(outline, Path(directory))

    def test_parenthetical_note_is_not_part_of_the_name(self):
        self.assertEqual(self.cast("- 主要：陈默、吴桂芝（独居老太太，七十一岁）"), ["陈默", "吴桂芝"])

    def test_off_page_people_are_not_required_cast(self):
        self.assertEqual(self.cast("- 次要：订单顾客（只在电话里）、刘姐(微信提及)、老周（回忆）"), [])
        self.assertEqual(self.cast("- 次要：老秦（站长）、急救员（龙套）"), ["老秦"])


class TestNotReadyPacket(unittest.TestCase):
    def test_refused_selection_is_reported_as_not_ready_not_malformed(self):
        from context_manager import verify_context
        packet = {"ready": False, "errors": ["transaction_incomplete"], "components": {},
                  "source_manifest": [], "package_sha256": "0" * 64}
        with tempfile.TemporaryDirectory() as directory:
            result = verify_context(Path(directory), packet)
        self.assertEqual(result["status"], "not_ready")
        self.assertEqual(result["errors"], ["packet_not_ready: transaction_incomplete"])
        self.assertFalse(result["ready"])


class TestDashboardFacts(unittest.TestCase):
    LEDGER = "\n".join([
        "## 🟡 活跃", "", "| ID | 伏笔内容 | 埋设章节 | 预期回收 |", "|---|---|---|---|",
        "| F1-02 | 头顶的数 | 第1章 | 第8章 |", "",
        "## ✅ 已回收（归档）", "", "| ID | 伏笔内容 | 埋设章节 | 回收章节 |", "|---|---|---|---|",
        "| F1-03 | 钥匙 | 第1章 | 第2章 |", "",
    ])

    def test_status_counts_written_chapters_and_reads_titles_and_ledger(self):
        import dashboard
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory) / "book"
            for sub in ("正文", "大纲", "追踪"):
                (book / sub).mkdir(parents=True)
            (book / "正文" / "第001章.md").write_text("第1章 十七分钟\n\n雨下得很大。\n", encoding="utf-8")
            (book / "大纲" / "章纲_第005章.md").write_text("# 章纲：第5章\n", encoding="utf-8")
            (book / "追踪" / "伏笔台账.md").write_text(self.LEDGER, encoding="utf-8")
            status = dashboard._collect_status(book)
            self.assertEqual(status["last_chapter"], 1)
            self.assertEqual(status["total_chars"], len("雨下得很大。"))
            self.assertEqual(status["foreshadow_count"], 2)
            chapters = dashboard._collect_chapters(book)
            self.assertEqual(chapters[0]["title"], "第1章 十七分钟")
            ledger = dashboard._collect_foreshadowing(book)
            self.assertEqual([(e["id"], e["state"], e["planted_ch"], e["recycled_ch"]) for e in ledger],
                             [("F1-02", "激活", 1, None), ("F1-03", "回收", 1, 2)])
            self.assertEqual(ledger[0]["content"], "头顶的数")


class TestOutlineLock(unittest.TestCase):
    def make_book(self, directory, outline_text):
        book = Path(directory) / "book"
        for sub in ("正文", "大纲", "追踪", "设定"):
            (book / sub).mkdir(parents=True)
        (book / "大纲" / "章纲_第001章.md").write_text(outline_text, encoding="utf-8")
        return book

    def test_unlocked_outline_blocks_prepare_until_locked_or_authorized(self):
        with tempfile.TemporaryDirectory() as directory:
            book = self.make_book(directory, "# 第1章\n\n> 提案，未锁定\n")
            before = transaction.book_hashes(book)
            with self.assertRaisesRegex(transaction.TransactionError, "outline_unlocked"):
                transaction.prepare(book, 1)
            self.assertEqual(transaction.book_hashes(book), before)
            self.assertIsNone(transaction.pending_transaction(book))
            journal = transaction.prepare(book, 1, allow_unlocked_outline=True)
            self.assertEqual(journal["status"], "prepared")

    def test_locked_outline_and_other_chapters_do_not_block(self):
        with tempfile.TemporaryDirectory() as directory:
            book = self.make_book(directory, "# 第1章\n\n> 已锁定\n")
            (book / "大纲" / "章纲_第010章.md").write_text("> 提案，未锁定\n", encoding="utf-8")
            self.assertIsNone(transaction.unlocked_outline(book, 1))
            self.assertEqual(transaction.unlocked_outline(book, 10), "大纲/章纲_第010章.md")
            self.assertEqual(transaction.prepare(book, 1)["status"], "prepared")


class TestBodyCharCount(unittest.TestCase):
    def run_cli(self, text, *args):
        with tempfile.TemporaryDirectory() as directory:
            chapter = Path(directory) / "第001章.md"
            chapter.write_text(text, encoding="utf-8")
            output = io.StringIO()
            argv = sys.argv
            sys.argv = ["check_text.py", str(chapter), "--no-auto-words", *args]
            try:
                with redirect_stdout(output):
                    try:
                        code = check_text.main()
                    except SystemExit as exc:
                        code = exc.code
            finally:
                sys.argv = argv
            return code, output.getvalue()

    def test_title_line_is_not_counted(self):
        body = "雨落在瓦上，他把车停进车棚。" * 2
        code, output = self.run_cli("第1章 很长很长很长的标题\n\n" + body + "\n", "--max-chars", str(len(body)))
        self.assertIn("字数：{}（".format(len(body)), output)
        self.assertNotIn("字数超限", output)
        self.assertIn(code, (0, None))


class TestNarrationAdvisories(unittest.TestCase):
    FILLER = "他把车停进车棚，拎着袋子上了五楼，楼道里的灯坏了小半年。\n\n" * 12

    def ids(self, text):
        return [h[0] for h in check_text.scan_density(text, len(text))]

    def test_narrator_gloss_flagged_when_clustered(self):
        gloss = ("数只管还剩多久，从来不管人是怎么没的。\n\n就是这个了，一把会扑锅的壶。\n\n"
                 "他愣了两秒才转过弯来。\n\n这种数他见多了，从来不管。\n\n")
        self.assertIn("narrator-gloss-tic", self.ids("第1章 旧账\n\n" + gloss + self.FILLER))
        self.assertNotIn("narrator-gloss-tic", self.ids("第1章 旧账\n\n就是这个了。\n\n" + self.FILLER))

    def test_readouts_and_dialogue_are_not_narrator_gloss(self):
        text = "第1章 旧账\n\n" + "她头顶：00:16:40。\n\n“你从来不听我的。”她说。\n\n" * 5 + self.FILLER
        self.assertNotIn("narrator-gloss-tic", self.ids(text))

    def test_one_line_paragraphs_flagged_by_share_not_by_presence(self):
        fragmented = "第1章 旧账\n\n" + "十七分钟。\n\n行吧。\n\n" * 6 + self.FILLER
        self.assertIn("one-line-paragraph-tic", self.ids(fragmented))
        occasional = "第1章 旧账\n\n十七分钟。\n\n行吧。\n\n" + self.FILLER * 2
        self.assertNotIn("one-line-paragraph-tic", self.ids(occasional))

    def test_short_dialogue_lines_do_not_count_as_one_line_paragraphs(self):
        dialogue = "第1章 旧账\n\n" + "“走。”\n\n“好。”\n\n" * 10 + self.FILLER
        self.assertNotIn("one-line-paragraph-tic", self.ids(dialogue))


if __name__ == "__main__":
    unittest.main()
