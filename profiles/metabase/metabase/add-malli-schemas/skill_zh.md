# 为 API 端点添加 Malli 模式

这项技能帮助您在 Metabase 代码库中高效且统一地向 API 端点添加 Malli 模式。

## 参考文件（最佳示例）

- `src/metabase/warehouses/api.clj` - 最全面的模式，自定义错误消息
- `src/metabase/api_keys/api.clj` - 优秀的响应模式
- `src/metabase/collections/api.clj` - 优秀的命名模式模式
- `src/metabase/timeline/api/timeline.clj` - 清洁、简单的示例

## 快速检查清单

当向端点添加 Malli 模式时：

- [ ] 路由参数有模式
- [ ] 查询参数有模式，并使用 `:optional true` 和 `:default`（在适当的地方）
- [ ] 请求体有模式（用于 POST/PUT）
- [ ] 响应模式已定义（使用路由字符串后的 `:-`）
- [ ] 尽可能使用 `ms` 命名空间中的现有模式类型
- [ ] 考虑为可重用或复杂的类型创建命名模式
- [ ] 为验证失败添加上下文错误消息

## 基本结构

### 完整端点示例

```clojure
(mr/def ::Color [:enum "red" "blue" "green"])

(mr/def ::ResponseSchema
  [:map
   [:id pos-int?]
   [:name string?]
   [:color ::Color]
   [:created_at ms/TemporalString]])

(api.macros/defendpoint :post "/:name" :- ::ResponseSchema
  "使用给定名称创建资源。"
  [;; 路由参数：
   {:keys [name]} :- [:map [:name ms/NonBlankString]]
   ;; 查询参数：
   {:keys [include archived]} :- [:map
                                   [:include {:optional true} [:maybe [:= "details"]]]
                                   [:archived {:default false} [:maybe ms/BooleanValue]]]
   ;; 请求体参数：
   {:keys [color]} :- [:map [:color ::Color]]
   ]
  ;; 端点实现，例如：
  {:id 99
   :name (str "mr or mrs " name)
   :color ({"red" "blue" "blue" "green" "green" "red"} color)
   :created_at (t/format (t/formatter "yyyy-MM-dd'T'HH:mm:ssXXX") (t/zoned-date-time))}
  )
```

## 常见模式

1. 路由参数（`api/user/id/5` 中的 5）
2. 查询参数（`api/users?sort=asc` 中的 sort+asc 对）
3. 请求体参数（请求体内容。几乎总是从 json 解码为 edn）
4. 原始请求映射

在 4 个参数中，除非必要，否则优先考虑使用原始请求。

### 路由参数

始终是必需的，通常只是一个包含 ID 的映射：

```clojure
[{:keys [id]} :- [:map [:id ms/PositiveInt]]]
```

对于多个路由参数：

```clojure
[{:keys [id field-id]} :- [:map
                           [:id ms/PositiveInt]
                           [:field-id ms/PositiveInt]]]
```

### 查询参数

为 `{:optional true ...}` 和 `:default` 值添加属性：

```clojure
{:keys [archived include limit offset]} :- [:map
                                            [:archived {:default false} [:maybe ms/BooleanValue]]
                                            [:include {:optional true} [:maybe [:= "tables"]]]
                                            [:limit {:optional true} [:maybe ms/PositiveInt]]
                                            [:offset {:optional true} [:maybe ms/PositiveInt]]]
```

### 请求体（POST/PUT）

```clojure
{:keys [name description parent_id]} :- [:map
                                         [:name ms/NonBlankString]
                                         [:description {:optional true} [:maybe ms/NonBlankString]]
                                         [:parent_id {:optional true} [:maybe ms/PositiveInt]]]
```

### 响应模式

#### 简单内联响应：

```clojure
(api.macros/defendpoint :get "/:id" :- [:map
                                        [:id pos-int?]
                                        [:name string?]]
  "获取一个事物"
  ...)
```

#### 命名模式用于重用：

```clojure
(mr/def ::Thing
  [:map
   [:id pos-int?]
   [:name string?]
   [:description [:maybe string?]]])

(api.macros/defendpoint :get "/:id" :- ::Thing
  "获取一个事物"
  ...)

(api.macros/defendpoint :get "/" :- [:sequential ::Thing]
  "获取所有事物"
  ...)
```

## 常见模式类型

### 从 `metabase.util.malli.schema`（别名为 `ms`）

优先使用 `ms/*` 命名空间中的模式，因为它们与我们的 API 基础设施配合得更好。

例如，使用 `ms/PositiveInt` 而不是 `pos-int?`。

```clojure
ms/PositiveInt                  ;; 正整数
ms/NonBlankString               ;; 非空字符串
ms/BooleanValue                 ;; 字符串 "true"/"false" 或布尔值
ms/MaybeBooleanValue            ;; BooleanValue 或 nil
ms/TemporalString               ;; ISO-8601 日期/时间字符串（仅用于请求参数！）
ms/OpaqueJSONObject             ;; JSON 对象，其键非我们声明；字符串键
ms/PositiveNum                  ;; 正数
ms/IntGreaterThanOrEqualToZero  ;; 0 或正
```

**重要提示：** 对于响应模式，使用 `:any` 而不是 `ms/TemporalString`！响应模式在 JSON 序列化之前进行验证，因此它们看到的是 Java Time 对象。

### 内置 Malli 类型

```clojure
:string                     ;; 任何字符串
:boolean                    ;; true/false
:int                        ;; 任何整数
:keyword                    ;; Clojure 关键字
pos-int?                    ;; 正整数谓词
[:maybe X]                  ;; X 或 nil
[:enum "a" "b" "c"]         ;; 这些值之一
[:or X Y]                   ;; 满足 X 或 Y 的模式
[:and X Y]                  ;; 满足 X 和 Y 的模式
[:sequential X]             ;; X 的序列
[:set X]                    ;; X 的集合
[:map-of K V]               ;; 具有键模式 K 和值模式 V 的映射
[:tuple X Y Z]              ;; 模式 X Y Z 的固定长度元组
```

避免使用序列模式，除非完全必要。

## 分步指南：向端点添加模式

### 示例：为 `GET /api/field/:id/related` 添加返回模式

**之前：**
```clojure
(api.macros/defendpoint :get "/:id/related"
  "返回相关实体。"
  [{:keys [id]} :- [:map [:id ms/PositiveInt]]]
  (-> (t2/select-one :model/Field :id id) api/read-check xrays/related))
```

**步骤 1：** 检查函数返回什么（查看 `xrays/related`）

**步骤 2：** 基于返回类型定义响应模式：

```clojure
(mr/def ::RelatedEntity
  [:map
   [:tables [:sequential [:map [:id pos-int?] [:name string?]]]]
   [:fields [:sequential [:map [:id pos-int?] [:name string?]]]]])
```

**步骤 3：** 将响应模式添加到端点：

```clojure
(api.macros/defendpoint :get "/:id/related" :- ::RelatedEntity
  "返回相关实体。"
  [{:keys [id]} :- [:map [:id ms/PositiveInt]]]
  (-> (t2/select-one :model/Field :id id) api/read-check xrays/related))
```

## 高级模式

### 自定义错误消息

```clojure
(def DBEngineString
  "有效数据库引擎名称的模式。"
  (mu/with-api-error-message
   [:and
    ms/NonBlankString
    [:fn
     {:error/message "有效数据库引擎"}
     #(u/ignore-exceptions (driver/the-driver %))]]
   (deferred-tru "值必须是有效的数据库引擎。")))
```

### 带文档的枚举

```clojure
(def PinnedState
  (into [:enum {:error/message "pinned state 必须是 'all', 'is_pinned', 或 'is_not_pinned'"}]
        #{"all" "is_pinned" "is_not_pinned"}))
```

### 复杂嵌套响应

```clojure
(mr/def ::DashboardQuestionCandidate
  [:map
   [:id ms/PositiveInt]
   [:name ms/NonBlankString]
   [:description [:maybe string?]]
   [:sole_dashboard_info
    [:map
     [:id ms/PositiveInt]
     [:name ms/NonBlankString]
     [:description [:maybe string?]]]]])

(mr/def ::DashboardQuestionCandidatesResponse
  [:map
   [:data [:sequential ::DashboardQuestionCandidate]]
   [:total ms/PositiveInt]])
```

### 分页响应模式

```clojure
(mr/def ::PaginatedResponse
  [:map
   [:data [:sequential ::Item]]
   [:total integer?]
   [:limit {:optional true} [:maybe integer?]]
   [:offset {:optional true} [:maybe integer?]]])
```

## 常见陷阱

### 不要：忘记为可空字段使用 `:maybe`

```clojure
[:description ms/NonBlankString]  ;; 错误 - 如果为 nil 则失败
[:description [:maybe ms/NonBlankString]]  ;; 正确 - 允许 nil
```

### 不要：忘记为可选查询参数使用 `:optional true`

```clojure
[:limit ms/PositiveInt]  ;; 错误 - 必需但不应是
[:limit {:optional true} [:maybe ms/PositiveInt]]  ;; 正确
```

### 不要：忘记为已知参数使用 `:default` 值

```clojure
[:limit ms/PositiveInt]  ;; 错误 - 必需但不应是
[:limit {:optional true :default 0} [:maybe ms/PositiveInt]]  ;; 正确
```

### 不要：混淆路由参数、查询参数和请求体

```clojure
;; 错误 - 全部在一个映射中
[{:keys [id name archived]} :- [:map ...]]

;; 正确 - 分离解构
[{:keys [id]} :- [:map [:id ms/PositiveInt]]
 {:keys [archived]} :- [:map [:archived {:default false} ms/BooleanValue]]
 {:keys [name]} :- [:map [:name ms/NonBlankString]]]
```

### 不要：在响应模式中使用 `ms/TemporalString` 来处理 Java Time 对象

```clojure
;; 错误 - Java Time 对象还不是字符串
[:date_joined ms/TemporalString]

;; 正确 - 模式在 JSON 序列化之前进行验证
[:date_join :any]  ;; Java Time 对象，由中间件序列化为字符串
[:last_login [:maybe :any]]  ;; Java Time 对象或 nil
```

**原因：** 响应模式在 JSON 序列化之前验证内部 Clojure 数据结构。Java Time 对象（如 `OffsetDateTime`）由 JSON 中间件转换为 ISO-8601 字符串，因此模式需要接受原始 Java 对象。

### 不要：在数据实际上是集合时使用 `[:sequential X]`

```clojure
;; 错误 - group_ids 实际上是集合
[:group_ids {:optional true} [:sequential pos-int?]]

;; 正确 - 匹配实际数据结构
[:group_ids {:optional true} [:maybe [:set pos-int?]]]
```

**原因：** Toucan 水合方法通常返回集合。JSON 中间件将集合序列化为数组，但模式在序列化之前进行验证。

### 不要：为重用结构创建匿名模式

使用 `mr/def` 为在多个地方使用的模式：

```clojure
(mr/def ::User
  [:map
   [:id pos-int?]
   [:email string?]
   [:name string?]])
```

## 查找返回类型

1. **查看被调用的函数**

```clojure
(api.macros/defendpoint :get "/:id"
  [{:keys [id]}]
  (t2/select-one :model/Field :id id))  ;; 返回一个 Field 实例
```

2. **检查 Toucan 模型结构**

查找 `src/metabase/*/models/*.clj` 中的模型定义。

3. **使用 clojure-mcp 或 REPL 检查**

```bash
./bin/mage -repl '(require '\''metabase.xrays.core) (doc metabase.xrays.core/related)'
```

4. **检查测试**

测试通常显示预期的响应结构。

## 理解模式验证时间

**关键概念：** 模式在请求/响应生命周期的不同时间点进行验证：

### 请求参数模式（查询/请求体/路由）

- 验证在 JSON 解析之后
- 数据已经反序列化（字符串、数字、布尔值）
- 使用 `ms/TemporalString` 为日期/时间输入
- 使用 `ms/BooleanValue` 为布尔查询参数

### 响应模式

- 验证在 JSON 序列化之前
- 数据仍然是 Clojure 格式（Java Time 对象、集合、关键字）
- 使用 `:any` 为 Java Time 对象
- 使用 `[:set X]` 为集合
- 使用 `[:enum :keyword]` 为关键字枚举

### 序列化流程

```
请求：  JSON 字符串 → 解析 → 强制转换 → 处理程序
响应：  处理程序 → 模式检查 → 编码 → 序列化 → JSON 字符串
```

## 工作流程总结

1. **阅读端点** - 理解它做什么
2. **识别参数** - 路由、查询、请求体
3. **添加参数模式** - 使用 `ms` 中的现有类型
4. **确定返回类型** - 检查实现
5. **定义响应模式** - 内联或使用 `mr/def` 命名
6. **测试** - 确保端点正常工作并正确验证

## 测试您的模式

添加模式后，验证：

1. **有效请求正常工作** - 使用正确数据测试
2. **无效请求优雅失败** - 使用错误类型测试
3. **可选参数正常工作** - 有/无可选参数测试
4. **错误消息清晰** - 检查验证错误响应

## 小贴士

- **从简单开始** - 先使用基本类型，再逐步完善
- **重用模式** - 如果看到相同的结构两次，将其定义为命名模式
- **保持具体** - 使用 `ms/PositiveInt` 而不是 `pos-int?`
- **添加文档** - 为命名模式添加文档字符串
- **遵循约定** - 查看同一命名空间中类似的端点
- **检查实际数据** - 使用 REPL 检查实际返回的内容，然后再序列化

## 其他资源

- [Malli 文档](https://github.com/metosin/malli)
- Metabase Malli 工具：`src/metabase/util/malli/schema.clj`
- Metabase 模式注册表：`src/metabase/util/malli/registry.clj`
