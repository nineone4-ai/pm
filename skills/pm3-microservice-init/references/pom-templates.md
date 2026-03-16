# POM 配置模板

## 1. 父 POM 模板

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    
    <parent>
        <artifactId>myth-starter-parent</artifactId>
        <groupId>cn.iiot.myth</groupId>
        <version>1.0.0.RELEASE</version>
    </parent>
    
    <modelVersion>4.0.0</modelVersion>
    <packaging>pom</packaging>
    
    <groupId>cn.iiot.myth</groupId>
    <artifactId>pm-{module}</artifactId>
    <version>1.0.0.RELEASE</version>
    
    <name>PM3 {业务名}模块</name>
    <description>PM3项目管理系统 - {业务名}业务模块</description>
    
    <properties>
        <myth.starter.version>1.0.0.RELEASE</myth.starter.version>
        <log4j2.version>2.15.0</log4j2.version>
        <fastjson.version>2.0.57</fastjson.version>
    </properties>
    
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>cn.iiot.myth</groupId>
                <artifactId>myth-starter-web</artifactId>
                <version>${myth.starter.version}</version>
            </dependency>
            <dependency>
                <groupId>cn.iiot.myth</groupId>
                <artifactId>myth-starter-orm</artifactId>
                <version>1.0.0.RELEASE</version>
            </dependency>
            <dependency>
                <groupId>cn.iiot.myth</groupId>
                <artifactId>myth-starter-feign</artifactId>
                <version>${myth.starter.version}</version>
            </dependency>
            <dependency>
                <groupId>cn.iiot.myth</groupId>
                <artifactId>myth-starter-cache</artifactId>
                <version>${myth.starter.version}</version>
            </dependency>
            <dependency>
                <groupId>cn.iiot.myth</groupId>
                <artifactId>myth-starter-excel</artifactId>
                <version>${myth.starter.version}</version>
            </dependency>
            <dependency>
                <groupId>cn.iiot.myth</groupId>
                <artifactId>myth-starter-swagger</artifactId>
                <version>${myth.starter.version}</version>
            </dependency>
            <dependency>
                <groupId>cn.iiot.myth</groupId>
                <artifactId>myth-starter-trace</artifactId>
                <version>${myth.starter.version}</version>
            </dependency>
            <dependency>
                <groupId>com.xuxueli</groupId>
                <artifactId>xxl-job-core</artifactId>
                <version>${xxl-job.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
    
    <modules>
        <module>pm-{module}-api</module>
        <module>pm-{module}-svc</module>
    </modules>
    
    <distributionManagement>
        <repository>
            <id>sungrow-mirror</id>
            <name>Sungrow Repository</name>
            <url>http://192.168.209.168:8081/nexus/content/repositories/maven-releases/</url>
        </repository>
        <snapshotRepository>
            <id>sungrow-mirror</id>
            <name>Sungrow Snapshot Repository</name>
            <url>http://192.168.209.168:8081/nexus/content/repositories/maven-snapshots/</url>
        </snapshotRepository>
    </distributionManagement>
</project>
```

## 2. API 模块 POM

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <artifactId>pm-{module}</artifactId>
        <groupId>cn.iiot.myth</groupId>
        <version>1.0.0.RELEASE</version>
    </parent>
    
    <modelVersion>4.0.0</modelVersion>
    <artifactId>pm-{module}-api</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    
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
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <encoding>UTF-8</encoding>
                    <parameters>true</parameters>
                    <source>1.8</source>
                    <target>1.8</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

## 3. SVC 模块 POM

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <artifactId>pm-{module}</artifactId>
        <groupId>cn.iiot.myth</groupId>
        <version>1.0.0.RELEASE</version>
    </parent>
    
    <modelVersion>4.0.0</modelVersion>
    <artifactId>pm-{module}-svc</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <maven.deploy.skip>true</maven.deploy.skip>
    </properties>
    
    <dependencies>
        <!-- Web核心 -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>myth-starter-web</artifactId>
            <version>1.0.5.RELEASE</version>
            <exclusions>
                <exclusion>
                    <groupId>com.github.ben-manes.caffeine</groupId>
                    <artifactId>caffeine</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
        
        <!-- ORM -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>myth-starter-orm</artifactId>
        </dependency>
        <dependency>
            <groupId>com.github.yulichang</groupId>
            <artifactId>mybatis-plus-join-boot-starter</artifactId>
            <version>1.5.4</version>
        </dependency>
        
        <!-- Feign -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>myth-starter-feign</artifactId>
        </dependency>
        
        <!-- Cache -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>myth-starter-cache</artifactId>
        </dependency>
        
        <!-- Excel -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>myth-starter-excel</artifactId>
        </dependency>
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>easyexcel</artifactId>
            <version>3.3.2</version>
        </dependency>
        
        <!-- Trace -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>myth-starter-trace</artifactId>
        </dependency>
        
        <!-- Swagger -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>myth-starter-swagger</artifactId>
        </dependency>
        
        <!-- Nacos -->
        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
        </dependency>
        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
        </dependency>
        
        <!-- Sentinel -->
        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
        </dependency>
        <dependency>
            <groupId>com.alibaba.csp</groupId>
            <artifactId>sentinel-datasource-nacos</artifactId>
        </dependency>
        
        <!-- Caffeine -->
        <dependency>
            <groupId>com.github.ben-manes.caffeine</groupId>
            <artifactId>caffeine</artifactId>
        </dependency>
        
        <!-- Liquibase -->
        <dependency>
            <groupId>org.liquibase</groupId>
            <artifactId>liquibase-core</artifactId>
        </dependency>
        
        <!-- Logging -->
        <dependency>
            <groupId>com.github.danielwegener</groupId>
            <artifactId>logback-kafka-appender</artifactId>
            <version>0.2.0-RC2</version>
        </dependency>
        <dependency>
            <groupId>com.plumelog</groupId>
            <artifactId>plumelog-logback</artifactId>
            <version>3.5.3</version>
        </dependency>
        
        <!-- XXL-Job -->
        <dependency>
            <groupId>com.xuxueli</groupId>
            <artifactId>xxl-job-core</artifactId>
            <version>2.4.0</version>
        </dependency>
        
        <!-- 内部服务依赖 -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>myth-platform-api</artifactId>
            <version>1.0.1-SNAPSHOT</version>
        </dependency>
        <dependency>
            <groupId>cn.iiot.myth.usercenter</groupId>
            <artifactId>myth-auth-api</artifactId>
            <version>1.0.2</version>
        </dependency>
        
        <!-- 本模块 API -->
        <dependency>
            <groupId>cn.iiot.myth</groupId>
            <artifactId>pm-{module}-api</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>
    </dependencies>
    
    <build>
        <finalName>pm-{module}</finalName>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>com.coderplus.maven.plugins</groupId>
                <artifactId>copy-rename-maven-plugin</artifactId>
                <version>1.0</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals><goal>copy</goal></goals>
                        <configuration>
                            <sourceFile>${project.build.directory}/pm-{module}.jar</sourceFile>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```
