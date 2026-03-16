---
name: pm3-business-rule-extractor
description: |
  【第四步】从 PRD 解析报告中提炼复杂业务规则，设计工作流集成和非功能性需求。
  输入: prd-parse-report.md + domain-model-report.md + api-design-report.md
  输出: business-rules-report.md
  触发场景："提炼业务规则"、"工作流设计"、"/pm3-rules"
compatibility:
  tools: [Read, Write, AskUserQuestion]
  requires: ["pm3-prd-parser", "pm3-domain-modeler", "pm3-api-designer"]
  output: "02-analyzeprd/{模块名}/{功能点名}/business-rules-report.md"
---

# PM3 Step 4: 业务规则提炼器

## 职责边界

**只做这些**:
- 将 PRD 业务规则转化为伪代码/Java方法签名
- 设计工作流变量和回调处理逻辑
- 识别需要分布式锁的并发场景
- 识别需要事务的操作
- 设计版本管理规则（如有）

**不做这些**:
- 不写完整实现代码
- 不生成测试用例（留给 skill-06）

---

## 执行步骤

### Step 1: 规则分类

将 `prd-parse-report.md` 中的业务规则按类型分类：

| 规则类型 | 识别特征 | 处理方式 |
|---------|---------|---------|
| 场景判定规则 | "当A时...当B时..." | 转化为 if-else 伪代码 |
| 字段联动规则 | "根据X自动带出Y" | 描述触发条件和赋值逻辑 |
| 计算规则 | "根据A和B计算C" | 写出计算公式 |
| 版本管理规则 | "审批通过后...旧版本..." | 描述版本切换逻辑 |
| 数据同步规则 | "写入/更新X表" | 描述同步时机和字段映射 |
| 审批决策规则 | "根据意见文本判断..." | 描述解析逻辑 |

### Step 2: 场景判定规则 → 伪代码

对于多场景判定（如首次/二次/重新开工），生成：

```java
// 场景判定方法签名
private SceneType determineSceneType(XxxVO param) {
    // 场景1判定条件: {PRD原文}
    if (条件1) return SceneType.FIRST;

    // 场景2判定条件: {PRD原文}
    if (条件2) return SceneType.SECOND;

    // 场景3判定条件: {PRD原文}
    if (条件3) return SceneType.RESTART;

    throw new BusinessException(BusinessErrorEnum.PARAM_ERROR);
}
```

### Step 3: 计算规则 → 方法签名

```java
// 毛利率资格判定
private Integer calculateXxx(XxxVO param) {
    // 优先级1: {PRD原文描述的条件}
    // 优先级2: {PRD原文描述的备用条件}
    // 默认值: 0
}
```

### Step 4: 版本管理规则

如果存在版本管理（多版本申请、审批后版本切换），描述：
- 新建时的版本初始状态
- 审批通过后的版本切换逻辑
- RESTART（重新开工等）场景的旧版本处理
- 删除草稿时的版本恢复

### Step 5: 工作流集成设计

如果存在审批流程，设计：

**流程定义**:
```yaml
processKey: {resource}-process
businessKey: {实体}.id
```

**流程变量**（从 PRD 审批节点中提取需要在流程中流转的字段）:
```json
{
  "projectId": "",
  "projectName": "",
  "applyNo": "",
  ...
}
```

**审批回调处理逻辑**:
| approvalResult值 | 含义 | 处理动作 |
|----------------|-----|---------|
| 2 | 审批通过 | 更新状态 → 版本切换 → 同步Main表 |
| 3 | 审批驳回 | 更新状态为驳回 |
| 其他 | 未知结果 | 抛出UNKNOWN_APPROVAL_RESULT |

**审批决策解析**（如有）:
```java
private Integer parseApprovalDecision(String approvalOpinion) {
    if (opinion.contains("全面")) return 1;
    ...
}
```

### Step 6: 并发控制设计

识别需要分布式锁的场景（通常是"同一项目不能并发操作"）：

```
锁场景: {描述}
锁Key格式: {resource}_lock:{projectId}（或其他业务唯一键）
锁超时: 30秒
锁获取失败: 抛出 CONCURRENT_OPERATION 异常
```

### Step 7: 事务边界设计

标注哪些操作需要在同一事务内完成：

```
事务1: 暂存草稿
  - 操作1: 保存/更新主表
  - 操作2: 保存/更新附件关联

事务2: 审批通过回调
  - 操作1: 更新审批状态
  - 操作2: 版本切换（更新多条记录）
  - 操作3: 同步Main表
  注意: 操作2和操作3必须原子完成，失败需回滚
```

---

## 输出模板

```markdown
# 业务规则报告 - {功能点名称}

**生成日期**: {日期}

---

## 1. 规则分类汇总

| 规则类型 | 数量 | 复杂度 |
|---------|-----|-------|
| 场景判定 | N | HIGH/MEDIUM/LOW |
| 字段联动 | N | ... |
| 计算规则 | N | ... |
| 版本管理 | N | ... |

---

## 2. 场景判定规则

### 2.1 {判定场景名称}

**触发时机**: {何时调用}

```java
private {ReturnType} {methodName}({ParamType} param) {
    // 判定逻辑伪代码
    // 来源: {PRD原文引用}
}
```

---

## 3. 计算规则

### 3.1 {计算规则名称}

**公式来源**: {PRD原文引用}

```java
private {ReturnType} {methodName}({ParamType} param) {
    // BigDecimal threshold = new BigDecimal("5.0000"); // 阈值来自业务参数配置
    // 计算逻辑
}
```

---

## 4. 版本管理规则（如有）

| 场景 | 版本处理逻辑 | 涉及字段 |
|-----|------------|---------|
| 新建申请 | ... | current_version=0 |
| 审批通过 | ... | current_version=1 |
| 删除草稿 | ... | 恢复preVersionId记录 |

---

## 5. 工作流集成

### 5.1 流程定义

| 属性 | 值 |
|-----|---|
| 流程Key | `{resource}-process` |
| 业务主键 | {实体}.id |

### 5.2 流程变量

```json
{
  // 从PRD审批节点中需要用到的字段
}
```

### 5.3 审批回调处理

```java
// completeTask 方法伪代码
public void completeTask(CompleteTaskDTO dto) {
    switch(dto.getApprovalResult()) {
        case "2": // 通过
            // 1. 更新状态
            // 2. 版本切换
            // 3. 同步Main表
            break;
        case "3": // 驳回
            // 更新状态为驳回
            break;
        default:
            throw new BusinessException(UNKNOWN_APPROVAL_RESULT);
    }
}
```

---

## 6. 并发控制

| 场景 | 锁Key | 超时 | 失败处理 |
|-----|------|-----|---------|
| {场景描述} | `{resource}_lock:{projectId}` | 30s | CONCURRENT_OPERATION |

---

## 7. 事务边界

| 操作 | 事务内步骤 | 失败回滚范围 |
|-----|---------|-----------|
| 暂存草稿 | 主表 + 附件 | 全部回滚 |
| 审批通过 | 状态更新 + 版本切换 + Main表 | 全部回滚 |

---

## 8. 待确认项

- [TODO-RULE-01] {问题}
```
