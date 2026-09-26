# Kotlin中的JPA实体映射

Kotlin的`data class`非常适合DTO，但不适合JPA实体。Hibernate依赖于`data class`会破坏的身份语义：所有字段的`equals`/`hashCode`会破坏状态变化后的`Set`/`Map`成员资格，自动生成的`copy()`会创建受管实体的脱离副本。

这项技能将教授Kotlin + Spring Data JPA项目的正确实体设计、身份策略和唯一性约束。

## 实体设计规则

- **永远不要用`data class`作为JPA实体。** 使用普通`class`。保留`data class`用于DTO。
- 除非项目明确使用共享模型，否则保持传输DTO和持久化实体分离。
- 仅在对象构造和持久化生命周期使其安全时，才将所需列建模为非空。
- 仅在项目已接受该权衡且生命周期安全时，才使用`lateinit`。
- 当存在JPA实体时，验证`kotlin("plugin.jpa")`或等效的无参数支持。
- 验证类和成员在需要时与代理兼容。

## 身份和等价

- 永远不要接受`data class`在实体上生成的所有字段`equals`/`hashCode`。
- 如果项目已经定义了身份策略，请遵循项目约定。
- 如果没有约定，请使用基于ID的等价性和稳定的`hashCode`。
- 对于数据库生成的ID，使用可空的`var id: Long? = null`建模未保存状态，并使用受保护的设置；不要使用`0L`作为哨兵值。
- 在讨论等价性时，要明确可变字段和延迟关联。

### 有问题的：`data class`实体

```kotlin
// 错误：data class会根据所有字段生成equals/hashCode，生成的ID使用0哨兵而不是null
data class Order(
    @Id @GeneratedValue val id: Long = 0,
    var status: String,
    var total: BigDecimal
)
// 错误：order.status = "SHIPPED"; set.contains(order) → false (hash改变了)
// 错误：Hibernate proxy.equals(entity) → false (代理的延迟字段未初始化)
```

### 正确：带基于ID的身份的普通类

```kotlin
@Entity
@Table(name = "orders")
class Order(
    @Column(nullable = false)
    var status: String,

    @Column(nullable = false)
    var total: BigDecimal
) {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null
        protected set

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Order) return false
        return id != null && id == other.id
    }

    override fun hashCode(): Int = javaClass.hashCode()

    // toString必须不引用延迟加载的集合
    override fun toString(): String = "Order(id=$id, status=$status)"
}
```

**关键规则：**
- `equals`仅按ID比较——在脏跟踪和代理解包下保持稳定
- `hashCode`返回基于类的常量——避免持久化后的`Set`/`Map`损坏
- `toString`排除延迟加载的关联——防止`LazyInitializationException`
- 构造函数参数是可变的实体字段；数据库生成的`id`是可空的，具有受保护的设置

## 唯一性约束

当API必须是无副作用的（例如，“为订单X预留库存”），在两个层级上强制执行唯一性：数据库约束用于正确性，应用程序检查用于干净的错误。

### 有问题的：没有重复保护

```kotlin
@Service
class ReservationService(private val repo: ReservationRepository) {
    @Transactional
    fun createReservation(variantId: Long, orderId: String, qty: Int): Reservation {
        // 错误：没有检查——重复会静默累积
        return repo.save(Reservation(variantId = variantId, orderId = orderId, quantity = qty))
    }
}
```

### 正确：数据库约束+应用程序保护

```kotlin
@Entity
@Table(
    name = "reservations",
    uniqueConstraints = [
        UniqueConstraint(columnNames = ["variant_id", "order_id"])
    ]
)
class Reservation(
    @Column(name = "variant_id", nullable = false)
    val variantId: Long,

    @Column(name = "order_id", nullable = false)
    val orderId: String,

    @Column(nullable = false)
    var quantity: Int
) {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null
        protected set
}

interface ReservationRepository : JpaRepository<Reservation, Long> {
    fun findByVariantIdAndOrderId(variantId: Long, orderId: String): Reservation?
}

@Service
class ReservationService(private val repo: ReservationRepository) {
    @Transactional
    fun createReservation(variantId: Long, orderId: String, qty: Int): Reservation {
        repo.findByVariantIdAndOrderId(variantId, orderId)?.let {
            throw IllegalStateException(
                "Reservation already exists for variant=$variantId, order=$orderId"
            )
        }
        return repo.save(Reservation(variantId = variantId, orderId = orderId, quantity = qty))
    }
}
```

**关键规则：**
- 数据库约束是强制性的——仅应用程序检查存在竞态条件
- 应用程序检查提供干净的错误消息——没有它，用户会收到原始的`DataIntegrityViolationException`
- 两个层级一起：应用程序捕获常见情况，数据库捕获竞态条件
- Spring Data会自动派生`findByXAndY`查询

## 查询和获取规则

- 通过查看实际查询计数或SQL日志来诊断N+1，而不是通过猜测注解。
- 优先考虑有针对性的获取解决方案：`@EntityGraph`、`JOIN FETCH`、批量获取或DTO投影。
- 对集合获取连接加分页要小心——指明权衡。
- 使用索引和唯一性约束来支持真实的查询模式。

## 常见的ORM陷阱

- **双向关联：** 在领域方法中维护双方。部分更新的图会导致微妙错误。
- **`orphanRemoval` vs cascade remove：** 不可以互换。在做出选择前解释生命周期语义。
- **延迟加载触发器：** `toString`、调试日志记录、JSON序列化和IDE检查都可能触发延迟加载。
- **批量更新/删除：** 绕过持久化上下文和生命周期回调。后续读取可能已过时。
- **多个集合获取：** 可能导致笛卡尔积。验证ORM可以安全执行集合密集型获取计划。
- **`Set` + 可变等价：** 实体状态变化后，集合成员资格可能破裂。
- **`@Version`：** 当并发更新很重要时，是最清晰的乐观并发机制。
- **`open-in-view`禁用：** DTO映射触及延迟字段必须在事务边界内进行。

## 安全措施

- 不要用`data class`作为JPA实体。
- 不要到处推荐`FetchType.EAGER`以掩盖延迟加载症状。
- 默认情况下不要通过API响应直接暴露实体。
- 不要在没有解释获取计划如何改变查询行为的情况下声称修复了N+1。
