#!/usr/bin/env python3
"""Excel测试用例 → Markdown 转换器（可配置版）

用法:
  python xlsx_to_md.py <input.xlsx> [output.md] [选项]

配置加载优先级:
  1. --config 指定的 JSON 文件
  2. 脚本同目录下的 config.json
  3. 代码内置的极简默认值
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

# ── 极简内置默认值（仅在 config.json 不存在时使用） ──────────
_MINIMAL_COLUMN_ALIASES = {
    "用例编号": ["用例编号", "TC编号", "Case ID"],
    "模块":     ["模块", "Module"],
    "用例标题": ["用例标题", "标题", "TestCase"],
    "优先级":   ["优先级", "Priority"],
    "前置条件": ["前置条件", "Precondition"],
    "测试步骤": ["测试步骤", "Steps"],
    "预期结果": ["预期结果", "Expected"],
    "备注":     ["备注", "Note"],
    "设计方法": ["设计方法", "Method"],
    "需求编号": ["需求编号", "ReqID"],
}
_MINIMAL_PRIORITY_LEVELS = ["P0", "P1", "P2", "P3"]
_MINIMAL_LIST_PREFIXES = ["1.", "2.", "3.", "-", "•", "*"]
_MINIMAL_DEFAULT_GROUP_BY = "模块"


def load_config(config_path: str | None = None) -> dict:
    """按优先级加载配置文件，返回配置字典。"""
    paths_to_try = []
    if config_path:
        paths_to_try.append(Path(config_path))
    paths_to_try.append(Path(__file__).parent / "config.json")

    for p in paths_to_try:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            print(f"📋 已加载配置: {p}")
            return cfg

    print("ℹ️ 未找到配置文件，使用内置默认值")
    return {}


def _get_aliases(cfg: dict) -> dict[str, list[str]]:
    return cfg.get("column_aliases", _MINIMAL_COLUMN_ALIASES)


def _get_module_names(cfg: dict) -> dict[str, str]:
    return cfg.get("module_names", {})


def _get_priority_levels(cfg: dict) -> list[str]:
    return cfg.get("priority_levels", _MINIMAL_PRIORITY_LEVELS)


def _get_list_prefixes(cfg: dict) -> list[str]:
    return cfg.get("list_prefixes", _MINIMAL_LIST_PREFIXES)


def _get_group_by(cfg: dict) -> str:
    return cfg.get("default_group_by", _MINIMAL_DEFAULT_GROUP_BY)


def _get_expand_module(cfg: dict) -> bool:
    return cfg.get("expand_module_name", False)


def natural_sort_key(s: str) -> list:
    """自然排序键：使 F1/F2/F11 按数字递增排列，而非字典序（F1,F11,F2,...）。
    按数字段与非数字段切分，数字段转 int 比较；非 F 开头的编号同样适用。
    """
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", str(s))]


def build_numbered_regex() -> re.Pattern:
    """构建匹配 1. ~ 99. 编号前缀的正则。"""
    return re.compile(r"^(\d{1,2})\.\s")


def normalize_module_name(raw: str, module_names: dict | None = None) -> str:
    """合并子模块名，如 'F1 平台资源池与租户资源管理' → 'F1'"""
    if not raw or (isinstance(raw, float) and pd.isna(raw)):
        return "未知"
    raw = str(raw).strip()
    names = module_names or {}
    for prefix in names:
        if raw == prefix or raw.startswith(prefix + " "):
            return prefix
    return raw


def map_columns(df: pd.DataFrame, aliases: dict[str, list[str]]) -> dict[str, str]:
    """将 DataFrame 列名映射到标准字段名。返回 {标准名: 实际列名}"""
    mapping: dict[str, str] = {}
    actual_cols = list(df.columns)
    for std_name, alias_list in aliases.items():
        for alias in alias_list:
            for col in actual_cols:
                if str(col).strip().lower() == alias.lower():
                    mapping[std_name] = col
                    break
            if std_name in mapping:
                break
    return mapping


def cell_text(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    return s


def build_overview(
    modules: dict,
    module_names: dict,
    priority_levels: list[str],
) -> list[str]:
    headers = ["模块", "模块名称", "用例数"] + priority_levels
    sep = ["------"] * len(headers)
    lines = [f"| {' | '.join(headers)} |", f"| {' | '.join(sep)} |"]

    totals = {p: 0 for p in priority_levels}
    total_cases = 0

    for mod in sorted(modules.keys(), key=natural_sort_key):
        cases = modules[mod]
        name = module_names.get(mod, "")
        counts = {p: sum(1 for c in cases if c["优先级"] == p) for p in priority_levels}
        total_cases += len(cases)
        for p in priority_levels:
            totals[p] += counts[p]
        cells = [mod, name, str(len(cases))] + [str(counts[p]) for p in priority_levels]
        lines.append(f"| {' | '.join(cells)} |")

    total_cells = ["**合计**", "", f"**{total_cases}**"] + [
        f"**{totals[p]}**" for p in priority_levels
    ]
    lines.append(f"| {' | '.join(total_cells)} |")
    return lines


def build_detail(
    cases: list[dict],
    priority_levels: list[str],
    list_prefixes: list[str],
) -> list[str]:
    num_re = build_numbered_regex()
    prefix_set = set(list_prefixes)
    lines = []

    for c in cases:
        rid = c.get("用例编号", "")
        title = c.get("用例标题", "")
        pri = c.get("优先级", "")
        pre = c.get("前置条件", "")
        steps = c.get("测试步骤", "")
        expect = c.get("预期结果", "")
        note = c.get("备注", "")
        method = c.get("设计方法", "")
        req = c.get("需求编号", "")

        lines.append(f"### {rid}")
        lines.append("")
        lines.append(f"**标题**：{title}")
        lines.append("")
        lines.append(f"**优先级**：{pri}")
        lines.append("")

        if method:
            lines.append(f"**设计方法**：{method}")
            lines.append("")
        if req:
            lines.append(f"**需求编号**：{req}")
            lines.append("")

        if pre:
            lines.append("**前置条件**：")
            lines.append("")
            for ln in pre.split("\n"):
                lines.append(f"> {ln}")
            lines.append("")

        if steps:
            lines.append("**测试步骤**：")
            lines.append("")
            for ln in steps.split("\n"):
                lines.append(ln)
            lines.append("")

        if expect:
            lines.append("**预期结果**：")
            lines.append("")
            for ln in expect.split("\n"):
                stripped = ln.strip()
                # 匹配编号前缀 (1. ~ 99.) 或已知列表符号
                if num_re.match(stripped) or any(stripped.startswith(p) for p in prefix_set):
                    lines.append(ln)
                else:
                    lines.append(f"- {ln}")
            lines.append("")

        if note:
            lines.append(f"**备注**：{note}")
            lines.append("")

        lines.append("---")
        lines.append("")
    return lines


def convert(
    input_path: str,
    output_path: str | None = None,
    config_path: str | None = None,
    module_names_override: dict | None = None,
    title: str | None = None,
    group_by: str | None = None,
    sheet: str | int | None = None,
    expand_module: bool | None = None,
) -> str:
    """主转换函数，返回生成的 Markdown 文本。"""

    # 加载配置
    cfg = load_config(config_path)
    column_aliases = _get_aliases(cfg)
    module_names = _get_module_names(cfg)
    priority_levels = _get_priority_levels(cfg)
    list_prefixes = _get_list_prefixes(cfg)
    default_group = group_by or _get_group_by(cfg)
    do_expand = expand_module if expand_module is not None else _get_expand_module(cfg)

    # CLI --module-names 合并覆盖
    if module_names_override:
        module_names = {**module_names, **module_names_override}

    # 读取 Excel
    xlsx = Path(input_path)
    if not xlsx.exists():
        raise FileNotFoundError(f"文件不存在: {input_path}")

    all_sheets = pd.read_excel(str(xlsx), sheet_name=None, header=None)

    # 选取 sheet
    selected_sheet = None
    sheet_name = ""

    if sheet is not None:
        if isinstance(sheet, int):
            # 按索引选取（0-based）
            sn_list = list(all_sheets.keys())
            if 0 <= sheet < len(sn_list):
                selected_sheet = all_sheets[sn_list[sheet]]
                sheet_name = sn_list[sheet]
            else:
                raise ValueError(f"Sheet 索引超出范围: {sheet}（共 {len(sn_list)} 个 Sheet）")
        else:
            # 按名称选取
            sheet_str = str(sheet)
            if sheet_str in all_sheets:
                selected_sheet = all_sheets[sheet_str]
                sheet_name = sheet_str
            else:
                raise ValueError(f"未找到名为 '{sheet_str}' 的 Sheet，可用: {list(all_sheets.keys())}")
    else:
        # 默认：取第一个有 ≥2 行数据的 sheet
        for sn, sdf in all_sheets.items():
            if len(sdf) >= 2:
                selected_sheet = sdf
                sheet_name = sn
                break

    if selected_sheet is None:
        raise ValueError("Excel 中没有找到有效数据（至少需要表头+1行数据）")

    df = selected_sheet
    headers = [cell_text(v) for v in df.iloc[0].tolist()]
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = headers

    # 列映射
    col_map = map_columns(df, column_aliases)
    if "用例编号" not in col_map:
        raise ValueError(
            f"未识别到'用例编号'列。\n"
            f"当前列名: {headers}\n"
            f"请检查 config.json 的 column_aliases 配置，或使用 --config 指定正确的配置文件。"
        )

    # 提取数据
    rows: list[dict] = []
    for i in range(len(df)):
        row = {}
        for std_name, actual_col in col_map.items():
            row[std_name] = cell_text(df.iloc[i][actual_col])
        rows.append(row)

    # 归一化模块名
    for r in rows:
        r["模块"] = normalize_module_name(r.get("模块", ""), module_names)
        if do_expand and r["模块"] in module_names:
            r["模块"] = f"{r['模块']} {module_names[r['模块']]}"

    # 按分组字段分组
    modules: dict[str, list[dict]] = {}
    for r in rows:
        mod = r.get(default_group, default_group)
        modules.setdefault(mod, []).append(r)

    # 组装 Markdown
    stem = xlsx.stem
    doc_title = title or stem
    lines = [
        f"# {doc_title}",
        "",
        f"> 来源：{xlsx.name} | Sheet：{sheet_name} | 总用例数：{len(rows)}",
        "",
        "---",
        "",
    ]

    lines.append("## 模块概览")
    lines.append("")
    lines.extend(build_overview(modules, module_names, priority_levels))
    lines.append("")
    lines.append("---")
    lines.append("")

    for mod in sorted(modules.keys(), key=natural_sort_key):
        name = module_names.get(mod, mod)
        lines.append(f"## {mod} {name}")
        lines.append("")
        lines.extend(build_detail(modules[mod], priority_levels, list_prefixes))

    md_text = "\n".join(lines)

    # 写入文件
    out = Path(output_path) if output_path else xlsx.with_suffix(".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md_text, encoding="utf-8")
    print(f"✅ 已生成: {out}  ({len(rows)} 条用例, {len(modules)} 个模块)")
    return md_text


def main():
    parser = argparse.ArgumentParser(description="Excel测试用例 → Markdown 转换器")
    parser.add_argument("input", help="输入 .xlsx 文件路径")
    parser.add_argument("output", nargs="?", default=None, help="输出 .md 文件路径（默认同目录）")
    parser.add_argument("--config", default=None, help="自定义配置文件路径（config.json）")
    parser.add_argument("--module-names", default=None, help="额外模块名称 JSON 文件路径（与 config 合并）")
    parser.add_argument("--sheet", default=None, help="指定 Sheet（索引或名称）")
    parser.add_argument("--group-by", default=None, help="分组字段（默认取 config 的 default_group_by）")
    parser.add_argument("--title", default=None, help="文档标题（默认取文件名）")
    parser.add_argument("--expand-module", action="store_true", default=None,
                        help="模块列输出长形式 '{code} {name}'，默认仅输出短编号")
    args = parser.parse_args()

    mnames = None
    if args.module_names:
        with open(args.module_names, "r", encoding="utf-8") as f:
            mnames = json.load(f)

    sheet_arg = args.sheet
    if sheet_arg is not None:
        try:
            sheet_arg = int(sheet_arg)
        except ValueError:
            pass

    convert(
        args.input,
        args.output,
        config_path=args.config,
        module_names_override=mnames,
        title=args.title,
        group_by=args.group_by,
        sheet=sheet_arg,
        expand_module=args.expand_module,
    )


if __name__ == "__main__":
    main()