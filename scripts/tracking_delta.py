#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tracking_delta.py — 写后事实增量的证据核对（纯标准库，无第三方依赖）。

章事务能保证正文与追踪五表一起落盘，但不能保证表里写的事实正文里真的发生过。
本工具让每条追踪变更都带一段正文原文摘录，并机械核对摘录确实出现在本章候选正文中：

  check          核对增量文件：结构、证据摘录是否逐字出现在正文、关键实体是否出现、
                 伏笔 ID 是否已登记在 stage 的伏笔台账
  apply-summary  用增量里的 summary 生成本章「章节摘要」条目：同章已有条目则替换，
                 否则追加到「近 10 章详记」节末尾

增量文件放在 stage 与正式工程之外的本次工作目录，字段见
assets/templates/tracking-delta.json。它只核对「有出处」，不判断摘录是否足以支持结论；
语义是否成立仍由主 Agent 自查。

用法：
  python3 scripts/tracking_delta.py check "{work}/tracking-delta.json" \\
      --chapter-file "{stage}/正文/{chapter_file}" --ledger "{stage}/追踪/伏笔台账.md"
  python3 scripts/tracking_delta.py apply-summary "{work}/tracking-delta.json" \\
      --summary-file "{stage}/追踪/章节摘要.md"

退出码：0 = 无错误（可有提示）；1 = 有错误；2 = 参数/文件/格式错误。
"""

import argparse
import json
import re
import sys

TABLES = ("章节摘要", "角色状态", "伏笔台账", "时间线", "节奏配额")
SUMMARY_FIELDS = ("发生了什么", "状态变化", "伏笔进出", "新登场", "关键实体", "承上", "启下")
EVIDENCE_MIN_CHARS = 6
LEDGER_ID_RE = re.compile(r"F\d+-\d+")
RECENT_HEADING = "## 近 10 章详记"


class DeltaError(ValueError):
    """增量文件结构不合法。"""


def _read(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def _squash(text):
    """去掉全部空白，使摘录不因换行和缩进差异而匹配失败。"""
    return re.sub(r"\s+", "", text)


def load_delta(path):
    try:
        data = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise DeltaError("增量文件不是合法 JSON：{}".format(exc))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise DeltaError("增量文件须为 version=1 的对象")
    if type(data.get("chapter")) is not int or data["chapter"] < 1:
        raise DeltaError("chapter 须为正整数")
    if not isinstance(data.get("title"), str):
        raise DeltaError("title 须为字符串（无标题填空串）")
    summary = data.get("summary")
    if not isinstance(summary, dict):
        raise DeltaError("summary 须为对象")
    for field in SUMMARY_FIELDS:
        value = summary.get(field)
        if field == "关键实体":
            if (not isinstance(value, list) or not value
                    or any(not isinstance(v, str) or not v.strip() for v in value)):
                raise DeltaError("summary.关键实体 须为非空字符串数组")
        elif not isinstance(value, str) or not value.strip():
            raise DeltaError("summary.{} 须为非空字符串（确无内容填 N/A）".format(field))
    claims = data.get("claims")
    if not isinstance(claims, list):
        raise DeltaError("claims 须为数组（本章确无追踪变更时为空数组）")
    for index, claim in enumerate(claims, 1):
        if (not isinstance(claim, dict)
                or any(not isinstance(claim.get(key), str) or not claim[key].strip()
                       for key in ("table", "subject", "change", "evidence"))):
            raise DeltaError("claims[{}] 须含非空的 table、subject、change、evidence".format(index))
        if claim["table"] not in TABLES:
            raise DeltaError("claims[{}].table 须为 {} 之一".format(index, "/".join(TABLES)))
    return data


def check_delta(delta, chapter_text, ledger_text=None):
    """返回 (errors, warnings)，每项为 (code, 说明)。"""
    errors, warnings = [], []
    body = _squash(chapter_text)

    for entity in delta["summary"]["关键实体"]:
        if _squash(entity) not in body:
            errors.append(("entity_not_in_chapter",
                           "关键实体「{}」未在本章正文中逐字出现，日后无法据此检索；"
                           "改用正文里实际出现的叫法，不要为此改正文".format(entity)))

    for index, claim in enumerate(delta["claims"], 1):
        label = "claims[{}]（{}·{}）".format(index, claim["table"], claim["subject"])
        evidence = _squash(claim["evidence"])
        if len(evidence) < EVIDENCE_MIN_CHARS:
            errors.append(("evidence_too_short",
                           "{} 的证据摘录不足 {} 字，无法定位".format(label, EVIDENCE_MIN_CHARS)))
        elif evidence not in body:
            errors.append(("evidence_not_found",
                           "{} 的证据摘录未在本章正文中逐字出现：{}".format(label, claim["evidence"][:40])))
        if claim["table"] == "伏笔台账":
            ids = LEDGER_ID_RE.findall(claim["subject"])
            if not ids:
                errors.append(("ledger_id_missing", "{} 的 subject 须含伏笔 ID（如 F1-03）".format(label)))
            elif ledger_text is not None:
                for ledger_id in ids:
                    if ledger_id not in ledger_text:
                        errors.append(("ledger_id_not_registered",
                                       "{} 的伏笔 {} 未登记在 stage 的伏笔台账".format(label, ledger_id)))
        elif claim["table"] == "角色状态" and _squash(claim["subject"]) not in body:
            warnings.append(("subject_not_in_chapter",
                             "{} 的角色名未在本章正文出现，请确认不是别名或误记".format(label)))

    state_change = delta["summary"]["状态变化"].strip()
    if state_change not in ("N/A", "无") and not any(c["table"] == "角色状态" for c in delta["claims"]):
        warnings.append(("state_change_without_claim",
                         "summary.状态变化 非空，但没有任何角色状态 claim 给出证据"))
    return errors, warnings


def render_summary(delta):
    summary = delta["summary"]
    heading = "### 第{}章 {}".format(delta["chapter"], delta["title"]).rstrip()
    lines = [heading, ""]
    for field in SUMMARY_FIELDS:
        value = summary[field]
        if field == "关键实体":
            value = "，".join(v.strip() for v in value)
        lines.append("- {}：{}".format(field, " ".join(value.split())))
    return "\n".join(lines) + "\n"


def apply_summary(delta, summary_text):
    """把本章条目写入摘要文本：同章已有则替换，否则追加到近 10 章详记节末尾。"""
    entry = render_summary(delta)
    lines = summary_text.splitlines()
    entry_re = re.compile(r"^###\s*第\s*{}\s*章(?!\d)".format(delta["chapter"]))
    start = next((i for i, line in enumerate(lines) if entry_re.match(line)), None)
    if start is not None:
        end = next((i for i in range(start + 1, len(lines))
                    if lines[i].startswith("### ") or lines[i].startswith("## ")), len(lines))
        new_lines = lines[:start] + entry.rstrip("\n").splitlines() + [""] + lines[end:]
        return "\n".join(new_lines).rstrip("\n") + "\n", "replaced"
    section = next((i for i, line in enumerate(lines) if line.strip() == RECENT_HEADING), None)
    if section is None:
        raise DeltaError("章节摘要缺少「{}」节，无法定位追加位置".format(RECENT_HEADING))
    end = next((i for i in range(section + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    head = "\n".join(lines[:end]).rstrip("\n")
    tail = "\n".join(lines[end:])
    text = head + "\n\n" + entry
    if tail.strip():
        text += "\n" + tail.rstrip("\n") + "\n"
    return text, "appended"


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="写后事实增量的证据核对")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="核对增量的结构与正文证据")
    check.add_argument("delta", help="增量 JSON 路径（工程外工作目录）")
    check.add_argument("--chapter-file", required=True, help="stage 中的本章候选正文")
    check.add_argument("--ledger", default=None, help="stage 中的伏笔台账（核对伏笔 ID 已登记）")
    apply_parser = sub.add_parser("apply-summary", help="生成/替换本章的章节摘要条目")
    apply_parser.add_argument("delta", help="增量 JSON 路径（工程外工作目录）")
    apply_parser.add_argument("--summary-file", required=True, help="stage 中的章节摘要")
    args = parser.parse_args(argv)

    try:
        delta = load_delta(args.delta)
        if args.command == "check":
            chapter_text = _read(args.chapter_file)
            ledger_text = _read(args.ledger) if args.ledger else None
            errors, warnings = check_delta(delta, chapter_text, ledger_text)
            for code, message in errors:
                print("[error] {}: {}".format(code, message))
            for code, message in warnings:
                print("[warn] {}: {}".format(code, message))
            print("第{}章增量：{} 条 claim，{} 个错误，{} 个提示".format(
                delta["chapter"], len(delta["claims"]), len(errors), len(warnings)))
            return 1 if errors else 0
        text, action = apply_summary(delta, _read(args.summary_file))
        with open(args.summary_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("第{}章摘要条目已{}".format(delta["chapter"], "替换" if action == "replaced" else "追加"))
        return 0
    except DeltaError as exc:
        print("[error] invalid_delta: {}".format(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print("[error] file_error: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
