# AWS RDS Spring Boot 集成

## 概述

将 AWS RDS 数据库（Aurora、MySQL、PostgreSQL）与 Spring Boot 应用程序进行配置。提供数据源配置、HikariCP 连接池、SSL 连接、特定环境的配置以及 AWS Secrets Manager 集成的模式。

## 何时使用

在为 RDS 工作负载配置 HikariCP 连接池、使用 Aurora 从属实现读写分离、设置 IAM 数据库身份验证、启用 SSL/TLS 连接、使用 Flyway 管理数据库迁移或排除 RDS 连接问题时使用。

## 说明

按照以下步骤配置 AWS RDS 与 Spring Boot：

1. **添加依赖项** — 包含 Spring Data JPA、数据库驱动程序（MySQL/PostgreSQL）和 Flyway
2. **配置数据源** — 在 application.yml 中设置连接属性
3. **配置 HikariCP** — 为您的 RDS 工作负载优化池设置
4. **设置 SSL** — 启用到 RDS 的加密连接
5. **配置配置文件** — 设置特定环境的配置（dev/prod）
6. **添加迁移** — 创建用于模式管理的 Flyway 脚本
7. **验证连接性** — 运行健康检查以验证数据库连接

   **如果验证失败**：检查安全组规则，验证凭证，确保您的网络可以访问 RDS，并确认 SSL 证书配置。

8. **运行迁移** — 仅在连接性验证通过后应用 Flyway 迁移

## 快速入门

### 第 1 步：添加依赖项

**Maven (pom.xml):**
```xml
<dependencies>
    <!-- Spring Data JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- Aurora MySQL 驱动程序 -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <version>8.2.0</version>
        <scope>runtime</scope>
    </dependency>

    <!-- Aurora PostgreSQL 驱动程序（替代方案） -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- 用于数据库迁移的 Flyway -->
    <dependency>
        <groupId>org.flywaydb</groupId>
        <artifactId>flyway-core</artifactId>
    </dependency>

    <!-- 验证 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
</dependencies>
```

**Gradle (build.gradle):**
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-validation'

    // Aurora MySQL
    runtimeOnly 'com.mysql:mysql-connector-j:8.2.0'

    // Aurora PostgreSQL（替代方案）
    runtimeOnly 'org.postgresql:postgresql'

    // Flyway
    implementation 'org.flywaydb:flyway-core'
}
```

### 第 2 步：基本数据源配置

使用下方 **示例** 部分的配置。对于 PostgreSQL，更改：
- 驱动程序：`org.postgresql.Driver`
- URL：`jdbc:postgresql://...` 并使用 `?ssl=true&sslmode=require`
- Dialect：`org.hibernate.dialect.PostgreSQLDialect`

### 第 3 步：设置环境变量

```bash
# 生产环境变量
export DB_PASSWORD=YourStrongPassword123!
export SPRING_PROFILES_ACTIVE=prod

# 开发环境
export SPRING_PROFILES_ACTIVE=dev
```

## 数据库迁移设置

为 Flyway 创建迁移文件：

```
src/main/resources/db/migration/
├── V1__create_users_table.sql
├── V2__add_phone_column.sql
└── V3__create_orders_table.sql
```

**V1__create_users_table.sql:**
```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 示例

### 示例 1：Aurora MySQL 配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://myapp-aurora-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:3306/devops
    username: admin
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 20000
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
```

### 示例 2：带有 SSL 的 Aurora PostgreSQL

```properties
spring.datasource.url=jdbc:postgresql://myapp-aurora-pg-cluster.cluster-abc123xyz.us-east-1.rds.amazonaws.com:5432/devops?ssl=true&sslmode=require
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}
spring.datasource.hikari.maximum-pool-size=30
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
```

### 示例 3：读写分离配置

```java
@Configuration
public class DataSourceConfiguration {

    @Bean
    @Primary
    public DataSource dataSource(
            @Qualifier("writerDataSource") DataSource writerDataSource,
            @Qualifier("readerDataSource") DataSource readerDataSource) {
        Map<Object, Object> targetDataSources = new HashMap<>();
        targetDataSources.put("writer", writerDataSource);
        targetDataSources.put("reader", readerDataSource);

        RoutingDataSource routingDataSource = new RoutingDataSource();
        routingDataSource.setTargetDataSources(targetDataSources);
        routingDataSource.setDefaultTargetDataSource(writerDataSource);

        return routingDataSource;
    }
}
```

## 限制和警告

- HikariCP 池大小必须尊重 RDS 实例连接限制
- 安全组必须允许从您的应用程序的 IP 范围传输流量
- 使用 AWS Secrets Manager 而不是硬编码凭证
- 启用存储自动扩展以防止存储耗尽

## 最佳实践

- **HikariCP**：启用泄漏检测并为故障转移场景配置超时
- **安全**：启用 SSL/TLS；尽可能使用 IAM 数据库身份验证
- **性能**：禁用 open-in-view；使用适当的索引和批量操作
- **监控**：启用 Spring Boot Actuator 并添加数据库健康检查

## 测试

使用此健康检查端点验证连接性：

```java
@RestController
@RequestMapping("/api/health")
public class DatabaseHealthController {
    @Autowired
    private DataSource dataSource;

    @GetMapping("/db-connection")
    public ResponseEntity<Map<String, Object>> testDatabaseConnection() {
        Map<String, Object> response = new HashMap<>();
        try (Connection connection = dataSource.getConnection()) {
            response.put("status", "success");
            response.put("database", connection.getCatalog());
            response.put("connected", true);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("status", "failed");
            response.put("error", e.getMessage());
            response.put("connected", false);
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(response);
        }
    }
}
```

```bash
curl http://localhost:8080/api/health/db-connection
```

## 支持

有关详细的故障排除和高级配置，请参阅：

- [AWS RDS Aurora 高级配置](references/advanced-configuration.md)
- [AWS RDS Aurora 故障排除指南](references/troubleshooting.md)
- [AWS RDS Aurora 文档](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/java_aurora_code_examples.html)
- [Spring Boot Data RDS Aurora 文档](https://www.baeldung.com/aws-aurora-rds-java)
