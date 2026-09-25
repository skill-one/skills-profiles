# OQL — 对象查询层

遍历实体的字段（非瞬态字段），对于每个值得查询的集合，考虑其数据如何映射到数据库中的**表**（*实体*）。你每个表只声明一个实体——`Expose`混入使得它们可查询。

# 后端

每个实体都携带一个授权级别；默认的`.controllerOnly()`是安全的（仅用户可见，Data Intelligence代理仍然可读取）。首先建模实体，然后为每个实体选择一个级别——参见`## Auth`。

## 设置

在**相同的写批次**中运行`mops add caffeineai-oql@0.7.0`作为你的第一个`mo:caffeineai-oql/...`导入。自动推导需要`moc >= 1.11`（生成的应用模板已经满足此条件）。

### 构建标志

`--default-persistent-actors`是强制性的。`--implicit-package=core`是可选的便利性；每个代码片段和源文件都必须导入它使用的`mo:core`模块。如果应用使用`OQL.Table`并且需要超过4 GiB的`Region`，请添加`--max-stable-pages 1638400`；依赖项自己的标志不会应用于依赖它的项目，因此必须在应用自己的构建中设置。

### 导入——每个解析器模块一个

`.toEntity`、构建链（`.sample` / `.build` / `.public_` / …）和记录`_toRow`推导从**在声明实体的文件中顶层导入**的模块解析——解析器不会遍历子模块，因此只导入`mo:caffeineai-oql`是不够的。导入你的代码使用的确切解析器模块：

- `mo:caffeineai-oql/Entity` — 总是（`.sample` / `.build` / `.edge` / `.ownedBy` / auth-level 构建链，以及`.payload` / `.flatten`在手动模式下）。
- 每个`.toEntity` / `.toEntityManual`接收者的集合模块——`MapEntity`、`SetEntity`、`ListEntity`、`ArrayEntity`或`VarArrayEntity`。
- 对于每个**自动推导**（`.toEntity`）记录：`RecordValue`，以及每个原始字段类型`<Type>Value`——`NatValue`、`TextValue`、`PrincipalValue`、`BoolValue`、`IntValue`、`FloatValue`、定长的`Nat`/`Int`宽度、`BlobValue`。手动`.payload`返回类型需要它们的`<Type>Value`；仅手动实体不需要`RecordValue`。

当集合模块缺少编译器名称时——*"字段`toEntity`不存在…你是否想导入`mo:caffeineai-oql/MapEntity`?"*——添加命名的导入。缺少`Entity`导入不会得到这样的提示：它表现为一个裸的*"类型`Builder<…>`中不存在字段`payload`"*（M0072）。将任何`field <builderMethod>不存在`错误视为缺少此列表的顶层导入，永远不会将其视为错误的包版本。

## 声明实体并安装

`.toEntity(name, typeName, primaryKey)`将记录集合转换为可查询的实体；编译器自动推导字段。每个实体设置自己的授权级别（参见`## Auth`）；下面的示例显示了每个级别一个表。`Expose`只添加OQL查询方法（`schema` / `execute`）——你的现有状态、类型和`shared`方法保持不变。

- 在每个`.toEntity` / `Entity.manual`链上始终调用`.sample({...})`；虚拟值可以。空集合+没有样本→空模式（`fields: []` / `"record { }"`）。

```motoko filepath=src/backend/sample_required.mo
include Expose({ entities = [tasks.toEntity("task", "Task", "id").sample({ id = 0; title = "" }).public_().build()] })
```

```motoko filepath=src/backend/main.mo
import Map       "mo:core/Map";
import Nat       "mo:core/Nat";
import Principal "mo:core/Principal";
import OQL       "mo:caffeineai-oql";
import Expose    "mo:caffeineai-oql/Expose";
// 解析器模块，顶层导入（见"导入"部分）。此应用从记录的`Nat` / `Text` / `Principal`字段推导出`Map`实体：
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
  // 如果不需要，不是所有集合都需要暴露——`users`仅支持认证，因此故意不将其转换为实体
  let users     : Map.Map<Principal, User>;

  transient let anyP = Principal.fromText("aaaaa-aa");   // 样本所有者；值被忽略

  // 查找调用者是否是管理员。
  func isAdmin(p : Principal) : Bool =
    switch (users.get(p)) { case (?u) u.isAdmin; case null false };

  // 自定义`.ownedByWith`规则：管理员可以看到所有文档，其他人只能看到自己的。`owner`是字段的`Value`——`Principal`列作为`#text`到达。
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
      // `supplies : Map<Product, Vendor>` — 两个非原始类型的映射。
      // 身份存在于键值记录中，而不是字段中，因此手动模式下迭代`.entries()`，提升双方`id`，并`.edge`双方——然后查询可以遍历"product.name"和"vendor.name"。
      OQL.Entity.manual<(Product, Vendor)>("supply", func () = supplies.entries(), "Supply", "key")
        .sample(({ id = 0; name = ""; priceUsd = 0 }, { id = 0; name = "" }))
        .payload("key",     func ((p, v)) = p.id.toText() # ":" # v.id.toText())
        .payload("product", func ((p, _)) = p.id) .edge("product", "product")
        .payload("vendor",  func ((_, v)) = v.id) .edge("vendor",  "vendor")
        .controllerOnly()
        .build(),
      // #controllerOnly（默认，此处明确显示）——仅平台可读取
      auditLogs.toEntity("auditLog", "AuditLog", "id")
        .sample({ id = 0; action = ""; atNs = 0 })
        .controllerOnly()
        .build(),
      // #scopedPerUser — 每个登录用户只读取自己的行
      notes.toEntity("note", "Note", "id")
        .sample({ id = 0; user = anyP; body = "" })
        .ownedBy("user")
        .scopedPerUser()
        .build(),
      // #controllerOrScoped — 控制器读取所有；范围读取使用`canSeeDocument`。
      // `.hidden` — 不透明列在模式中缺失+默认投影
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

授权是**按实体**的——每个构建器声明一个级别，并且`schema()`和`execute()`都针对实时`caller`运行检查。没有应用范围的配置，没有令牌。当未设置时，默认为`#controllerOnly`。

| 构建器调用 | 谁读取 | 返回的行 |
|---|---|---|
| `.public_()` | 任何人（包括匿名用户） | 所有 |
| `.controllerOnly()` *(默认)* | 仅控制器 | 所有 |
| `.scopedPerUser()` | 任何登录调用者 | 只有自己的 |
| `.controllerOrScoped()` | 控制器+登录调用者 | 控制器：所有；用户：自己的 |

### 选择级别

根据谁应该读取其行来为每个实体选择——如有疑问，请保持默认。

- **`.controllerOnly()`** *(默认)* — 私有应用数据，代理应该回答的，但用户不会直接读取（订单、指标、审计日志、配置）。代理以控制器身份调用，因此它读取所有数据，而数据对用户保持私有。
- **`.public_()`** — 任何人可读的数据，包括注销的访客（公共目录、已发布内容、排行榜）。
- **`.controllerOrScoped()`** — 每个用户只读取自己的行，但代理仍然必须回答聚合问题（个人资料、用户的订单）。需要所有者列。
- **`.scopedPerUser()`** — 严格每用户私有数据：每个用户只能读取自己的，并且代理也受范围限制，因此**不能**回答此表的任何问题（私信、私人日记）。需要所有者列——除非代理必须对其盲目的，否则优先使用`.controllerOrScoped()`。

用户可以覆盖每个实体；如果请求暗示每用户数据但存在歧义，请询问。

### 每用户（行级）范围

范围级别（`.scopedPerUser()`、`.controllerOrScoped()`）需要一个方法来知道哪些行属于调用者——一个**所有者列**或尊重主体的源。`.build()`如果范围实体没有两者，就会捕获，并且如果`.public_()`实体声明了所有者（检查永远不会运行），也会捕获。这是防止常见数据泄露脚本的防护栏。

**何时标记：** `Principal`字段是信号。

- `.ownedBy(field)` — 字段*就是*所有者；可见性是身份相等。
- `.ownedByWith(field, canSee)` — 自定义可见性（团队、管理员、共享）。`canSee : (caller : Principal, owner : Value) -> Bool` 决定每行；`field`不必是`Principal`，并且闭包可以读取演员状态。

范围调用者只能看到自己拥有的行——既作为查询目标，也通过连接——因此遍历永远不会泄露另一个所有者的行。

```mo
// 每用户笔记：每个登录用户只能读取自己的行。
notes.toEntity("note", "Note", "id")
  .sample({ id = 0; owner = Principal.fromText("aaaaa-aa") /* 任何principal */; body = "" })
  .ownedBy("owner")
  .scopedPerUser()
  .build()

// `.ownedByWith`自定义规则：所有者可以看到自己的文档，列出的管理员可以看到所有人的，平台控制器可以看到所有（`#controllerOrScoped`）。
// `owner`是字段的`Value`——`Principal`列作为`#text(principal)`到达。
docs.toEntity("doc", "Doc", "id")
  .sample({ id = 0; owner = Principal.fromText("aaaaa-aa"); title = "" })
  .ownedByWith("owner", func (caller, owner) =
    admins.get(caller) != null or owner == #text(caller.toText()))
  .controllerOrScoped()
  .build()
```

在决定**哪些**行一个范围调用者可以看到时，`.viewWith(view)`决定它以**什么形状**看到它们——一个针对主体的每主题红action，它只在所有权检查已经允许的行上运行：

```mo
// 所有人都看到自己的预订；在此处不需要自己的行上的确切金额——但可以缩小非所有者共享日历的联系人字段，例如：
bookings.toEntity("booking", "Booking", "id")
  .sample({ id = 0; calendarId = 0; contact = "" })
  .ownedByWith("calendarId", canSeeCalendar)
  .viewWith(func (subject, b) = if (isOwner(subject, b)) b else { b with contact = "" })
  .scopedPerUser()
  .build()
```

`view : (subject : Principal, row : T) -> T` 重新塑造类型的行；整个查询管道（包括过滤器）都会评估看到的行，因此谓词永远不会探测视图隐藏的值。视图仅针对范围主题运行——将`.viewWith`与`.public_()`搭配使用会在`.build()`时捕获（不受限制的读取始终看到原始行）。

`.ownedBy(f)`正好是`.ownedByWith(f, OQL.Entity.ownerIsCaller)`。最多一个所有者列；它必须是一个真实字段，而不是`.edge` / `.hidden`。对于所有者键存储（`Map<Principal, List<T>`），使用`OQL.Entity.newScoped(name, scopedIter, typeName, primaryKey)`以便扫描是O(user rows)：`scopedIter(?p)`只返回`p`的行，`scopedIter(null)`返回所有（模式种子）。

## 超越每记录一行实体

相同的存储可以支持多个实体——选择客户端应该看到的内容：

- **重塑** — 将`Map<K1, Map<K2, V>`扁平化为行；让扁平化器发出一个平面的**记录**（而不是元组），这样它仍然可以自动推导，然后`.edge`提升的键。
- **枚举** — 通过索引键（`Map<Author, …>.keys()`）使用`OQL.Entity.manual`推导实体；没有行的条目简单地不会出现。
- **合成** — 从数组字段投影一个连接，以便从双方都可以将许多对多查询：

```mo
OQL.Entity.manual<(Article, Text)>("articleTag", func () = flattenTags(articles), "Pair", "pair")
  .sample(({ id = 0 }, ""))
  .payload("article", func ((a, _)) = a.id) .edge("article", "article")
  .payload("tag",     func ((_, t)) = t)    .edge("tag", "tag")
  .build()
```

## 更大数据 — `OQL.Table`

对于预期会增长很大的表（数万行以上——事件、交易、日志、导入的数据集），将其存储在`OQL.Table`中。它比堆集合扩展得更远；行由它们的追加位置键值。

声明一个有三个决策——**列、索引、行函数**：

```motoko filepath=src/backend/tables_demo.mo
import OQL    "mo:caffeineai-oql";
import Expose "mo:caffeineai-oql/Expose";
import Entity "mo:caffeineai-oql/Entity";   // 构建器链——始终导入
import Table  "mo:caffeineai-oql/Table";

actor {
  type Event = { kind : Nat; amount : Nat; note : Text };

  // 决策1 + 2（列、索引）在`Table.new`运行的地方是固定的——
  // 迁移链条目在下面
  let events : Table.Table;

  // 3. 行函数：你的记录→每个列的（名称, Value）一个，名称匹配。
  func eventRow(e : Event) : [(Text, OQL.Value)] =
    [("kind", #nat(e.kind)), ("amount", #nat(e.amount)), ("note", #text(e.note))];

  // 写入：返回的位置是行的主键。
  // 修改是删除+追加。
  public func addEvent(e : Event) : async Nat {
    Table.append(events, e, eventRow);
  };

  // 必须注册表实体在Expose混入中——`schema()`和`execute()`只看到注册了什么；不在该列表中的表存在但对每个查询都不可见。相同的列表、相同的授权级别，以及到其他实体的FK边缘，与任何实体一样。`entity`默认类型名称为实体名称，主键为"id"; `entityWith(events, "event", "Event", "id")`覆盖其中任何一个。
  include Expose({
    entities = [
      Table.entity(events, "event").public_().build(),
      // ... 应用程序的其他实体 ...
    ];
  });
};
```

`Table.new`在引入表的迁移链条目中运行：

```motoko
import Table "mo:caffeineai-oql/Table";

module {
  public func migration(_old : {}) : { events : Table.Table } {
    {
      // 1. 列：名称、类型对。顺序很重要，集合是固定的，对于表的生命周期。类型：#nat / #int / #float / #bool（64位单元）+ #text。
      // 2. 索引：查询将过滤或排序的列——
      // #hash用于相等，#ordered用于范围/orderBy。
      events = Table.new(
        [("kind", #nat), ("amount", #nat), ("note", #text)],   // 列
        [("kind", #hash), ("amount", #ordered)],               // 索引
      );
    };
  };
};
```

重要的规则：

- **数据完全加载完成——数据和索引——在应用启动写入之前**。如果写入在加载过程中发生，重新运行无法完成索引；在应用中用`buildIndex`重建它（较慢，始终有效）。
- **之后，加载和写入交替进行**。加载之间应用可以自由写入；下一个相同命令的运行会作为增量加载拾取增长，无需准备。
- **一次不能两者同时进行**——应用会拒绝，它不会错误地回答。
- **查询在整个过程中都有效**，包括加载期间；索引仍在上传的列会扫描直到完成。

## 批量上传（`ImportData`）——将现有数据加载到`Table`中

当用户的数据已经存在（来自电子表格的CSV导出或应用替换的系统），不要通过`append` trickle它——包括`ImportData`混入并作为预构建的**段图像**加载：加载器在链下以完全刷新段的字节布局排列行，应用验证并复制字节，因此一条消息的成本是O(columns)而不是O(rows)，并且整个堆栈在加载期间保持平坦。

```motoko filepath=src/backend/bulk_load_demo.mo
import Expose     "mo:caffeineai-oql/Expose";
import Entity     "mo:caffeineai-oql/Entity";   // 构建器链——始终导入
import Table      "mo:caffeineai-oql/Table";
import ImportData "mo:caffeineai-oql/ImportData";

actor {
  // 加载时声明表**无索引**，添加`ImportData([t.importTarget(name)])`，用`scripts/ingest.mjs`加载，加载后构建索引（`--index`或`buildIndex`）——数据和索引在**应用开始写入之前**完成
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

混入添加了**控制器仅限**端点（`layout`, `rows`, `putSegment`, `importFlush`, `buildIndex`, `indexStatus`）——图像的统计信息是可信的答案，因此加载表面属于可以安装代码的当事人。

**运行加载器。** 该工具在`scripts/`中附带此技能——纯Node（≥ 20）且**无需安装任何依赖项**；每个调用都通过`icp canister call`，因此必须设置icp-cli：

```bash
node <this skill's directory>/scripts/ingest.mjs \
  --canister <canister-id> --target event --file events.csv \
  -e ic --index kind:hash
```

- `--target`是可以在应用中声明的`importTarget`名称；应用的`layout()`是模式权威——CSV标题与列按名称匹配，因此文件列顺序无关紧要（忽略CSV中的额外列；文件中缺少声明的列是一个错误）。
- 连接标志与icp-cli相同，就像调用其他任何canister调用一样：`-e <environment>` (`-e ic`为已部署的应用), `-n <network>`, `--identity <name>`（默认：你当前的标识符）。端点是控制器仅限的，因此标识符必须是**应用的控制器**。如果没有这些标志，你的icp默认值适用——canister NAME然后解析到项目的默认环境，因此从应用的项目目录运行该工具。
- `--index col:kind`（可重复，`kind` = `hash`)在加载后构建并上传该列的索引。对于它无法构建的任何内容（`#ordered`，复合的），通过混入的端点在链上构建：`icp canister call <id> buildIndex '("event", vec {"kind"}, variant {hash})'`——查询正确扫描（速度正确，只是较慢），然后索引服务；`indexStatus '("event")'`报告进度。
- 以与客户端将如何读取相同的方式验证加载：`icp canister call <id> execute '("{\"start\":\"event\",\"aggregate\":[{\"fn\":\"count\"}])' --query`
  必须返回CSV的行数。
- CSV单元格按声明的类型解码。一个未加引号的空字段是一个**空单元格**；在`#text`列中引用`""`是一个空字符串；`#bytes(w)`列的字段是**base64**，必须解码为恰好`w`个字节。
- **重新运行相同的命令可以继续**：表已经持有的行会被跳过，并且`putSegment`的期望第一行保护将任何重复发送转换为响亮的陷阱而不是重复的行。

**操作规则**（违反规则会响亮地拒绝而不是损坏）：

1. **在应用开始写入之前完全完成第一次加载——数据和索引——**。如果写入在加载过程中发生，重新运行无法完成索引；在应用中用`buildIndex`重建它（较慢，始终有效）。
2. **之后，加载和写入交替进行**。加载之间应用可以自由写入；下一个相同命令的运行会拾取增长作为增量加载，无需准备。
3. **一次不能两者同时进行**——应用会拒绝，它不会错误地回答。
4. **查询在整个过程中都有效**，包括加载期间；一个索引仍在上传的列会扫描直到完成。
