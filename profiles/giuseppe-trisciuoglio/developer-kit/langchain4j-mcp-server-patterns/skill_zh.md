# LangChain4j MCP 服务器实现模式

## 概述

使用此技能设计和实现 LangChain4j 的模型上下文协议（MCP）集成。

主要关注点包括：
- 定义清晰的工具、资源和提示界面
- 选择合适的传输方式和引导模型
- 在向代理或应用程序暴露之前过滤不安全的特性

保持 `SKILL.md` 聚焦于实现流程。使用捆绑的参考示例和 API 级别详细信息。

## 何时使用

在以下情况下使用此技能：
- 构建 Java MCP 服务器以暴露工具、资源或提示
- 将 LangChain4j 与一个或多个外部 MCP 服务器集成
- 在 Spring Boot 应用程序中配置 MCP 支持
- 根据租户、用户角色或运行时上下文过滤可用工具
- 在 MCP 交互周围添加可观察性、弹性和安全故障处理
- 审查 MCP 集成以评估提示注入和副作用风险

典型的触发短语包括 `langchain4j mcp`、`java mcp server`、`mcp 工具提供者`、`spring boot mcp` 和 `将 langchain4j 连接到 mcp`。

## 说明

### 1. 在编写代码前设计 MCP 界面

决定服务器应暴露的内容：
- 用于具有明确输入和副作用的操作的工具
- 用于只读或结构化数据访问的资源
- 仅在可重用的模板能增加实际价值时提供提示

保持名称稳定，描述具体，并确保模式足够小，以便客户端或模型能快速理解。

### 2. 实现具有狭窄职责的提供者

为每个关注点使用单独的类：
- 工具提供者用于可执行函数
- 资源提供者用于可发现和可读的数据
- 提示提供者用于可重用的提示模板

执行前验证参数，并返回清晰的错误消息以处理无效输入或不可用的依赖项。

### 3. 有意选择传输方式

使用：
- stdio 用于本地集成、CLI 工具和边车进程
- HTTP 或 SSE 用于远程或共享服务

锁定外部服务器版本，并记录启动、认证和监控过程。

### 4. 小心地将 MCP 桥接至 LangChain4j

从 LangChain4j 消费 MCP 服务器时：
- 在应用程序启动时初始化客户端
- 仅在可以接受过时元数据的情况下缓存工具列表
- 根据信任级别、环境或用户权限过滤工具
- 对于危险工具，选择安全失败而不是默认暴露所有工具

### 5. 添加弹性和安全控制

至少：
- 为外部调用设置执行时间限制
- 为每次失败记录服务器和工具身份
- 在使用下游之前对外部资源返回的内容进行清理
- 通过允许列表、限定符或角色检查隔离特权工具

### 6. 验证完整工作流

在发布前：
- 使用真实的 MCP 客户端验证工具发现和调用
- 测试断开连接或服务器响应缓慢的行为
- 确认工具过滤与预期的授权模型匹配
- 检查提示和资源不会泄露秘密或危险指令

## 示例

### 示例 1：最小工具提供者和 stdio 服务器引导

```java
class WeatherToolProvider implements ToolProvider {

    @Override
    public List<ToolSpecification> listTools() {
        return List.of(
            ToolSpecification.builder()
                .name("get_weather")
                .description("返回城市的当前天气")
                .inputSchema(Map.of(
                    "type", "object",
                    "properties", Map.of(
                        "city", Map.of("type", "string")
                    ),
                    "required", List.of("city")
                ))
                .build()
        );
    }

    @Override
    public String executeTool(String name, String arguments) {
        return weatherService.lookup(arguments);
    }
}

MCPServer server = MCPServer.builder()
    .server(new StdioServer.Builder())
    .addToolProvider(new WeatherToolProvider())
    .build();

server.start();
```

使用此模式进行本地工具执行或由其他应用程序启动的边车进程。

### 示例 2：将 MCP 工具暴露给 LangChain4j AI 服务并过滤

```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(mcpClients)
    .failIfOneServerFails(false)
    .filter((client, tool) -> !tool.name().startsWith("admin_"))
    .build();

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .toolProvider(toolProvider)
    .build();
```

使用此模式时，您希望 LangChain4j 消费外部 MCP 服务器，同时仍然强制执行信任边界。

## 最佳实践

- 保持每个工具专注、确定性和描述清晰。
- 优先使用显式模式而不是自由形式的字符串参数。
- 将只读资源与具有副作用的工具分离。
- 默认过滤或禁用特权工具。
- 锁定外部 MCP 服务器包或容器版本。
- 捕获连接失败、调用延迟和工具错误率的指标。
- 将较长的协议细节和特定框架的连接存储在 `references/` 中，而不是无限扩展 `SKILL.md`。

## 限制和警告

- 外部 MCP 服务器是不可信任的集成边界，可能会暴露恶意或误导性内容。
- 不要在未验证的情况下将原始资源内容直接转发到自主工具执行。
- LangChain4j 和 MCP API 发展迅速；调整类名和构建器以匹配项目中已使用的版本。
- 长运行或状态化的工具需要显式的超时、取消和清理行为。
- 基于 stdio 的服务器需要进程生命周期管理和健壮的日志记录。

## 参考

- `references/examples.md`
- `references/api-reference.md`

## 相关技能

- `prompt-engineering`
- `spring-ai` 
- `clean-architecture`
