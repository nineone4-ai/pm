---
name: pm3-skeleton-generator
description: "基于 OpenSpec 系分产物生成 PM3 微服务的可编译代码骨架。读取冻结的 API Spec、领域模型、系分文档，通过 6-Agent 流水线生成完整的 Controller、Service、Entity、Mapper、Feign Client 等代码框架，执行 mvn compile 验证，输出带 TODO 的任务清单供后续实现。触发词：'基于系分生成代码骨架'、'生成 pm-xxx 代码框架'"
---

# PM3 代码骨架生成器

基于系分产物（API Spec + 领域模型 + 系分文档）生成 PM3 微服务的可编译代码骨架。

## 核心原则

> **可编译，但零业务逻辑。**

骨架是介于"空项目"和"完整实现"之间的中间态：
- 确保项目**立即可运行**（mvn compile 通过）
- 为后续实现 Agent 提供**清晰的实现入口**（每个 TODO 是一个任务）
- 固化**分层架构约束**（Controller 不直接调 DAO）

---

## 触发条件

当用户说以下内容时触发：
- "基于系分生成代码骨架"
- "生成 pm-xxx 的代码框架"
- "根据系分文档创建微服务结构"
- "Skeleton generation for pm-xxx"
- "为订单模块生成代码框架"

---

## 路径配置

### 输入路径（系分产物目录）
```
/Users/eason/Documents/Obsidian Vault/20_项目/PM3/01-1-system_analysis/{模块中文名}/
```
- 示例：`/Users/eason/Documents/Obsidian Vault/20_项目/PM3/01-1-system_analysis/国内工程管理/`
- 示例：`/Users/eason/Documents/Obsidian Vault/20_项目/PM3/01-1-system_analysis/国内设计管理/`

系分产物文件：
- `04_api_spec.yaml` - OpenAPI 接口规范
- `03_domain_model.md` - 领域模型文档
- `05_system_design.md` - 系统设计文档

### 输出路径（代码生成目录）
```
/Users/eason/IdeaProjects/pm3/pm-{module}/
```

---

## 前置依赖（必须全部 FROZEN）

执行前确认以下产物已就绪：

| 产物 | 文件 | 用途 |
|------|------|------|
| OpenAPI Spec | `04_api_spec.yaml` | 生成 Controller + DTO |
| 领域模型 | `03_domain_model.md` | 生成 Entity + Mapper |
| 系分文档 | `05_system_design.md` | 生成 Service 接口签名 |

---

## 6-Agent 流水线

```
冻结的系分产物
     ↓
① OpenSpec 整合 Agent（合并产物为统一 Proposal）
     ↓
② 实体层 Agent ──┐
③ 控制层 Agent ──┤ 并行执行
④ 服务层 Agent ──┤
⑤ DAO 层 Agent ──┘
     ↓
⑥ 工程整合 Agent（编译验证）
     ↓
可编译代码骨架（含 TODO 清单）
```

---

## 执行步骤

### Step 1: 读取系分产物

**输入目录：**`/Users/eason/Documents/Obsidian Vault/20_项目/PM3/01-1-system_analysis/{模块中文名}/`

读取以下文件：
- `04_api_spec.yaml` - 获取接口路径、参数、响应定义
- `03_domain_model.md` - 获取实体关系、字段定义
- `05_system_design.md` - 获取业务逻辑、时序图

**模块名称映射：**
- 从目录名提取模块中文名（如`国内工程管理`）
- 根据系分产物推断模块英文名（如`pm-domestic-engineering`）

### Step 2: 创建项目结构

**输出目录：**`/Users/eason/IdeaProjects/pm3/pm-{module}/`

创建项目目录结构：
```
pm-{module}/
├── pom.xml
├── pm-{module}-api/
│   ├── pom.xml
│   └── src/main/java/com/sungrow/pm/{module}/
│       ├── client/          ← Feign Client 接口（跨服务调用）
│       └── dto/             ← DTO（跨服务数据传输）
└── pm-{module}-svc/
    ├── pom.xml
    └── src/main/java/com/sungrow/pm/{module}/
        ├── Application.java
        ├── controller/      ← REST Controller
        ├── service/         ← Service 接口 + 实现
        ├── mapper/          ← MyBatis Mapper
        ├── entity/          ← Entity（数据库实体）
        ├── vo/              ← VO（前后端交互，复杂场景）
        ├── enums/           ← 枚举类
        ├── exception/       ← 异常处理
        └── utils/           ← 工具类
```

**分层定义：**
| 对象 | 用途 | 使用场景 |
|------|------|----------|
| **Entity** | 数据库实体 | 简单列表/详情查询直接使用；Service 层操作 |
| **VO** | 前后端交互对象 | 复杂场景（含子对象集合、附件等） |
| **DTO** | 跨服务数据传输 | Feign Client 调用时使用 |

### Step 3: 生成实体层

根据领域模型生成：

**Entity 类（数据库实体）：**
```java
@Data
@TableName("{table_name}")
public class {Business} {
    @TableId(type = IdType.ASSIGN_UUID)
    private String id;

    // TODO: 根据领域模型添加业务字段

    @TableField(fill = FieldFill.INSERT)
    private Date createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Date updateTime;

    @TableField(fill = FieldFill.INSERT)
    private String createBy;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private String updateBy;

    @TableLogic
    @TableField(fill = FieldFill.INSERT)
    private Integer deleted;
}
```

**VO 类（前后端交互，复杂场景使用）：**
```java
@Data
@ApiModel("{业务名}VO")
public class {Business}VO {
    @ApiModelProperty("主键ID")
    private String id;

    // TODO: 根据业务复杂度添加字段
    // 简单场景：直接使用 Entity
    // 复杂场景（以下情况使用 VO）：
    // 1. 包含子对象集合（如订单包含订单项列表）
    // 2. 包含附件集合
    // 3. 包含关联实体数据（如订单包含用户信息）
    // 4. 需要展示/接收额外计算字段

    @ApiModelProperty("创建时间")
    private Date createTime;

    @ApiModelProperty("更新时间")
    private Date updateTime;
}
```

**DTO 类（跨服务数据传输，API 模块）：**
```java
@Data
public class {Business}DTO implements Serializable {
    private String id;
    // TODO: 跨服务需要传输的字段
    // 注意：DTO 应精简，只包含必要的字段
}
```

### Step 4: 生成控制层

根据 API Spec 生成 Controller：

```java
@RestController
@RequestMapping("/api/pm-{module}/{business}")
@Api(tags = "{业务名}模块接口")
public class {Business}Controller {

    // ========== 列表查询（简单场景：直接使用 Entity） ==========
    @Permission("{module}:list:query")
    @ApiOperation("分页查询")
    @PostMapping("/list")
    public RestResponse<IPage<{Business}>> pageList(@RequestBody {Business} queryParam) {
        return RestResponse.ok(service.pageList(queryParam));
    }

    // ========== 详情查询（简单场景：直接使用 Entity） ==========
    @Permission("{module}:detail:query")
    @ApiOperation("获取详情")
    @GetMapping("/detail/{id}")
    public RestResponse<{Business}> getDetail(@PathVariable String id) {
        return RestResponse.ok(service.getById(id));
    }

    // ========== 复杂场景（使用 VO）示例 ==========
    // @Permission("{module}:detail:query")
    // @ApiOperation("获取详情（含子对象）")
    // @GetMapping("/detail-with-items/{id}")
    // public RestResponse<{Business}VO> getDetailWithItems(@PathVariable String id) {
    //     return RestResponse.ok(service.getDetailVO(id));
    // }

    // ========== 新增（简单场景：直接使用 Entity） ==========
    @Permission("{module}:create:execute")
    @ApiOperation("新增")
    @PostMapping("/create")
    public RestResponse<Boolean> create(@RequestBody {Business} entity) {
        return RestResponse.ok(service.save(entity));
    }

    // ========== 修改（简单场景：直接使用 Entity） ==========
    @Permission("{module}:update:execute")
    @ApiOperation("修改")
    @PostMapping("/update")
    public RestResponse<Boolean> update(@RequestBody {Business} entity) {
        return RestResponse.ok(service.updateById(entity));
    }

    // ========== 删除 ==========
    @Permission("{module}:delete:execute")
    @ApiOperation("删除")
    @PostMapping("/delete/{id}")
    public RestResponse<Boolean> delete(@PathVariable String id) {
        return RestResponse.ok(service.removeById(id));
    }
}
```

**设计说明：**
- **简单 CRUD**：直接使用 Entity 进行前后端交互，减少转换层
- **复杂场景**：使用 VO 封装多个对象/集合
- **新增/修改**：前端传递完整 Entity（含业务字段），后端自动填充审计字段

### Step 5: 生成服务层

**Service 接口（继承 MyBatis-Plus 基础接口）：**
```java
public interface I{Business}Service extends IBaseService<{Business}> {
    // TODO: 根据业务需求添加自定义方法
    // 示例：复杂场景下使用 VO 的方法
    // {Business}VO getDetailVO(String id);
}
```

**Service 实现（关键：带 TODO 的骨架）：**
```java
@Slf4j
@Service
public class {Business}ServiceImpl extends BaseServiceImpl<{Business}Mapper, {Business}>
        implements I{Business}Service {

    // ========== 简单 CRUD 已继承自 BaseServiceImpl ==========
    // save(T entity) - 新增
    // updateById(T entity) - 修改
    // removeById(Serializable id) - 删除
    // getById(Serializable id) - 根据 ID 查询
    // page(Page<T> page, Wrapper<T> queryWrapper) - 分页查询

    // TODO: 实现复杂业务逻辑（需要时使用 VO）
    // @Override
    // public {Business}VO getDetailVO(String id) {
    //     // TODO[1]: 查询主实体
    //     // TODO[2]: 查询子对象集合
    //     // TODO[3]: 查询附件列表
    //     // TODO[4]: 组装 VO 返回
    //     throw new UnsupportedOperationException("待实现：获取详情VO");
    // }
}
```

### Step 6: 生成 DAO 层

**Mapper 接口：**
```java
public interface {Business}Mapper extends BaseMapper<{Business}> {
    // TODO: 自定义查询方法（需要时添加）
    // 示例：复杂分页查询
    // IPage<{Business}> selectPageList(Page<{Business}> page,
    //                                   @Param("param") {Business} queryParam);
}
```

**Mapper XML：**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.sungrow.pm.{module}.mapper.{Business}Mapper">

    <!-- 基础 CRUD 已由 MyBatis-Plus 提供 -->

    <!-- TODO: 自定义复杂查询（需要时添加） -->
    <!--
    <select id="selectPageList" resultType="com.sungrow.pm.{module}.entity.{Business}">
        SELECT
            t.*
        FROM {table_name} t
        WHERE t.deleted = 0
        <!-- 添加动态查询条件 -->
        ORDER BY t.create_time DESC
    </select>
    -->

</mapper>
```

### Step 7: 生成基础设施

**启动类：**
```java
@SpringBootApplication(exclude = {RedisRepositoriesAutoConfiguration.class})
@EnableDiscoveryClient
@EnableFeignClients(basePackages = {"com.issidp", "com.sungrow", "cn.iiot"})
@ComponentScan(basePackages = {"com.issidp", "com.sungrow", "cn.iiot"})
@MapperScan("com.sungrow.pm.{module}.mapper")
public class Application {
    public static void main(String[] args) {
        MythApplication.run(Application.class, args);
    }
}
```

**Feign Client（API 模块，跨服务调用）：**
```java
@FeignClient(name = "pm-{module}", fallbackFactory = {Business}ClientFallbackFactory.class)
public interface I{Business}Client {

    // DTO 用于跨服务数据传输（精简字段，只传输必要数据）

    @PostMapping("/api/pm-{module}/{business}/list")
    RestResponse<IPage<{Business}DTO>> pageList(@RequestBody {Business}DTO queryParam);

    @GetMapping("/api/pm-{module}/{business}/detail/{id}")
    RestResponse<{Business}DTO> getDetail(@PathVariable("id") String id);

    @PostMapping("/api/pm-{module}/{business}/create")
    RestResponse<Boolean> create(@RequestBody {Business}DTO dto);

    @PostMapping("/api/pm-{module}/{business}/update")
    RestResponse<Boolean> update(@RequestBody {Business}DTO dto);

    @PostMapping("/api/pm-{module}/{business}/delete/{id}")
    RestResponse<Boolean> delete(@PathVariable("id") String id);
}
```

### Step 8: 编译验证

执行以下流程直到编译通过：

```bash
# 1. 执行编译
mvn compile -q 2>&1 | head -50

# 2. 如有错误，自动修复
# - 解析错误信息，定位文件和行号
# - 修复 import 缺失
# - 修复包声明
# - 修复类型不匹配

# 3. 重复直到零错误
```

### Step 9: 输出报告

生成包含以下内容的报告：
- 生成文件清单
- TODO 任务统计
- 编译验证结果
- 下一步操作指南

---

## POM 配置模板

### 父 POM
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <artifactId>myth-starter-parent</artifactId>
        <groupId>cn.iiot.myth</groupId>
        <version>1.0.0.RELEASE</version>
    </parent>

    <groupId>cn.iiot.myth</groupId>
    <artifactId>pm-{module}</artifactId>
    <version>1.0.0.RELEASE</version>
    <packaging>pom</packaging>

    <modules>
        <module>pm-{module}-api</module>
        <module>pm-{module}-svc</module>
    </modules>
</project>
```

### API 模块 POM
```xml
<dependencies>
    <dependency>
        <groupId>cn.iiot.myth</groupId>
        <artifactId>myth-starter-common</artifactId>
        <optional>true</optional>
    </dependency>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-openfeign</artifactId>
    </dependency>
</dependencies>
```

### SVC 模块 POM
包含依赖：web、orm、feign、cache、excel、swagger、nacos、sentinel、liquibase 等。

---

## 质量检查清单

生成完成后，确认以下事项：

- [ ] `mvn compile` 零错误
- [ ] 所有 Controller 方法都有对应的 Service 接口方法
- [ ] 所有 Service 方法都有 TODO 注释说明待实现逻辑
- [ ] 无循环依赖（Controller 不直接引用 Mapper）
- [ ] 所有字段命名与 OpenAPI Spec 保持一致
- [ ] Feign Client 与 Controller 接口签名一致
- [ ] Mapper XML namespace 与接口全限定名一致

---

## 与 pm3-microservice-init 的关系

| 对比项 | pm3-microservice-init | pm3-skeleton-generator |
|--------|----------------------|------------------------|
| **触发时机** | 项目初始化 | 系分完成后 |
| **输入** | 模块名称 | 完整的系分产物 |
| **输出** | 空的微服务结构 | 带完整类定义的代码骨架 |
| **Controller** | 模板框架 | 根据 API Spec 生成完整方法 |
| **Service** | 模板框架 | 根据系分生成接口 + TODO 实现 |
| **Entity/VO** | 空类 | 根据领域模型生成完整字段 |

**对象分层对比：**

| 对象 | pm3-microservice-init | pm3-skeleton-generator |
|------|----------------------|------------------------|
| **Entity** | 空类框架 | 根据领域模型生成完整字段 |
| **VO** | 无 | 复杂场景前后端交互对象 |
| **DTO** | 无 | 跨服务调用传输对象（精简） |

**使用顺序：**
1. `pm3-microservice-init` → 创建空项目结构
2. 多轮人机协作 → 完善系分文档
3. `pm3-skeleton-generator` → 生成业务代码骨架
4. `pm3-execute` → 实现 TODO 中的业务逻辑

---

## 输出示例

```
═══════════════════════════════════════════════════════════════
              PM3 代码骨架生成报告
═══════════════════════════════════════════════════════════════

📦 项目信息
   模块中文名：国内工程管理
   模块英文名：pm-domestic-engineering
   项目路径：/Users/eason/IdeaProjects/pm3/pm-domestic-engineering/

📂 系分来源
   /Users/eason/Documents/Obsidian Vault/20_项目/PM3/01-1-system_analysis/国内工程管理/

📊 生成统计
   ├── Entity:           3 个（简单场景直接使用）
   ├── VO:               2 个（复杂场景前后端交互）
   ├── DTO:              3 个（跨服务传输，精简字段）
   ├── Controller:       2 个 (共 8 个接口)
   ├── Service:          2 个接口 + 2 个实现（继承 BaseServiceImpl）
   ├── Mapper:           3 个（继承 BaseMapper）
   ├── Feign Client:     2 个
   └── 待实现 TODO:     12 个（仅复杂业务方法）

✅ 质量检查
   [✓] mvn compile 零错误
   [✓] Controller-Service 映射完整
   [✓] 所有 Service 方法含 TODO
   [✓] 无循环依赖
   [✓] 字段命名一致

📝 TODO 任务清单
   ├── OrderService.createOrder:       5 个 TODO
   ├── OrderService.cancelOrder:       3 个 TODO
   ├── OrderService.queryList:         2 个 TODO
   └── ...

🚀 下一步操作
   1. 配置数据库连接 (bootstrap-local.yml)
   2. 执行 Liquibase 迁移脚本
   3. 使用 pm3-execute 逐条实现 TODO
   4. 使用 pm3-verify 验证实现

═══════════════════════════════════════════════════════════════
```

---

## 禁止事项

- ❌ 骨架中不允许出现真实业务代码
- ❌ 不允许修改已冻结的系分产物
- ❌ 不允许跳过编译验证
- ❌ 不允许遗漏 TODO 标记

---

## 对象分层说明

### Entity / VO / DTO 使用规范

| 对象 | 全称 | 用途 | 使用场景 | 所在模块 |
|------|------|------|----------|----------|
| **Entity** | 实体类 | 数据库映射 | Service 层操作、简单 CRUD 前后端交互 | pm-{module}-svc |
| **VO** | View Object | 前后端交互 | 复杂场景（含子对象、附件等） | pm-{module}-svc |
| **DTO** | Data Transfer Object | 跨服务传输 | Feign Client 调用（字段精简） | pm-{module}-api |

### 场景示例

**场景 1：简单列表查询**
```java
// Controller - 直接使用 Entity
@PostMapping("/list")
public RestResponse<IPage<Order>> pageList(@RequestBody Order queryParam) {
    return RestResponse.ok(service.page(new Page<>(), queryWrapper));
}
```

**场景 2：复杂详情查询（含子对象）**
```java
// VO 定义
@Data
public class OrderVO {
    private String id;
    private String orderNo;
    private List<OrderItem> items;      // 子对象集合
    private List<Attachment> attachments; // 附件集合
}

// Controller - 使用 VO
@GetMapping("/detail/{id}")
public RestResponse<OrderVO> getDetail(@PathVariable String id) {
    return RestResponse.ok(service.getDetailVO(id));
}
```

**场景 3：跨服务调用**
```java
// DTO 定义（精简字段）
@Data
public class OrderDTO {
    private String id;
    private String orderNo;
    private String status;
    // 不含子对象集合，减少网络传输
}

// Feign Client - 使用 DTO
@FeignClient(name = "pm-order")
public interface IOrderClient {
    @GetMapping("/api/pm-order/order/detail/{id}")
    RestResponse<OrderDTO> getDetail(@PathVariable("id") String id);
}
```

---

## 关联文档

- 代码骨架生成设计文档
- PM3微服务初始化工具 (pm3-microservice-init)
- 多轮人机协作迭代机制设计
