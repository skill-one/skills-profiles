# Java MCP 服务器生成器

使用官方 Java SDK 和 Maven 或 Gradle 生成一个完整的、可用于生产环境的 Java MCP 服务器。

## 项目生成

当被要求创建一个 Java MCP 服务器时，生成一个具有以下结构的完整项目：

```
my-mcp-server/
├── pom.xml (或 build.gradle.kts)
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/mcp/
│   │   │       ├── McpServerApplication.java
│   │   │       ├── config/
│   │   │       │   └── ServerConfiguration.java
│   │   │       ├── tools/
│   │   │       │   ├── ToolDefinitions.java
│   │   │       │   └── ToolHandlers.java
│   │   │       ├── resources/
│   │   │       │   ├── ResourceDefinitions.java
│   │   │       │   └── ResourceHandlers.java
│   │   │       └── prompts/
│   │   │           ├── PromptDefinitions.java
│   │   │           └── PromptHandlers.java
│   │   └── resources/
│   │       └── application.properties (如果使用 Spring)
│   └── test/
│       └── java/
│           └── com/example/mcp/
│               └── McpServerTest.java
└── README.md
```

## Maven pom.xml 模板

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>my-mcp-server</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>My MCP Server</name>
    <description>Model Context Protocol 服务器实现</description>

    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <mcp.version>0.14.1</mcp.version>
        <slf4j.version>2.0.9</slf4j.version>
        <logback.version>1.4.11</logback.version>
        <junit.version>5.10.0</junit.version>
    </properties>

    <dependencies>
        <!-- MCP Java SDK -->
        <dependency>
            <groupId>io.modelcontextprotocol.sdk</groupId>
            <artifactId>mcp</artifactId>
            <version>${mcp.version}</version>
        </dependency>

        <!-- Logging -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>${slf4j.version}</version>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <version>${logback.version}</version>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.projectreactor</groupId>
            <artifactId>reactor-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.1.2</version>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.5.0</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <transformers>
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>com.example.mcp.McpServerApplication</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

## Gradle build.gradle.kts 模板

```kotlin
plugins {
    id("java")
    id("application")
}

group = "com.example"
version = "1.0.0"

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    // MCP Java SDK
    implementation("io.modelcontextprotocol.sdk:mcp:0.14.1")
    
    // Logging
    implementation("org.slf4j:slf4j-api:2.0.9")
    implementation("ch.qos.logback:logback-classic:1.4.11")
    
    // Testing
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
    testImplementation("io.projectreactor:reactor-test:3.5.0")
}

application {
    mainClass.set("com.example.mcp.McpServerApplication")
}

tasks.test {
    useJUnitPlatform()
}
```

## McpServerApplication.java 模板

```java
package com.example.mcp;

import com.example.mcp.tools.ToolHandlers;
import com.example.mcp.resources.ResourceHandlers;
import com.example.mcp.prompts.PromptHandlers;
import io.mcp.server.McpServer;
import io.mcp.server.McpServerBuilder;
import io.mcp.server.transport.StdioServerTransport;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import reactor.core.Disposable;

public class McpServerApplication {
    
    private static final Logger log = LoggerFactory.getLogger(McpServerApplication.class);
    
    public static void main(String[] args) {
        log.info("Starting MCP Server...");
        
        try {
            McpServer server = createServer();
            StdioServerTransport transport = new StdioServerTransport();
            
            // Start server
            Disposable serverDisposable = server.start(transport).subscribe();
            
            // Graceful shutdown
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                log.info("Shutting down MCP server");
                serverDisposable.dispose();
                server.stop().block();
            }));
            
            log.info("MCP Server started successfully");
            
            // Keep running
            Thread.currentThread().join();
            
        } catch (Exception e) {
            log.error("Failed to start MCP server", e);
            System.exit(1);
        }
    }
    
    private static McpServer createServer() {
        McpServer server = McpServerBuilder.builder()
            .serverInfo("my-mcp-server", "1.0.0")
            .capabilities(capabilities -> capabilities
                .tools(true)
                .resources(true)
                .prompts(true))
            .build();
        
        // Register handlers
        ToolHandlers.register(server);
        ResourceHandlers.register(server);
        PromptHandlers.register(server);
        
        return server;
    }
}
```

## ToolDefinitions.java 模板

```java
package com.example.mcp.tools;

import io.mcp.json.JsonSchema;
import io.mcp.server.tool.Tool;

import java.util.List;

public class ToolDefinitions {
    
    public static List<Tool> getTools() {
        return List.of(
            createGreetTool(),
            createCalculateTool()
        );
    }
    
    private static Tool createGreetTool() {
        return Tool.builder()
            .name("greet")
            .description("生成问候信息")
            .inputSchema(JsonSchema.object()
                .property("name", JsonSchema.string()
                    .description("要问候的名称")
                    .required(true)))
            .build();
    }
    
    private static Tool createCalculateTool() {
        return Tool.builder()
            .name("calculate")
            .description("执行数学计算")
            .inputSchema(JsonSchema.object()
                .property("operation", JsonSchema.string()
                    .description("要执行的操作")
                    .enumValues(List.of("add", "subtract", "multiply", "divide"))
                    .required(true))
                .property("a", JsonSchema.number()
                    .description("第一个操作数")
                    .required(true))
                .property("b", JsonSchema.number()
                    .description("第二个操作数")
                    .required(true)))
            .build();
    }
}
```

## ToolHandlers.java 模板

```java
package com.example.mcp.tools;

import com.fasterxml.jackson.databind.JsonNode;
import io.mcp.server.McpServer;
import io.mcp.server.tool.ToolResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import reactor.core.publisher.Mono;

public class ToolHandlers {
    
    private static final Logger log = LoggerFactory.getLogger(ToolHandlers.class);
    
    public static void register(McpServer server) {
        // 注册工具列表处理器
        server.addToolListHandler(() -> {
            log.debug("列出可用工具");
            return Mono.just(ToolDefinitions.getTools());
        });
        
        // 注册 greet 处理器
        server.addToolHandler("greet", ToolHandlers::handleGreet);
        
        // 注册 calculate 处理器
        server.addToolHandler("calculate", ToolHandlers::handleCalculate);
    }
    
    private static Mono<ToolResponse> handleGreet(JsonNode arguments) {
        log.info("greet 工具被调用");
        
        if (!arguments.has("name")) {
            return Mono.just(ToolResponse.error()
                .message("缺少 'name' 参数")
                .build());
        }
        
        String name = arguments.get("name").asText();
        String greeting = "你好，" + name + "! 欢迎使用 MCP。";
        
        log.debug("为 {} 生成了问候信息", name);
        
        return Mono.just(ToolResponse.success()
            .addTextContent(greeting)
            .build());
    }
    
    private static Mono<ToolResponse> handleCalculate(JsonNode arguments) {
        log.info("calculate 工具被调用");
        
        if (!arguments.has("operation") || !arguments.has("a") || !arguments.has("b")) {
            return Mono.just(ToolResponse.error()
                .message("缺少必要参数")
                .build());
        }
        
        String operation = arguments.get("operation").asText();
        double a = arguments.get("a").asDouble();
        double b = arguments.get("b").asDouble();
        
        double result;
        switch (operation) {
            case "add":
                result = a + b;
                break;
            case "subtract":
                result = a - b;
                break;
            case "multiply":
                result = a * b;
                break;
            case "divide":
                if (b == 0) {
                    return Mono.just(ToolResponse.error()
                        .message("除以零")
                        .build());
                }
                result = a / b;
                break;
            default:
                return Mono.just(ToolResponse.error()
                    .message("未知操作: " + operation)
                    .build());
        }
        
        log.debug("计算: {} {} {} = {}", a, operation, b, result);
        
        return Mono.just(ToolResponse.success()
            .addTextContent("结果: " + result)
            .build());
    }
}
```

## ResourceDefinitions.java 模板

```java
package com.example.mcp.resources;

import io.mcp.server.resource.Resource;

import java.util.List;

public class ResourceDefinitions {
    
    public static List<Resource> getResources() {
        return List.of(
            Resource.builder()
                .name("示例数据")
                .uri("resource://data/example")
                .description("示例资源数据")
                .mimeType("application/json")
                .build(),
            Resource.builder()
                .name("配置")
                .uri("resource://config")
                .description("服务器配置")
                .mimeType("application/json")
                .build()
        );
    }
}
```

## ResourceHandlers.java 模板

```java
package com.example.mcp.resources;

import io.mcp.server.McpServer;
import io.mcp.server.resource.ResourceContent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import reactor.core.publisher.Mono;

import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ResourceHandlers {
    
    private static final Logger log = LoggerFactory.getLogger(ResourceHandlers.class);
    private static final Map<String, Boolean> subscriptions = new ConcurrentHashMap<>();
    
    public static void register(McpServer server) {
        // 注册资源列表处理器
        server.addResourceListHandler(() -> {
            log.debug("列出可用资源");
            return Mono.just(ResourceDefinitions.getResources());
        });
        
        // 注册资源读取处理器
        server.addResourceReadHandler(ResourceHandlers::handleRead);
        
        // 注册资源订阅处理器
        server.addResourceSubscribeHandler(ResourceHandlers::handleSubscribe);
        
        // 注册资源取消订阅处理器
        server.addResourceUnsubscribeHandler(ResourceHandlers::handleUnsubscribe);
    }
    
    private static Mono<ResourceContent> handleRead(String uri) {
        log.info("读取资源: {}", uri);
        
        switch (uri) {
            case "resource://data/example":
                String jsonData = String.format(
                    "{\"message\":\"示例资源数据\",\"timestamp\":\"%s\"}",
                    Instant.now()
                );
                return Mono.just(ResourceContent.text(jsonData, uri, "application/json"));
                
            case "resource://config":
                String config = "{\"serverName\":\"my-mcp-server\",\"version\":\"1.0.0\"}";
                return Mono.just(ResourceContent.text(config, uri, "application/json"));
                
            default:
                log.warn("请求未知资源: {}", uri);
                return Mono.error(new IllegalArgumentException("未知资源 URI: " + uri));
        }
    }
    
    private static Mono<Void> handleSubscribe(String uri) {
        log.info("客户端订阅了资源: {}", uri);
        subscriptions.put(uri, true);
        return Mono.empty();
    }
    
    private static Mono<Void> handleUnsubscribe(String uri) {
        log.info("客户端取消订阅了资源: {}", uri);
        subscriptions.remove(uri);
        return Mono.empty();
    }
}
```

## PromptDefinitions.java 模板

```java
package com.example.mcp.prompts;

import io.mcp.server.prompt.Prompt;
import io.mcp.server.prompt.PromptArgument;

import java.util.List;

public class PromptDefinitions {
    
    public static List<Prompt> getPrompts() {
        return List.of(
            Prompt.builder()
                .name("code-review")
                .description("生成代码审查提示")
                .argument(PromptArgument.builder()
                    .name("language")
                    .description("编程语言")
                    .required(true)
                    .build())
                .argument(PromptArgument.builder()
                    .name("focus")
                    .description("审查重点区域")
                    .required(false)
                    .build())
                .build()
        );
    }
}
```

## PromptHandlers.java 模板

```java
package com.example.mcp.prompts;

import io.mcp.server.McpServer;
import io.mcp.server.prompt.PromptMessage;
import io.mcp.server.prompt.PromptResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;

public class PromptHandlers {
    
    private static final Logger log = LoggerFactory.getLogger(PromptHandlers.class);
    
    public static void register(McpServer server) {
        // 注册提示列表处理器
        server.addPromptListHandler(() -> {
            log.debug("列出可用提示");
            return Mono.just(PromptDefinitions.getPrompts());
        });
        
        // 注册提示获取处理器
        server.addPromptGetHandler(PromptHandlers::handleCodeReview);
    }
    
    private static Mono<PromptResult> handleCodeReview(String name, Map<String, String> arguments) {
        log.info("获取提示: {}", name);
        
        if (!name.equals("code-review")) {
            return Mono.error(new IllegalArgumentException("未知提示: " + name));
        }
        
        String language = arguments.getOrDefault("language", "Java");
        String focus = arguments.getOrDefault("focus", "一般质量");
        
        String description = "针对 " + language + " 的代码审查，重点区域为 " + focus;
        
        List<PromptMessage> messages = List.of(
            PromptMessage.user("请审查这段 " + language + " 代码，重点区域为 " + focus + "."),
            PromptMessage.assistant("我将针对 " + focus + " 审查代码。请分享代码。"),
            PromptMessage.user("这是要审查的代码: [在此处粘贴代码]")
        );
        
        log.debug("生成了针对 {} ({}) 的代码审查提示", language, focus);
        
        return Mono.just(PromptResult.builder()
            .description(description)
            .messages(messages)
            .build());
    }
}
```

## McpServerTest.java 模板

```java
package com.example.mcp;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.mcp.server.McpServer;
import io.mcp.server.McpSyncServer;
import io.mcp.server.tool.ToolResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class McpServerTest {
    
    private McpSyncServer syncServer;
    private ObjectMapper objectMapper;
    
    @BeforeEach
    void setUp() {
        McpServer server = createTestServer();
        syncServer = server.toSyncServer();
        objectMapper = new ObjectMapper();
    }
    
    private McpServer createTestServer() {
        // 与主应用程序相同的设置
        McpServer server = McpServerBuilder.builder()
            .serverInfo("test-server", "1.0.0")
            .capabilities(cap -> cap.tools(true))
            .build();
        
        // 注册处理器
        ToolHandlers.register(server);
        
        return server;
    }
    
    @Test
    void testGreetTool() {
        ObjectNode args = objectMapper.createObjectNode();
        args.put("name", "Java");
        
        ToolResponse response = syncServer.callTool("greet", args);
        
        assertFalse(response.isError());
        assertEquals(1, response.getContent().size());
        assertTrue(response.getContent().get(0).getText().contains("Java"));
    }
    
    @Test
    void testCalculateTool() {
        ObjectNode args = objectMapper.createObjectNode();
        args.put("operation", "add");
        args.put("a", 5);
        args.put("b", 3);
        
        ToolResponse response = syncServer.callTool("calculate", args);
        
        assertFalse(response.isError());
        assertTrue(response.getContent().get(0).getText().contains("8"));
    }
    
    @Test
    void testDivideByZero() {
        ObjectNode args = objectMapper.createObjectNode();
        args.put("operation", "divide");
        args.put("a", 10);
        args.put("b", 0);
        
        ToolResponse response = syncServer.callTool("calculate", args);
        
        assertTrue(response.isError());
    }
}
```

## README.md 模板

````markdown
# My MCP Server

一个使用 Java 和官方 MCP Java SDK 构建的 Model Context Protocol 服务器。

## 功能

- ✅ 工具: greet, calculate
- ✅ 资源: 示例数据, 配置
- ✅ 提示: code-review
- ✅ 使用 Project Reactor 的响应式流
- ✅ 使用 SLF4J 的结构化日志记录
- ✅ 完整的测试覆盖率

## 要求

- Java 17 或更高版本
- Maven 3.6+ 或 Gradle 7+

## 构建

### Maven
```bash
mvn clean package
```

### Gradle
```bash
./gradlew build
```

## 运行

### Maven
```bash
java -jar target/my-mcp-server-1.0.0.jar
```

### Gradle
```bash
./gradlew run
```

## 测试

### Maven
```bash
mvn test
```

### Gradle
```bash
./gradlew test
```

## 与 Claude Desktop 集成

添加到 `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "java",
      "args": ["-jar", "/path/to/my-mcp-server-1.0.0.jar"]
    }
  }
}
```

## 许可证

MIT
````

## 生成说明

1. **询问项目名称和包名**
2. **选择构建工具** (Maven 或 Gradle)
3. **生成所有文件** 并具有正确的包结构
4. **使用响应式流** 用于异步处理器
5. **包含全面的日志记录** 使用 SLF4J
6. **为所有处理器添加测试**
7. **遵循 Java 习惯** (camelCase, PascalCase)
8. **包含错误处理** 并提供适当的响应
9. **使用 Javadoc 记录公共 API**
10. **提供同步和异步** 示例
