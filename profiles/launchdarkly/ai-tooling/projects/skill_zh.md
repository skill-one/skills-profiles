# LaunchDarkly 项目设置

您正在使用一个技能，它将指导您在代码库中设置 LaunchDarkly 项目管理。您的工作是探索代码库以了解技术栈和模式，评估哪种方法最合适，从参考资料中选择正确的实现路径，执行设置并验证其是否正常工作。

## 前置条件

**选择一项：**
- 具有项目写入 (`projects:write`) 权限的 LaunchDarkly API 访问令牌
- 在您的环境中配置的 LaunchDarkly MCP 服务器

## 核心原则

1. **先理解**：探索代码库以了解技术栈和模式。
2. **选择合适的方案**：选择与您的架构匹配的方法。
3. **遵循规范**：尊重现有的代码风格和结构。
4. **验证集成**：确认设置是否正常工作：代理执行检查并报告结果。

## API 密钥检测

在提示用户输入 API 密钥之前，尝试自动检测：

1. **检查环境变量**：查找 `LAUNCHDARKLY_API_KEY`、`LAUNCHDARKLY_API_TOKEN` 或 `LD_API_KEY`
2. **检查 MCP 配置**：如果使用 Claude，读取 `~/.claude/config.json` 中的 `mcpServers.launchdarkly.env.LAUNCHDARKLY_API_KEY`
3. **提示用户**：仅在检测失败时，要求用户提供 API 密钥

有关 API 使用模式的更多信息，请参阅 [快速入门](references/quick-start.md)。

## 项目是什么？

项目是 LaunchDarkly 的顶级组织容器，其中包含：
- 所有您的配置
- 功能标志和细分
- 多个环境（默认创建生产环境和测试环境）

将项目视为需要各自隔离配置的独立应用程序、服务或团队。

## 项目设置工作流程

### 第 1 步：探索代码库

在实施任何内容之前，了解现有架构：

1. **识别技术栈：**
   - 使用什么语言？（Python、Node.js、Go、Java 等）
   - 使用什么框架？（FastAPI、Express、Spring Boot 等）
   - 是否存在现有的 LaunchDarkly 集成？

2. **检查环境管理：**
   - 环境变量如何存储？（.env 文件、密钥管理器、配置文件）
   - 配置在哪里加载？（启动脚本、配置模块）
   - 是否存在现有的 LaunchDarkly SDK 密钥？

3. **查找模式：**
   - 是否存在现有的 API 客户端或服务模块？
   - 如何通常进行外部 API 集成？
   - 是否有 CLI、脚本目录或管理工具？

4. **了解用例：**
   - 这是否是一个新项目正在设置？
   - 添加到现有的 LaunchDarkly 集成？
   - 是否是多服务架构的一部分？
   - 是否需要在区域/团队之间克隆项目？

### 第 2 步：评估情况

根据您的探索，确定正确的方案：

| 情景 | 推荐路径 |
|------|----------|
| 新项目，无 LaunchDarkly 集成 | **快速设置** - 创建项目并保存 SDK 密钥 |
| 现有的 LaunchDarkly 使用 | **添加到现有** - 创建新项目或使用现有项目 |
| 多个服务/微服务 | **多项目** - 为每个服务创建项目 |
| 多区域或多租户 | **项目克隆** - 克隆模板项目 |
| 基础设施即代码 (IaC) 设置 | **自动化设置** - 基于脚本的创建 |
| 需要项目管理工具 | **CLI/管理工具** - 构建项目管理实用程序 |

### 第 3 步：选择您的实现路径

选择与您的技术栈和用例匹配的参考指南：

**按语言/技术栈：**
- [Python 实现](references/python-setup.md) - 用于 Python 应用程序（FastAPI、Django、Flask）
- [Node.js/TypeScript 实现](references/nodejs-setup.md) - 用于 Node.js/Express/NestJS 应用程序
- [Go 实现](references/go-setup.md) - 用于 Go 服务
- [多语言设置](references/multi-language-setup.md) - 用于多语言架构

**按用例：**
- [快速入门](references/quick-start.md) - 创建第一个项目并获取 SDK 密钥
- [环境配置](references/env-config.md) - 将 SDK 密钥保存到 .env、密钥或配置
- [项目克隆](references/project-cloning.md) - 为区域/团队克隆项目
- [IaC/自动化](references/iac-automation.md) - Terraform、脚本、CI/CD 集成
- [管理工具](references/admin-tooling.md) - 构建 CLI 或管理实用程序

### 第 4 步：实现集成

遵循所选的参考指南来实施项目管理。关键注意事项：

1. **API 身份验证：**
   - 安全存储 API 令牌
   - 遵循现有的密钥管理模式
   - 永远不要将令牌提交到版本控制

2. **项目命名：**
   - 使用一致且描述性的名称
   - 遵循现有的命名规范
   - 项目密钥：小写、连字符、以字母开头

3. **SDK 密钥管理：**
   - 为每个环境提取和存储 SDK 密钥
   - 使用与代码库中其他密钥相同的模式
   - 考虑为测试/预发布/生产使用不同的密钥

4. **错误处理：**
   - 优雅地处理现有项目（409 冲突）
   - 提供清晰的错误消息
   - 不要无声失败

### 第 5 步：验证设置

创建项目后，验证其是否正常工作：

1. **获取以确认其存在。** 优先使用 MCP `get-project` 工具而不是原始 `curl` — 它返回您可以直接检查的 typed 对象。如果您必须调用 REST API：
   ```bash
   curl -X GET "https://app.launchdarkly.com/api/v2/projects/{projectKey}?expand=environments" \
     -H "Authorization: {api_token}"
   ```
   **不要直接将响应传递到 `.environments.items[]` 风格的 `jq` 过滤器。** `environments` 的形状因 `expand` 参数而异 — 有时它是 `{items: [...]}`，有时是一个裸数组 — 手动编写的过滤器会因 `Cannot index array with string "items"` 而失败。首先运行 `jq -e .` 来检查实际形状，或使用 `jq '.environments | if type == "object" then .items else . end'` 来处理两种情况。

2. **测试 SDK 集成：**
   运行快速验证以确保 SDK 密钥正常工作：
   ```python
   import ldclient
   from ldclient.config import Config

   ldclient.set_config(Config("{sdk_key}"))
   # SDK 成功初始化

   # 始终在关闭之前刷新事件 — 否则，在短生命周期的脚本和长时间运行的服务中，尾随事件有丢失的风险。
   ldclient.get().flush()
   ldclient.get().close()
   ```

3. **报告结果：**
   - ✓ 项目存在且具有环境
   - ✓ SDK 密钥存在且有效
   - ✓ SDK 可以初始化（或标记任何问题）

## 项目密钥最佳实践

项目密钥必须遵循以下规则：

```
✓ 良好示例：
  - "support-ai"
  - "chat-bot-v2"
  - "internal-tools"

✗ 不好示例：
  - "Support_AI"     # 不能有大写或下划线
  - "123-project"    # 必须以字母开头  
  - "my.project"     # 不允许点
```

**命名建议：**
- 保持密钥简短但描述性
- 使用团队/服务/目的作为命名方案
- 在整个组织中保持一致性

## 常见的组织模式

### 按团队
```
platform-ai       → 平台团队代理
customer-ai       → 客户成功团队代理
internal-ai       → 内部工具团队代理
```

### 按应用程序/服务
```
mobile-ai         → 移动应用程序配置
web-ai            → 网络应用程序配置
api-ai            → API 服务配置
```

### 按区域/部署
```
ai-us             → 美国区域
ai-eu             → 欧洲区域
ai-apac           → 亚洲-太平洋区域
```

## 边缘情况

| 情况 | 操作 |
|------|------|
| 项目已存在 | 检查是否是正确的项目；使用它或使用不同的密钥创建 |
| 需要多个项目 | 为每个服务/区域/团队分别创建 |
| 服务之间共享配置 | 使用相同的项目，通过 SDK 上下文区分 |
| 令牌缺乏权限 | 请求 `projects:write` 或使用 MCP 服务器 |
| 项目名称冲突 | 密钥必须唯一，名称可以相似 |

## 不要做的事情

- 在理解用例之前不要创建项目
- 不要将 API 令牌或 SDK 密钥提交到版本控制
- 不要在测试/开发环境中使用生产 SDK 密钥
- 不要不必要地创建重复项目
- 不要跳过探索阶段

## 下一步

设置项目后：

1. **创建配置** - 使用 `configs-create` 技能
2. **设置 SDK 集成** - 使用 `sdk` 技能
3. **配置目标** - 使用 `configs-targeting` 技能

## 相关技能

- `configs-create` - 在项目中创建配置
- `sdk` - 在您的应用程序中集成 SDK
- `configs-targeting` - 配置配置目标
- `configs-variations` - 管理配置变体

## 参考资料

- [Python 实现](references/python-setup.md)
- [Node.js 实现](references/nodejs-setup.md)
- [Go 实现](references/go-setup.md)
- [快速入门指南](references/quick-start.md)
- [环境配置](references/env-config.md)
- [项目克隆](references/project-cloning.md)
- [IaC/自动化](references/iac-automation.md)
- [管理工具](references/admin-tooling.md)
