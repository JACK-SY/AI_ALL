# CLAUDE.md

本项目为鼎捷雅典娜AI模型运控平台的QA测试管理工作区，不含源代码。

## 项目性质

纯文档项目，所有内容均为中文。从 Sprint 4 起正式启用本工作区进行测试管理（Sprint 1~3 为回溯建档）。

## 目录结构与用途

| 目录 | 用途 | 备注 |
|------|------|------|
| `.sdd/` | AI-SDD框架缓存（PRD模板、参考文档、需求文件） | 仅 `requirement/` 有内容，`specification/` `task/` 未启用 |
| `.trae/skills/` | Trae 技能 Junction 链接 | 指向 `C:\Users\osshenyang\.agents\skills\` |
| `需求文档/` | Sprint需求文档存档 | Word 格式历史存档，新需求以知识库 PRD 为准 |
| `测试用例/` | 测试用例 Excel 交付件 + Markdown 源文件 | Sprint4 起新产出需同时有 Markdown 源 |
| `测试分析报告/` | 测试分析报告 + 测试计划 | Markdown 为源，Word 为交付导出 |
| `测试规范档案/` | 7份测试规范文档 | 均 Markdown，不可导出 |
| `历史BUG库/` | 历史缺陷记录 | Excel 格式 |
| `版本快照/` | 各Sprint版本快照 | Markdown，含机制说明与 S1~S4 快照 |
| `项目概览/` | 平台知识图谱 + 知识库仓库 | 知识库为独立 Git 仓库，**勿修改其内容** |

## 需求权威来源：model-ops-knowledge

**`项目概览/model-ops-knowledge/`** 是本项目的**需求权威来源（Single Source of Truth）**，所有需求理解、PRD引用、测试设计均以该知识库中的文档为准。该目录为团队共用仓库，**不得修改其内容**。

### 权威文档层级（优先级从高到低）

1. **当前活跃PRD**：`项目概览/model-ops-knowledge/projects/model-ops-platform/prd/Sprint4_PRD_模型治理与调用链路增强_评审版.md`
2. **领域术语定义**：`项目概览/model-ops-knowledge/CONTEXT.md`
3. **产品边界与协作流程**：`项目概览/model-ops-knowledge/projects/model-ops-platform/overview/产品边界与协作流程.md`
4. **信息架构与页面设计**：`项目概览/model-ops-knowledge/projects/model-ops-platform/wireframes/Sprint4_信息架构与页面设计草案.md`
5. **架构决策记录（ADR）**：`项目概览/model-ops-knowledge/docs/adr/`（共13份，ADR与Sprint决策记录冲突时以ADR为准）
6. **Sprint决策记录**：`项目概览/model-ops-knowledge/projects/model-ops-platform/overview/Sprint4_决策记录.md`
7. **技术方案**：`项目概览/model-ops-knowledge/projects/model-ops-platform/tech-specs/`
8. **本地简化PRD**：`.sdd/requirement/` — 仅作为AI-SDD技能的输入缓存，与知识库PRD冲突时以知识库为准

### 归档文档说明

`项目概览/model-ops-knowledge/projects/model-ops-platform/archive/` 下的内容（含 `legacy-before-s4/` 与 `s4-superseded/`）仅用于历史追溯，**不参与**当前需求理解、测试设计或追溯矩阵构建，除非用户明确要求。

## 需求同步机制

### 读取最新PRD的方式

- **测试用例生成时**：优先读取 `项目概览/model-ops-knowledge/projects/model-ops-platform/prd/` 下的当前PRD，而非 `.sdd/requirement/` 下的缓存
- **需求解析时**：优先使用知识库 `CONTEXT.md` 进行术语消歧，而非自行推测
- **交叉验证时**：若本地 `.sdd/requirement/` 与知识库PRD存在差异，以知识库版本为准，并在输出中标注差异点

### 同步触发时机

| 触发场景 | 操作 |
|----------|------|
| 启动新Sprint测试工作时 | 读取知识库对应Sprint的PRD，提取需求结构与验收条件 |
| 知识库PRD有更新时 | 重新解析变更部分，标注受影响的测试用例 |
| 生成版本快照时 | 快照中记录所引用的知识库PRD文件名与版本状态 |
| 发现需求歧义时 | 对照知识库 `CONTEXT.md` 术语定义和 `docs/adr/` 决策记录澄清 |

### 知识库推荐阅读顺序

1. `CONTEXT.md` — 领域术语
2. `projects/model-ops-platform/overview/产品边界与协作流程.md` — 产品范围
3. `projects/model-ops-platform/prd/Sprint4_PRD_模型治理与调用链路增强_评审版.md` — 当前PRD
4. `projects/model-ops-platform/wireframes/Sprint4_信息架构与页面设计草案.md` — 信息架构
5. `docs/adr/` — 架构决策

## 产出物格式策略

### 格式标准

| 产出物 | 源格式（优先） | 交付格式 | 说明 |
|--------|---------------|----------|------|
| 需求文档 | Markdown | Word (.docx) | Markdown为源，Word为正式交付导出 |
| 测试用例 | Markdown（规范列定义） | Excel (.xlsx) | Markdown便于追溯与diff，Excel为交付格式 |
| 测试分析报告 | Markdown | Word (.docx) | Markdown为源，Word为交付导出 |
| 测试计划 | Markdown | Word (.docx) | 同上 |
| 版本快照 | Markdown | — | 仅Markdown，不导出 |
| 测试规范 | Markdown | — | 仅Markdown，不导出 |
| 历史BUG | Excel (.xlsx) | — | 原始记录即为Excel，无需转换 |

### 原则

1. **Markdown优先**：所有可文本化的产出物优先使用Markdown编写，确保可diff、可追溯、可PR
2. **Office交付**：正式交付物允许导出为Word/Excel，但源文件必须保留Markdown版本
3. **禁止二进制入库**：图片使用相对路径引用放 `assets/` 目录下；Office文件仅在交付目录中保留，不在 `.sdd/` 等工作目录中保存
4. **命名规范**：文件命名统一格式为 `Sprint{N}_{产出物类型}_{主题}.{扩展名}`
5. **版本标识统一**：全部使用 `Sprint{N}` 格式，不再使用 Q1/Q2/Q3 或 S1/S2/S3
6. **存量豁免**：Sprint1~3 历史产出物免除 Markdown 源文件要求；Sprint4 起严格执行

## 可用技能

### 本地技能（.claude/skills）
- `SY-generate-test-cases` — AI辅助测试用例生成流水线（6阶段5门禁）
- `generate-prd` — 从业务需求生成完整PRD文档
- `generate-test-docs` — 自主学习型测试文档生成器

### Trae 技能链接（.trae/skills → C:\Users\osshenyang\.agents\skills）
- `SY-generate-test-cases` — 同上，Trae IDE 内使用
- `tdd` — 测试驱动开发
- `to-issues` — 需求/文档拆分为 GitHub Issues
- `to-prd` — 快速生成 PRD 草稿
- `grilling` — 文档深度质询与澄清

## AI-SDD框架

- 配置文件：`.sdd-config.json`（`lang: "zh"`, `root: ".sdd"`）
- 文档依赖链：`CONSTITUTION.md → requirement/ → specification/ → task/ → implementation`
- 当前仅 `requirement/` 阶段有实际内容（`specification/` `task/` `implementation` 目录未创建）
- PRD模板使用SysML需求图（Mermaid `requirementDiagram`语法）、状态图（`stateDiagram-v2`）和用例图
- 双专家评审：产品策略专家 + UX专家，补充内容以 `【补充】` 标记

## 测试规范核心规则

**用例标题格式**（严格遵守）：`【# 需求编号_模块_功能】场景类型：测试点`

**优先级**：P0/P1/P2/P3，由设计方法+风险因子矩阵自动推导得出，不对各优先级占比设目标比例，仅对最终分布做事后统计

**设计方法标注**（每条必填）：EP / BVA / ST / EG，可组合如 EP+BVA

**优先级自动判定**：设计方法类型 + 风险因子矩阵 → 自动推导，非人工主观

**需求追溯**：双向追溯，覆盖率计算，孤立项检测

## 平台业务域

7个知识域：业务域（模型市场/体验中心/接入点/模型实验室/模型数据/模型管理/模型观测/基础设置）、系统架构域、数据资产域、运维故障域、开发流程域、组织权限域、安全合规域

**核心业务流**：模型上架→部署→发布→市场展示；接入点创建→关联模型→业务集成

**当前Sprint重点**：Sprint 4 — 模型治理与调用链路增强

## 关键参考文件

| 文件 | 说明 |
|------|------|
| `项目概览/model-ops-knowledge/projects/model-ops-platform/prd/Sprint4_PRD_模型治理与调用链路增强_评审版.md` | **当前有效PRD基线** |
| `项目概览/model-ops-knowledge/CONTEXT.md` | 领域术语定义（约70个核心术语） |
| `项目概览/model-ops-knowledge/docs/adr/` | 架构决策记录（ADR 0001~0013） |
| `项目概览/model-ops-knowledge/projects/model-ops-platform/overview/Sprint4_决策记录.md` | Sprint4决策（约50条） |
| `项目概览/model-ops-knowledge/projects/model-ops-platform/overview/Sprint4_技术边界说明.md` | 技术约束与系统契约 |
| `项目概览/鼎捷雅典娜AI模型中心知识图谱.md` | 平台7域知识图谱 |
| `测试规范档案/测试规范总纲.md` | 测试规范主文件 |
| `测试规范档案/需求解析规则规范.md` | 需求ID提取正则与场景流识别关键词 |
| `测试规范档案/技能已知问题与改进追踪.md` | 技能缺陷与改进状态 |
| `版本快照/版本快照.md` | Sprint1~4版本记录 |
| `.sdd/requirement/sprint2-model-platform.md` | 历史PRD缓存（status: archived） |
