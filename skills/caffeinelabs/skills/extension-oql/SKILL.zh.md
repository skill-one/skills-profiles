---
name: extension-oql
description: 通过 Caffeine Data Intelligence 代理使罐子（canister）的数据可查询。当应用程序存储结构化数据（地图/列表/记录数组）且需要用自然语言回答时使用——例如“顶级客户”、“按区域划分的收入”、“活跃项目”。通过 `caffeineai-oql` mops 包的 `Expose` 混合宏添加可发现的 `schema()` 和 JSON `execute()` 查询端点。
---

# OQL — 对象查询层

遍历实体的字段（非瞬态字段），对于每个值得查询的集合，考虑其数据如何映射到数据库中的**表**（一个*实体*）。你只为每个表声明一个实体——`Expose`混入使得它们可查询。

# 后端

每个实体都携带一个授权级别；默认的`.controllerOnly()`是安全的（仅用户可见，Data Intelligence代理仍然可读）。首先建模实体，然后为每个实体选择一个级别——参见`## Auth`。

## 设置

在**相同的写批次**中运行`mops add caffeineai-oql@0.7.0`作为你的第一个`mo:caffeineai-oql/...`导入。自动推导需要`moc >= 1.11`（生成的应用模板已经满足此条件）。

### 构建标志

`--default-persistent-actors`是必需的。`--implicit-package=core`是可选的便利性；每个代码片段和源文件都必须导入它使用的`mo:core`模块。如果应用使用`OQL.Table`并且需要超过4 GiB的`Region`，请添加`--max-stable-pages 1638400`；依赖项的自己的标志不会应用于依赖它的项目，因此必须在应用自己的构建中设置。

### 导入——每个解析器模块一个

`.toEntity`、构建器链（`.sample` / `.build` / `.public_` / …）和记录`_toRow`推导从在声明实体的文件中**顶层导入**的模块解析——解析器不会遍历子模块，因此仅导入`mo:caffeineai-oql`是不够的。导入你的代码使用的确切解析器模块：

- `mo:caffeineai-oql/Entity`——始终（构建器链`.sample` / `.build` / `.edge` / `.ownedBy` / auth-level，以及手动模式下的`.payload` / `.flatten`）。
- 每个`.toEntity` / `.toEntityManual`接收者的集合模块——`MapEntity`、`SetEntity`、`ListEntity`、`ArrayEntity`或`VarArrayEntity`。
- 对于每个**自动推导**（`.toEntity`）记录：`RecordValue`，加上每个基本字段类型的一个`<Type>Value`——`NatValue`、`TextValue`、`PrincipalValue`、`BoolValue`、`IntValue`、`FloatValue`、定长的`Nat`/`Int`宽度、`BlobValue`。手动`.payload`返回类型需要它们的`<Type>Value`；手动实体不需要`RecordValue`。

当集合模块缺少编译器名称时（例如："字段`toEntity`不存在…你是否想导入`mo:caffeineai-oql/MapEntity`？"），请添加命名的导入。缺少`Entity`导入不会获得此类提示：它表现为一个裸的*"字段`payload`不存在于类型`Builder<…>`*"（M0072）。将任何`字段`<`builderMethod>``不存在`错误视为此列表的缺失顶层导入，而不是错误的包版本。

## 声明实体并安装

`.toEntity(name, typeName, primaryKey)`将记录集合转换为可查询的实体；编译器自动推导字段。每个实体设置自己的授权级别（参见`## Auth`）；下面的示例显示了每个级别一个表。`Expose`仅添加OQL查询方法（`schema` / `execute`）——你的现有状态、类型和`shared`方法保持不变。

- 在每个`.toEntity` / `Entity.manual`链上始终调用`.sample({...})`；假值可以。空集合+无样本→空模式（`fields: []` / `"record { }"`）。

<!-- motoko-check:skip -->
```motoko filepath=src/backend/sample_required.mo
include Expose({ entities = [tasks.toEntity("task", "Task", "id").sample({ id = 0; title = "" }).public_().build()] })
```

```motoko filepath=src/backend/main.mo
import Map       "mo:core/Map";
import Nat       "mo:core/Nat";
import Principal "mo:core/Principal";
import OQL       "mo:caffeineai-oql";
import Expose    "mo:caffeineai-oql/Expose";
// 解析器模块，顶层导入（见"导入"部分）。此应用在Nat / Text / Principal字段记录上推导Map实体：
import MapEntity      "mo:caffeineai-oql/MapEntity";
import Entity         "mo:caffeineai-oql/Entity";
import RecordValue    "mo:caffeineai-oql/RecordValue";
import NatValue       "mo:caffeineai-oql/NatValue";
import TextValue      "mo:caffeineai-oql/TextValue";
import PrincipalValue "mo:caffeineai-oql/PrincipalValue";

actor {
  type Product  = { id : Nat; name : Text; priceUsd : Nat };
  type Vendor   = { id : Nat; name : Text };
  type AuditLog = { id : Nat; action : Text; atNs : Nat };
  type Note     = { id : Nat; user : Principal; body : Text };
  type Document = { id : Nat; owner : Principal; title : Text; ciphertext : Text };
  type User     = { id : Principal; isAdmin : Bool };

  let products  : Map.Map<Nat, Product>;
  let vendors   : Map.Map<Nat, Vendor>;
  let supplies  : Map.Map<Product, Vendor>;
  let auditLogs : Map.Map<Nat, AuditLog>;
  let notes     : Map.Map<Nat, Note>;
  let documents : Map.Map<Nat, Document>;
  // 如果不需要，则不是所有集合都需要暴露——`users`仅支持认证，因此故意不将其转换为实体
  let users     : Map.Map<Principal, User>;

  transient let anyP = Principal.fromText("aaaaa-aa");   // 样本所有者；值被忽略

  // 查找调用者是否是管理员。
  func isAdmin(p : Principal) : Bool =
    switch (users.get(p)) { case (?u) u.isAdmin; case null false };

  // 自定义`.ownedByWith`规则：管理员可以看到所有文档，其他人只能看到自己的。`owner`是字段的Value——一个Principal列作为#text到达。
  func canSeeDocument(caller : Principal, owner : OQL.Value) : Bool =
    isAdmin(caller) or owner == #text(caller.toText());

  include Expose({
    entities = [
      // #public_ — 任何人，包括匿名用户，都可以读取整个目录
      products.toEntity("product", "Product", "id")
        .sample({ id = 0; name = ""; priceUsd = 0 })
        .public_()
        .build(),
      vendors.toEntity("vendor", "Vendor", "id")
        .sample({ id = 0; name = "" })
        .public_()
        .build(),
      // `supplies : Map<Product, Vendor>`——两个非基本类型之间的映射。
      // 身份存在于键/值记录中，而不是字段中，因此在手动模式下迭代`.entries()`，提升每侧的id，并`.edge`两者——然后查询可以遍历"product.name"和"vendor.name"。
      OQL.Entity.manual<(Product, Vendor)>("supply", func () = supplies.entries(), "Supply", "key")
        .sample(({ id = 0; name = ""; priceUsd = 0 }, { id = 0; name = "" }))
        .payload("key",     func ((p, v)) = p.id.toText() # ":" # v.id.toText())
        .payload("product", func ((p, _)) = p.id) .edge("product", "product")
        .payload("vendor",  func ((_, v)) = v.id) .edge("vendor",  "vendor")
        .controllerOnly()
        .build(),
      // #controllerOnly（默认）—— 仅平台可读取
      auditLogs.toEntity("auditLog", "AuditLog", "id")
        .sample({ id = 0; action = ""; atNs = 0 })
        .controllerOnly()
        .build(),
      // #scopedPerUser — 每个已登录的用户只读取自己的行
      notes.toEntity("note", "Note", "id")
        .sample({ id = 0; user = anyP; body = "" })
        .ownedBy("user")
        .scopedPerUser()
        .build(),
      // #controllerOrScoped — 控制器读取所有；用户读取使用`canSeeDocument`。
      // `.hidden` — 透明列不在模式中+默认投影
      documents.toEntity("document", "Document", "id")
        .sample({ id = 0; owner = anyP; title = ""; ciphertext = "" })
        .hidden("ciphertext")
        .ownedByWith("owner", canSeeDocument)
        .controllerOrScoped()
        .build(),
    ];
  });
}
```

迁移链头部：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";

module {
  type Product  = { id : Nat; name : Text; priceUsd : Nat };
  type Vendor   = { id : Nat; name : Text };
  type AuditLog = { id : Nat; action : Text; atNs : Nat };
  type Note     = { id : Nat; user : Principal; body : Text };
  type Document = { id : Nat; owner : Principal; title : Text; ciphertext : Text };
  type User     = { id : Principal; isAdmin : Bool };

  type NewActor = {
    products  : Map.Map<Nat, Product>;
    vendors   : Map.Map<Nat, Vendor>;
    supplies  : Map.Map<Product, Vendor>;
    auditLogs : Map.Map<Nat, AuditLog>;
    notes     : Map.Map<Nat, Note>;
    documents : Map.Map<Nat, Document>;
    users     : Map.Map<Principal, User>;
  };

  public func migration(_old : {}) : NewActor {
    {
      products  = Map.empty<Nat, Product>();
      vendors   = Map.empty<Nat, Vendor>();
      supplies  = Map.empty<Product, Vendor>();
      auditLogs = Map.empty<Nat, AuditLog>();
      notes     = Map.empty<Nat, Note>();
      documents = Map.empty<Nat, Document>();
      users     = Map.empty<Principal, User>();
    };
  };
};
```

## Auth

授权是**按实体**的——每个构建器声明一个级别，`schema()`和`execute()`都针对实时`caller`运行检查。没有应用范围的配置，没有令牌。未设置时默认为`#controllerOnly`。

| 构建器调用 | 谁读取 | 返回的行
|---|---|---|
| `.public_()` | 任何人（包括匿名用户） | 所有
| `.controllerOnly()` *(默认)* | 仅控制器 | 所有
| `.scopedPerUser()` | 任何已登录的调用者 | 仅调用者自己的
| `.controllerOrScoped()` | 控制器+已登录的调用者 | 控制器：所有；用户：自己的

### 选择级别

根据谁应该读取其行来为每个实体选择——如有疑问，请保持默认。

- **`.controllerOnly()`** *(默认)* — 应用数据，代理应回答，但用户不直接读取（订单、指标、审计日志、配置）。代理作为控制器调用，因此它读取所有内容，而数据对用户保持私密。
- **`.public_()`** — 任何人可读的数据，包括未登录的访客（公共目录、发布内容、排行榜）。
- **`.controllerOrScoped()`** — 每个用户只读取自己的行，但代理仍必须回答聚合问题（个人资料、用户的订单）。需要所有者列。
- **`.scopedPerUser()`** — 严格按用户私有的数据：每个用户只读取自己的，代理也受限制，因此它**不能**回答此表的查询（私信、私人日记）。需要所有者列——除非代理必须对其盲目的，否则优先使用`.controllerOrScoped()`。

用户可以覆盖每个实体；如果请求暗示按用户数据，但存在歧义，请询问。

### 按用户（行级）范围

范围级别（`.scopedPerUser()`、`.controllerOrScoped()`）需要一个方法来知道哪些行属于调用者——一个**所有者列**或一个尊重主体的源。`.build()`如果范围实体没有两者之一就会捕获，并且如果`.public_()`实体声明了所有者（检查永远不会运行），也会捕获。这是防止常见数据泄露陷阱的护栏。

**何时标记**：`Principal`字段是信号。

- `.ownedBy(field)` — 字段*就是*所有者；可见性是身份相等。
- `.ownedByWith(field, canSee)` — 自定义可见性（团队、管理员、共享）。`canSee : (caller : Principal, owner : Value) -> Bool` 决定每行；`field`不必是`Principal`，闭包可以读取演员状态。

范围调用者只看到其拥有的行——既作为查询目标，也通过连接——因此遍历永远不会泄露另一个所有者的行。

```mo
// 按用户笔记：每个已登录的用户只读取自己的行。
notes.toEntity("note", "Note", "id")
  .sample({ id = 0; owner = Principal.fromText("aaaaa-aa") /* 任何principal */; body = "" })
  .ownedBy("owner")
  .scopedPerUser()
  .build()

// `.ownedByWith`自定义规则：所有者看到自己的文档，列出的管理员看到所有人的，平台控制器看到所有（#controllerOrScoped）。
// `owner`是字段的Value——一个Principal列作为#text(principal)到达。
docs.toEntity("doc", "Doc", "id")
  .sample({ id = 0; owner = Principal.fromText("aaaaa-aa"); title = "" })
  .ownedByWith("owner", func (caller, owner) =
    admins.get(caller) != null or owner == #text(caller.toText()))
  .controllerOrScoped()
  .build()
```

在范围调用者看到**哪些**行时，`.viewWith(view)`决定它以**什么形状**看到它们——一个按主题的遮罩，仅在所有权检查已经承认的行上运行：

```mo
// 所有人看到自己的预订；这里不需要在自己的行上看到确切的金额——但为非共享日历的所有者粗化联系字段，例如：
bookings.toEntity("booking", "Booking", "id")
  .sample({ id = 0; calendarId = 0; contact = "" })
  .ownedByWith("calendarId", canSeeCalendar)
  .viewWith(func (subject, b) = if (isOwner(subject, b)) b else { b with contact = "" })
  .scopedPerUser()
  .build()
```

`view : (subject : Principal, row : T) -> T` 重新塑造了类型的行；整个查询管道（包括过滤器）评估了**已查看**的行，因此谓词永远不会探测视图隐藏的值。视图仅针对范围主题运行——`.viewWith`与`.public_()`搭配会在`.build()`时捕获（不受限制的读取始终看到原始行）。

`.ownedBy(f)`正好是`.ownedByWith(f, OQL.Entity.ownerIsCaller)`。最多一个所有者列；它必须是一个真实字段，而不是`.edge` / `.hidden`。对于所有者键存储（`Map<Principal, List<T>>`）使用`OQL.Entity.newScoped(name, scopedIter, typeName, primaryKey)`，以便扫描是O(user rows)：`scopedIter(?p)`只返回`p`的行，`scopedIter(null)`返回所有（模式播种）。

## 实体构建器

两种模式，由行类型`T`选择。

### 自动推导——`.toEntity`

对于所有字段都是基本类型且具有内置的`_toRow`（`Nat`、`Int`、`Float`、`Text`、`Bool`、定长的`Nat`/`Int`宽度、`Principal`）的记录：

```mo
customers.toEntity(name, typeName, primaryKey)
  .sample(template)              // 必须调用——空集合+无样本→空模式
  .edge(field, targetEntity)     // 将现有字段标记为外键
  .ownedBy(field)                // (或`.ownedByWith(field, canSee))`按用户范围
  .scopedPerUser()               // 授权级别：.public_ / .controllerOnly（默认） / .scopedPerUser / .controllerOrScoped
  .hidden(field)                 // 透明/敏感——从模式+默认投影中删除
  .build()
```

- `.toEntity`是`OQL.Entity.new<T>(name, func () = coll.values(), …)`的糖；它存在于`Map`、`Set`、`List`、`[T]`和`[var T]`。它迭代**值**仅——如果行的身份（PK或所有者）存在于*Map键*中，则它不是字段：通过手动模式在`.entries()`上提升它，或者当它是所有者时使用`OQL.Entity.newScoped`。
- `primaryKey`，以及任何`.edge` / `.ownedBy`字段，必须命名行的真实、非`.hidden`列。
- `.edge(name, target)`将**现有**字段（它不会添加一个）标记为外键，启用查询中的点路径遍历`"name.targetField"`。外键/PK类型必须是`Text`、`Nat`/`Int`或`Bool`（拒绝`Float`键），并且目标的主键不能是`.hidden`。
- **边缘目标必须是此canister中`Expose`注册的实体**。到缺失实体的边缘（拼写错误，或到另一个canister的外键）会静默地从`schema()`中删除整个字段——列仍然存储和过滤，但无法由模式驱动的客户端发现。跨canister外键应作为普通payload字段，而不是`.edge`。
- `.sample(template)`播种模式发现。始终调用它；没有它，空集合将产生空模式（`fields: []`）。只有形状重要，值不重要。
- `.hidden(name)`从模式+默认投影中删除可推导字段；它**不会**跳过`_toRow`——不支持的字段类型仍然需要手动模式或`<Type>Value`。

模式字段按**字典顺序**（`__record`组合器的规范形式）列出；如果显示顺序重要，请在客户端排序。

### 手动模式——`.toEntityManual` / `OQL.Entity.manual`

对于非记录`T`、计算字段或具有嵌套/变体/选项/集合字段的记录：

```mo
// 必须的，本文件顶层 — `.payload` / `.flatten` 是通过接收者表示法可达的实体
// 函数，而不是构建器中的字段：
import Entity "mo:caffeineai-oql/Entity";

authors.toEntityManual<Author>("author", "Author", "id")
  .sample({ id = 0; name = ""; address = { street = ""; city = "" }; tags = [] })
  .payload("name", func a = a.name)        // 一个字段；提取返回一个 _toRow 值
  .flatten(func a = a.address)             // 将嵌套记录的字段拆分为列
  .payload("tagCount", func a = a.tags.size())
  // .edge tags a 声明的列；.hidden 删除你已经通过
  // `.payload` / `.flatten` 添加的字段 — 不添加字段
  .build()
```

**`field payload` 在类型 `Builder<…>` 中不存在 (M0072) 意味着上面缺少 `Entity`
导入 — 它永远不会是包版本问题。** `.payload` 和 `.flatten` 自 0.1.0 起
就是 `Entity` 函数；添加不同 `caffeineai-oql` 版本的 `mops add` 不会修复此错误。
导入 `mo:caffeineai-oql` 不够，通过 `OQL.Entity.…` 重新导出模块也无法解决：
接收者表示法针对 **顶层导入** 解析，所以调用 `OQL.Entity.manual(...).payload(...)`
的文件仍然需要自己的 `import Entity "mo:caffeineai-oql/Entity";`。与 `.toEntity`
不同，此失败不会提供“您是否想导入…？”提示。

- `.payload(name, extract)` — `name` 不能包含 `.`。优先使用
  `func r = r.field` (让 Motoko 推断；避免冗余注解)。对于选项/变体，返回
  `Text`/`Nat` 并带哨兵（见下文）。
- `.flatten(extract : T -> S)` — `S` 必须是扁平的；它的每个字段都成为顶级列。
  使用 `.hidden` 删除不需要的。名称冲突会得到 `__1`，`__2` 后缀（不会删除任何内容）。
- `OQL.Entity.manual<T>(name, iter, typeName, primaryKey)` 用于任意行源
  (自定义拆分器，过滤迭代器)。始终链式 `.sample(...)` 并用一个类型为 `T` 的
  虚拟行。限定调用通过 `OQL` 导入解析，但连接到其结果的任何 `.payload` /
  `.flatten` 仍然需要顶层 `Entity` 导入。

`OQL.Value` 是 `{ #null_; #bool; #nat; #int; #float; #text }`。数值变体相互比较，
所以 JSON 整数阈值与 `Float` 值匹配。

| 行类型 `T` | 模式 |
|---|---|
| 所有原始记录 | `.toEntity` |
| 包含 `?` / 变体 / 嵌套字段的记录 | 一旦你发布 `<Type>Value.mo>` (下方)；否则手动 |
| 包含集合字段的记录 | 手动 — `.size()` 或 `Text.join` 到 payload |
| 元组 / 原始 / 计算值 | 手动 |

## 转换非原始字段

为了保持记录在自动派生路径上，给每个非原始字段类型一个 `_toRow : T -> OQL.Value`：
每个类型一个文件 `<TypeName>Value.mo`，一个 `public func _toRow`，在声明实体的文件中
**顶层**导入 — 与内置值模块相同的顶层规则（见 `## Setup` → 导入）；
解析器不会遍历子模块。父记录然后通过 `.toEntity(...)` 链式，无需每个字段的 `.payload`。

```mo
// OptTextValue.mo — 选项 → 哨兵
module { public func _toRow(self : ?Text) : OQL.Value =
  switch self { case null { #text("") }; case (?t) { #text(t) } }; };

// StatusValue.mo — 变体 → 标签文本
module { public func _toRow(self : Status) : OQL.Value =
  #text(switch self { case (#draft) "draft"; case (#published) "published" }); };

// DepartmentValue.mo — 嵌套记录 → 子主键 (然后 .edge 字段)
module { public func _toRow(self : Department) : OQL.Value = #text(self.name); };
```

**始终返回一个 `Value` 变体**，即使为空（哨兵 `""` / `0` / `false`）— 一个
`_toRow` 有时返回 `#null_` 会使报告的模式类型按行顺序翻转。哨兵使字段可查询
(`eq value ""` 匹配空值)。对于一次性字段，在 `.payload` 中内联相同的转换，
而不是模块；只有当 2+ 实体需要时才将其提升到模块。
一个既用作实体又用作嵌套字段的记录只需发布其 `<Type>Value.mo>` — 结构
`Row` 派生和您的 `Value` 折叠是不同的类型，可以共存。

## 超越每行一个记录的实体模式

相同的存储可以支持多个实体 — 选择客户端应看到的内容：

- **reshaped** — 将 `Map<K1, Map<K2, V>>` 拆分为行；让拆分器发出
  扁平的 **记录** (而不是元组)，这样它仍然自动派生，然后 `.edge` 提升的键。
- **enumerated** — 通过 `Map<Author, …>.keys()` 派生实体，使用
  `OQL.Entity.manual`；没有行的条目简单地不会出现。
- **synthetic** — 从数组字段投影一个连接，使两边都可以进行多对多查询：

```mo
OQL.Entity.manual<(Article, Text)>("articleTag", func () = flattenTags(articles), "Pair", "pair")
  .sample(({ id = 0 }, ""))
  .payload("article", func ((a, _)) = a.id) .edge("article", "article")
  .payload("tag",     func ((_, t)) = t)    .edge("tag", "tag")
  .build()
```

## 更大的数据 — `OQL.Table`

对于预期会增长的大型表（数万行及以上 — 事件、交易、日志、导入的数据集），将其存储在 `OQL.Table` 中。它扩展远超堆集合所能容纳的范围；行按追加位置键值。

声明一个涉及三个决策 — **列、索引、行函数**：

```motoko filepath=src/backend/tables_demo.mo
import OQL    "mo:caffeineai-oql";
import Expose "mo:caffeineai-oql/Expose";
import Entity "mo:caffeineai-oql/Entity";   // 构建器链 — 始终导入
import Table  "mo:caffeineai-oql/Table";

actor {
  type Event = { kind : Nat; amount : Nat; note : Text };

  // 决策 1 + 2 (列、索引) 在 `Table.new` 运行时固定 —
  // 迁移链入口下方
  let events : Table.Table;

  // 3. 行函数：你的记录 → 每个列一个 (名称, Value)，名称匹配。
  func eventRow(e : Event) : [(Text, OQL.Value)] =
    [("kind", #nat(e.kind)), ("amount", #nat(e.amount)), ("note", #text(e.note))];

  // 写入：返回的位置是行的主键。
  // 修改是删除 + 追加。
  public func addEvent(e : Event) : async Nat {
    Table.append(events, e, eventRow);
  };

  // 必须的：在 `Expose` 混合中注册表的实体 — `schema()` 和
  // `execute()` 只看到已注册的内容；不在列表中的表存在但对每个查询不可见。
  // 同样的列表，相同的授权级别，以及到其他实体的外键边，与任何实体相同。
  // `entity` 默认将类型名称设置为实体名称，主键设置为 "id"；
  // `entityWith(events, "event", "Event", "id")` 覆盖其中之一。
  include Expose({
    entities = [
      Table.entity(events, "event").public_().build(),
      // ... 应用程序的其他实体 ...
    ];
  });
};
```

`Table.new` 在引入表的迁移链入口运行：

<!-- motoko-check:skip -->
```motoko
import Table "mo:caffeineai-oql/Table";

module {
  public func migration(_old : {}) : { events : Table.Table } {
    {
      // 1. 列： (名称, 类型) 对。顺序很重要，集合在表的整个生命周期中是固定的。
      // 类型：#nat / #int / #float / #bool (64 位单元格) + #text。
      // 2. 索引：查询将过滤或排序的列 —
      //    #hash 用于相等，#ordered 用于范围 / orderBy。
      events = Table.new(
        [("kind", #nat), ("amount", #nat), ("note", #text)],   // 列
        [("kind", #hash), ("amount", #ordered)],               // 索引
      );
    };
  };
};
```

重要的规则：

- **模式一旦数据刷新后就固定** — 不能添加、删除或重类型列；不同的形状意味着新的表。
- **值类型必须等于列类型** — 不匹配会在 `append` 时大声捕获，而不是存储损坏的单元格；
  数值单元格是 64 位的。
- **将要批量加载数据的表声明时没有索引** — 加载后建立索引（下一节）。
- **`Table` 只能通过 `Expose` 中的实体进行查询** — 单独声明表只存储数据而不暴露任何内容；
  `schema()` / `execute()` 看到的正是 `entities` 列表。

除了索引的作用外，`Table` 直接从段统计回答整列的 **`sum` / `avg`** —
在表大小中扁平 — 并且只读取查询触及的列。

## 批量上传 (`ImportData`) — 将现有数据加载到 `Table`

当用户的数据已经存在（来自电子表格的 CSV 导出或应用程序替换的系统），
不要通过 `append` 慢慢传输 — 包含 `ImportData` 混合，并作为预构建的 **段图像** 加载：
加载器在链下以刷新段的字节布局方式布置行，然后可以器器验证并复制字节，所以一条消息的成本是 O(列) 而不是 O(行)，并且堆在整个过程中保持扁平。

```motoko filepath=src/backend/bulk_load_demo.mo
import Expose     "mo:caffeineai-oql/Expose";
import Entity     "mo:caffeineai-oql/Entity";   // 构建器链 — 始终导入
import Table      "mo:caffeineai-oql/Table";
import ImportData "mo:caffeineai-oql/ImportData";

actor {
  // 加载时声明表无索引 — `loadSegment` 在声明索引的表上捕获
  // (一个缺少加载行的就绪索引会静默欠载)。索引在加载后后台构建。
  // 在引入它的迁移链入口中构造：
  //   events = Table.new([("kind", #nat), ("amount", #nat), ("note", #text)], []);
  let events : Table.Table;

  include Expose({
    entities = [
      Table.entity(events, "event").public_().build(),
      // ... 应用程序的其他实体 ...
    ];
  });
  include ImportData([ events.importTarget("event") ]);
};
```

混合添加 **仅控制器** 端点 (`layout`, `rows`, `putSegment`, `importFlush`, `buildIndex`, `indexStatus`) —
图像的统计信息是可信答案，所以加载表面属于可以安装代码的**主体**。

**运行加载器。** 该工具在 `scripts/` 中附带此技能 — 纯 Node (≥ 20)，
**无需安装依赖**；每个调用都通过 `icp canister call`，所以必须设置 icp-cli：

```bash
node <此技能的目录>/scripts/ingest.mjs \
  --canister <canister-id> --target event --file events.csv \
  -e ic --index kind:hash
```

- `--target` 是在可器器中声明的 `importTarget` 名称；可器器的 `layout()` 是模式权威 —
  CSV 标头按名称与列匹配，所以文件列顺序无关紧要（忽略 CSV 列；文件中缺少声明的列是错误）。
- 连接标志传递给 icp-cli，与其他可器器调用相同的方式工作：`-e <environment>` (`-e ic` 对于已部署的应用程序)，
  `-n <network>`，`--identity <name>` (默认：您当前的)。
  端点是**仅控制器**，所以身份必须是可器器的**控制器**。
  没有它们，您的 icp 默认适用 — 可器器名称然后针对项目的默认环境解析，所以从应用程序的项目目录运行该工具。
- `--index col:kind` (可重复，`kind` = `hash`) 在加载行后链下构建该列的索引。
  对于它无法构建的任何内容 (`#ordered`，复合)，通过混合的端点链式构建：`icp canister call <id> buildIndex '("event", vec {"kind"},
  variant {hash})'` — 查询正确扫描（只是更慢）直到构建完成，然后索引服务；
  `indexStatus '("event")'` 报告进度。
- 以与客户端将读取相同的方式验证加载：
  `icp canister call <id> execute '("{\"start\":\"event\",\"aggregate\":[{\"fn\":\"count\"}]}")' --query`
  必须返回 CSV 的行数。
- CSV 单元格按声明类型解码。未加引号的空字段是**空单元格**；在 `#text` 列中加引号的 `""` 是空字符串；
  `#bytes(w)` 列的字段是**base64**，必须解码为恰好 `w` 字节。
- **重新运行相同的命令会继续**：表已持有的行会被跳过，并且 `putSegment` 的
  `expect-first-row` 守护将任何双发送转换为大声捕获而不是重复的行。

**操作规则** (违反会大声拒绝而不是损坏)：

1. **在应用程序开始写入之前完全完成第一次加载 — 数据和索引**。如果写入在加载中途发生，
   重新运行无法完成索引；在可器器中用 `buildIndex` 重建它（较慢，始终有效）。
2. **加载和写入交替进行**。加载之间应用程序可以自由写入；下一个相同命令的运行
   挑战增长作为增量加载，无需准备。
3. **一次不能两者同时进行** — 可器器拒绝，它不会错误回答。
4. **查询在整个过程中保持工作**，包括加载中；一个索引仍在上传的列会扫描直到完成。

## 清单

- [ ] 在第一个导入的同一批次中 `mops add caffeineai-oql@0.7.0`
- [ ] 顶层导入解析器模块 (见 `## Setup` → 导入)：`Entity`
      (**始终** — 每个构建器方法包括 `.payload` / `.flatten` 通过它解析)，集合模块 (`MapEntity` / …)，以及
      `RecordValue` + 每个自动派生记录的原始字段类型的 `<Type>Value`
- [ ] 每个实体：行迭代器存在；`.toEntity` (所有原始) 或
      `.toEntityManual` / `OQL.Entity.manual` 否则
- [ ] `<Type>Value.mo` 对于跨实体重用的每个非原始字段，顶层导入
- [ ] 每个`.toEntity` / `Entity.manual` 链式上的 `.sample(template)` (虚拟值可以)
- [ ] FK 字段 `.edge(name, target)`；不透明/敏感自动派生字段
      `.hidden(name)` (手动：通过没有 `.payload` 或仅添加 `.hidden` 的列来省略)
- [ ] 每个哨兵转换返回一个 `Value` 变体
- [ ] 每个用户实体使用 `.ownedBy` / `.ownedByWith` **和** 一个作用域级别
      (`.scopedPerUser()` / `.controllerOrScoped()`) — 从不 `.controllerOnly()`
- [ ] 大型、追加为主的表 → `OQL.Table`；将句柄保存在持久字段中并通过迁移传递
- [ ] 现有数据集导入 → 声明表**无索引**，添加 `ImportData([t.importTarget(name)])`，
  用 `scripts/ingest.mjs` 加载，加载后建立索引 (`--index` 或 `buildIndex`) —
  数据和索引在**应用程序开始写入之前**完成
