# 创建 Spring Boot Kotlin 项目提示

- 请确保您的系统已安装以下软件：

  - Java 21
  - Docker
  - Docker Compose

- 如果需要自定义项目名称，请更改 [下载 Spring Boot 项目模板](#download-spring-boot-project-template) 中的 `artifactId` 和 `packageName`

- 如果需要更新 Spring Boot 版本，请更改 [下载 Spring Boot 项目模板](#download-spring-boot-project-template) 中的 `bootVersion`

## 检查 Java 版本

- 在终端中运行以下命令并检查 Java 版本

```shell
java -version
```

## 下载 Spring Boot 项目模板

- 在终端中运行以下命令以下载 Spring Boot 项目模板

```shell
curl https://start.spring.io/starter.zip \
  -d artifactId=${input:projectName:demo-kotlin} \
  -d bootVersion=3.4.5 \
  -d dependencies=configuration-processor,webflux,data-r2dbc,postgresql,data-redis-reactive,data-mongodb-reactive,validation,cache,testcontainers \
  -d javaVersion=21 \
  -d language=kotlin \
  -d packageName=com.example \
  -d packaging=jar \
  -d type=gradle-project-kotlin \
  -o starter.zip
```

## 解压下载的文件

- 在终端中运行以下命令以解压下载的文件

```shell
unzip starter.zip -d ./${input:projectName:demo-kotlin}
```

## 删除下载的 zip 文件

- 在终端中运行以下命令以删除下载的 zip 文件

```shell
rm -f starter.zip
```

## 解压下载的文件

- 在终端中运行以下命令以解压下载的文件

```shell
unzip starter.zip -d ./${input:projectName:demo-kotlin}
```

## 添加额外依赖

- 将 `springdoc-openapi-starter-webmvc-ui` 和 `archunit-junit5` 依赖插入到 `build.gradle.kts` 文件中

```gradle.kts
dependencies {
  implementation("org.springdoc:springdoc-openapi-starter-webflux-ui:2.8.6")
  testImplementation("com.tngtech.archunit:archunit-junit5:1.2.1")
}
```

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

- 将 R2DBC 配置插入到 `application.properties` 文件中

```properties
# R2DBC 配置
spring.r2dbc.url=r2dbc:postgresql://localhost:5432/postgres
spring.r2dbc.username=postgres
spring.r2dbc.password=rootroot

spring.sql.init.mode=always
spring.sql.init.platform=postgres
spring.sql.init.continue-on-error=true
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

- 在项目根目录下创建 `docker-compose.yaml` 并添加以下服务：`redis:6`、`postgresql:17` 和 `mongo:8`。

  - redis 服务应具有
    - 密码 `rootroot`
    - 映射端口 6379 到 6379
    - 挂载卷 `./redis_data` 到 `/data`
  - postgresql 服务应具有
    - 密码 `rootroot`
    - 映射端口 5432 到 5432
    - 挂载卷 `./postgres_data` 到 `/var/lib/postgresql/data`
  - mongo 服务应具有
    - initdb 根用户名 `root`
    - initdb 根密码 `rootroot`
    - 映射端口 27017 到 27017
    - 挂载卷 `./mongo_data` 到 `/data/db`

- 将 `redis_data`、`postgres_data` 和 `mongo_data` 目录插入到 `.gitignore` 文件中

- 运行 `gradle clean test` 命令以检查项目是否正常工作

```shell
./gradlew clean test
```

- (可选) `docker-compose up -d` 以启动服务，`./gradlew spring-boot:run` 以运行 Spring Boot 项目，`docker-compose rm -sf` 以停止服务。

让我们一步一步来。
