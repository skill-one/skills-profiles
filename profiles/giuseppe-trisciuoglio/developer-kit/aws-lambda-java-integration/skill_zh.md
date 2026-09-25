# AWS Lambda Java 集成

创建高性能 AWS Lambda 函数的 Java 模式，优化冷启动。

## 概述

本技能提供完整的 AWS Lambda Java 开发模式，涵盖两种主要方法：

1. **Micronaut 框架** - 具有完整功能的框架，支持 AOT 编译、依赖注入，冷启动 < 1 秒
2. **原始 Java** - 最小开销方法，冷启动 < 500 毫秒

两种方法都支持 API Gateway 和 ALB 集成，并提供生产就绪的配置。

## 何时使用

- 部署 Java 函数到 AWS Lambda
- 优化冷启动至 1 秒以下
- 选择 Micronaut 和原始 Java 方法
- 配置 API Gateway 或 ALB 集成
- 设置 Java Lambda 的 CI/CD 管道

## 说明

### 1. 选择方法

| 方法 | 冷启动 | 适合场景 | 复杂度 |
|------|--------|----------|--------|
| Micronaut | < 1 秒 | 复杂应用、需要 DI、企业级 | 中等 |
| 原始 Java | < 500 毫秒 | 简单处理器、最小开销 | 低 |

**验证**：在继续之前确认方法是否符合您的用例。

### 2. 项目结构

```
my-lambda-function/
├── build.gradle (或 pom.xml)
├── src/main/java/com/example/Handler.java
└── serverless.yml (或 template.yaml)
```

**验证**：验证项目结构是否与模板匹配。

### 3. 实现示例

#### Micronaut 处理器

```java
@FunctionBean("my-function")
public class MyFunction implements Function<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    private final MyService service;

    public MyFunction(MyService service) {
        this.service = service;
    }

    @Override
    public APIGatewayProxyResponseEvent apply(APIGatewayProxyRequestEvent request) {
        // 处理请求
        return new APIGatewayProxyResponseEvent()
            .withStatusCode(200)
            .withBody("{\"message\": \"Success\"}");
    }
}
```

#### 原始 Java 处理器

```java
public class MyHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    private static final MyService service = new MyService();

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        return new APIGatewayProxyResponseEvent()
            .withStatusCode(200)
            .withBody("{\"message\": \"Success\"}");
    }
}
```

**验证**：在部署前运行 `sam local invoke` 验证处理器是否正常工作。

## 核心模式

### 连接管理

```java
// 一次性初始化，跨调用重用
private static final DynamoDbClient dynamoDb = DynamoDbClient.builder()
    .region(Region.US_EAST_1)
    .build();

// 避免：在处理器中创建客户端（每次调用都变慢）
```

### 错误处理

```java
@Override
public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
    try {
        return successResponse(process(request));
    } catch (ValidationException e) {
        return errorResponse(400, e.getMessage());
    } catch (Exception e) {
        context.getLogger().log("Error: " + e.getMessage());
        return errorResponse(500, "Internal error");
    }
}
```

## 最佳实践

### 配置

- **内存**：从 512MB 开始，根据分析调整
- **超时**：Micronaut 10-30 秒，原始 Java 5-10 秒
- **运行时**：Java 17 或 21 以获得最佳性能

### 打包

- 使用 Gradle Shadow 插件或 Maven Shade 插件
- 排除不必要的依赖

### 监控

- 启用 X-Ray 追踪以进行性能分析
- 使用 CloudWatch Insights 跟踪冷启动与热启动

## 部署选项

### Serverless Framework

```yaml
service: my-java-lambda
provider:
  name: aws
  runtime: java21
  memorySize: 512
  timeout: 10
package:
  artifact: build/libs/function.jar
functions:
  api:
    handler: com.example.Handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

**验证**：首先使用 `--stage dev` 运行 `serverless deploy`。

### AWS SAM

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      Runtime: java21
      MemorySize: 512
      Timeout: 10
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

**验证**：在部署前运行 `sam validate`。

## 限制和警告

### Java 特定限制

- **反射**：最小化使用；优先使用 AOT 编译（Micronaut）
- **类路径扫描**：减慢冷启动；使用显式配置
- **大型框架**：Spring Boot 增加显著冷启动开销

### 常见陷阱

1. **处理器中初始化** - 导致热调用重复工作
2. **过大的 JAR** - 仅包含必要的依赖
3. **内存不足** - Java 比 Node.js/Python 需要更多内存
4. **无超时处理** - 始终设置适当的超时

## 参考

有关特定主题的详细指导：

- **[Micronaut Lambda](references/micronaut-lambda.md)** - 完整 Micronaut 设置、AOT 配置、DI 优化
- **[原始 Java Lambda](references/raw-java-lambda.md)** - 最小处理器模式、单例缓存、JAR 打包
- **[Serverless 部署](references/serverless-deployment.md)** - Serverless Framework、SAM、CI/CD 管道、预置并发
- **[Lambda 测试](references/testing-lambda.md)** - JUnit 5、SAM Local、集成测试、性能测量

## 示例

### 示例 1：创建 Micronaut Lambda 函数

**输入：**
```
使用 Micronaut 创建处理用户 REST API 的 Java Lambda 函数
```

**处理：**
1. 使用 Micronaut 插件配置 Gradle 项目
2. 创建扩展 MicronautRequestHandler 的 Handler 类
3. 实现 GET/POST/PUT/DELETE 方法
4. 使用 application.yml 配置 AOT 优化
5. 使用 Shadow 插件设置打包
6. **验证**：在部署前使用 SAM CLI 本地测试

**输出：**
- 完整项目结构
- 具有依赖注入的处理器
- serverless.yml 部署配置

### 示例 2：优化原始 Java 的冷启动

**输入：**
```
我的 Java Lambda 冷启动为 3 秒，如何优化？
```

**处理：**
1. 分析初始化代码
2. 将 AWS 客户端创建移至静态字段
3. 在 build.gradle 中减少依赖
4. 配置优化的 JVM 选项
5. 考虑预置并发
6. **验证**：在更改后使用 CloudWatch 指标测量冷启动

**输出：**
- 使用单例模式的重构代码
- 最小化 JAR
- 冷启动 < 500 毫秒

### 示例 3：使用 GitHub Actions 部署

**输入：**
```
使用 SAM 配置 Java Lambda 的 CI/CD
```

**处理：**
1. 创建 GitHub Actions 工作流
2. 使用 Shadow 配置 Gradle 构建
3. 设置 SAM 构建和部署
4. 部署前添加测试阶段
5. 配置生产环境保护

**输出：**
- 完整的 .github/workflows/deploy.yml
- 多阶段管道（dev/staging/prod）
- 集成测试自动化

## 版本

版本：1.0.0
