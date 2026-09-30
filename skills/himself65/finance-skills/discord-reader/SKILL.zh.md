---
name: discord-reader
description: 通过连接到 Discord 桌面应用的 opencli 读取 Discord 进行金融研究：服务器、频道、成员、活跃频道的最近消息以及消息搜索。当用户想要检查 Discord、列出服务器或频道、阅读或搜索交易、加密货币或市场社区的消息，或了解 Discord 社区对某个股票或加密货币的看法时，请使用此技能。仅读权限：无法发送、回复、编辑或删除消息。
---

# Discord 技能（只读）

使用 [opencli](https://github.com/jackwener/opencli) 读取 Discord 进行金融研究，opencli 是一个通用的 CLI 工具，通过 Chrome DevTools Protocol (CDP) 将桌面应用程序和 Web 服务桥接到终端。

**此技能为只读模式。** 它专为金融研究设计：搜索交易服务器讨论、监控加密货币/市场群组、追踪金融社区中的情绪以及阅读消息。它**不支持**发送消息、反应、编辑、删除或任何写入操作。

**重要提示**：opencli 通过 CDP 连接到 Discord 桌面应用程序 — 无需机器人账户或提取令牌。只需运行 Discord 桌面版即可。

---

## 第 1 步：确保已安装 opencli 并准备 Discord

**当前环境状态：**

```
!`(command -v opencli && opencli discord-app status 2>&1 | head -5 && echo "READY" || echo "SETUP_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`
```

如果上述状态显示 `READY`，则跳至第 2 步。如果 `NOT_INSTALLED`，则先安装：

```bash
# 全局安装 opencli
npm install -g @jackwener/opencli
```

如果 `SETUP_NEEDED`，则引导用户完成设置：

### 设置

opencli 需要 Node.js >= 20。它通过 CDP（Chrome DevTools Protocol）连接到 Discord 桌面版 — Discord 适配器无需 Browser Bridge 扩展。需要两件事：

1. **以启用远程调试的方式启动 Discord：**

```bash
# macOS
/Applications/Discord.app/Contents/MacOS/Discord --remote-debugging-port=9232 &

# Linux
discord --remote-debugging-port=9232 &
```

2. **设置 CDP 端点环境变量：**

```bash
export OPENCLI_CDP_ENDPOINT="http://127.0.0.1:9232"
```

将此内容添加到您的 shell 配置文件（`.zshrc` / `.bashrc`）中，以便跨会话持久化。

3. **验证连接：**

```bash
opencli discord-app status
```

### 常见设置问题

| 症状 | 解决方法 |
|------|--------|
| `CDP 连接被拒绝` | 确保以 `--remote-debugging-port=9232` 启动 Discord |
| `OPENCLI_CDP_ENDPOINT 未设置` | 运行 `export OPENCLI_CDP_ENDPOINT="http://127.0.0.1:9232"` |
| `status` 显示断开连接 | 以 CDP 标志重启 Discord 并重试 |
| Discord 未在预期端口上 | 检查是否有其他应用程序正在使用端口 9232，或使用其他端口 |

### 提示：创建 shell 别名

```bash
alias discord-cdp='/Applications/Discord.app/Contents/MacOS/Discord --remote-debugging-port=9232 &'
```

---

## 第 2 步：确定用户需求

将用户的请求匹配到下方的读命令之一，然后使用 `references/commands.md` 中的相应命令。

| 用户请求 | 命令 | 关键标志 |
|------|------|--------|
| 连接检查 | `opencli discord-app status` | — |
| 列出服务器 | `opencli discord-app servers` | `-f json` |
| 列出频道 | `opencli discord-app channels` | `-f json` |
| 列出在线成员 | `opencli discord-app members` | `-f json` |
| 读取最近消息 | `opencli discord-app read` | `N`（数量），`-f json` |
| 搜索消息 | `opencli discord-app search "QUERY"` | `-f json` |

**注意**：opencli 在 Discord 中的**当前活动**服务器和频道上操作。要从不同频道读取，用户必须先在 Discord 应用中导航到该频道，或使用 `channels` 命令识别可用选项。

---

## 第 3 步：执行命令

### 通用模式

```bash
# 使用 -f json 或 -f yaml 获取结构化输出
opencli discord-app servers -f json
opencli discord-app channels -f json

# 从活动频道读取最近消息
opencli discord-app read 50 -f json

# 在活动频道中搜索金融主题
opencli discord-app search "AAPL earnings" -f json
opencli discord-app search "BTC pump" -f json
```

### 关键规则

1. **先检查连接** — 在执行任何其他命令前运行 `opencli discord-app status` |
2. **使用 `-f json` 或 `-f yaml`** 在处理数据时获取结构化输出 |
3. **先在 Discord 中导航** — opencli 从 Discord 应用中当前活动的服务器/频道读取 |
4. **从小规模读取开始** — 除非用户要求更多，否则使用 `opencli discord-app read 20` |
5. **使用搜索进行关键词查询** — `opencli discord-app search` 使用 Discord 的内置搜索（Cmd+F / Ctrl+F） |
6. **只读模式** — opencli 也暴露了 `discord-app send` 和 `discord-app delete`；不要调用它们，也不要发送消息、反应、编辑、删除或管理服务器设置。

### 输出格式标志 (`-f`)

| 格式 | 标志 | 适用于 |
|------|------|--------|
| 表格 | `-f table`（默认） | 人类可读的终端输出 |
| JSON | `-f json` | 程序化处理，LLM 上下文 |
| YAML | `-f yaml` | 结构化输出，可读 |
| Markdown | `-f md` | 文档，报告 |
| CSV | `-f csv` | 电子表格导出 |

### 读取服务器的典型工作流程

```bash
# 1. 验证连接
opencli discord-app status

# 2. 列出服务器以确认您在正确的服务器上
opencli discord-app servers -f json

# 3. 列出当前服务器中的频道
opencli discord-app channels -f json

# 4. 读取最近消息（先在 Discord 中导航到目标频道）
opencli discord-app read 50 -f json

# 5. 搜索感兴趣的主题
opencli discord-app search "price target" -f json
```

---

## 第 4 步：展示结果

优先展示对用户研究问题重要的信息，而不是原始数据。归因每条消息（用户名、时间戳、内容），按主题分组搜索结果，并注明看涨或看跌倾向以及观点是共识还是反共识。以表格形式展示服务器和频道列表（名称和类型）。保持 CDP 端点和会话细节私密。

---

## 第 5 步：诊断

如果出现问题，请检查：

1. **Discord 是否以 CDP 运行？**
```bash
# 检查端口是否开放
lsof -i :9232
```

2. **环境变量是否已设置？**
```bash
echo $OPENCLI_CDP_ENDPOINT
```

3. **opencli 是否能连接？**
```bash
opencli discord-app status
```

如果所有检查都失败，请以 CDP 标志重启 Discord：
```bash
/Applications/Discord.app/Contents/MacOS/Discord --remote-debugging-port=9232 &
export OPENCLI_CDP_ENDPOINT="http://127.0.0.1:9232"
opencli discord-app status
```

---

## 错误参考

| 错误 | 原因 | 解决方法 |
|------|------|--------|
| `CDP 连接被拒绝` | Discord 未以 CDP 启动或端口错误 | 以 `--remote-debugging-port=9232` 启动 Discord |
| `OPENCLI_CDP_ENDPOINT 未设置` | 缺少环境变量 | `export OPENCLI_CDP_ENDPOINT="http://127.0.0.1:9232"` |
| `无活动频道` | 未在 Discord 中查看任何频道 | 在 Discord 应用中导航到频道 |
| 速率限制 | 请求过多 | 等待几分钟，然后重试 |

---

## 参考文件

- `references/commands.md` — 完整的读命令参考，包含所有标志和示例用法

当您需要精确的命令语法或详细的标志描述时，请阅读参考文件。
