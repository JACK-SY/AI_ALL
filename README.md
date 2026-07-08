# AI模型运控平台 — QA测试管理工作区

鼎捷雅典娜AI模型运控平台（`https://ai-hub.digiwincloud.com.cn`）的测试管理工作区，纯文档项目，不含源代码。

## 项目状态

| 维度 | 说明 |
|------|------|
| 当前迭代 | **Sprint 4 — 模型治理与调用链路增强** |
| 项目启用 | Sprint 4 起正式启用本工作区（Sprint 1~3 为回溯建档） |
| 需求权威来源 | [`项目概览/model-ops-knowledge/`](项目概览/model-ops-knowledge/) （团队共用仓库，勿修改） |

## 目录结构

```
AI_ALL/
├── CLAUDE.md                  # Claude Code 项目指导文件
├── README.md                  # 本文件
├── .sdd-config.json           # AI-SDD 框架配置
│
├── .sdd/                      # AI-SDD 框架缓存
│   ├── .cache/generate-prd/   #   PRD 模板 + 参考文档（双专家评审规则等）
│   └── requirement/           #   需求缓存（Sprint2 PRD，已归档）
│
├── .trae/skills/              # Trae 技能 Junction 链接
│   ├── SY-generate-test-cases → ~/.agents/skills/SY-generate-test-cases
│   ├── tdd                  → ~/.agents/skills/tdd
│   ├── to-issues            → ~/.agents/skills/to-issues
│   ├── to-prd               → ~/.agents/skills/to-prd
│   └── grilling             → ~/.agents/skills/grilling
│
├── 需求文档/                   # Sprint 需求文档（Word 格式历史存档）
│   ├── Sprint1_需求文档.docx
│   ├── Sprint2_需求文档.docx
│   └── Sprint3_需求文档.docx
│
├── 测试用例/                   # 测试用例交付件
│   ├── Sprint1_测试用例.xlsx
│   ├── Sprint2_测试用例.xlsx
│   └── Sprint3_测试用例.xlsx
│
├── 测试分析报告/               # 测试分析报告 + 测试计划
│   ├── Sprint1_测试报告.docx
│   ├── Sprint2_测试分析报告.md
│   └── Sprint3_测试报告.docx
│
├── 测试规范档案/               # 测试规范体系（7份）
│   ├── 测试规范总纲.md
│   ├── 测试设计方法规范.md
│   ├── 优先级与回归分类规范.md
│   ├── 需求追溯矩阵规范.md
│   ├── 需求解析规则规范.md
│   ├── 交互模式与流程规范.md
│   └── 技能已知问题与改进追踪.md
│
├── 历史BUG库/                  # 历史缺陷记录
│   ├── Sprint1-2_Bug.xlsx
│   └── Sprint3_Bug.xlsx
│
├── 版本快照/                   # Sprint 版本快照
│   └── 版本快照.md             #   S1~S4 完整快照 + 机制说明
│
└── 项目概览/                   # 平台知识 + 需求权威来源
    ├── 鼎捷雅典娜AI模型中心知识图谱.md
    └── model-ops-knowledge/   #   独立 Git 仓库（勿修改）
        ├── CONTEXT.md         #     领域术语定义（~70个）
        ├── docs/adr/          #     架构决策记录（ADR 0001~0013）
        ├── projects/model-ops-platform/
        │   ├── overview/      #     产品边界、决策记录、技术边界
        │   ├── planning/      #     项目 Backlog
        │   ├── prd/           #     ★ 当前有效 PRD（Sprint4 评审版）
        │   ├── tech-specs/    #     技术方案（7份）
        │   ├── wireframes/    #     信息架构与页面设计草案
        │   └── archive/       #     历史归档（S1~S3 PRD、旧方案）
        └── templates/         #     PRD 模板 + 技术方案模板
```

## Sprint 概览

| Sprint | 主题 | 测试管理 | 说明 |
|--------|------|---------|------|
| Sprint 1 | AI模型运控平台首期交付 | 回溯建档 | 基础能力：模型空间、API Key、使用记录 |
| Sprint 2 | 渠道扩容与向量能力 | 回溯建档 | 10家供应商、Embedding/Rerank、IndepthAI、模型定价 |
| Sprint 3 | 安全围栏专项 | ❌ 未实施 | PRD 已编写但未进入开发/测试，快照仅做需求级建档 |
| **Sprint 4** | **模型治理与调用链路增强** | **正式启用** | 租户资源管理、接入点分离、API Key 治理、Kafka 日志、用量限额 |

## 核心规范

### 用例标题格式（强制）

```
【# 需求编号_模块_功能】场景类型：测试点
```

### 优先级

| 级别 | 含义 | 执行时机 |
|------|------|---------|
| P0 | 阻塞级，核心功能不可用 | 冒烟测试 |
| P1 | 严重级，影响核心业务流程 | 核心回归 |
| P2 | 一般级，次要功能或异常处理 | 全量回归 |
| P3 | 轻微级，边缘场景 | 有空执行 |

> 优先级由设计方法+风险因子矩阵自动推导，不对各优先级占比设目标比例，仅对最终统计数据做事后健康检查。

### 产出物格式

- **Markdown 优先**：所有新建产出物以 Markdown 为源文件
- **Office 交付**：允许导出 Word/Excel 作为正式交付件
- **命名规范**：`Sprint{N}_{产出物类型}_{主题}.{扩展名}`
- **版本标识**：统一 `Sprint{N}`，不再使用 Q1/Q2 或 S1/S2

### 需求同步

所有需求理解引用知识库 PRD，本地 `.sdd/requirement/` 仅作缓存。冲突时以知识库为准。

## 可用技能

| 技能 | 用途 | 来源 |
|------|------|------|
| `SY-generate-test-cases` | AI辅助测试用例生成流水线（6阶段5门禁） | .claude/skills + .trae/skills |
| `generate-prd` | 从业务需求生成完整PRD文档 | .claude/skills |
| `generate-test-docs` | 自主学习型测试文档生成器 | .claude/skills |
| `tdd` | 测试驱动开发 | .trae/skills |
| `to-issues` | 需求/文档拆分为 GitHub Issues | .trae/skills |
| `to-prd` | 快速生成 PRD 草稿 | .trae/skills |
| `grilling` | 文档深度质询与澄清 | .trae/skills |

## 快速开始

1. **了解平台**：阅读 [`项目概览/鼎捷雅典娜AI模型中心知识图谱.md`](项目概览/鼎捷雅典娜AI模型中心知识图谱.md)
2. **读取当前PRD**：[`项目概览/model-ops-knowledge/projects/model-ops-platform/prd/`](项目概览/model-ops-knowledge/projects/model-ops-platform/prd/)
3. **理解测试规范**：[`测试规范档案/测试规范总纲.md`](测试规范档案/测试规范总纲.md)
4. **查看迭代基线**：[`版本快照/版本快照.md`](版本快照/版本快照.md)
5. **启动用例生成**：使用 `/SY-generate-test-cases` 技能

## 关键约定

- 🔒 `项目概览/model-ops-knowledge/` 为团队共用仓库，**不得修改其内容**
- 📝 Sprint4 起新产出物严格执行 Markdown 优先、Office 交付规范
- 🏷️ 文件命名统一 `Sprint{N}_` 前缀，杜绝 Q1/S1 等旧标识
- 📊 版本快照在测试完成后必须生成，统计数据为最终值
- 🔗 技能 Junction 链接指向 `C:\Users\osshenyang\.agents\skills\`，如技能更新请重新链接
