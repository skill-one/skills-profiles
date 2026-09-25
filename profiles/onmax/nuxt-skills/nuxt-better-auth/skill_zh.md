# Nuxt Better Auth

使用与任务最匹配的最小参考。

## 选择参考

| 任务                                                                                         | 阅读                                                             |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| 安装模块、配置环境变量或创建配置文件                                                          | [参考/安装.md](references/installation.md)                      |
| 读取客户端会话状态、构建认证表单、调用插件或获取认证绑定数据                                       | [参考/客户端认证.md](references/client-auth.md)                |
| 在服务器处理程序中读取或强制执行会话、创建会话或刷新缓存的会话数据                                | [参考/服务器认证.md](references/server-auth.md)                |
| 保护页面或 API 路由并配置重定向                                                              | [参考/路由保护.md](references/route-protection.md)             |
| 注册 Better Auth 插件及其客户端配套                                                         | [参考/插件.md](references/plugins.md)                          |
| 配置 NuxtHub、生成的模式或二级存储                                                              | [参考/数据库.md](references/database.md)                       |
| 将 Nuxt 前端连接到外部 Better Auth 服务器                                                        | [参考/客户端仅.md](references/client-only.md)                  |
| 使用推断的认证类型或添加项目字段                                                              | [参考/类型.md](references/types.md)                            |

## 适用于所有任务的规则

- 确认消费者安装的包版本支持您使用的每个 API。发布的功能可能比消费者的 lockfile 新。
- 使用 `requireUserSession(event)` 在服务器端强制执行受保护的 API 读取和修改。路由规则和页面元数据也控制导航。
- 仅导航到经过验证的本地重定向路径。
- 在 `clientOnly` 模式下，不要使用本地服务器辅助函数或期望 SSR 会话水合。
- 在会话有效负载字段进行服务器端更改后，调用 `refreshSessionCookieCache(event)`。使用 `runWithSessionRefresh()` 包装创建或更改当前会话的自定义客户端认证端点。

在完成实现之前，运行消费者的类型检查和最窄的相关认证测试。

## 资源

- [文档站点](https://better-auth.nuxt.dev)
- [Better Auth 文档](https://www.better-auth.com/)
