# Spring Data JPA

## 概述

提供 Spring Data JPA 仓库的模式、实体关系、查询、分页、审计和事务。

## 使用场景

创建具有 CRUD 操作、实体关系、`@Query` 注解、分页、审计或 UUID 主键的仓库。

## 使用说明

### 创建仓库接口

要实现一个仓库接口：

1. **扩展适当的仓库接口：**
   ```java
   @Repository
   public interface UserRepository extends JpaRepository<User, Long> {
       // 在此处定义自定义方法
   }
   ```

2. **使用派生查询进行简单条件：**
   ```java
   Optional<User> findByEmail(String email);
   List<User> findByStatusOrderByCreatedDateDesc(String status);
   ```

3. **使用 `@`Query 实现自定义查询：**
   ```java
   @Query("SELECT u FROM User u WHERE u.status = :status")
   List<User> findActiveUsers(@Param("status") String status);
   ```

### 配置实体

1. **使用适当的注解定义实体：**
   ```java
   @Entity
   @Table(name = "users")
   public class User {
       @Id
       @GeneratedValue(strategy = GenerationType.IDENTITY)
       private Long id;

       @Column(nullable = false, length = 100)
       private String email;
   }
   ```

2. **使用适当的级联类型配置关系：**
   ```java
   @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
   private List<Order> orders = new ArrayList<>();
   ```
   **验证：** 在应用到生产数据之前，使用小数据集测试级联行为。验证删除操作不会意外级联。

3. **设置数据库审计：**
   ```java
   @CreatedDate
   @Column(nullable = false, updatable = false)
   private LocalDateTime createdDate;
   ```

### 应用查询模式

1. **使用派生查询进行简单条件**
2. **使用 `@`Query 进行复杂查询**
3. **使用 Optional<T> 返回单个结果**
4. **使用 Pageable 进行分页**
5. **使用 `@`Modifying 进行更新/删除操作**

### 管理事务

1. **使用 `@`Transactional(readOnly = true) 标记只读操作**
2. **使用显式事务边界进行修改操作**
3. **在需要时指定回滚条件**

### 验证和优化

**1. 验证实体配置：**
- 在生产部署前在事务中测试级联行为
- 验证双向关系同步正确

**2. 优化查询性能：**
- 对大表上的查询运行 `EXPLAIN ANALYZE`
- 如果检测到性能问题：添加索引 → 使用 EXPLAIN 验证 → 重复
- 使用 `@EntityGraph` 防止 N+1 查询

**3. 验证分页：**
- 确保索引列支持分页查询
- 使用大数据集测试以验证游标稳定性

## 示例

### 基本 CRUD 仓库

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    // 派生查询
    List<Product> findByCategory(String category);

    // 自定义查询
    @Query("SELECT p FROM Product p WHERE p.price > :minPrice")
    List<Product> findExpensiveProducts(@Param("minPrice") BigDecimal minPrice);
}
```

### 分页实现

```java
@Service
public class ProductService {
    private final ProductRepository repository;

    public Page<Product> getProducts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("name").ascending());
        return repository.findAll(pageable);
    }
}
```

### 具有审计的实体

```java
@Entity
@EntityListeners(AuditingEntityListener.class)
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdDate;

    @LastModifiedDate
    private LocalDateTime lastModifiedDate;

    @CreatedBy
    @Column(nullable = false, updatable = false)
    private String createdBy;
}
```

## 最佳实践

### 实体设计
- 仅使用构造函数注入（绝不使用字段注入）
- 优先使用 `final` 修饰符的不可变字段
- 使用 Java 记录（16+）或 `@Value` 用于 DTO
- 始终提供适当的 `@Id` 和 `@GeneratedValue` 注解
- 使用显式的 `@Table` 和 `@Column` 注解

### 性能优化
- 使用适当的获取策略（LAZY vs EAGER）
- 对大数据集实现分页
- 对频繁查询的字段使用数据库索引
- 考虑使用 `@EntityGraph` 避免 N+1 查询问题

### 参考文档

有关完整示例、详细模式和高阶配置，请参阅：

- [示例](references/examples.md) - 常见场景的完整代码示例
- [参考](references/reference.md) - 详细模式和高阶配置

## 限制和警告

- 不要直接在 REST API 中暴露 JPA 实体；始终使用 DTO 以防止懒加载问题。
- 通过在查询中使用 `@EntityGraph` 或 `JOIN FETCH` 避免 N+1 查询问题。
- 对大型集合使用 `CascadeType.REMOVE` 要谨慎，因为它可能导致性能问题。
- 不要使用集合的 EAGER 获取类型；它可能导致过多的数据库查询。
- 避免长时间运行的事务，它们可能导致数据库锁竞争。
- 使用 `@Transactional(readOnly = true)` 进行读操作以启用优化。
- 注意一级缓存；在同一个事务中，实体可能不会反映数据库更改。
- UUID 主键可能导致索引碎片；考虑使用顺序 UUID 或 Long ID。
- 大数据集的分页需要适当的索引以避免全表扫描。
