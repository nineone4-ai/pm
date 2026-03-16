# PM3 API 设计基准规范

> 文档版本：v1.0  
> 最后更新：2026-03-03  
> 适用范围：pm-platform、pm-development 模块

---

## 一、模块与功能划分规则

### 1.1 模块界定

PM3 项目按业务域划分为以下主要模块：

| 模块 | 路径前缀 | 职责 | 示例 |
|------|----------|------|------|
| pm-platform | `/api/myth-platform/` | 平台基础服务 | 主数据、组织、权限 |
| pm-permission | `/api/myth-permission/` | 权限管理服务 | 用户、角色、菜单 |
| pm-development | `/api/pm-development/` | 开发业务服务 | 线索、立项、 quota |
| pm-oss | `/fileInfo` | 文件服务 | 文件上传下载 |

### 1.2 功能边界划分原则

1. **单一职责**：每个 Controller 只负责一个业务实体的 CRUD
2. **API路径**：接口统一使用 `/api/` 路径前缀
3. **业务聚合**：同一业务实体的所有操作放在同一 Controller

### 1.3 版本管理规则

- **版本号位置**：路径第二段，如 `/api/myth-permission/user`

---

## 二、API 命名规范

### 2.1 URL 路径命名规则

**路径格式**：`api//{模块}/{资源}/{操作}`

```
✅ 正确示例：
/api/myth-permission/user/manage/list
/api/myth-platform/master/detail/{projectId}
/api/pm-development/pmDevClueMain/add

❌ 错误示例：
/api/myth-permission/getUserList    # 动词开头
/api/myth-permission/User/List      # 大写开头
```

### 2.2 大小写规范

| 位置 | 规范 | 示例 |
|------|------|------|
| 路径段 | kebab-case（小写 + 连字符） | `/sec-staff` |
| 资源名 | camelCase（小驼峰） | `/pmDevClueMain` |
| 操作名 | camelCase（小驼峰） | `/userPageByOrgCode` |

### 2.3 资源名词单复数规则

- **集合操作**：使用复数（但 PM3 实践中多用单数）
- **单个资源**：使用单数
- **PM3 现状**：统一使用单数形式

### 2.4 嵌套资源路径规范

```java
// 二级资源嵌套
GET /api/myth-platform/org/{orgCode}/users

// 状态子资源
POST /api/myth-permission/role/{roleCode}/status

// 操作子资源
POST /api/myth-permission/menu/{menuId}/children
```

### 2.5 常见操作的标准命名

| 操作 | 路径后缀 | HTTP 方法 |
|------|----------|----------|
| 分页列表 | `/list` 或 `/pageList` | GET/POST |
| 详情获取 | `/get` 或 `/detail/{id}` | GET |
| 新增 | `/add` 或 `/manage` | POST |
| 修改 | `/update` 或 `/manage` | POST/PUT |
| 删除 | `/delete` 或 `/{id}` | POST/DELETE |
| 启用/禁用 | `/updateStatus` | POST/PUT |
| 批量删除 | `/batchDelete/{ids}` 或 `/deleteByIds` | DELETE |
| 导出 | `/export` | GET/POST |
| 导入 | `/import` | POST |
| 树形结构 | `/tree` | GET |

---

## 三、必要元素清单

每个 API 必须包含以下元素：

### 3.1 权限标识（@Permission）

```java
// 格式：模块：功能：操作
@Permission("UserManage")              // 简单权限
@Permission("dmanage-clue-list:add")   // 细粒度权限
@Permission("file:info:export")        // 冒号分隔权限
```

**权限命名规则**：
- 平台模块：使用英文单词，如 `UserManage`、`RoleManageEdit`
- 业务模块：使用 kebab-case，如 `dmanage-clue-list:add`
- 文件模块：使用冒号分隔，如 `file:info:export`

### 3.2 请求方法（HTTP Method）

| 注解 | 用途 | 示例 |
|------|------|------|
| `@GetMapping` | 查询操作 | 列表、详情、树形 |
| `@PostMapping` | 创建、更新、复杂查询 | 新增、修改、分页查询 |
| `@PutMapping` | 更新操作 | 状态变更、全量更新 |
| `@DeleteMapping` | 删除操作 | 单个删除、批量删除 |
| `@PatchMapping` | 部分更新 | （PM3 暂未使用） |

### 3.3 完整路径（含版本号）

```java
@RestController
@RequestMapping("/api/myth-permission/user")
public class UserV3Controller {
    // 完整路径：/api/myth-permission/user/manage/list
    @GetMapping("/manage/list")
    public RestResponse<PageResult<UserDTO>> pageList(...) { }
}
```

### 3.4 入参定义

```java
// 必须使用参数对象，禁止散参
public RestResponse<PageResult<UserDTO>> pageList(
    @Valid UserQueryParam param  // 必须使用@Valid 校验
) { }

// Request Body 必须标注@RequestBody
public RestResponse<String> add(
    @RequestBody @Valid UserAddParam param
) { }

// 路径变量必须标注@PathVariable
public RestResponse<UserDTO> detail(
    @PathVariable String userId
) { }

// 查询参数必须标注@RequestParam（可选参数需标注 required=false）
public RestResponse<List<UserDTO>> list(
    @RequestParam("orgCode") String orgCode,
    @RequestParam(value = "keyword", required = false) String keyword
) { }
```

### 3.5 出参结构

```java
// 所有接口必须使用 RestResponse 包装
public RestResponse<T> method(...) {
    return RestResponse.ok(data);      // 成功
    return RestResponse.failed(msg);   // 失败
}
```

### 3.6 错误码定义

PM3 使用标准 HTTP 状态码 + 业务错误码：

| 错误码 | 含义 | 触发条件 |
|--------|------|----------|
| 200 | 成功 | 操作成功 |
| 400 | 请求参数错误 | 参数校验失败 |
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 500 | 服务器内部错误 | 系统异常 |

---

## 四、常见接口命名示例

### 4.1 列表查询（分页）

```java
@ApiOperation("分页获取角色列表")
@GetMapping("/manage/list")
public RestResponse<PageResult<RoleDTO>> pageList(
    @Valid RoleQueryParam roleQueryParam,
    HttpServletRequest request
) {
    String languageCode = request.getHeader(HttpHeaders.ACCEPT_LANGUAGE);
    if(StrUtil.isBlank(languageCode)){
        languageCode = CommonConstants.DEFAULT_LANGGUAGE;
    }
    roleQueryParam.setLanguageCode(languageCode);
    PageResult<RoleDTO> roleDTOPageResult = sunGrowRoleService.pageDTO(roleQueryParam);
    return RestResponse.ok(roleDTOPageResult);
}
```

### 4.2 详情获取

```java
@Permission("projectMasterData:detail")
@AuditLog(title = "项目详情", businessType = BusinessType.QUERY)
@ApiOperation("项目详情")
@GetMapping("/detail/{projectId}")
public RestResponse<ProjectDetailVO> detail(@PathVariable String projectId){
    return RestResponse.ok(mdmMasterDataService.detail(projectId));
}
```

### 4.3 创建/新增

```java
@Permission("dmanage-clue-list:add")
@ApiOperation("新增线索申请数据")
@AuditLog(title = "线索主表", desc = "新增线索申请数据", businessType = BusinessType.INSERT)
@PostMapping("/add")
public RestResponse<String> add(@RequestBody PmDevClueMainAddParam pmDevClueMainAddParam) {
    pmDevClueMainService.saveClueMain(pmDevClueMainAddParam);
    return RestResponse.ok("提交或者保存成功");
}
```

### 4.4 更新（全量）

```java
@ApiOperation(value = "修改角色")
@AuditLog(title = "角色-", desc = "修改角色", businessType = BusinessType.UPDATE)
@PostMapping("manage/update")
public RestResponse<Boolean> update(@RequestBody @Valid RoleEditParam roleEditParam) {
    return RestResponse.ok(sunGrowRoleService.updateByParam(roleEditParam));
}
```

### 4.5 删除

```java
// 单个删除
@ApiOperation(value = "根据 code 删除角色")
@AuditLog(title = "角色-", desc = "删除角色", businessType = BusinessType.DELETE)
@PostMapping("/delete")
public RestResponse<Boolean> delete(@RequestParam(name = "roleCode") String roleCode) {
    return RestResponse.ok(sunGrowRoleService.removeRoleByCode(roleCode));
}

// 批量删除（路径变量方式）
@ApiOperation("批量删除主数据 - 语种")
@DeleteMapping("/batchDelete/{ids}")
@AuditLog(title = "主数据 - 语种批量删除", businessType = BusinessType.DELETE)
public RestResponse batchDelete(@PathVariable("ids") @NotEmpty List<String> ids){
    return RestResponse.ok(languageService.deleteByIds(ids));
}

// 批量删除（请求体方式）
@ApiOperation(value = "twork 根据 id 删除角色")
@AuditLog(title = "角色管理", desc = "twork 根据 id 删除角色", businessType = BusinessType.DELETE)
@DeleteMapping("/deleteByIds")
public RestResponse<Boolean> deleteByIds(@RequestBody List<String> ids) {
    return RestResponse.ok(roleService.removeRoleByIds(ids));
}
```

### 4.6 状态变更（审核、启用/禁用）

```java
@ApiOperation(value = "启用/禁用")
@PostMapping("/updateStatus")
@AuditLog(title = "角色-", desc = "启用/禁用", businessType = BusinessType.UPDATE)
public RestResponse<Boolean> updateStatus(@RequestBody RoleStatusParam param){
    return RestResponse.ok(sunGrowRoleService.updateStatus(param));
}
```

### 4.7 批量操作

```java
// 批量删除见 4.5 示例

// 批量授权、批量导入等遵循相同模式：
// 1. 使用@RequestBody 接收参数数组或集合
// 2. 返回 RestResponse<Boolean> 或 RestResponse<Integer>（影响行数）
```

### 4.8 导入/导出

```java
// Excel 导入
@ApiOperation(value = "Excel 导入菜单")
@AuditLog(title = "导入菜单", desc = "Excel 导入菜单", businessType = BusinessType.INSERT)
@PostMapping("/import")
public RestResponse<MenuImportDTO> excelImport(@RequestParam("file") MultipartFile file) {
    ExcelUtils<MenuExcelDTO> util = new ExcelUtils<>(MenuExcelDTO.class);
    List<MenuExcelDTO> rows = new ArrayList<MenuExcelDTO>();
    try {
        rows = util.importExcel(file.getInputStream());
    } catch (Exception e) {
        log.error("用户 Excel 导入异常", e);
    }
    MenuImportDTO result = menuService.importMenus(rows);
    return RestResponse.ok(result);
}

// Excel 导出
@ApiOperation(value = "导出系统菜单")
@AuditLog(title = "导出系统菜单", desc = "导出系统菜单", businessType = BusinessType.EXPORT)
@PostMapping("/export")
public void excelExport(@RequestBody @Valid MenuExportParam param, HttpServletResponse response) {
    List<MenuExcelDTO> menus = menuService.listExportMenus(param);
    ExcelUtils<MenuExcelDTO> util = new ExcelUtils<>(MenuExcelDTO.class);
    util.exportExcel(menus, "系统菜单", response);
}
```

---

## 五、入参规范

### 5.1 Query Parameter 使用场景和命名规则

**使用场景**：
- GET 请求的简单查询参数
- 文件下载的标识参数
- 树形结构的筛选参数

**命名规则**：
```java
// 单个参数
@RequestParam("orgCode") String orgCode

// 可选参数
@RequestParam(value = "keyword", required = false) String keyword

// 带默认值
@RequestParam(value = "pageNum", defaultValue = "1") Integer pageNum
```

### 5.2 Path Variable 使用场景和命名规则

**使用场景**：
- 资源标识符（ID、Code）
- 层级资源定位
- 批量操作的 ID 列表

**命名规则**：
```java
// 单个资源 ID
@GetMapping("/detail/{projectId}")
public RestResponse<ProjectDetailVO> detail(@PathVariable String projectId)

// 批量 ID（逗号分隔）
@DeleteMapping("/batchDelete/{ids}")
public RestResponse batchDelete(@PathVariable("ids") @NotEmpty List<String> ids)
```

### 5.3 Request Body 使用场景

**使用场景**：
- POST/PUT 请求的复杂参数
- 需要参数校验的场景
- 列表、分页查询（多条件）

**DTO 使用规范**：
```java
// 查询参数对象：*QueryParam
public RestResponse<PageResult<UserDTO>> pageList(
    @RequestBody @Valid UserQueryParam param
)

// 新增参数对象：*AddParam 或*SaveParam
public RestResponse<String> add(
    @RequestBody @Valid UserAddParam param
)

// 编辑参数对象：*EditParam 或*UpdateParam
public RestResponse<Boolean> update(
    @RequestBody @Valid UserEditParam param
)

// 导出参数对象：*ExportParam
public void export(
    @RequestBody @Valid UserExportParam param,
    HttpServletResponse response
)
```

### 5.4 参数校验注解使用规范

```java
// 类级别校验
@Data
public class UserAddParam {
    
    // 必填校验
    @NotNull(message = "用户 ID 不能为空")
    private String userId;
    
    // 字符串长度校验
    @NotBlank(message = "用户名不能为空")
    @Size(max = 50, message = "用户名长度不能超过 50 字符")
    private String userName;
    
    // 邮箱格式校验
    @Email(message = "邮箱格式不正确")
    private String email;
    
    // 数字范围校验
    @Min(value = 0, message = "年龄不能小于 0")
    @Max(value = 150, message = "年龄不能大于 150")
    private Integer age;
    
    // 集合非空校验
    @NotEmpty(message = "角色 ID 列表不能为空")
    private List<String> roleIds;
}

// 方法级别校验（必须配合@Valid 使用）
public RestResponse<String> add(@RequestBody @Valid UserAddParam param)
```

### 5.5 日期/时间参数格式

**PM3 项目使用规范**：

```java
// 推荐使用：ISO8601 字符串格式
private String createTime;    // "2024-01-15 10:30:00"

// 或：Long 类型时间戳
private Long createTimeStamp; // 1705284600000

// 日期范围查询
private String startDate;     // "2024-01-01"
private String endDate;       // "2024-12-31"
```

**注解标注**：
```java
@DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
private Date createTime;
```

---

## 六、出参规范

### 6.1 统一响应结构

PM3 项目使用 `RestResponse<T>` 作为统一响应包装类：

```java
public class RestResponse<T> {
    private Integer code;      // 状态码：200=成功，其他=失败
    private String message;    // 提示信息
    private T data;            // 业务数据
    
    public static <T> RestResponse<T> ok(T data)
    public static <T> RestResponse<T> ok()
    public static <T> RestResponse<T> failed(String message)
    public static <T> RestResponse<T> failed(Integer code, String message)
}
```

**成功响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "userId": "123",
    "userName": "张三"
  }
}
```

**失败响应示例**：
```json
{
  "code": 500,
  "message": "系统异常，请稍后重试",
  "data": null
}
```

### 6.2 分页响应格式

PM3 使用 `PageResult<T>` 作为分页响应包装：

```java
public class PageResult<T> {
    private long total;           // 总记录数
    private List<T> records;      // 当前页数据列表
    private long pageNum;         // 当前页码
    private long pageSize;        // 每页大小
    private long pages;           // 总页数
}
```

**分页响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "records": [
      {"id": "1", "name": "张三"},
      {"id": "2", "name": "李四"}
    ],
    "pageNum": 1,
    "pageSize": 10,
    "pages": 10
  }
}
```

### 6.3 树形结构返回格式

PM3 使用 `Tree<T>` 结构返回树形数据：

```java
public class Tree<T> {
    private T key;                      // 节点标识（通常是 ID）
    private String title;               // 节点标题（通常是名称）
    private List<Tree<T>> children;     // 子节点列表
    private Boolean isLeaf;             // 是否叶子节点
    // 其他扩展字段...
}
```

**树形响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "key": "1",
      "title": "研发部",
      "children": [
        {
          "key": "1-1",
          "title": "后端组",
          "children": [],
          "isLeaf": true
        }
      ],
      "isLeaf": false
    }
  ]
}
```

### 6.4 错误响应格式

```json
{
  "code": 403,
  "message": "无权限访问该资源",
  "data": null
}
```

**常见错误码**：

| 错误码 | 错误信息 | 触发条件 |
|--------|---------|---------|
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 无权限 | 用户无该接口权限 |
| 404 | 资源不存在 | 请求的资源 ID 不存在 |
| 400 | 请求参数错误 | 参数校验失败 |
| 500 | 系统异常 | 服务器内部错误 |

### 6.5 字段命名规则

**统一使用 camelCase（小驼峰）**：

```java
// ✅ 正确
private String userId;
private String userName;
private Date createTime;

// ❌ 错误
private String user_id;      // snake_case
private String UserID;       // PascalCase
```

### 6.6 空值处理

| 数据类型 | 空值处理 | 示例 |
|----------|----------|------|
| 字符串 | 空字符串 `""` | `""` |
| 数值类型 | `null` | `null` |
| 集合类型 | 空数组 `[]` | `[]` |
| 对象类型 | `null` | `null` |

**禁止返回 undefined 或未定义的字段**。

---

## 七、示例代码

### 7.1 完整 Controller 示例

```java
package com.sungrow.pm.platform.controller.sungrow;

import com.sungrow.pm.platform.annotation.AuditLog;
import com.sungrow.pm.platform.annotation.Permission;
import com.sungrow.pm.platform.common.businesstype.BusinessType;
import com.sungrow.pm.platform.common.rest.RestResponse;
import com.sungrow.pm.platform.dto.role.RoleDTO;
import com.sungrow.pm.platform.param.role.*;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 角色管理 Controller
 * 
 * @author PM3 Team
 * @since 2024-01-01
 */
@Api(tags = "角色管理")
@RestController
@RequestMapping("/api/myth-permission/sungrow/role")
@RequiredArgsConstructor
public class RoleController {

    private final SunGrowRoleService sunGrowRoleService;

    /**
     * 分页获取角色列表
     * 
     * @param roleQueryParam 查询参数
     * @param request HTTP 请求
     * @return 分页角色列表
     */
    @ApiOperation("分页获取角色列表")
    @GetMapping("/manage/list")
    public RestResponse<PageResult<RoleDTO>> pageList(
            @Valid RoleQueryParam roleQueryParam,
            HttpServletRequest request) {
        
        String languageCode = request.getHeader(HttpHeaders.ACCEPT_LANGUAGE);
        if(StrUtil.isBlank(languageCode)){
            languageCode = CommonConstants.DEFAULT_LANGGUAGE;
        }
        roleQueryParam.setLanguageCode(languageCode);
        PageResult<RoleDTO> roleDTOPageResult = sunGrowRoleService.pageDTO(roleQueryParam);
        return RestResponse.ok(roleDTOPageResult);
    }

    /**
     * 根据 ID 获取角色详情
     * 
     * @param roleQueryParam 包含角色 ID 的参数
     * @param request HTTP 请求
     * @return 角色详情
     */
    @ApiOperation("主键获取角色信息")
    @GetMapping("/get")
    public RestResponse<RoleDTO> getById(
            RoleManageGetParam roleQueryParam,
            HttpServletRequest request) {
        
        String languageCode = request.getHeader(HttpHeaders.ACCEPT_LANGUAGE);
        if(StrUtil.isBlank(languageCode)){
            languageCode = CommonConstants.DEFAULT_LANGGUAGE;
        }
        RoleDTO roleDTO = sunGrowRoleService.getByRoleId(roleQueryParam.getId());
        return RestResponse.ok(roleDTO);
    }

    /**
     * 新增角色
     * 
     * @param roleAddParam 新增参数
     * @return 操作结果
     */
    @ApiOperation("新增角色")
    @AuditLog(title = "角色管理", desc = "新增角色", businessType = BusinessType.INSERT)
    @PostMapping("/manage/add")
    public RestResponse<String> add(@RequestBody @Valid RoleManageAddParam roleAddParam) {
        String result = sunGrowRoleService.saveByParam(roleAddParam);
        if(StringUtils.isBlank(result)){
            return RestResponse.ok(result);
        }else {
            return RestResponse.failed(result);
        }
    }

    /**
     * 修改角色
     * 
     * @param roleEditParam 修改参数
     * @return 操作结果
     */
    @ApiOperation(value = "修改角色")
    @AuditLog(title = "角色管理", desc = "修改角色", businessType = BusinessType.UPDATE)
    @PostMapping("manage/update")
    public RestResponse<Boolean> update(@RequestBody @Valid RoleEditParam roleEditParam) {
        return RestResponse.ok(sunGrowRoleService.updateByParam(roleEditParam));
    }

    /**
     * 启用/禁用角色
     * 
     * @param param 状态参数
     * @return 操作结果
     */
    @ApiOperation(value = "启用/禁用")
    @PostMapping("/updateStatus")
    @AuditLog(title = "角色管理", desc = "启用/禁用", businessType = BusinessType.UPDATE)
    public RestResponse<Boolean> updateStatus(@RequestBody RoleStatusParam param){
        return RestResponse.ok(sunGrowRoleService.updateStatus(param));
    }

    /**
     * 根据 code 删除角色
     * 
     * @param roleCode 角色编码
     * @return 操作结果
     */
    @ApiOperation(value = "根据 code 删除角色")
    @AuditLog(title = "角色管理", desc = "删除角色", businessType = BusinessType.DELETE)
    @PostMapping("/delete")
    public RestResponse<Boolean> delete(@RequestParam(name = "roleCode") String roleCode) {
        return RestResponse.ok(sunGrowRoleService.removeRoleByCode(roleCode));
    }
}
```

### 7.2 DTO 示例

```java
package com.sungrow.pm.platform.param.role;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.util.List;

/**
 * 角色查询参数
 */
@ApiModel("角色查询参数")
@Data
public class RoleQueryParam {
    
    @ApiModelProperty("页码")
    @NotNull(message = "页码不能为空")
    private Integer pageNum = 1;
    
    @ApiModelProperty("每页大小")
    @NotNull(message = "每页大小不能为空")
    private Integer pageSize = 10;
    
    @ApiModelProperty("角色名称（模糊查询）")
    private String roleName;
    
    @ApiModelProperty("角色编码")
    private String roleCode;
    
    @ApiModelProperty("启用状态：0-禁用，1-启用")
    private Integer enableStatus;
    
    @ApiModelProperty("语言编码")
    private String languageCode;
}

/**
 * 角色新增参数
 */
@ApiModel("角色新增参数")
@Data
public class RoleManageAddParam {
    
    @NotBlank(message = "角色编码不能为空")
    @ApiModelProperty("角色编码")
    private String roleCode;
    
    @NotBlank(message = "角色名称不能为空")
    @ApiModelProperty("角色名称")
    private String roleName;
    
    @ApiModelProperty("角色描述")
    private String remark;
    
    @ApiModelProperty("排序号")
    private Integer sort;
    
    @NotNull(message = "菜单 ID 列表不能为空")
    @ApiModelProperty("菜单 ID 列表")
    private List<String> menuIds;
}

/**
 * 角色详情 DTO
 */
@ApiModel("角色详情 DTO")
@Data
public class RoleDTO {
    
    @ApiModelProperty("角色 ID")
    private String id;
    
    @ApiModelProperty("角色编码")
    private String roleCode;
    
    @ApiModelProperty("角色名称")
    private String roleName;
    
    @ApiModelProperty("角色描述")
    private String remark;
    
    @ApiModelProperty("排序号")
    private Integer sort;
    
    @ApiModelProperty("启用状态")
    private Integer enableStatus;
    
    @ApiModelProperty("菜单 ID 列表")
    private List<String> menuIds;
    
    @ApiModelProperty("创建时间")
    private String createTime;
    
    @ApiModelProperty("更新时间")
    private String updateTime;
}
```

---

## 八、附录

### 8.1 常用注解速查

| 注解 | 用途 | 示例 |
|------|------|------|
| `@RestController` | 标识 REST 控制器 | `@RestController` |
| `@RequestMapping` | 定义基础路径 | `@RequestMapping("/api/user")` |
| `@GetMapping` | GET 请求映射 | `@GetMapping("/list")` |
| `@PostMapping` | POST 请求映射 | `@PostMapping("/add")` |
| `@PutMapping` | PUT 请求映射 | `@PutMapping("/update")` |
| `@DeleteMapping` | DELETE 请求映射 | `@DeleteMapping("/delete")` |
| `@ApiOperation` | Swagger 接口描述 | `@ApiOperation("用户列表")` |
| `@ApiModel` | Swagger 模型描述 | `@ApiModel("用户参数")` |
| `@ApiModelProperty` | Swagger 字段描述 | `@ApiModelProperty("用户名")` |
| `@Permission` | 权限标识 | `@Permission("UserManage")` |
| `@AuditLog` | 操作日志 | `@AuditLog(title = "用户管理")` |
| `@Valid` | 参数校验 | `@Valid UserAddParam param` |
| `@RequestBody` | 请求体绑定 | `@RequestBody UserAddParam param` |
| `@RequestParam` | 请求参数绑定 | `@RequestParam("id") String id` |
| `@PathVariable` | 路径变量绑定 | `@PathVariable String id` |

### 8.2 校验注解速查

| 注解 | 用途 | 示例 |
|------|------|------|
| `@NotNull` | 非 null 校验 | `@NotNull(message = "ID 不能为空")` |
| `@NotBlank` | 非空字符串校验 | `@NotBlank(message = "名称不能为空")` |
| `@NotEmpty` | 集合非空校验 | `@NotEmpty(message = "列表不能为空")` |
| `@Size` | 长度/大小校验 | `@Size(max = 50, message = "长度不超过 50")` |
| `@Min` | 最小值校验 | `@Min(value = 0, message = "最小值为 0")` |
| `@Max` | 最大值校验 | `@Max(value = 100, message = "最大值为 100")` |
| `@Email` | 邮箱格式校验 | `@Email(message = "邮箱格式不正确")` |
| `@Pattern` | 正则表达式校验 | `@Pattern(regexp = "^1[3-9]\\d{9}$")` |

### 8.3 相关文档

- 《PM3-API 模板文档.md》- 可复用的接口清单模板
- Swagger UI: `http://localhost:8080/swagger-ui.html`
