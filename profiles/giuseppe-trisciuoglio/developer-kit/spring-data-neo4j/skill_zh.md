# Spring Data Neo4j 集成模式

## 概述

为 Spring Boot 应用程序提供 Spring Data Neo4j 集成模式。涵盖使用 `@Node` 和 `@Relationship` 的节点实体映射、仓库配置（命令式和响应式）、使用 `@Query` 的自定义 Cypher 查询以及使用嵌入式 Neo4j 数据库的集成测试。

## 何时使用

在以下情况下使用此技能：
- Spring Boot 中的图数据库和 Neo4j 集成
- 节点实体、关系和 Cypher 查询
- Spring Data Neo4j 仓库（命令式或响应式）
- 使用嵌入式数据库的 Neo4j 测试

## 说明

### 1. 设置 Spring Data Neo4j

**添加依赖项：**

Maven:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-neo4j</artifactId>
</dependency>
```

Gradle:
```groovy
implementation 'org.springframework.boot:spring-boot-starter-data-neo4j'
```

**在 application.properties 中配置连接：**
```properties
spring.neo4j.uri=bolt://localhost:7687
spring.neo4j.authentication.username=neo4j
spring.neo4j.authentication.password=secret
```

**配置 Cypher-DSL 方言（推荐）：**
```java
@Configuration
public class Neo4jConfig {
    @Bean
    Configuration cypherDslConfiguration() {
        return Configuration.newConfig()
            .withDialect(Dialect.NEO4J_5).build();
    }
}
```

> **验证检查点**：在继续之前，通过 cypher-shell 运行 `MATCH (n) RETURN count(n)` 来验证连接是否正常工作。

### 2. 定义节点实体

1. **使用 `@`Node 注解**来标记实体类
2. **选择 ID 策略：**
   - 业务键作为 `@`Id（不可变，自然标识符）
   - 生成的 `@`Id `@`GeneratedValue（Neo4j 内部 ID）
3. **定义关系**使用 `@`Relationship 注解
4. **保持实体不可变**使用 final 字段
5. **使用 `@`Property**用于自定义属性名

> **验证检查点**：如果实体保存失败，请检查约束违规——重复的 ID 违反唯一性约束。

### 3. 创建仓库

1. **扩展仓库接口：**
   - `Neo4jRepository<Entity, ID>` 用于命令式操作
   - `ReactiveNeo4jRepository<Entity, ID>` 用于响应式操作
2. **使用查询派生**用于简单查询
3. **应用 `@`Query 注解**用于复杂 Cypher 查询
4. **使用 `$`paramName 语法**用于参数

> **验证检查点**：首先使用 `findAll()` 测试仓库—if 结果为空，请验证 Neo4j 实例正在运行且凭证正确。

### 4. 测试您的实现

1. **使用 `@`DataNeo4jTest**进行具有测试切片的仓库测试
2. **设置 Neo4j Harness**使用嵌入式数据库和 fixtures
3. **通过 `withFixture()` Cypher 查询提供测试数据**
4. **在测试之间清理测试数据**

> **验证检查点**：如果测试因 "Connection refused" 失败，请确保嵌入式 Neo4j 在 `@BeforeAll` 中成功启动。

## 基本实体映射

### 使用业务键的节点实体

```java
@Node("Movie")
public class MovieEntity {

    @Id
    private final String title;  // 业务键作为 ID

    @Property("tagline")
    private final String description;

    private final Integer year;

    @Relationship(type = "ACTED_IN", direction = Direction.INCOMING)
    private List<Roles> actorsAndRoles = new ArrayList<>();

    @Relationship(type = "DIRECTED", direction = Direction.INCOMING)
    private List<PersonEntity> directors = new ArrayList<>();

    public MovieEntity(String title, String description, Integer year) {
        this.title = title;
        this.description = description;
        this.year = year;
    }
}
```

### 使用生成 ID 的节点实体

```java
@Node("Movie")
public class MovieEntity {

    @Id @GeneratedValue
    private Long id;

    private final String title;

    @Property("tagline")
    private final String description;

    public MovieEntity(String title, String description) {
        this.id = null;  // 从不手动设置
        this.title = title;
        this.description = description;
    }

    // 用于生成 ID 的不可变 wither 方法
    public MovieEntity withId(Long id) {
        if (this.id != null && this.id.equals(id)) {
            return this;
        } else {
            MovieEntity newObject = new MovieEntity(this.title, this.description);
            newObject.id = id;
            return newObject;
        }
    }
}
```

## 仓库模式

### 基本仓库接口

```java
@Repository
public interface MovieRepository extends Neo4jRepository<MovieEntity, String> {

    // 从方法名派生查询
    MovieEntity findOneByTitle(String title);

    List<MovieEntity> findAllByYear(Integer year);

    List<MovieEntity> findByYearBetween(Integer startYear, Integer endYear);
}
```

### 响应式仓库

```java
@Repository
public interface MovieRepository extends ReactiveNeo4jRepository<MovieEntity, String> {

    Mono<MovieEntity> findOneByTitle(String title);

    Flux<MovieEntity> findAllByYear(Integer year);
}
```

**命令式与响应式：**
- 使用 `Neo4jRepository` 用于阻塞、命令式操作
- 使用 `ReactiveNeo4jRepository` 用于非阻塞、响应式操作
- **不要在同一应用程序中混合命令式和响应式**
- 响应式需要数据库端 Neo4j 4+ 版本

## 使用 `@`Query 的自定义查询

```java
@Repository
public interface AuthorRepository extends Neo4jRepository<Author, Long> {

    @Query("MATCH (b:Book)-[:WRITTEN_BY]->(a:Author) " +
           "WHERE a.name = $name AND b.year > $year " +
           "RETURN b")
    List<Book> findBooksAfterYear(@Param("name") String name,
                                   @Param("year") Integer year);

    @Query("MATCH (b:Book)-[:WRITTEN_BY]->(a:Author) " +
           "WHERE a.name = $name " +
           "RETURN b ORDER BY b.year DESC")
    List<Book> findBooksByAuthorOrderByYearDesc(@Param("name") String name);
}
```

**自定义查询最佳实践：**
- 使用 `$parameterName` 用于参数占位符
- 当参数名与方法参数不同时使用 `@Param` 注解
- MATCH 指定节点模式和关系
- WHERE 过滤结果
- RETURN 定义返回内容

## 测试策略

### Neo4j Harness 用于集成测试

**测试配置：**
```java
@DataNeo4jTest
class BookRepositoryIntegrationTest {

    private static Neo4j embeddedServer;

    @BeforeAll
    static void initializeNeo4j() {
        embeddedServer = Neo4jBuilders.newInProcessBuilder()
            .withDisabledServer()  // 无需 HTTP 访问
            .withFixture(
                "CREATE (b:Book {isbn: '978-0547928210', " +
                "name: 'The Fellowship of the Ring', year: 1954})" +
                "-[:WRITTEN_BY]->(a:Author {id: 1, name: 'J. R. R. Tolkien'}) " +
                "CREATE (b2:Book {isbn: '978-0547928203', " +
                "name: 'The Two Towers', year: 1956})" +
                "-[:WRITTEN_BY]->(a)"
            )
            .build();
    }

    @AfterAll
    static void stopNeo4j() {
        embeddedServer.close();
    }

    @DynamicPropertySource
    static void neo4jProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.neo4j.uri", embeddedServer::boltURI);
        registry.add("spring.neo4j.authentication.username", () -> "neo4j");
        registry.add("spring.neo4j.authentication.password", () -> "null");
    }

    @Autowired
    private BookRepository bookRepository;

    @Test
    void givenBookExists_whenFindOneByTitle_thenBookIsReturned() {
        Book book = bookRepository.findOneByTitle("The Fellowship of the Ring");
        assertThat(book.getIsbn()).isEqualTo("978-0547928210");
    }
}
```

## 示例

### 示例 1：保存和检索实体

**输入：**
```java
MovieEntity movie = new MovieEntity("The Matrix", "Welcome to the Real World", 1999);
movieRepository.save(movie);

MovieEntity found = movieRepository.findOneByTitle("The Matrix");
```

**输出：**
```java
MovieEntity{
    title="The Matrix",
    description="Welcome to the Real World",
    year=1999,
    actorsAndRoles=[],
    directors=[]
}
```

### 示例 2：自定义 Cypher 查询

**输入：**
```java
List<Book> books = authorRepository.findBooksAfterYear("J.R.R. Tolkien", 1950);
```

**输出：**
```java
[
    Book{isbn="978-0547928210", name="The Fellowship of the Ring", year=1954},
    Book{isbn="978-0547928203", name="The Two Towers", year=1956},
    Book{isbn="978-0547928227", name="The Return of the King", year=1957}
]
```

### 示例 3：关系遍历

**输入：**
```java
@Query("MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) " +
       "WHERE m.title = $title RETURN a.name as actorName")
List<String> findActorsByMovieTitle(@Param("title") String title);

List<String> actors = movieRepository.findActorsByMovieTitle("The Matrix");
```

**输出：**
```java
["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving"]
```

---

从基本到高级示例，涵盖完整的电影数据库、社交网络模式、电子商务产品目录、自定义查询和响应式操作。

有关完整代码示例，请参阅 [示例](./references/examples.md)。

## 最佳实践

### 实体设计
- 使用不可变实体和 final 字段
- 在业务键 (`@`Id) 或生成 ID (`@`Id `@`GeneratedValue) 之间选择
- 保持实体专注于图结构，而不是业务逻辑
- 使用正确的关系方向（INCOMING、OUTGOING、UNDIRECTED）

### 仓库设计
- 扩展 `Neo4jRepository` 用于命令式或 `ReactiveNeo4jRepository` 用于响应式
- 使用查询派生进行简单查询
- 为复杂图模式编写自定义 `@`Query
- 不要在同一应用程序中混合命令式和响应式

### 配置
- 始终显式配置 Cypher-DSL 方言
- 使用环境特定属性配置凭证
- 永远不要在源代码中硬编码凭证
- 根据负载配置连接池

### 测试
- 使用 Neo4j Harness 进行集成测试
- 通过 `withFixture()` Cypher 查询提供测试数据
- 使用 `@DataNeo4jTest` 进行测试切片
- 测试成功和边缘情况场景

### 架构
- 仅使用构造函数注入
- 将领域实体与 DTO 分离
- 遵循基于功能的包结构
- 保持领域层框架无关

### 安全
- 使用 Spring Boot 属性覆盖凭证
- 配置适当的认证和授权
- 在服务层验证输入参数
- 使用参数化查询防止 Cypher 注入

## 约束和警告

- 不要在同一应用程序中混合命令式和响应式仓库。
- Neo4j 事务对于写操作是必需的；确保 `@Transactional` 正确配置。
- 小心深度关系遍历，因为它可能导致性能问题。
- 大型结果集应分页以避免内存问题。
- Cypher 查询区分大小写；确保属性名的一致大小写。
- 不可变实体需要为生成 ID 提供适当的 wither 方法。
- Spring Data Neo4j 中的关系默认不是懒加载的；考虑投影用于大型图。
- Neo4j Java 驱动程序与响应式流不兼容；使用响应式驱动程序进行响应式操作。

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| `Connection refused` on localhost:7687 | Neo4j 服务器未运行 | 启动 Neo4j 或在测试中使用嵌入式 Neo4j |
| `Authentication failed` | 错误的凭证 | 检查 `spring.neo4j.authentication.username/password` |
| 实体未保存 / `MATCH` 返回空 | 事务未提交 | 添加 `@Transactional` 或验证自动提交设置 |
| `ConstraintViolationException` on save | 重复的 `@Id` 值 | 确保 IDs 唯一或使用 `@GeneratedValue` |
| 结果中缺少关系 | 错误的 `@Relationship` 方向 | 检查 `Direction.INCOMING/OUTGOING/UNDIRECTED` |
| `@Query` 返回错误数据 | Cypher 参数语法 | 使用 `$paramName` 而不是 `$ {paramName}` |
| 使用 `@DataNeo4jTest` 测试失败 | 嵌入式 Neo4j 未启动 | 确保 `@BeforeAll` 在测试前启动 Neo4j |

## 参考

有关详细文档，包括完整的 API 参考、Cypher 查询模式和配置选项：

- [注解参考](./references/reference.md#annotations-reference)
- [Cypher 查询语言](./references/reference.md#cypher-query-language)
- [配置属性](./references/reference.md#configuration-properties)
- [仓库方法](./references/reference.md#repository-methods)
- [投影和 DTO](./references/reference.md#projections-and-dtos)
- [事务管理](./references/reference.md#transaction-management)
- [性能调优](./references/reference.md#performance-tuning)

### 外部资源
- [Spring Data Neo4j 官方文档](https://docs.spring.io/spring-data/neo4j/reference/)
- [Neo4j 开发者指南](https://neo4j.com/developer/)
- [Spring Data Commons 文档](https://docs.spring.io/spring-data/commons/reference/)
