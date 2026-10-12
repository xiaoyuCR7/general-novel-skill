#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_check_text.py — 测试 check_text.py 门禁检查核心功能。

运行方式：
    python scripts/tests/test_check_text.py
"""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# 把 scripts 目录加入 sys.path
SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_text
from check_text import (
    BANNED_WORDS,
    count_chars,
    scan_lines,
    scan_gate_c,
    scan_blocking_patterns,
    print_gate_report,
    extract_chapter_number,
    has_skip_marker,
    strip_dialogue,
)


class TestGateABannedWords(unittest.TestCase):
    """Gate A 禁用词检测。"""

    def test_banned_word_in_narration_is_blocking(self):
        """叙述域命中禁用词记为 blocking。"""
        lines = ["他不禁笑了。"]
        # 「不禁」是内置禁用词
        banned, toxic = scan_lines(lines, BANNED_WORDS)
        self.assertTrue(any(h[1] == "不禁" for h in banned))
        # 叙述域命中应为 blocking
        self.assertTrue(any(h[3] == "blocking" for h in banned if h[1] == "不禁"))

    def test_banned_word_in_dialogue_is_advisory(self):
        """对话域命中禁用词降级为 advisory。"""
        lines = ['他说：「我仿佛知道答案。」']
        banned, toxic = scan_lines(lines, BANNED_WORDS)
        # 「仿佛」命中
        fangfo_hits = [h for h in banned if h[1] == "仿佛"]
        self.assertTrue(fangfo_hits)
        # 对话域应为 advisory
        self.assertEqual(fangfo_hits[0][3], "advisory")

    def test_no_banned_word(self):
        """干净文本无命中。"""
        lines = ["天空很蓝，他推开门走出去。"]
        banned, toxic = scan_lines(lines, BANNED_WORDS)
        self.assertEqual(banned, [])

    def test_multiple_banned_words(self):
        """一行内多个禁用词都应被检出。"""
        lines = ["他似乎不禁意味深长地笑了。"]
        banned, _ = scan_lines(lines, BANNED_WORDS)
        words_hit = {h[1] for h in banned}
        self.assertIn("似乎", words_hit)
        self.assertIn("不禁", words_hit)
        self.assertIn("意味深长", words_hit)

    def test_whitelist_exemption(self):
        """白名单命中时跳过。"""
        lines = ["他不禁笑了。"]
        banned, _ = scan_lines(lines, BANNED_WORDS, whitelist={"不禁"})
        self.assertFalse(any(h[1] == "不禁" for h in banned))


class TestGateBToxicPatterns(unittest.TestCase):
    """Gate B 毒句式检测。"""

    def test_not_is_comparison(self):
        """「不是A，而是B」句式命中。"""
        lines = ["这不是结束，而是新的开始。"]
        _, toxic = scan_lines(lines, BANNED_WORDS)
        rule_ids = {h[1] for h in toxic}
        self.assertIn("not-is-comparison", rule_ids)

    def test_no_only_pattern(self):
        """「没有X，只有Y」句式命中。"""
        lines = ["没有退路，只有前进。"]
        _, toxic = scan_lines(lines, BANNED_WORDS)
        rule_ids = {h[1] for h in toxic}
        self.assertIn("no-only", rule_ids)

    def test_this_moment_pattern(self):
        """「这一刻，」起手式命中。"""
        lines = ["这一刻，时间静止了。"]
        _, toxic = scan_lines(lines, BANNED_WORDS)
        rule_ids = {h[1] for h in toxic}
        self.assertIn("this-moment", rule_ids)

    def test_clean_text_no_toxic(self):
        """干净文本无毒句式命中。"""
        lines = ["他推开门，走进院子，看见老树。"]
        _, toxic = scan_lines(lines, BANNED_WORDS)
        self.assertEqual(toxic, [])


class TestGateCPsycheTelling(unittest.TestCase):
    """Gate C 心理告知检测。"""

    def test_direct_emotion_statement(self):
        """「他很紧张」类直接陈述情绪命中。"""
        lines = ["他很紧张地握住剑柄。"]
        hits = scan_gate_c(lines)
        self.assertTrue(any("心理告知" in h[1] for h in hits))

    def test_heart_surge_pattern(self):
        """「心中涌起」句式命中。"""
        lines = ["他心中涌起一股不安。"]
        hits = scan_gate_c(lines)
        self.assertTrue(any("心中" in h[1] for h in hits))

    def test_no_psyche_telling(self):
        """干净文本无心理告知命中。"""
        lines = ["他握紧剑柄，推门而出。"]
        hits = scan_gate_c(lines)
        self.assertEqual(hits, [])


class TestWordCount(unittest.TestCase):
    """字数统计功能。"""

    def test_count_chars_chinese(self):
        non_ws, cjk = count_chars("你好世界")
        self.assertEqual(non_ws, 4)
        self.assertEqual(cjk, 4)

    def test_count_chars_mixed(self):
        non_ws, cjk = count_chars("Hello 世界 123")
        # 非空白：Hello5 + 空格0 + 世界2 + 123 = 10
        self.assertEqual(non_ws, 10)
        self.assertEqual(cjk, 2)

    def test_count_chars_whitespace_only(self):
        non_ws, cjk = count_chars("  \n\t  ")
        self.assertEqual(non_ws, 0)
        self.assertEqual(cjk, 0)

    def test_count_chars_with_punctuation(self):
        non_ws, cjk = count_chars("你好，世界！")
        # 非空白：6（含标点），汉字：4
        self.assertEqual(non_ws, 6)
        self.assertEqual(cjk, 4)


class TestGateReportJson(unittest.TestCase):
    """门禁报告 JSON 格式输出。"""

    def _make_chapter_text(self):
        """生成一段含多个命中的章节文本。"""
        return (
            "# 第37章 测试\n\n"
            "他不禁笑了。这不是结束，而是开始。\n\n"
            "他很紧张地看着前方。\n\n"
            "这一刻，他终于明白了。\n\n"
            "他推开门，走了出去。\n"
        )

    def test_gate_report_returns_stats_dict(self):
        """print_gate_report 返回统计字典，键齐全。"""
        text = self._make_chapter_text()
        lines = text.splitlines()
        words = list(BANNED_WORDS)
        non_ws, _ = count_chars(text)

        buf = io.StringIO()
        with redirect_stdout(buf):
            stats = print_gate_report(text, lines, words, set(), non_ws)

        # 关键字段存在
        expected_keys = {
            "banned_blocking", "banned_advisory",
            "toxic_blocking", "toxic_advisory",
            "gate_c", "gate_g_meta_refusal", "trailer",
            "density_advisory", "structure_advisory",
            "para_tics_advisory", "gate_f",
            "blocking", "advisory", "ai_score",
        }
        self.assertTrue(expected_keys.issubset(stats.keys()))

    def test_gate_report_ai_score_in_range(self):
        """AI 味分数在 0-100 之间。"""
        text = "他推开门，走出去。"
        lines = text.splitlines()
        non_ws, _ = count_chars(text)
        with redirect_stdout(io.StringIO()):
            stats = print_gate_report(text, lines, list(BANNED_WORDS), set(), non_ws)
        self.assertGreaterEqual(stats["ai_score"], 0.0)
        self.assertLessEqual(stats["ai_score"], 100.0)

    def test_gate_report_blocking_count(self):
        """含禁用词与毒句式的文本，blocking 计数 > 0。"""
        text = "他不禁笑了。这不是结束，而是开始。\n"
        lines = text.splitlines()
        non_ws, _ = count_chars(text)
        with redirect_stdout(io.StringIO()):
            stats = print_gate_report(text, lines, list(BANNED_WORDS), set(), non_ws)
        self.assertGreater(stats["blocking"], 0)


class TestSkipMarkerAndChapterNumber(unittest.TestCase):
    """豁免标记与章号解析。"""

    def test_has_skip_marker(self):
        text = "<!-- 闸口:跳过 -->\n正文内容"
        self.assertTrue(has_skip_marker(text))

    def test_no_skip_marker(self):
        text = "普通正文"
        self.assertFalse(has_skip_marker(text))

    def test_skip_marker_outside_head_not_triggered(self):
        """豁免标记在第 6 行之后不生效。"""
        text = "\n".join(["行"] * 6) + "\n<!-- 闸口:跳过 -->"
        self.assertFalse(has_skip_marker(text))

    def test_extract_chapter_number(self):
        self.assertEqual(extract_chapter_number("正文/第037章_测试.md"), 37)
        self.assertEqual(extract_chapter_number("第37章.md"), 37)
        self.assertIsNone(extract_chapter_number("readme.md"))


class TestR5ClosingQuote(unittest.TestCase):
    def test_complete_chinese_quoted_ending_is_not_truncated(self):
        from check_text import scan_structure
        for text in ("他说：“这一栏，现在可以验了。”", "她答：‘可以了。’"):
            with self.subTest(text=text):
                self.assertFalse(any(hit[0] == "truncation" for hit in scan_structure(text)))
        self.assertTrue(any(hit[0] == "truncation" for hit in scan_structure("他抬手，正要")))


class TestBlockingPrecision(unittest.TestCase):
    """blocking 规则不得误伤正常句子，也不得漏掉真正的同构句式。"""

    def blocking_ids(self, line):
        banned, toxic = scan_lines([line], BANNED_WORDS)
        return sorted([h[1] for h in banned if h[3] == "blocking"]
                      + [h[1] for h in toxic if h[5] == "blocking"])

    def test_function_word_shi_is_not_reverse_contrast(self):
        for line in ("可是天已经黑了，不是他不想走。", "他只是点了点头，不是很在意。",
                     "老张还是老样子，不是在喝茶就是在看报。", "他总是这样，不是吗。"):
            with self.subTest(line=line):
                self.assertEqual(self.blocking_ids(line), [])
        self.assertEqual(self.blocking_ids("这是命令，不是请求。"), ["reverse-not-is"])

    def test_negation_parade_needs_bare_parallel_negations(self):
        for line in ("他无奈地摇头，无数念头闪过。", "屋里没有灯，也没有人。"):
            with self.subTest(line=line):
                self.assertEqual(self.blocking_ids(line), [])
        self.assertEqual(self.blocking_ids("没有犹豫，没有迟疑。"), ["negation-parade"])

    def test_banned_word_inside_idiom_is_exempt(self):
        self.assertEqual(self.blocking_ids("她做事一丝不苟。"), [])
        self.assertEqual(self.blocking_ids("他眼里闪过一丝不安。"), ["一丝"])

    def test_curly_quotes_are_dialogue_domain(self):
        banned, _ = scan_lines(["“你似乎不太高兴。”她说。"], BANNED_WORDS)
        self.assertEqual([(h[1], h[3]) for h in banned], [("似乎", "advisory")])
        self.assertEqual(strip_dialogue("“走。”他说。"), "「」他说。")

    def test_story_objects_are_not_meta_leaks(self):
        def meta(line):
            return [h[3] for h in scan_blocking_patterns(["标题", line]) if h[1] == "meta-leak"]
        self.assertEqual(meta("他把鱼钩子甩进河里，又铺垫子坐下。"), [])
        self.assertEqual(meta("这里要留个钩子，做好铺垫。"), ["留个钩子"])


class TestSecondGenerationAdvisories(unittest.TestCase):
    """密度型 advisory：成片才报，单次自然用法不报。"""

    FILLER = "雨落在瓦上。" * 20

    def density_ids(self, text):
        return [h[0] for h in check_text.scan_density(text, len(text))]

    def test_bare_contrast_only_flagged_when_clustered(self):
        clustered = "这不是威胁，是通知。他不是怕，是没力气怕了。那不是光，是火。" + self.FILLER
        self.assertIn("bare-contrast-tic", self.density_ids(clustered))
        self.assertNotIn("bare-contrast-tic", self.density_ids("这不是威胁，是通知。" + self.FILLER * 2))

    def test_body_cliche_density(self):
        text = "他指节发白，喉结滚动。她瞳孔骤缩，深吸一口气。他攥紧了拳头，呼吸一滞。" + self.FILLER
        self.assertIn("body-cliche-tic", self.density_ids(text))
        self.assertNotIn("body-cliche-tic", self.density_ids("他深吸一口气。" + self.FILLER))

    def test_formula_tags_flagged_but_plain_said_is_not(self):
        formula = "\n".join(["“走吧。”他沉声道。", "她淡淡地说：“好。”",
                             "「去。」他冷冷地说道。"] * 3)
        self.assertIn("ai-tag-monotony", [h[0] for h in check_text.scan_ai_patterns(formula)])
        plain = "\n".join(["“走吧。”他说。", "“好。”她说。"] * 10)
        self.assertNotIn("ai-tag-monotony", [h[0] for h in check_text.scan_ai_patterns(plain)])

    def test_meta_leak_is_not_labelled_explainer_tone(self):
        ids = [h[0] for h in check_text.scan_ai_patterns("标题\n这是本章的伏笔。")]
        self.assertIn("ai-meta-leak", ids)
        self.assertNotIn("ai-explainer-tone", ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
