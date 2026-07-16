---
name: xlsx-to-md
description: "Excel(.xlsx) 测试用例与 Markdown 文件的双向转换工具。当用户提到测试用例 Excel、xlsx 转 md、用例格式转换、将 xlsx 生成 Markdown、Excel 用例导出、md 转 xlsx、Markdown 转回 Excel、把 md 还原成 xlsx、用例双向转换等场景时触发此技能，即使用户只是说'把测试用例转成md'、'帮我转换这个xlsx'、'生成md版本'、'把md转回Excel'也应使用。"
---

# Excel ↔ Markdown 测试用例双向转换

将 `.xlsx` 测试用例文件与结构化 Markdown 文件互相转换，支持完整的闭环流转。

## 为什么需要这个技能

Excel 表格直接贴到 Markdown 中会丢失结构、难以 diff 和追溯；而纯 Markdown 又无法直接交付给不熟悉 Git 的团队。本技能解决双向流转：
- **正向**（xlsx → md）：生成可 diff、可追溯、可 PR 的 Markdown 源文件
- **反向**（md → xlsx）：将 Markdown 还原为 Excel 交付件，方便线下评审和分发

---

## 正向转换：xlsx → md

### 第一步：确认输入

1. 用户指定 `.xlsx` 文件路径
2. 用 Read 工具或 Bash(pandas) 预览文件，确认表头位置、总行数与列数
3. 如果列名与 config.json 中的 `column_aliases` 差异较大，告知用户需要修改配置

### 第二步：执行转换

```bash
python <skill-path>/scripts/xlsx_to_md.py <input.xlsx> [output.md] [选项]
```

**全部 CLI 参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `input` | ✅ | 输入 Excel 文件路径 |
| `output` | ❌ | 输出 .md 路径（默认与 xlsx 同目录） |
| `--config` | ❌ | 自定义配置文件路径（默认加载脚本同目录的 config.json） |
| `--module-names` | ❌ | 额外模块名称 JSON 文件路径（与 config 合并，此处优先） |
| `--sheet` | ❌ | 指定 Sheet 页（数字索引 0-based，或名称字符串；默认自动选取） |
| `--group-by` | ❌ | 分组字段名（默认取 config 的 `default_group_by`） |
| `--title` | ❌ | 文档标题（默认取 xlsx 文件名） |
| `--expand-module` | ❌ | 模块列输出长形式 `{code} {name}`，默认仅输出短编号 |

### 第三步：验证输出

检查模块概览表用例数一致性、必填字段非空、Markdown 语法正常。

### 第四步：告知用户

报告生成文件路径、用例总数和模块数。

---

## 反向转换：md → xlsx

### 第一步：确认输入

1. 用户指定 `.md` 文件路径（须为本技能生成的格式，或遵循相同结构）
2. 用 Read 工具预览，确认包含 `## 模块概览` 和 `### ` 用例编号

### 第二步：执行转换

```bash
python <skill-path>/scripts/md_to_xlsx.py <input.md> [output.xlsx] [选项]
```

**全部 CLI 参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `input` | ✅ | 输入 Markdown 文件路径 |
| `output` | ❌ | 输出 .xlsx 路径（默认与 md 同目录） |
| `--config` | ❌ | 自定义配置文件路径（用于读取列头映射等） |
| `--sheet-name` | ❌ | 输出 Sheet 名称（默认从 md 元信息提取，若无则为 Sheet1） |

### 第三步：验证输出

1. 检查生成的 xlsx 行数与 md 中用例数一致
2. 必填字段（用例编号、模块、用例标题、优先级）非空
3. 如有差异，提示用户人工核查

### 第四步：告知用户

报告生成文件路径、用例总数，以及与原始元信息对比的校验结果。

---

## 自定义配置

所有可变规则都在 `config.json` 中定义。当项目列名或模块有变动时，只需修改此文件。

### config.json 完整结构

```json
{
  "column_aliases": {
    "用例编号": ["用例编号", "测试用例编号", "TC编号", "Case ID"],
    "模块":     ["模块", "功能模块", "Module"],
    "用例标题": ["用例标题", "标题", "TestCase"],
    "优先级":   ["优先级", "Priority"],
    "前置条件": ["前置条件", "Precondition"],
    "测试步骤": ["测试步骤", "Steps"],
    "预期结果": ["预期结果", "Expected"],
    "备注":     ["备注", "Note"],
    "设计方法": ["设计方法", "Method"],
    "需求编号": ["需求编号", "ReqID"]
  },
  "module_names": {
    "F1":  "平台资源池与租户资源管理",
    "F2":  "接入点路由增强"
  },
  "priority_levels": ["P0", "P1", "P2", "P3"],
  "default_group_by": "模块",
  "list_prefixes": ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-", "•", "*"],
  "export_column_names": ["用例编号", "模块", "用例标题", "优先级", "前置条件", "测试步骤", "预期结果", "备注", "设计方法", "需求编号"],
  "expand_module_name": false
}
```

### 各字段详解

| 字段 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `column_aliases` | `dict[str, list[str]]` | 正向 | 标准字段→Excel 列名别名，匹配时大小写不敏感按顺序优先 |
| `module_names` | `dict[str, str]` | 双向 | 模块编号→名称映射，正向用于归一化和概览表，反向用于可选展开 |
| `priority_levels` | `list[str]` | 双向 | 优先级枚举，正向决定概览表列头，反向从概览表解析补充 |
| `default_group_by` | `str` | 正向 | 默认分组字段标准名 |
| `list_prefixes` | `list[str]` | 正向 | 预期结果列表前缀识别列表 |
| `export_column_names` | `list[str]` | 反向 | 输出 xlsx 的列头名称列表，长度须与标准字段数一致（10列），覆盖 `column_aliases[key][0]` 的默认行为 |
| `expand_module_name` | `bool` | 反向 | 设为 `true` 时，模块列输出 `{code} {name}` 长形式 |

### 配置加载优先级

1. `--config` 参数指定的 JSON 文件（最高）
2. 脚本同目录下的 `config.json`
3. 代码内置的极简默认值

### 适配新项目示例

**场景 A：列名不同** — 新项目 Excel 用"TC-ID"表示用例编号，"Severity"表示优先级：

```json
{
  "column_aliases": {
    "用例编号": ["TC-ID", "用例编号"],
    "优先级":   ["Severity", "优先级"]
  }
}
```

**场景 B：新增模块** — Sprint 5 新增 F17 模块：

```json
{
  "module_names": {
    "F17": "新模块名称"
  }
}
```

**场景 C：自定义输出列头** — 交付 xlsx 需要用英文列名：

```json
{
  "export_column_names": ["Case ID", "Module", "Title", "Priority", "Precondition", "Steps", "Expected", "Note", "Method", "Req ID"]
}
```

---

## 双向转换对应关系

### 正向 → 反向映射

| 正向操作 | 反向还原 | 有损性 |
|---------|---------|--------|
| 子模块名归一化 `F1 xxx` → `F1` | 默认仅还原短编号 `F1`；若 `expand_module_name=true` 则还原为 `F1 平台资源池...` | ✅ 可还原 |
| 前置条件加 `> ` 引用块 | 逐行去掉 `> ` 前缀 | ✅ 可还原 |
| 预期结果纯文本行加 `- ` 前缀 | 逐行去掉 `- ` 前缀 | ⚠️ 有损（见下文） |

### 有损转换说明

预期结果的 `- ` 前缀剥离是唯一的有损场景：若原始 Excel 单元格中有不含编号且本身以 `- ` 开头的行，反向转换时无法区分这是自动添加的还是原文自带的副本。实际测试用例中极少出现此类情况，影响可忽略。如有疑虑，可在反向转换后人工核查预期结果列。

---

## 输出格式规范

### 正向输出（Markdown）

```
# [文档标题]

> 来源：[文件名] | Sheet：[sheet名] | 总用例数：[N]

---

## 模块概览

| 模块 | 模块名称 | 用例数 | P0 | P1 | P2 | P3 |
|------|----------|--------|----|----|----|----|
| F1   | xxx      | 38     | 21 | 15 | 2  | 0  |
| **合计** |      | **190**| **120** | ... |

---

## F1 [模块名称]

### TC_RES_001

**标题**：...

**优先级**：P0

**设计方法**：EP

**需求编号**：F1_RES

**前置条件**：

> 1.平台管理员已登录;
> 2.模型库中存在已纳管模型M

**测试步骤**：

1.进入模型管理→模型库选择模型M点击发布;
2.在向导步骤2搜索租户CL0100并勾选

**预期结果**：

1.搜索结果展示CL0100及租户名称;
2.提示发布成功

---
```

### 反向输出（Excel）

- 列头取 `export_column_names` 或 `column_aliases[key][0]`
- 首行冻结、自动列宽、单元格自动换行
- 数据行按模块章节顺序排列

---

## 特殊场景处理

| 场景 | 处理方式 |
|------|---------|
| 多 Sheet 页 | 正向：`--sheet` 指定；反向：`--sheet-name` 指定输出名称 |
| 合并单元格 | pandas 自动取左上角值 |
| 单元格换行 | 正向保留换行；反向还原换行符 |
| 列名不匹配 | 提示修改 config.json 的 `column_aliases` |
| 模块名变动 | 引导修改 `module_names`，或 `--module-names` 追加 |
| 编号超过 9 步 | 正向内置 1-99 正则匹配；反向自动识别多位编号 |
| md 格式不规范 | 反向解析时跳过无法识别的行并在控制台提示 |