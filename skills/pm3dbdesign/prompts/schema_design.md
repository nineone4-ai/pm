# 表结构设计提示词

## 任务

将提取的数据实体转换为符合 PM3.0 规范的 MySQL 表结构。

## 输入

提取的实体列表（JSON格式）

## 设计规则

### 1. 表名生成规则

根据实体类型和名称生成表名：

```
pm_<模块前缀>_<业务实体名>[_<后缀>]
```

| 实体类型 | 后缀 | 示例 |
|---------|------|------|
| 主实体 | 无 | 线索 → pm_clue |
| 附件实体 | attachment | 线索附件 → pm_clue_attachment |
| 申请单实体 | apply | 线索申请 → pm_clue_apply |
| 审批单实体 | approval | 线索审批 → pm_clue_approval |
| 关联实体 | 关联对象名 | 开发权线索 → pm_dev_right_clue |

模块前缀映射：

| 模块 | 前缀 | 示例 |
|------|------|------|
| 线索管理 | clue | pm_clue_xxx |
| 开发权管理 | dev_right | pm_dev_right_xxx |
| 预立项管理 | pre_project | pm_pre_project_xxx |
| 立项管理 | project | pm_project_xxx |
| 指标管理 | quota | pm_quota_xxx |

### 2. 字段映射规则

#### 2.1 类型映射

| 需求类型 | 需求长度/格式 | MySQL类型 |
|---------|-------------|----------|
| 文本 | N字符 | VARCHAR(N) |
| 文本 | N汉字 | VARCHAR(N*3) |
| 文本 | 无 | VARCHAR(255) |
| 数值 | 精度N位 | DECIMAL(18,N) |
| 数值 | 默认 | DECIMAL(18,2) |
| 数值 | 整数 | BIGINT/INT |
| 日期型 | - | DATE |
| 时间型 | - | DATETIME |
| 布尔值 | - | TINYINT(1) |

#### 2.2 审计字段（所有表必须添加）

```sql
`id` VARCHAR(32) NOT NULL COMMENT '主键ID',
`create_by` VARCHAR(64) DEFAULT NULL COMMENT '创建人ID',
`update_by` VARCHAR(64) DEFAULT NULL COMMENT '更新人ID',
`create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
`update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
`is_del` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0-未删除，1-已删除',
`remark` VARCHAR(1000) DEFAULT NULL COMMENT '备注',
```

#### 2.3 业务字段映射示例

| 原始字段名 | 英文名 | MySQL类型 | 说明 |
|-----------|--------|----------|------|
| 线索ID | clue_id | VARCHAR(16) | 原表主键 |
| 项目名称 | project_name | VARCHAR(384) | 128汉字 |
| 项目总容量 | project_capacity | DECIMAL(18,2) | 精度2位 |
| 获取时间 | obtain_date | DATE | 日期型 |
| 创建时间 | create_time | DATETIME | 审计字段 |
| 线索状态 | clue_status | TINYINT | 字典值转数值 |
| 是否长期有效 | is_long_term | TINYINT(1) | 布尔转数值 |

### 3. 索引设计规则

#### 3.1 必建索引

```sql
-- 主键索引（自动创建）
PRIMARY KEY (`id`)

-- 软删除索引（所有表必须）
KEY `idx_<表名>_is_del` (`is_del`)
```

#### 3.2 选建索引

| 场景 | 索引类型 | 命名规则 |
|------|---------|---------|
| 业务唯一字段（编号、编码） | 唯一索引 | uk_<表名>_<字段名> |
| 外键字段 | 普通索引 | idx_<表名>_<字段名> |
| 状态字段 | 普通索引 | idx_<表名>_<字段名> |
| 时间字段 | 普通索引 | idx_<表名>_<字段名> |
| 高频查询字段 | 普通索引 | idx_<表名>_<字段名> |

#### 3.3 组合索引规则

- 等值条件字段在前，范围条件字段在后
- 区分度高的字段在前
- 命名：`idx_<表名>_<字段1>_<字段2>`

### 4. 外键处理规则

**不使用物理外键**，采用逻辑外键：

```sql
-- 不推荐
FOREIGN KEY (`project_id`) REFERENCES `pm_project` (`id`)

-- 推荐（逻辑外键 + 索引）
`project_id` VARCHAR(32) NOT NULL COMMENT '项目ID（关联pm_project.id）',
KEY `idx_<表名>_project_id` (`project_id`) COMMENT '项目ID索引',
```

### 5. 统一表冲突处理

当检测到以下表名时，标记为"复用已有表"，不生成DDL：

| 类型 | 表名模式 | 处理方式 |
|------|---------|---------|
| 身份认证 | idm_* | 复用idm表，通过逻辑外键关联 |
| 权限角色 | permission_* | 复用permission表 |
| 主数据 | mam_*, mdm_* | 复用主数据表 |
| 附件 | pm_attachment | 复用pm_attachment |
| 审批流 | activity_* | 复用Activity工作流 |

## 输出格式

```json
{
  "tables": [
    {
      "table_name": "pm_clue",
      "table_comment": "线索主表",
      "entity_source": "线索数据项",
      "module": "线索管理",
      "is_reuse_existing": false,
      "fields": [
        {
          "field_name": "clue_id",
          "data_type": "VARCHAR",
          "length": "16",
          "nullable": false,
          "default_value": null,
          "comment": "线索ID，原业务主键",
          "is_primary_key": false,
          "is_unique": true,
          "is_foreign_key": false
        },
        {
          "field_name": "id",
          "data_type": "VARCHAR",
          "length": "32",
          "nullable": false,
          "default_value": null,
          "comment": "主键ID",
          "is_primary_key": true,
          "is_unique": true,
          "is_foreign_key": false
        }
      ],
      "indexes": [
        {
          "index_name": "PRIMARY",
          "index_type": "PRIMARY",
          "fields": ["id"],
          "comment": "主键索引"
        },
        {
          "index_name": "uk_pm_clue_clue_id",
          "index_type": "UNIQUE",
          "fields": ["clue_id"],
          "comment": "线索ID唯一索引"
        },
        {
          "index_name": "idx_pm_clue_is_del",
          "index_type": "INDEX",
          "fields": ["is_del"],
          "comment": "软删除标记索引"
        }
      ],
      "ddl": "CREATE TABLE `pm_clue` (...)"
    }
  ]
}
```

## 特殊处理

### 1. 状态字段转换

将文本型状态转换为数值型，提高查询效率：

| 原字段 | 原类型 | 新字段 | 新类型 | 枚举映射 |
|-------|-------|-------|-------|---------|
| 线索状态 | 文本(8汉字) | clue_status | TINYINT | 0-不通过, 1-通过, 2-放弃 |
| 审批状态 | 文本(8汉字) | approval_status | TINYINT | 0-草稿, 1-审批中, 2-审批驳回, 3-审批完成 |

### 2. 附件表处理

优先建议复用 `pm_attachment`：

```sql
-- 不新建附件表，而是：
-- 1. 在业务表中添加 business_type 字段区分业务类型
-- 2. 通过 pm_attachment.business_id 关联业务表
```

如果必须独立管理附件，创建从表：

```sql
CREATE TABLE `pm_clue_attachment` (
  `id` VARCHAR(32) NOT NULL,
  `clue_id` VARCHAR(16) NOT NULL COMMENT '线索ID（关联pm_clue.clue_id）',
  `file_name` VARCHAR(384) NOT NULL COMMENT '文件名称',
  ...
) COMMENT='线索附件表';
```

### 3. 申请单/审批单处理

- 申请单：创建独立的申请单表，记录每次申请的信息
- 审批单：建议复用 Activity 工作流，如需要记录额外审批信息，创建审批记录从表
