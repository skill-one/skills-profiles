---
name: loops-api
description: 在用户希望从应用代码、后端服务、webhook 处理程序或服务器端自动化中集成 Loops 时，请使用此技能。这包括 Loops HTTP API 和用于服务器端联系人、联系人属性、邮件列表、事件、API 密钥验证、事务性电子邮件、内容编辑（活动、群组、受众细分、电子邮件消息、主题和组件）、工作流图/节点变异以及入站 Loops webhook 的官方 SDK。在类似 "Loops API"、"Loops SDK"、"通过 API 创建活动"、"更新电子邮件消息 LMX"、"通过 API 创建主题"、"通过 API 创建工作流"、"添加工作流节点"、"Loops webhook"、"从我的应用发送 Loops 事件"、"在 webhook 中将联系人添加到 Loops"、"从后端代码发送事务性电子邮件" 或任何用户希望将 Loops 集成到其应用、后端、webhook 或自动化中的时候触发。不应用于 CLI 或仅限 shell 的请求。
---

# Loops API和SDK技能

此技能可帮助您从应用程序代码中实现Loops的工作流程。用于后端集成、精确的请求指导以及SDK或HTTP决策。

## 使用场景

当用户需要以下功能时，请使用此技能：

- 将Loops集成到应用程序、后端、webhook或自动化流程中
- 在官方SDK和原始HTTP之间进行选择
- 管理联系人、联系人属性、邮件列表、事件或事务性邮件
- 通过API发送事务性邮件或创建、编辑和发布事务性邮件模板
- 管理联系人屏蔽状态/移除
- 创建具有受众定位（邮件列表、细分或过滤器）、分组和排期的草稿活动
- 将活动和事务性邮件组织到分组中
- 列出或创建用于活动/工作流定位的受众细分
- 更新邮件内容（主题、发件人、CC/BCC、格式、回退、LMX），发送预览并运行Guardian检查
- 列出、创建、更新和获取主题和组件以构建LMX负载
- 上传用于邮件内容的图片
- 创建、更新、检查和删除工作流和工作流节点（包括邮件列表更改、分支、重定向和排队联系人处理）
- 列出工作流事件触发的事件模式
- 接收和验证传入的Loops webhook（联系人、邮件发送和参与事件）
- 从代码中验证凭证或排查Loops请求行为

此技能用于实施和运营使用，而非广泛的邮件策略或可投递性审查。

## 工作方式

当此技能激活时：

1. 首先选择正确的接口：SDK或原始HTTP。
2. 当语言有官方SDK时，优先为应用程序代码使用官方SDK。
3. 仅在没有SDK可用或用户需要精确负载控制时，才使用原始HTTP。
4. 将Loops请求保留在服务器端。
5. 当细节重要时，通过官方文档或OpenAPI规范验证精确行为。
6. 对于LMX邮件设计或品牌工作，使用`references/http-api.md`中的主题/组件端点；LMX设计政策存在于`loops-lmx`技能中。
7. 如果任务主要关于Loops CLI安装、认证、shell使用或命令帮助，请使用单独的`loops-cli`技能。

官方参考资料：

- 文档：`https://loops.so/docs`
- API参考：`https://loops.so/docs/api-reference/intro`
- 活动示例：`https://loops.so/docs/api-reference/examples/campaigns`
- JavaScript SDK：`https://loops.so/docs/sdks/javascript`
- Webhooks：`https://loops.so/docs/webhooks`
- OpenAPI规范：`https://app.loops.so/openapi.json`

## 选择接口

- SDK或HTTP API：
  - 应用程序代码
  - 后端服务
  - webhook处理程序
  - 可重复的集成
  读取`references/http-api.md`

如果用户是从终端而不是编写应用程序代码进行工作，请使用`loops-cli`技能。

## 类别路由

- 认证、基本URL、速率限制、联系人、屏蔽、属性、列表、事件、上传、传入的Loops webhook、SDK示例和HTTP错误：
  读取`references/http-api.md`
- 活动、活动分组、事务性分组、受众细分、工作流、工作流节点、事件模式、事务性邮件、邮件消息、主题、组件和修订安全的更新：
  读取`references/http-api.md`。对于LMX标记本身，也使用`loops-lmx`技能。

## 输出清单

目标是让用户留下：

- 任务正确的API接口选择
- 精确的负载形状或SDK使用
- 任何影响行为的Loops特定注意事项
- 下一步验证步骤，例如小型测试请求或API密钥检查
