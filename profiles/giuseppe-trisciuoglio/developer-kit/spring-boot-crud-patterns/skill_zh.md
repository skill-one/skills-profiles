# Spring Boot CRUD模式

## 概述

为Spring Boot 3.5+服务提供完整的CRUD工作流，采用面向特性的架构。创建和验证领域聚合、JPA仓库、应用服务和REST控制器，并确保关注点分离。将详细代码列表推迟到参考文件中，以逐步披露。

## 使用场景

- 为基于Spring Data JPA的创建/读取/更新/删除工作流创建REST端点。
- 采用DDD启发式架构实现特征包，包含聚合、仓库和应用服务。
- 定义DTO记录、请求验证和控制器映射，以供外部客户端使用。
- 诊断现有Spring Boot服务中的CRUD回归、仓库契约或事务边界。
- 触发短语：**"实现Spring CRUD控制器"**、**"创建端点"**、**"添加数据库实体"**、**"优化基于特征的仓库"**、**"为JPA聚合映射DTO"**、**"为REST列表端点添加分页"**。

## 指南

遵循此简化的工作流，以明确的验证门控交付与特征一致的CRUD服务：

### 1. 建立特征结构

创建`feature/<name>/`目录，包含`domain`、`application`、`presentation`和`infrastructure`子包。
**验证**：在继续之前，验证目录结构是否与特征边界匹配。

### 2. 定义领域模型

创建实体类，通过工厂方法（`create`、`update`）强制执行不变量。保持领域逻辑框架无关。
**验证**：在继续之前，断言所有不变量都通过单元测试覆盖。

### 3. 暴露领域端口

在`domain/repository`中声明仓库接口，描述持久化契约而不涉及实现细节。
**验证**：确认接口签名与领域操作匹配。

### 4. 提供基础设施适配器

在`infrastructure/persistence`中创建映射到领域模型的JPA实体。实现Spring Data仓库。
**验证**：运行`@DataJpaTest`以验证实体映射和仓库集成。

### 5. 实现应用服务

创建`@Transactional`服务类，编排领域操作和DTO映射。
**验证**：确保事务边界正确，并在需要时应用乐观锁。

### 6. 定义DTO和控制器

使用Java记录定义API契约，并使用`jakarta.validation`注解。映射REST端点并使用正确的状态码。
**验证**：测试验证约束并验证HTTP状态码（201 POST、200 GET、204 DELETE）。

### 7. 验证和部署

使用Testcontainers运行集成测试。验证迁移（Liquibase/Flyway）与聚合模式一致。
**验证**：在部署前执行完整测试套件；确认模式迁移脚本已应用。

参考`references/examples-product-feature.md`获取与每一步完全一致的完整代码示例。

## 示例

### Java代码示例：产品特征

```java
// feature/product/domain/Product.java
package com.example.product.domain;

import java.math.BigDecimal;
import java.time.Instant;

public record Product(
    String id,
    String name,
    String description,
    BigDecimal price,
    int stock,
    Instant createdAt,
    Instant updatedAt
) {
    public static Product create(String name, String desc, BigDecimal price, int stock) {
        if (name == null || name.isBlank()) throw new IllegalArgumentException("Name required");
        if (price == null || price.compareTo(BigDecimal.ZERO) < 0) throw new IllegalArgumentException("Invalid price");
        return new Product(null, name.trim(), desc, price, stock, Instant.now(), null);
    }

    public Product withPrice(BigDecimal newPrice) {
        return new Product(id, name, description, newPrice, stock, createdAt, Instant.now());
    }
}
```

```java
// feature/product/domain/repository/ProductRepository.java
package com.example.product.domain.repository;

import com.example.product.domain.Product;
import java.util.Optional;

public interface ProductRepository {
    Product save(Product product);
    Optional<Product> findById(String id);
    void deleteById(String id);
}
```

```java
// feature/product/infrastructure/persistence/ProductJpaEntity.java
package com.example.product.infrastructure.persistence;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;

@Entity @Table(name = "products")
public class ProductJpaEntity {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private String id;
    private String name;
    private String description;
    private BigDecimal price;
    private int stock;
    private Instant createdAt;
    private Instant updatedAt;

    // getters, setters, constructor from domain (omitted for brevity)
}
```

```java
// feature/product/infrastructure/persistence/JpaProductRepository.java
package com.example.product.infrastructure.persistence;

import com.example.product.domain.Product;
import com.example.product.domain.repository.ProductRepository;
import org.springframework.stereotype.Repository;

@Repository
public class JpaProductRepository implements ProductRepository {
    private final SpringDataProductRepository springData;

    public JpaProductRepository(SpringDataProductRepository springData) {
        this.springData = springData;
    }

    @Override
    public Product save(Product product) {
        ProductJpaEntity entity = toEntity(product);
        ProductJpaEntity saved = springData.save(entity);
        return toDomain(saved);
    }

    // findById, deleteById implementations...
}
```

```java
// feature/product/presentation/rest/ProductController.java
package com.example.product.presentation.rest;

import com.example.product.domain.Product;
import com.example.product.domain.repository.ProductRepository;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/products")
public class ProductController {
    private final ProductService service;

    public ProductController(ProductService service) { this.service = service; }

    @PostMapping
    public ResponseEntity<ProductResponse> create(@Valid @RequestBody CreateProductRequest req) {
        Product product = service.create(req.toDomain());
        return ResponseEntity.status(201).body(ProductResponse.from(product));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getById(@PathVariable String id) {
        return service.findById(id)
            .map(p -> ResponseEntity.ok(ProductResponse.from(p)))
            .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable String id) {
        service.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    // record DTOs
    public record CreateProductRequest(
        @NotBlank String name,
        String description,
        @NotNull @DecimalMin("0.01") java.math.BigDecimal price,
        @Min(0) int stock
    ) {
        Product toDomain() { return Product.create(name, description, price, stock); }
    }

    public record ProductResponse(String id, String name, java.math.BigDecimal price) {
        static ProductResponse from(Product p) { return new ProductResponse(p.id(), p.name(), p.price()); }
    }
}
```

### JSON输入/输出示例

**创建请求：**
```json
{
  "name": "无线键盘",
  "description": "人体工学键盘",
  "price": 79.99,
  "stock": 50
}
```

**创建响应（201）：**
```json
{
  "id": "prod-123",
  "name": "无线键盘",
  "price": 79.99,
  "_links": { "self": "/api/products/prod-123" }
}
```

**分页列表请求：**
```bash
curl "http://localhost:8080/api/products?page=0&size=10&sort=name,asc"
```

## 最佳实践

- 按聚合将领域、应用和表示代码组合在特征包内。
- 使用Java记录创建不可变的DTO；在服务边界转换领域类型。
- 为写操作应用事务和乐观锁。
- 规范分页默认值（页码、大小、排序），并记录查询参数。
- 在info级别记录CRUD生命周期事件（创建、更新、删除），并保留结构化审计跟踪。
- 通过Spring Boot Actuator暴露健康和指标；监控吞吐量和错误率。

## 限制和警告

- **永远不要**在控制器中直接暴露JPA实体，以防止懒加载泄漏和序列化问题。
- **永远不要**混合字段注入与构造函数注入；为可测试性保持不可变性。
- **永远不要**在控制器或仓库适配器中嵌入业务逻辑；将其保留在领域/应用层。
- **始终**积极验证输入，以防止约束违规并产生一致的错误负载。
- **始终**确保迁移（Liquibase/Flyway）与聚合演变一致，然后再部署模式更改。
- **始终**在合并到主分支前使用Testcontainers运行集成测试，以防止持久化回归。

## 参考

- [HTTP方法、注解、DTO模式](references/crud-reference.md)
- [从入门到高级的渐进式示例](references/examples-product-feature.md)
- [Spring Boot官方文档](references/spring-official-docs.md)
- [CRUD生成器脚本](scripts/generate_crud_boilerplate.py) - `python scripts/generate_crud_boilerplate.py --spec entity.json --package com.example.product --output ./generated`
