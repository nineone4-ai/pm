# PM3 API 接口模板文档

> 文档版本：v1.0  
> 最后更新：2026-03-03  
> 使用说明：复制模板后修改为新接口设计

---

## 一、接口列表总表

| 接口名称 | 请求方法 | 请求路径 | 权限标识 | 所属模块 | 说明 |
|---------|---------|---------|---------|---------|------|
| 分页查询列表 | GET | `/list` | `{module}:list` | 所有模块 | 带分页、筛选、排序 |
| 获取详情 | GET | `/detail/{id}` | `{module}:detail` | 所有模块 | 根据 ID 获取单个资源 |
| 新增资源 | POST | `/add` | `{module}:add` | 所有模块 | 创建新资源 |
| 修改资源 | POST | `/update` | `{module}:edit` | 所有模块 | 全量更新资源 |
| 删除资源 | POST | `/delete` | `{module}:delete` | 所有模块 | 单个删除 |
| 批量删除 | DELETE | `/batchDelete/{ids}` | `{module}:batchDelete` | 所有模块 | 批量删除多个资源 |
| 启用/禁用 | POST | `/updateStatus` | `{module}:status` | 所有模块 | 状态变更 |
| 导出 Excel | GET | `/export` | `{module}:export` | 所有模块 | 导出为 Excel 文件 |
| 导入 Excel | POST | `/import` | `{module}:import` | 所有模块 | 从 Excel 导入 |
| 树形结构 | GET | `/tree` | `{module}:tree` | 树形模块 | 获取树形数据 |

---

## 二、接口详细模板

### 模板 1：列表查询接口（带分页）

```markdown
### [模块名称] 分页查询列表

**接口路径**：`GET {基础路径}/list`

**权限标识**：`{module}:list`

**功能说明**：分页查询 [资源名称] 列表，支持多条件筛选和排序

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| pageNum | Integer | Query | 否 | 1 | 页码 |
| pageSize | Integer | Query | 否 | 10 | 每页大小 |
| keyword | String | Query | 否 | - | 关键词（模糊查询） |
| status | Integer | Query | 否 | - | 状态：0-禁用，1-启用 |
| createTimeStart | String | Query | 否 | - | 创建开始时间（yyyy-MM-dd） |
| createTimeEnd | String | Query | 否 | - | 创建结束时间（yyyy-MM-dd） |

**请求示例**：

```http
GET /api/{module}/{resource}/list?pageNum=1&pageSize=10&keyword=test&status=1
Authorization: Bearer {token}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "records": [
      {
        "id": "1",
        "name": "测试资源 1",
        "code": "TEST_001",
        "status": 1,
        "createTime": "2024-01-15 10:30:00",
        "updateTime": "2024-01-15 10:30:00"
      },
      {
        "id": "2",
        "name": "测试资源 2",
        "code": "TEST_002",
        "status": 0,
        "createTime": "2024-01-16 11:00:00",
        "updateTime": "2024-01-16 11:00:00"
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "pages": 10
  }
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| total | Long | 总记录数 |
| records | Array | 当前页数据列表 |
| records[].id | String | 资源 ID |
| records[].name | String | 资源名称 |
| records[].code | String | 资源编码 |
| records[].status | Integer | 状态：0-禁用，1-启用 |
| records[].createTime | String | 创建时间 |
| records[].updateTime | String | 更新时间 |
| pageNum | Integer | 当前页码 |
| pageSize | Integer | 每页大小 |
| pages | Long | 总页数 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:list")
@ApiOperation("[资源名称] 分页查询列表")
@AuditLog(title = "[资源名称] 管理", desc = "分页查询列表", businessType = BusinessType.QUERY)
@GetMapping("/list")
public RestResponse<PageResult<[Resource]DTO>> pageList(@Valid [Resource]QueryParam param) {
    PageResult<[Resource]DTO> pageResult = [resource]Service.pageDTO(param);
    return RestResponse.ok(pageResult);
}
```

**QueryParam 模板**：

```java
@ApiModel("[资源名称] 查询参数")
@Data
public class [Resource]QueryParam {
    
    @ApiModelProperty("页码")
    @NotNull(message = "页码不能为空")
    private Integer pageNum = 1;
    
    @ApiModelProperty("每页大小")
    @NotNull(message = "每页大小不能为空")
    private Integer pageSize = 10;
    
    @ApiModelProperty("关键词（模糊查询）")
    private String keyword;
    
    @ApiModelProperty("状态：0-禁用，1-启用")
    private Integer status;
    
    @ApiModelProperty("创建开始时间（yyyy-MM-dd）")
    private String createTimeStart;
    
    @ApiModelProperty("创建结束时间（yyyy-MM-dd）")
    private String createTimeEnd;
}
```

---

### 模板 2：详情获取接口

```markdown
### [模块名称] 获取详情

**接口路径**：`GET {基础路径}/detail/{id}`

**权限标识**：`{module}:detail`

**功能说明**：根据 ID 获取 [资源名称] 的详细信息

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| id | String | Path | 是 | - | 资源 ID |

**请求示例**：

```http
GET /api/{module}/{resource}/detail/123
Authorization: Bearer {token}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "123",
    "name": "测试资源",
    "code": "TEST_001",
    "description": "这是资源描述",
    "status": 1,
    "sort": 1,
    "remark": "备注信息",
    "createTime": "2024-01-15 10:30:00",
    "createBy": "admin",
    "updateTime": "2024-01-15 10:30:00",
    "updateBy": "admin"
  }
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | String | 资源 ID |
| name | String | 资源名称 |
| code | String | 资源编码 |
| description | String | 资源描述 |
| status | Integer | 状态：0-禁用，1-启用 |
| sort | Integer | 排序号 |
| remark | String | 备注 |
| createTime | String | 创建时间 |
| createBy | String | 创建人 |
| updateTime | String | 更新时间 |
| updateBy | String | 更新人 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 404 | 资源不存在 | 请求的 ID 不存在 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:detail")
@ApiOperation("[资源名称] 获取详情")
@AuditLog(title = "[资源名称] 管理", desc = "获取详情", businessType = BusinessType.QUERY)
@GetMapping("/detail/{id}")
public RestResponse<[Resource]DetailVO> detail(@PathVariable String id) {
    return RestResponse.ok([resource]Service.detail(id));
}
```

---

### 模板 3：创建接口

```markdown
### [模块名称] 新增资源

**接口路径**：`POST {基础路径}/add`

**权限标识**：`{module}:add`

**功能说明**：创建新的 [资源名称]

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| name | String | Body | 是 | - | 资源名称 |
| code | String | Body | 是 | - | 资源编码 |
| description | String | Body | 否 | - | 资源描述 |
| status | Integer | Body | 否 | 1 | 状态：0-禁用，1-启用 |
| sort | Integer | Body | 否 | 0 | 排序号 |
| remark | String | Body | 否 | - | 备注 |

**请求示例**：

```http
POST /api/{module}/{resource}/add
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "测试资源",
  "code": "TEST_001",
  "description": "这是资源描述",
  "status": 1,
  "sort": 1,
  "remark": "备注信息"
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": "123"
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| data | String | 新增资源的 ID |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 400 | 请求参数错误 | 参数校验失败 |
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:add")
@ApiOperation("[资源名称] 新增")
@AuditLog(title = "[资源名称] 管理", desc = "新增资源", businessType = BusinessType.INSERT)
@PostMapping("/add")
public RestResponse<String> add(@RequestBody @Valid [Resource]AddParam param) {
    String id = [resource]Service.saveByParam(param);
    return RestResponse.ok(id);
}
```

**AddParam 模板**：

```java
@ApiModel("[资源名称] 新增参数")
@Data
public class [Resource]AddParam {
    
    @NotBlank(message = "资源名称不能为空")
    @Size(max = 50, message = "资源名称长度不能超过 50 字符")
    @ApiModelProperty("资源名称")
    private String name;
    
    @NotBlank(message = "资源编码不能为空")
    @Size(max = 50, message = "资源编码长度不能超过 50 字符")
    @ApiModelProperty("资源编码")
    private String code;
    
    @Size(max = 200, message = "描述长度不能超过 200 字符")
    @ApiModelProperty("资源描述")
    private String description;
    
    @ApiModelProperty("状态：0-禁用，1-启用")
    private Integer status = 1;
    
    @ApiModelProperty("排序号")
    private Integer sort = 0;
    
    @Size(max = 200, message = "备注长度不能超过 200 字符")
    @ApiModelProperty("备注")
    private String remark;
}
```

---

### 模板 4：更新接口

```markdown
### [模块名称] 修改资源

**接口路径**：`POST {基础路径}/update`

**权限标识**：`{module}:edit`

**功能说明**：修改 [资源名称] 的信息（全量更新）

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| id | String | Body | 是 | - | 资源 ID |
| name | String | Body | 是 | - | 资源名称 |
| code | String | Body | 是 | - | 资源编码 |
| description | String | Body | 否 | - | 资源描述 |
| status | Integer | Body | 否 | - | 状态：0-禁用，1-启用 |
| sort | Integer | Body | 否 | - | 排序号 |
| remark | String | Body | 否 | - | 备注 |

**请求示例**：

```http
POST /api/{module}/{resource}/update
Content-Type: application/json
Authorization: Bearer {token}

{
  "id": "123",
  "name": "更新后的资源名称",
  "code": "TEST_001",
  "description": "更新后的描述",
  "status": 1,
  "sort": 2,
  "remark": "更新后的备注"
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| data | Boolean | 操作结果：true-成功，false-失败 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 400 | 请求参数错误 | 参数校验失败 |
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 404 | 资源不存在 | 请求的 ID 不存在 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:edit")
@ApiOperation("[资源名称] 修改")
@AuditLog(title = "[资源名称] 管理", desc = "修改资源", businessType = BusinessType.UPDATE)
@PostMapping("/update")
public RestResponse<Boolean> update(@RequestBody @Valid [Resource]EditParam param) {
    return RestResponse.ok([resource]Service.updateByParam(param));
}
```

**EditParam 模板**：

```java
@ApiModel("[资源名称] 修改参数")
@Data
public class [Resource]EditParam {
    
    @NotBlank(message = "资源 ID 不能为空")
    @ApiModelProperty("资源 ID")
    private String id;
    
    @NotBlank(message = "资源名称不能为空")
    @Size(max = 50, message = "资源名称长度不能超过 50 字符")
    @ApiModelProperty("资源名称")
    private String name;
    
    @NotBlank(message = "资源编码不能为空")
    @Size(max = 50, message = "资源编码长度不能超过 50 字符")
    @ApiModelProperty("资源编码")
    private String code;
    
    @Size(max = 200, message = "描述长度不能超过 200 字符")
    @ApiModelProperty("资源描述")
    private String description;
    
    @ApiModelProperty("状态：0-禁用，1-启用")
    private Integer status;
    
    @ApiModelProperty("排序号")
    private Integer sort;
    
    @Size(max = 200, message = "备注长度不能超过 200 字符")
    @ApiModelProperty("备注")
    private String remark;
}
```

---

### 模板 5：删除接口

```markdown
### [模块名称] 删除资源

**接口路径**：`POST {基础路径}/delete`

**权限标识**：`{module}:delete`

**功能说明**：根据 [标识字段] 删除 [资源名称]

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| {idField} | String | Query | 是 | - | 资源标识（ID 或 Code） |

**请求示例**：

```http
POST /api/{module}/{resource}/delete?id=123
Authorization: Bearer {token}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| data | Boolean | 操作结果：true-成功，false-失败 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:delete")
@ApiOperation("[资源名称] 删除")
@AuditLog(title = "[资源名称] 管理", desc = "删除资源", businessType = BusinessType.DELETE)
@PostMapping("/delete")
public RestResponse<Boolean> delete(@RequestParam("{idField}") String {idField}) {
    return RestResponse.ok([resource]Service.removeBy{idField}(idField));
}
```

---

### 模板 6：批量删除接口

```markdown
### [模块名称] 批量删除资源

**接口路径**：`DELETE {基础路径}/batchDelete/{ids}`

**权限标识**：`{module}:batchDelete`

**功能说明**：批量删除多个 [资源名称]

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| ids | Array | Path | 是 | - | 资源 ID 列表（逗号分隔） |

**请求示例**：

```http
DELETE /api/{module}/{resource}/batchDelete/1,2,3,4,5
Authorization: Bearer {token}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| data | Boolean | 操作结果：true-成功，false-失败 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:batchDelete")
@ApiOperation("[资源名称] 批量删除")
@AuditLog(title = "[资源名称] 管理", desc = "批量删除", businessType = BusinessType.DELETE)
@DeleteMapping("/batchDelete/{ids}")
public RestResponse<Boolean> batchDelete(@PathVariable("ids") @NotEmpty List<String> ids) {
    return RestResponse.ok([resource]Service.deleteByIds(ids));
}
```

---

### 模板 7：状态变更接口

```markdown
### [模块名称] 启用/禁用

**接口路径**：`POST {基础路径}/updateStatus`

**权限标识**：`{module}:status`

**功能说明**：启用或禁用 [资源名称]

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| id | String | Body | 是 | - | 资源 ID |
| status | Integer | Body | 是 | - | 状态：0-禁用，1-启用 |

**请求示例**：

```http
POST /api/{module}/{resource}/updateStatus
Content-Type: application/json
Authorization: Bearer {token}

{
  "id": "123",
  "status": 1
}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| data | Boolean | 操作结果：true-成功，false-失败 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 400 | 请求参数错误 | 参数校验失败 |
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 404 | 资源不存在 | 请求的 ID 不存在 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:status")
@ApiOperation("[资源名称] 启用/禁用")
@AuditLog(title = "[资源名称] 管理", desc = "启用/禁用", businessType = BusinessType.UPDATE)
@PostMapping("/updateStatus")
public RestResponse<Boolean> updateStatus(@RequestBody [Resource]StatusParam param) {
    return RestResponse.ok([resource]Service.updateStatus(param));
}
```

**StatusParam 模板**：

```java
@ApiModel("[资源名称] 状态参数")
@Data
public class [Resource]StatusParam {
    
    @NotBlank(message = "资源 ID 不能为空")
    @ApiModelProperty("资源 ID")
    private String id;
    
    @NotNull(message = "状态不能为空")
    @ApiModelProperty("状态：0-禁用，1-启用")
    private Integer status;
}
```

---

### 模板 8：导出接口

```markdown
### [模块名称] 导出 Excel

**接口路径**：`GET {基础路径}/export`

**权限标识**：`{module}:export`

**功能说明**：导出 [资源名称] 列表为 Excel 文件

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| keyword | String | Query | 否 | - | 关键词（筛选） |
| status | Integer | Query | 否 | - | 状态：0-禁用，1-启用 |
| createTimeStart | String | Query | 否 | - | 创建开始时间 |
| createTimeEnd | String | Query | 否 | - | 创建结束时间 |

**请求示例**：

```http
GET /api/{module}/{resource}/export?keyword=test&status=1
Authorization: Bearer {token}
```

**响应**：Excel 文件下载（Content-Type: application/vnd.ms-excel）

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:export")
@ApiOperation("[资源名称] 导出 Excel")
@AuditLog(title = "[资源名称] 管理", desc = "导出 Excel", businessType = BusinessType.EXPORT)
@GetMapping("/export")
public void export([Resource]ExportParam param, HttpServletResponse response) {
    List<[Resource]ExcelDTO> list = [resource]Service.listExport(param);
    ExcelUtils<[Resource]ExcelDTO> util = new ExcelUtils<>([Resource]ExcelDTO.class);
    util.exportExcel(list, "[资源名称] 列表", response);
}
```

**ExcelDTO 模板**：

```java
@Data
public class [Resource]ExcelDTO {
    
    @Excel(name = "资源 ID", orderNum = "1")
    private String id;
    
    @Excel(name = "资源名称", orderNum = "2")
    private String name;
    
    @Excel(name = "资源编码", orderNum = "3")
    private String code;
    
    @Excel(name = "状态", orderNum = "4", readConverterExp = "0=禁用，1=启用")
    private Integer status;
    
    @Excel(name = "创建时间", orderNum = "5", dateFormat = "yyyy-MM-dd HH:mm:ss")
    private Date createTime;
}
```

---

### 模板 9：导入接口

```markdown
### [模块名称] 导入 Excel

**接口路径**：`POST {基础路径}/import`

**权限标识**：`{module}:import`

**功能说明**：从 Excel 文件导入 [资源名称]

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| file | File | Form | 是 | - | Excel 文件 |

**请求示例**：

```http
POST /api/{module}/{resource}/import
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: [Excel 文件]
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "totalCount": 100,
    "successCount": 98,
    "failCount": 2,
    "failRecords": [
      {
        "rowNum": 5,
        "reason": "资源编码已存在"
      },
      {
        "rowNum": 10,
        "reason": "资源名称不能为空"
      }
    ]
  }
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| totalCount | Integer | 总记录数 |
| successCount | Integer | 成功导入数 |
| failCount | Integer | 失败记录数 |
| failRecords | Array | 失败记录详情 |
| failRecords[].rowNum | Integer | 行号 |
| failRecords[].reason | String | 失败原因 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 400 | 请求参数错误 | 文件为空或格式错误 |
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:import")
@ApiOperation("[资源名称] 导入 Excel")
@AuditLog(title = "[资源名称] 管理", desc = "导入 Excel", businessType = BusinessType.INSERT)
@PostMapping("/import")
public RestResponse<[Resource]ImportDTO> excelImport(@RequestParam("file") MultipartFile file) {
    ExcelUtils<[Resource]ExcelDTO> util = new ExcelUtils<>([Resource]ExcelDTO.class);
    List<[Resource]ExcelDTO> rows = new ArrayList<>();
    try {
        rows = util.importExcel(file.getInputStream());
    } catch (Exception e) {
        log.error("[资源名称]Excel 导入异常", e);
    }
    [Resource]ImportDTO result = [resource]Service.importData(rows);
    return RestResponse.ok(result);
}
```

---

### 模板 10：树形结构接口

```markdown
### [模块名称] 获取树形结构

**接口路径**：`GET {基础路径}/tree`

**权限标识**：`{module}:tree`

**功能说明**：获取 [资源名称] 的树形结构数据

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| keyword | String | Query | 否 | - | 关键词（筛选） |
| status | Integer | Query | 否 | - | 状态：0-禁用，1-启用 |

**请求示例**：

```http
GET /api/{module}/{resource}/tree?keyword=test
Authorization: Bearer {token}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "key": "1",
      "title": "根节点 1",
      "children": [
        {
          "key": "1-1",
          "title": "子节点 1-1",
          "children": [],
          "isLeaf": true
        },
        {
          "key": "1-2",
          "title": "子节点 1-2",
          "children": [],
          "isLeaf": true
        }
      ],
      "isLeaf": false
    },
    {
      "key": "2",
      "title": "根节点 2",
      "children": [],
      "isLeaf": true
    }
  ]
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| key | String | 节点 ID |
| title | String | 节点名称 |
| children | Array | 子节点列表 |
| isLeaf | Boolean | 是否叶子节点 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:tree")
@ApiOperation("[资源名称] 获取树形结构")
@AuditLog(title = "[资源名称] 管理", desc = "获取树形结构", businessType = BusinessType.QUERY)
@GetMapping("/tree")
public RestResponse<List<Tree<String>>> tree(@RequestParam(required = false) String keyword) {
    return RestResponse.ok([resource]Service.tree(keyword));
}
```

---

## 三、特殊场景模板

### 模板 11：文件上传接口

```markdown
### [模块名称] 文件上传

**接口路径**：`POST {基础路径}/upload`

**权限标识**：`{module}:upload`

**功能说明**：上传文件到 [存储位置]

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| file | File | Form | 是 | - | 文件 |
| bizType | String | Form | 否 | - | 业务类型 |

**请求示例**：

```http
POST /api/{module}/file/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: [文件]
bizType: avatar
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "fileId": "123",
    "fileName": "avatar.png",
    "filePath": "/files/2024/01/15/avatar.png",
    "fileUrl": "http://cdn.example.com/files/2024/01/15/avatar.png",
    "fileSize": 102400
  }
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| fileId | String | 文件 ID |
| fileName | String | 文件名称 |
| filePath | String | 文件路径 |
| fileUrl | String | 文件访问 URL |
| fileSize | Long | 文件大小（字节） |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 400 | 请求参数错误 | 文件为空或超出大小限制 |
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:upload")
@ApiOperation("文件上传")
@AuditLog(title = "文件管理", desc = "文件上传", businessType = BusinessType.INSERT)
@PostMapping("/upload")
public RestResponse<FileUploadDTO> upload(
        @RequestParam("file") MultipartFile file,
        @RequestParam(value = "bizType", required = false) String bizType) {
    
    FileUploadDTO result = fileService.upload(file, bizType);
    return RestResponse.ok(result);
}
```

---

### 模板 12：统计/报表接口

```markdown
### [模块名称] 统计数据

**接口路径**：`GET {基础路径}/statistics`

**权限标识**：`{module}:statistics`

**功能说明**：获取 [业务场景] 的统计数据

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| startDate | String | Query | 是 | - | 开始日期（yyyy-MM-dd） |
| endDate | String | Query | 是 | - | 结束日期（yyyy-MM-dd） |
| dimension | String | Query | 否 | day | 统计维度：day/week/month |

**请求示例**：

```http
GET /api/{module}/report/statistics?startDate=2024-01-01&endDate=2024-01-31&dimension=day
Authorization: Bearer {token}
```

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "totalCount": 1000,
    "successCount": 950,
    "failCount": 50,
    "trendData": [
      {"date": "2024-01-01", "value": 30},
      {"date": "2024-01-02", "value": 35},
      {"date": "2024-01-03", "value": 28}
    ],
    "categoryData": [
      {"category": "类别 A", "count": 500},
      {"category": "类别 B", "count": 300},
      {"category": "类别 C", "count": 200}
    ]
  }
}
```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| totalCount | Long | 总数 |
| successCount | Long | 成功数 |
| failCount | Long | 失败数 |
| trendData | Array | 趋势数据 |
| trendData[].date | String | 日期 |
| trendData[].value | Integer | 数值 |
| categoryData | Array | 分类数据 |
| categoryData[].category | String | 分类名称 |
| categoryData[].count | Integer | 数量 |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| 400 | 请求参数错误 | 日期格式错误或必填参数缺失 |
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 500 | 系统异常 | 服务器内部错误 |
```

**Controller 代码模板**：

```java
@Permission("{module}:statistics")
@ApiOperation("统计数据")
@AuditLog(title = "报表管理", desc = "统计数据", businessType = BusinessType.QUERY)
@GetMapping("/statistics")
public RestResponse<StatisticsDTO> statistics(
        @RequestParam("startDate") String startDate,
        @RequestParam("endDate") String endDate,
        @RequestParam(value = "dimension", defaultValue = "day") String dimension) {
    
    StatisticsDTO result = [resource]Service.statistics(startDate, endDate, dimension);
    return RestResponse.ok(result);
}
```

---

## 四、快速复制模板

### 空白模板（可直接填充）

```markdown
### [接口名称]

**接口路径**：`{METHOD} {路径}`

**权限标识**：``

**功能说明**：

**请求参数**：

| 参数名 | 类型 | 位置 | 必填 | 默认值 | 说明 |
|-------|------|------|------|--------|------|
| | | | | | |

**请求示例**：

```http

```

**响应示例**：

```json

```

**返回参数字段说明**：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| | | |

**错误响应**：

| 错误码 | 错误信息 | 触发条件 |
|-------|---------|---------|
| | | |
```

---

## 五、附录

### A. 权限标识命名规范

| 模块 | 前缀 | 示例 |
|------|------|------|
| 用户管理 | `User` | `UserManage`、`UserManageEdit` |
| 角色管理 | `Role` | `RoleManage`、`RoleManageEdit` |
| 菜单管理 | `Menu` | `MenuManage`、`MenuManageAdd` |
| 组织管理 | `Org` | `OrgManage`、`OrgManageEdit` |
| 文件管理 | `file:` | `file:info:upload`、`file:info:export` |
| 业务模块 | `{业务}-{功能}-` | `dmanage-clue-list:add` |

### B. DTO 命名规范

| 类型 | 后缀 | 示例 |
|------|------|------|
| 查询参数 | `QueryParam` | `UserQueryParam` |
| 新增参数 | `AddParam` | `UserAddParam` |
| 修改参数 | `EditParam` 或 `UpdateParam` | `UserEditParam` |
| 详情参数 | `GetParam` | `UserManageGetParam` |
| 状态参数 | `StatusParam` | `UserStatusParam` |
| 导出参数 | `ExportParam` | `UserExportParam` |
| 数据 DTO | `DTO` | `UserDTO` |
| 详情 VO | `DetailVO` 或 `VO` | `UserDetailVO` |
| Excel DTO | `ExcelDTO` | `UserExcelDTO` |
| 导入结果 | `ImportDTO` | `UserImportDTO` |

### C. 常用注解清单

```java
// Controller 类注解
@RestController          // REST 控制器
@RequestMapping("/path") // 基础路径
@Api(tags = "模块名称")   // Swagger 标签

// 方法注解
@GetMapping              // GET 请求
@PostMapping             // POST 请求
@PutMapping              // PUT 请求
@DeleteMapping           // DELETE 请求
@ApiOperation            // 接口描述
@AuditLog                // 操作日志
@Permission              // 权限标识

// 参数注解
@RequestBody             // 请求体
@RequestParam            // 请求参数
@PathVariable            // 路径变量
@Valid                   // 参数校验

// 字段校验注解
@NotNull                 // 非 null
@NotBlank                // 非空字符串
@NotEmpty                // 集合非空
@Size                    // 长度/大小
@Min/@Max                // 数值范围
@Email                   // 邮箱格式
@Pattern                 // 正则表达式
```

---

**使用说明**：

1. 复制对应场景的模板
2. 替换 `[模块名称]`、`[资源名称]`、`{module}`、`{resource}` 等占位符
3. 根据实际需求调整参数字段
4. 按照模板编写 Controller、Param、DTO 类
5. 测试接口并更新 Swagger 文档
