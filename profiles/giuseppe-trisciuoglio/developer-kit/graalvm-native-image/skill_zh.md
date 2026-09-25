# GraalVM Native Image for Java Applications

使用 GraalVM Native Image 将 Java 应用程序编译为高性能原生可执行文件的专业技能，可大幅减少启动时间和内存消耗。

## 概述

GraalVM Native Image 将 Java 应用程序在编译时（AOT）编译为独立的原生可执行文件。这些可执行文件以毫秒级启动，比基于 JVM 的部署需要显著更少的内存，并且非常适合无服务器函数、CLI 工具和微服务，其中快速启动和低资源使用至关重要。

此技能提供了一个结构化的工作流程，用于将 JVM 应用程序迁移到原生二进制文件，涵盖构建工具配置、框架特定模式、反射元数据管理以及解决原生构建错误的迭代方法。

## 何时使用

在以下情况下使用此技能：
- 将基于 JVM 的 Java 应用程序转换为 GraalVM 原生可执行文件
- 优化无服务器或容器化部署的冷启动时间
- 减少 Java 微服务的内存占用（RSS）
- 使用 GraalVM Native Build Tools 配置 Maven 或 Gradle
- 解决原生构建中的 `ClassNotFoundException`、`NoSuchMethodException` 或丢失资源错误
- 生成或编辑 `reflect-config.json`、`resource-config.json` 或其他 GraalVM 元数据文件
- 使用 GraalVM 追踪代理收集可达性元数据
- 实现 `RuntimeHints` 以支持 Spring Boot 原生
- 使用 Quarkus 或 Micronaut 构建原生镜像

## 说明

### 1. 上下文项目分析

在配置之前，分析项目以确定构建工具、框架和依赖项：

**检测构建工具：**

```bash
# 检查 Maven
if [ -f "pom.xml" ]; then
    echo "构建工具：Maven"
    # 检查 Maven 包装器
    [ -f "mvnw" ] && echo "Maven 包装器可用"
fi

# 检查 Gradle
if [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    echo "构建工具：Gradle"
    [ -f "build.gradle.kts" ] && echo "Kotlin DSL"
    [ -f "gradlew" ] && echo "Gradle 包装器可用"
fi
```

**通过分析依赖项检测框架：**

- **Spring Boot**：在 `pom.xml` 或 `build.gradle` 中查找 `spring-boot-starter-*`
- **Quarkus**：查找 `quarkus-*` 依赖项
- **Micronaut**：查找 `micronaut-*` 依赖项
- **纯 Java**：未检测到框架依赖项

**检查 Java 版本：**

```bash
java -version 2>&1
# GraalVM Native Image 需要 Java 17+（推荐：Java 21+）
```

**识别潜在的原生镜像挑战：**

- 反射密集型库（Jackson、Hibernate、JAXB）
- 动态代理使用（JDK 代理、CGLIB）
- 资源包和类路径资源
- JNI 或原生库依赖项
- 序列化要求

### 2. 构建工具配置

根据检测到的环境配置适当的构建工具插件。

**对于 Maven 项目**，向标准构建添加一个专门的 `native` 配置文件以保持其清洁。有关完整配置，请参阅 [Maven Native Profile 参考](references/maven-native-profile.md)。

关键的 Maven 设置：

```xml
<profiles>
  <profile>
    <id>native</id>
    <build>
      <plugins>
        <plugin>
          <groupId>org.graalvm.buildtools</groupId>
          <artifactId>native-maven-plugin</artifactId>
          <version>0.10.6</version>
          <extensions>true</extensions>
          <executions>
            <execution>
              <id>build-native</id>
              <goals>
                <goal>compile-no-fork</goal>
              </goals>
              <phase>package</phase>
            </execution>
          </executions>
          <configuration>
            <imageName>${project.artifactId}</imageName>
            <buildArgs>
              <buildArg>--no-fallback</buildArg>
            </buildArgs>
          </configuration>
        </plugin>
      </plugins>
    </build>
  </profile>
</profiles>
```

构建命令：`./mvnw -Pnative package`

**对于 Gradle 项目**，应用 `org.graalvm.buildtools.native` 插件。有关完整配置，请参阅 [Gradle Native Plugin 参考](references/gradle-native-plugin.md)。

关键的 Gradle 设置（Kotlin DSL）：

```kotlin
plugins {
    id("org.graalvm.buildtools.native") version "0.10.6"
}

graalvmNative {
    binaries {
        named("main") {
            imageName.set(project.name)
            buildArgs.add("--no-fallback")
        }
    }
}
```

构建命令：`./gradlew nativeCompile`

### 3. 框架特定配置

每个框架都有自己的 AOT 策略。根据检测到的框架应用正确的配置。

**Spring Boot**（3.x+）：Spring Boot 具有内置的 GraalVM 支持，并具有 AOT 处理。有关包括 `RuntimeHints`、`@RegisterReflectionForBinding` 和测试支持的模式的参考，请参阅 [Spring Boot Native 参考](references/spring-boot-native.md)。

要点：
- 使用 `spring-boot-starter-parent` 3.x+，其中包含原生配置文件
- 通过 `RuntimeHintsRegistrar` 注册反射提示
- 使用 `process-aot` 目标运行 AOT 处理
- 构建：`./mvnw -Pnative native:compile` 或 `./gradlew nativeCompile`

**Quarkus 和 Micronaut**：这些框架设计为原生优先，需要最小的额外配置。请参阅 [Quarkus & Micronaut 参考](references/quarkus-micronaut-native.md)。

### 4. GraalVM 可达性元数据

原生镜像使用封闭世界假设——所有代码路径在构建时都必须已知。动态功能（如反射、资源和代理）需要显式的元数据配置。

**元数据文件**放置在 `META-INF/native-image/<group.id>/<artifact.id>/`：

| 文件 | 目的 |
|------|---------|
| `reachability-metadata.json` | 统一元数据（反射、资源、JNI、代理、包、序列化） |
| `reflect-config.json` | 遗留：反射注册 |
| `resource-config.json` | 遗留：资源包含模式 |
| `proxy-config.json` | 遗留：动态代理接口 |
| `serialization-config.json` | 遗留：序列化注册 |
| `jni-config.json` | 遗留：JNI 访问注册 |

有关完整格式和示例，请参阅 [反射 & 资源配置参考](references/reflection-resource-config.md)。

### 5. 迭代修复引擎

原生镜像构建通常由于缺少元数据而失败。遵循以下迭代方法：

**步骤 1 — 执行原生构建：**

```bash
# Maven
./mvnw -Pnative package 2>&1 | tee native-build.log

# Gradle
./gradlew nativeCompile 2>&1 | tee native-build.log
```

**步骤 2 — 解析构建错误并确定根本原因：**

常见错误模式及其修复方法：

| 错误模式 | 原因 | 修复 |
|---------------|-------|-----|
| `ClassNotFoundException: com.example.MyClass` | 缺少反射元数据 | 添加到 `reflect-config.json` 或使用 `@RegisterReflectionForBinding` |
| `NoSuchMethodException` | 方法未注册用于反射 | 将方法添加到反射配置 |
| `MissingResourceException` | 资源未包含在原生镜像中 | 添加到 `resource-config.json` |
| `Proxy class not found` | 动态代理未注册 | 将接口列表添加到 `proxy-config.json` |
| `UnsupportedFeatureException: Serialization` | 缺少序列化元数据 | 添加到 `serialization-config.json` |

**步骤 3 — 应用修复** 通过更新适当的元数据文件或使用框架注解。

**步骤 4 — 重新构建并验证。** 重复直到构建成功。

**步骤 5 — 如果手动修复不足够**，使用 GraalVM 追踪代理自动收集可达性元数据。请参阅 [追踪代理参考](references/tracing-agent.md)。

### 6. 验证和基准测试

原生构建成功后：

**验证可执行文件是否正常运行：**

```bash
# 运行原生可执行文件
./target/<app-name>

# 对于 Spring Boot，验证应用程序上下文加载
curl http://localhost:8080/actuator/health
```

**测量启动时间：**

```bash
# 测量启动时间
time ./target/<app-name>

# 对于 Spring Boot，检查启动日志
./target/<app-name> 2>&1 | grep "Started .* in"
```

**测量内存占用（RSS）：**

```bash
# 在 Linux 上
ps -o rss,vsz,comm -p $(pgrep <app-name>)

# 在 macOS 上
ps -o rss,vsz,comm -p $(pgrep <app-name>)
```

**与 JVM 基线比较：**

| 指标 | JVM | 原生 | 改进 |
|--------|-----|--------|-------------|
| 启动时间 | ~2-5s | ~50-200ms | 10-100x |
| 内存 (RSS) | ~200-500MB | ~30-80MB | 3-10x |
| 二进制大小 | JRE + JARs | 单个二进制文件 | 简化 |

### 7. Docker 集成

使用原生可执行文件构建最小容器镜像：

```dockerfile
# 多阶段构建
FROM ghcr.io/graalvm/native-image-community:21 AS builder
WORKDIR /app
COPY . .
RUN ./mvnw -Pnative package -DskipTests

# 最小运行时镜像
FROM debian:bookworm-slim
COPY --from=builder /app/target/<app-name> /app/<app-name>
EXPOSE 8080
ENTRYPOINT ["/app/<app-name>"]
```

对于 Spring Boot 应用程序，使用 `paketobuildpacks/builder-jammy-tiny` 与 Cloud Native Buildpacks：

```bash
./mvnw -Pnative spring-boot:build-image
```

## 最佳实践

1. **在复杂项目上从追踪代理开始** 以生成初始元数据基线
2. **使用 `native` 配置文件** 将原生特定配置与标准构建分开
3. **优先使用 `--no-fallback`** 确保真正的原生构建（无 JVM 回退）
4. **使用 `nativeTest` 进行测试** 以在原生模式下运行 JUnit 测试
5. **使用 GraalVM 可达性元数据存储库** 获取第三方库的元数据
6. **尽量减少反射** —— 优先使用构造函数注入和编译时 DI
7. **显式包含资源模式** 而不是依赖类路径扫描
8. **在之前和之后进行性能分析** —— 始终测量启动和内存改进
9. **使用 Java 21+** 以获得最佳的 GraalVM 兼容性和性能
10. **保持 GraalVM 和 Native Build Tools 版本一致**

## 示例

### 示例 1：为 Spring Boot Maven 项目添加原生支持

**场景**：您有一个 Spring Boot 3.x REST API 并希望将其编译为原生可执行文件。

**步骤 1 — 在 `pom.xml` 中添加原生配置文件：**

```xml
<profiles>
  <profile>
    <id>native</id>
    <build>
      <plugins>
        <plugin>
          <groupId>org.springframework.boot</groupId>
          <artifactId>spring-boot-maven-plugin</artifactId>
          <executions>
            <execution>
              <id>process-aot</id>
              <goals>
                <goal>process-aot</goal>
              </goals>
            </execution>
          </executions>
        </plugin>
        <plugin>
          <groupId>org.graalvm.buildtools</groupId>
          <artifactId>native-maven-plugin</artifactId>
        </plugin>
      </plugins>
    </build>
  </profile>
</profiles>
```

**步骤 2 — 为 DTO 注册反射提示：**

```java
@RestController
@RegisterReflectionForBinding({UserDto.class, OrderDto.class})
public class UserController {

    @GetMapping("/users/{id}")
    public UserDto getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
}
```

**步骤 3 — 构建和运行：**

```bash
./mvnw -Pnative native:compile
./target/myapp
# Started MyApplication in 0.089 seconds
```

### 示例 2：解决原生构建中的反射错误

**场景**：原生构建失败并报告 `ClassNotFoundException` 用于 Jackson 序列化的 DTO。

**错误输出：**

```
com.oracle.svm.core.jdk.UnsupportedFeatureError:
  Reflection registration missing for class com.example.dto.PaymentResponse
```

**修复**—— 将其添加到 `src/main/resources/META-INF/native-image/reachability-metadata.json`：

```json
{
  "reflection": [
    {
      "type": "com.example.dto.PaymentResponse",
      "allDeclaredConstructors": true,
      "allDeclaredMethods": true,
      "allDeclaredFields": true
    }
  ]
}
```

**或使用 Spring Boot 注解方法：**

```java
@RegisterReflectionForBinding(PaymentResponse.class)
@Service
public class PaymentService { /* ... */ }
```

### 示例 3：使用追踪代理处理复杂项目

**场景**：一个具有许多第三方库的项目需要全面的可达性元数据。

```bash
# 1. 构建 JAR
./mvnw package -DskipTests

# 2. 使用追踪代理运行
java -agentlib:native-image-agent=config-output-dir=src/main/resources/META-INF/native-image \
    -jar target/myapp.jar

# 3. 调用所有端点
curl http://localhost:8080/api/users
curl -X POST http://localhost:8080/api/orders -H 'Content-Type: application/json' -d '{"item":"test"}'
curl http://localhost:8080/actuator/health

# 4. 停止应用程序（Ctrl+C），然后构建原生
./mvnw -Pnative native:compile

# 5. 验证
./target/myapp
```

## 限制和警告

### 关键限制

- **GraalVM Native Image 需要 Java 17+**（推荐 Java 21+ 以获得最佳兼容性）
- **封闭世界假设**：所有代码路径在构建时都必须已知——动态类加载、运行时字节码生成和 `MethodHandles.Lookup` 可能无法工作
- **构建时间和内存**：原生编译是资源密集型的——典型项目需要 2-10 分钟和 4-8 GB 内存
- **并非所有库都兼容**：严重依赖反射、动态代理或 CGLIB 的库可能需要广泛的元数据配置
- **AOT 配置在构建时固定**：Spring Boot `@Profile` 和 `@ConditionalOnProperty` 在 AOT 处理期间评估，而不是在运行时

### 常见陷阱

- **忘记 `--no-fallback`**：如果没有此标志，构建可能会静默地生成一个 JVM 回退镜像，而不是真正的原生可执行文件
- **追踪代理覆盖不足**：代理仅捕获在运行时执行的代码路径——确保所有功能都经过测试
- **版本不匹配**：保持 GraalVM JDK、Native Build Tools 插件和框架版本一致以避免不兼容
- **类路径差异**：AOT/构建时的类路径必须与运行时匹配——在原生编译后添加/删除 JAR 会导致失败

### 安全注意事项

- 原生可执行文件比 JAR 更难反编译，但并非防篡改
- 确保不在构建时将密钥嵌入原生镜像
- 使用环境变量或外部配置管理敏感数据

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 构建内存不足 | 增加 build 内存：`-J-Xmx8g` 在 `buildArgs` 中 |
| 构建时间过长 | 使用构建缓存、减少类路径、启用开发模式的快速构建模式 |
| 应用程序运行时崩溃 | 缺少反射/资源元数据——运行追踪代理 |
| Spring Boot 上下文加载失败 | 检查 `@Conditional` bean 和配置文件依赖 |
| 第三方库不兼容 | 检查 GraalVM 可达性元数据存储库或添加手动提示 |
