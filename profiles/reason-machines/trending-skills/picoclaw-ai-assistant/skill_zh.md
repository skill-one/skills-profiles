# PicoClaw AI 助手

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

PicoClaw 是一款用 Go 语言编写的超轻量级个人 AI 助手。它运行在 10 美元硬件上，RAM 小于 10MB，启动时间不到 1 秒。它支持多个 LLM 提供商（兼容 OpenAI、Anthropic、Volcengine），可选的网页搜索工具，并在 x86_64、ARM64、MIPS 和 RISC-V Linux 设备上部署为单个自包含的二进制文件。

---

## 安装

### 预编译二进制文件

从 [发布页面](https://github.com/sipeed/picoclaw/releases) 下载：

```bash
# Linux ARM64 (树莓派、LicheeRV-Nano 等)
wget https://github.com/sipeed/picoclaw/releases/download/v0.1.1/picoclaw-linux-arm64
chmod +x picoclaw-linux-arm64
./picoclaw-linux-arm64 onboard
```

### 从源代码构建

```bash
git clone https://github.com/sipeed/picoclaw.git
cd picoclaw

# 安装依赖
make deps

# 为当前平台构建
make build

# 为所有平台构建
make build-all

# 树莓派 Zero 2 W — 32 位
make build-linux-arm      # → build/picoclaw-linux-arm

# 树莓派 Zero 2 W — 64 位
make build-linux-arm64    # → build/picoclaw-linux-arm64

# 构建 Pi Zero 的两种变体
make build-pi-zero

# 构建并安装到系统路径
make install
```

### Docker Compose

```bash
git clone https://github.com/sipeed/picoclaw.git
cd picoclaw

# 首次运行 — 生成 docker/data/config.json 然后退出
docker compose -f docker/docker-compose.yml --profile gateway up

# 编辑配置
vim docker/data/config.json

# 在后台运行
docker compose -f docker/docker-compose.yml --profile gateway up -d

# 查看日志
docker compose -f docker/docker-compose.yml logs -f picoclaw-gateway

# 停止
docker compose -f docker/docker-compose.yml --profile gateway down
```

#### Docker: Web 控制台（启动器模式）

```bash
docker compose -f docker/docker-compose.yml --profile launcher up -d
# 打开 http://localhost:18800
```

#### Docker: 单次代理模式

```bash
# 单个问题
docker compose -f docker/docker-compose.yml run --rm picoclaw-agent -m "2+2 等于多少？"

# 交互式会话
docker compose -f docker/docker-compose.yml run --rm picoclaw-agent
```

#### Docker: 将网关暴露给主机

如果网关需要从主机访问，请设置：

```bash
PICOCLAW_GATEWAY_HOST=0.0.0.0 docker compose -f docker/docker-compose.yml --profile gateway up -d
```

或者将 `PICOCLAW_GATEWAY_HOST=0.0.0.0` 设置在 `docker/data/config.json` 中。

### Termux (Android)

```bash
pkg install wget proot
wget https://github.com/sipeed/picoclaw/releases/download/v0.1.1/picoclaw-linux-arm64
chmod +x picoclaw-linux-arm64
termux-chroot ./picoclaw-linux-arm64 onboard
```

---

## 快速入门

### 1. 初始化

```bash
picoclaw onboard
```

这将创建 `~/.picoclaw/config.json` 并包含一个初始配置。

### 2. 配置 `~/.picoclaw/config.json`

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.picoclaw/workspace",
      "model_name": "gpt-4o",
      "max_tokens": 8192,
      "temperature": 0.7,
      "max_tool_iterations": 20
    }
  },
  "model_list": [
    {
      "model_name": "gpt-4o",
      "model": "openai/gpt-4o",
      "api_key": "$OPENAI_API_KEY",
      "request_timeout": 300
    },
    {
      "model_name": "claude-sonnet",
      "model": "anthropic/claude-sonnet-4-5",
      "api_key": "$ANTHROPIC_API_KEY"
    },
    {
      "model_name": "ark-code",
      "model": "volcengine/ark-code-latest",
      "api_key": "$VOLCENGINE_API_KEY",
      "api_base": "https://ark.cn-beijing.volces.com/api/coding/v3"
    }
  ],
  "tools": {
    "web": {
      "brave": {
        "enabled": false,
        "api_key": "$BRAVE_API_KEY"
      },
      "tavily": {
        "enabled": false,
        "api_key": "$TAVILY_API_KEY"
      }
    }
  }
}
```

> 不要硬编码 API 密钥。在配置中使用 `$VAR_NAME` 语法引用环境变量，或在启动前在 shell 环境中设置它们。

### 3. 运行

```bash
# 交互式聊天
picoclaw

# 单条消息
picoclaw -m "总结最新的 Go 发布说明"

# 使用特定模型
picoclaw -model claude-sonnet -m "重构这个函数以提高清晰度"
```

---

## 主要 CLI 命令

| 命令 | 描述 |
|---|---|
| `picoclaw onboard` | 初始化配置和工作区 |
| `picoclaw` | 启动交互式聊天会话 |
| `picoclaw -m "..."` | 发送一条消息并退出 |
| `picoclaw -model <name>` | 覆盖默认模型 |
| `picoclaw -config <path>` | 使用自定义配置文件 |

---

## 配置参考

### 模型条目字段

```json
{
  "model_name": "my-model",        // 在 -model 标志和代理默认值中使用的别名
  "model": "provider/model-id",    // 带有提供者前缀的模型标识符
  "api_key": "$ENV_VAR",           // API 密钥 — 使用环境变量引用
  "api_base": "https://...",       // 可选：覆盖基本 URL（用于自托管或区域端点）
  "request_timeout": 300           // 可选：超时秒数
}
```

### 支持的提供者前缀

| 前缀 | 提供者 |
|---|---|
| `openai/` | OpenAI 和兼容 OpenAI 的 API |
| `anthropic/` | Anthropic Claude |
| `volcengine/` | Volcengine (Ark) |

### 代理默认值

```json
"agents": {
  "defaults": {
    "workspace": "~/.picoclaw/workspace",  // 文件操作的 working directory
    "model_name": "gpt-4o",                // 默认模型别名
    "max_tokens": 8192,                    // 最大响应 token 数
    "temperature": 0.7,                    // 采样温度
    "max_tool_iterations": 20              // 最大代理工具调用循环迭代次数
  }
}
```

### 网页搜索工具

获取免费 API 密钥：
- **Tavily**: https://tavily.com — 每月 1,000 次免费查询
- **Brave Search**: https://brave.com/search/api — 每月 2,000 次免费查询

```json
"tools": {
  "web": {
    "tavily": {
      "enabled": true,
      "api_key": "$TAVILY_API_KEY"
    },
    "brave": {
      "enabled": false,
      "api_key": "$BRAVE_API_KEY"
    }
  }
}
```

一次只启用一个搜索提供者，除非您希望使用回退行为。

---

## 常见模式

### 模式：最小 $10 设备设置

对于 LicheeRV-Nano 或类似超低资源板：

```bash
# 从发布页面下载 RISC-V 或 ARM 二进制文件
wget https://github.com/sipeed/picoclaw/releases/download/v0.1.1/picoclaw-linux-riscv64
chmod +x picoclaw-linux-riscv64

# 初始化
./picoclaw-linux-riscv64 onboard

# 编辑配置 — 使用轻量级模型，低 max_tokens
cat > ~/.picoclaw/config.json << 'EOF'
{
  "agents": {
    "defaults": {
      "workspace": "~/.picoclaw/workspace",
      "model_name": "gpt-4o-mini",
      "max_tokens": 2048,
      "temperature": 0.5,
      "max_tool_iterations": 10
    }
  },
  "model_list": [
    {
      "model_name": "gpt-4o-mini",
      "model": "openai/gpt-4o-mini",
      "api_key": "$OPENAI_API_KEY",
      "request_timeout": 120
    }
  ]
}
EOF

./picoclaw-linux-riscv64
```

### 模式：全栈开发助手（带网页搜索）

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/projects",
      "model_name": "claude-sonnet",
      "max_tokens": 8192,
      "temperature": 0.3,
      "max_tool_iterations": 30
    }
  },
  "model_list": [
    {
      "model_name": "claude-sonnet",
      "model": "anthropic/claude-sonnet-4-5",
      "api_key": "$ANTHROPIC_API_KEY",
      "request_timeout": 600
    }
  ],
  "tools": {
    "web": {
      "tavily": {
        "enabled": true,
        "api_key": "$TAVILY_API_KEY"
      }
    }
  }
}
```

### 模式：使用环境变量的 Docker

```yaml
# docker/docker-compose.override.yml
services:
  picoclaw-gateway:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - PICOCLAW_GATEWAY_HOST=0.0.0.0
```

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml --profile gateway up -d
```

### 模式：在 Go 中为特定目标构建

```bash
# 为 MIPS（OpenWRT 路由器）交叉编译
GOOS=linux GOARCH=mips GOMIPS=softfloat go build -o build/picoclaw-linux-mips ./cmd/picoclaw

# 为 32 位 ARM（旧款树莓派）交叉编译
GOOS=linux GOARCH=arm GOARM=7 go build -o build/picoclaw-linux-arm ./cmd/picoclaw

# 为 RISC-V 64 位交叉编译
GOOS=linux GOARCH=riscv64 go build -o build/picoclaw-linux-riscv64 ./cmd/picoclaw
```

---

## 故障排除

### 二进制文件在设备上无法执行

```bash
# 验证二进制文件是否与设备架构匹配
file picoclaw-linux-arm64
uname -m   # 应匹配：aarch64 = arm64, x86_64 = amd64

# 确保有可执行权限
chmod +x picoclaw-linux-arm64
```

### Termux 上出现 "Permission denied"

Termux 需要使用 `proot` 进行某些系统调用：

```bash
pkg install proot
termux-chroot ./picoclaw-linux-arm64 onboard
```

### API 密钥未识别

- 不要在配置中使用 `"api_key": "sk-..."` 字面量 — 设置环境变量并引用它们作为 `"$OPENAI_API_KEY"`。
- 验证环境变量是否在当前 shell 中导出：`echo $OPENAI_API_KEY`。

### Docker 网关从主机无法访问

在启动容器前，在环境中设置 `PICOCLAW_GATEWAY_HOST=0.0.0.0` 或在 `config.json` 中设置。

### 近期版本内存使用过高

项目指出，最近的 PR 可能将 RAM 使用推高到 10–20MB。如果这对超低内存设备是问题，请钉定到较早的版本标签：

```bash
git checkout v0.1.1
make build
```

### 配置文件位置

默认：`~/.picoclaw/config.json`

运行时覆盖：

```bash
picoclaw -config /path/to/custom-config.json
```

### 依赖项更改后重新构建

```bash
cd picoclaw
make deps
make build
```

---

## 硬件目标快速参考

| 设备 | 价格 | 二进制文件 |
|---|---|---|
| LicheeRV-Nano (E/W) | ~$10 | `picoclaw-linux-riscv64` |
| NanoKVM | ~$30–50 | `picoclaw-linux-riscv64` |
| MaixCAM / MaixCAM2 | ~$50–100 | `picoclaw-linux-arm64` |
| 树莓派 Zero 2 W (32 位操作系统) | ~$15 | `picoclaw-linux-arm` |
| 树莓派 Zero 2 W (64 位操作系统) | ~$15 | `picoclaw-linux-arm64` |
| 通过 Termux 的 Android | — | `picoclaw-linux-arm64` |
| 标准 Linux x86_64 | — | `picoclaw-linux-amd64` |
