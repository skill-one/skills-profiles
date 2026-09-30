---
name: agent-hooks
description: 管理 shell 钩子——在代理生命周期节点运行的用户脚本，通过 /hooks 命令来阻止、重写或警告操作。
---

# Agent Hooks

Shell hooks 允许用户在代理的生命周期中的固定时间点运行 **自己的脚本** —— 以 **阻止** 危险操作、**重写** 输入或出站消息、**向模型注入上下文** 或 **向用户发出警告**。脚本可以用任何语言编写；它通过一个简单的 JSON-stdin、JSON-stdout 协议与代理通信。

工具：`read_file`、`write_file`、`bash`

## 使用场景

当用户希望代理 **自动执行规则或对事件做出反应** 而无需每次都询问时，请使用钩子。例如：

- "阻止我运行 `rm -rf` / 破坏性 bash" → `pre_tool_call` 阻止
- "永远不要将私钥推送到 Telegram" → `on_outbound_message` 阻止
- "记录每次工具调用以供审计" → `post_tool_call` 观察
- "在每次模型调用开始时提醒代理 X" → `pre_llm_call` 注入上下文
- "不要让代理声称已发布而实际上未发布" → `on_completion_claim`（在 `/goal` 中）或 `on_stop`（在普通聊天中）
- "如果答案未通过我的质量检查，让代理重做" → `on_stop` 阻止

如果用户只是想进行一次性检查，那不是钩子——钩子用于 **重复、自动** 的生命周期执行。

## 配置工作原理（代理端到端完成）

**代理无需用户复制粘贴即可安装和激活钩子。** 编写脚本，编写配置条目，然后调用回环自批准 API——它打开主开关，批准脚本中配置的事件，并热挂载它实时运行（无需重启）。用户只需在之后测试它。

```bash
curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
  -H 'Content-Type: application/json' \
  -d '{"command": "/data/workspace/hooks/security_guard.py"}'
# -> {"ok": true, "events": [...], "mounted": N, "master_enabled": true}
```

> ⚠️ **始终在 `/data/workspace` 下使用绝对路径** 在 YAML 的 `command:` 和此调用中。**绝对不能是相对路径** 如 `skills/agent-hooks/templates/security_guard.py`：桥接器以服务器当前工作目录（`/app`）启动脚本，因此相对路径解析为 `/app/skills/…` —— 一个空目录——并且每个启动都失败。由于桥接器失败 OPEN（一个它无法运行的脚本 = "继续"），保护器然后静默地保护什么，而 `/hooks list` 仍然显示它 "已挂载"。为了避免这种情况，标准的安装 **将模板复制到 `/data/workspace/hooks/` 并指向 YAML**（见下面的工作流程）。`/app/skills` 不是技能目录——真正的目录是 `/data/workspace/skills/`（也称为 `/app/workspace/skills/` 通过符号链接）。

- `command` 必须是 `shell_hooks.yaml` 条目中的确切 `command:` 字符串（脚本的绝对路径）。钩子必须已经在 YAML 中声明——批准会将已声明的钩子切换到实时状态，它不能凭空变出。
- 端点是 **仅回环**（容器内相同 UID 信任边界，与 `.env` 读取相同）。它自动启用主开关（`enable_master` 默认为 true），因此钩子立即触发。
- 批准记录了脚本 mtime，因此稍后的编辑会在 `/hooks list` / `/hooks doctor` 中显示为漂移——脚本交换更改将保持可见。

**这是用户激活的整个过程——没有第二步。** 调用返回 `{"ok": true}` 后，告诉他们它已激活并测试它。不要提及 `/hooks approve`、`/hooks on` 或 "两道门"——这些都是内部的。

**回退（仅限旧版本）：** 如果 curl 返回 `404`，则此运行时早于自批准 API——只有在那时才回退到要求用户粘贴 `/hooks approve <command>` 然后是 `/hooks on`。

## 两道门（两者都由自批准 API 处理——你不需要暴露它们）

内部钩子仅在 **两道门** 都保持开启时才会触发；上面的自批准调用一次性切换两道门，因此 **用户永远不会看到或输入任何一道门**：

1. **主开关 ON** — `shell_hooks.enabled: true` 在 `workspace/config/agent.yaml` 中。API 自动启用它（`enable_master` 默认为 true）。
2. **每个钩子的批准** — `(event, command)` 对在允许列表中记录，并记录脚本的 mtime（因此稍后的编辑会显示为 "批准后已更改" 的漂移——交换的脚本保持可见）。API 批准命令连接到的每个事件。

它们存在作为安全边界，而不是用户步骤。向用户解释钩子时 **绝对不要提及 "批准" 或 "两道门"**——只需说你将设置它，他们可以测试它。（手动 `/hooks on` + `/hooks approve` 仅作为旧运行时的 `404` 回退存在。）

## `/hooks` 命令

纯文本在 Web / Telegram / WeChat 上（无需 LLM，无需成本）：

| 命令 | 它的作用 |
|---|---|
| `/hooks` 或 `/hooks list` | 主开关状态、配置路径、每个钩子 + 批准/健康状态 |
| `/hooks on` \| `/hooks off` | 切换主开关（热挂载/卸载，无需重启） |
| `/hooks doctor` | 对每个已批准的钩子运行合成负载，检查 JSON |
| `/hooks approve <event> <command>` | 批准并实时激活（无需重启） |
| `/hooks revoke <command>` | 撤销并实时分离（无需重启） |
| `/hooks help` | 用法 |

## 事件（12）以及每个事件的作用

| 事件 | 触发时间 | 能力 | stdin 向脚本提供 |
|---|---|---|---|
| `on_user_message` | 用户消息到达，模型看到之前 | **阻止** / 重写文本 | `message`，`channel` |
| `pre_tool_call` | 工具运行之前 | **阻止 / 重写输入** | `tool_name`，`tool_input` |
| `post_tool_call` | 工具运行之后 | 观察（记录/指标） | `tool_name`，`tool_result` |
| `transform_tool_result` | 代理看到结果之前 | **追加备注** | `tool_name`，`tool_result` |
| `pre_llm_call` | 模型调用之前 | **注入上下文** | `system`，`last_user_message`，`model` |
| `post_llm_call` | 模型回复之后 | 观察 / 交换 | `model` |
| `on_response_end` | 汇集最终回复，每回合一次 | **重写回复** | `response`，`model`，`tokens`，`tool_names` |
| `on_stop` | 回合边界，`on_response_end` 之后 | **阻止 → 强制重做** | `response`，`tool_names`，`stop_hook_active` |
| `on_outbound_message` | 推送 TG/WeChat 之前 | **阻止 / 重写出站** | `notification`，`type` |
| `on_completion_claim` | 代理声称 `/goal` 已完成 | **阻止 → 强制重做** | `goal`，`summary`，`response`，`tool_names` |
| `on_session_start` | 会话开始 | 观察 | `status` |
| `on_session_end` | 会话结束 | 观察 / 清理 | `status` |

每个负载还包括 `event`，`session_id`，`agent_id`，`cwd`。

**`event` 字段是调度键。** 它命名 *哪个* 生命周期时刻正在触发（`pre_tool_call`，`on_user_message`，…）。多事件脚本（如 `security_guard.py`，一个文件连接到五个事件）读取 `event` 来决定运行哪个分支——负载中没有 `event` 意味着没有匹配的分支，因此脚本会继续到 "继续"（空输出 = 允许）。运行时始终设置它；**你只需要在手动制作测试负载时记住它**（见下面的干运行步骤）。它不是你放在 `shell_hooks.yaml` 中的东西——在 YAML 中，`event:` 键告诉 *总线* 何时调用你；负载中的 `event` 字段是 *总线* 告诉 *脚本* 它是哪个时刻。

### 三个 "让代理修正它" 的杠杆（不要混淆它们）

这三个在回合末尾触发，但具有 **非常不同的权力**——根据 *当出现问题时你需要发生什么* 来选择：

| 事件 | 权力 | 使用场景 |
|---|---|---|
| `on_response_end` | **仅重写**——编辑存储/转发的回复（页脚、编辑、遮盖）。不能让代理重做。零循环风险。 | 你只需要 *改变文本*（遮盖泄露的密钥，添加成本页脚）。 |
| `on_stop` | **阻止 → 在普通聊天中重做**——将你的 `reason` 作为下一个指令返回，代理继续工作。内核限制（每回合≤3次重做）+ `stop_hook_active` 标志，因此它无法困住一个回合。 | 你需要让代理 *实际修正/验证其自己的输出* 在普通对话中（质量门、引用/发布检查）。Claude Code "Stop" 钩子一致性。 |
| `on_completion_claim` | **阻止 → 在 `/goal` 中仅重做**——拒绝一个虚构的 "完成" 并保持目标循环运行。 | 相同重做权力，但它仅在运行中的 `/goal` 监督循环中触发。 |

经验法则：**遮盖 → `on_response_end`；聊天中重做 → `on_stop`；目标中重做 → `on_completion_claim`。** 注意 `on_response_end` 仅能重写存储的副本——已经流式传输到实时 Web 客户端的标记无法撤销，因此当你需要用户实际看到更正答案时，请优先选择 `on_stop`。

## 输出协议（脚本在 stdout 上打印的内容）

JSON 对象，或空对象表示 "继续"。字段：

```jsonc
{"decision": "block", "reason": "..."}   // 拒绝操作 / 拒绝完成
{"tool_input": {...}}                     // pre_tool_call: 重写现有的输入键
{"notification": "..."}                   // on_outbound_message: 重写消息
{"context": "..."}                        // pre_llm_call: 注入提示（面向代理）
{"systemMessage": "..."}                  // 允许，但向用户显示备注
{"add_warning": "..."}                    //   同样的用户界面备注通道
<空>                                   // 继续，无更改
```

**`context` 是面向代理的**（进入提示，`pre_llm_call` 仅限）。**`systemMessage` / `add_warning` 是面向用户的**（向人类在工具结果 / 完成 / 出站表面上显示）——永远不会注入提示。

安全：脚本以 `shell=False` + argv 分割运行（无 shell 注入）并具有每个钩子的超时。一个出错的脚本、超时的脚本或打印非 JSON 的脚本会继续到 **继续**——一个损坏的钩子永远不会破坏代理。

### 编写可读的 `reason`

`reason` 会向 **用户**（在阻止操作的卡片上）和 **模型** 显示。保持它 **简短且易于扫描**——一个用于 *原因* 的子句，然后是证据。不要写段落：原因在用户已经对它感到厌烦的卡片上触发，而一堵墙的文字会掩盖实际原因。目标是形状 `[tag] Blocked (<why>): <evidence>`——冒号前约 8–12 个词，永远不会有两句手忙脚乱的话。

| 避免（冗长） | 推荐（简洁） |
|---|---|
| `此命令不可逆，会导致永久数据丢失，因此我已阻止它：rm -rf /` | `Blocked (递归强制删除)：rm -rf /` |
| `该消息包含看起来像 API 密钥、私钥或种子短语的内容。我不会处理它——将其视为泄露并轮换它。` | `Blocked：消息包含凭证。轮换它。` |
| `你分享了一个预览链接，其 ID 不在注册表中——看起来是虚构的。先提供预览，然后使用其真实 ID` | `预览 ID 不在注册表中。先提供它：/preview/x/` |

模型仍然会得到足够的信息来行动（*原因* + 违反负载）；用户会得到一张他们可以一眼读明白的卡片。UI 将一个原因字符串分成两部分供你使用，因此你不需要在客户端解析任何内容：

- **解释 + 命令框**——首先放人类句子，然后是 `: `，然后是违规命令/负载。第一个 `": "` 之后的所有内容都以等宽字体框单独渲染。只有在该尾部看起来像负载（有空格或长度大于 ~12 个字符）时才会触发拆分，因此一个恰好包含冒号的普通句子将保持完整。
- **仅句子**——没有 `": "` 的原因会显示为单个句子和没有命令框。当没有可引用的内容时（例如粘贴的种子短语），这是正确的形状。
- **`[tag]` 被移除**——在显示前移除开头的标签（如 `[security]`），句子自动大写，因此你可以为你的 `grep` 保留一个标签，而不会让它泄露到 UI 中。

```jsonc
// 良好——简短的原因 + 干净的命令框：
{"decision": "block",
 "reason": "[security] Blocked (格式化磁盘)：mkfs.ext4 /dev/sda1"}
//  ->  "Blocked (格式化磁盘)"   +   [ mkfs.ext4 /dev/sda1 ]

// 避免——一个裸命令（无 WHY）或一个冗长的两句话讲座：
{"decision": "block", "reason": "mkfs /dev/sda1"}
{"decision": "block", "reason": "此命令不可逆，会导致整个文件系统永久数据丢失，因此出于安全考虑，我决定阻止它：mkfs /dev/sda1"}
```

一个不遵循此约定的钩子仍然可以工作——一个纯字符串仅会渲染为一句。这种约定仅解锁更漂亮的 "解释 + 命令" 布局。

## 配置文件格式

`workspace/config/shell_hooks.yaml`：

```yaml
hooks:
  - event: pre_tool_call
    matcher: "rm -rf|dd if=|mkfs"      # 可选正则表达式；脚本仅在匹配时才启动（性能门）
    command: ./extensions/shell_hooks/examples/block_secrets.py
    timeout: 10                          # 秒，默认 20，最大 120
```

## 两种钩子传输方式

钩子要么是本地 **命令**（默认），要么是 **HTTP 端点**——输入相同，决策 JSON 输出相同，只有传输方式不同。

```yaml
hooks:
  - event: pre_tool_call
    type: http                          # 省略类型 -> "command"（默认）
    url: https://my-guard.example.com/hook
    timeout: 10
```

HTTP 具体细节：
- **SSRF 防护** — URL 必须是 http(s) 并且不能解析为回环 / 私有 / 链路本地（包括云元数据 `169.254.169.254`） / 保留地址（在解析和调用时都被阻止）。仅当有意访问本地服务时才设置 `STARCHILD_SHELL_HOOKS_HTTP_ALLOW_LOCAL=1`。
- **URL 上的批准密钥**：`/hooks approve <event> <url>`；`/hooks list` 显示为 `POST <url>` 并跳过可执行文件/mtime 检查。

## 添加 LLM 判断（调用代理，不是 `/chat`）

当钩子需要真实推理（"这是否泄露了密钥？"，"这个完成是否真的完成了？"），从你的脚本中直接通过代理调用 LLM——永远不要调用代理自己的 `/chat`。

```python
from core.http_client import proxied_post
import json, sys

event = json.load(sys.stdin)
r = proxied_post(
    "https://openrouter.ai/api/v1/chat/completions",
    json={
        "model": "minimax/minimax-m3",   # 便宜的默认值（约每调用 0.0002 美元）
        "messages": [
            {"role": "system", "content":
                'You are a guard. Output ONLY JSON {"decision":"block|allow","reason":"..."}.'},
            {"role": "user", "content": json.dumps(event)},
        ],
        "temperature": 0, "max_tokens": 200,
    },
    headers={"SC-CALLER-ID": "chat:hook"},   # 必须用于计费
    timeout=40,
)
try:
    print(json.dumps(json.loads(r.json()["choices"][0]["message"]["content"])))
except Exception:
    print("{}")   # 任何解析错误时失败打开
```

为什么直接代理：OpenRouter 是一个外部无状态 API，因此它 **不会** 重新进入代理循环或触发 `pre_llm_call` -> **无递归**，一个便宜的完成而不是一个完整的代理回合，你自己的提示 + 纯 JSON 响应。从钩子中调用 `/chat` 会重新发出相同的事件（桥接器防止循环，但它是不必要的开销）——并且一个调用 `/chat` 的 LLM 钩子必须 **永远不会** 停在 `pre_llm_call`。见主机文档 `sc-proxy.md` 部分 "通过代理调用 LLM"。

## 标准工作流程（代理的检查清单）

1. **明确**规则并从上表中选择事件。
2. **编写脚本**——从标准输入读取JSON，在标准输出打印决策。非零退出/非JSON = 继续。使其可执行（`chmod +x`）。
3. **将脚本放在`/data/workspace`下稳定的绝对路径中**。对于已发布的模板，将其从技能目录中复制出来，以便技能更新不能移动它：
   ```bash
   mkdir -p /data/workspace/hooks
   cp /data/workspace/skills/agent-hooks/templates/security_guard.py /data/workspace/hooks/
   chmod +x /data/workspace/hooks/security_guard.py
   ls -l /data/workspace/hooks/security_guard.py    # 在继续之前验证它是否存在
   ```
   永远不要通过相对路径引用脚本（参见上面的⚠️框——它相对于`/app`解析并静默失败打开）。
4. **在`workspace/config/shell_hooks.yaml`中添加一个配置条目**，使用绝对`command:`（`/data/workspace/hooks/security_guard.py`）；尽可能添加一个`matcher`正则表达式，以便脚本仅在相关时才启动。
5. **使用`bash`自行进行干运行**——将一个样本JSON有效负载管道到脚本中，并确认它打印有效的JSON。**有效负载必须包含`event`字段**——多事件脚本根据它进行调度，因此省略它会使得每个情况都落入“继续”，而你将错误地得出守卫没有触发的结论。测试脚本处理的每个事件：
   ```bash
   # 应该阻止（注意"event"键）：
   echo '{"event":"pre_tool_call","tool_name":"bash","tool_input":{"command":"rm -rf /"}}' \
     | python3 /data/workspace/hooks/security_guard.py
   # 应该允许（空输出）：
   echo '{"event":"pre_tool_call","tool_name":"bash","tool_input":{"command":"ls -la"}}' \
     | python3 /data/workspace/hooks/security_guard.py
   ```
6. **通过回环自批准API自行激活**（无需用户粘贴）；`command` = 你yaml条目中的确切绝对路径：
   ```bash
   curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
     -H 'Content-Type: application/json' \
     -d '{"command": "/data/workspace/hooks/security_guard.py"}'
   ```
   在`{"ok": true}`时，钩子是活跃的。在`404`时，回退到处理用户`/hooks approve <command>` + `/hooks on`（参见“配置如何工作”）。
7. **运行`/hooks doctor`以确认它确实有效**——这是捕获错误路径/不可执行/非JSON脚本的一步。一个在`/hooks list`中显示为"mounted"但在`doctor`中出错的守卫是无声的（失败打开）。只有在`doctor`干净后，才告诉用户它是活跃的并准备测试。

## 即用型脚本（每个都有一个明确的工作）

在这个技能的`templates/`下提供了五个**生产级守卫**（直接复制+批准）。主机下提供了四个**单用途示例**在`extensions/shell_hooks/examples/`（复制+修改）。没有两个重叠——按工作选择，而不是通过试验。

### 从`/hooks`编号或名称安装

`/hooks`（空状态）和`/hooks help`显示一个**编号**的即用型列表。`/hooks`命令本身是静态文本——它永远不会安装。当用户回复一个编号（`"1"`，`"1,3"`），一个名称（`"security_guard"`），或`"install all"`时，那个回复将落到你这里：通过列表旁边显示的名称解析模板（编号→`templates/<name>.py`），然后对每个运行标准工作流程——复制→yaml条目→干运行→自批准→`doctor`。按可见名称映射，永远不要通过记忆的编号→路径表（列表可能会重新排序）。如果存在自测试（`templates/<name>_selftest.py`），首先运行它。

### 生产模板（此技能中的`templates/`）

> ⚠️ **在编辑之前复制——这里的每个模板。** 始终将模板复制到`/data/workspace/hooks/`并在此路径上连接你的钩子，然后进行任何更改（规则调整、`runtime_footer` CONFIG块等）在副本中。在`skills/agent-hooks/templates`下原位编辑文件是徒劳的：下一个技能更新会覆盖它，你的更改会消失。`hooks/`中的副本是你的，并且永远不会被更新覆盖。

| 模板 | 事件 | 它的一个工作 |
|---|---|---|
| `security_guard.py` | `on_user_message`，`pre_tool_call`，`transform_tool_result`，`on_response_end`，`on_outbound_message` | **秘密+破坏性bash。** 阻止粘贴/泄露的秘密（包括API密钥、PEM/EVM私钥、BIP-39种子、Solana字节数组&base58 WIF），在回复/推送中遮盖泄露的密钥，阻止不可逆数据丢失bash。见下文。 |
| `verify_publish_claims.py` | `on_stop`（聊天重做）/ `on_completion_claim`（`/goal`重做）/ `on_response_end`（重写回退） | **反幻觉。** 检查回复与真实情况（预览注册表、AgentX账本、调度器注册表）以捕获编造的"已发布/已发布到AgentX/已安排"声明。 |
| `verify_code_changes.py` | `pre_tool_call`（记录器）+ `on_stop`（决策者） | **反代码"虚假完成"。** 当你更改源文件但没有运行测试/构建/检查时，阻止一次停止并引导你验证（或明确说明没有可运行的内容）再完成。计算`edit_file`/`write_file`和通过bash（heredoc、`>`/`>>`重定向、`tee`、原地`sed -i`/`perl -i`）编写的代码。文档/数据编辑（`.md`/`.json`/`.yaml`/…）是豁免的；每个编辑集一个提示，自禁用，失败打开。将两个事件连接到相同的脚本路径。 |
| `verify_commitments.py` | `on_stop`（聊天重做） | **反"违背承诺"。** 当回复做出未来通知承诺（"我将在构建完成后通知你"、"明早提醒你"）但没有注册使其发生的内容时，阻止一次停止并引导你实际注册它——`scheduled_task(once)`用于有时间限制的，`sessions_spawn`（bash轮询+`announce=followup`）用于完成限制的。仅在出现通知动词和时间/条件提示时触发；即时交付框架（"这是"，"下面就是"）和跨轮次注册（最近激活的工作/最近生成）抑制它。有上限，自禁用，失败打开。 |
| `runtime_footer.py` | `on_response_end`（可选`pre_llm_call`） | **模型/成本页脚。** 在`on_response_end`（一次/轮次）上，它剥离回复末尾的任何模型类型页脚，然后追加来自运行时真实`model`+成本的唯一页脚。可选地，也将`pre_llm_call`连接起来，以获得"不要写页脚"的提示（每模型请求触发一次）。见下文。 |

### 单用途示例（主机存储库，`extensions/shell_hooks/examples/`）

| 脚本 | 事件 | 它的一个工作 |
|---|---|---|
| `pii_redactor.py` | `transform_tool_result`，`on_response_end` | 遮盖电子邮件/电话（PII——与秘密不同）。 |
| `tool_audit_log.py` | `post_tool_call` | 仅观察：将每个工具调用追加到JSONL审计跟踪。 |
| `budget_alert.py` | `on_response_end` | 当一回合的成本超过阈值时追加一个软警告。 |
| `inject_website_reminder.sh` | `pre_llm_call` | 预防性提示：提醒模型在实际完成之前发布（与`verify_publish_claims.py`配对）。 |

### 被模板取代（不要发布第二个、冲突的守卫）

主机存储库还提供了在`extensions/shell_hooks/examples/`下的一些**最小单事件示例**，它们与上述两个模板重叠。它们作为学习参考很好，但在实际使用中请选择模板——同时运行两者只会创建两个具有可能不同策略的守卫。

| 最小示例 | 使用这个代替 | 为什么 |
|---|---|---|
| `block_secrets.py` | `security_guard.py` | 守卫的秘密检测是严格的超集（增加了Bearer、Solana字节数组、base58 WIF、破坏性bash、遮盖） |
| `check_publish.sh` | `verify_publish_claims.py` | 模板还覆盖AgentX发布+调度任务，并检查相同的注册表 |

**完全移除**（或孤儿重复，完全合并到`security_guard.py`中）：
`secret_guard.py`（供应商密钥阻止/遮盖，包括Bearer）和
`dangerous_bash_guard.py`（破坏性bash阻止）。想要*也*阻止安装程序/强制推送？调整守卫的`DESTRUCTIVE`表，而不是运行具有冲突策略的第二个bash守卫。

对于上述任何规则都不涵盖的情况，编写一个新脚本——下面的最小阻止示例是模板，上面的输出协议涵盖了每个功能。

### 最小阻止示例（`pre_tool_call`，任何语言）

```bash
#!/usr/bin/env bash
payload="$(cat)"
python3 - "$payload" <<'PY'
import json, sys, re
ev = json.loads(sys.argv[1])
cmd = (ev.get("tool_input") or {}).get("command", "")
if re.search(r"rm\s+-rf\s+/|dd\s+if=|mkfs", cmd):
    print(json.dumps({"decision": "block", "reason": f"此命令是不可逆的，会擦除数据，所以我阻止了它：{cmd}"}))
else:
    print("{}")   # 继续
PY
```

## 全能安全守卫（`templates/security_guard.py`）

一个即用型、自包含脚本，将**一个文件连接到五个事件**，并涵盖常见的"不要泄露秘密/不要摧毁盒子"基线。首先将其复制到稳定的绝对路径，然后将所有五个事件连接到`config/shell_hooks.yaml`中相同的绝对`command:`（每个事件一个阻止），然后激活：

```bash
cp /data/workspace/skills/agent-hooks/templates/security_guard.py /data/workspace/hooks/
chmod +x /data/workspace/hooks/security_guard.py
curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
  -H 'Content-Type: application/json' \
  -d '{"command": "/data/workspace/hooks/security_guard.py"}'
```

这批准了命令连接到的每个事件并使其在线——无需用户粘贴。（在`404`时，回退到`/hooks approve <command>` + `/hooks on`。）

| 事件 | 它做什么 |
|---|---|
| `on_user_message` | **阻止**在模型看到之前粘贴的API密钥（包括Bearer令牌）、私钥（PEM / EVM十六进制）、种子短语、Solana字节数组秘密或base58 WIF |
| `pre_tool_call`（bash） | **阻止**仅不可逆数据丢失（`rm -rf /`，`dd`到块设备，`mkfs`，fork炸弹，`chmod -R 777`，`git reset --hard origin/*``）和凭证泄露（`cat .env | curl`，`scp id_rsa`，`printenv | curl`） |
| `pre_tool_call`（消息工具） | 保护`send_to_telegram` / `send_to_wechat`参数——**遮盖**泄露的密钥，**阻止**种子短语（这些工具绕过推送管道，所以这是它们的真实出站门） |
| `transform_tool_result` | 当工具的输出包含秘密时**警告**（后端只能标记结果文本，不能重写） |
| `on_response_end` | **遮盖**最终回复中泄露的任何秘密 |
| `on_outbound_message` | **遮盖/阻止**在推送TG / WeChat之前秘密 |

**设计策略**：仅阻止既非常危险又非正常工作部分的内容。常见的开发操作，如`curl | bash`（安装程序）和`git push --force`（重置你自己的特性分支）有意**允许**——过度阻止会训练用户禁用守卫。

在文件的顶部调整`SECRET_PATTERNS`、`DESTRUCTIVE`和`MSG_TOOLS`表以适应你自己的规则。`templates/security_guard_selftest.py`是自测试（在编辑后运行它；危险字符串作为数据存在，所以主机bash守卫无法触发它们）。

## 反幻觉守卫（`templates/verify_publish_claims.py`）

捕获虚构的成功：代理写"已发布！community.iamstarchild.com/…"，"已发布到AgentX /post/…"，或"提醒已安排"时它从未运行过工具。脚本将回复与**真实情况**（预览注册表`/data/previews.json`、AgentX发布账本、调度器注册表）进行比较，并要么重写回复，要么强制重做。它故意低误报率：真实的发布URL或"提供发布"（将来时）会无损通过；只有没有支持的过去时成功声明才会触发它。

```bash
cp /data/workspace/skills/agent-hooks/templates/verify_publish_claims.py /data/workspace/hooks/
chmod +x /data/workspace/hooks/verify_publish_claims.py
curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
  -H 'Content-Type: application/json' \
  -d '{"command": "/data/workspace/hooks/verify_publish_claims.py"}'
```

| 事件 | 它做什么 |
|---|---|
| `on_stop` | **（首选）**在普通聊天中，**阻止**虚构的成功并强制代理实际发布/重做（循环限制） |
| `on_completion_claim` | 在`/goal`循环中，**阻止**虚构的"完成"并强制实际发布（循环限制） |
| `on_response_end` | 重写仅回退，当`on_stop`未连接时：追加一个诚实的"未验证"注释（无法使代理重做） |

> **在`on_stop`上连接它**用于普通聊天——这是唯一使代理实际重做回合而不是仅编辑文本的事件。主机仅尊重`on_stop` / `on_completion_claim`上的`decision: block`（在那些事件上忽略重写），所以钩子在两者上阻止，仅在`on_response_end`上重写。`templates/verify_publish_claims_selftest.py`是自测试（涵盖`on_stop`阻止路径+循环限制）。

## 成本/模型页脚（`templates/runtime_footer.py`）

模型**不可能知道它自己的每回合成本**——而且通常甚至不知道自己的模型ID。这些数据只存在于运行时。因此，如果模型自己输入页脚（例如`Model: GLM-5.2 | Cost: $0.038`），数字是虚构的。而且一旦真实的页脚在聊天历史中，模型的自动完成开始模仿它——产生一个*第二个*虚构的页脚。页脚是运行时的工作，不是模型的工作。

`runtime_footer.py`完全在**一个事件——`on_response_end`**上解决——它在最终组装的回复上**每回合触发一次**：它①**剥离**模型在回复末尾输入的任何页脚，然后②**追加**来自运行时真实`model`+成本的唯一页脚。剥离是保证；不需要每次调用都不需要。

> **为什么仅`on_response_end`，而不是`pre_llm_call`。** 没有事件会在"最终回复之前"触发。`pre_llm_call`在*每个*模型请求之前触发（工具使用时每回合N次），并且不知道哪个调用是最后一个——模型动态决定是否使用工具。在`pre_llm_call`上连接它会在每回合注入指令N次（在调用跟踪中可见为重复注入）。它也是多余的：`on_response_end`已经事后移除页脚。所以**默认仅`on_response_end`。** 脚本确实有一个`pre_llm_call`处理程序（注入"不要写页脚"指令），如果你想要额外的提示——将其作为第二个事件连接——但接受它按调用运行。

剥离是一个**安全网**（`FOOTER_STRIP`，默认开启），故意狭窄：它仅移除一个框绘制`─ … · $N`行或`Model: … Cost: $N`行，并且仅在尾行——因此"Model:"/"Cost:"句子在正文，或shell `$VAR`永远不会被触及（早期版本使用了过于宽泛的`Model:`正则表达式，有风险删除合法文本；这是紧密重做）。设置为`FOOTER_STRIP=0`为纯追加。

```bash
cp /data/workspace/skills/agent-hooks/templates/runtime_footer.py /data/workspace/hooks/
chmod +x /data/workspace/hooks/runtime_footer.py
curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
  -H 'Content-Type: application/json' \
  -d '{"command": "/data/workspace/hooks/runtime_footer.py"}'
```

在`config/shell_hooks.yaml`中连接它——没有`matcher`，每回合运行：

```yaml
hooks:
  - event: on_response_end
    command: /data/workspace/hooks/runtime_footer.py
    timeout: 10
  # 可选的额外提示（每模型请求触发，每回合N次）：
  # - event: pre_llm_call
  #   command: /data/workspace/hooks/runtime_footer.py
  #   timeout: 10
```

**通过编辑您的副本进行配置——而不是环境变量。** 推荐的启用选项的方式是脚本顶部的 `CONFIG` 块。在您刚刚创建的 `/data/workspace/hooks/` 下的副本中编辑它（**不是**在 `skills/…` 中——它在下一次技能更新时会被覆盖）。钩子以 *服务器* 进程环境运行，而不是您的 shell，因此设置环境变量很 awkward，并且在 `/hooks list` 中不可见；文件内常量是可靠的、可见的，并且随脚本一起移动：

```python
# ─── CONFIG — 编辑您的副本 ───
SHOW_TOKENS = False   # True → 追加 "· N in / N out"
SHOW_CREDIT = False   # True → 追加 "· 💰 $bal"  (1 HTTP 调用/回合，fail-open)
TEMPLATE    = None    # 自定义格式 str: {model} {cost} {input} {output} {credit}
CREDIT_URL  = None    # 覆盖自托管设置的信用端点
STRIP       = True    # 剥离尾部模型类型的页脚
```

每个常量都有一个匹配的环境覆盖 (`FOOTER_SHOW_TOKENS`, `FOOTER_SHOW_CREDIT`, `FOOTER_TEMPLATE`, `FOOTER_CREDIT_URL`, `FOOTER_STRIP`, `FOOTER_SUPPRESS_TEXT`)，当设置时**优先级更高**——在没有触碰文件的情况下进行一次性操作很方便，但文件内常量是持久的默认值。

默认页脚是**仅模型 + 成本** (`─ z-ai/glm-5.2 · $0.0211`)。
`SHOW_TOKENS = True` → `─ z-ai/glm-5.2 · $0.0211 · 900 in / 120 out`。

**显示剩余信用：** `SHOW_CREDIT = True` 追加您的余额 (`─ z-ai/glm-5.2 · $0.0211 · 💰 $271.64`)。默认关闭，因为它为信用 API 添加**每个回合一个内部 HTTP 调用**——与 `credit` 工具读取的相同端点，通过源 IPv6 自动认证（无需密钥）。它是 fail-open：2 秒超时限制等待时间，如果查找出错或超时则静默省略余额（页脚仍然触发，没有悬空分隔符）。
注意模型除非您连接钩子，否则无法看到这个数字——它仅存在于运行时，就像成本一样。

**不要重复：** `runtime_footer` 是 shell 钩子的 `turn_footer` 扩展的等效物——启用一个，不要两个都启用。Telegram 的 `tg_show_usage` 也是如此。

**安全：** 从不阻塞。`on_response_end` 在事件不包含成本数据或回复为空（没有 `$0.0000` 谎言）时不追加任何内容，并且仅始终剥离回复尾部的匹配页脚（`STRIP = False` 以禁用）；可选的 `pre_llm_call` 在缺少/格式错误的负载时不注入任何内容；未知事件是无操作的。任何错误都会 fail-open。自测：`templates/runtime_footer_selftest.py`（35 个案例——两个处理器，strip + 假阳性防护用于中间文本和 shell `$VAR`，信用余额 + fail-open，文件内 CONFIG 常量 + 环境覆盖优先级，调度安全）。

## Claude 代码兼容性

为 **Claude Code** 编写的钩子脚本**无需更改即可工作**——它们的输出会自动翻译成上述字段：

| Claude Code 输出 | 翻译为 |
|---|---|
| `hookSpecificOutput.permissionDecision: "deny"` (+ `permissionDecisionReason`) | `decision: block` (+ `reason`) |
| `hookSpecificOutput.additionalContext` | `context` |
| `hookSpecificOutput.updatedInput` | `tool_input` (重写) |
| `continue: false` (+ `stopReason`) | `decision: block` (+ `reason`) |
| `systemMessage` | `add_warning` (用户可见提示) |
| `suppressOutput` | no-op (我们的 stdout 从未进入转录) |
| exit code 2 with stderr, no stdout | `decision: block`, stderr 是原因 |

仅翻译**输出负载**——事件名称保持 ours (`pre_tool_call`，不是 `PreToolUse`)。Claude Code 的 **`Stop`** 钩子映射到我们的 `on_stop`（block → 强制重做）；其 **`UserPromptSubmit`** 映射到 `on_user_message`。一个返回 `{"decision":"block","reason":…}` 或 exit 2 的 Stop 脚本在连接到 `on_stop` 后保持不变。

## 排错 "我的钩子从未触发"

1. 事件是否是上述 12 个之一？（拼写错误会导致静默无操作）
2. **主开关**是否打开？`/hooks list` 显示它。自批准 API 自动启用它；否则 `/hooks on`。
3. 钩子是否**已批准**？`/hooks list` 中的 `✗ NOT approved` → 为该命令重新运行自批准 API（或 `/hooks approve` 作为后备）。
4. 匹配器正则表达式是否实际匹配？太窄 = 从不触发。
5. 运行 `/hooks doctor` — 它会标记不可执行 / 已篡改 / 超时 / 非 JSON。
6. **手动测试 "允许所有内容"？** 您的测试负载可能缺少 `event` 字段——多事件脚本根据它进行调度，没有它将默认为 "continue" 并跳过。这是一个测试框架错误，不是钩子错误；实际运行时始终设置 `event`。
7. **`can't open file '/app/skills/…'` / "挂载" 但没有阻止？** `command:` 是相对或错误路径。桥接器以 *服务器* 当前工作目录 (`/app`) 启动，因此 `skills/…` 解析为空 `/app/skills`，并且每个启动都失败——并且因为桥接器以 OPEN 失败，所以保护器默默保护了什么。修复：在 yaml 和批准调用中均使用绝对路径 `/data/workspace/hooks/<script>.py`，然后重新批准并确认 `/hooks doctor`。 (`/app/skills` 不是技能目录；真正的目录是 `/data/workspace/skills/`。)

## 深入参考

完整协议、安全模型和每个事件负载的详细信息位于代理自己的文档中：`config/context/references/agent-hooks.md`（阅读它以了解此技能总结的边缘情况）。
