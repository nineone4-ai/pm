# 配置文件模板

## 1. bootstrap.yml

```yaml
spring:
  profiles:
    active: ${active:prod}
  application:
    name: pm-{module}
```

## 2. bootstrap-local.yml（本地环境）

```yaml
server:
  port: {port}

# management配置
management:
  server:
    port: {admin_port}
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
  desc: {业务名}模块

spring:
  cloud:
    nacos:
      username: nacos
      password: nacos
      config:
        namespace: {nacos_namespace}
        server-addr: 192.168.209.166:8848
        enabled: true
        group: MYTH_PLATFORM
        file-extension: yaml
        shared-configs[0]:
          dataId: pm-{module}.yaml
          group: MYTH_PLATFORM
          refresh: true
      discovery:
        server-addr: 192.168.209.166:8848
        namespace: {nacos_namespace}
        enabled: true
        group: DEFAULT_GROUP

    sentinel:
      enabled: false
      transport:
        dashboard: sentinel:8080
        port: {sentinel_port}
      datasource:
        ds1:
          nacos:
            server-addr: nacos:8848
            dataId: myth-platform-rule.json
            groupId: MYTH_PLATFORM
            ruleType: flow
            dataType: json
```

## 3. logback-spring.xml（日志配置）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration scan="true" scanPeriod="10 seconds">
    <contextName>pm-{module}</contextName>
    
    <!-- 日志格式 -->
    <property name="LOG_PATTERN" value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n"/>
    <property name="LOG_PATTERN_CONSOLE" value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n"/>
    
    <!-- 控制台输出 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${LOG_PATTERN_CONSOLE}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>
    
    <!-- 文件输出 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/pm-{module}.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/pm-{module}.%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
            <maxFileSize>100MB</maxFileSize>
            <maxHistory>30</maxHistory>
            <totalSizeCap>3GB</totalSizeCap>
        </rollingPolicy>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>
    
    <!-- Kafka 输出 -->
    <appender name="KAFKA" class="com.github.danielwegener.logback.kafka.KafkaAppender">
        <topic>pm-{module}-log</topic>
        <producerConfig>bootstrap.servers=192.168.209.166:9092</producerConfig>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>
    
    <!-- Root 日志级别 -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
        <appender-ref ref="KAFKA"/>
    </root>
    
    <!-- SQL 日志级别 -->
    <logger name="com.sungrow.pm.{module}" level="DEBUG"/>
    <logger name="com.baomidou.mybatisplus" level="DEBUG"/>
</configuration>
```

## 4. Liquibase 迁移脚本（liquibase/index.xml）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
    http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.5.xsd">
    
    <!-- 创建 {业务名} 表 -->
    <changeSet id="create-{table_name}-table" author="{author}">
        <comment>创建 {业务名} 表</comment>
        
        <createTable tableName="{table_name}">
            <column name="id" type="VARCHAR(32)">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="name" type="VARCHAR(100)">
                <constraints nullable="false"/>
            </column>
            <column name="code" type="VARCHAR(50)"/>
            <column name="status" type="INT" defaultValueNumeric="1">
                <constraints nullable="false"/>
            </column>
            <column name="description" type="VARCHAR(500)"/>
            <column name="amount" type="DECIMAL(18,2)"/>
            <column name="sort" type="INT" defaultValueNumeric="0"/>
            <column name="remark" type="VARCHAR(500)"/>
            <column name="create_by" type="VARCHAR(32)"/>
            <column name="create_time" type="DATETIME"/>
            <column name="update_by" type="VARCHAR(32)"/>
            <column name="update_time" type="DATETIME"/>
            <column name="delete_flag" type="CHAR(1)" defaultValue="0">
                <constraints nullable="false"/>
            </column>
        </createTable>
        
        <!-- 添加索引 -->
        <createIndex indexName="idx_{table_name}_code" tableName="{table_name}">
            <column name="code"/>
        </createIndex>
        
        <createIndex indexName="idx_{table_name}_status" tableName="{table_name}">
            <column name="status"/>
        </createIndex>
        
        <createIndex indexName="idx_{table_name}_delete_flag" tableName="{table_name}">
            <column name="delete_flag"/>
        </createIndex>
        
        <!-- 添加注释 -->
        <addComments tableName="{table_name}" comments="{业务名}表"/>
    </changeSet>
    
</databaseChangeLog>
```

## 端口分配规则

| 服务类型 | 端口范围 | 管理端口 |
|---------|---------|---------|
| 业务模块 | 8030-8099 | +100 |
| 审批模块 | 8040-8049 | +100 |
| 集成模块 | 8050-8059 | +100 |
| 定时任务模块 | 8060-8069 | +100 |

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `active` | 激活的 profile | prod |
| `nacos_namespace` | Nacos 命名空间 | - |
