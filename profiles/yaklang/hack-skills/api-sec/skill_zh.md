# API 安全路由器

这是 API 安全测试的路由入口。

首先使用此技能判断 API 问题主要涉及的是信息收集/文档、对象授权、令牌信任还是 GraphQL/隐藏参数，然后路由到更深入的主题技能。

## 使用场景

- 目标暴露了 REST API、移动后端或 GraphQL 端点
- 您需要在进入具体主题之前定义 API 测试顺序
- 您希望将对象授权、JWT、GraphQL 和隐藏字段作为单独的轨道处理

## 技能地图

- [API 信息收集和文档](../api-recon-and-docs/SKILL.md)：OpenAPI、Swagger、版本漂移、隐藏文档
- [API 授权和 BOLA](../api-authorization-and-bola/SKILL.md)：BOLA、BFLA、方法滥用、隐藏可写字段
- [API 认证和 JWT 滥用](../api-auth-and-jwt-abuse/SKILL.md)：携带令牌、头部信任、声明滥用、速率限制绕过
- [GraphQL 和隐藏参数](../graphql-and-hidden-parameters/SKILL.md)：内省、批处理、未记录的字段、隐藏参数

## 快速排查

| 观察 | 路由 |
|---|---|
| 存在 Swagger 或 OpenAPI | [api-recon-and-docs](../api-recon-and-docs/SKILL.md) |
| URL、JSON、头部或 GraphQL 参数中出现 ID | [api-authorization-and-bola](../api-authorization-and-bola/SKILL.md) |
| 通信中可见 JWT 令牌 | [api-auth-and-jwt-abuse](../api-auth-and-jwt-abuse/SKILL.md) |
| 存在 `/graphql` 或批处理 JSON 数组 | [graphql-and-hidden-parameters](../graphql-and-hidden-parameters/SKILL.md) |
| 注册、登录或个人资料更新接受额外字段 | [api-authorization-and-bola](../api-authorization-and-bola/SKILL.md) 然后是 [api-auth-and-jwt-abuse](../api-auth-and-jwt-abuse/SKILL.md) |

## 推荐流程

1. 从暴露的端点和文档资源开始
2. 然后评估对象级别和函数级别的授权
3. 然后评估令牌、头部、签名和速率限制边界
4. 如果存在 GraphQL 或复杂 JSON，继续处理隐藏字段和模式滥用

## 相关分类

- [auth-sec](../auth-sec/SKILL.md)
- [business-logic-vuln](../business-logic-vuln/SKILL.md)
- [recon-for-sec](../recon-for-sec/SKILL.md)
