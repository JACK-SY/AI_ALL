### 文档依赖关系

#### 创建顺序

文档按以下顺序创建，每个文档引用其上游文档：

```
CONSTITUTION.md → requirement/ (PRD) → specification/*_spec.md → specification/*_design.md → task/ → 实现
```

**方向含义**：`A → B` 表示"B参照A创建"。上游文档是下游文档的真实来源。

- `CONSTITUTION.md`：项目原则（顶层，所有文档必须遵守）
- `requirement/`：PRD/需求文档（根据CONSTITUTION创建）
- `specification/*_spec.md`：抽象规格说明书（从需求派生）
- `specification/*_design.md`：技术设计文档（从规格详细化）
- `task/`：任务日志（从设计分解，临时性）
- `实现`：源代码（根据任务/设计实现）

#### 验证方向

一致性检查按反向验证——从下游回溯到上游：

```
实现 → task/ → specification/*_design.md → specification/*_spec.md → requirement/ → CONSTITUTION.md
```

每个下游文档对照其上游真实来源进行检查。发现不一致时，优先依据上游文档（PRD > 规格说明书 > 设计文档）。

#### 文档持久性

| 文档 | 持久性 | 规则 |
|:--|:--|:--|
| `CONSTITUTION.md` | **持久** | 项目原则。仅通过 `/constitution` 更新 |
| `requirement/*.md` | **持久** | PRD/需求。当业务需求变更时更新 |
| `specification/*_spec.md` | **持久** | 抽象规格说明书。当需求变更时更新 |
| `specification/*_design.md` | **持久** | 技术设计。整合 task/ 中的重要设计决策 |
| `task/` | **临时** | **实现完成后删除**。删除前将重要设计决策迁移至 `specification/*_design.md` |

#### 变更传播

当上游文档变更时，下游文档可能需要更新：

| 变更文档 | 影响范围 | 更新条件 |
|:--|:--|:--|
| `CONSTITUTION.md` | 所有下游 | 原则变更影响所有文档 |
| `requirement/` | `specification/*_spec.md`、`specification/*_design.md` | 新增/变更/删除的需求必须被反映 |
| `specification/*_spec.md` | `specification/*_design.md`、`task/` | API签名、数据模型或行为变更 |
| `specification/*_design.md` | `task/`、实现 | 架构或接口变更 |

**不需要更新的情况**：

- 内部实现优化（无接口变更）
- Bug修复（修正偏离规格的偏差）
- 重构（无行为变更）

#### 交叉引用规则

文档使用需求ID相互引用以保持可追溯性：

| ID格式 | 类型 | 示例 |
|:--|:--|:--|
| `UR-xxx` | 用户需求 | `UR-001`：用户可以登录 |
| `FR-xxx` | 功能需求 | `FR-001`：通过OAuth认证 |
| `NFR-xxx` | 非功能需求 | `NFR-001`：响应时间 < 200ms |

**可追溯链**：

```
requirement/（定义UR/FR/NFR） → specification/*_spec.md（引用FR/NFR） → specification/*_design.md（实现FR/NFR） → task/（覆盖FR/NFR）
```

- `specification/*_spec.md` 必须在其"功能需求"章节中引用PRD需求ID
- `specification/*_design.md` 必须将设计决策追溯到规格需求
- `task/` 必须覆盖所有功能需求（FR-xxx）并考虑非功能需求（NFR-xxx）