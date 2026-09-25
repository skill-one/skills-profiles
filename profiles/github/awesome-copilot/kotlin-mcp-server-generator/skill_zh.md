# Kotlin MCP 服务器项目生成器

生成一个完整的、可用于生产的模型上下文协议（MCP）服务器项目。

## 项目要求

您将创建一个 Kotlin MCP 服务器，包含：

1. **项目结构**：基于 Gradle 的 Kotlin 项目布局
2. **依赖项**：官方 MCP SDK、Ktor 和 kotlinx 库
3. **服务器设置**：配置好的 MCP 服务器及传输方式
4. **工具**：至少 2-3 个具有类型化输入/输出的实用工具
5. **错误处理**：适当的异常处理和验证
6. **文档**：包含设置和使用说明的 README
7. **测试**：带有协程的基本测试结构

## 模板结构

```
myserver/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── src/
│   ├── main/
│   │   └── kotlin/
│   │       └── com/example/myserver/
│   │           ├── Main.kt
│   │           ├── Server.kt
│   │           ├── config/
│   │           │   └── Config.kt
│   │           └── tools/
│   │               ├── Tool1.kt
│   │               └── Tool2.kt
│   └── test/
│       └── kotlin/
│           └── com/example/myserver/
│               └── ServerTest.kt
└── README.md
```

## build.gradle.kts 模板

```kotlin
plugins {
    kotlin("jvm") version "2.1.0"
    kotlin("plugin.serialization") version "2.1.0"
    application
}

group = "com.example"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("io.modelcontextprotocol:kotlin-sdk:0.7.2")
    
    // Ktor 用于传输
    implementation("io.ktor:ktor-server-netty:3.0.0")
    implementation("io.ktor:ktor-client-cio:3.0.0")
    
    // 序列化
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    
    // 协程
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
    
    // 日志记录
    implementation("io.github.oshai:kotlin-logging-jvm:7.0.0")
    implementation("ch.qos.logback:logback-classic:1.5.12")
    
    // 测试
    testImplementation(kotlin("test"))
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
}

application {
    mainClass.set("com.example.myserver.MainKt")
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(17)
}
```

## settings.gradle.kts 模板

```kotlin
rootProject.name = "{{PROJECT_NAME}}"
```

## Main.kt 模板

```kotlin
package com.example.myserver

import io.modelcontextprotocol.kotlin.sdk.server.StdioServerTransport
import kotlinx.coroutines.runBlocking
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

fun main() = runBlocking {
    logger.info { "启动 MCP 服务器..." }
    
    val config = loadConfig()
    val server = createServer(config)
    
    // 使用 stdio 传输
    val transport = StdioServerTransport()
    
    logger.info { "服务器 '${config.name}' v${config.version} 已准备就绪" }
    server.connect(transport)
}
```

## Server.kt 模板

```kotlin
package com.example.myserver

import io.modelcontextprotocol.kotlin.sdk.server.Server
import io.modelcontextprotocol.kotlin.sdk.server.ServerOptions
import io.modelcontextprotocol.kotlin.sdk.Implementation
import io.modelcontextprotocol.kotlin.sdk.ServerCapabilities
import com.example.myserver.tools.registerTools

fun createServer(config: Config): Server {
    val server = Server(
        serverInfo = Implementation(
            name = config.name,
            version = config.version
        ),
        options = ServerOptions(
            capabilities = ServerCapabilities(
                tools = ServerCapabilities.Tools(),
                resources = ServerCapabilities.Resources(
                    subscribe = true,
                    listChanged = true
                ),
                prompts = ServerCapabilities.Prompts(listChanged = true)
            )
        )
    ) {
        config.description
    }
    
    // 注册所有工具
    server.registerTools()
    
    return server
}
```

## Config.kt 模板

```kotlin
package com.example.myserver.config

import kotlinx.serialization.Serializable

@Serializable
data class Config(
    val name: String = "{{PROJECT_NAME}}",
    val version: String = "1.0.0",
    val description: String = "{{PROJECT_DESCRIPTION}}"
)

fun loadConfig(): Config {
    return Config(
        name = System.getenv("SERVER_NAME") ?: "{{PROJECT_NAME}}",
        version = System.getenv("VERSION") ?: "1.0.0",
        description = System.getenv("DESCRIPTION") ?: "{{PROJECT_DESCRIPTION}}"
    )
}
```

## Tool1.kt 模板

```kotlin
package com.example.myserver.tools

import io.modelcontextprotocol.kotlin.sdk.server.Server
import io.modelcontextprotocol.kotlin.sdk.CallToolRequest
import io.modelcontextprotocol.kotlin.sdk.CallToolResult
import io.modelcontextprotocol.kotlin.sdk.TextContent
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import kotlinx.serialization.json.putJsonObject
import kotlinx.serialization.json.putJsonArray

fun Server.registerTool1() {
    addTool(
        name = "tool1",
        description = "tool1 的描述",
        inputSchema = buildJsonObject {
            put("type", "object")
            putJsonObject("properties") {
                putJsonObject("param1") {
                    put("type", "string")
                    put("description", "第一个参数")
                }
                putJsonObject("param2") {
                    put("type", "integer")
                    put("description", "可选的第二个参数")
                }
            }
            putJsonArray("required") {
                add("param1")
            }
        }
    ) { request: CallToolRequest ->
        // 提取和验证参数
        val param1 = request.params.arguments["param1"] as? String
            ?: throw IllegalArgumentException("param1 是必需的")
        val param2 = (request.params.arguments["param2"] as? Number)?.toInt() ?: 0
        
        // 执行工具逻辑
        val result = performTool1Logic(param1, param2)
        
        CallToolResult(
            content = listOf(
                TextContent(text = result)
            )
        )
    }
}

private fun performTool1Logic(param1: String, param2: Int): String {
    // 在此处实现工具逻辑
    return "处理：$param1 值 $param2"
}
```

## tools/ToolRegistry.kt 模板

```kotlin
package com.example.myserver.tools

import io.modelcontextprotocol.kotlin.sdk.server.Server

fun Server.registerTools() {
    registerTool1()
    registerTool2()
    // 在此处注册其他工具
}
```

## ServerTest.kt 模板

```kotlin
package com.example.myserver

import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse

class ServerTest {
    
    @Test
    fun `测试服务器创建`() = runTest {
        val config = Config(
            name = "test-server",
            version = "1.0.0",
            description = "测试服务器"
        )
        
        val server = createServer(config)
        
        assertEquals("test-server", server.serverInfo.name)
        assertEquals("1.0.0", server.serverInfo.version)
    }
    
    @Test
    fun `测试 tool1 执行`() = runTest {
        val config = Config()
        val server = createServer(config)
        
        // 测试工具执行
        // 注意：您需要实现适当的测试工具调用服务器
    }
}
```

## README.md 模板

```markdown
# {{PROJECT_NAME}}

一个使用 Kotlin 构建的模型上下文协议（MCP）服务器。

## 描述

{{PROJECT_DESCRIPTION}}

## 要求

- Java 17 或更高版本
- Kotlin 2.1.0

## 安装

构建项目：

\`\`\`bash
./gradlew build
\`\`\`

## 使用

使用 stdio 传输运行服务器：

\`\`\`bash
./gradlew run
\`\`\`

或构建并运行 jar：

\`\`\`bash
./gradlew installDist
./build/install/{{PROJECT_NAME}}/bin/{{PROJECT_NAME}}
\`\`\`

## 配置

通过环境变量进行配置：

- `SERVER_NAME`：服务器名称（默认： "{{PROJECT_NAME}}"）
- `VERSION`：服务器版本（默认： "1.0.0"）
- `DESCRIPTION`：服务器描述

## 可用工具

### tool1
{{TOOL1_DESCRIPTION}}

**输入：**
- `param1` (string, required)：第一个参数
- `param2` (integer, optional)：第二个参数

**输出：**
- 操作的文本结果

## 开发

运行测试：

\`\`\`bash
./gradlew test
\`\`\`

构建：

\`\`\`bash
./gradlew build
\`\`\`

开发模式自动重载运行：

\`\`\`bash
./gradlew run --continuous
\`\`\`

## 多平台

此项目使用 Kotlin Multiplatform，可以针对 JVM、Wasm 和 iOS。
有关平台配置，请参阅 `build.gradle.kts`。

## 许可证

MIT
```

## 生成说明

生成 Kotlin MCP 服务器时：

1. **Gradle 设置**：创建包含所有依赖项的 `build.gradle.kts`
2. **包结构**：遵循 Kotlin 包规范
3. **类型安全**：使用数据类和 kotlinx.serialization
4. **协程**：所有操作应为挂起函数
5. **错误处理**：使用 Kotlin 异常和验证
6. **JSON 模式**：使用 `buildJsonObject` 为工具模式
7. **测试**：包含协程测试工具
8. **日志记录**：使用 kotlin-logging 进行结构化日志记录
9. **配置**：使用数据类和环境变量
10. **文档**：公共 API 的 KDoc 注释

## 最佳实践

- 使用挂起函数进行所有异步操作
- 利用 Kotlin 的空安全和类型系统
- 使用数据类进行结构化数据
- 应用 kotlinx.serialization 进行 JSON 处理
- 使用密封类为结果类型
- 使用 Result/Either 模式实现适当的错误处理
- 使用 kotlinx-coroutines-test 编写测试
- 使用依赖注入提高可测试性
- 遵循 Kotlin 编码规范
- 使用有意义的名称和 KDoc 注释

## 传输选项

### Stdio 传输
```kotlin
val transport = StdioServerTransport()
server.connect(transport)
```

### SSE 传输（Ktor）
```kotlin
embeddedServer(Netty, port = 8080) {
    mcp {
        Server(/*...*/) { "描述" }
    }
}.start(wait = true)
```

## 多平台配置

对于多平台项目，在 `build.gradle.kts` 中添加：

```kotlin
kotlin {
    jvm()
    js(IR) { nodejs() }
    wasmJs()
    
    sourceSets {
        commonMain.dependencies {
            implementation("io.modelcontextprotocol:kotlin-sdk:0.7.2")
        }
    }
}
```
