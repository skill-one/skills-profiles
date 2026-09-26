# OpenClaw 操作手册

诊断和修复实际问题。这里的所有命令都经过测试且可以正常工作。

---

## 快速健康检查

当出现任何问题时，首先运行这个。复制粘贴整个代码块：

```bash
echo "=== 网关 ===" && \
ps aux | grep -c "[o]penclaw" && \
echo "=== 配置 JSON ===" && \
python3 -m json.tool ~/.openclaw/openclaw.json > /dev/null 2>&1 && echo "JSON: 正常" || echo "JSON: 损坏" && \
echo "=== 通道 ===" && \
cat ~/.openclaw/openclaw.json | jq -r '.channels | to_entries[] | "\(.key): 政策=\(.value.dmPolicy // "n/a") 启用=\(.value.enabled // "隐式")"' && \
echo "=== 插件 ===" && \
cat ~/.openclaw/openclaw.json | jq -r '.plugins.entries | to_entries[] | "\(.key): \(.value.enabled)"' && \
echo "=== 凭证 ===" && \
ls ~/.openclaw/credentials/whatsapp/default/ 2>/dev/null | wc -l | xargs -I{} echo "WhatsApp 密钥: {} 个文件" && \
for d in ~/.openclaw/credentials/telegram/*/; do bot=$(basename "$d"); [ -f "$d/token.txt" ] && echo "Telegram $bot: 正常" || echo "Telegram $bot: 缺失"; done && \
[ -f ~/.openclaw/credentials/bird/cookies.json ] && echo "Bird cookies: 正常" || echo "Bird cookies: 缺失" && \
echo "=== 定时任务 ===" && \
cat ~/.openclaw/cron/jobs.json | jq -r '.jobs[] | "\(.name): 启用=\(.enabled) 状态=\(.state.lastStatus // "从未") \(.state.lastError // "")"' && \
echo "=== 最近错误 ===" && \
tail -10 ~/.openclaw/logs/gateway.err.log 2>/dev/null && \
echo "=== 内存数据库 ===" && \
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT COUNT(*) || ' 块, ' || (SELECT COUNT(*) FROM files) || ' 文件索引' FROM chunks;" 2>/dev/null
```

---

## 文件映射

```
~/.openclaw/
├── openclaw.json                    # 主配置 — 通道、认证、网关、插件、技能
├── openclaw.json.bak*               # 自动备份 (.bak, .bak.1, .bak.2 ...)
├── exec-approvals.json              # 执行批准套接字配置
│
├── agents/main/
│   ├── agent/auth-profiles.json     # Anthropic 认证令牌
│   └── sessions/
│       ├── sessions.json            # 会话索引 — 键类似于 agent:main:whatsapp:+1234
│       └── *.jsonl                  # 会话文本记录（每行一个 JSON）
│
├── workspace/                       # 代理工作区（git 跟踪）
│   ├── SOUL.md                      # 个性、写作风格、语气规则
│   ├── IDENTITY.md                  # 名称、生物类型、氛围
│   ├── USER.md                      # 所有者上下文和偏好
│   ├── AGENTS.md                    # 会话行为、内存规则、安全
│   ├── BOOT.md                      # 启动指令（自动驾驶通知协议）
│   ├── HEARTBEAT.md                 # 定期任务清单（空 = 无心跳 API 调用）
│   ├── MEMORY.md                    # 精选长期记忆（仅主会话加载）
│   ├── TOOLS.md                     # 联系人、SSH 主机、设备昵称
│   ├── memory/                      # 每日日志：YYYY-MM-DD.md, topic-chat.md
│   └── skills/                      # 工作区级别的技能
│
├── memory/main.sqlite               # 向量记忆数据库（Gemini 嵌入，FTS5 搜索）
│
├── logs/
│   ├── gateway.log                  # 运行时：启动、通道初始化、配置重新加载、关闭
│   ├── gateway.err.log              # 错误：连接中断、API 失败、超时
│   └── commands.log                 # 命令执行日志
│
├── cron/
│   ├── jobs.json                    # 任务定义（计划、有效负载、交付目标）
│   └── runs/                        # 每个任务的运行日志：{job-uuid}.jsonl
│
├── credentials/
│   ├── whatsapp/default/            # Baileys 会话：~1400 个 app-state-sync-key-*.json 文件
│   ├── telegram/{botname}/token.txt # 机器人令牌（每个机器人账户一个）
│   └── bird/cookies.json            # X/Twitter 认证 cookies
│
├── extensions/{name}/               # 自定义插件（TypeScript）
│   ├── openclaw.plugin.json         # {"id", "channels", "configSchema"}
│   ├── index.ts                     # 入口点
│   └── src/                         # channel.ts, actions.ts, runtime.ts, types.ts
│
├── identity/                        # device.json, device-auth.json
├── devices/                         # paired.json, pending.json
├── media/inbound/                   # 接收的图像、音频文件
├── media/browser/                   # 浏览器截图
├── browser/openclaw/user-data/      # Chromium 配置文件 (~180MB)
├── tools/signal-cli/                # Signal CLI 二进制文件
├── subagents/runs.json              # 子代理执行日志
├── canvas/index.html                # 连接设备网页 UI
└── telegram/
    ├── update-offset-coder.json     # {"lastUpdateId": N} — Telegram 轮询光标
    └── update-offset-sales.json     # 将这些重置为 0 以重播遗漏的消息
```

---

## 故障排除：WhatsApp

### "我发送了消息但没有回复"

这是 #1 问题。消息到达但机器人没有回复。按顺序检查：

```bash
# 1. 机器人是否实际运行？
grep -i "whatsapp.*starting\|whatsapp.*listening" ~/.openclaw/logs/gateway.log | tail -5

# 2. 检查 408 超时中断（WhatsApp 网页经常断开连接）
grep -i "408\|499\|retry" ~/.openclaw/logs/gateway.err.log | tail -10
# 如果你看到 "Web connection closed (status 408). Retry 1/12" — 这是正常的，
# 它会自动恢复。但如果重试达到 12/12，会话完全丢失。

# 3. 检查跨上下文消息阻止
grep -i "cross-context.*denied" ~/.openclaw/logs/gateway.err.log | tail -10
# 常见："Cross-context messaging denied: action=send target provider "whatsapp" while bound to "signal""
# 这意味着代理处于 Signal 会话中，并尝试在 WhatsApp 上回复。
# 修复：消息需要通过 WhatsApp 会话上下文，而不是 Signal。

# 4. 检查该联系人的会话是否存在
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r 'to_entries[] | select(.key | test("whatsapp")) | "\(.key) | \(.value.origin.label // "?")"

# 5. 检查发送者是否被允许
cat ~/.openclaw/openclaw.json | jq '.channels.whatsapp | {dmPolicy, allowFrom, selfChatMode, groupPolicy}'
# 如果 dmPolicy 是 "allowlist" 且发送者不在 allowFrom 中，消息将被静默丢弃。

# 6. 检查是否是群组消息（群组默认禁用）
cat ~/.openclaw/openclaw.json | jq '.channels.whatsapp.groupPolicy'
# "disabled" 表示所有群组消息都被忽略。

# 7. 检查车道拥塞（代理正在处理其他任务）
grep "lane wait exceeded" ~/.openclaw/logs/gateway.err.log | tail -5
# 如果代理卡在长时间的 LLM 调用上，新消息将排队。

# 8. 检查代理运行超时
grep "embedded run timeout" ~/.openclaw/logs/gateway.err.log | tail -5
# 硬限制是 600 秒（10 分钟）。如果代理的回复时间超过这个时间，它将被终止。
```

### "WhatsApp 完全断开连接"

```bash
# 检查凭证文件是否存在（应该有 ~1400 个文件）
ls ~/.openclaw/credentials/whatsapp/default/ | wc -l

# 如果 0 个文件：会话从未创建或被擦除
# 修复：重新配对 `openclaw configure`

# 检查 QR/配对事件
grep -i "pair\|link\|qr\|scan\|logged out" ~/.openclaw/logs/gateway.log | tail -10

# 检查 Baileys 错误
grep -i "baileys\|DisconnectReason\|logout\|stream:error" ~/.openclaw/logs/gateway.err.log | tail -20

# 核心修复：删除凭证并重新配对
# rm -rf ~/.openclaw/credentials/whatsapp/default/
# openclaw configure
```

---

## 故障排除：Telegram

### "机器人有问题 / 忘记事情"

这是两个看起来相同的问题：

```bash
# 1. 检查配置验证错误（常见问题）
grep -i "telegram.*unrecognized\|telegram.*invalid\|telegram.*policy" ~/.openclaw/logs/gateway.err.log | tail -10
# 已知问题：openclaw.json 中的 "token" 和 "username" 下面的键没有被识别。
# 正确的字段是 "botToken"，而不是 "token"。

# 2. 检查实际配置
cat ~/.openclaw/openclaw.json | jq '.channels.telegram'
# 验证每个机器人都有 "botToken"（不是 "token"）和 "name" 字段。

# 3. 检查轮询状态——机器人会在 getUpdates 超时后丢失轮询连接
grep -i "telegram.*exit\|telegram.*timeout\|getUpdates" ~/.openclaw/logs/gateway.err.log | tail -10
# "[telegram] [sales] channel exited: Request to 'getUpdates' timed out after 500 seconds"
# 这意味着机器人失去了与 Telegram API 的连接并停止监听。
# 修复：重启网关 — `openclaw gateway restart`

# 4. 检查轮询偏移量（如果机器人“忘记”或重播旧消息）
cat ~/.openclaw/telegram/update-offset-coder.json
cat ~/.openclaw/telegram/update-offset-sales.json
# 如果 lastUpdateId 卡住或为 0，机器人将重新处理旧消息。
# 要跳转到最新：网关在重启时自动设置这个。

# 5. 检查两个机器人是否都在启动
grep -i "telegram.*starting\|telegram.*coder\|telegram.*sales" ~/.openclaw/logs/gateway.log | tail -10

# 6. "机器人忘记"——这通常是会话问题，而不是 Telegram
# 每个Telegram 用户都会在 sessions.json 中获得自己的会话。
# 检查会话是否存在：
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r 'to_entries[] | select(.key | test("telegram")) | "\(.key) | \(.value.origin.label // .key)"

# 7. 检查是否发生压缩（上下文窗口被修剪 = "忘记"）
SESS_ID="粘贴会话 ID"
grep '"compaction"' ~/.openclaw/agents/main/sessions/$SESS_ID.jsonl | wc -l
# 压缩计数 > 0，表示从上下文中修剪了旧消息。
# 代理的压缩模式是：
cat ~/.openclaw/openclaw.json | jq '.agents.defaults.compaction'
```

### Telegram 配置修复模板

```bash
# 正确的 Telegram 配置结构：
cat ~/.openclaw/openclaw.json | jq '.channels.telegram = {
  "enabled": true,
  "accounts": {
    "coder": {
      "name": "机器人显示名称",
      "enabled": true,
      "botToken": "你的机器人令牌"
    },
    "sales": {
      "name": "销售机器人名称",
      "enabled": true,
      "botToken": "你的机器人令牌"
    }
  },
  "dmPolicy": "pairing",
  "groupPolicy": "disabled"
}' > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json
```

---

## 故障排除：Signal

### "Signal RPC 发送消息失败"

这会阻止定时任务和跨通道通知。

```bash
# 1. 检查 signal-cli 进程是否存活
ps aux | grep "[s]ignal-cli"

# 2. 检查 RPC 端点
grep -i "signal.*starting\|signal.*8080\|signal.*rpc" ~/.openclaw/logs/gateway.log | tail -10
# 应该看到："[signal] [default] starting provider (http://127.0.0.1:8080)"

# 3. 检查连接不稳定
grep -i "HikariPool\|reconnecting\|SSE stream error\|terminated" ~/.openclaw/logs/gateway.err.log | tail -10
# "HikariPool-1 - Thread starvation or clock leap detected" = signal-cli 内部数据库问题
# "SSE stream error: TypeError: terminated" = 失去与 signal-cli 守护进程的连接

# 4. 检查速率限制
grep -i "signal.*rate" ~/.openclaw/logs/gateway.err.log | tail -5
# "Signal RPC -5: Failed to send message due to rate limiting"

# 5. 检查目标格式错误
grep -i "unknown target" ~/.openclaw/logs/gateway.err.log | tail -5
# "Unknown target "adi" for Signal. Hint: <E.164|uuid:ID|...>"
# 代理必须使用电话号码 (+1...) 或 uuid: 格式，而不是名称。

# 6. 修复配置名称警告垃圾信息
grep -c "No profile name set" ~/.openclaw/logs/gateway.err.log
# 如果计数高：运行 `signal-cli updateProfile` 设置一个名称

# 7. 直接测试 signal-cli
ACCT=$(cat ~/.openclaw/openclaw.json | jq -r '.channels.signal.account')
echo "账户: $ACCT"
# signal-cli -a $ACCT send -m "test" +TARGET_NUMBER

# 8. 检查是否需要重启 signal-cli 守护进程
# 网关将 signal-cli 作为子进程管理。
# 重启整个网关：openclaw gateway restart
```

---

## 故障排除：定时任务

```bash
# 1. 概览所有任务
cat ~/.openclaw/cron/jobs.json | jq '.jobs[] | {name, enabled, schedule: .schedule, channel: .payload.channel, to: .payload.to}'

# 2. 失败的任务及其错误详情
cat ~/.openclaw/cron/jobs.json | jq '.jobs[] | select(.state.lastStatus == "error") | {name, error: .state.lastError, lastRun: (.state.lastRunAtMs | . / 1000 | todate), id}'

# 3. 读取失败任务的实际运行日志
JOB_ID="粘贴任务 UUID"
tail -20 ~/.openclaw/cron/runs/$JOB_ID.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        obj = json.loads(line)
        if obj.get('type') == 'message':
            role = obj['message']['role']
            text = ''.join(c.get('text','') for c in obj['message'].get('content',[]) if isinstance(c,dict))
            if text.strip():
                sid = path.split('/')[-1].replace('.jsonl','')[:8]
                ts = obj.get('timestamp','')[:19]
                print(f'{ts} [{sid}] [{role}] {text[:300]}')
    except: pass
"

# 4. 定时任务常见失败原因:
#    - "Signal RPC -1" → Signal 守护进程宕机，见 Signal 部分
#    - "gateway timeout after 10000ms" → 网关在重启窗口期间无法访问
#    - "Brave Search 429" → 免费套餐速率限制被击穿（每月 2000 个请求）
#    - "embedded run timeout" → 任务运行时间超过 600 秒

# 5. 下一个计划运行时间
cat ~/.openclaw/cron/jobs.json | jq -r '.jobs[] | select(.enabled) | "\(.name): \((.state.nextRunAtMs // 0) | . / 1000 | todate)"

# 6. 暂时禁用一个损坏的任务
cat ~/.openclaw/cron/jobs.json | jq '(.jobs[] | select(.name == "JOB_NAME")).enabled = false' > /tmp/cron.json && mv /tmp/cron.json ~/.openclaw/cron/jobs.json
```

---

## 故障排除：记忆 / "它忘记了"

记忆系统有 3 层。当代理“忘记”时，其中一层出了问题：

### 第 1 层：上下文窗口（在会话内）

```bash
# 检查会话的压缩计数（压缩 = 修剪旧消息）
grep -c '"compaction"' ~/.openclaw/agents/main/sessions/SESSION_ID.jsonl
# 7 次压缩 = 代理已经“忘记”了它最早的消息 7 次。

# 检查压缩模式
cat ~/.openclaw/openclaw.json | jq '.agents.defaults.compaction'
# "safeguard" = 只有在达到上下文限制时才压缩
```

### 第 2 层：工作区记忆文件

```bash
# 存在哪些每日记忆文件
ls -la ~/.openclaw/workspace/memory/

# MEMORY.md 中的内容（长期精选）
cat ~/.openclaw/workspace/MEMORY.md

# 在记忆文件中搜索特定内容
grep -ri "KEYWORD" ~/.openclaw/workspace/memory/
```

### 第 3 层：向量记忆数据库（SQLite + Gemini 嵌入）

```bash
# 索引的文件有哪些
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT path, size, datetime(mtime/1000, 'unixepoch') as modified FROM files;"

# 存在多少个块（文本片段）
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT COUNT(*) FROM chunks;"

# 通过文本搜索块（FTS5 全文搜索）
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT substr(text, 1, 200) FROM chunks_fts WHERE chunks_fts MATCH 'KEYWORD' LIMIT 5;"

# 检查嵌入配置
sqlite3 ~/.openclaw/memory/main.sqlite "SELECT value FROM meta WHERE key='memory_index_meta_v1';" | python3 -m json.tool

# 检查 Gemini 嵌入速率限制（会破坏索引）
grep -i "gemini.*batch.*failed\|RESOURCE_EXHAUSTED\|429" ~/.openclaw/logs/gateway.err.log | tail -10
# "embeddings: gemini batch failed (2/2); disabling batch" = 索引降级

# 重建记忆索引（重新索引所有工作区文件）
# 删除数据库并重启网关 — 它将重建：
# rm ~/.openclaw/memory/main.sqlite && openclaw gateway restart
```

---

## 搜索会话

### 查找某人的会话

```bash
# 通过名称搜索会话索引（不区分大小写）
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r 'to_entries[] | select(.value.origin.label // "" | test("NAME"; "i")) | "\(.value.sessionId) | \(.value.lastChannel) | \(.value.origin.label)"
```

### 通过通道查找会话

```bash
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r 'to_entries[] | select(.value.lastChannel == "whatsapp") | "\(.value.sessionId) | \(.value.origin.label // .key)"
# 替换 "whatsapp" 为：signal, telegram, 或检查 .key 以查找 cron 会话
```

### 最新的会话

```bash
cat ~/.openclaw/agents/main/sessions/sessions.json | jq -r '[to_entries[] | {id: .value.sessionId, updated: .value.updatedAt, label: (.value.origin.label // .key), ch: (.value.lastChannel // "cron")}] | sort_by(.updated) | reverse | .[:10][] | "\(.updated | . / 1000 | todate) | \(.ch) | \(.label)"
```

### 在所有会话中搜索消息内容

```bash
# 快速：查找包含关键词的会话文件
grep -l "KEYWORD" ~/.openclaw/agents/main/sessions/*.jsonl

# 详细：显示匹配的消息及其时间戳
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

### 读取特定会话文本记录

```bash
# 会话的最后 30 条消息
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

始终：备份，使用 jq 编辑，重启。

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.manual
jq 'YOUR_EDIT_HERE' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json
openclaw gateway restart
```

### 常见编辑

```bash
# 切换 WhatsApp 到 allowlist
jq '.channels.whatsapp.dmPolicy = "allowlist" | .channels.whatsapp.allowFrom = ["+1XXXXXXXXXX"]' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 启用 WhatsApp 自动驾驶（机器人像你一样回复所有人）
jq '.channels.whatsapp.dmPolicy = "open", selfChatMode: false, allowFrom: ["*"]' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 将号码添加到 Signal allowlist
jq '.channels.signal.allowFrom += ["+1XXXXXXXXXX"]' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 更改模型
jq '.agents.defaults.models = {"anthropic/claude-sonnet-4": {"alias": "sonnet"}}' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 设置并发性
jq '.agents.defaults.maxConcurrent = 10 | .agents.defaults.subagents.maxConcurrent = 10' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json

# 禁用一个插件
jq '.plugins.entries.imessage.enabled = false' ~/.openclaw/openclaw.json > /tmp/oc.json && mv /tmp/oc.json ~/.openclaw/openclaw.json
```

### 从备份恢复

```bash
# 最新备份
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json

# 列出所有备份按日期
ls -lt ~/.openclaw/openclaw.json.bak*

# 在重启之前验证 JSON
python3 -m json.tool ~/.openclaw/openclaw.json > /dev/null && echo "OK" || echo "损坏"

# 核心重置
openclaw configure
```

---

## 通道安全模式

| 模式 | 行为 | 风险 |
|---|---|---|
| `open` + `allowFrom: ["*"]` | 任何人都可以发送，机器人像你一样回复所有 | 高 — 消耗 API 信用，机器人像你一样说话 |
| `allowlist` + `allowFrom: ["+1..."]` | 只有列出的号码才能通过 | 低 — 明确控制 |
| `pairing` | 未知发送者会收到代码，你需要批准 | 低 — 批准门 |
| `disabled` | 通道完全关闭 | 无 |

### 检查当前安全态势

```bash
cat ~/.openclaw/openclaw.json | jq '{
  whatsapp: {policy: .channels.whatsapp.dmPolicy, from: .channels.whatsapp.allowFrom, groups: .channels.whatsapp.groupPolicy, selfChat: .channels.whatsapp.selfChatMode},
  signal: {policy: .channels.signal.dmPolicy, from: .channels.signal.allowFrom, groups: .channels.signal.groupPolicy},
  telegram: {policy: .channels.telegram.dmPolicy, groups: .channels.telegram.groupPolicy, bots: [.channels.telegram.accounts | to_entries[] | "\(.key)=\(.value.enabled)"],
  imessage: {enabled: .channels.imessage.enabled, policy: .channels.imessage.dmPolicy}
}'
```

---

## 工作区文件

| 文件 | 内容 | 何时编辑 |
|---|---|---|
| `SOUL.md` | 个性：语气、风格（“不使用破折号，小写非正式”） | 改变机器人说话方式 |
| `IDENTITY.md` | 名称（Jarvis）、生物类型、表情符号 | 重新品牌化 |
| `USER.md` | 所有者信息、偏好 | 当所有者上下文发生变化时 |
| `AGENTS.md` | 操作规则：记忆协议、安全、群组聊天行为、心跳指令 | 改变机器人行为 |
| `BOOT.md` | 启动指令（自动驾驶通知协议：WA → Signal） | 改变启动时发生的事情 |
| `HEARTBEAT.md` | 定期任务清单（空 = 无心跳 API 调用） | 添加/删除定期任务 |
| `MEMORY.md` | 精选长期记忆（仅在主/直接会话加载） | 机器人自己管理这个 |
| `TOOLS.md` | 联系人、SSH 主机、设备昵称 | 添加本地工具笔记 |
| `memory/*.md` | 每日原始日志、特定主题聊天日志 | 机器人自动写入 |

---

## 会话 JSONL 格式

每个 `.jsonl` 文件每行有一个 JSON 对象。类型：

| 类型 | 内容 |
|---|---|
| `session` | 会话标题：id、时间戳、cwd |
| `message` | 会话回合：角色（用户/助手/工具结果）、内容、模型、使用情况 |
| `custom` | 元数据：`model-snapshot`, `openclaw.cache-ttl` |
| `compaction` | 上下文窗口被修剪（旧消息被丢弃） |
| `model_change` | 会话中切换模型 |
| `thinking_level_change` | 调整思考级别 |

会话索引 (`sessions.json`) 键：
- 模式：`agent:main:{channel}:{contact}` 或 `agent:main:cron:{job-uuid}`
- 字段：`sessionId`（UUID = 文件名）、`lastChannel`、`origin.label`（人类名称）、`origin.from`（规范地址）、`updatedAt`（以毫秒为单位的 Unix 时间戳）、`chatType`（直接/群组）

---

## 网关启动顺序

正常启动大约需要 3 秒：
```
[heartbeat] 启动
[gateway] 监听 ws://127.0.0.1:18789
[browser/service] 浏览器控制服务就绪
[hooks] 加载 3 个内部钩子处理器（boot-md, command-logger, session-memory）
[whatsapp] [default] 启动提供程序
[signal] [default] 启动提供程序（http://127.0.0.1:8080）
[telegram] [coder] 启动提供程序
[telegram] [sales] 启动提供程序
[whatsapp] 监听个人 WhatsApp 入站消息。
[signal] signal-cli: 在 /127.0.0.1:8080 上启动 HTTP 服务器
```

如果任何行为丢失，则该组件启动失败。检查 `gateway.err.log`。

---

## 已知错误模式

| 错误 | 含义 | 修复 |
|---|---|---|
| `Web connection closed (status 408)` | WhatsApp 网页超时，自动重试最多 12 次 | 通常会自动恢复。如果达到 12/12，会话完全丢失 |
| `Signal RPC -1: Failed to send message` | signal-cli 守护进程失去连接 | 重启网关 |
| `Signal RPC -5: Failed to send message due to rate limiting` | Signal 速率限制 | 等待并重试，减少消息频率 |
| `No profile name set` (signal-cli 警告) | 洪水警告，无害 | 运行 `signal-cli -a +ACCOUNT updateProfile --given-name "Name"` |
| `Cross-context messaging denied` | 代理尝试跨通道发送 | 这是一种安全功能。消息必须从正确的通道会话中发送，而不是 Signal。 |
| `getUpdates timed out after 500 seconds` | Telegram 机器人丢失轮询连接 | 重启网关 |
| `Unrecognized keys: "token", "username"` | Telegram 机器人配置键错误 | 使用 `botToken` 而不是 `token` 在 openclaw.json 中 |
| `RESOURCE_EXHAUSTED` (Gemini 429) | Gemini 嵌入速率限制 | 减少工作区文件更迭，或升级 Gemini 配额 |
| `lane wait exceeded` | 代理被长时间 LLM 调用阻塞 | 等待，或重启如果卡住 > 2 分钟 |
| `embedded run timeout: timeoutMs=600000` | 代理回复超过 10 分钟 | 将任务分解成更小的部分 |
| `gateway timeout after 10000ms` | 在重启窗口期间网关无法访问 | 定时任务在网关宕机时触发 — 暂时现象 |

---

## 扩展 OpenClaw

OpenClaw 有 4 个扩展层。每个层解决不同的问题：

| 层 | 内容 | 位置 | 如何添加 |
|---|---|---|---|
| **技能** | 知识 + 工作流，代理按需加载 | `/opt/homebrew/lib/node_modules/openclaw/skills/` 或 `~/.openclaw/workspace/skills/` | `clawdhub install <slug>` 或 `npx add-skill <repo>` |
| **扩展** | 自定义通道插件（TypeScript） | `~/.openclaw/extensions/{name}/` | 创建 `openclaw.plugin.json` + TypeScript 源代码 |
| **通道** | 消息平台（内置） | `openclaw.json → channels.*` + `plugins.entries.*` | 配置在 openclaw.json 中，添加凭证 |
| **定时任务** | 定期自主任务 | `~/.openclaw/cron/jobs.json` | 代理通过工具创建它们，或直接编辑 jobs.json |

### 技能：ClawdHub 生态系统

技能是扩展代理知识和能力的主要方式。它们是包含可选脚本和资源的 markdown 文件，在相关内容加载时加载到上下文中。

```bash
# 搜索技能（跨注册表向量搜索）
clawdhub search "postgres optimization"
clawdhub search "image generation"

# 浏览最新技能
clawdhub explore

# 安装技能
clawdhub install supabase-postgres-best-practices
clawdhub install nano-banana-pro

# 安装特定版本的技能
clawdhub install my-skill --version 1.2.3

# 列出已安装的技能
clawdhub list

# 更新所有已安装的技能
clawdhub update --all

# 更新特定技能
clawdhub update my-skill
clawdhub update my-skill --force  # 覆盖本地更改
```

**当前安装的技能（与 OpenClaw 预装）：**

| 类别 | 技能 |
|---|---|
| **消息** | discord, slack, imsg, wacli, voice-call |
| **社交/网络** | bird (X/Twitter), blogwatcher, github, trello, notion |
| **Google** | gog, google-workspace-mcp, goplaces, local-places |
| **媒体** | nano-banana-pro (Gemini 图像生成), openai-image-gen, video-frames, gifgrep, pixelation, sag (TTS), openai-whisper, sherpa-onnx-tts, songsee, camsnap |
| **编码代理** | coding-agent (Codex/Claude Code/Pi), ccbg (后台运行器) |
| **生产力** | apple-notes, apple-reminders, bear-notes, things-mac, obsidian, himalaya (电子邮件) |
| **智能家居** | openhue (Philips Hue), eightctl (Eight Sleep), sonoscli, blucli (BluOS) |
| **开发工具** | github, worktree, starter, desktop |
| **内容** | remotion-best-practices, remotion-fastest-tech-stack, humanizer, summarize, market, buildinpublic |
| **元数据** | skill-creator, clawdhub, find-skills, add-skill, model-usage, session-logs, recentplans, canvas |

### 创建自己的技能

一个技能只是一个包含 `SKILL.md` 的文件夹：

```
my-skill/
├── SKILL.md              # 必须有：YAML 前置符 + markdown 说明
├── scripts/              # 可选：可执行脚本
├── references/           # 可选：在需要时加载的文档
└── assets/               # 可选：模板、图像
```

**SKILL.md 格式:**
```markdown
---
name: my-skill
description: 这是什么，何时触发。描述是代理决定是否加载完整技能的主要触发器 — 代理读取这个来决定是否加载完整技能。
---

# 我的技能

说明放在这里。保持少于 500 行。将大内容分解到 references/ 文件中。
```

**主要原则：上下文窗口是一个共享资源。** 只包含代理不知道的内容。优先简洁的示例而不是冗长的解释。

```bash
# 发布到 ClawdHub
clawdhub login
clawdhub publish ./my-skill --slug my-skill --name "我的技能" --version 1.0.0

# 或者发布到 GitHub 以便使用 npx add-skill
# （有关详情，请参阅 add-skill 技能）
```

### 多代理编排

OpenClaw 可以生成其他 AI 代理（Codex、Claude Code、Pi）作为后台工作进程。这是运行并行编码任务、审查或任何从多个代理中受益的工作的方式。

**模式：`bash pty:true background:true workdir:/path command:"agent 'task'"**

```bash
# 生成 Codex 来构建某物（后台，自动批准）
bash pty:true workdir:~/project background:true command:"codex exec --full-auto '构建一个用于待办事项的 REST API'"
# 返回 sessionId 以进行跟踪

# 在不同的任务上生成 Claude Code
bash pty:true workdir:~/other-project background:true command:"claude '重构认证模块'"

# 监控所有正在运行的代理
process action:list

# 检查特定代理的输出
process action:log sessionId:XXX

# 如果代理提问，发送输入
process action:submit sessionId:XXX data:"yes"

# 终止卡住的代理
process action:kill sessionId:XXX
```

**并行 PR 审查:**
```bash
# 获取所有 PR 引用
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'

# 启动一个代理每个 PR
bash pty:true workdir:~/project background:true command:"codex exec '审查 PR #86. git diff origin/main...origin/pr/86'"
bash pty:true workdir:~/project background:true command:"codex exec '审查 PR #87. git diff origin/main...origin/pr/87'"
```

**使用 git worktrees 进行并行问题修复:**
```bash
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

bash pty:true workdir:/tmp/issue-78 background:true command:"codex --yolo '修复问题 #78: 描述。提交并推送。'"
bash pty:true workdir:/tmp/issue-99 background:true command:"codex --yolo '修复问题 #99: 描述。提交并推送。'"
```

**自动通知代理完成:**
```bash
bash pty:true workdir:~/project background:true command:"codex --yolo exec '你的任务。

当完全完成后，运行: openclaw gateway wake --text \"完成: 摘要\" --mode now'"
```

### Canvas：连接设备的网页 UI

推送 HTML/游戏/仪表板到连接的 Mac/iOS/Android 节点：

```bash
# 检查 canvas 配置
cat ~/.openclaw/openclaw.json | jq '.canvasHost // "未配置"'

# 列出连接的节点
openclaw nodes list

# 在节点上呈现 HTML 内容
# canvas action:present node:<node-id> target:http://localhost:18793/__moltbot__/canvas/my-page.html

# Canvas 文件位于：
ls ~/.openclaw/canvas/
```

### 语音通话

通过 Twilio/Telnyx/Plivo 启动电话通话：

```bash
# 检查 voice-call 插件是否启用
cat ~/.openclaw/openclaw.json | jq '.plugins.entries["voice-call"] // "not configured"'

# CLI 使用
openclaw voicecall call --to "+15555550123" --message "你好"
openclaw voicecall status --call-id <id>
```

### Cron：定期自主任务

```bash
# 查看所有任务
cat ~/.openclaw/cron/jobs.json | jq '.jobs[] | {name, enabled, schedule: .schedule, channel: .payload.channel, to: .payload.to}'

# 任务计划类型:
# "kind": "at", "atMs": <epoch>          — 单次执行特定时间
# "kind": "every", "everyMs": <ms>       — 重复间隔

# 任务交付目标:
# channel + to 字段决定结果去哪里（signal, whatsapp, telegram）
# sessionTarget: "isolated" = 每次运行时使用新上下文（没有之前运行的记忆）

# 要添加任务，代理通过工具创建它们，或直接编辑 jobs.json：
# 查看现有任务作为模板在 ~/.openclaw/cron/jobs.json 中
```

---

## 许可证

MIT
