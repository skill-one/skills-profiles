---
name: telegram-reader
description: 使用 tdl CLI 阅读Telegram频道和群组，获取财经新闻和市场研究：列出群组和频道、按名称查找频道、导出最近消息或特定日期或ID范围内的消息。当用户需要检查Telegram、查看其频道中的最新动态、阅读或导出新闻、加密货币或交易频道或群组中的消息，或收集Telegram上发布的市场新闻和信号时，请使用此技能。仅读权限：无法发送消息或加入/离开频道。
---

# Telegram 新闻技能（仅读）

使用 [tdl](https://github.com/iyear/tdl)（一个 Telegram 命令行工具）读取 Telegram 频道和群组，获取金融新闻和市场研究信息。

**此技能仅支持读取操作。** 它的设计用于金融研究：读取频道消息、监控金融新闻频道、导出消息历史记录。它**不支持**发送消息、加入/离开频道或任何写入操作。

---

## 第 1 步：确保已安装 tdl

**当前环境状态：**

```
!`(command -v tdl && tdl version 2>&1 | head -3 || echo "TDL_NOT_INSTALLED") 2>/dev/null`
```

如果上述状态显示版本号，则表示 tdl 已安装 — 跳转到第 2 步。

如果显示 `TDL_NOT_INSTALLED`，根据用户平台安装 tdl：

| 平台 | 安装命令 |
|------|--------|
| macOS / Linux | `curl -sSL https://docs.iyear.me/tdl/install.sh \| sudo bash` |
| macOS (Homebrew) | `brew install telegram-downloader` |
| Linux (Termux) | `pkg install tdl` |
| Linux (AUR) | `yay -S tdl` |
| Linux (Nix) | `nix-env -iA nixos.tdl` |
| Go (任何平台) | `go install github.com/iyear/tdl@latest` |

macOS 默认使用 Homebrew。在 Linux 上，安装脚本会以 `sudo` 运行，因此在使用前请与用户确认，或提供他们的包管理器。

---

## 第 2 步：确保 tdl 已认证

**当前认证状态：**

```
!`(tdl chat ls --limit 1 2>&1 >/dev/null && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null`
```

如果 `AUTH_OK`，跳转到第 3 步。

如果 `AUTH_NEEDED`，引导用户完成登录。**登录需要交互式输入** — 用户必须手动输入他们的手机号和验证码。

### 登录方法

**方法 A：二维码（推荐 — 速度最快）**

```bash
tdl login -T qr
```

终端会显示一个二维码。用户使用他们的 Telegram 移动应用扫描它（设置 > 设备 > 链接桌面设备）。

**方法 B：手机号 + 验证码**

```bash
tdl login -T code
```

用户输入他们的手机号，然后输入发送到他们的 Telegram 应用的验证码。

**方法 C：从 Telegram 桌面版导入**

如果用户已安装并登录 Telegram 桌面版：

```bash
tdl login
```

这将导入现有桌面客户端的会话。桌面客户端必须来自 [官方网站](https://desktop.telegram.org/)，**不能**来自 App Store 或 Microsoft Store。

### 命名空间

默认情况下，tdl 使用 `default` 命名空间。要管理多个账户：

```bash
tdl login -n work -T qr      # 登录到 "work" 命名空间
tdl chat ls -n work           # 使用 "work" 命名空间执行命令
```

### 重要登录说明

- 登录是一次**单向操作**。成功登录后，会话会保存在磁盘上。
- 如果登录失败，请让用户检查他们的网络连接并重试。
- **切勿**以编程方式请求或处理 Telegram 密码/2FA 码 — 始终让用户交互式输入。

---

## 第 3 步：确定用户需求

将用户的请求匹配到以下读取操作之一。

| 用户请求 | 命令 | 关键标志 |
|---|---|---|
| 列出所有聊天/频道 | `tdl chat ls` | `-o json`, `-f "FILTER"` |
| 仅列出频道 | `tdl chat ls -f "Type contains 'channel'"` | `-o json` |
| 导出最近消息 | `tdl chat export -c CHAT -T last -i N` | `--all`, `--with-content` |
| 按时间范围导出消息 | `tdl chat export -c CHAT -T time -i START,END` | `--all`, `--with-content` |
| 按ID范围导出消息 | `tdl chat export -c CHAT -T id -i FROM,TO` | `--all`, `--with-content` |
| 从主题/线程导出 | `tdl chat export -c CHAT --topic TOPIC_ID` | `--all`, `--with-content` |
| 按名称搜索频道 | `tdl chat ls -f "VisibleName contains 'NAME'"` | `-o json` |

### 聊天标识符

`-c` 标志接受多种格式：

| 格式 | 示例 |
|---|---|
| 用户名（带 @） | `-c @channel_name` |
| 用户名（不带 @） | `-c channel_name` |
| 数字聊天 ID | `-c 123456789` |
| 公共链接 | `-c https://t.me/channel_name` |
| 电话号码 | `-c "+1 123456789"` |
| 保存的消息 | `-c ""`（空） |

---

## 第 4 步：执行命令

### 列出聊天

```bash
# 列出所有聊天
tdl chat ls

# JSON 输出用于处理
tdl chat ls -o json

# 仅过滤频道
tdl chat ls -f "Type contains 'channel'"

# 按名称搜索
tdl chat ls -f "VisibleName contains 'Bloomberg'"
```

### 导出消息

始终使用 `--all --with-content` 获取文本消息（而不仅仅是媒体）：

```bash
# 频道最后 20 条消息
tdl chat export -c @channel_name -T last -i 20 --all --with-content -o /tmp/tdl-export.json

# 按时间范围导出消息（Unix 时间戳）
tdl chat export -c @channel_name -T time -i 1710288000,1710374400 --all --with-content -o /tmp/tdl-export.json

# 按ID范围导出消息
tdl chat export -c @channel_name -T id -i 100,200 --all --with-content -o /tmp/tdl-export.json
```

### 关键规则

1. **先检查认证** — 在执行其他命令前运行 `tdl chat ls --limit 1` 验证会话是否有效
2. **导出消息时始终使用 `--all --with-content`** — 没有这些标志，tdl 仅导出媒体消息
3. **使用 `-o FILE`** 将导出保存到文件，然后读取 JSON — 这比解析 stdout 更可靠
4. **从小规模导出开始** — 除非用户要求更多，否则使用 `-T last -i 20`
5. **在导出前使用 `chat ls` 过滤器** 帮助用户找到正确的频道
6. **仅读操作** — 不要发送消息、加入或离开频道、或修改任何内容
7. **转换时间戳** — 当用户提供日期时，将其转换为 Unix 时间戳用于 `-T time` 过滤器

### 处理导出的 JSON

导出后，读取 JSON 文件并提取相关信息：

```bash
# 导出消息
tdl chat export -c @channel_name -T last -i 20 --all --with-content -o /tmp/tdl-export.json

# 读取并处理导出
cat /tmp/tdl-export.json
```

导出 JSON 包含消息对象，其中包含 `id`、`date`、`message`（文本内容）、`from_id`、`views` 和媒体元数据等字段。

---

## 第 5 步：展示结果

优先展示最相关的新闻或市场更新，而不是原始数据。为每条消息标注时间戳和来源频道，按主题（宏观、财报、加密货币）对来自多个频道的消息进行分组，并突出重大新闻、价格目标、财报意外。对于频道列表，显示名称、成员数量和类型。

---

## 第 6 步：诊断

如果出现问题：

| 错误 | 原因 | 解决方法 |
|---|---|---|
| `not authorized` 或会话错误 | 未登录或会话过期 | 运行 `tdl login -T qr` 重新认证 |
| `FLOOD_WAIT_X` | 被 Telegram 限流 | 等待 X 秒后重试 |
| `CHANNEL_PRIVATE` | 无权访问频道 | 用户必须在 Telegram 应用中先加入该频道 |
| `tdl: command not found` | tdl 未安装 | 使用第 1 步安装 |

---

## 参考文件

- `references/commands.md` — 读取频道和导出消息的 tdl 命令完整参考

需要精确命令语法或详细标志文档时，请阅读参考文件。
