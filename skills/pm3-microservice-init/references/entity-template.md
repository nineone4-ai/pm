# Entity 模板

## 标准 Entity

```java
package com.sungrow.pm.{module}.entity;

import cn.iiot.myth.starter.orm.bean.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.util.Date;

/**
 * <p>
 * {业务描述}实体
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("{table_name}")
public class {Business} extends BaseEntity {

    /**
     * 名称
     */
    @TableField("name")
    private String name;

    /**
     * 编码
     */
    @TableField("code")
    private String code;

    /**
     * 状态（0-禁用，1-启用）
     */
    @TableField("status")
    private Integer status;

    /**
     * 描述
     */
    @TableField("description")
    private String description;

    /**
     * 金额
     */
    @TableField("amount")
    private BigDecimal amount;

    /**
     * 生效日期
     */
    @TableField("effective_date")
    private Date effectiveDate;

    /**
     * 失效日期
     */
    @TableField("expiry_date")
    private Date expiryDate;

    /**
     * 排序
     */
    @TableField("sort")
    private Integer sort;

    /**
     * 备注
     */
    @TableField("remark")
    private String remark;

    // ==================== 字段常量（用于 Lambda 查询） ====================
    public static final String NAME = "name";
    public static final String CODE = "code";
    public static final String STATUS = "status";
    public static final String CREATE_TIME = "create_time";
}
```

## BaseEntity（继承的审计字段）

```java
package cn.iiot.myth.starter.orm.bean;

/**
 * 基础实体类（包含审计字段）
 */
public class BaseEntity {
    
    /**
     * 主键ID
     */
    private String id;
    
    /**
     * 创建人ID
     */
    private String createBy;
    
    /**
     * 创建时间
     */
    private Date createTime;
    
    /**
     * 更新人ID
     */
    private String updateBy;
    
    /**
     * 更新时间
     */
    private Date updateTime;
    
    /**
     * 删除标识（0-未删除，1-已删除）
     */
    private String deleteFlag;
}
```

## 字段类型映射

| Java 类型 | MySQL 类型 | 注解示例 |
|-----------|-----------|---------|
| String | VARCHAR | `@TableField("name")` |
| Integer | INT | `@TableField("status")` |
| Long | BIGINT | `@TableField("count")` |
| BigDecimal | DECIMAL | `@TableField("amount")` |
| Date | DATETIME | `@TableField("create_time")` |
| Boolean | TINYINT | `@TableField("enabled")` |

## 表名规范

```
pm_{业务模块}_{业务实体}

示例：
- pm_order_info
- pm_order_detail
- pm_inventory_stock
- pm_payment_record
```

## 常用字段命名

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | VARCHAR(32) | 主键 |
| `name` | VARCHAR(100) | 名称 |
| `code` | VARCHAR(50) | 编码 |
| `status` | INT | 状态 |
| `description` | VARCHAR(500) | 描述 |
| `remark` | VARCHAR(500) | 备注 |
| `sort` | INT | 排序 |
| `delete_flag` | CHAR(1) | 删除标识 |
| `create_by` | VARCHAR(32) | 创建人 |
| `create_time` | DATETIME | 创建时间 |
| `update_by` | VARCHAR(32) | 更新人 |
| `update_time` | DATETIME | 更新时间 |
