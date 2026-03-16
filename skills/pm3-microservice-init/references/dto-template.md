# DTO 模板

## 1. QueryParam（查询参数）

```java
package com.sungrow.pm.{module}.dto;

import cn.iiot.myth.framework.common.param.PageParam;
import cn.iiot.myth.starter.orm.annotation.FieldMeta;
import cn.iiot.myth.starter.orm.bean.FilterCondition;
import cn.iiot.myth.starter.orm.bean.SortCondition;
import cn.iiot.myth.starter.orm.constants.FieldTypeEnum;
import com.sungrow.pm.{module}.entity.{Business};
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

/**
 * <p>
 * {业务描述}查询参数
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Data
@EqualsAndHashCode(callSuper = true)
@ApiModel(value = "{Business}QueryParam", description = "{业务名}查询参数")
public class {Business}QueryParam extends PageParam {
    
    @FieldMeta(tableClass = {Business}.class, 
               fieldName = "t.name", 
               fieldType = FieldTypeEnum.STRING)
    @ApiModelProperty(value = "名称")
    private String name;
    
    @FieldMeta(tableClass = {Business}.class, 
               fieldName = "t.status", 
               fieldType = FieldTypeEnum.INTEGER)
    @ApiModelProperty(value = "状态")
    private Integer status;
    
    @ApiModelProperty(value = "过滤条件集合")
    private List<FilterCondition> filterConditions;
    
    @ApiModelProperty(value = "排序条件集合")
    private List<SortCondition> sortConditions;
}
```

## 2. AddParam（新增参数）

```java
package com.sungrow.pm.{module}.dto;

import cn.iiot.myth.framework.common.param.ApiParam;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;
import lombok.EqualsAndHashCode;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

/**
 * <p>
 * {业务描述}新增参数
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Data
@EqualsAndHashCode(callSuper = true)
@ApiModel(value = "{Business}AddParam", description = "{业务名}新增参数")
public class {Business}AddParam extends ApiParam {
    
    @NotBlank(message = "名称不能为空")
    @ApiModelProperty(value = "名称", required = true)
    private String name;
    
    @ApiModelProperty(value = "编码")
    private String code;
    
    @NotNull(message = "状态不能为空")
    @ApiModelProperty(value = "状态", required = true)
    private Integer status;
    
    @ApiModelProperty(value = "描述")
    private String description;
}
```

## 3. EditParam（修改参数）

```java
package com.sungrow.pm.{module}.dto;

import cn.iiot.myth.framework.common.param.ApiParam;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;
import lombok.EqualsAndHashCode;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

/**
 * <p>
 * {业务描述}修改参数
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Data
@EqualsAndHashCode(callSuper = true)
@ApiModel(value = "{Business}EditParam", description = "{业务名}修改参数")
public class {Business}EditParam extends ApiParam {
    
    @NotBlank(message = "ID 不能为空")
    @ApiModelProperty(value = "主键ID", required = true)
    private String id;
    
    @NotBlank(message = "名称不能为空")
    @ApiModelProperty(value = "名称", required = true)
    private String name;
    
    @ApiModelProperty(value = "编码")
    private String code;
    
    @NotNull(message = "状态不能为空")
    @ApiModelProperty(value = "状态", required = true)
    private Integer status;
    
    @ApiModelProperty(value = "描述")
    private String description;
}
```

## 4. DTO（响应对象）

```java
package com.sungrow.pm.{module}.dto;

import cn.iiot.myth.starter.orm.annotation.FieldMetaRsp;
import com.fasterxml.jackson.annotation.JsonFormat;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;

import java.math.BigDecimal;
import java.util.Date;

/**
 * <p>
 * {业务描述}响应DTO
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Data
@ApiModel(value = "{Business}DTO", description = "{业务名}响应对象")
public class {Business}DTO {
    
    @FieldMetaRsp(fieldName = "t.id")
    @ApiModelProperty(value = "主键ID")
    private String id;
    
    @FieldMetaRsp(fieldName = "t.name")
    @ApiModelProperty(value = "名称")
    private String name;
    
    @FieldMetaRsp(fieldName = "t.code")
    @ApiModelProperty(value = "编码")
    private String code;
    
    @FieldMetaRsp(fieldName = "t.status")
    @ApiModelProperty(value = "状态")
    private Integer status;
    
    @FieldMetaRsp(fieldName = "t.description")
    @ApiModelProperty(value = "描述")
    private String description;
    
    @FieldMetaRsp(fieldName = "t.amount")
    @ApiModelProperty(value = "金额")
    private BigDecimal amount;
    
    @FieldMetaRsp(fieldName = "t.create_time")
    @ApiModelProperty(value = "创建时间")
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createTime;
    
    @FieldMetaRsp(fieldName = "t.create_by")
    @ApiModelProperty(value = "创建人")
    private String createBy;
}
```

## DTO 类型说明

| DTO 类型 | 继承 | 用途 | 校验注解 |
|---------|------|------|---------|
| `QueryParam` | `PageParam` | 分页查询 | 无 |
| `AddParam` | `ApiParam` | 新增操作 | `@NotBlank`, `@NotNull` |
| `EditParam` | `ApiParam` | 修改操作 | `@NotBlank`, `@NotNull` |
| `DTO` | 无 | 响应数据 | 无 |

## 常用校验注解

| 注解 | 用途 |
|------|------|
| `@NotNull` | 不能为 null |
| `@NotBlank` | 不能为空字符串 |
| `@NotEmpty` | 不能为 null 或空集合 |
| `@Size` | 字符串/集合长度 |
| `@Min` | 最小值 |
| `@Max` | 最大值 |
| `@Pattern` | 正则表达式 |
