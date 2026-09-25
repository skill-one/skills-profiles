# 使用 WireMock 进行 REST API 单元测试

## 概述

使用 WireMock 测试外部 REST API 集成模式的指南：模拟响应、验证请求、错误场景以及无需网络依赖的快速测试。

## 使用场景

- 测试调用外部 REST API 的服务
- 模拟 HTTP 响应以实现可预测的测试行为
- 测试错误场景（超时、5xx 错误、格式错误的响应）
- 验证请求详情（请求头、查询参数、请求体）

## 操作步骤

1. **添加依赖**：在测试范围内添加 WireMock（Maven/Gradle）
2. **注册扩展**：使用 `@RegisterExtension WireMockExtension` 并配置 `dynamicPort()`
3. **配置客户端**：使用 `wireMock.getRuntimeInfo().getHttpBaseUrl()` 作为基础 URL
4. **模拟响应**：使用 `stubFor()` 并匹配请求（URL、请求头、请求体）
5. **执行和断言**：调用服务方法，使用 AssertJ 验证结果
6. **验证请求**：使用 `verify()` 确保正确的 API 使用

**如果模拟不匹配**：检查 URL 编码、请求头名称，使用 `urlEqualTo` 验证查询参数。

**如果测试卡住**：在 HTTP 客户端配置连接超时；使用 `withFixedDelay()` 模拟超时。

**如果端口冲突**：始终使用 `wireMockConfig().dynamicPort()`。

## 示例

### Maven 依赖

```xml
<dependency>
  <groupId>org.wiremock</groupId>
  <artifactId>wiremock</artifactId>
  <version>3.4.1</version>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

### 基本模拟和验证

```java
import com.github.tomakehurst.wiremock.junit5.WireMockExtension;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static org.assertj.core.api.Assertions.assertThat;

class ExternalWeatherServiceTest {

  @RegisterExtension
  static WireMockExtension wireMock = WireMockExtension.newInstance()
    .options(wireMockConfig().dynamicPort())
    .build();

  @Test
  void shouldFetchWeatherDataFromExternalApi() {
    wireMock.stubFor(get(urlEqualTo("/weather?city=London"))
      .withHeader("Accept", containing("application/json"))
      .willReturn(aResponse()
        .withStatus(200)
        .withHeader("Content-Type", "application/json")
        .withBody("{\"city\":\"London\",\"temperature\":15,\"condition\":\"Cloudy\"}")));

    String baseUrl = wireMock.getRuntimeInfo().getHttpBaseUrl();
    WeatherApiClient client = new WeatherApiClient(baseUrl);
    WeatherData weather = client.getWeather("London");

    assertThat(weather.getCity()).isEqualTo("London");
    assertThat(weather.getTemperature()).isEqualTo(15);

    wireMock.verify(getRequestedFor(urlEqualTo("/weather?city=London"))
      .withHeader("Accept", containing("application/json")));
  }
}
```

有关错误场景、请求体验证、超时模拟和状态测试的更多信息，请参阅 `references/advanced-examples.md`。

## 最佳实践

- **动态端口**：防止并行测试执行时的冲突
- **验证请求**：确保客户端正确使用 API
- **测试错误**：覆盖超时、4xx、5xx 场景
- **专注的模拟**：每个测试一个关注点
- **自动重置**：`@RegisterExtension` 在测试之间重置 WireMock
- **避免调用真实 API**：始终模拟第三方端点

## 限制和警告

- **需要动态端口**：固定端口会导致并行执行冲突
- **HTTPS 测试**：如果测试 TLS 连接，请配置 WireMock TLS 设置
- **模拟优先级**：更具体的模拟优先于通用模拟
- **性能**：WireMock 增加开销；在客户端层模拟以实现更快的测试
- **API 变更**：保持模拟与实际 API 合约同步

## 参考

- [WireMock 文档](https://wiremock.org/)
- [WireMock 模拟指南](https://wiremock.org/docs/stubbing/)
- `references/advanced-examples.md` - 错误场景、请求体验证、超时
