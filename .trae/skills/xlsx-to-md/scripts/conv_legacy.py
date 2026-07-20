#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性转换：禅道导出的 Sprint1~3 测试用例 xlsx → md
- Sheet 固定取「用例」
- 用例编号：Sprint3 保留原值(唯一)；Sprint1/2 用禅道套件ID同值，改为 TC_S{N}_{3位序号} 行号编号
- 模块：从「相关研发需求」提取 [#NNNN] 作为分组键 + 模块名
- 优先级：1/2/3 → P1/P2/P3
- 设计方法/备注/Sprint：补为「历史回溯」「Sprint{N}」
用法： python conv_legacy.py
"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"C:/Users/osshenyang/.agents/skills/xlsx-to-md/scripts")
import xlsx_to_md as X
import pandas as pd

PRI_MAP = {"1": "P1", "2": "P2", "3": "P3", 1: "P1", 2: "P2", 3: "P3"}
FILES = [
    ("测试用例/Sprint1_测试用例.xlsx", 1),
    ("测试用例/Sprint2_测试用例.xlsx", 2),
    ("测试用例/Sprint3_测试用例.xlsx", 3),
]
CFG = r"C:/Users/osshenyang/.agents/skills/xlsx-to-md/scripts/config_zentao.json"

def mod_key_name(raw):
    """从 '59658:统一转发路由网关 (优先级:1.高,预计工时:0)(#59658)' 提取 (key, name)。"""
    if not raw or str(raw) == "nan":
        return "未分组", "未分组"
    s = str(raw).strip()
    m = re.search(r"#(\d+)", s)
    key = m.group(1) if m else s.split(":")[0]
    m2 = re.match(r"^\d+:\s*(.+?)\s*\(优先级", s)
    name = m2.group(1).strip() if m2 else s
    return key, name

def load_rows(xlsx):
    sdf = pd.read_excel(xlsx, sheet_name="用例", header=None)
    headers = [X.cell_text(v) for v in sdf.iloc[0].tolist()]
    df = sdf.iloc[1:].reset_index(drop=True)
    df.columns = headers
    return df

def build(df, sprint):
    cfg = X.load_config(CFG)
    aliases = X._get_aliases(cfg)
    col_map = X.map_columns(df, aliases)
    # 提取标准字段行
    rows = []
    for i in range(len(df)):
        row = {}
        for std, actual in col_map.items():
            row[std] = X.cell_text(df.iloc[i][actual])
        rows.append(row)
    # 编号 / 模块 / 优先级 / Sprint / 设计方法 处理
    module_names = {}
    for idx, r in enumerate(rows, 1):
        if sprint == 3:
            r["用例编号"] = r.get("用例编号", "") or f"TC_S3_{idx:03d}"
        else:
            r["用例编号"] = f"TC_S{sprint}_{idx:03d}"
        key, name = mod_key_name(r.get("模块", ""))
        module_names[key] = name
        r["模块"] = key
        pri = str(r.get("优先级", "")).strip()
        r["优先级"] = PRI_MAP.get(pri, pri) or pri
        if not r.get("设计方法"):
            r["设计方法"] = "历史回溯"
        r["需求编号"] = key
        r["备注"] = f"Sprint{sprint}（历史回溯建档）"
    return rows, module_names, cfg

def emit(rows, module_names, cfg, title, source):
    pri_levels = ["P1", "P2", "P3"]
    list_prefixes = X._get_list_prefixes(cfg)
    modules = {}
    for r in rows:
        modules.setdefault(r["模块"], []).append(r)
    lines = [
        f"# {title}",
        "",
        f"> 来源：{source} | Sheet：用例 | 总用例数：{len(rows)} | 优先级：1/2/3→P1/P2/P3 | 编号：Sprint3保留原值，Sprint1/2生成行号编号",
        "",
        "---",
        "",
        "## 模块概览",
        "",
    ]
    lines.extend(X.build_overview(modules, module_names, pri_levels))
    lines += ["", "---", ""]
    for mod in sorted(modules.keys(), key=X.natural_sort_key):
        name = module_names.get(mod, mod)
        lines.append(f"## {mod} {name}")
        lines.append("")
        lines.extend(X.build_detail(modules[mod], pri_levels, list_prefixes))
    return "\n".join(lines)

for xlsx, sprint in FILES:
    df = load_rows(xlsx)
    rows, mnames, cfg = build(df, sprint)
    title = f"Sprint{sprint} 测试用例（模型平台）"
    md = emit(rows, mnames, cfg, title, xlsx.split("/")[-1])
    out = xlsx.replace(".xlsx", ".md")
    from pathlib import Path
    p = Path(out)
    p.write_text(md, encoding="utf-8")
    # 概览统计
    from collections import Counter
    c = Counter(r["模块"] for r in rows)
    print(f"✅ {out}  | {len(rows)}条 | {len(c)}模块")
    for k in sorted(c.keys(), key=X.natural_sort_key):
        print(f"     {k} {mnames[k]}: {c[k]}")