---
name: pm3-api-designer
description: |
  【第三步】基于 PRD 解析报告 + 领域模型报告，设计 REST API。
  推导接口路径、请求/响应参数、权限标识、异常枚举。
  输入: prd-parse-report.md + domain-model-report.md
  输出: api-design-report.md
  触发场景："设计接口"、"API设计"、"/pm3-api"
compatibility:
  tools: [Read, Write, AskUserQuestion]
  requires: ["pm3-prd-parser", "pm3-domain-modeler"]
  input: "02-analyzeprd/{模块名}/{功能点名}/*.md"
  output: "02-analyzeprd/{模块名}/{功能点名}/api-design-report.md"
---

# PM3 Step 3: API 设计器

## 职责边界

**只做这些**:
- 从按钮清单推导 API 列表
- 设计请求/响应参数结构（引用实体字段）
- 生成权限标识
- 枚举异常场景和错误码
- 设计 VO / QueryParam 结构

**不做这些**:
- 不设计 BPM 工作流变量（留给 skill-04）
- 不写 Service 实现逻辑（留给 skill-05）

---

## 执行步骤

### Step 1: 读取输入文件

读取（优先级顺序）：
1. `prd-parse-report.md`：获取按钮清单、业务规则
2. `domain-model-report.md`：获取实体字段列表

**两个文件都必须存在才能执行本 skill。**

### Step 2: 按钮 → API 映射

每个按钮对应一个或多个 API。映射规则：

| 按钮类型 | HTTP方法 | 路径模式 | 说明 |
|---------|---------|---------|-----|
| 新建/暂存 | POST | /{resource}/draft | 草稿保存（含新建和编辑） |
| 提交审批 | POST | /{resource}/submit | 先暂存再提交 |
| 查询列表 | GET | /{resource}/page | 分页查询 |
| 查询详情 | GET | /{resource}/{id} | 单条查询 |
| 删除 | DELETE | /{resource}/{id} | 逻辑删除 |
| 导出 | GET | /{resource}/export | Excel导出 |
| BPM回调 | POST | /{resource}/complete-task | 审批回调（内部接口） |
| 预审核/预览 | GET/POST | /{resource}/pre-audit/{id} | 查看预审结果 |
| 实时计算 | POST | /{resource}/realtime-{action} | 实时获取计算结果 |

**路径规则**:
- base path: `/api/pm-engineering/`
- resource: 功能点名称转 kebab-case（如 `start-apply`）
- 完整示例: `/api/pm-engineering/start-apply/draft`

### Step 3: 权限标识生成

格式: `{模块前缀}:{resource}:{操作}`

| 操作 | 权限后缀 |
|-----|---------|
| 暂存/新增 | :draft |
| 提交 | :submit |
| 分页查询 | :list |
| 详情查询 | :detail |
| 删除 | :delete |
| 导出 | :export |
| 预审核 | :pre-audit |
| BPM回调 | （内部接口，无权限标识） |

模块前缀: `engineering`（pm-engineering 服务的固定前缀）

### Step 4: 设计 VO 和 QueryParam

**VO（请求体）**: 包含所有"可编辑"字段（对应 PRD 中非只读字段）
**QueryParam（查询参数）**: 包含所有查询条件字段

对于"自动带出"字段：
- 纳入 VO（前端在暂存时一并传入），标注 `自动带出，不可编辑`

### Step 5: 异常场景枚举

从以下来源收集异常场景：
1. 按钮校验规则（"必填"字段 → 对应一个枚举）
2. 状态守卫（"非草稿状态不可提交" → 对应一个枚举）
3. 业务规则（版本冲突、并发等）
4. 外部依赖失败（BPM 流程启动失败）

生成枚举格式：
```java
PROJECT_ID_REQUIRED("项目ID为空"),
ONLY_DRAFT_SUBMIT("非草稿状态不可提交"),
BPM_PROCESS_START_FAILED("BPM流程启动失败"),
```

---

## 输出模板

```markdown
# API 设计报告 - {功能点名称}

**基于**: prd-parse-report.md + domain-model-report.md
**生成日期**: {日期}

---

## 1. API 列表

| 接口地址 | 方法 | 功能说明 | 权限标识 |
|---------|------|---------|---------|
| /api/pm-engineering/{resource}/draft | POST | 暂存草稿 | engineering:{resource}:draft |
| ... | ... | ... | ... |

---

## 2. 核心 API 详细说明

### 2.1 暂存草稿

**URL**: `POST /api/pm-engineering/{resource}/draft`
**权限**: `engineering:{resource}:draft`

**请求体 ({Name}VO)**:
```json
{
  "id": "",              // 编辑时传，新建不传
  "projectId": "",       // [必填] 项目ID
  ...
}
```

**响应**:
```json
{
  "code": 200,
  "data": "{id}"
}
```

**业务规则**:
1. {来自PRD的规则原文}

**异常**:
| 场景 | 错误码 | 错误信息 |
|-----|-------|---------|
| projectId为空 | 500 | PROJECT_ID_REQUIRED |

---

## 3. VO 字段清单

| 字段名(camelCase) | 类型 | 必填 | 说明 | 来源 |
|----------------|-----|-----|-----|-----|
| id | String | N | 编辑时传 | 主键 |
| ... | ... | ... | ... | ... |

---

## 4. QueryParam 字段清单

| 字段名 | 类型 | 说明 |
|-------|-----|-----|
| pageNum | Integer | 页码 |
| pageSize | Integer | 每页数量 |
| ... | ... | ... |

---

## 5. 异常枚举

```java
// BusinessErrorEnum.java 追加项
{ENUM_NAME}("{描述}"),
```

---

## 6. 待确认项

- [TODO-API-01] {问题}
```

---

## 质量检查

- [ ] 每个 PRD 按钮都有对应 API
- [ ] 权限标识格式统一
- [ ] 异常枚举覆盖所有必填校验
- [ ] BPM 回调接口已标注为内部接口（无权限标识）
- [ ] VO 不包含只读字段（如 applyNo、createTime）
