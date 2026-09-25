# Spring Boot 项目创建器

## 概述

使用 Spring Initializr API 从零生成完全配置的 Spring Boot 项目。该技能引导用户选择项目参数，选择架构风格（DDD 或分层），配置数据存储，并设置 Docker Compose 以进行本地开发。结果是具有标准化结构、依赖管理和配置的构建就绪项目。

## 使用场景

- 使用标准结构快速启动新的 Spring Boot 3.x 或 4.x 项目。
- 使用 JPA、SpringDoc OpenAPI 和 Docker Compose 初始化后端微服务。
- 搭建遵循 DDD（领域驱动设计）或分层（Controller/Service/Repository/Model）架构的项目。
- 通过 Docker Compose 设置包含 PostgreSQL、Redis 和/或 MongoDB 的本地开发基础设施。
- 触发短语：**"create spring boot project"**、**"new spring boot app"**、**"bootstrap java project"**、**"scaffold spring boot microservice"**、**"initialize spring boot backend"**、**"generate spring boot project"**。

## 前置条件

开始之前，请确保已安装以下工具：

- **Java 开发工具包 (JDK)**：版本 17+（推荐使用 Java 21 用于 Spring Boot 3.x/4.x）
- **Apache Maven**：构建工具（Spring Initializr 默认生成 Maven 项目）
- **Docker** 和 **Docker Compose**：用于运行本地基础设施服务
- **curl** 和 **unzip**：用于从 Spring Initializr 下载和提取项目

## 操作步骤

按照以下步骤创建新的 Spring Boot 项目。

### 1. 收集项目配置

使用 **AskUserQuestion** 向用户询问以下项目参数。提供合理的默认值：

| 参数 | 默认值 | 选项 |
|------|--------|------|
| **Group ID** | `com.example` | 任何有效的 Java 包名 |
| **Artifact ID** | `demo` | 肋骨命名标识符 |
| **Package Name** | 与 Group ID 相同 | 有效的 Java 包 |
| **Spring Boot 版本** | `3.4.5` | `3.4.x`, `4.0.x`（检查 start.spring.io 获取最新版本） |
| **Java 版本** | `21` | `17`, `21` |
| **架构** | 用户选择 | `DDD` 或 `Layered` |
| **Docker 服务** | 用户选择 | PostgreSQL, Redis, MongoDB（多选） |
| **构建工具** | `maven` | `maven`, `gradle` |

### 2. 使用 Spring Initializr 生成项目

使用 `curl` 从 start.spring.io 下载项目骨架。

**基础依赖**（始终包含）：
- `web` — Spring Web MVC
- `validation` — Jakarta Bean Validation
- `data-jpa` — Spring Data JPA
- `testcontainers` — Testcontainers 支持

**条件依赖**（基于 Docker 服务选择）：
- 选择 PostgreSQL → 添加 `postgresql`
- 选择 Redis → 添加 `data-redis`
- 选择 MongoDB → 添加 `data-mongodb`

```bash
# 示例：Spring Boot 3.4.5 仅使用 PostgreSQL
curl -s https://start.spring.io/starter.zip \
  -d type=maven-project \
  -d language=java \
  -d bootVersion=3.4.5 \
  -d groupId=com.example \
  -d artifactId=demo \
  -d packageName=com.example \
  -d javaVersion=21 \
  -d packaging=jar \
  -d dependencies=web,data-jpa,postgresql,validation,testcontainers \
  -o starter.zip

unzip -o starter.zip -d ./demo
rm starter.zip
cd demo
```

### 3. 添加额外依赖

编辑 `pom.xml` 以添加 SpringDoc OpenAPI 和 ArchUnit 用于架构测试。

```xml
<!-- SpringDoc OpenAPI -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.15</version>
</dependency>

<!-- ArchUnit for architecture tests -->
<dependency>
    <groupId>com.tngtech.archunit</groupId>
    <artifactId>archunit-junit5</artifactId>
    <version>1.4.1</version>
    <scope>test</scope>
</dependency>
```

### 4. 创建架构结构

根据用户的选择，在 `src/main/java/<packagePath>/` 下创建包结构。

#### 选项 A：分层架构

```
src/main/java/com/example/
├── controller/        # REST 控制器 (@RestController)
├── service/           # 业务逻辑 (@Service)
├── repository/        # 数据访问 (@Repository, Spring Data 接口)
├── model/             # JPA 实体 (@Entity)
│   └── dto/           # 请求/响应 DTO（Java 记录）
├── config/            # 配置类 (@Configuration)
└── exception/         # 自定义异常和 @ControllerAdvice
```

为每一层创建占位符类：

- **config/OpenApiConfig.java** — SpringDoc OpenAPI 配置 Bean
- **exception/GlobalExceptionHandler.java** — `@RestControllerAdvice` 带标准错误处理
- **model/dto/ErrorResponse.java** — 标准错误响应记录

#### 选项 B：DDD（领域驱动设计）架构

```
src/main/java/com/example/
├── domain/                 # 核心领域（无框架）
│   ├── model/              # 实体、值对象、聚合
│   ├── repository/         # 仓库接口（端口）
│   └── exception/          # 领域异常
├── application/            # 用例 / 应用服务
│   ├── service/            # @Service 组合
│   └── dto/                # 输入/输出 DTO（记录）
├── infrastructure/         # 外部适配器
│   ├── persistence/        # JPA 实体、Spring Data 仓库
│   └── config/             # Spring @Configuration
└── presentation/           # REST API 层
    ├── controller/         # @RestController
    └── exception/          # @RestControllerAdvice
```

为每一层创建占位符类：

- **infrastructure/config/OpenApiConfig.java** — SpringDoc OpenAPI 配置 Bean
- **presentation/exception/GlobalExceptionHandler.java** — `@RestControllerAdvice` 带标准错误处理
- **application/dto/ErrorResponse.java** — 标准错误响应记录

### 5. 配置应用程序属性

创建 `src/main/resources/application.properties` 并使用所选服务。

**始终包含：**

```properties
# 应用程序
spring.application.name=${artifactId}

# SpringDoc OpenAPI
springdoc.swagger-ui.doc-expansion=none
springdoc.swagger-ui.operations-sorter=alpha
springdoc.swagger-ui.tags-sorter=alpha
```

**如果选择 PostgreSQL：**

```properties
# PostgreSQL / JPA
spring.datasource.driver-class-name=org.postgresql.Driver
spring.datasource.url=jdbc:postgresql://localhost:5432/${POSTGRES_DB:postgres}
spring.datasource.username=${POSTGRES_USER:postgres}
spring.datasource.password=${POSTGRES_PASSWORD:changeme}
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

**如果选择 Redis：**

```properties
# Redis
spring.data.redis.host=localhost
spring.data.redis.port=6379
spring.data.redis.password=${REDIS_PASSWORD:changeme}
```

**如果选择 MongoDB：**

```properties
# MongoDB
spring.data.mongodb.host=localhost
spring.data.mongodb.port=27017
spring.data.mongodb.authentication-database=admin
spring.data.mongodb.username=${MONGO_USER:root}
spring.data.mongodb.password=${MONGO_PASSWORD:changeme}
spring.data.mongodb.database=${MONGO_DB:test}
```

### 6. 设置 Docker Compose

在项目根目录创建 `docker-compose.yaml`，仅包含用户选择的服务。

```yaml
services:
  # 如果选择 PostgreSQL 则包含
  postgresql:
    image: postgres:17
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_DB: ${POSTGRES_DB:-postgres}
    volumes:
      - ./postgres_data:/var/lib/postgresql/data

  # 如果选择 Redis 则包含
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD:-changeme}
    volumes:
      - ./redis_data:/data

  # 如果选择 MongoDB 则包含
  mongodb:
    image: mongo:8
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER:-root}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-changeme}
    volumes:
      - ./mongo_data:/data/db
```

### 7. 创建 Docker Compose 的 .env 文件

在项目根目录创建 `.env` 文件，包含本地开发默认凭证：

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=postgres

# Redis
REDIS_PASSWORD=changeme

# MongoDB
MONGO_USER=root
MONGO_PASSWORD=changeme
MONGO_DB=test
```

仅包含用户选择的服务变量。Docker Compose 自动加载此文件。

### 8. 更新 .gitignore

将 Docker Compose 卷目录和 `.env` 文件追加到 `.gitignore`：

```
# Docker Compose
.env
postgres_data/
redis_data/
mongo_data/
```

### 9. 验证构建

运行 Maven 构建以确认项目编译并通过测试：

```bash
./mvnw clean verify
```

如果构建成功，通知用户。如果失败，诊断并修复问题后再继续。

### 10. 向用户展示总结

展示创建项目的总结：

```
项目创建成功

  Artifact:      <artifactId>
  Spring Boot:   <version>
  Java:          <javaVersion>
  架构:          <DDD | Layered>
  构建工具:      Maven
  Docker:        <服务列表>

  目录:         ./<artifactId>/

  下一步:
    1. cd <artifactId>
    2. docker compose up -d
    3. ./mvnw spring-boot:run
    4. 打开 http://localhost:8080/swagger-ui.html
```

## 架构模式

### 分层架构

传统的三层架构，具有明确的关注点分离：

| 层级 | 包 | 责任 |
|------|----|------|
| **表示层** | `controller/` | HTTP 端点、请求/响应映射 |
| **业务层** | `service/` | 业务逻辑、事务管理 |
| **数据访问层** | `repository/` | 数据库操作（通过 Spring Data） |
| **领域层** | `model/` | JPA 实体和 DTO |

**适用于**：简单的 CRUD 应用、中小型服务、新接触 Spring Boot 的团队。

### DDD 架构

具有六边形边界的领域驱动设计：

| 层级 | 包 | 责任 |
|------|----|------|
| **领域层** | `domain/` | 实体、值对象、领域服务（无框架） |
| **应用层** | `application/` | 用例、组合、DTO 映射 |
| **基础设施层** | `infrastructure/` | JPA 适配器、外部集成、配置 |
| **表示层** | `presentation/` | REST 控制器、错误处理 |

**适用于**：复杂的业务领域、具有丰富逻辑的微服务、长期项目。

## 示例

### 示例 1：简单的 REST API 与 PostgreSQL（分层）

**用户请求**："创建一个使用 PostgreSQL 的 Spring Boot REST API 项目"

```bash
curl -s https://start.spring.io/starter.zip \
  -d type=maven-project \
  -d bootVersion=3.4.5 \
  -d groupId=com.example \
  -d artifactId=my-api \
  -d packageName=com.example.myapi \
  -d javaVersion=21 \
  -d dependencies=web,data-jpa,postgresql,validation,testcontainers \
  -o starter.zip
```

结果：分层项目，包含 `controller/`、`service/`、`repository/`、`model/` 包，PostgreSQL Docker Compose 和 SpringDoc OpenAPI。

### 示例 2：DDD 微服务与多个存储

**用户请求**："启动一个具有 DDD、PostgreSQL 和 Redis 的 Spring Boot 3 微服务"

```bash
curl -s https://start.spring.io/starter.zip \
  -d type=maven-project \
  -d bootVersion=3.4.5 \
  -d groupId=com.acme \
  -d artifactId=order-service \
  -d packageName=com.acme.order \
  -d javaVersion=21 \
  -d dependencies=web,data-jpa,postgresql,data-redis,validation,testcontainers \
  -o starter.zip
```

结果：DDD 项目，包含 `domain/`、`application/`、`infrastructure/`、`presentation/` 包，PostgreSQL + Redis Docker Compose 和 SpringDoc OpenAPI。

## 最佳实践

- **始终使用 Spring Initializr** 生成项目，以获取正确的依赖管理和父 POM。
- **使用 Java 记录** 作为 DTO — 它们是不可变的且简洁的。
- **DDD 架构中保持领域层无框架** — `domain/` 中无 Spring 注解。
- **使用环境变量** 存储生产中的敏感配置（数据库密码等）。
- **固定 Docker 镜像版本** 在 `docker-compose.yaml` 中，避免意外的破坏性变更。
- **运行 `./mvnw clean verify`** 后设置以确保所有内容编译并通过测试。
- **使用 Testcontainers** 进行集成测试，而不是依赖 Docker Compose。

## 限制和警告

- Spring Initializr 需要互联网访问 — 此技能无法离线工作。
- Spring Boot 4.x 的可用性取决于当前的发布周期 — 检查 start.spring.io 获取最新版本。
- Docker Compose 凭证从 `.env` 文件加载（git-忽略）— 永远不要将密钥提交到版本控制。
- `spring.jpa.hibernate.ddl-auto=update` 设置仅用于开发 — 生产中应使用 Flyway 或 Liquibase。
- ArchUnit 版本必须与 Spring Boot 捆绑的 JUnit 5 版本兼容。
