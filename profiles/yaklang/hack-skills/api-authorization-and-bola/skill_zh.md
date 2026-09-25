# 技能：API 授权与 BOLA — 对象访问、函数访问和批量赋值

> **AI 加载指令**：当 API 暴露对象 ID、嵌套资源或角色敏感函数，并且您需要一个专注的授权测试路径时，请使用此技能：BOLA、BFLA、方法滥用和隐藏字段控制。

## 1. 核心测试循环

1. 创建账户 A 和账户 B。
2. 以账户 A 的身份捕获创建、读取、更新和删除流程。
3. 使用账户 B 的令牌重放。
4. 测试兄弟端点、嵌套端点和替代 HTTP 动词。

## 2. 测试表面

| 表面 | 示例 |
|---|---|
| 对象读取 | `/api/v1/orders/123` |
| 嵌套对象 | `/api/v1/users/1/invoices/9` |
| 管理员或内部函数 | `/api/v1/admin/users` |
| 更新路径 | `PUT`、`PATCH`、`DELETE` 变体 |
| 隐藏的 JSON 字段 | `role`、`org`、`verified`、`tier` |

## 3. 快速负载

```json
{"role":"admin"}
{"isAdmin":true}
{"org":"target-company"}
{"verified":true}
```

## 4. 测试人员遗漏的内容

- 头部、Cookie、GraphQL 参数和嵌套对象中的对象 ID
- 使用相同路由但授权较弱的不同方法
- 存在父级检查但缺少子资源检查
- 管理员文档揭示额外可写字段

## 5. 下一步路由

- 对于 JWT 或令牌层滥用：[api 授权与 JWT 滥用](../api-auth-and-jwt-abuse/SKILL.md)
- 对于 GraphQL 和隐藏参数发现：[graphql 和隐藏参数](../graphql-and-hidden-parameters/SKILL.md)
- 对于 API 外部的更广泛 IDOR 模式：[idor 破坏对象授权](../idor-broken-object-authorization/SKILL.md)
