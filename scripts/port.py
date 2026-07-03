#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""搬运工：把审题 skill 产出的文件精准搬运到「各岗位AI审题进度」仓库对应文件夹。

支持的文件类型与目标：
  保留题目（…可保留的题目/可保留题目）   → <岗位>/2_保留题目/
  重新出题（…需要重新出题/重新出题）     → <岗位>/3_需重新出题/
  重新出答案（…重新出答案/重出答案）     → <岗位>/4_需重新出答案/
  审核看板（roundN_dashboard.html）       → <岗位>/5_审核结果看板/
  汇总（…汇总/最终保留/审核通过）         → <岗位>/6_汇总/
  待审核题目（…待N轮审核）               → <岗位>/1_待审核题目/
  语言-待语言问题审核                     → <岗位>/7_语言问题审核/1_待语言问题审核/
  语言-一审结果                           → <岗位>/7_语言问题审核/2_一审结果/
  语言-待重出                             → <岗位>/7_语言问题审核/3_待重出/
  语言-重出结果                           → <岗位>/7_语言问题审核/4_重出结果/

用法：
  python port.py --repo <仓库路径> --src <源文件或目录> [--src ...] [--apply]
  不带 --apply 为预演（只打印计划，含改名与匹配结果，不复制）。
"""
import argparse
import csv
import re
import shutil
import sys
from pathlib import Path

# ---- 子行业别名：文件名用词 → 仓库 positions.csv 的「子行业」列用词 ----
SUB_ALIAS = [
    ("汽车整车与零部件制造业", "汽车及零部件"),
    ("汽车整车及零部件制造业", "汽车及零部件"),
    ("汽车整车及零部件制造", "汽车及零部件"),
    ("汽车及零部件", "汽车及零部件"),
    ("新能源制造业", "新能源制造"),
    ("新能源制造", "新能源制造"),
    ("半导体与集成电路制造业", "半导体与集成电路"),
    ("半导体与集成电路", "半导体与集成电路"),
    ("消费电子通信智能设备", "消费电子/通信/智能设备"),
    ("消费电子/通信/智能设备", "消费电子/通信/智能设备"),
    ("制造业通用", "制造业通用"),
    ("通用行业", "通用行业"),
]
POSTS = ["嵌入式软件工程师", "自动化工程师", "电气工程师", "电子工程师",
         "设备工程师", "机械工程师", "质量工程师", "硬件工程师",
         "工艺工程师", "技术支持工程师", "工程技术通用"]
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
      "八": 8, "九": 9, "十": 10}


def load_positions(repo: Path):
    rows = list(csv.DictReader(open(repo / "data" / "positions.csv", encoding="utf-8")))
    return rows


def find_sub(name):
    for a, real in SUB_ALIAS:
        if a in name:
            return real
    return None


def find_post(name):
    for p in POSTS:
        if p in name:
            return p
    return None


def round_of(name):
    m = re.search(r"待([0-9一二三四五六七八九十])轮审核", name)
    if m:
        r = m.group(1)
        return int(r) if r.isdigit() else CN.get(r, 1)
    m = re.match(r"^([0-9]+)轮[_-]", name)
    if m:
        return int(m.group(1))
    m = re.search(r"第([0-9一二三四五六七八九十])轮", name)
    if m:
        r = m.group(1)
        return int(r) if r.isdigit() else CN.get(r, 1)
    m = re.search(r"([0-9])轮", name)
    if m:
        return int(m.group(1))
    return None


def classify(name):
    """返回目标相对文件夹（相对岗位目录）。无法识别返回 None。"""
    n = name
    # 语言问题审核（优先判断，含「语言」关键词）
    if "语言" in n or "题干语言" in n:
        if "重出结果" in n or "重出答案" in n or "重新出" in n:
            return "8_语言问题审核/4_重出结果"
        if "待重出" in n:
            return "8_语言问题审核/3_待重出"
        if "一审结果" in n or "审核结果" in n or "一审" in n:
            return "8_语言问题审核/2_一审结果"
        return "8_语言问题审核/1_待语言问题审核"
    # 收尾题目（知识审核最后一轮重新出的题目，先于「重新出题」判断）
    if "收尾" in n:
        return "6_收尾题目"
    # 看板
    if "dashboard" in n.lower() or "看板" in n:
        return "5_审核结果看板"
    # 汇总（最终保留）
    if "汇总" in n or "最终保留" in n or "审核通过" in n:
        return "7_汇总"
    # 保留题目
    if "可保留" in n or "保留的题目" in n or "保留题目" in n:
        return "2_保留题目"
    # 重新出答案（先于重新出题判断，避免「重新出」误判）
    if "重新出答案" in n or "重出答案" in n:
        return "4_需重新出答案"
    # 重新出题
    if "需要重新出题" in n or "重新出题" in n or "需重新出题" in n:
        return "3_需重新出题"
    # 待审核题目
    if "待" in n and "轮审核" in n:
        return "1_待审核题目"
    return None


def resolve_position(sub, post, positions):
    cands = []
    for r in positions:
        if r["子行业"] != sub:
            continue
        if r["岗位名称"] == post:
            cands.append(r["path"])
        elif post == "质量工程师" and r["岗位名称"] == "汽车质量工程师" and sub == "汽车及零部件":
            cands.append(r["path"])
    if len(cands) == 1:
        return cands[0]
    return cands or None


def normalize_name(orig, sub, post, folder, rnd):
    """规范化文件名。返回 (新文件名, 是否改名)。"""
    ext = Path(orig).suffix
    if not sub or not post:
        return orig, False
    if folder == "5_审核结果看板":
        newname = f"第{rnd}轮审核看板{ext}" if rnd else f"审核看板{ext}"
    elif folder == "1_待审核题目":
        newname = f"{sub}-{post}题目_待{rnd or 1}轮审核{ext}"
    elif folder == "2_保留题目":
        newname = (f"{rnd}轮_{sub}_{post}_可保留的题目{ext}" if rnd
                   else f"{sub}_{post}_可保留的题目{ext}")
    elif folder == "3_需重新出题":
        newname = (f"{rnd}轮_{sub}_{post}_需要重新出题{ext}" if rnd
                   else f"{sub}_{post}_需要重新出题{ext}")
    elif folder == "4_需重新出答案":
        newname = (f"{rnd}轮_{sub}_{post}_重新出答案{ext}" if rnd
                   else f"{sub}_{post}_重新出答案{ext}")
    elif folder == "6_收尾题目":
        newname = f"{sub}-{post}_收尾题目{ext}"
    elif folder == "7_汇总":
        newname = f"{sub}-{post}_最终汇总保留题目{ext}"
    elif folder.startswith("8_语言问题审核"):
        lang_word = {
            "8_语言问题审核/1_待语言问题审核": "待语言问题审核",
            "8_语言问题审核/2_一审结果": "语言问题一审结果",
            "8_语言问题审核/3_待重出": "语言问题待重出",
            "8_语言问题审核/4_重出结果": "语言问题重出结果",
        }[folder]
        newname = f"{sub}-{post}_{lang_word}{ext}"
    else:
        return orig, False
    newname = newname.replace("/", "／")
    return newname, (newname != orig)


def iter_sources(srcs):
    for s in srcs:
        p = Path(s)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in (".xlsx", ".html", ".htm") \
                        and not f.name.startswith("~") and not f.name.startswith("."):
                    yield f
        elif p.is_file():
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--src", action="append", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    positions = load_positions(repo)

    plan, unmatched = [], []
    for f in iter_sources(args.src):
        name = f.name
        ctx = str(f.parent)  # 父目录路径，用于补全文件名缺失的行业/岗位
        sub = find_sub(name) or find_sub(ctx)
        post = find_post(name) or find_post(ctx)
        folder = classify(name)
        rnd = round_of(name) or round_of(ctx)
        if not sub or not post or not folder:
            unmatched.append((str(f), sub, post, folder, rnd))
            continue
        pos = resolve_position(sub, post, positions)
        if not pos or isinstance(pos, list):
            unmatched.append((str(f), sub, post, folder, f"岗位={pos}"))
            continue
        newname, renamed = normalize_name(name, sub, post, folder, rnd)
        dest = repo / pos / folder / newname
        plan.append((f, dest, renamed))

    print(f"\n===== 搬运计划：{len(plan)} 个文件 =====")
    for f, dest, renamed in plan:
        flag = "（改名）" if renamed else ""
        print(f"  {f.name} {flag}\n    → {dest.relative_to(repo)}")
    if unmatched:
        print(f"\n===== ⚠️ 无法识别（需人工确认）：{len(unmatched)} 个 =====")
        for u in unmatched:
            print(f"  {u}")

    if args.apply:
        for f, dest, _ in plan:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
        print(f"\n✅ 已搬运 {len(plan)} 个文件到仓库。")
    else:
        print("\n（预演模式，加 --apply 执行）")


if __name__ == "__main__":
    main()


