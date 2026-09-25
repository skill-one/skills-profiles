# 创建 Spring Boot Java 项目提示

- 请确保您的系统已安装以下软件：

  - Java 21
  - Docker
  - Docker Compose

- 如果您需要自定义项目名称，请更改 [下载 Spring Boot 项目模板](#download-spring-boot-project-template) 中的 `artifactId` 和 `packageName`

- 如果您需要更新 Spring Boot 版本，请更改 [下载 Spring Boot 项目模板](#download-spring-boot-project-template) 中的 `bootVersion`

## 检查 Java 版本

- 在终端中运行以下命令并检查 Java 版本

```shell
java -version
```

## 下载 Spring Boot 项目模板

- 在终端中运行以下命令下载 Spring Boot 项目模板

```shell
curl https://start.spring.io/starter.zip \
  -d artifactId=${input:projectName:demo-java} \
  -d bootVersion=3.4.5 \
  -d dependencies=lombok,configuration-processor,web,data-jpa,postgresql,data-redis,data-mongodb,validation,cache,testcontainers \
  -d javaVersion=21 \
  -d packageName=com.example \
  -d packaging=jar \
  -d type=maven-project \
  -o starter.zip
```

## 解压下载的文件

- 在终端中运行以下命令解压下载的文件

```shell
unzip starter.zip -d ./${input:projectName:demo-java}
```

## 删除下载的 zip 文件

- 在终端中运行以下命令删除下载的 zip 文件

```shell
rm -f starter.zip
```

## 切换到项目根目录

- 在终端中运行以下命令切换到项目根目录

```shell
cd ${input:projectName:demo-java}
```

## 添加额外依赖

- 将 `springdoc-openapi-starter-webmvc-ui` 和 `archunit-junit5` 依赖插入到 `pom.xml` 文件中

```xml
<dependency>
  <groupId>org.springdoc</groupId>
  <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
  <version>2.8.6</version>
</dependency>
<dependency>
  <groupId>com.tngtech.archunit</groupId>
  <artifactId>archunit-junit5</artifactId>
  <version>1.2.1</version>
  <scope>test</scope>
</dependency>
```

## 添加 SpringDoc、Redis、JPA 和 MongoDB 配置

- 将 SpringDoc 配置插入到 `application.properties` 文件中

```properties
# SpringDoc 配置
springdoc.swagger-ui.doc-expansion=none
springdoc.swagger-ui.operations-sorter=alpha
springdoc.swagger-ui.tags-sorter=alpha
```

- 将 Redis 配置插入到 `application.properties` 文件中

```properties
# Redis 配置
spring.data.redis.host=localhost
spring.data.redis.port=6379
spring.data.redis.password=rootroot
```

- 将 JPA 配置插入到 `application.properties` 文件中

```properties
# JPA 配置
spring.datasource.driver-class-name=org.postgresql.Driver
spring.datasource.url=jdbc:postgresql://localhost:5432/postgres
spring.datasource.username=postgres
spring.datasource.password=rootroot
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

- 将 MongoDB 配置插入到 `application.properties` 文件中

```properties
# MongoDB 配置
spring.data.mongodb.host=localhost
spring.data.mongodb.port=27017
spring.data.mongodb.authentication-database=admin
spring.data.mongodb.username=root
spring.data.mongodb.password=rootroot
spring.data.mongodb.database=test
```

## 添加 `docker-compose.yaml` 并配置 Redis、PostgreSQL 和 MongoDB 服务

- 在项目根目录创建 `docker-compose.yaml` 并添加以下服务：`redis:6`、`postgresql:17` 和 `mongo:8`。

  - redis 服务应具有：
    - 密码 `rootroot`
    - 将端口 6379 映射到 6379
    - 挂载卷 `./redis_data` 到 `/data`
  - postgresql 服务应具有：
    - 密码 `rootroot`
    - 将端口 5432 映射到 5432
    - 挂载卷 `./postgres_data` 到 `/var/lib/postgresql/data`
  - mongo 服务应具有：
    - initdb 根用户名 `root`
    - initdb 根密码 `rootroot`
    - 将端口 27017 映射到 27017
    - 挂载卷 `./mongo_data` 到 `/data/db`

## 添加 `.gitignore` 文件

- 在 `.gitignore` 文件中插入 `redis_data`、`postgres_data` 和 `mongo_data` 目录

## 运行 Maven 测试命令

- 运行 `./mvnw clean test` 命令检查项目是否正常工作

```shell
./mvnw clean test
```

## 运行 Maven 运行命令（可选）

- （可选）`docker-compose up -d` 启动服务，`./mvnw spring-boot:run` 运行 Spring Boot 项目，`docker-compose rm -sf` 停止服务。

## 逐步操作
