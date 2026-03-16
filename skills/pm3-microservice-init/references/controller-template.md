# Controller 模板

## 标准 Controller

```java
package com.sungrow.pm.{module}.controller;

import cn.iiot.myth.framework.common.api.RestResponse;
import cn.iiot.myth.starter.common.annotation.Permission;
import cn.iiot.myth.starter.logging.auditlog.AuditLog;
import cn.iiot.myth.starter.logging.auditlog.BusinessType;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.sungrow.pm.{module}.dto.{Business}AddParam;
import com.sungrow.pm.{module}.dto.{Business}DTO;
import com.sungrow.pm.{module}.dto.{Business}EditParam;
import com.sungrow.pm.{module}.dto.{Business}QueryParam;
import com.sungrow.pm.{module}.service.I{Business}Service;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

/**
 * <p>
 * {业务描述}控制器
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Slf4j
@RestController
@RequestMapping("/api/pm-{module}/{business}")
@Api(tags = "{业务名}模块接口")
public class {Business}Controller {

    @Autowired
    private I{Business}Service {business}Service;

    /**
     * 分页查询
     */
    @Permission("{module}:list:query")
    @ApiOperation("分页查询")
    @AuditLog(title = "{业务名}模块", desc = "分页查询", businessType = BusinessType.QUERY)
    @PostMapping("/list")
    public RestResponse<IPage<{Business}DTO>> pageList(
            @RequestBody {Business}QueryParam param) {
        return RestResponse.ok({business}Service.pageList(param));
    }

    /**
     * 新增
     */
    @Permission("{module}:list:add")
    @ApiOperation("新增")
    @AuditLog(title = "{业务名}模块", desc = "新增", businessType = BusinessType.INSERT)
    @PostMapping("/add")
    public RestResponse<String> add(
            @RequestBody @Valid {Business}AddParam param) {
        {business}Service.save(param);
        return RestResponse.ok("操作成功");
    }

    /**
     * 修改
     */
    @Permission("{module}:list:edit")
    @ApiOperation("修改")
    @AuditLog(title = "{业务名}模块", desc = "修改", businessType = BusinessType.UPDATE)
    @PostMapping("/update")
    public RestResponse<Boolean> update(
            @RequestBody @Valid {Business}EditParam param) {
        return RestResponse.ok({business}Service.update(param));
    }

    /**
     * 详情
     */
    @Permission("{module}:list:view")
    @ApiOperation("详情")
    @GetMapping("/detail/{id}")
    public RestResponse<{Business}DTO> getDetail(@PathVariable("id") String id) {
        return RestResponse.ok({business}Service.getDetail(id));
    }

    /**
     * 删除
     */
    @Permission("{module}:list:delete")
    @ApiOperation("删除")
    @AuditLog(title = "{业务名}模块", desc = "删除", businessType = BusinessType.DELETE)
    @GetMapping("/delete/{id}")
    public RestResponse<Boolean> delete(@PathVariable("id") String id) {
        return RestResponse.ok({business}Service.delete(id));
    }
}
```

## 关键注解说明

| 注解 | 用途 |
|------|------|
| `@RestController` | REST 控制器 |
| `@RequestMapping` | 路径映射 |
| `@Api(tags)` | Swagger 分组 |
| `@Permission` | 权限控制 |
| `@AuditLog` | 审计日志 |
| `@ApiOperation` | 接口描述 |
| `@Valid` | 参数校验 |
| `@RequestBody` | 请求体参数 |
| `@PathVariable` | 路径参数 |

## BusinessType 枚举值

| 枚举值 | 用途 |
|--------|------|
| `BusinessType.QUERY` | 查询 |
| `BusinessType.INSERT` | 新增 |
| `BusinessType.UPDATE` | 修改 |
| `BusinessType.DELETE` | 删除 |
| `BusinessType.EXPORT` | 导出 |
| `BusinessType.IMPORT` | 导入 |

## 权限编码规范

```
{module}:{业务}:{操作}

示例：
- order:list:query    → 订单列表查询
- order:list:add      → 订单新增
- order:list:edit     → 订单修改
- order:list:view     → 订单详情
- order:list:delete   → 订单删除
```
