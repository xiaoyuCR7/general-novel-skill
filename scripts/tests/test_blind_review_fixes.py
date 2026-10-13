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


class TestOutlinePlanRhythm(unittest.TestCase):
    QUOTA = "\n".join([
        "## A/B/C 配额记录", "", "| 章节 | 配额 | 触发内容 |", "|---|---|---|", "| 第1章 | A | 开局 |", "",
        "## 事件冷却记录", "", "| 章节 | 事件类型 | 事件内容 |", "|---|---|---|", "| 第1章 | crisis | 开局 |", "",
        "## 档位记录", "", "| 章节 | 档位 |", "|---|---|", "| 第1章 | 中 |", "",
    ])

    def outline(self, event):
        return "\n".join(["## 基本信息", "", "- 节奏档位：中档", "- A/B/C 配额预声明：不触发",
                          "- 事件类型：" + event, ""])

    def run_plan(self, events):
        import rhythm_guard
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "quota.md").write_text(self.QUOTA, encoding="utf-8")
            (root / "大纲").mkdir()
            for chapter, event in events.items():
                (root / "大纲" / "章纲_第{:03d}章.md".format(chapter)).write_text(self.outline(event), encoding="utf-8")
            records = rhythm_guard.parse_quota_file(str(root / "quota.md"))
            output = io.StringIO()
            with redirect_stdout(output):
                code = rhythm_guard.check_outline_plan(records, str(root / "大纲"))
            return code, output.getvalue(), (root / "quota.md").read_text(encoding="utf-8")

    def test_batch_catches_cooldown_between_planned_chapters_without_writing(self):
        code, output, quota_after = self.run_plan({2: "world", 3: "bond", 4: "bond"})
        self.assertEqual(code, 1)
        self.assertIn("第4章", output)
        self.assertIn("bond 第3章触发", output)
        self.assertEqual(quota_after, self.QUOTA)

    def test_compatible_batch_passes_and_recorded_chapters_are_skipped(self):
        code, output, _ = self.run_plan({1: "bond", 2: "world", 3: "bond"})
        self.assertEqual(code, 0)
        self.assertNotIn("第1章：", output)


class TestTimelineSameDay(unittest.TestCase):
    def issues(self, second_desc):
        import timeline_manager
        text = "\n".join([
            "## 时间锚点", "", "| 编号 | 标签 | 时间表达式 |", "|---|---|---|", "| A1 | 起点 | 第1天 |", "",
            "## 第 1 卷", "", "| 章节 | 故事内时间 | 事件 | 时间标记/约定 |", "|---|---|---|---|",
            "| 第1章 | @A1+1（第2天 00:07 至 01:57） | 甲 | 无 |",
            "| 第2章 | " + second_desc + " | 乙 | 无 |", "",
        ])
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory) / "book"
            (book / "追踪").mkdir(parents=True)
            (book / "追踪" / "时间线.md").write_text(text, encoding="utf-8")
            output = io.StringIO()
            argv = sys.argv
            sys.argv = ["timeline_manager.py", "check", str(book)]
            try:
                with redirect_stdout(output):
                    try:
                        timeline_manager.main()
                    except SystemExit:
                        pass
            finally:
                sys.argv = argv
            return output.getvalue()

    def test_same_day_with_different_clock_times_is_sequential(self):
        self.assertNotIn("C5_branch_time_conflict", self.issues("@A1+1（第2天 02:00 至 08:40）"))

    def test_same_day_without_clock_times_still_warns(self):
        self.assertIn("C5_branch_time_conflict", self.issues("@A1+1（第2天，另一条线）"))


class TestTimelineScaling(unittest.TestCase):
    """百万字规模下，时间线的活跃部分不随章数增长，未了结的约定不因为旧而丢失。"""

    HEADER = ["# 时间线", "", "## 时间锚点", "", "| 编号 | 标签 | 时间表达式 |", "|---|---|---|",
              "| A1 | 开局 | 第1天 |", "", "## 第 1 卷", "",
              "| 章节 | 故事内时间 | 事件 | 时间标记/约定 |", "|---|---|---|---|"]

    def timeline(self, chapters):
        rows = []
        for n in range(1, chapters + 1):
            promise = "无"
            if n == 30:
                promise = "三年之约：第三年冬至回山"
            elif n == 40:
                promise = "十日后交货；约定已兑现"
            elif n == 55:
                promise = "闪回；依据：世界观第三条"
            rows.append("| 第{}章 | @A1+{} | 事件{} | {} |".format(n, n, n, promise))
        return "\n".join(self.HEADER + rows) + "\n"

    def test_only_recent_open_and_cited_rows_are_kept(self):
        import context_manager as cm
        text, stats = cm._select_timeline_rows(self.timeline(800), 801, "本章回到 @A1 那天，并呼应第120章的雪夜。")
        self.assertIn("| A1 | 开局 | 第1天 |", text)
        self.assertIn("三年之约", text)
        self.assertIn("| 第120章 |", text)
        self.assertIn("| 第791章 |", text)
        self.assertIn("| 第800章 |", text)
        for dropped in ("| 第40章 |", "| 第55章 |", "| 第500章 |", "| 第790章 |"):
            self.assertNotIn(dropped, text)
        self.assertIn("已省略", text)
        self.assertEqual(stats["kept_open_commitments"], 1)
        self.assertEqual(stats["kept_cited_by_outline"], 1)
        self.assertEqual(stats["kept"] + stats["omitted"], 800)
        self.assertLess(len(text), len(self.timeline(800)) // 20)

    def test_small_books_and_unknown_text_are_untouched(self):
        import context_manager as cm
        short = self.timeline(8)
        self.assertEqual(cm._select_timeline_rows(short, 9)[0], short)
        legacy = "# 时间线\n第3章：铜门只能由两人同时开启。\n" * 50
        self.assertEqual(cm._select_timeline_rows(legacy, 400)[0], legacy)

    def test_selected_size_does_not_grow_with_chapter_count(self):
        import context_manager as cm
        small = len(cm._select_timeline_rows(self.timeline(200), 201)[0])
        large = len(cm._select_timeline_rows(self.timeline(2000), 2001)[0])
        self.assertLess(large - small, 200)

    def test_archive_candidate_keeps_open_commitments_active(self):
        import context_manager as cm
        import timeline_manager as tm
        candidate = tm.build_archive_candidate(self.timeline(60), 50)
        self.assertEqual(len(candidate["open"]), 1)
        self.assertIn("三年之约", candidate["open"][0])
        self.assertEqual(candidate["archived"], 49)
        text = candidate["text"]
        self.assertIn("## 当前时间位置", text)
        self.assertIn("截至第50章：@A1+50", text)
        self.assertLess(text.index("## 未完成的约定与期限"), text.index("## 历史记录（第50章及以前，已归档）"))
        selection = cm._tracking_selection(text, "timeline")
        self.assertIn("三年之约", selection["content"])
        self.assertIn("| 第60章 |", selection["content"])
        self.assertNotIn("| 第20章 |", selection["content"])
        self.assertGreater(selection["omitted_chars"], 0)
        self.assertEqual(len(tm.parse_timeline(text)["chapters"]), 60)
        self.assertIsNone(tm.build_archive_candidate(self.timeline(5), 0))


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


class TestLinkedParentDirectory(unittest.TestCase):
    """书籍之上的目录带链接（macOS 的 /var、搬到别的盘的文件夹）不应让书被拒读。"""

    DEMO = SCRIPT_DIR.parent / "demo" / "看见倒计时的骑手"

    def setUp(self):
        import os
        import shutil
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.base = Path(os.path.realpath(holder.name))
        self.book = self.base / "real" / "book"
        shutil.copytree(str(self.DEMO), str(self.book),
                        ignore=shutil.ignore_patterns(".chapter-transaction*"))
        self.alias = self.link(self.base / "alias", self.base / "real")

    def link(self, link, target):
        import os
        try:
            if os.name == "nt":
                import _winapi
                _winapi.CreateJunction(str(target), str(link))
                self.addCleanup(os.rmdir, str(link))
            else:
                os.symlink(str(target), str(link), target_is_directory=True)
                self.addCleanup(os.unlink, str(link))
        except (OSError, NotImplementedError) as exc:
            self.skipTest("OS does not permit directory links: " + str(exc))
        return link

    def test_context_selection_reads_a_book_under_a_linked_parent(self):
        from context_manager import select_context
        direct = select_context(self.book, 5)
        linked = select_context(self.alias / "book", 5)
        self.assertTrue(direct["ready"], direct.get("missing_required"))
        self.assertTrue(linked["ready"], linked.get("missing_required"))

    def test_resume_recognises_a_book_under_a_linked_parent(self):
        import resume
        report = resume.build_report(str(self.alias / "book"))
        self.assertEqual(report["project_state"], "native", report["debts"])
        self.assertEqual(report["last_chapter"],
                         resume.build_report(str(self.book))["last_chapter"])

    def test_book_root_link_is_still_refused_and_names_the_real_directory(self):
        import os
        import resume
        from context_manager import generate_context_report, select_context
        root_link = self.link(self.base / "book-link", self.book)
        report = resume.build_report(str(root_link))
        self.assertEqual(report["project_state"], "unknown")
        self.assertIn(os.path.realpath(str(self.book)), " ".join(report["debts"]))
        context = select_context(root_link, 5)
        self.assertFalse(context["ready"])
        self.assertIn(os.path.realpath(str(self.book)), generate_context_report(context))

    def test_materialize_refusal_names_the_resolved_path(self):
        import os
        import source_materialize
        source = self.alias / "book" / "正文" / "第001章.md"
        with self.assertRaises(ValueError) as caught:
            source_materialize.copy_source(source, self.base / "copy.md")
        self.assertIn("link", str(caught.exception))
        self.assertIn(os.path.realpath(str(source)), str(caught.exception))
        self.assertFalse((self.base / "copy.md").exists())
