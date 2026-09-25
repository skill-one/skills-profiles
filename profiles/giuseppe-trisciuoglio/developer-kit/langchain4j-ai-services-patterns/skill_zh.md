# LangChain4j AI服务模式

本技能提供使用基于接口的模式、系统及用户消息的注解、内存管理、工具集成以及抽象低级LLM交互的高级AI应用模式来构建声明式AI服务的指导。

## 概述

LangChain4j AI服务使用Java接口和注解定义AI功能，提供类型安全的声明式AI，并具有极少的样板代码。

## 使用场景

使用本技能的场景包括：
- 使用Java接口构建具有极少样板代码的声明式AI服务
- 创建具有内存管理的类型安全对话式AI
- 实现具有函数/工具调用能力的AI代理
- 设计返回结构化数据（枚举、POJO、列表）的AI服务
- 声明式集成RAG模式

## 使用说明

按照以下步骤使用LangChain4j创建声明式AI服务：

### 1. 定义AI服务接口

创建具有AI交互方法签名的Java接口：

```java
interface Assistant {
    String chat(String userMessage);
}
```

### 2. 添加系统及用户消息的注解

使用`@SystemMessage`和`@UserMessage`注解定义提示：

```java
interface CustomerSupportBot {
    @SystemMessage("你是一名TechCorp的有帮助的客户支持代理")
    String handleInquiry(String customerMessage);

    @UserMessage("分析情绪：{{it}}")
    Sentiment analyzeSentiment(String feedback);
}
```

### 3. 创建AI服务实例

使用`AiServices`构建器或创建来实例化服务：

```java
// 简单创建
Assistant assistant = AiServices.create(Assistant.class, chatModel);

// 或使用构建器进行高级配置
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .build();
```

### 4. 配置多轮对话的内存

使用`@MemoryId`添加内存管理以支持多用户场景：

```java
interface MultiUserAssistant {
    String chat(@MemoryId String userId, String userMessage);
}

Assistant assistant = AiServices.builder(MultiUserAssistant.class)
    .chatModel(model)
    .chatMemoryProvider(userId -> MessageWindowChatMemory.withMaxMessages(10))
    .build();
```

### 5. 集成工具进行函数调用

使用`@Tool`注解注册工具以启用AI函数执行：

```java
class Calculator {
    @Tool("添加两个数字") double add(double a, double b) { return a + b; }
}

interface MathGenius {
    String ask(String question);
}

MathGenius mathGenius = AiServices.builder(MathGenius.class)
    .chatModel(model)
    .tools(new Calculator())
    .build();
```

### 6. 验证和测试

使用具体验证模式测试AI服务：

```java
// 1. 使用示例输入测试
String response = assistant.chat("你好，你好吗？");
assert response != null && !response.isEmpty();

// 2. 使用断言验证结构化输出
Sentiment result = bot.analyzeSentiment("很棒的产品！");
assert result == Sentiment.POSITIVE;

// 3. 记录具有副作用的工具调用以进行审计
MathGenius math = AiServices.builder(MathGenius.class)
    .chatModel(model)
    .tools(new Calculator())
    .build();

// 4. 测试用户之间的内存隔离
String userA = assistant.chat("用户A消息", "session-a");
String userB = assistant.chat("用户B消息", "session-b");
assert !userA.equals(userB); // 验证内存隔离
```

## 示例

参见[examples.md](references/examples.md)获取包括以下内容的全面实用示例：
- 基本聊天接口
- 具有内存的状态助手
- 多用户场景
- 结构化输出提取
- 工具调用和函数执行
- 流式响应
- 错误处理
- RAG集成
- 生产模式

## API参考

完整的API文档、注解、接口和配置模式可在[references.md](references/references.md)中找到。

## 最佳实践

1. **使用类型安全的接口**而不是基于字符串的提示
2. **实现适当的内存管理**并设置合适的限制
3. **设计清晰的工具描述**并包含参数文档
4. **优雅地处理错误**使用自定义错误处理器
5. **使用结构化输出**以获得可预测的响应
6. **实现用户输入验证**
7. **监控性能**以支持生产部署

## 依赖项

```xml
<!-- Maven -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.8.0</version>
</dependency>
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.8.0</version>
</dependency>
```

```gradle
// Gradle
implementation 'dev.langchain4j:langchain4j:1.8.0'
implementation 'dev.langchain4j:langchain4j-open-ai:1.8.0'
```

## 参考

- [LangChain4j文档](https://langchain4j.com/docs/)
- [LangChain4j AI服务 - API参考](references/references.md)
- [LangChain4j AI服务 - 实用示例](references/examples.md)

## 限制和警告

- AI服务依赖于LLM响应，这些响应是非确定性的；测试应考虑可变性。
- 内存提供商会存储对话历史；确保在多用户场景中进行适当的清理。
- 工具执行可能成本较高；实现速率限制和超时处理。
- 不要在系统或用户消息中传递敏感数据（API密钥、密码）。
- 大型上下文窗口可能导致高令牌成本；实现消息修剪策略。
- 流式响应需要适当的错误处理以支持部分失败。
- 在生产系统中使用AI生成的输出前应进行验证。
- 对具有副作用的工具要谨慎；AI模型可能会意外调用它们。
- 令牌限制因模型而异；确保提示和上下文符合模型限制。
