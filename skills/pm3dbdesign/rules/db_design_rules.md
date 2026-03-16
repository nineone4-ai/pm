# 数据库设计规范

# 数据库环境

### 基础环境

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **数据库类型** | MySQL 5.7 | 生产环境统一版本 |
| **字符集** | utf8mb4 | 支持完整Unicode字符集（含emoji） |
| **排序规则** | utf8mb4_general_ci | 不区分大小写的通用排序规则 |
| **存储引擎** | InnoDB | 支持事务、行级锁、外键 |

### DDL模板

```sql
CREATE TABLE `pm_模块前缀_表名` (
  -- 表字段定义
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='表说明';
```

**项目管理模块示例**：
```sql
CREATE TABLE `pm_overseas_customer` (
  -- 表字段定义
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='海外客户档案主表';
```

---

## 设计原则

### 1. 必须包含的审计字段

**所有业务表必须包含以下6个审计字段**：

| 字段名 | 类型 | 长度 | 必填 | 默认值 | 说明 |
|--------|------|------|------|--------|------|
| `id` | VARCHAR | 32 | 是 | - | 主键，UUID |
| `create_by` | VARCHAR | 64 | 否 | - | 创建人ID |
| `update_by` | VARCHAR | 64 | 否 | - | 更新人ID |
| `create_time` | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| `update_time` | DATETIME | - | 否 | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| `is_del` | TINYINT | 1 | 是 | 0 | 软删除标记：0-未删除，1-已删除 |
|  `remark`| VARCHAR  |1000  | 否 |  | 备注 |

**DDL示例**：
```sql
CREATE TABLE `pm_project` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键ID',
  -- ... 业务字段 ...
  `create_by` VARCHAR(64) NOT NULL COMMENT '创建人ID',
  `update_by` VARCHAR(64) NOT NULL COMMENT '更新人ID',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_del` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0-未删除，1-已删除',
  `remark` VARCHAR(1000) NOT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  KEY `idx_pm_project_is_del` (`is_del`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='项目表';
```

### 2. 字段长度和默认值

**字段长度规范**：

| 字段类型 | 推荐长度 | 说明 |
|---------|---------|------|
| 用户名 | VARCHAR(50) | 一般不超过50字符 |
| 姓名 | VARCHAR(50) | 中文名最多10字，留有余量 |
| 手机号 | VARCHAR(20) | 11位手机号，预留国际号码 |
| 邮箱 | VARCHAR(100) | RFC标准最大64@255 |
| 短文本 | VARCHAR(100) | 标题、名称类 |
| 长文本 | VARCHAR(1000) | 描述、备注类 |
| 超长文本 | TEXT | 富文本内容 |
| 金额 | DECIMAL(18,6) | 最大999999999999.99 |
| 百分比 | DECIMAL(5,2) | 0.00-100.00 |

**默认值规范**：
- 字符串字段：`DEFAULT ''`（空字符串，避免NULL）
- 数值字段：`DEFAULT 0`
- 状态字段：`DEFAULT 0`（初始状态）
- 时间字段：`DEFAULT CURRENT_TIMESTAMP`
- 软删除字段：`DEFAULT 0`

**示例**：
```sql
`project_name` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '项目名称',
`project_budget` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '项目预算',
`project_status` TINYINT NOT NULL DEFAULT 0 COMMENT '项目状态：0-草稿，1-进行中，2-已完成',
```

### 3. 索引控制

**规范**：
- 每个表索引数量：**不允许超过5个**（不含主键）
- 避免过多索引影响写入性能
- 索引选择原则：
  - 高频查询字段
  - WHERE条件字段
  - ORDER BY字段
  - 外键字段

**必建索引**：
- 主键索引（自动创建）
- `is_del` 字段索引（软删除查询）

### 4. 系统统一表规范(严格遵循)

**附件管理统一表**：

项目管理系统（PM3.0）使用统一的附件表 `pm_attachment` 管理所有业务模块的附件，使用business_type进行区分，各业务模块**不应单独设计附件表**。

**表结构**：
```sql
CREATE TABLE `pm_attachment` (
  `id` varchar(50) NOT NULL COMMENT 'ID',
  `business_id` varchar(50) NOT NULL COMMENT '业务ID(开发权、预立项、立项、指标)',
  `business_type` varchar(50) NOT NULL COMMENT '业务类型(开发权、预立项、立项、指标)',
  `attachment_type` varchar(50) NOT NULL COMMENT '附件类型',
  `filename` varchar(200) NOT NULL COMMENT '文件名称',
  `upload_name` varchar(200) NOT NULL COMMENT '上传人',
  `upload_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '上传时间',
  `file_path` varchar(200) NOT NULL COMMENT '文件路径',
  `required` varchar(30) DEFAULT '2' COMMENT '是否必传 1：必传，2：非必传',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='附件数据项';
```

**其他统一表**（根据系统实际情况添加）：

- `operator_log`：统一操作日志表
- `platform_dict_data`：统一数据字典表

**禁止新建的统一表类型**：

> [!warning] 以下类型的表不允许新建，必须遵循系统已有表结构设计

### 审批流程相关表

| 表前缀 | 说明 |
|--------|------|
| Activity 工作流引擎 | 涉及审批流的业务应复用已有的 Activity 审批流程设计，不得新建审批相关表 |

### 身份认证相关表（idm_*）

| 表名 | 说明 |
|------|------|
| `idm_oauth_client` | OAuth 客户端 |
| `idm_oauth_client_user` | OAuth 客户端用户关联 |
| `idm_org` | 组织机构 |
| `idm_position` | 岗位 |
| `idm_tenant` | 租户 |
| `idm_tenant_user` | 租户用户关联 |
| `idm_user` | 用户 |
| `idm_user_org` | 用户组织关联 |

### 权限角色相关表（permission_*）

| 表名 | 说明 |
|------|------|
| `permission_role` | 角色 |
| `permission_role_apply_record` | 角色申请记录 |
| `permission_role_approver` | 角色审批人 |
| `permission_role_assign` | 角色分配 |
| `permission_role_btn_ref` | 角色按钮引用 |
| `permission_role_data_range` | 角色数据范围 |
| `permission_role_field` | 角色字段 |
| `permission_role_field_ref` | 角色字段引用 |
| `permission_role_group` | 角色分组 |
| `permission_role_operation` | 角色操作 |
| `permission_role_org_parse` | 角色组织解析 |
| `permission_role_relation` | 角色关系 |
| `permission_role_resource` | 角色资源 |
| `permission_role_row_ref` | 角色行引用 |
| `permission_role_user_data_range` | 角色用户数据范围 |
| `permission_group_role` | 分组角色 |

### 主数据管理表（mam_* / mdm_*）

| 表名 | 说明 |
|------|------|
| `mam_area` | 区域 |
| `mam_person` | 人员 |
| `mdm_centralized` | 集中度 |
| `mdm_city` | 城市 |
| `mdm_company` | 公司 |
| `mdm_country` | 国家 |
| `mdm_currency` | 币种 |
| `mdm_dept` | 部门 |
| `mdm_dept_view` | 部门视图 |
| `mdm_dept_view_prd` | 部门视图（生产） |
| `mdm_dept_view_prd_new` | 部门视图（生产新） |
| `mdm_equity_transfer_view` | 股权转让视图 |
| `mdm_language` | 语言 |
| `mdm_language_view` | 语言视图 |
| `mdm_material_category` | 物料分类 |
| `mdm_position` | 职位 |
| `mdm_profit_center` | 利润中心 |
| `mdm_profit_center_prd` | 利润中心（生产） |
| `mdm_project` | 项目 |
| `mdm_project_view` | 项目视图 |
| `mdm_province` | 省份 |
| `mdm_reg_cer_type` | 注册证书类型 |
| `mdm_request_og` | 请求组织 |
| `mdm_sap` | SAP 数据 |
| `mdm_subsidiary` | 子公司 |
| `mdm_supply_category` | 供应分类 |
| `mdm_unit` | 单位 |

**设计约束**：

```markdown
1. 审批流程：使用 Activity 工作流引擎，通过 business_key 关联业务表，不新建审批表
2. 身份认证：通过 idm_user.id 关联用户，通过 idm_org.id 关联组织，不新建用户/组织表
3. 权限角色：复用 permission_role 等权限表，通过 role_id/user_id 关联，不新建角色权限表
4. 主数据引用：通过 mdm_xxx_id 字段关联已有主数据表，不新建主数据表
```

---

## 📝 命名规范

### 1. 表命名规范

**格式**：`pm_<模块前缀>_<业务名称>`

**规则**：
- 全小写
- 使用下划线风格（snake_case）
- 以模块前缀开头（2-5个字符）
- 业务名称简洁明确
- **项目管理模块统一使用 `pm_` 前缀**

**禁止**：
- ❌ 使用SQL保留字（如：order, user, group等）
- ❌ 使用中文
- ❌ 使用特殊字符（除下划线）
- ❌ 使用驼峰命名（camelCase）

**示例**：

| 模块 | 表名 | 说明 |
|------|------|------|
| 项目管理 | `pm_project` | pm = Project Management |
| 项目管理-客户档案 | `pm_overseas_customer` | overseas = 海外 |
| 合同管理 | `pm_cm_contract` | cm = Contract Management |
| 成本管理 | `pm_cost_expense` | cost = Cost |
| 用户管理 | `sys_user` | sys = System |
| 组织架构 | `sys_dept` | dept = Department |

### 2. 字段命名规范

**格式**：`<字段名>`（全小写，下划线分隔）

**规则**：

- 全小写
- 使用下划线风格（snake_case）
- 见名知意，避免缩写（除非是通用缩写）
- 禁止使用保留字、中文、驼峰命名

**常用字段命名**：

| 字段含义 | 命名 | 类型 |
|---------|------|------|
| 主键ID | `id` | BIGINT |
| 名称 | `xxx_name` | VARCHAR |
| 编号 | `xxx_code` | VARCHAR |
| 状态 | `xxx_status` | TINYINT |
| 类型 | `xxx_type` | TINYINT |
| 数量 | `xxx_count` | INT |
| 金额 | `xxx_amount` | DECIMAL |
| 描述 | `xxx_desc` | VARCHAR/TEXT |
| 备注 | `remark` | VARCHAR/TEXT |
| 开始时间 | `start_time` | DATETIME |
| 结束时间 | `end_time` | DATETIME |

**示例**：
```sql
`project_name` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '项目名称',
`project_code` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '项目编号',
`project_status` TINYINT NOT NULL DEFAULT 0 COMMENT '项目状态',
`project_budget` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '项目预算',
`start_date` DATE NOT NULL COMMENT '开始日期',
`end_date` DATE NOT NULL COMMENT '结束日期',
```

### 3. 索引命名规范

**格式**：

| 索引类型 | 命名格式 | 示例 |
|---------|---------|------|
| **主键索引** | `pk_<表名>` | `pk_pm_project` |
| **唯一索引** | `uk_<表名>_<字段名>` | `uk_pm_project_code` |
| **普通索引** | `idx_<表名>_<字段名>` | `idx_pm_project_status` |
| **组合索引** | `idx_<表名>_<字段1>_<字段2>` | `idx_pm_project_status_type` |

**示例**：
```sql
-- 主键索引（自动创建，通常不需要手动命名）
PRIMARY KEY (`id`)

-- 唯一索引
UNIQUE KEY `uk_pm_project_code` (`project_code`)

-- 普通索引
KEY `idx_pm_project_status` (`project_status`)
KEY `idx_pm_project_is_del` (`is_del`)

-- 组合索引
KEY `idx_pm_project_status_type` (`project_status`, `project_type`)
```

---

## 🔧 字段类型规范

### 1. 数值类型

| 类型 | 长度 | 范围 | 适用场景 |
|------|------|------|---------|
| **TINYINT** | 1字节 | -128~127 或 0~255 | 状态、类型、标志位 |
| **SMALLINT** | 2字节 | -32768~32767 | 小范围计数 |
| **INT** | 4字节 | -2^31~2^31-1 | 普通计数、数量 |
| **BIGINT** | 8字节 | -2^63~2^63-1 | 大数值 |
| **DECIMAL(M,D)** | 变长 | 依赖M和D | 金额、精确小数 |

**使用建议**：
- 状态字段：`TINYINT`（如：0-草稿，1-进行中，2-已完成）
- 主键：`VARCHAR(32)`（UUID）
- 金额：`DECIMAL(15,2)`（最多13位整数+2位小数）
- 数量：`INT`或`DECIMAL(10,2)`

**示例**：
```sql
`project_status` TINYINT NOT NULL DEFAULT 0 COMMENT '项目状态：0-草稿，1-进行中，2-已完成',
`employee_count` INT NOT NULL DEFAULT 0 COMMENT '员工数量',
`project_budget` DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '项目预算（元）',
`completion_rate` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '完成率（百分比）',
```

### 2. 字符串类型

| 类型 | 最大长度 | 存储方式 | 适用场景 |
|------|---------|---------|---------|
| **CHAR(N)** | 255字符 | 定长 | 固定长度字符串（如：UUID） |
| **VARCHAR(N)** | 65535字节 | 变长 | 变长字符串（如：名称、描述） |
| **TEXT** | 65535字节 | 变长 | 长文本（如：富文本内容） |
| **MEDIUMTEXT** | 16MB | 变长 | 超长文本 |
| **LONGTEXT** | 4GB | 变长 | 极大文本（少用） |

**长度建议**：

| 字段类型 | 推荐长度 | 说明 |
|---------|---------|------|
| 用户名 | VARCHAR(50) | - |
| 姓名 | VARCHAR(50) | - |
| 手机号 | VARCHAR(20) | 预留国际号码 |
| 邮箱 | VARCHAR(100) | - |
| 编号/Code | VARCHAR(50) | - |
| 短标题 | VARCHAR(100) | - |
| 长标题 | VARCHAR(200) | - |
| 描述 | VARCHAR(500) | - |
| 富文本 | TEXT | 或MEDIUMTEXT |

**示例**：
```sql
`project_name` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '项目名称',
`project_code` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '项目编号',
`project_desc` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '项目描述',
`project_detail` TEXT COMMENT '项目详情（富文本）',
```

### 3. 日期时间类型

| 类型 | 格式 | 范围 | 适用场景 |
|------|------|------|---------|
| **DATE** | YYYY-MM-DD | 1000-01-01 ~ 9999-12-31 | 日期（不含时间） |
| **DATETIME** | YYYY-MM-DD HH:MM:SS | 1000-01-01 00:00:00 ~ 9999-12-31 23:59:59 | 日期时间 |
| **TIMESTAMP** | YYYY-MM-DD HH:MM:SS | 1970-01-01 00:00:01 ~ 2038-01-19 03:14:07 | 时间戳 |

**使用建议**：
- 审计字段（create_time/update_time）：`DATETIME`
- 业务日期（start_date/end_date）：`DATE`
- 避免使用`TIMESTAMP`（范围小，有时区问题）

**示例**：
```sql
`start_date` DATE NOT NULL COMMENT '开始日期',
`end_date` DATE NOT NULL COMMENT '结束日期',
`create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
`update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
```

### 4. 枚举和JSON类型

**ENUM类型**：
- ⚠️ **不推荐使用**
- 原因：难以维护、修改需要ALTER TABLE

**JSON类型**：
- ✅ MySQL 5.7+支持
- 适用场景：扩展字段、非结构化数据
- 示例：`extra_info JSON COMMENT '扩展信息'`

**建议**：
- 状态/类型字段使用 `TINYINT` + 注释说明枚举值
- 扩展字段使用 `JSON` 或单独的扩展表

---

## 📊 索引设计规范

### 1. 索引类型

| 索引类型 | 说明 | 使用场景 |
|---------|------|---------|
| **主键索引** | 唯一且非空 | 主键字段（自动创建） |
| **唯一索引** | 唯一但可为空 | 业务唯一字段（如：编号） |
| **普通索引** | 可重复 | 高频查询字段 |
| **组合索引** | 多字段索引 | 多条件组合查询 |

### 2. 索引创建原则

**必建索引**：
- 主键字段（自动创建）
- `is_del` 字段（软删除查询必用）
- 外键字段（关联查询必用）

**选建索引**：
- WHERE条件高频字段
- ORDER BY字段
- GROUP BY字段
- 唯一性约束字段（业务编号等）

**不建索引**：
- 低频查询字段
- TEXT/BLOB字段
- 区分度很低的字段（如：性别）
- 更新频繁的字段

### 3. 组合索引规则

**最左前缀原则**：
- 索引：`idx_status_type_time (status, type, create_time)`
- 可用：`WHERE status = ?`
- 可用：`WHERE status = ? AND type = ?`
- 可用：`WHERE status = ? AND type = ? AND create_time > ?`
- ❌ 不可用：`WHERE type = ?`（跳过了status）

**字段顺序**：
1. 等值条件字段在前
2. 范围条件字段在后
3. 区分度高的字段在前

**示例**：
```sql
-- 好的组合索引
KEY `idx_pm_project_status_type` (`project_status`, `project_type`)

-- 不好的组合索引（范围条件在前）
KEY `idx_pm_project_time_status` (`create_time`, `project_status`)  -- ❌
```

### 4. 索引命名和注释

```sql
-- 唯一索引
UNIQUE KEY `uk_pm_project_code` (`project_code`) COMMENT '项目编号唯一索引',

-- 普通索引
KEY `idx_pm_project_status` (`project_status`) COMMENT '项目状态索引',
KEY `idx_pm_project_is_del` (`is_del`) COMMENT '软删除标记索引',
KEY `idx_pm_project_create_time` (`create_time`) COMMENT '创建时间索引',

-- 组合索引
KEY `idx_pm_project_status_type` (`project_status`, `project_type`) COMMENT '状态类型组合索引',
```

---

## 🔒 约束规范

### 1. 主键约束

```sql
PRIMARY KEY (`id`)
```

- 每个表必须有主键
- 使用雪花ID（BIGINT）
- 单字段主键，不使用复合主键

### 2. 唯一约束

```sql
UNIQUE KEY `uk_pm_project_code` (`project_code`)
```

- 业务唯一字段添加唯一约束
- 示例：项目编号、员工工号、手机号等

### 3. 非空约束

```sql
`project_name` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '项目名称',
```

- 重要字段设置 `NOT NULL`
- 配合合理的默认值

### 4. 外键约束

**⚠️ 不推荐使用物理外键**

**原因**：
- 影响性能（插入/删除需要检查）
- 分库分表困难
- 锁等待问题

**替代方案**：
- 使用逻辑外键（字段名体现关联关系）
- 在应用层保证数据一致性
- 添加索引加速关联查询

**示例**：
```sql
-- 不推荐
FOREIGN KEY (`project_id`) REFERENCES `t_pm_project` (`id`)

-- 推荐（逻辑外键）
`project_id` VARCHAR(32) NOT NULL COMMENT '项目ID（关联t_pm_project.id）',
KEY `idx_pm_task_project_id` (`project_id`) COMMENT '项目ID索引',
```

