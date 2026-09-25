# 技能：GraphQL 和隐藏参数 — 探视、批量处理和未公开字段

> **AI 加载指令**：当存在 GraphQL 或 REST 文档建议可选、已弃用或未公开字段时，使用此技能。专注于模式发现、隐藏参数滥用以及批量处理作为倍增器。

## 1. GraphQL 初步探索

```graphql
query { __typename }
query {
  __schema {
    types { name }
  }
}
```

如果探视受限，继续进行：

- 字段建议和基于错误的发现
- 已知的类型探测，如 `__type(name: "User")`
- JS 和移动包路由提取

## 2. 高价值 GraphQL 测试

| 主题 | 示例 |
|---|---|
| IDOR | `user(id: "victim")` |
| 批量处理 | 登录或对象获取操作的数组 |
| 隐藏字段 | 在类型定义中暴露的管理员专有字段 |
| 嵌套授权漏洞 | 具有较弱检查的关联对象字段 |

## 3. 隐藏参数发现

寻找：

- 管理员文档中存在但在公共文档中不存在的字段
- `additionalProperties` 或宽松模式
- 前端代码使用比可见 UI 控件更丰富的请求体
- 携带角色、组织、功能标志或内部过滤字段的移动端端点

## 4. 下一步路由

- 如果隐藏字段影响权限：[API 授权和 Bola](../api-authorization-and-bola/SKILL.md)
- 如果 GraphQL 批量处理改变授权或速率行为：[API 授权和 JWT 滥用](../api-auth-and-jwt-abuse/SKILL.md)
- 如果端点发现不完整：[API 探测和文档](../api-recon-and-docs/SKILL.md)
