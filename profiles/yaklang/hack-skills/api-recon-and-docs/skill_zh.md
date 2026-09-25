# 技能：API 探测与文档 — 端点、模式与版本表面

> **AI 加载指令**：当目标是 REST、移动或 GraphQL API，且在利用前需要枚举端点、文档、版本和隐藏表面区域时，首先使用此技能。

## 1. 主要目标

1. 发现所有可访问的 API 入口点。
2. 提取模式、可选字段和角色差异。
3. 识别旧版本、移动路径、GraphQL 端点和未记录的参数。

## 2. 探测清单

### JavaScript 和客户端挖掘

```bash
curl https://目标/app.js | grep -oE '(/api|/rest|/graphql)[^"'\'' ]+' | sort -u
```

### 常见文档和模式路径

```text
/swagger.json
/openapi.json
/api-docs
/docs
/.well-known/
/graphql
/gql
```

### 版本和产品差异

```text
/api/v1/
/api/v2/
/api/mobile/v1/
/legacy/
```

## 3. 从文档中提取的内容

- 可选和未记录的字段
- 仅限管理员请求示例
- 可能仍然活跃的已弃用端点
- 模式提示，如 `additionalProperties: true`
- 与过滤、排序、ID、角色或租户相关的参数名称

## 4. 下一步操作

| 发现 | 下一个技能 |
|---|---|
| 各处出现对象 ID | [API 授权和 Bola](../api-authorization-and-bola/SKILL.md) |
| JWT、OAuth、角色声明 | [API 授权和 JWT 滥用](../api-auth-and-jwt-abuse/SKILL.md) |
| GraphQL 或隐藏字段 | [GraphQL 和隐藏参数](../graphql-and-hidden-parameters/SKILL.md) |
| 强大的认证边界但有可疑的业务流程 | [业务逻辑漏洞](../business-logic-vulnerabilities/SKILL.md) |
