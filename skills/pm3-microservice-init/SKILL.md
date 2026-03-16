---
name: pm3-microservice-init
description: "交互式初始化 PM3 微服务模块骨架。自动创建项目目录结构、POM 配置、启动类、配置文件。不包含具体业务代码（Controller、Service、Mapper、Entity、DTO、Enums、Exception等），由开发者根据系分文档自行实现。使用方法：1) 用户提供模块名称，skill 自动推断业务领域和端口 2) 生成项目骨架 3) 提供下一步操作指南。"
---

# PM3 微服务初始化工具

## 使用方法

**用户只需提供：**
- 模块英文名称（kebab-case），如 `pm-order` 或 `order-management`

**Skill 会自动：**
- 推断业务领域名称（如 `order`）
- 分配可用端口（如 `8035`）
- 创建微服务基础结构（目录、POM、启动类、配置文件）
- **不生成业务代码**（Controller、Service、Mapper、Entity、DTO 等由开发者根据系分文档实现）

---

## 交互式调用

当用户说类似以下内容时触发：
- "帮我初始化一个订单模块"
- "创建一个新的微服务"
- "初始化 pm-payment 模块"
- "我想新建一个库存管理服务"

---

## Skill 执行流程

```
1. 解析模块名称
   └── 从中文名称提取英文名，或使用提供的英文名

2. 推断业务领域
   └── 根据模块名推断，如 pm-order → order

3. 分配服务端口
   └── 检查已有端口，避免冲突

4. 创建目录结构
   ├── pm-xxx-api/
   └── pm-xxx-svc/

5. 生成配置文件
   ├── pom.xml × 3 (父POM + api/svc子POM)
   ├── bootstrap.yml
   ├── bootstrap-local.yml
   └── logback-spring.xml

6. 生成启动类
   └── Application.java

7. 输出完成报告
   └── 文件列表 + 操作指南
```

---

## 代码生成模板

### 1. 父 POM
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
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

### 2. API POM
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

### 3. SVC POM
包含所有必需依赖：web、orm、feign、cache、excel、swagger、nacos、sentinel 等。

### 4. 启动类
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

---

## Bootstrap 配置模板

### bootstrap.yml（主配置）
```yaml
spring:
  profiles:
    active: ${active:local}
  application:
    name: {service-name}
```

### bootstrap-local.yml（本地开发）
```yaml
server:
  port: {port}
  servlet:
    context-path: /api/{service-name}

#management配置
management:
  server:
    port: {management-port}
  health:
    sentinel:
      enabled: false
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true

service:
  version: 3.0.0
  desc: {service-desc}

spring:
  cloud:
    nacos:
      username: nacos
      password: nacos
      config:
        enabled: true
        group: MYTH_PLATFORM
        file-extension: yaml
        namespace: {local-namespace}
        server-addr: 192.168.209.167:30848
        shared-configs[0]:
          dataId: myth-common.yaml
          group: MYTH_PLATFORM
          refresh: true
      discovery:
        enabled: true
        group: DEFAULT_GROUP
        server-addr: 192.168.209.167:30848
        namespace: {local-namespace}

    sentinel:
      enabled: false
      transport:
        dashboard: sentinel:8080
        port: {sentinel-port}
      datasource:
        ds1:
          nacos:
            server-addr: nacos:8848
            dataId: {service-name}-rule.json
            groupId: MYTH_PLATFORM
            ruleType: flow
            dataType: json
```

### bootstrap-dev.yml（开发环境）
```yaml
server:
  port: {port}
  servlet:
    context-path: /api/{service-name}

management:
  server:
    port: {management-port}
  health:
    sentinel:
      enabled: false

spring:
  cloud:
    nacos:
      server-addr: ${NACOS_SERVER}
      username: ${NACOS_USERNAME:nacos}
      password: ${NACOS_PASSWORD:nacos}
      config:
        enabled: true
        group: MYTH_PLATFORM
        file-extension: yaml
        shared-configs[0]:
          dataId: myth-common.yaml
          group: MYTH_PLATFORM
          refresh: true
      discovery:
        enabled: true
        group: DEFAULT_GROUP
    sentinel:
      enabled: false
      transport:
        dashboard: sentinel:8080
        port: {sentinel-port}
      datasource:
        ds1:
          nacos:
            server-addr: nacos:8848
            dataId: {service-name}-rule.json
            groupId: MYTH_PLATFORM
            ruleType: flow
            dataType: json
```

### bootstrap-sit.yml（SIT测试环境）
```yaml
server:
  port: {port}
  servlet:
    context-path: /api/{service-name}

management:
  server:
    port: {management-port}
  health:
    sentinel:
      enabled: false
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true

service:
  version: 3.0.0
  desc: {service-desc}

spring:
  cloud:
    nacos:
      username: nacos
      password: Sungrow@123
      config:
        enabled: true
        group: MYTH_PLATFORM
        file-extension: yaml
        server-addr: 192.168.209.167:30848
        namespace: d326857e-dae8-455e-9b3a-c03c15e4b973
        shared-configs[0]:
          dataId: myth-common.yaml
          group: MYTH_PLATFORM
          refresh: true
      discovery:
        enabled: true
        group: DEFAULT_GROUP
        server-addr: 192.168.209.167:30848
        namespace: d326857e-dae8-455e-9b3a-c03c15e4b973
    sentinel:
      enabled: false
      transport:
        dashboard: sentinel.myth-platform:8080
        port: {sentinel-port}
      datasource:
        ds1:
          nacos:
            server-addr: 192.168.209.167:30848
            dataId: {service-name}-rule.json
            groupId: MYTH_PLATFORM
            ruleType: flow
            dataType: json
```

### bootstrap-uat.yml（UAT测试环境）
```yaml
server:
  port: {port}
  servlet:
    context-path: /api/{service-name}

management:
  server:
    port: {management-port}
  health:
    sentinel:
      enabled: false
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true

service:
  version: 3.0.0
  desc: {service-desc}

spring:
  cloud:
    nacos:
      username: nacos
      password: Sungrow@123
      config:
        enabled: true
        group: MYTH_PLATFORM
        file-extension: yaml
        server-addr: 192.168.209.169:30848
        namespace: a99669a6-7adc-4b19-91fb-8cb8da14aff7
        shared-configs[0]:
          dataId: myth-common.yaml
          group: MYTH_PLATFORM
          refresh: true
      discovery:
        enabled: true
        group: DEFAULT_GROUP
        server-addr: 192.168.209.169:30848
        namespace: a99669a6-7adc-4b19-91fb-8cb8da14aff7
    sentinel:
      enabled: false
      transport:
        dashboard: sentinel:8080
        port: {sentinel-port}
      datasource:
        ds1:
          nacos:
            server-addr: 192.168.209.169:30848
            dataId: {service-name}-rule.json
            groupId: MYTH_PLATFORM
            ruleType: flow
            dataType: json
```

### bootstrap-prod.yml（生产环境）
```yaml
server:
  port: {port}
  servlet:
    context-path: /api/{service-name}

#management配置
management:
  server:
    port: {management-port}
  health:
    sentinel:
      enabled: false
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true

service:
  version: 3.0.0
  desc: {service-desc}

spring:
  cloud:
    nacos:
      username: nacos
      password: Sungrow@123
      config:
        enabled: true
        group: PM_PROD
        file-extension: yaml
        server-addr: nacos.prod.svc.cluster.local:8848
        namespace: a5908311-ac62-4573-85ab-d507f32b82a0
        shared-configs[0]:
          dataId: myth-common.yaml
          group: PM_PROD
          refresh: true
      discovery:
        enabled: true
        group: PM_PROD
        server-addr: nacos.prod.svc.cluster.local:8848
        namespace: a5908311-ac62-4573-85ab-d507f32b82a0
    sentinel:
      enabled: false
      transport:
        dashboard: sentinel:8080
        port: {sentinel-port}
      datasource:
        ds1:
          nacos:
            server-addr: nacos.prod.svc.cluster.local:8848
            dataId: {service-name}-rule.json
            groupId: PM_PROD
            ruleType: flow
            dataType: json
```

### 配置参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `{service-name}` | 服务名称（spring.application.name）| pm-order, myth-auth |
| `{port}` | 服务端口 | 8030, 8035 |
| `{management-port}` | Actuator 管理端口 | port + 1 (如 8031) |
| `{sentinel-port}` | Sentinel 传输端口 | port + 2 (如 8032) |
| `{service-desc}` | 服务描述 | 订单管理, 认证中心 |
| `{local-namespace}` | 本地开发命名空间 | 408669ea-3e1b-405f-8654-6f6ecb939075 |

### 环境配置对照表

| 环境 | Nacos 地址 | Namespace | Group | 用户名/密码 |
|------|-----------|-----------|-------|------------|
| local | 192.168.209.167:30848 | 408669ea-3e1b-405f-8654-6f6ecb939075 | MYTH_PLATFORM | nacos/nacos |
| dev | ${NACOS_SERVER} | - | MYTH_PLATFORM | 环境变量 |
| sit | 192.168.209.167:30848 | d326857e-dae8-455e-9b3a-c03c15e4b973 | MYTH_PLATFORM | nacos/Sungrow@123 |
| uat | 192.168.209.169:30848 | a99669a6-7adc-4b19-91fb-8cb8da14aff7 | MYTH_PLATFORM | nacos/Sungrow@123 |
| prod | nacos.prod.svc.cluster.local:8848 | a5908311-ac62-4573-85ab-d507f32b82a0 | PM_PROD | nacos/Sungrow@123 |

---

## 生成的文件结构

```
pm-{module}/
├── pom.xml                                    # 父POM
├── pm-{module}-api/
│   ├── pom.xml                                # API模块POM
│   └── src/main/java/com/sungrow/pm/{module}/
│       ├── client/                            # (空目录，由开发者添加Feign Client)
│       └── param/
│           └── dto/                           # (空目录，由开发者添加DTO)
├── pm-{module}-svc/
│   ├── pom.xml                                # SVC模块POM
│   └── src/main/
│       ├── java/com/sungrow/pm/{module}/
│       │   ├── Application.java               # 启动类
│       │   ├── config/                        # (空目录，由开发者添加配置类)
│       │   ├── controller/                    # (空目录，由开发者添加Controller)
│       │   ├── dto/                           # (空目录，由开发者添加DTO)
│       │   ├── entity/                        # (空目录，由开发者添加Entity)
│       │   ├── enums/                         # (空目录，由开发者添加枚举)
│       │   ├── exception/                     # (空目录，由开发者添加异常类)
│       │   ├── mapper/                        # (空目录，由开发者添加Mapper)
│       │   ├── service/                       # (空目录，由开发者添加Service)
│       │   └── utils/                         # (空目录，由开发者添加工具类)
│       └── resources/
│           ├── bootstrap.yml                  # 主配置
│           ├── bootstrap-local.yml            # 本地开发配置
│           ├── logback-spring.xml             # 日志配置
│           ├── mapper/                        # (空目录，由开发者添加Mapper XML)
│           └── liquibase/
│               └── index.xml                  # 数据库迁移脚本(空模板)
```

**说明：** 所有业务相关的目录（controller、service、mapper、entity、dto、enums、exception、utils）均为空目录，由开发者根据系分文档自行实现。

---

## 端口分配策略

| 模块类型 | 端口范围 | 示例 |
|---------|---------|------|
| 基础业务模块 | 8030-8099 | 8035 |
| 审批模块 | 8040-8049 | 8045 |
| 集成模块 | 8050-8059 | 8055 |
| 定时任务模块 | 8060-8069 | 8065 |

---

## 后续操作指南

Skill 执行完成后，告知用户：

### 1. 配置 Nacos 连接
检查 `bootstrap-local.yml` 中的 Nacos 配置是否正确。

### 2. 业务代码开发
根据系分文档，在对应目录下创建业务代码：
```java
// 1. 在 entity/ 目录下创建实体类
// 2. 在 dto/ 目录下创建参数和返回DTO
// 3. 在 mapper/ 目录下创建数据访问层
// 4. 在 service/ 目录下创建业务逻辑层
// 5. 在 controller/ 目录下创建接口层
// 6. 在 enums/ 目录下创建枚举类
// 7. 在 exception/ 目录下创建异常类
```

### 3. 数据库准备
```bash
# 1. 在 liquibase/index.xml 中添加数据库变更集
# 2. 或手动创建数据库表
```

### 4. 启动测试
```bash
# 编译启动服务
mvn clean install
cd pm-xxx-svc
mvn spring-boot:run

# 访问 Swagger 文档
# http://localhost:{port}/api/pm-xxx/swagger-ui.html
```

---

## 交互示例

**用户输入：**
> "帮我初始化一个订单模块"

**Skill 执行：**
1. 解析模块名：`pm-order`
2. 推断业务领域：`order`
3. 分配端口：`8035`（检查后发现未使用）
4. 创建目录结构
5. 生成 POM 文件和配置文件
6. 生成启动类
7. 创建空业务目录
8. 输出完成报告

**输出：**
```
✅ 已完成！PM3 订单模块骨架已初始化

📁 生成目录：/Users/eason/IdeaProjects/pm3/pm-order
📦 模块名：pm-order
🏷  业务领域：order
🔌 服务端口：8035

生成文件列表：
├── pom.xml                                    # 父POM
├── pm-order-api/
│   ├── pom.xml                                # API模块POM
│   └── src/main/java/com/sungrow/pm/order/
│       ├── client/                            # (空)
│       └── param/dto/                         # (空)
├── pm-order-svc/
│   ├── pom.xml                                # SVC模块POM
│   └── src/main/
│       ├── java/com/sungrow/pm/order/
│       │   ├── Application.java               # 启动类
│       │   ├── config/                        # (空)
│       │   ├── controller/                    # (空)
│       │   ├── dto/                           # (空)
│       │   ├── entity/                        # (空)
│       │   ├── enums/                         # (空)
│       │   ├── exception/                     # (空)
│       │   ├── mapper/                        # (空)
│       │   ├── service/                       # (空)
│       │   └── utils/                         # (空)
│       └── resources/
│           ├── bootstrap.yml
│           ├── bootstrap-local.yml
│           ├── logback-spring.xml
│           ├── mapper/                         # (空)
│           └── liquibase/index.xml

下一步操作：
1. 根据系分文档，在 controller/service/mapper/entity/dto 目录下创建业务代码
2. 配置 Nacos 连接（检查 bootstrap-local.yml）
3. 在 liquibase/index.xml 中添加数据库表结构
4. 启动服务测试
```

---

## 注意事项

1. **本 Skill 只生成项目骨架**，不包含任何业务代码实现
2. 所有业务代码（Controller、Service、Mapper、Entity、DTO、Enums、Exception 等）需由开发者根据系分文档自行实现
3. 项目结构遵循 PM3 规范，可直接用于后续系分驱动的代码生成

---
