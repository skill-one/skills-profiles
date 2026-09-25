# 数据查看器

仅管理员可用的数据检查扩展，适用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## 概述

每个 Caffeine 应用都预装了 `caffeineai-data-viewer` mops 包，并且启用了 moc 的 `--generate-view-queries` 标志。在 actor 中包含 `include MixinViews()` 后，编译器会为支持的类型中每个稳定的变量 **自动暴露一个仅控制器可用的 `__<var>` 查询**：

- `Map.Map<K, V>` — `(?K, ?Nat) -> [(K, V)]`
- `Set.Set<K>` — `(?K, ?Nat) -> [K]`
- `[V]`, `[var V]`, `List.List<V>`, `Stack.Stack<V>`, `Queue.Queue<V>` — `(?Nat, ?Nat) -> [V]`

`null` 游标从开头开始；`null` 计数返回从游标开始的所有数据。每个生成的查询会拦截任何非控制器调用者——它们仅用于管理员仪表板和调试查看器，而不是面向用户的端点。

# 后端

包和 `include` 已经集成到模板中。您无需添加或修改任何内容即可使查看器工作——声明一个支持的类型的稳定变量，`__<var>` 查询就会自动出现。

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import MixinViews "mo:caffeineai-data-viewer/MixinViews";

actor {
  include MixinViews();

  let users = Map.empty<Principal, Text>();

  // 自动生成：__users : (ko : ?Principal, count : ?Nat) -> [(Principal, Text)] 查询
};
```

随包提供的 Lintoko 规则 `include-mixin-views` 如果 actor 主体缺少 `include MixinViews();` 会报错。保留 `include`——移除它将禁用所有自动生成的查看器。

## 规则

- 绝对不要将生成的 `__<var>` 查询用作面向用户的端点的替代品——它们会拦截任何非控制器调用者。公开的列表/信息/搜索方法仍然需要使用 `public query func listX(...)` 正常编写。
- 绝对不要声明名称以 `__` 开头的 actor 成员——它要么与自动生成的查询冲突，要么触发了保留的前缀。
- 纯（不可变）集合（`pure/Map`、`pure/Set`、`pure/List`、`pure/Queue`）**不支持**。查看器设计为仅可变；纯集合字段访问在 Caffeine 项目中也是已弃用的模式。
