# 重力管理器

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能合集。

重力管理器是一个专业的 AI 账户管理器和代理网关。它获取 Google（Gemini）和 Anthropic（Claude）的网页会话令牌，并将它们作为标准 API 端点（兼容 OpenAI、原生 Anthropic 和原生 Gemini 格式）公开，具有智能的多账户轮换、配额跟踪和自动故障转移。

**主要功能：**
- 多账户管理，带实时配额仪表盘
- 协议转换：网页会话 → OpenAI / Anthropic / Gemini API
- 429/401 错误时自动轮换（毫秒级故障转移）
- 模型路由和重映射
- 桌面应用程序（Tauri v2 + React + Rust）或无头 Docker/服务器模式

---

## 安装

### 选项 A：单行脚本（Linux/macOS）

```bash
curl -fsSL https://raw.githubusercontent.com/lbjlaq/Antigravity-Manager/v4.1.30/install.sh | bash
```

安装特定版本：
```bash
curl -fsSL https://raw.githubusercontent.com/lbjlaq/Antigravity-Manager/v4.1.30/install.sh | bash -s -- --version 4.1.30
```

干运行（预览而不安装）：
```bash
curl -fsSL https://raw.githubusercontent.com/lbjlaq/Antigravity-Manager/v4.1.30/install.sh | bash -s -- --dry-run
```

### 选项 B：Windows（PowerShell）

```powershell
irm https://raw.githubusercontent.com/lbjlaq/Antigravity-Manager/main/install.ps1 | iex
```

### 选项 C：Homebrew（macOS / Linuxbrew）

```bash
brew tap lbjlaq/antigravity-manager https://github.com/lbjlaq/Antigravity-Manager
brew install --cask antigravity-tools
```

### 选项 D：Docker（推荐用于服务器/NAS）

```bash
docker run -d --name antigravity-manager \
  -p 8045:8045 \
  -e API_KEY=$ANTIGRAVITY_API_KEY \
  -e WEB_PASSWORD=$ANTIGRAVITY_WEB_PASSWORD \
  -e ABV_MAX_BODY_SIZE=104857600 \
  -v ~/.antigravity_tools:/root/.antigravity_tools \
  lbjlaq/antigravity-manager:latest
```

Docker Compose:

```yaml
# docker-compose.yml
version: "3.8"
services:
  antigravity:
    image: lbjlaq/antigravity-manager:latest
    container_name: antigravity-manager
    restart: unless-stopped
    ports:
      - "8045:8045"
    environment:
      - API_KEY=${ANTIGRAVITY_API_KEY}
      - WEB_PASSWORD=${ANTIGRAVITY_WEB_PASSWORD}
      - ABV_MAX_BODY_SIZE=104857600
    volumes:
      - ~/.antigravity_tools:/root/.antigravity_tools
```

```bash
docker compose up -d
docker logs antigravity-manager          # 查看日志 / 恢复忘记的密钥
```

### 选项 E：手动下载

从 [GitHub Releases](https://github.com/lbjlaq/Antigravity-Manager/releases) 下载：
- macOS: `.dmg`（Apple Silicon + Intel）
- Windows: `.msi` 或便携式 `.zip`
- Linux: `.deb`, `.rpm`, 或 `.AppImage`

---

## 认证 / 安全模型

重力使用两个独立的凭证：

| 凭证 | 环境变量 | 配置键 | 用途 |
|---|---|---|---|
| API 密钥 | `API_KEY` | `api_key` | 认证 AI API 调用（`Authorization: Bearer ...`） |
| 网页密码 | `WEB_PASSWORD` | `admin_password` | 登录管理网页界面 |

**场景 A — 仅设置 `API_KEY`：**
- 网页界面登录：使用 `API_KEY`
- API 调用：使用 `API_KEY`

**场景 B — 两者都设置（推荐）：**
- 网页界面登录：仅使用 `WEB_PASSWORD`（API 密钥用于登录被拒绝）
- API 调用：仅使用 `API_KEY`

恢复凭证：
```bash
docker logs antigravity-manager
# 或
grep -E '"api_key"|"admin_password"' ~/.antigravity_tools/gui_config.json
```

---

## API 端点

代理服务器默认在端口 **8045** 上运行。

### 兼容 OpenAI（适用于任何 OpenAI SDK）

```
POST http://localhost:8045/v1/chat/completions
Authorization: Bearer $ANTIGRAVITY_API_KEY
```

### 原生 Anthropic（Claude Code 等）

```
POST http://localhost:8045/v1/messages
Authorization: Bearer $ANTIGRAVITY_API_KEY
```

### 原生 Gemini

```
POST http://localhost:8045/v1/models/{model}:generateContent
Authorization: Bearer $ANTIGRAVITY_API_KEY
```

---

## 代码示例

### Python — OpenAI SDK（通过重力使用 Gemini）

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ANTIGRAVITY_API_KEY"],
    base_url="http://localhost:8045/v1",
)

response = client.chat.completions.create(
    model="gemini-2.5-pro",
    messages=[
        {"role": "user", "content": "用简单的语言解释量子纠缠。"}
    ],
    stream=True,
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Python — Anthropic SDK（通过重力使用 Claude）

```python
import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ["ANTIGRAVITY_API_KEY"],
    base_url="http://localhost:8045",
)

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "写一首关于分布式系统的俳句。"}
    ],
)
print(message.content[0].text)
```

### Python — 使用 Anthropic 进行流式传输

```python
import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ["ANTIGRAVITY_API_KEY"],
    base_url="http://localhost:8045",
)

with client.messages.stream(
    model="claude-opus-4-5",
    max_tokens=2048,
    system="你是一个有帮助的编程助手。",
    messages=[{"role": "user", "content": "用 Rust 实现二分查找。"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### TypeScript / Node — OpenAI SDK

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.ANTIGRAVITY_API_KEY!,
  baseURL: "http://localhost:8045/v1",
});

async function chat(prompt: string): Promise<string> {
  const response = await client.chat.completions.create({
    model: "gemini-2.5-flash",
    messages: [{ role: "user", content: prompt }],
  });
  return response.choices[0].message.content ?? "";
}

// 通过 Imagen 3 生成图像
async function generateImage(prompt: string) {
  const response = await client.images.generate({
    model: "imagen-3.0-generate-002",
    prompt,
    size: "1024x1024",  // 映射到 Imagen 3 的宽高比
    n: 1,
  });
  return response.data[0].url;
}
```

### cURL — 快速测试

```bash
# 测试兼容 OpenAI 的端点
curl -s http://localhost:8045/v1/chat/completions \
  -H "Authorization: Bearer $ANTIGRAVITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "你好！"}]
  }' | jq '.choices[0].message.content'

# 测试 Anthropic 端点
curl -s http://localhost:8045/v1/messages \
  -H "Authorization: Bearer $ANTIGRAVITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "max_tokens": 256,
    "messages": [{"role": "user", "content": "你好！"}]
  }' | jq '.content[0].text'
```

---

## 连接 Claude Code CLI

Claude Code 使用 Anthropic 协议。指向重力：

```bash
# 在启动 Claude Code 前设置环境变量
export ANTHROPIC_API_KEY=$ANTIGRAVITY_API_KEY
export ANTHROPIC_BASE_URL=http://localhost:8045

claude  # 启动 Claude Code — 它将使用重力作为后端
```

或在你的项目根目录创建一个 `.env`：

```bash
# .env
ANTHROPIC_API_KEY=你的重力 API 密钥
ANTHROPIC_BASE_URL=http://localhost:8045
```

---

## 连接到流行的 AI 客户端

### Cherry Studio

1. 打开 Cherry Studio → 设置 → API 提供商
2. 选择 **兼容 OpenAI**
3. Base URL: `http://localhost:8045/v1`
4. API 密钥: 你的 `ANTIGRAVITY_API_KEY`

### Cursor

在 Cursor 设置中设置：
- OpenAI Base URL: `http://localhost:8045/v1`
- API 密钥: 你的 `ANTIGRAVITY_API_KEY`

### Continue.dev

```json
// ~/.continue/config.json
{
  "models": [
    {
      "title": "Gemini Pro (重力)",
      "provider": "openai",
      "model": "gemini-2.5-pro",
      "apiKey": "YOUR_ANTIGRAVITY_API_KEY",
      "apiBase": "http://localhost:8045/v1"
    },
    {
      "title": "Claude (重力)",
      "provider": "anthropic",
      "model": "claude-sonnet-4-5",
      "apiKey": "YOUR_ANTIGRAVITY_API_KEY",
      "apiBase": "http://localhost:8045"
    }
  ]
}
```

---

## 配置文件

配置存储在 `~/.antigravity_tools/gui_config.json`：

```json
{
  "api_key": "sk-your-api-key",
  "admin_password": "你的网页界面密码",
  "proxy": {
    "port": 8045,
    "max_body_size": 104857600,
    "admin_password": "你的网页界面密码"
  },
  "model_routes": [
    {
      "pattern": "gpt-4.*",
      "target": "gemini-2.5-pro"
    },
    {
      "pattern": "gpt-3.5.*",
      "target": "gemini-2.5-flash"
    }
  ]
}
```

### 环境变量（Docker / 服务器模式）

| 变量 | 描述 | 默认值 |
|---|---|---|
| `API_KEY` | 用于认证代理请求的 API 密钥 | 必须提供 |
| `WEB_PASSWORD` | 网页界面管理员密码 | 回退到 `API_KEY` |
| `ABV_MAX_BODY_SIZE` | 请求体的最大字节数（用于图像上传） | `104857600`（100MB） |

---

## 模型路由

重力的模型路由器允许你将传入的模型名称重映射到实际的上游模型。这在客户端硬编码模型名称（如 `gpt-4`）时很有用。

通过网页界面（API 代理 → 模型路由器）或 `gui_config.json` 进行配置：

```json
{
  "model_routes": [
    {
      "pattern": "gpt-4-turbo",
      "target": "gemini-2.5-pro"
    },
    {
      "pattern": "gpt-4o",
      "target": "gemini-2.5-pro"
    },
    {
      "pattern": "gpt-3\\.5.*",
      "target": "gemini-2.5-flash"
    },
    {
      "pattern": "claude-3-opus.*",
      "target": "claude-opus-4-5"
    }
  ]
}
```

**分层路由**（自动）：重力按账户类型（Ultra → Pro → Free）和配额重置频率优先级排序，优先消耗快速重置的账户。

**后台任务降级**（自动）：检测到的后台任务（例如 Claude CLI 标题生成）将自动重定向到 Flash 级模型，以保留高级配额。

---

## 账户管理

### 通过 UI 添加账户

1. 打开重力管理器桌面应用程序或网页界面（`http://localhost:8045`）
2. 导航到 **账户**
3. 点击 **添加账户** — 应用程序生成 OAuth 2.0 授权 URL
4. 在任何浏览器中完成授权
5. 应用程序自动捕获回调；如果需要，点击 "已授权，继续"

### 批量导入（JSON）

从其他工具导出并在账户页面导入：

```json
[
  {
    "token": "session-token-1",
    "type": "google",
    "label": "账户-工作"
  },
  {
    "token": "session-token-2",
    "type": "anthropic",
    "label": "账户-个人"
  }
]
```

### 从 v1 迁移

重力在首次启动时自动检测并迁移 v1 数据库格式 — 无需手动步骤。

---

## 配额监控

仪表板显示所有账户的实时配额：

- **Gemini Pro** 剩余调用次数（跨账户平均）
- **Gemini Flash** 剩余调用次数
- **Claude** 剩余调用次数
- **Imagen 3** 图像生成配额

**智能建议**：仪表板算法自动选择配额空间最大的账户，并提供一键切换。

**403 检测**：上游禁止的账户将自动标记并跳过轮换。

---

## 从源代码构建（Rust + Tauri v2）

### 前置条件

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Node.js（用于前端）
node --version  # 需要 v18+

# Tauri v2 CLI
cargo install tauri-cli --version "^2"

# 系统依赖（Linux）
sudo apt install libwebkit2gtk-4.1-dev libayatana-appindicator3-dev librsvg2-dev
```

### 构建 & 运行

```bash
git clone https://github.com/lbjlaq/Antigravity-Manager.git
cd Antigravity-Manager

npm install          # 安装前端依赖
cargo tauri dev      # 开发模式下运行
cargo tauri build    # 构建发布二进制文件 → src-tauri/target/release/bundle/
```

### 仅构建无头服务器（无界面）

```bash
cd src-tauri
cargo build --release --features headless
./target/release/antigravity-manager --headless --port 8045
```

---

## 故障排除

### 端口 8045 已被占用

```bash
# 查找并终止进程
lsof -ti:8045 | xargs kill -9
# 或在 gui_config.json 中更改端口：
# "proxy": { "port": 8046 }
```

### 忘记 API 密钥或网页密码

```bash
# Docker
docker logs antigravity-manager | grep -E "api_key|password"

# 本地安装
cat ~/.antigravity_tools/gui_config.json | grep -E '"api_key"|"admin_password"'
```

### 账户显示 403 / 被禁止

账户在上游被标记。在账户视图中会标记为 403 徽章并自动跳过。添加一个新账户并移除/重新授权被禁止的账户。

### 请求以 429 失败

重力自动处理此问题（毫秒级轮换到下一个账户）。如果所有账户都已用尽，请添加更多账户或等待配额重置。检查仪表板以获取每个账户的配额状态。

### macOS Gatekeeper 阻止应用程序

```bash
xattr -d com.apple.quarantine /Applications/Antigravity\ Tools.app
# 或使用：
brew install --cask antigravity-tools --no-quarantine
```

### Docker 容器重启后不持久化账户

确保卷挂载正确：
```bash
docker run ... -v ~/.antigravity_tools:/root/.antigravity_tools ...
# 验证数据是否存在：
ls ~/.antigravity_tools/
```

### Claude Code 无法连接

```bash
# 验证代理正在运行
curl -s http://localhost:8045/v1/models \
  -H "Authorization: Bearer $ANTIGRAVITY_API_KEY"

# 检查环境变量是否导出（而不仅仅是设置）
export ANTHROPIC_BASE_URL=http://localhost:8045
export ANTHROPIC_API_KEY=$ANTIGRAVITY_API_KEY
echo $ANTHROPIC_BASE_URL  # 应该打印 URL
```

---

## 项目结构（供贡献者）

```
Antigravity-Manager/
├── src/                    # React 前端（TypeScript）
│   ├── components/         # UI 组件（仪表板、账户等）
│   └── pages/
├── src-tauri/              # Rust 后端
│   ├── src/
│   │   ├── main.rs         # Tauri 应用程序入口
│   │   ├── proxy/          # Axum HTTP 代理服务器
│   │   │   ├── router.rs   # 模型路由逻辑
│   │   │   ├── dispatcher.rs # 账户轮换
│   │   │   └── mapper.rs   # 协议转换
│   │   ├── accounts/       # 账户存储 & OAuth
│   │   └── quota/          # 配额跟踪
│   └── Cargo.toml
├── docker/
│   └── Dockerfile
├── install.sh              # Linux/macOS 安装器
├── install.ps1             # Windows 安装器
└── docker-compose.yml
```
