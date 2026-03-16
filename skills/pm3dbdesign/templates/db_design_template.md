# XXX模块数据库设计文档

> 文档版本：v1.0
> 创建日期：{{create_date}}
> 创建人：Claude (自动生成)
> 最后更新：{{update_date}}

{{conflict_report}}

---

## 1. 概述

### 1.1 文档说明

本文档描述{{module_name}}的MySQL数据库表结构设计，包括表字段定义、索引设计和命名规范。
文档基于需求规格说明书自动生成，遵循PM3.0数据库设计规范。

### 1.2 数据库环境

- **数据库类型**：MySQL 5.7+
- **字符集**：utf8mb4
- **排序规则**：utf8mb4_general_ci
- **存储引擎**：InnoDB

### 1.3 设计原则

- 所有表必须包含审计字段（id、create_by、update_by、create_time、update_time、is_del、remark）
- 使用软删除机制（is_del标记）
- 主键统一使用VARCHAR(32)存储UUID
- 合理设置字段长度和默认值
- 为高频查询字段建立索引
- 复用系统统一表（idm_*, permission_*, mam_*, mdm_*等），不新建此类表

---

## 2. 命名规范

### 2.1 表命名规范

- **格式**：`pm_<模块前缀>_<业务名称>`，全小写，使用下划线分隔
- **示例**：`pm_clue`、`pm_dev_right_main`
- **禁止**：使用保留字、中文、特殊字符

### 2.2 字段命名规范

- **格式**：全小写，使用下划线分隔，见名知意
- **示例**：`clue_id`、`project_name`、`create_time`
- **禁止**：使用保留字、中文、驼峰命名

### 2.3 索引命名规范

| 索引类型 | 命名格式 | 示例 |
|---------|---------|------|
| 主键索引 | PRIMARY | PRIMARY |
| 唯一索引 | uk_<表名>_<字段名> | uk_pm_clue_clue_id |
| 普通索引 | idx_<表名>_<字段名> | idx_pm_clue_status |
| 组合索引 | idx_<表名>_<字段1>_<字段2> | idx_pm_clue_status_type |

---

## 3. 字段类型规范

### 3.1 常用字段类型

| 数据类型 | 长度标注 | 使用场景 | 示例 |
|---------|---------|---------|------|
| VARCHAR | 指定长度 | 变长字符串 | clue_id VARCHAR(16) |
| DECIMAL | 18,2 | 金额、精确数值 | capacity DECIMAL(18,2) |
| TINYINT | 1 | 状态、布尔值 | status TINYINT(1) |
| DATETIME | - | 日期时间 | create_time DATETIME |
| DATE | - | 日期 | obtain_date DATE |
| TEXT | - | 长文本 | remark TEXT |

### 3.2 长度设置建议

| 字段类型 | 推荐长度 | 说明 |
|---------|---------|------|
| ID/编号 | VARCHAR(32) | UUID或业务编码 |
| 编码/Code | VARCHAR(50) | 业务编码 |
| 名称/Name | VARCHAR(100) | 通用名称 |
| 标题/Title | VARCHAR(200) | 标题描述 |
| 长文本 | VARCHAR(1000) | 描述、备注 |
| 富文本 | TEXT | 详细内容 |

---

## 4. 表结构设计

{{tables_section}}

---

## 5. 表清单

| 序号 | 表名 | 中文名称 | 说明 |
|------|------|----------|------|
{{table_list}}

---

## 6. 数据字典

### 6.1 通用枚举值定义

#### is_del - 删除标记
| 值 | 名称 | 说明 |
|----|------|------|
| 0 | 未删除 | 正常数据 |
| 1 | 已删除 | 已软删除，查询时需过滤 |

{{enum_section}}

