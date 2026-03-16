---
name: pm3-superpower-spec-generator
description: |
  当用户需要基于 PRD 生成 PM3 后端技术规格说明书时触发。
  必须使用的场景：用户提到"生成技术规格"、"PRD转技术文档"、
  "/pm3-superpower"、"写开发规格"、"从PRD生成技术文档"等关键词时。
  当用户需要把产品需求转化为后端技术语言时，必须使用此skill。
  如果用户提供了 PRD 文档或功能索引.md，并需要生成开发文档，立即触发。
compatibility:
  tools: [Read, Edit, Write, Bash, AskUserQuestion]
  requires: []
  optional_deps: []
---

# PM3 Superpower Spec Generator

## 核心理念：渐进式生成，过程即资产

> 本 skill 采用**五步渐进式**工作流。每一步产出一份独立的过程文档，
> 既是下一步的输入，也是可检查、可回溯的中间资产。
> 最终的 spec 文档由第五步汇总合成，面向开发交付。

```
PRD (原始输入)
  │
  ▼ Step 1: pm3-prd-parser
prd-parse-report.md          ← 原始信息提取，不推断
  │
  ▼ Step 2: pm3-domain-modeler
domain-model-report.md       ← 实体/字段/DDL/状态机
  │
  ▼ Step 3: pm3-api-designer
api-design-report.md         ← API/VO/权限/异常枚举
  │
  ▼ Step 4: pm3-business-rule-extractor
business-rules-report.md     ← 业务规则伪代码/工作流/并发设计
  │
  ▼ Step 5: pm3-spec-assembler
{功能点}-spec.md             ← 最终交付文档（面向开发）
```

**文件存储位置**:
```
02-analyzeprd/{模块名}/{功能点名}/
  ├── prd-parse-report.md       (Step 1 输出)
  ├── domain-model-report.md    (Step 2 输出)
  ├── api-design-report.md      (Step 3 输出)
  └── business-rules-report.md  (Step 4 输出)

03-coding/deliverydoc/
  └── {功能点名}-spec.md        (Step 5 输出，交付物)
```

---

## 上下文预算硬性约束（必须遵守）

| 内容 | Token 上限 | 读取策略 |
|------|-----------|---------|
| PRD 内容 | ≤ 40K tokens | **仅读取目标模块行范围，禁止全文加载** |
| 过程报告（Step 2-5 读取前序报告） | ≤ 15K tokens | 只读当前步骤需要的报告 |
| 引用文档合计 | ≤ 5K tokens | 按需加载对应小节 |
| 单次输出 | ≤ 20K tokens | 超出则分两阶段生成 |

---

## 输入格式

```
/pm3-superpower-spec-generator <模块名称> <功能点名称> [--step N] [选项]
```

**示例**:
```bash
# 全流程一键生成（依次执行5步）
/pm3-superpower-spec-generator 开工管理 开工申请

# 只执行某一步
/pm3-superpower-spec-generator 开工管理 开工申请 --step 1
/pm3-superpower-spec-generator 开工管理 开工申请 --step 2

# 从某步开始（跳过已完成的步骤）
/pm3-superpower-spec-generator 开工管理 开工申请 --from-step 3

# 指定 PRD 文件路径
/pm3-superpower-spec-generator 开工管理 开工申请 --prd "docs/国内工程管理_PRD.md"

# 跳过某章节（传到 Step 5）
/pm3-superpower-spec-generator 开工管理 开工申请 --skip-chapters "8"
```

### 选项说明

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--step N` | 只执行第 N 步 | 全流程 |
| `--from-step N` | 从第 N 步开始（前序步骤已完成） | 第1步 |
| `--prd <路径>` | 指定 PRD 文件路径 | 自动探测 |
| `--skip-chapters` | 跳过 spec 某些章节（传入 Step 5） | 无 |
| `--no-confirm` | 跳过交互确认 | false |

---

## 执行流程

### ▶ Phase 0: PRD 智能切片（所有步骤的前置）

> 任何情况下都必须先执行，禁止跳过。

#### 0.1 定位 PRD 文件

优先级：
1. `--prd` 参数指定的路径
2. `Glob` 扫描 `20_项目/PM3/01-prd/` 和 `docs/` 目录
3. 找到多个时用 `AskUserQuestion` 确认

#### 0.2 读取目录（仅前 150 行）

```
Read(file=<prd_path>, offset=1, limit=150)
```

提取所有 `## ` 二级标题，构建模块行号索引：
```
模块名 → { start_line, end_line }
```

#### 0.3 读取目标模块切片

```
Read(file=<prd_path>, offset=<start_line>, limit=<行数>)
```

**超大模块处理**（> 120K 字符时触发）:
1. 在模块切片内提取 `#### ` 四级标题（功能点列表）
2. 用 `AskUserQuestion` 让用户选择本次处理的功能点
3. 仅读取：功能点行范围 + 模块前 100 行（业务流程/角色定义）

---

### ▶ Step 1: PRD 解析（pm3-prd-parser）

**输入**: Phase 0 的 PRD 切片（内存中）
**输出**: `02-analyzeprd/{模块名}/{功能点名}/prd-parse-report.md`
**上下文消耗**: PRD切片（≤40K tokens）+ 输出（≤8K tokens）

**执行内容**（详见 `references/01-prd-parser.md`）:

1. 定位功能点行范围
2. 提取：功能描述原文、字段清单、按钮清单、状态清单、业务规则原文、审批流程、外部依赖
3. 标记所有 [UNCLEAR] 待确认项

**关键原则**: 只提取，不推断。所有内容必须有 PRD 原文依据。

**完成后展示**:
```
✓ Step 1 完成: prd-parse-report.md
  - 字段: N 个（含 N 个待确认）
  - 按钮: N 个
  - 状态: N 个
  - 业务规则: N 条
  - 审批节点: N 个
  继续执行 Step 2？[Y/n]
```

---

### ▶ Step 2: 领域建模（pm3-domain-modeler）

**输入**: `prd-parse-report.md`
**输出**: `02-analyzeprd/{模块名}/{功能点名}/domain-model-report.md`
**上下文消耗**: Step1报告（≤8K）+ 输出（≤12K tokens）

**执行内容**（详见 `references/02-domain-modeler.md`）:

1. 字段名 → Java类型 + DB类型（按内置规则推断）
2. 判断是否需要附属表（Main表、关联表）
3. 生成 ASCII ER 图
4. 推导状态机（Mermaid 状态图 + 枚举代码）
5. 生成 DDL 建表语句（含索引建议）

**标记 [TODO-TYPE] 无法推断的字段类型。**

**完成后展示**:
```
✓ Step 2 完成: domain-model-report.md
  - 实体数: N 个
  - 总字段: N 个（含 N 个 [TODO-TYPE]）
  - 状态数: N 个
  继续执行 Step 3？[Y/n]
```

---

### ▶ Step 3: API 设计（pm3-api-designer）

**输入**: `prd-parse-report.md` + `domain-model-report.md`
**输出**: `02-analyzeprd/{模块名}/{功能点名}/api-design-report.md`
**上下文消耗**: Step1+2报告（≤15K）+ 输出（≤10K tokens）

**执行内容**（详见 `references/03-api-designer.md`）:

1. 按钮清单 → API 列表（路径、HTTP方法）
2. 生成权限标识（`engineering:{resource}:{操作}`）
3. 设计 VO 字段（可编辑字段）和 QueryParam 字段（查询条件）
4. 枚举所有异常场景 → `BusinessErrorEnum` 追加项

**完成后展示**:
```
✓ Step 3 完成: api-design-report.md
  - API数量: N 个（含 N 个内部接口）
  - 权限标识: N 个
  - 异常枚举: N 个
  继续执行 Step 4？[Y/n]
```

---

### ▶ Step 4: 业务规则提炼（pm3-business-rule-extractor）

**输入**: `prd-parse-report.md` + `domain-model-report.md` + `api-design-report.md`
**输出**: `02-analyzeprd/{模块名}/{功能点名}/business-rules-report.md`
**上下文消耗**: Step1-3报告（≤20K）+ 输出（≤10K tokens）

> ⚠️ 若三份报告合计超过 20K tokens，改为只读 Step1 报告 + Step3 报告（跳过 Step2）。
> Step2 的实体信息已经在 Step3 报告中有所引用，通常不需要重复加载。

**执行内容**（详见 `references/04-business-rule-extractor.md`）:

1. 将 PRD 业务规则分类（场景判定/字段联动/计算规则/版本管理）
2. 将规则转化为 Java 方法伪代码（含方法签名）
3. 设计工作流变量和审批回调处理
4. 识别并发控制场景（分布式锁设计）
5. 标注事务边界

**完成后展示**:
```
✓ Step 4 完成: business-rules-report.md
  - 业务规则: N 条（已转化为伪代码）
  - 工作流变量: N 个
  - 需要分布式锁: Y/N
  - 需要附加事务: N 处
  继续执行 Step 5（最终合成）？[Y/n]
```

---

### ▶ Step 5: Spec 合成（pm3-spec-assembler）

**输入**: 前4步的所有报告
**输出**: `03-coding/deliverydoc/{功能点名}-spec.md`（最终交付）
**上下文消耗**: 4份报告摘要（≤20K）+ 输出（≤25K tokens，允许超）

> Step 5 采用两阶段生成（先骨架再填充），以避免单次输出超长。

**执行内容**（详见 `references/05-spec-assembler.md`）:

**第一阶段（骨架）**: 生成含完整目录的骨架文档，章节正文用 `[PENDING]` 占位
**第二阶段（填充）**: 逐章节用 `Edit` 替换 `[PENDING]`，每次填充 1-2 章节

填充顺序：
```
1→2→3→4→5→6→7→8→9→10 （可用 --skip-chapters 跳过某章节）
```

**完成后展示**:
```
✓ Step 5 完成: 03-coding/deliverydoc/{name}-spec.md
  总章节: 10
  API数量: N
  实体数量: N
  残留待确认项: N 个（见文档附录B）
```

---

## 快速恢复机制

如果某次会话中断，下次可以：
1. 检查 `02-analyzeprd/{模块名}/{功能点名}/` 目录下已有哪些报告
2. 使用 `--from-step N` 从中断处继续

```bash
# 检查进度
ls 02-analyzeprd/开工管理/开工申请/

# 从 Step 3 继续（Step 1、2 已完成）
/pm3-superpower-spec-generator 开工管理 开工申请 --from-step 3
```

---

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| PRD 文件未找到 | 提示用 `--prd` 指定路径 |
| 模块名匹配不到 | 展示所有 `##` 标题，让用户选择 |
| 模块切片 > 120K 字符 | 触发二次切片，让用户选择功能点 |
| 前序报告不存在 | 报告缺少哪个文件，提示先执行对应步骤 |
| 字段类型无法推断 | 标记 [TODO-TYPE]，不猜测 |
| 上下文接近上限 | 停止当前步骤，提示用 `--from-step` 继续 |

---

## 附录：你的 PRD 文件参考数据

> 基于 `国内工程管理_PRD.md` 实测：

| 模块名称 | 字符数 | 包含功能点 | 建议执行策略 |
|---------|-------|---------|-----------|
| 开工管理 | ~94,500 | 业务参数配置/开工申请/二次开工/重新开工/审批 | 每次选 1-2 个功能点 |
| 施工组织总设计方案评审 | ~19,800 | 评审申请/变更重提 | 可一次处理 |

---

## 附录：各步骤引用的 Skill 文件

| 步骤 | Skill 文件 |
|-----|-----------|
| Step 1 | `references/01-prd-parser.md` |
| Step 2 | `references/02-domain-modeler.md` |
| Step 3 | `references/03-api-designer.md` |
| Step 4 | `references/04-business-rule-extractor.md` |
| Step 5 | `references/05-spec-assembler.md` |
