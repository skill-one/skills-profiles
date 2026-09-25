# WireMock 独立 Docker 实战技巧

## 概述

提供运行 WireMock 作为独立 Docker 容器的模式，用于集成测试和端到端测试期间模拟外部 API。将 WireMock 作为独立服务运行，模拟真实 API 行为以测试 HTTP 客户端、重试逻辑和错误处理。

## 使用场景

在以下情况下使用：
- 集成测试或端到端测试期间模拟外部 API
- 无需真实服务即可模拟错误条件（超时、5xx、速率限制）
- 测试 HTTP 客户端配置、重试逻辑和错误处理
- 创建可移植、可重复的测试环境
- 在实现真实服务前验证 API 合约

## 使用说明

### 第 1 步：设置 Docker Compose

创建包含 WireMock 3.5.2、端口映射和映射文件挂载的 `docker-compose.yml`：

```yaml
version: "3.8"
services:
  wiremock:
    image: wiremock/wiremock:3.5.2
    ports:
      - "8080:8080"
    volumes:
      - ./wiremock:/home/wiremock
    command: ["--global-response-templating"]
```

### 第 2 步：创建目录结构

创建 WireMock 配置目录：

```
wiremock/
├── mappings/   # JSON 模拟定义
└── __files/   # 响应体文件
```

### 第 3 步：定义 API 模拟

在 `wiremock/mappings/` 中为每个场景创建 JSON 模拟文件：

- **成功**：返回 200 及 JSON 正文
- **未找到**：返回 404
- **服务器错误**：返回 500
- **超时**：使用 `fixedDelayMilliseconds`
- **速率限制**：返回 429 及 Retry-After 头

### 第 4 步：启动 WireMock

```bash
docker compose up -d
```

### 第 5 步：验证 WireMock 是否运行

```bash
curl http://localhost:8080/__admin/mappings
```

预期：如果没有加载模拟，返回空数组 `{"mappings":[]}`，或您的模拟定义。如果出现连接拒绝，请检查容器是否运行：`docker compose ps`

### 第 6 步：配置 HTTP 客户端

将应用程序指向 `http://localhost:8080`（或 Docker 网络中的 `http://wiremock:8080`）而不是真实 API。

### 第 7 步：测试边界情况

始终测试：200、400、401、403、404、429、500、超时、格式错误的响应。

## 示例

### 示例 1：模拟成功 GET 请求

```json
{
  "request": { "method": "GET", "url": "/api/users/123" },
  "response": {
    "status": 200,
    "jsonBody": { "id": 123, "name": "Mario Rossi" }
  }
}
```

### 示例 2：模拟服务器错误

```json
{
  "request": { "method": "GET", "url": "/api/error" },
  "response": { "status": 500, "body": "Internal Server Error" }
}
```

### 示例 3：模拟超时

```json
{
  "request": { "method": "GET", "url": "/api/slow" },
  "response": {
    "status": 200,
    "fixedDelayMilliseconds": 5000,
    "jsonBody": { "message": "delayed" }
  }
}
```

### 示例 4：包含应用程序的 Docker Compose

```yaml
services:
  wiremock:
    image: wiremock/wiremock:3.5.2
    ports:
      - "8080:8080"
    volumes:
      - ./wiremock:/home/wiremock

  app:
    build: .
    environment:
      - API_BASE_URL=http://wiremock:8080
    depends_on:
      - wiremock
```

## 最佳实践

1. **按功能组织模拟**：使用子目录如 `users/`、`products/`
2. **版本控制模拟**：将模拟保存在 git 中以实现可重复测试
3. **测试所有错误场景**：401、403、404、429、500、超时
4. **测试间重置**：`curl -X POST http://localhost:8080/__admin/reset`
5. **使用描述性文件名**：`get-user-success.json`、`post-user-error.json`

## 限制和警告

- 确保 8080 端口可用或映射到其他端口
- 运行多个容器时配置 Docker 网络设置
- 启用 `--global-response-templating` 以实现动态响应
- WireMock 在容器重启时重置模拟

## 故障排除

**请求不匹配模拟？**
检查 WireMock 接收的内容：`curl http://localhost:8080/__admin/requests` — 显示未匹配请求的详细信息。

**模拟文件未加载？**
验证文件位置：将 JSON 模拟文件放在 `wiremock/mappings/`，响应文件放在 `wiremock/__files/`。检查文件权限。

**连接拒绝错误？**
运行 `docker compose ps` 验证容器是否运行。使用 `lsof -i :8080` 检查端口冲突。

## 参考

在 `references/` 中查看完整示例：
- `docker-compose.yml` - 完整 Docker Compose 配置
- `wiremock/mappings/` - 所有场景的完整模拟示例
