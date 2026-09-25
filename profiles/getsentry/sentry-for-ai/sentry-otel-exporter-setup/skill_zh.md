# Sentry OTel Exporter 设置

**术语**: 当提到导出器组件时，始终大写“Sentry Exporter”。

使用 Sentry Exporter 将 OpenTelemetry Collector 发送到 Sentry 的跟踪和日志。

## 设置概述

复制此清单以跟踪您的进度：

```
OTel 导出器设置：
- [ ] 第 1 步：检查现有配置
- [ ] 第 2 步：检查收集器版本并在需要时安装
- [ ] 第 3 步：配置项目创建设置
- [ ] 第 4 步：编写收集器配置
- [ ] 第 5 步：添加环境变量占位符
- [ ] 第 6 步：运行收集器
- [ ] 第 7 步：验证设置
- [ ] 第 8 步：使用 OTLPIntegration 启用跟踪连接性（Python/Ruby/Node.js）
```

## 第 1 步：检查现有配置

通过查找包含 `receivers:` 的 YAML 文件来搜索现有的 OpenTelemetry Collector 配置。还要检查名为 `otel-collector-config.*`、`collector-config.*` 或 `otelcol.*` 的文件。

**如果找到现有配置**：询问用户他们想要哪种方法：
- **修改现有配置**：将 Sentry Exporter 添加到现有文件（建议避免重复）
- **创建单独的配置**：保持现有配置不变并为测试创建一个新配置

**在继续到第 2 步之前，等待用户的回答并记录他们的选择。** 工作流程的其余部分取决于此决定。

**如果没有找到配置**：请注意，您将在第 4 步中创建一个新的 `collector-config.yaml`，然后继续到第 2 步。

## 第 2 步：检查收集器版本

Sentry Exporter 需要 **otelcol-contrib v0.145.0 或更高版本**。

### 检查现有收集器

1. 运行 `which otelcol-contrib` 检查是否在 PATH 上，或检查项目中的 `./otelcol-contrib`
2. 如果找到，运行适当的版本命令并解析版本号
3. **记录收集器路径**（如果在 PATH 上为 `otelcol-contrib`，如果本地为 `./otelcol-contrib`）以供后续步骤使用

| 现有版本 | 操作 |
| --- | --- |
| ≥ 0.145.0 | 跳转到第 3 步 — 现有收集器兼容 |
| < 0.145.0 | 继续以下安装 |
| 未安装 | 继续以下安装 |

### 安装

询问用户他们希望如何运行收集器：
- **二进制文件**：从 GitHub 发布下载。
  无需 Docker。
- **Docker**：作为容器运行。
  需要安装 Docker。

### 二进制安装

从 GitHub 获取最新发布版本：

```bash
curl -s https://api.github.com/repos/open-telemetry/opentelemetry-collector-releases/releases/latest | grep '"tag_name"' | cut -d'"' -f4
```

**重要**：GitHub API 返回带有 `v` 前缀的版本（例如，`v0.145.0`）。下载 URL 路径需要带有 `v` 前缀的完整标签，但文件名和 Docker 标签使用不带前缀的数字版本（例如，`0.145.0`）。

检测用户平台并下载二进制文件：

1. 运行 `uname -s` 和 `uname -m` 检测操作系统和架构
2. 映射到发布值：
   - Darwin + arm64 → `darwin_arm64`
   - Darwin + x86_64 → `darwin_amd64`
   - Linux + x86_64 → `linux_amd64`
   - Linux + aarch64 → `linux_arm64`
3. 下载并解压：

```bash
curl -LO https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v<numeric_version>/otelcol-contrib_<numeric_version>_<os>_<arch>.tar.gz
tar -xzf otelcol-contrib_<numeric_version>_<os>_<arch>.tar.gz
chmod +x otelcol-contrib
```

示例：对于版本 `v0.145.0`，URL 路径中使用 `v0.145.0`，文件名中使用 `0.145.0`。

为用户执行这些步骤 — 不要只是向他们展示命令。

4. **询问用户** 他们是否希望删除下载的 tarball 以节省磁盘空间（~50MB）：
   - **是，删除它**：删除 tarball
   - **否，保留它**：将 tarball 保存在原位

**等待用户的响应。** 只有在用户明确选择时才删除：

```bash
rm otelcol-contrib_<numeric_version>_<os>_<arch>.tar.gz
```

### Docker 安装

1. 通过运行 `docker --version` 验证 Docker 是否已安装
2. 从 GitHub 获取最新发布标签（与上述相同）
3. 使用不带 `v` 前缀的数字版本拉取镜像：

```bash
docker pull otel/opentelemetry-collector-contrib:<numeric_version>
```

示例：对于 GitHub 标签 `v0.145.0`，使用 `docker pull otel/opentelemetry-collector-contrib:0.145.0`。

`docker run` 命令在创建配置后第 6 步提供。

## 第 3 步：配置 Sentry 项目创建

询问用户是否要启用自动创建 Sentry 项目。
不要推荐任何选项：
- **是**：从 service.name 创建项目。
  需要在您的 Sentry 组织中至少有一个团队。
  所有新项目都将分配给找到的第一个团队。
  初始数据在创建过程中可能会丢失。
- **否**：在遥测到达之前，项目必须在 Sentry 中存在。

**在继续到第 4 步之前，等待用户的回答。**

**如果用户选择是**：警告他们导出器将扫描所有项目并使用它找到的第一个团队。
所有自动创建的项目都将分配给该团队。
如果他们还没有团队，他们应该在 Sentry 中先创建一个。

## 第 4 步：编写收集器配置

**使用第 1 步的决策** — 如果用户选择修改现有配置，请编辑该文件。如果他们选择创建单独的配置，请创建一个新文件。
**记录配置文件路径** 以供第 5 步和第 6 步使用。

从 Sentry Exporter 文档中获取最新配置：

- **示例配置**（用作模板）：
  `https://raw.githubusercontent.com/open-telemetry/opentelemetry-collector-contrib/main/exporter/sentryexporter/docs/example-config.yaml`
- **完整规范**（所有可用选项）：
  `https://raw.githubusercontent.com/open-telemetry/opentelemetry-collector-contrib/main/exporter/sentryexporter/docs/spec.md`

使用 WebFetch 将示例配置作为起始模板检索。
如果用户需要示例中未显示的高级选项，请参考规范。

### 如果编辑现有配置（根据第 1 步的决策）

将 `sentry` 导出器添加到 `exporters:` 部分并在适当的管道（`traces`、`logs`）中包含它。除非用户请求，否则不要删除或修改其他导出器。

### 如果创建新配置（根据第 1 步的决策）

基于获取的示例创建 `collector-config.yaml`。
确保凭证使用环境变量引用（`${env:SENTRY_ORG_SLUG}`、`${env:SENTRY_AUTH_TOKEN}`）。

如果用户在第 3 步中选择自动创建，请将 `auto_create_projects: true` 添加到 Sentry 导出器。

### 添加调试导出器（推荐）

在设置过程中进行故障排除时，向管道添加带有 `verbosity: detailed` 的 `debug` 导出器。
这将所有遥测记录到控制台。
验证设置后删除它。

## 第 5 步：添加环境变量占位符

Sentry Exporter 需要两个环境变量。
您将添加占位符值，用户自己填写 — 永远不要实际凭证。

**语言限制**：永远不要说“添加凭证”、“添加环境变量”或“添加令牌”，除非明确说明这些是**占位符**。始终说明用户稍后填写它们。

**不要说**：
- “让我添加环境变量”
- “我会将凭证添加到您的 .env”
- “添加 Sentry 认证令牌”

**要说**：
- “我将为您添加占位符环境变量以供填写”
- “添加占位符值 — 您将用实际凭证替换这些值”
- “我将设置 env var 键的占位符值”

使用 glob `**/.env` 在项目中搜索现有的 `.env` 文件。**始终询问用户要使用哪个文件 — 不要根据上下文推断或猜测基于打开的文件。

显示发现的选项：
- **[发现的 .env 文件路径]**：添加到现有文件（列出每个发现的路径）
- **在根目录创建新文件**：在项目根目录创建 .env

**等待用户明确选择。** 在他们选择之前不要继续。
记录 env 文件路径以供第 5 步（验证）和第 6 步（运行）使用。

将以下占位符值添加到所选文件：

```bash
SENTRY_ORG_SLUG=your-org-slug
SENTRY_AUTH_TOKEN=your-token-here
```

添加占位符后，告诉用户如何从 Sentry 获取他们的实际值：

1. **Sentry 组织标签**：在 Sentry 中，转到 **设置 → 组织设置 → 组织标签**。这也是您的子域（例如，`myorg` 在 `https://myorg.sentry.io` 中）
2. **Sentry 认证令牌**：在 Sentry 中创建一个内部集成：
   - 在 Sentry 中，转到 **设置 → 开发者设置 → 自定义集成**
   - 点击 **创建新集成** → 选择 **内部集成**
   - 设置权限：
     - **组织：读取** — 需要
     - **项目：读取** — 需要
     - **项目：写入** — 仅在使用 `auto_create_projects` 时需要
   - 保存，然后点击 **创建新令牌** 并复制它

确保所选的 `.env` 文件在 `.gitignore` 中。

### 等待用户设置凭证

解释如何获取值后，询问用户他们是否已更新 `.env` 文件：
- **是，凭证已设置**：继续验证并运行收集器
- **尚未设置**：我将等待您更新 .env 文件

如果用户选择“尚未设置”，请等待并再次询问。
直到凭证确认后，才继续到第 6 步。

### 验证配置

一旦凭证设置，使用第 2 步的安装选择适当的验证方法来验证配置。

**使用第 1 步的配置文件路径**（您修改的现有配置或新的 `collector-config.yaml`）。

#### 二进制验证

使用第 2 步记录的收集器路径（如果在 PATH 上为 `otelcol-contrib`，如果本地为 `./otelcol-contrib`）。

**首先加载环境变量**，然后运行验证：

```bash
set -a && source "<env_file>" && set +a && "<collector_path>" validate --config "<config_file>"
```

#### Docker 验证

**注意**：Docker 卷挂载需要绝对路径。
如果 `<config_file>` 或 `<env_file>` 是相对路径，请将它们前缀为 `$(pwd)/`。如果它们已经是绝对路径，请直接使用它们。

```bash
docker run --rm \
  -v "<config_file>":/etc/otelcol-contrib/config.yaml \
  --env-file "<env_file>" \
  otel/opentelemetry-collector-contrib:<numeric_version> \
  validate --config /etc/otelcol-contrib/config.yaml
```

使用第 5 步选择的 `.env` 文件路径。

**如果验证失败**：
1. 仔细检查错误消息
2. 在配置文件中修复问题
3. 再次运行验证
4. 重复直到验证通过

**一旦验证通过**，询问用户他们是否准备好运行收集器：
- **是，现在运行它**：继续到第 6 步并启动收集器
- **尚未准备**：等待。用户可能想要审查配置或准备他们的环境

**等待用户的确认，然后继续到第 6 步。**

## 第 6 步：运行收集器

**只有在用户确认他们准备好运行收集器后，才会到达此步骤。**

**向用户提供运行命令，但不要自动执行它。** 用户将自行运行它。

根据第 2 步选择的安装方法提供适当的命令。

**使用之前选择的实际路径**：
- **配置文件**：来自第 1 步（现有配置或新的 `collector-config.yaml`）
- **环境文件**：来自第 5 步（用户选择的 `.env` 文件）
- **收集器路径**：来自第 2 步（如果在 PATH 上为 `otelcol-contrib`，如果本地为 `./otelcol-contrib`）

### 二进制

**首先加载环境变量**，然后运行收集器：

```bash
set -a && source "<env_file>" && set +a && "<collector_path>" --config "<config_file>"
```

### Docker

**注意**：Docker 卷挂载需要绝对路径。
如果 `<config_file>` 或 `<env_file>` 是相对路径，请将它们前缀为 `$(pwd)/`。如果它们已经是绝对路径，请直接使用它们。

**如果重新运行**：首先停止并删除任何现有容器：

```bash
docker stop otel-collector 2>/dev/null; docker rm otel-collector 2>/dev/null
```

```bash
docker run -d \
  --name otel-collector \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 13133:13133 \
  -v "<config_file>":/etc/otelcol-contrib/config.yaml \
  --env-file "<env_file>" \
  otel/opentelemetry-collector-contrib:<numeric_version>
```

使用第 2 步拉取的相同数字版本（不带 `v` 前缀）。

提供命令后，告诉用户准备好时运行它，然后继续到第 7 步进行验证。

## 第 7 步：验证设置

1. 检查收集器日志以检查成功启动（没有关于无效配置或连接失败的错误）
2. 查找指示连接到 Sentry 的日志消息
3. 从一个已注入服务的服务发送测试遥测，并验证它在 Sentry 中出现

**成功标准**：
- 收集器无错误启动
- 跟踪和/或日志在发送后 60 秒内出现在 Sentry 中

如果使用 Docker，使用 `docker logs otel-collector` 检查日志。

## 第 8 步：使用 OTLPIntegration 启用跟踪连接性

如果用户的应用程序使用 Sentry SDK（Python、Ruby 或 Node.js），建议启用 OTLPIntegration。
这确保了**跟踪连接性** — 将 OTel 跟踪链接到 Sentry 错误、日志、crons 和指标 — 并自动设置分布式跟踪传播。

没有此步骤，通过收集器发送的跟踪出现在 Sentry 中，但与同一服务的其他 Sentry 事件（错误、日志）没有连接。

询问用户：**您的应用程序使用 Sentry Python SDK、Sentry Ruby SDK 还是 Sentry Node.js SDK 吗？**

- **Python**：按照以下 Python 设置
- **Ruby**：按照以下 Ruby 设置
- **Node.js**：按照以下 Node.js 设置
- **无 / 其他 SDK**：跳过此步骤。
  通过 OTLPIntegration 的跟踪连接性目前适用于 Python、Ruby 和 Node.js。

### Python OTLPIntegration

文档：https://docs.sentry.io/platforms/python/integrations/otlp/

1. 安装附加组件：

```bash
pip install "sentry-sdk[opentelemetry-otlp]"
```

2. 向现有的 `sentry_sdk.init()` 调用添加 `OTLPIntegration`，将 `collector_url` 设置为收集器的 OTLP 跟踪端点：

```python
from sentry_sdk.integrations.otlp import OTLPIntegration

sentry_sdk.init(
    dsn="___PUBLIC_DSN___",
    integrations=[
        OTLPIntegration(collector_url="http://localhost:4318/v1/traces"),
    ],
)
```

使用收集器的实际 OTLP HTTP 端点。
默认情况下，如果本地运行，则为 `http://localhost:4318/v1/traces`。

### Ruby OTLPIntegration

文档：https://docs.sentry.io/platforms/ruby/integrations/otlp/

1. 在 Gemfile 中添加宝石：

```ruby
gem "sentry-opentelemetry"
gem "opentelemetry-sdk"
gem "opentelemetry-exporter-otlp"
gem "opentelemetry-instrumentation-all"
```

2. 运行 `bundle install`

3. 配置 OpenTelemetry 仪器化：

```ruby
OpenTelemetry::SDK.configure do |c|
  c.use_all
end
```

4. 在现有的 `Sentry.init` 块中启用 OTLP，将 `collector_url` 设置为收集器的 OTLP 跟踪端点：

```ruby
Sentry.init do |config|
  config.dsn = "___PUBLIC_DSN___"
  config.otlp.enabled = true
  config.otlp.collector_url = "http://localhost:4318/v1/traces"
end
```

使用收集器的实际 OTLP HTTP 端点。
默认情况下，如果本地运行，则为 `http://localhost:4318/v1/traces`。

### Node.js OTLPIntegration

文档：https://docs.sentry.io/platforms/javascript/guides/node/

1. 安装轻量级 Sentry SDK 和 OpenTelemetry 依赖项：

```bash
npm install @sentry/node-core @opentelemetry/api @opentelemetry/sdk-trace-node @opentelemetry/sdk-trace-base
```

2. 创建一个仪器文件（`instrument.mjs`），将 OTel 和 Sentry 一起设置：

```javascript
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import * as Sentry from '@sentry/node-core/light';
import { otlpIntegration } from '@sentry/node-core/light/otlp';

const provider = new NodeTracerProvider();
provider.register();

Sentry.init({
  dsn: '___PUBLIC_DSN___',
  integrations: [
    otlpIntegration({
      collectorUrl: 'http://localhost:4318/v1/traces',
    }),
  ],
});
```

3. 使用 `--import` 标志启动您的应用程序：

```bash
node --import ./instrument.mjs app.mjs
```

使用收集器的实际 OTLP HTTP 端点。
默认情况下，如果本地运行，则为 `http://localhost:4318/v1/traces`。

> **在使用 `otlpIntegration` 时，不要设置 `tracesSampleRate`** — OTel 控制采样。
> 设置它将与 OTLP 路径冲突。

## 故障排除

| 错误 | 原因 | 修复 |
| --- | --- | --- |
| “failed to create project” | 缺少 Project:Write 权限 | 更新 Sentry 中的内部集成权限 |
| “no team found” | 组织中没有团队 | 在启用自动创建之前在 Sentry 中创建团队 |
| “invalid auth token” | 错误的令牌类型或过期 | 使用内部集成令牌，而不是用户认证令牌 |
| “connection refused” on 4317/4318 | 收集器未运行或端口冲突 | 检查收集器日志并确保端口可用 |
| 使用环境变量验证失败 | .env 文件未加载或占位符未替换 | 确保真实凭证在 .env 中，并且文件已加载 |
| “container name already in use” | 先前容器存在 | 运行 `docker stop otel-collector && docker rm otel-collector` |
