---
name: pm3-spec-assembler
description: |
  【第五步·最终交付】将前四步的报告汇总合成为完整的 spec 技术规格文档。
  这是面向开发的最终交付物，不再包含过程标注。
  输入: prd-parse-report + domain-model-report + api-design-report + business-rules-report
  输出: {功能点名}-spec.md（交付文档）
  触发场景："生成spec"、"合成文档"、"/pm3-assemble"
compatibility:
  tools: [Read, Write, AskUserQuestion]
  requires: ["pm3-prd-parser", "pm3-domain-modeler", "pm3-api-designer", "pm3-business-rule-extractor"]
  input: "02-analyzeprd/{模块名}/{功能点名}/*.md"
  output: "05-coding/deliverydoc/{功能点名}-spec.md"
---

# PM3 Step 5: Spec 合成器（最终交付）

## 职责边界

**只做这些**:
- 读取4份过程报告
- 按交付 spec 模板结构汇总
- 补充非功能性需求（性能/并发/日志/异常处理）
- 生成代码文件路径清单（附录）
- 移除过程中的 [TODO] 待确认项（已确认）或将其集中展示

**输出原则**:
- 面向开发人员，不留过程痕迹
- 所有章节完整，无占位符
- 代码示例使用真实的类名/表名/路径

---

## 执行步骤

### Step 0: 完整性检查

读取以下4个文件，**全部存在才能继续**：

```
02-analyzeprd/{模块名}/{功能点名}/prd-parse-report.md       ✓/✗
02-analyzeprd/{模块名}/{功能点名}/domain-model-report.md    ✓/✗
02-analyzeprd/{模块名}/{功能点名}/api-design-report.md      ✓/✗
02-analyzeprd/{模块名}/{功能点名}/business-rules-report.md  ✓/✗
```

缺失时，报告缺哪个文件，提示执行对应 skill。

### Step 1: 汇总读取

读取全部4个文件，建立字段索引：

```
来源映射:
  spec.第1章  ← prd-parse-report.第1节（功能描述）
  spec.第2章  ← prd-parse-report.第6节 + business-rules-report.第2节
  spec.第3章  ← domain-model-report.第2-5节
  spec.第4章  ← api-design-report.第1-4节
  spec.第5章  ← domain-model-report.第5节（DDL）
  spec.第6章  ← business-rules-report.第2-4节
  spec.第7章  ← api-design-report.第1节（权限列）
  spec.第8章  ← business-rules-report.第5节
  spec.第9章  ← prd-parse-report.第7节 + business-rules-report.第6节
  spec.第10章 ← 根据复杂度生成标准模板
```

### Step 2: 处理残留 [TODO]

检查4份报告中的所有 `[TODO]` 标记：

- **已在过程中确认的**: 填入确认结果，删除标记
- **仍未确认的**: 集中到 spec 末尾"待确认项"附录
- **不影响开发的**: 直接标注合理默认值并注明

### Step 3: 补充非功能性需求

根据功能特征生成非功能性需求：

| 功能特征 | 自动补充的需求项 |
|---------|--------------|
| 列表查询 | 响应时间 < 500ms |
| 单条查询 | 响应时间 < 200ms |
| 暂存操作 | 响应时间 < 1s |
| 包含BPM流程 | 提交审批 < 2s（含流程启动） |
| 并发控制 | 支持100+并发，Redis分布式锁 |
| 审批状态变更 | Spring事务，rollbackFor=Exception.class |
| 日志规范 | 操作日志格式（方法开始/操作类型/结果） |

### Step 4: 生成代码文件路径清单

根据实体名和模块路径，生成附录A：

```
基础路径: {项目根路径}/{service-module}/src/main/java/com/sungrow/pm/{module}/

Controller: .../controller/{EntityName}Controller.java
Service接口: .../service/{EntityName}Service.java
Service实现: .../service/impl/{EntityName}ServiceImpl.java
Entity主表: .../entity/{EntityName}.java
Entity附表: .../entity/{EntityName}Main.java（如有）
VO: .../vo/{FeatureName}VO.java
QueryParam: .../dto/query/{FeatureName}QueryParam.java
枚举: .../enums/{Name}StatusEnum.java
常量: .../constants/{Name}SceneType.java（如有场景判定）
异常枚举追加: .../exception/BusinessErrorEnum.java
SQL主表: .../resources/db/{table_name}.sql
SQL附表: .../resources/db/{table_name}_main.sql（如有）
```

### Step 5: 写入最终文档

写入路径: `05-coding/deliverydoc/{功能点名称-kebab-case}-spec.md`

写完后输出摘要：
```
✓ Spec 文档已生成: 05-coding/deliverydoc/{name}-spec.md
  - 章节数: 10
  - API数量: N
  - 实体数量: N
  - 残留待确认项: N 个（见文档末尾附录B）
```

---

## 输出模板（完整 spec 结构）

```markdown
# {功能点名称}({EnglishName}) 功能AI开发技术规格书

**文档版本**: 1.0
**创建日期**: {日期}
**适用范围**: AI辅助开发
**作者**: Claude Code

---

## 1. 功能概述

### 1.1 功能背景
{来自 prd-parse-report 第1节}

### 1.2 功能目标
{提炼自功能描述，列表形式}

### 1.3 业务范围
| 业务场景 | 说明 |
|---------|------|
| {场景} | {说明} |

---

## 2. 业务流程

### 2.1 核心业务流程图
{ASCII 流程图，来自 business-rules-report}

### 2.2 场景类型判定逻辑（如有多场景）
{Java伪代码，来自 business-rules-report 第2节}

### 2.3 操作类型判定（如有）
{判定规则表格}

---

## 3. 数据模型

### 3.1 核心实体关系图
{ASCII ER图，来自 domain-model-report}

### 3.2 实体字段详细说明
{字段表格，来自 domain-model-report}

---

## 4. API 设计

### 4.1 REST API 列表
{接口列表表格，来自 api-design-report}

### 4.2 核心 API 详细说明
{每个核心接口的请求/响应/规则，来自 api-design-report}

---

## 5. 数据库设计

### 5.1 主表结构
{DDL，来自 domain-model-report}

### 5.2 附属表结构（如有）
{DDL}

---

## 6. 业务规则

### 6.1 场景类型判定规则
{规则表格 + Java伪代码}

### 6.2 各场景必填校验规则
{分场景的校验规则}

### 6.3 计算规则（如有）
{计算方法伪代码}

### 6.4 版本管理规则（如有）
{版本切换规则表格}

---

## 7. 权限控制

### 7.1 接口权限清单
{权限标识表格，来自 api-design-report}

### 7.2 数据权限
{数据过滤规则，来自 PRD 查询条件}

---

## 8. 工作流集成（如有审批流）

### 8.1 流程定义
{流程Key、业务主键等}

### 8.2 流程变量
{JSON格式的流程变量}

### 8.3 审批回调处理
{回调处理逻辑表格 + 伪代码}

---

## 9. 依赖关系

### 9.1 内部依赖
{依赖模块表格}

### 9.2 外部依赖
{Redis/MySQL/Nacos等}

### 9.3 关键常量定义（如有）
{Java常量代码块}

---

## 10. 非功能性需求

### 10.1 性能要求
{性能指标表格}

### 10.2 数据一致性
{事务和一致性描述}

### 10.3 并发控制（如有）
{Redis分布式锁设计}

### 10.4 日志规范
{操作日志和异常日志格式}

### 10.5 异常处理
{异常枚举表格，来自 api-design-report}

### 10.6 扩展性考虑
{可扩展的设计点}

---

## 附录

### A. 关键代码文件路径
{代码文件路径表格}

### B. 待确认项（如有残留）
{所有未解决的 TODO 项}

### C. 版本历史
| 版本 | 日期 | 修改内容 | 作者 |
|-----|------|---------|------|
| 1.0 | {日期} | 初始版本 | Claude Code |
```

---

## 质量检查

- [ ] 10个章节全部有内容，无空章节
- [ ] 所有 [TODO] 已处理（确认或集中到附录B）
- [ ] DDL 包含完整注释
- [ ] API 请求参数与 VO 字段一致
- [ ] 权限标识格式统一
- [ ] 附录A代码路径基于真实项目结构
