# OpenClaw 运维手册

诊断并修复真实问题。本文档中每条命令均已经过测试，可直接使用。

---

## 快速健康检查

当任何异常发生时，先运行此检查。整块复制粘贴：

```bash
echo "=== GATEWAY ===" && \
ps aux | grep -c "[o]penclaw" && \
echo "=== CONFIG JSON ===" && \
python3 -m json.tool ~/.openclaw/openclaw.json > /dev/null 2>&1 && echo "JSON: OK" || echo "JSON: BROKEN" && \
echo "=== CHANNELS ===" && \
cat ~/.openclaw/openclaw.json | jq -r '.channels | to_entries[] | "\(.key): policy=\(.value.dmPolicy // "n/a") enabled=\(.value.enabled // "implicit")"' && \
echo "=== PLUGINS ===" && \
cat ~/.openclaw/openclaw.json | jq -r '.plugins.entries | to_entries[] | "\(.key): \(.value.enabled)"' && \
echo "=== CREDS ===" && \
ls ~/.openclaw/credentials/whatsapp/default/ 2>/dev/null | wc -l | xargs -I{} echo "WhatsApp keys: {} files" && \
for d in ~/.openclaw/credentials/telegram/*/; do bot=$(basename "$d"); [ -f "$d/token.txt" ] && echo "Telegram $bot: OK" || echo "Telegram $bot: MISSING"; done && \
[ -f ~/.openclaw/credentials/bird/cookies.json ] && echo "Bird cookies: OK" || echo "Bird cookies: MISSING" && \
echo "=== CRON ===" && \
cat ~/.openclaw/cron/jobs.json | jq -r '.jobs[] | "\(.name): enabled=\(.enabled) status=\(.state.lastStatus // "never") \(.state.lastError // "")"' && \
echo "=== RECENT ERRORS ===" && \
tail -10 ~/.openclaw/logs/gateway.err.log 2>/dev/null && \
echo "=== MEMORY DB ===" && \
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT COUNT(*) || ' chunks, ' || (SELECT COUNT(*) FROM files) || ' files indexed' FROM chunks;" 2>/dev/null
```

---

## 文件目录结构

```
~/.openclaw/
├── openclaw.json                    # 主配置文件 — 通道、认证、网关、插件、技能
├── openclaw.json.bak*               # 自动备份（.bak、.bak.1、.bak.2 ...）
├── exec-approvals.json              # 执行审批套接字配置
│
├── agents/main/
│   ├── agent/auth-profiles.json     # Anthropic 认证令牌
│   └── sessions/
│       ├── sessions.json            # 会话索引 — 键形如 agent:main:whatsapp:+1234
│       └── *.jsonl                  # 会话转录记录（每行一个 JSON 对象）
│
├── workspace/                       # 代理工作区（受 git 管理）
│   ├── SOUL.md                      # 人格、写作风格、语气规则
│   ├── IDENTITY.md                  # 名称、生物类型、气质
│   ├── USER.md                      # 所有者上下文和偏好
│   ├── AGENTS.md                    # 会话行为、记忆规则、安全策略
│   ├── BOOT.md                      # 启动指令（自动驾驶通知协议）
│   ├── HEARTBEAT.md                 # 周期性任务清单（为空 = 跳心跳检测）
│   ├── MEMORY.md                    # 精选长期记忆（仅限主会话）
│   ├── TOOLS.md                     # 联系人、SSH 主机、设备昵称
│   ├── memory/                      # 日志文件：YYYY-MM-DD.md、topic-chat.md
│   └── skills/                      # 工作区级技能
│
├── memory/main.sqlite               # 向量记忆数据库（Gemini 嵌入，FTS5 搜索）
│
├── logs/
│   ├── gateway.log                  # 运行时日志：启动、通道初始化、配置重载、关闭
│   ├── gateway.err.log              # 错误日志：连接断开、API 故障、超时
│   └── commands.log                 # 命令执行日志
│
├── cron/
│   ├── jobs.json                    # 任务定义（调度、载荷、投递目标）
│   └── runs/                        # 各任务的运行日志：{job-uuid}.jsonl
│
├── credentials/
│   ├── whatsapp/default/            # Baileys 会话：约 1400 个 app-state-sync-key-*.json 文件
│   ├── telegram/{botname}/token.txt # 机器人令牌（每个机器人账户一个）
│   └── bird/cookies.json            # X/Twitter 认证 Cookie
│
├── extensions/{name}/               # 自定义插件（TypeScript）
│   ├── openclaw.plugin.json         # {"id", "channels", "configSchema"}
│   ├── index.ts                     # 入口文件
│   └── src/                         # channel.ts、actions.ts、runtime.ts、types.ts
│
├── identity/                        # device.json、device-auth.json
├── devices/                         # paired.json、pending.json
├── media/inbound/                   # 收到的图片、音频文件
├── media/browser/                   # 浏览器截图
├── browser/openclaw/user-data/      # Chromium 配置文件（约 180MB）
├── tools/signal-cli/                # Signal CLI 二进制文件
├── subagents/runs.json              # 子代理执行日志
├── canvas/index.html                # Web 画布界面
└── telegram/
    ├── update-offset-coder.json     # {"lastUpdateId": N} — Telegram 轮询游标
    └── update-offset-sales.json     # 重置为 0 可重放遗漏消息
```

---

## 故障排除：WhatsApp

### "我发了消息但没收到回复"

这是排名第一的问题。消息已送达但机器人没有响应。按以下顺序检查：

```bash
# 1. 机器人是否实际在运行？
grep -i "whatsapp.*starting\|whatsapp.*listening" ~/.openclaw/logs/gateway.log | tail -5

# 2. 检查 408 超时断开（WhatsApp Web 频繁断开连接）
grep -i "408\|499\|retry" ~/.openclaw/logs/gateway.err.log | tail -10
# 如果看到 "Web connection closed (status 408). Retry 1/12" — 这是正常的，
# 会自动恢复。但如果重试达到 12/12，说明会话已完全断开。

# 3. 检查跨上下文消息拦截
grep -i "cross-context.*denied" ~/.openclaw/logs/gateway.err.log | tail -10
# 常见情况："Cross-context messaging denied: action=send target provider "whatsapp" while bound to "signal""
# 意思是代理处于 Signal 会话中，却尝试通过 WhatsApp 回复。
# 修复：消息必须在 WhatsApp 会话上下文中接收，而非 Signal。

# 4. 检查该联系人的会话是否存在
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r 'to_entries[] | select(.key | test("whatsapp")) | "\(.key) | \(.value.origin.label // "?")"'

# 5. 检查发送者是否被允许
cat ~/.openclaw/openclaw.json | jq '.channels.whatsapp | {dmPolicy, allowFrom, selfChatMode, groupPolicy}'
# 如果 dmPolicy 是 "allowlist" 且发送者不在 allowFrom 中，消息会被静默丢弃。

# 6. 检查是否为群消息（群消息默认禁用）
cat ~/.openclaw/openclaw.json | jq '.channels.whatsapp.groupPolicy'
# "disabled" 表示所有群消息都会被忽略。

# 7. 检查队列拥堵（代理正忙于其他任务）
grep "lane wait exceeded" ~/.openclaw/logs/gateway.err.log | tail -5
# 如果代理卡在长时间的 LLM 调用上，新消息会排队等待。

# 8. 检查代理运行超时
grep "embedded run timeout" ~/.openclaw/logs/gateway.err.log | tail -5
# 硬性限制为 600 秒（10 分钟）。如果代理的响应超过此时间，会被强制终止。
```

### "WhatsApp 完全断开连接"

```bash
# 检查凭证文件是否存在（应有约 1400 个文件）
ls ~/.openclaw/credentials/whatsapp/default/ | wc -l

# 如果为 0 个文件：会话从未创建或被清除
# 修复：使用 `openclaw configure` 重新配对

# 检查 QR/配对事件
grep -i "pair\|link\|qr\|scan\|logged out" ~/.openclaw/logs/gateway.log | tail -10

# 检查 Baileys 错误
grep -i "baileys\|DisconnectReason\|logout\|stream:error" ~/.openclaw/logs/gateway.err.log | tail -20

# 终极修复：删除凭证并重新配对
# rm -rf ~/.openclaw/credentials/whatsapp/default/
# openclaw configure
```

---

## 故障排除：Telegram

### "机器人有问题 / 会忘记事情"

两个看起来相同但本质不同的问题：

```bash
# 1. 检查配置验证错误（最常见的一种）
grep -i "telegram.*unrecognized\|telegram.*invalid\|telegram.*policy" ~/.openclaw/logs/gateway.err.log | tail -10
# 已知问题：accounts 下的 "token" 和 "username" 键不被识别。
# 正确的字段是 "botToken"，而非 "token"。

# 2. 检查实际配置
cat ~/.openclaw/openclaw.json | jq '.channels.telegram'
# 确认每个机器人都有 "botToken"（而非 "token"）和 "name" 字段。

# 3. 检查轮询状态 — 机器人在 getUpdates 超时后会停止工作
grep -i "telegram.*exit\|telegram.*timeout\|getUpdates" ~/.openclaw/logs/gateway.err.log | tail -10
# "[telegram] [sales] channel exited: Request to 'getUpdates' timed out after 500 seconds"
# 意思是机器人与 Telegram API 的连接丢失，停止了监听。
# 修复：重启网关 — `openclaw gateway restart`

# 4. 检查轮询偏移量（如果机器人"忘记"或重放旧消息）
cat ~/.openclaw/telegram/update-offset-coder.json
cat ~/.openclaw/telegram/update-offset-sales.json
# 如果 lastUpdateId 卡住或为 0，机器人会重新处理旧消息。
# 要跳到最新消息：网关在重启时会自动设置此值。

# 5. 检查两个机器人是否都在启动
grep -i "telegram.*starting\|telegram.*coder\|telegram.*sales" ~/.openclaw/logs/gateway.log | tail -10

# 6. "机器人忘记" — 这通常是会话问题，而非 Telegram 问题
# 每个 Telegram 用户在 sessions.json 中都有自己的会话。
# 检查会话是否存在：
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r 'to_entries[] | select(.key | test("telegram")) | "\(.key) | \(.value.origin.label // "?")"'

# 7. 检查是否发生了压缩（上下文窗口被修剪 = "忘记了"）
SESS_ID="paste-session-id"
grep '"compaction"' ~/.openclaw/agents/main/sessions/$SESS_ID.jsonl | wc -l
# 如果压缩次数 > 0，旧消息已从上下文中被修剪。
# 代理的压缩模式为：
cat ~/.openclaw/openclaw.json | jq '.agents.defaults.compaction'
```

### Telegram 配置修复模板

```bash
# 正确的 Telegram 配置结构：
cat ~/.openclaw/openclaw.json | jq '.channels.telegram = {
  "enabled": true,
  "accounts": {
    "coder": {
      "name": "Bot Display Name",
      "enabled": true,
      "botToken": "your-bot-token-here"
    },
    "sales": {
      "name": "Sales Bot Name",
      "enabled": true,
      "botToken": "your-bot-token-here"
    }
  },
  "dmPolicy": "pairing",
  "groupPolicy": "disabled"
}' > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json
```

---

## 故障排除：Signal

### "Signal RPC 发送消息失败"

这会阻塞 cron 任务和跨通道通知。

```bash
# 1. 检查 signal-cli 进程是否存活
ps aux | grep "[s]ignal-cli"

# 2. 检查 RPC 端点
grep -i "signal.*starting\|signal.*8080\|signal.*rpc" ~/.openclaw/logs/gateway.log | tail -10
# 应看到："[signal] [default] starting provider (http://127.0.0.1:8080)"

# 3. 检查连接不稳定
grep -i "HikariPool\|reconnecting\|SSE stream error\|terminated" ~/.openclaw/logs/gateway.err.log | tail -10
# "HikariPool-1 - Thread starvation or clock leap detected" = signal-cli 内部数据库问题
# "SSE stream error: TypeError: terminated" = 与 signal-cli 守护进程的连接丢失

# 4. 检查速率限制
grep -i "signal.*rate" ~/.openclaw/logs/gateway.err.log | tail -5
# "Signal RPC -5: Failed to send message due to rate limiting"

# 5. 检查目标格式错误
grep -i "unknown target" ~/.openclaw/logs/gateway.err.log | tail -5
# "Unknown target "adi" for Signal. Hint: <E.164|uuid:ID|...>"
# 代理必须使用电话号码（+1...）或 uuid: 格式，而非名称。

# 6. 修复配置文件名警告刷屏
grep -c "No profile name set" ~/.openclaw/logs/gateway.err.log
# 如果数量很高：运行 signal-cli updateProfile 设置名称

# 7. 直接测试 signal-cli
ACCT=$(cat ~/.openclaw/openclaw.json | jq -r '.channels.signal.account')
echo "Account: $ACCT"
# signal-cli -a $ACCT send -m "test" +TARGET_NUMBER

# 8. 检查 signal-cli 守护进程是否需要重启
# 网关将 signal-cli 作为子进程管理。
# 重启整个网关：openclaw gateway restart
```

---

## 故障排除：Cron 任务

```bash
# 1. 所有任务概览
cat ~/.openclaw/cron/jobs.json | jq -r '.jobs[] | "\(.enabled | if . then "ON " else "OFF" end) \(.state.lastStatus // "never" | if . == "error" then "FAIL" elif . == "ok" then "OK  " else .  end) \(.name)"'

# 2. 失败任务及错误详情
cat ~/.openclaw/cron/jobs.json | jq '.jobs[] | select(.state.lastStatus == "error") | {name, error: .state.lastError, lastRun: (.state.lastRunAtMs | . / 1000 | todate), id}'

# 3. 读取失败任务的运行日志
JOB_ID="paste-job-uuid-here"
tail -20 ~/.openclaw/cron/runs/$JOB_ID.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        obj = json.loads(line)
        if obj.get('type') == 'message':
            role = obj['message']['role']
            text = ''.join(c.get('text','') for c in obj['message'].get('content',[]) if isinstance(c,dict))
            if text.strip():
                print(f'[{role}] {text[:300]}')
    except: pass
"

# 4. 常见的 cron 失败原因：
#    - "Signal RPC -1" → Signal 守护进程宕机，参见上方 Signal 章节
#    - "gateway timeout after 10000ms" → cron 触发时网关正在重启
#    - "Brave Search 429" → 免费层级速率限制（2000 次/月）
#    - "embedded run timeout" → 任务执行超过 600 秒

# 5. 下一次计划运行时间
cat ~/.openclaw/cron/jobs.json | jq -r '.jobs[] | select(.enabled) | "\(.name): \((.state.nextRunAtMs // 0) | . / 1000 | todate)"'

# 6. 暂时禁用故障任务
cat ~/.openclaw/cron/jobs.json | jq '(.jobs[] | select(.name == "JOB_NAME")).enabled = false' > /tmp/cron.json && mv /tmp/cron.json ~/.openclaw/cron/jobs.json
```

---

## 故障排除：记忆 / "它忘记了"

记忆系统有 3 层。当代理"忘记"时，其中某一层出了问题：

### 第 1 层：上下文窗口（会话内）

```bash
# 检查某次会话的压缩次数（压缩 = 旧消息被修剪）
grep -c '"compaction"' ~/.openclaw/agents/main/sessions/SESSION_ID.jsonl
# 7 次压缩 = 代理已"忘记"最早消息 7 次。

# 检查压缩模式
cat ~/.openclaw/openclaw.json | jq '.agents.defaults.compaction'
# "safeguard" = 仅在触及上下文限制时压缩
```

### 第 2 层：工作区记忆文件

```bash
# 查看存在哪些日志记忆文件
ls -la ~/.openclaw/workspace/memory/

# 查看 MEMORY.md 内容（长期精选记忆）
cat ~/.openclaw/workspace/MEMORY.md

# 在记忆文件中搜索特定内容
grep -ri "KEYWORD" ~/.openclaw/workspace/memory/
```

### 第 3 层：向量记忆数据库（SQLite + Gemini 嵌入）

```bash
# 查看已索引的文件
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT path, size, datetime(mtime/1000, 'unixepoch') as modified FROM files;"

# 查看文本块（片段）数量
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT COUNT(*) FROM chunks;"

# 按文本搜索块（FTS5 全文搜索）
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT substr(text, 1, 200) FROM chunks_fts WHERE chunks_fts MATCH 'KEYWORD' LIMIT 5;"

# 检查嵌入配置
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT value FROM meta WHERE key='memory_index_meta_v1';" | python3 -m json.tool

# 检查 Gemini 嵌入速率限制（会导致索引失败）
grep -i "gemini.*batch.*failed\|RESOURCE_EXHAUSTED\|429" ~/.openclaw/logs/gateway.err.log | tail -10
# "embeddings: gemini batch failed (2/2); disabling batch" = 索引功能降级

# 重建记忆索引（重新索引所有工作区文件）
# 删除数据库并重启网关 — 它会自动重建：
# rm ~/.openclaw/memory/main.sqlite && openclaw gateway restart
```

---

## 搜索会话

### 查找某人的对话

```bash
# 按名称搜索会话索引（不区分大小写）
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r 'to_entries[] | select(.value.origin.label // "" | test("NAME"; "i")) | "\(.value.sessionId) | \(.value.lastChannel) | \(.value.origin.label)"'
```

### 按通道查找会话

```bash
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r 'to_entries[] | select(.value.lastChannel == "whatsapp") | "\(.value.sessionId) | \(.value.origin.label // .key)"'
# 将 "whatsapp" 替换为：signal、telegram，或检查 .key 以查找 cron 会话
```

### 最近的会话

```bash
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r '[to_entries[] | {id: .value.sessionId, updated: .value.updatedAt, label: (.value.origin.label // .key), ch: (.value.lastChannel // "cron")}] | sort_by(.updated) | reverse | .[:10][] | "\(.updated | . / 1000 | todate) | \(.ch) | \(.label)"'
```

### 跨所有会话搜索消息内容

```bash
# 快速：查找哪些会话文件包含某关键词
grep -l "KEYWORD" ~/.openclaw/agents/main/sessions/*.jsonl

# 详细：显示匹配消息及时间戳
grep "KEYWORD" ~/.openclaw/agents/main/sessions/*.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    path, data = line.split(':', 1)
    try:
        obj = json.loads(data)
        if obj.get('type') == 'message':
            role = obj['message']['role']
            text = ''.join(c.get('text','') for c in obj['message'].get('content',[]) if isinstance(c,dict))
            if text.strip():
                sid = path.split('/')[-1].replace('.jsonl','')[:8]
                ts = obj.get('timestamp','')[:19]
                print(f'{ts} [{sid}] [{role}] {text[:200]}')
    except: pass
" | head -30
```

### 读取特定会话转录

```bash
# 查看某次会话的最后 30 条消息
tail -50 ~/.openclaw/agents/main/sessions/SESSION_ID.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        obj = json.loads(line)
        if obj.get('type') == 'message':
            role = obj['message']['role']
            text = ''.join(c.get('text','') for c in obj['message'].get('content',[]) if isinstance(c,dict))
            if text.strip() and role != 'toolResult':
                print(f'[{role}] {text[:300]}')
                print()
    except: pass
"
```

---

## 配置编辑

### 安全编辑模式

始终遵循：备份、用 jq 编辑、重启。

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.manual
jq 'YOUR_EDIT_HERE' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json
openclaw gateway restart
```

### 常见编辑操作

```bash
# 将 WhatsApp 切换为白名单模式
jq '.channels.whatsapp.dmPolicy = "allowlist" | .channels.whatsapp.allowFrom = ["+1XXXXXXXXXX"]' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 启用 WhatsApp 自动驾驶模式（机器人代表你回复所有人）
jq '.channels.whatsapp += {dmPolicy: "open", selfChatMode: false, allowFrom: ["*"]}' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 将号码加入 Signal 白名单
jq '.channels.signal.allowFrom += ["+1XXXXXXXXXX"]' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 更改模型
jq '.agents.defaults.models = {"anthropic/claude-sonnet-4": {"alias": "sonnet"}}' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 设置并发数
jq '.agents.defaults.maxConcurrent = 10 | .agents.defaults.subagents.maxConcurrent = 10' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 禁用某个插件
jq '.plugins.entries.imessage.enabled = false' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json
```

### 从备份恢复

```bash
# 最新备份
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json

# 按日期列出所有备份
ls -lt ~/.openclaw/openclaw.json.bak*

# 重启前验证 JSON
python3 -m json.tool ~/.openclaw/openclaw.json > /dev/null && echo "OK" || echo "BROKEN"

# 终极重置
openclaw configure
```

---

## 通道安全模式

| 模式 | 行为 | 风险 |
|---|---|---|
| `open` + `allowFrom: ["*"]` | 任何人可发送消息，机器人回复所有人 | 高 — 消耗 API 额度，机器人以你的身份发言 |
| `allowlist` + `allowFrom: ["+1..."]` | 仅列表中的号码可通过 | 低 — 显式控制 |
| `pairing` | 未知发送者会收到验证码，需你审批 | 低 — 审批门槛 |
| `disabled` | 通道完全关闭 | 无 |

### 检查当前安全状态

```bash
cat ~/.openclaw/openclaw.json | jq '{
  whatsapp: {policy: .channels.whatsapp.dmPolicy, from: .channels.whatsapp.allowFrom, groups: .channels.whatsapp.groupPolicy, selfChat: .channels.whatsapp.selfChatMode},
  signal: {policy: .channels.signal.dmPolicy, from: .channels.signal.allowFrom, groups: .channels.signal.groupPolicy},
  telegram: {policy: .channels.telegram.dmPolicy, groups: .channels.telegram.groupPolicy, bots: [.channels.telegram.accounts | to_entries[] | "\(.key)=\(.value.enabled)"]},
  imessage: {enabled: .channels.imessage.enabled, policy: .channels.imessage.dmPolicy}
}'
```

---

## 工作区文件

| 文件 | 内容 | 何时编辑 |
|---|---|---|
| `SOUL.md` | 人格：语气、风格（"不用破折号，小写随意风格"） | 要更改机器人说话方式时 |
| `IDENTITY.md` | 名称（Jarvis）、生物类型、表情符号 | 要重新品牌化时 |
| `USER.md` | 所有者信息、偏好设置 | 用户上下文变化时 |
| `AGENTS.md` | 操作规则：记忆协议、安全策略、群聊行为、心跳指令 | 要更改机器人行为时 |
| `BOOT.md` | 启动指令（自动驾驶通知协议：WA → Signal） | 要更改启动时行为时 |
| `HEARTBEAT.md` | 周期清单（为空 = 不发起心跳 API 调用） | 添加/移除周期任务时 |
| `MEMORY.md` | 精选长期记忆（仅在主/直接会话中加载） | 机器人自行管理 |
| `TOOLS.md` | 联系人、SSH 主机、设备昵称 | 添加本地工具备注时 |
| `memory/*.md` | 每日原始日志、主题专用对话日志 | 机器人自动写入 |

---

## 会话 JSONL 格式

每个 `.jsonl` 文件每行一个 JSON 对象。类型如下：

| type | 说明 |
|---|---|
| `session` | 会话头部：id、时间戳、cwd |
| `message` | 对话回合：角色（user/assistant/toolResult）、内容、模型、用量 |
| `custom` | 元数据：`model-snapshot`、`openclaw.cache-ttl` |
| `compaction` | 上下文窗口被修剪（旧消息被丢弃） |
| `model_change` | 会话中途切换了模型 |
| `thinking_level_change` | 思维级别被调整 |

会话索引（`sessions.json`）的键：
- 格式：`agent:main:{channel}:{contact}` 或 `agent:main:cron:{job-uuid}`
- 字段：`sessionId`（UUID = 文件名）、`lastChannel`、`origin.label`（人类可读名称）、`origin.from`（规范地址）、`updatedAt`（纪元毫秒）、`chatType`（直接/群组）

---

## 网关启动序列

正常启动耗时约 3 秒：
```
[heartbeat] started
[gateway] listening on ws://127.0.0.1:18789
[browser/service] Browser control service ready
[hooks] loaded 3 internal hook handlers (boot-md, command-logger, session-memory)
[whatsapp] [default] starting provider
[signal] [default] starting provider (http://127.0.0.1:8080)
[telegram] [coder] starting provider
[telegram] [sales] starting provider
[whatsapp] Listening for personal WhatsApp inbound messages.
[signal] signal-cli: Started HTTP server on /127.0.0.1:8080
```

如果缺少任何一行，说明对应组件启动失败。请检查 `gateway.err.log`。

---

## 已知错误模式

| 错误 | 含义 | 修复方法 |
|---|---|---|
| `Web connection closed (status 408)` | WhatsApp Web 超时，自动重试最多 12 次 | 通常能自愈。如果达到 12/12，重启网关 |
| `Signal RPC -1: Failed to send message` | signal-cli 守护进程连接丢失 | 重启网关 |
| `Signal RPC -5: Failed to send message due to rate limiting` | Signal 速率限制 | 等待后重试，降低消息频率 |
| `No profile name set`（signal-cli WARN） | 日志刷屏，无害 | `signal-cli -a +ACCOUNT updateProfile --given-name "Name"` |
| `Cross-context messaging denied` | 代理尝试跨通道发送消息 | 非 bug — 属于安全护栏。消息必须从正确的通道会话发出 |
| `getUpdates timed out after 500 seconds` | Telegram 机器人轮询连接丢失 | 重启网关 |
| `Unrecognized keys: "token", "username"` | Telegram 机器人配置键错误 | 在 openclaw.json 中使用 `botToken` 而非 `token` |
| `RESOURCE_EXHAUSTED`（Gemini 429） | 嵌入速率限制 | 减少工作区文件变更频率，或升级 Gemini 配额 |
| `lane wait exceeded` | 代理被长时间 LLM 调用阻塞 | 等待，或卡住超过 2 分钟则重启 |
| `embedded run timeout: timeoutMs=600000` | 代理响应超过 10 分钟 | 将任务拆分为更小的部分 |
| `gateway timeout after 10000ms` | 重启窗口期间网关不可达 | cron 在网关宕机时触发 — 临时性问题 |

---

## 扩展 OpenClaw

OpenClaw 有 4 个扩展层。每层解决不同问题：

| 层级 | 内容 | 位置 | 如何添加 |
|---|---|---|---|
| **技能** | 代理按需加载的知识和工作流 | `/opt/homebrew/lib/node_modules/openclaw/skills/` 或 `~/.openclaw/workspace/skills/` | `clawdhub install <slug>` 或 `npx add-skill <repo>` |
| **扩展** | 自定义通道插件（TypeScript） | `~/.openclaw/extensions/{name}/` | 创建 `openclaw.plugin.json` + TypeScript 源码 |
| **通道** | 消息平台（内置） | `openclaw.json → channels.*` + `plugins.entries.*` | 在 openclaw.json 中配置，添加凭证 |
| **Cron 任务** | 定时自主任务 | `~/.openclaw/cron/jobs.json` | 代理通过工具创建，或直接编辑 jobs.json |

### 技能：ClawdHub 生态系统

技能是扩展代理知识和能力的主要方式。它们是带有可选脚本/资源的 Markdown 文件，在相关时加载到上下文中。

```bash
# 搜索技能（跨注册表的向量搜索）
clawdhub search "postgres optimization"
clawdhub search "image generation"

# 浏览最新技能
clawdhub explore

# 安装技能
clawdhub install supabase-postgres-best-practices
clawdhub install nano-banana-pro

# 安装特定版本
clawdhub install my-skill --version 1.2.3

# 列出已安装的技能
clawdhub list

# 更新所有已安装技能
clawdhub update --all

# 更新特定技能
clawdhub update my-skill
clawdhub update my-skill --force  # 覆盖本地更改
```

**当前已安装的技能（随 OpenClaw 捆绑提供）：**

| 分类 | 技能 |
|---|---|
| **消息** | discord, slack, imsg, wacli, voice-call |
| **社交/网络** | bird (X/Twitter), blogwatcher, github, trello, notion |
| **Google** | gog, google-workspace-mcp, goplaces, local-places |
| **媒体** | nano-banana-pro (Gemini 图片生成), openai-image-gen, video-frames, gifgrep, pixelation, sag (TTS), openai-whisper, sherpa-onnx-tts, songsee, camsnap |
| **编码代理** | coding-agent (Codex/Claude Code/Pi), ccbg (后台运行器), tmux |
| **生产力** | apple-notes, apple-reminders, bear-notes, things-mac, obsidian, himalaya (邮件) |
| **智能家居** | openhue (Philips Hue), eightctl (Eight Sleep), sonoscli, blucli (BluOS) |
| **开发工具** | github, worktree, starter, desktop, supabase-postgres-best-practices, superdesign |
| **内容** | remotion-best-practices, remotion-fastest-tech-stack, humanizer, summarize, market, buildinpublic |
| **元技能** | skill-creator, clawdhub, find-skills, add-skill, model-usage, session-logs, recentplans, canvas |

### 创建自定义技能

一个技能就是一个包含 `SKILL.md` 的文件夹：

```
my-skill/
├── SKILL.md              # 必需：YAML 前置元数据 + Markdown 指令
├── scripts/              # 可选：可执行脚本
├── references/           # 可选：按需加载的文档
└── assets/               # 可选：模板、图片
```

**SKILL.md 格式：**
```markdown
---
name: my-skill
description: 说明其功能及何时触发。此描述是主要
  触发器 — 代理通过它决定是否加载完整技能。
---

# My Skill

指令写在这里。仅在技能触发后才加载。
保持 500 行以内。将大段内容拆分到 references/ 文件中。
```

**核心原则：上下文窗口是共享资源。** 只包含代理还不知道的内容。优先使用简洁示例而非冗长解释。

```bash
# 发布到 ClawdHub
clawdhub login
clawdhub publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0

# 或发布到 GitHub 以配合 npx add-skill 使用
# （详见 add-skill 技能文档）
```

### 多代理编排

OpenClaw 可以派生其他 AI 代理（Codex、Claude Code、Pi）作为后台工作者。这是并行运行编码任务、代码审查或任何受益于多代理协作的工作的方式。

**模式：** `bash pty:true background:true workdir:/path command:"agent 'task'"`

```bash
# 派生 Codex 构建某个项目（后台、自动审批）
bash pty:true workdir:~/project background:true command:"codex exec --full-auto 'Build a REST API for todos'"
# 返回 sessionId 用于追踪

# 派生 Claude Code 处理不同任务
bash pty:true workdir:~/other-project background:true command:"claude 'Refactor the auth module'"

# 监控所有运行中的代理
process action:list

# 查看特定代理的输出
process action:log sessionId:XXX

# 如果代理提问，发送输入
process action:submit sessionId:XXX data:"yes"

# 终止卡住的代理
process action:kill sessionId:XXX
```

**并行 PR 审查：**
```bash
# 获取所有 PR 引用
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'

# 每个 PR 启动一个代理
bash pty:true workdir:~/project background:true command:"codex exec 'Review PR #86. git diff origin/main...origin/pr/86'"
bash pty:true workdir:~/project background:true command:"codex exec 'Review PR #87. git diff origin/main...origin/pr/87'"
```

**使用 git worktree 并行修复问题：**
```bash
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

bash pty:true workdir:/tmp/issue-78 background:true command:"codex --yolo 'Fix issue #78: description. Commit and push.'"
bash pty:true workdir:/tmp/issue-99 background:true command:"codex --yolo 'Fix issue #99: description. Commit and push.'"
```

**代理完成后自动通知：**
```bash
bash pty:true workdir:~/project background:true command:"codex --yolo exec 'Your task.

When completely finished, run: openclaw gateway wake --text \"Done: summary\" --mode now'"
```

### 添加新通道

通道是代理可以通信的消息平台。内置通道：WhatsApp、Signal、Telegram、iMessage、Discord、Slack。

**启用内置通道：**
```bash
# 1. 启用插件
jq '.plugins.entries.discord.enabled = true' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 2. 添加通道配置
jq '.channels.discord = {enabled: true, dmPolicy: "pairing", groupPolicy: "disabled"}' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 3. 添加凭证（通道特定）
# 4. 重启网关
openclaw gateway restart
```

**构建自定义通道扩展：**

```
~/.openclaw/extensions/{name}/
├── openclaw.plugin.json    # {"id": "name", "channels": ["name"], "configSchema": {...}}
├── package.json            # 标准 npm 包
├── index.ts                # 入口文件
└── src/
    ├── channel.ts          # 入站消息处理 + 出站发送
    ├── actions.ts          # 代理可调用的工具操作
    ├── runtime.ts          # 生命周期：启动、停止、健康检查
    ├── config-schema.ts    # 插件配置的 JSON Schema
    └── types.ts            # TypeScript 类型
```

```bash
# 列出已安装的扩展
ls ~/.openclaw/extensions/

# 查看扩展清单
cat ~/.openclaw/extensions/*/openclaw.plugin.json | jq .

# 检查扩展源文件
find ~/.openclaw/extensions/ -name "*.ts" -not -path "*/node_modules/*"
```

### 跨通道通信

代理可以在一个通道接收消息，在另一个通道发送消息，但有护栏限制：

```bash
# 检查跨上下文设置
cat ~/.openclaw/openclaw.json | jq '.tools.message.crossContext'
# allowAcrossProviders: true = 代理可以跨通道发送
# marker.enabled: false = 跨通道消息不添加 "[via Signal]" 前缀

# 如果看到 "Cross-context messaging denied" 错误：
# 代理尝试从绑定到通道 A 的会话发送到通道 B。
# 这是安全特性。要允许此行为：
jq '.tools.message.crossContext.allowAcrossProviders = true' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json
```

**BOOT.md 通知协议**（已配置）：
代理接收 WhatsApp 消息，在 WhatsApp 上回复，然后向 Signal 发送通知摘要。这是主要的跨通道模式 — 一个通道上自动驾驶，另一个通道上控制中心。

### Canvas：连接设备的 Web 界面

向已连接的 Mac/iOS/Android 节点推送 HTML/游戏/仪表盘：

```bash
# 检查 canvas 配置
cat ~/.openclaw/openclaw.json | jq '.canvasHost // "not configured"'

# 列出已连接节点
openclaw nodes list

# 在节点上展示 HTML 内容
# canvas action:present node:<node-id> target:http://localhost:18793/__moltbot__/canvas/my-page.html

# Canvas 文件位于：
ls ~/.openclaw/canvas/
```

### 语音通话

通过 Twilio/Telnyx/Plivo 发起电话：

```bash
# 检查 voice-call 插件是否启用
cat ~/.openclaw/openclaw.json | jq '.plugins.entries["voice-call"] // "not configured"'

# CLI 用法
openclaw voicecall call --to "+15555550123" --message "Hello"
openclaw voicecall status --call-id <id>
```

### Cron：定时自主任务

```bash
# 查看所有任务
cat ~/.openclaw/cron/jobs.json | jq '.jobs[] | {name, enabled, schedule: .schedule, channel: .payload.channel, to: .payload.to}'

# 任务调度类型：
# "kind": "at", "atMs": <epoch>          — 特定时间一次性执行
# "kind": "every", "everyMs": <ms>       — 周期性间隔执行

# 任务投递目标：
# channel + to 字段决定结果发送到哪里（signal、whatsapp、telegram）
# sessionTarget: "isolated" = 每次运行使用全新上下文（不记忆之前的运行）

# 要添加任务，代理通过工具创建，或直接编辑 jobs.json：
# 在 ~/.openclaw/cron/jobs.json 中查看现有任务作为模板
```

---

## 许可证

MIT
