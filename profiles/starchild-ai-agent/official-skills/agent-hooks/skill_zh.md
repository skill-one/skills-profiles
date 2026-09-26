# Agent Hooks

Shell hooks 允许用户在代理的生命周期中的固定点运行 **自己的脚本**，以 **阻止** 危险操作、**重写** 输入或出站消息、**向模型注入上下文** 或 **提醒用户**。脚本可以用任何语言编写；它通过一个简单的 JSON 在标准输入上、JSON 在标准输出上的协议与代理进行通信。

工具：`read_file`，`write_file`，`bash`

## 使用场景

当用户希望代理 **自动执行规则或对事件做出反应** 而无需每次都询问时，请使用钩子。示例：

- "阻止我运行 `rm -rf` / 破坏性 bash" → `pre_tool_call` 阻止
- "永远不要将私钥推送到 Telegram" → `on_outbound_message` 阻止
- "记录每个工具调用以供审计" → `post_tool_call` 观察
- "在每次模型调用开始时提醒代理 X" → `pre_llm_call` 上下文
- "不要让代理声称它发布时实际上没有" → `on_completion_claim`（在 `/goal` 中）或 `on_stop`（在正常聊天中）
- "如果答案未通过我的质量检查，让代理重做" → `on_stop` 阻止

如果用户只是想要一次性检查，那不是钩子——钩子是用于 **重复、自动** 生命周期执行的。

## 配置工作原理（代理端到端处理）

**代理安装和激活钩子，无需用户复制粘贴。** 编写脚本，编写配置条目，然后调用回环自批准 API——它打开主开关，批准脚本针对它连接的每个事件，并热挂载它实时（无需重启）。用户只需在之后测试它。

```bash
curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
  -H 'Content-Type: application/json' \
  -d '{"command": "/data/workspace/hooks/security_guard.py"}'
# -> {"ok": true, "events": [...], "mounted": N, "master_enabled": true}
```

> ⚠️ **始终在 `/data/workspace` 下使用绝对路径** 在 yaml `command:` 和此调用中。**绝对不是相对路径**，如 `skills/agent-hooks/templates/security_guard.py`：桥接程序以 *服务器* 当前工作目录（`/app`）启动脚本，所以相对路径解析为 `/app/skills/…` — 一个空目录 — 并且每个启动都失败。因为桥接程序失败 OPEN（它无法运行的脚本 = "继续"），所以保护器在 `/hooks list` 仍然显示它 "挂载" 的情况下静默地保护什么。为了避免这种情况，标准安装 **将模板复制到 `/data/workspace/hooks/` 并指向 yaml**（见下文的工作流程）。`/app/skills` 不是技能目录——真正的目录是 `/data/workspace/skills/`（通过符号链接称为 `/app/workspace/skills/`）。

- `command` 必须是 `shell_hooks.yaml` 条目中的确切 `command:` 字符串（绝对脚本路径）。钩子必须在 yaml 中声明——批准将声明的钩子切换为实时，它不能凭空变出。
- 端点是 **仅回环**（相同 UID 在容器中的信任边界，与 `.env` 读取相同）。它自动启用主开关（`enable_master` 默认为 true），因此钩子立即触发。
- 批准记录了脚本 mtime，因此后续编辑在 `/hooks list` / `/hooks doctor` 中显示为漂移——脚本交换更改保持可见。

**这是用户激活的整个过程——没有第二步。** 调用返回 `{"ok": true}` 后，告诉他们它已激活并准备测试。不要提及 `/hooks approve`，`/hooks on` 或 "两道门"——这些都是内部的。

**回退（仅限旧版本）：** 如果 curl 返回 `404`，则此运行时早于自批准 API——只有在那时才回退到要求用户粘贴 `/hooks approve <command>` 然后是 `/hooks on`。

## 两道门（两者都由自批准 API 处理——你不需要显示它们）

内部钩子仅在 **两者都保持** 时才触发；上面的自批准调用一次性切换两者，因此 **用户永远不会看到或输入任何**：

1. **主开关 ON** — `shell_hooks.enabled: true` 在 `workspace/config/agent.yaml` 中。API 自动启用它（`enable_master` 默认为 true）。
2. **每个钩子的批准** — `(event, command)` 对在允许列表中记录，并带有脚本的 mtime（因此后续编辑显示为 "自批准以来已更改" 漂移——交换的脚本保持可见）。API 批准该命令连接到的每个事件。

它们的存在是为了安全边界，而不是用户步骤。向用户解释钩子时 **绝对不要提及 "批准" 或 "两道门"**——只需说你将设置它，他们可以测试它。（手动 `/hooks on` + `/hooks approve` 仅作为旧运行时的 `404` 回退存在。）

## `/hooks` 命令

纯文本在 Web / Telegram / WeChat 上（无 LLM，无成本）：

| 命令 | 它的作用 |
|---|---|
| `/hooks` 或 `/hooks list` | 主开关状态、配置路径、每个钩子 + 批准/健康 |
| `/hooks on` \| `/hooks off` | 切换主开关（热挂载/卸载，无需重启） |
| `/hooks doctor` | 对每个批准的钩子针对合成负载运行，检查 JSON |
| `/hooks approve <event> <command>` | 批准 + 激活实时（无需重启） |
| `/hooks revoke <command>` | 撤销 + 实时分离（无需重启） |
| `/hooks help` | 用法 |

## 事件（12）和每个事件能做什么

| 事件 | 触发 | 能力 | stdin 给脚本 |
|---|---|---|---|
| `on_user_message` | 用户消息到达，在模型看到它之前 | **阻止** / 重写文本 | `message`，`channel` |
| `pre_tool_call` | 工具运行之前 | **阻止 / 重写输入** | `tool_name`，`tool_input` |
| `post_tool_call` | 工具运行之后 | 观察（记录/指标） | `tool_name`，`tool_result` |
| `transform_tool_result` | 代理看到结果之前的结果 | **附加注释** | `tool_name`，`tool_result` |
| `pre_llm_call` | 模型调用之前 | **注入上下文** | `system`，`last_user_message`，`model` |
| `post_llm_call` | 模型回复之后 | 观察 / 交换 | `model` |
| `on_response_end` | 最终回复组装，每轮一次 | **重写回复** | `response`，`model`，`tokens`，`tool_names` |
| `on_stop` | 轮次边界，`on_response_end` 之后 | **阻止 → 强制重做** | `response`，`tool_names`，`stop_hook_active` |
| `on_outbound_message` | 在 TG/WeChat 推送之前 | **阻止 / 重写出站** | `notification`，`type` |
| `on_completion_claim` | 代理声称 `/goal` 已完成 | **阻止 → 强制重做** | `goal`，`summary`，`response`，`tool_names` |
| `on_session_start` | 会话开始 | 观察 | `status` |
| `on_session_end` | 会话结束 | 观察 / 清理 | `status` |

每个负载还包括 `event`，`session_id`，`agent_id`，`cwd`。

**`event` 字段是调度键。** 它命名 *哪个* 生命周期时刻触发（`pre_tool_call`，`on_user_message`，…）。多事件脚本（如 `security_guard.py`，一个文件连接到五个事件）读取 `event` 来决定运行哪个分支——负载中没有 `event` 意味着没有匹配的分支，所以脚本会默认跳转到 "继续"（空输出 = 允许）。运行时始终设置它；**只有在手动制作测试负载时才需要记住它**（见下文的干运行步骤）。它不是你放在 `shell_hooks.yaml` 中的内容——在 yaml 中，`event:` 键告诉 *总线* 何时调用你；负载中的 `event` 字段是总线告诉 *脚本* 它是哪个时刻。

### 三个 "让代理修复它" 的杠杆（不要混淆它们）

这三个在轮次的末尾触发，但具有 **非常不同的权力**——根据 *当出现问题时你需要发生什么* 来选择：

| 事件 | 权力 | 使用场景 |
|---|---|---|
| `on_response_end` | **仅重写** — 编辑存储/转发回复（页脚，编辑，掩码）。不能让代理重做。零循环风险。 | 你只需要 *改变文本*（掩码泄露的密钥，添加成本页脚）。 |
| `on_stop` | **阻止 → 在正常聊天中重做** — 将你的 `reason` 作为下一个指令返回，代理继续工作。内核限制（每轮 ≤3 次重做）+ `stop_hook_active` 标志，所以它不能困住轮次。 | 你需要代理 *实际上修复/验证其自己的输出* 在普通对话中（质量门，引用/发布检查）。Claude Code "Stop" 钩子一致性。 |
| `on_completion_claim` | 在 `/goal` 循环中 **阻止** "完成" 并保持目标循环运行。 | 相同重做权力，但仅在运行中的 `/goal` 监督循环中触发。 |

经验法则：**掩码 → `on_response_end`；在聊天中重做 → `on_stop`；在目标中重做 → `on_completion_claim`。** 注意 `on_response_end` 只能重写存储的副本——已经流式传输到实时 Web 客户端的标记无法撤销，因此当你需要用户实际看到更正答案时，请优先选择 `on_stop`。

## 输出协议（脚本在 stdout 上打印的内容）

JSON 对象，或空表示 "继续"。字段：

```jsonc
{"decision": "block", "reason": "..."}   // 拒绝操作 / 拒绝完成
{"tool_input": {...}}                     // pre_tool_call: 重写现有输入键
{"notification": "..."}                   // on_outbound_message: 重写消息
{"context": "..."}                        // pre_llm_call: 注入提示（代理端）
{"systemMessage": "..."}                  // 允许，但向用户显示注释
{"add_warning": "..."}                    //   相同用户面注释通道
<empty>                                   // 继续，无更改
```

**`context` 是代理端**（进入提示符，`pre_llm_call` 仅限）。**`systemMessage` / `add_warning` 是用户端**（向人类显示在工具结果 / 完成 / 出站表面上）——永远不会注入提示符。

安全：脚本以 `shell=False` + argv 分割（无 shell 注入）运行，并具有每个钩子的超时。一个脚本出错、超时或打印非 JSON，会默认跳转到 **继续**——一个损坏的钩子永远不会破坏代理。

### 编写可读的 `reason`

`reason` 显示给 **用户**（在阻止操作的卡片上）和 **模型**。保持它 **简短且易于扫描**——一个条款用于 *为什么*，然后是证据。不要写段落：`reason` 触发在用户已经对它感到烦恼的卡片上，一堵墙的文字会隐藏实际原因。目标是 `[tag] 阻止 (<为什么>): <证据>`——冒号前约 8–12 个词，永远不会有两句手忙脚乱的话。

| 避免（冗长） | 推荐（简洁） |
|---|---|
| `This command is irreversible and would cause permanent data loss, so I've blocked it: rm -rf /` | `Blocked (递归强制删除): rm -rf /` |
| `That message contains what looks like an API key, private key, or seed phrase. I won't process it — treat it as exposed and rotate it.` | `Blocked: 消息包含凭证。旋转它。` |
| `You shared a preview link whose id isn't in the registry — it looks made up. Serve the preview first and use its real id` | `预览 ID 不在注册表中。首先提供预览：/preview/x/` |

模型仍然获得足够的信息来行动（*为什么* + 违法负载）；用户获得一张他们可以一目了然的卡片。UI 将一个 reason 字符串分成两部分，所以你不需要在客户端解析任何内容：

- **解释 + 命令框** — 首先放人类句子，然后 `: `, 然后是违法的命令/负载。冒号之后的一切都渲染在一个单独的等宽框中。只有在那个尾部看起来像负载时（包含空格或长度超过 ~12 个字符）才会触发分割，所以一个普通的句子恰好包含冒号，则保持完整。
- **仅句子** — 没有冒号的 reason 显示为单个句子，没有命令框。当没有可引用的内容时（例如粘贴的种子短语）是正确的形状。
- **`[tag]` 被剥离** — 在显示之前移除一个开头的标签，如 `[security]`，句子自动大写，所以你可以为你的 `grep` 保留一个标签，而不会它泄露到 UI 中。

```jsonc
// 良好——简短的为什么 + 干净的命令框:
{"decision": "block",
 "reason": "[security] 阻止 (格式化磁盘): mkfs.ext4 /dev/sda1"}
//  ->  "Blocked (格式化磁盘)"   +   [ mkfs.ext4 /dev/sda1 ]

// 避免——一个裸命令（没有为什么）或一个冗长的两句话讲座:
{"decision": "block", "reason": "mkfs /dev/sda1"}
{"decision": "block", "reason": "This command is irreversible and would cause permanent data loss across the entire filesystem, so I have decided to block it for your safety: mkfs /dev/sda1"}
```

一个不遵循此约定的钩子仍然可以工作——一个纯文本只渲染为一句。这种约定解锁了更友好的 "解释 + 命令" 布局。

## 配置文件格式

`workspace/config/shell_hooks.yaml`:

```yaml
hooks:
  - event: pre_tool_call
    matcher: "rm -rf|dd if=|mkfs"      # 可选正则表达式；脚本仅在匹配时才启动（性能门）
    command: ./extensions/shell_hooks/examples/block_secrets.py
    timeout: 10                          # 秒，默认 20，最大 120
```

## 两种钩子传输方式

钩子要么是本地 **命令**（默认），要么是 **HTTP 端点**——输入相同，输出相同，只有传输不同。

```yaml
hooks:
  - event: pre_tool_call
    type: http                          # 省略类型 -> "command" (默认)
    url: https://my-guard.example.com/hook
    timeout: 10
```

HTTP 具体信息：

- **SSRF 守卫** — URL 必须是 http(s) 并且绝对不能解析为回环 / 私有 / 链路本地（包括云元数据 `169.254.169.254`）/ 保留地址（在解析和调用时都被阻止）。仅当有意击中本地服务时才设置 `STARCHILD_SHELL_HOOKS_HTTP_ALLOW_LOCAL=1`。

- **URL 上的批准密钥**：`/hooks approve <event> <url>`；`/hooks list` 显示为 `POST <url>` 并跳过可执行文件/mtime 检查。

## 添加 LLM 判断（调用代理，不是 /chat）

当钩子需要真实的推理时（"这个答案泄露了密钥吗？" "这个完成实际上是完成了吗？"），直接通过代理调用 LLM——永远不要代理自己的 `/chat`。

```python
from core.http_client import proxied_post
import json, sys

event = json.load(sys.stdin)
r = proxied_post(
    "https://openrouter.ai/api/v1/chat/completions",
    json={
        "model": "minimax/minimax-m3",   # 廉价的默认值 (~$0.0002/调用)
        "messages": [
            {"role": "system", "content":
                'You are a guard. Output ONLY JSON {"decision":"block|allow","reason":"..."}.'],
            {"role": "user", "content": json.dumps(event)},
        ],
        "temperature": 0, "max_tokens": 200,
    },
    headers={"SC-CALLER-ID": "chat:hook"},   # 必须用于计费
    timeout=40,
)
try:
    print(json.dumps(json.loads(r.json()["choices"][0]["message"]["content"]))
except Exception:
    print("{}")   # 任何解析错误时失败打开
```

为什么直接代理：OpenRouter 是一个外部无状态 API，所以它 **不会** 重新进入代理循环或触发 `pre_llm_call` -> **没有递归**，一个廉价的完成代替一个完整的代理轮次，你自己的提示符 + 纯 JSON 响应。从 `/chat` 调用代理会重新发出相同的事件（桥接程序防止循环，但这是不必要的开销）——并且一个调用 `/chat` 的 LLM 钩子必须 **永远不会** 停在 `pre_llm_call`。有关详细信息，请参阅主机文档 `sc-proxy.md` 部分 "通过代理调用 LLM"。

## 标准工作流程（代理的检查清单）

1. **澄清** 规则并从上表中选择事件。
2. **编写脚本** — 从 stdin 读取 JSON，在 stdout 上打印决策。
   非零退出 / 非JSON = 继续。使其可执行 (`chmod +x`)。
3. **将脚本放在一个稳定的绝对路径** 在 `/data/workspace` 下。对于要分发的模板，将它们从技能目录复制出来，以便技能更新不会移动它：
   ```bash
   mkdir -p /data/workspace/hooks
   cp /data/workspace/skills/agent-hooks/templates/security_guard.py /data/workspace/hooks/
   chmod +x /data/workspace/hooks/security_guard.py
   ls -l /data/workspace/hooks/security_guard.py    # 在继续之前验证它是否存在
   ```
   永远不要通过相对路径引用脚本（见上面的 ⚠️ 盒子——它解析为 `/app` 并静默失败打开）。
4. **在 `workspace/config/shell_hooks.yaml` 中添加配置条目**，绝对 `command:` (`/data/workspace/hooks/security_guard.py`)；当可能时添加一个 `matcher` 正则表达式，以便脚本仅在相关时启动。
5. **用 `bash` 自己进行干运行** — 将一个样本 JSON 负载管道到脚本中并确认它打印有效的 JSON。**负载必须包括 `event` 字段** — 多事件脚本根据它进行调度，所以省略它会导致每个情况都跳转到 "继续" 并你会错误地认为保护器没有触发。测试脚本处理的每个事件：
   ```bash
   # 应该阻止（注意 `event` 字段）:
   echo '{"event":"pre_tool_call","tool_name":"bash","tool_input":{"command":"rm -rf /"}}' \
     | python3 /data/workspace/hooks/security_guard.py
   # 应该允许（空输出）:
   echo '{"event":"pre_tool_call","tool_name":"bash","tool_input":{"command":"ls -la"}}' \
     | python3 /data/workspace/hooks/security_guard.py
   ```
6. **通过回环自批准 API 自己激活它**（无需用户粘贴）；`command` = 从 yaml 条目中的确切绝对路径：
   ```bash
   curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
     -H 'Content-Type: application/json' \
     -d '{"command": "/data/workspace/hooks/security_guard.py"}'
   ```
   在 `{"ok": true}` 钩子是实时的。在 `404` 时，回退到让用户粘贴 `/hooks approve <command>` + `/hooks on`（见 "配置工作原理"）。

7. **运行 `/hooks doctor` 以确认它实际上可以工作** — 这是捕获错误路径 / 非可执行脚本 / 超时 / 非JSON 的步骤。一个显示为 `/hooks list` 中的 "挂载" 但在 `doctor` 中出错的钩子是一个静默的无操作（失败打开）。只有在 `doctor` 清洁后，才告诉用户它已激活并准备好测试。

## 即用型脚本（每个都有一个明确的工作）

五个 **生产级保护器** 随此技能一起提供在 `templates/` 下（直接复制 + 批准即可）。四个 **单用途示例** 随主机一起提供在 `extensions/shell_hooks/examples/` 下（复制 + 修改）。没有两个重叠——根据工作选择，而不是通过试验。

### 从 `/hooks` 编号或名称安装

`/hooks`（空状态）和 `/hooks help` 显示一个 **编号** 的即用型列表。`/hooks` 命令本身是静态文本——它永远不会安装。当用户回复编号（`"1"`，`"1,3"`），名称（`"security_guard"`），或 `"install all"` 时，该回复会落在你身上：解析它到模板 **通过编号旁边显示的名称**（编号→`templates/<name>.py`），然后为每个运行标准工作流程——复制 → yaml 条目 → 干运行 → 自批准 → `doctor`。

### 生产模板（在此技能中，`templates/`）

> ⚠️ **复制到编辑之前——对于这里的每个模板。** 在 yaml `command:` 和此调用中始终使用 `/data/workspace` 下的绝对路径。**绝对不是相对路径**，如 `skills/agent-hooks/templates/security_guard.py`：桥接程序以 *服务器* 当前工作目录（`/app`）启动脚本，所以相对路径解析为 `/app/skills/…` — 一个空目录 — 并且每个启动都失败——因为桥接程序失败 OPEN，保护器在 `/hooks list` 仍然显示它 "挂载" 的情况下静默地保护什么。为了避免这种情况，标准安装 **将模板复制到 `/data/workspace/hooks/` 并指向 yaml**（见下文的工作流程）。`/app/skills` 不是技能目录——真正的目录是 `/data/workspace/skills/`（通过符号链接称为 `/app/workspace/skills/`）。

| 模板 | 事件 | 它的一个工作 |
|---|---|---|
| `security_guard.py` | `on_user_message`，`pre_tool_call`，`transform_tool_result`，`on_response_end`，`on_outbound_message` | **密钥 + 破坏性 bash。** 阻止粘贴/泄露的密钥（包括 Bearer 令牌），私钥（PEM / EVM 十六进制），种子短语，Solana 字节数组密钥，或 base58 WIF，阻止不可逆数据损失的 bash。见下文。 |
| `verify_publish_claims.py` | `on_stop`（聊天重做） / `on_completion_claim`（`/goal` 重做） | **反幻觉。** 捕获虚构的成功：代理写入 "已发布！community.iamstarchild.com/…"，"推送到 AgentX /post/…" 或 "提醒计划" 当它从未运行工具时。脚本检查回复与 **事实依据** — 预览注册表 (`/data/previews.json`), AgentX 发布账本, 调度注册表 — 并要么重写回复，要么强制重做。它故意低误报：一个真实的发布 URL 或一个 "提出发布"（将来时）会无损通过；只有过去时成功的声明与没有支持会触发它。 |

### 单用途示例（主机存储库，`extensions/shell_hooks/examples/`）

| 脚本 | 事件 | 它的一个工作 |
|---|---|---|
| `pii_redactor.py` | `transform_tool_result`，`on_response_end` | 掩码电子邮件 / 电话（PII — 与密钥不同）。 |
| `tool_audit_log.py` | `post_tool_call` | 仅观察：将每个工具调用追加到 JSONL 审计跟踪。 |
| `budget_alert.py` | `on_response_end` | 当一轮的成本超过阈值时追加一个警告。 |
| `inject_website_reminder.sh` | `pre_llm_call` | 预防性提示：提醒模型在声称完成之前实际发布（与 `verify_publish_claims.py` 配对）。 |

### 被模板取代的（不要发送第二个冲突的保护器）

主机存储库还提供一些 **最小单事件示例** 在 `extensions/shell_hooks/examples/` 下，它们与上面的模板重叠。它们作为学习参考很好，但对于实际使用请选择模板——运行两者会创建两个具有可能不同策略的保护器。

| 最小示例 | 使用这个 | 为什么 |
|---|---|---|
| `block_secrets.py` | `security_guard.py` | 代理的密钥检测是严格超集（添加 Bearer, Solana 字节数组, base58 WIF, 破坏性 bash, 掩码） |
| `check_publish.sh` | `verify_publish_claims.py` | 模板还涵盖 AgentX 发布 + 调度任务，并检查相同的注册表 |

**完全删除**（或遗弃的重复，完全合并到 `security_guard.py`）：
`secret_guard.py`（供应商密钥阻止/掩码，包括 Bearer）和 `dangerous_bash_guard.py`（破坏性 bash 阻止）。想要 *也* 阻止安装程序 / 强制推送？调整保护器的 `DESTRUCTIVE` 表而不是运行一个具有冲突策略的第二个 bash 保护器。

对于任何上述不涵盖的规则，请编写一个新脚本——最小编译示例（见下文的输出协议）是模板，输出协议 above 覆盖了每个功能。

### 最小阻止示例 (`pre_tool_call`，任何语言)

```bash
#!/usr/bin/env bash
payload="$(cat)"
python3 - "$payload" <<'PY'
import json, sys, re
ev = json.loads(sys.argv[1])
cmd = (ev.get("tool_input") or {}).get("command", "")
if re.search(r"rm\s+-rf\s+/|dd\s+if=|mkfs", cmd):
    print(json.dumps({"decision": "block", "reason": f"This command is irreversible and would erase data, so I've blocked it: {cmd}"))
else:
    print("{}")   # continue
PY
```

## 全能型安全保护器 (`templates/security_guard.py`)

一个即用型、自包含脚本，将 **一个文件连接到五个事件** 并涵盖常见的 "不要泄露密钥 / 不要破坏盒子" 基线。首先将其复制到一个稳定的绝对路径，然后在 `config/shell_hooks.yaml` 中将所有五个事件连接到同一个绝对 `command:`（一个事件一个阻止），然后激活：

```bash
cp /data/workspace/skills/agent-hooks/templates/security_guard.py /data/workspace/hooks/
chmod +x /data/workspace/hooks/security_guard.py
curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
  -H 'Content-Type: application/json' \
  -d '{"command": "/data/workspace/hooks/security_guard.py"}'
```

这批准了该命令连接到的每个事件，并将其实时挂载——无需用户粘贴。(**在 `404` 时，回退到 `/hooks approve <command>` + `/hooks on`（见 "配置工作原理"）。)

| 事件 | 它的作用 |
|---|---|
| `on_user_message` | **阻止** 在模型看到它之前粘贴的 API 密钥（包括 Bearer 令牌），私钥（PEM / EVM 十六进制），种子短语，Solana 字节数组密钥或 base58 WIF |
| `pre_tool_call` (bash) | **阻止** 仅不可逆数据损失的 (`rm -rf /`, `dd` 到块设备, `mkfs`, fork 炮弹, `chmod -R 777`, `git reset --hard origin/*``) 和凭证泄露 (`cat .env | curl`, `scp id_rsa`, `printenv | curl`) |
| `pre_tool_call` (消息工具) | 保护 `send_to_telegram` / `send_to_wechat` 参数——**掩码** 泄露的密钥，**阻止** 种子短语（这些工具绕过推送管道，所以这是它们真正的出站门禁） |
| `transform_tool_result` | **警告** 当工具的输出包含密钥时 | |
| `on_response_end` | **掩码** 最终回复中泄露的任何密钥 |
| `on_outbound_message` | **掩码 / 阻止** 在 TG / WeChat 推送之前泄露的密钥 |

**设计策略：** 仅阻止既非常危险又不是正常工作的一部分。常见的开发操作，如 `curl | bash`（安装程序）和 `git push --force`（强制重置你自己的特性分支）是故意 **允许** 的——过度阻止会训练用户禁用保护器。

调整文件顶部的 `SECRET_PATTERNS`，`DESTRUCTIVE` 和 `MSG_TOOLS` 表以适应你自己的规则。`templates/security_guard_selftest.py` 是自测试（在编辑后运行它；危险字符串作为数据仅存在，所以主机 bash 保护器无法触发它们）。 |

## 反幻觉保护器 (`templates/verify_publish_claims.py`)

捕获虚构的成功：代理写入 "已发布！community.iamstarchild.com/…"，"推送到 AgentX /post/…" 或 "提醒计划" 当它从未运行工具时。脚本检查回复与 **事实依据** — 预览注册表 (`/data/previews.json`), AgentX 发布账本, 调度注册表 — 并要么重写回复，要么强制重做。它故意低误报：一个 *真实的* 发布 URL 或一个 "提出发布"（将来时）会无损通过；只有过去时成功的声明与没有支持会触发它。

```bash
cp /data/workspace/skills/agent-hooks/templates/verify_publish_claims.py /data/workspace/hooks/
chmod +x /data/workspace/hooks/verify_publish_claims.py
curl -s -X POST http://localhost:8000/internal/runtime/hooks/approve \
  -H 'Content-Type: application/json' \
  -d '{"command": "/data/workspace/hooks/verify_publish_claims.py"}'
```

| 事件 | 它的作用 |
|---|---|
| `on_response_end` | **(首选)** 在正常聊天中，**阻止** 虚构的成功并强制代理实际发布/重做（循环限制） |
| `on_completion_claim` | 在 `/goal` 循环中 **阻止** 虚构的 "完成" 并保持目标循环运行。 |

> **在正常聊天中连接它**——这是唯一使代理 *实际修复/验证其自己的输出* 的钩子。Claude Code "Stop" 钩子一致性。 |

## 成本/模型页脚 (`templates/runtime_footer.py`)

模型 **无法知道它自己的每条回复成本**——而且通常甚至不知道它自己的模型 ID。这些数据只存在于运行时。因此，如果模型输入它自己的页脚（例如 `Model: GLM-5.2 | Cost: $0.038`），数字是虚构的。一旦真实的页脚进入聊天历史记录，模型的自动完成开始模仿它——产生一个 *第二个* 虚构的页脚。页脚是运行时的责任，不是模型的责任。

`runtime_footer.py` 完全在 **一个事件——`on_response_end`** 上解决——它在每条最终组装的回复中触发一次/轮次：它 ① **删除** 模型在回复末尾输入的任何页脚，然后 ② **附加** 来自运行时真实 `model` + 成本的 **一个真实页脚**。删除是保证；不需要每次调用。 |

**为什么单独在 `on_response_end` 考虑**。没有触发 "就在最终回复之前" 的事件。`pre_llm_call` 触发 *每个* 模型请求之前。连接到 `pre_llm_call` 也会注入提示符（在代理端）。连接 `pre_llm_call` 也可以用于额外的提示（每条模型请求触发）。 |

**默认页脚是** **模型 + 成本** (`─ z-ai/glm-5.2 · $0.0211`)。
`SHOW_TOKENS = True` → `─ z-ai/glm-5.2 · $0.0211 · 900 in / 120 out`。

**显示剩余信用：** `SHOW_CREDIT = True` 追加你的余额 (`─ z-ai/glm-5.2 · $0.0211 · 💰 $271.64`)。默认情况下禁用，因为它添加了 **每轮一个内部 HTTP 调用** 到信用 API——与 `credit` 工具读取相同的端点，由源 IPv6 自动身份验证（无需密钥）。它是失败打开：2 秒超时限制等待，如果查找错误或超时，余额将静默省略（页脚仍然触发，没有悬垂分隔符）。 |

**不要重复：** `runtime_footer` 是 shell 钩子的等效物，主机 `turn_footer` 扩展——启用一个，不要两个。对于 Telegram 的 `tg_show_usage` 也是如此。 |

**安全：** 永远不会阻止。`on_response_end` 在没有成本数据或回复为空时追加 nothing，并且永远只删除回复尾部的狭义匹配页脚（`STRIP = False` 以禁用）；可选的 `pre_llm_call` 注入 nothing 在缺失/格式不正确的负载上；未知事件是无操作的。任何错误都会失败打开。自测试：`templates/runtime_footer_selftest.py`（35 个案例——两个处理程序，删除 + 假阳性保护，用于中间正文 prose 和 shell `$VAR`，信用余额 + 失败打开，文件内常量 + 环境覆盖优先级，调度安全）。 |

## Claude Code 兼容性

为 Claude Code 编写的钩子脚本可以不做更改即可使用——它们的输出会自动转换为上述字段：

| Claude Code 输出 | 转换为 |
|---|---|
| `hookSpecificOutput.permissionDecision: "deny"` (+ `permissionDecisionReason`) | `decision: block` (+ `reason`) |
| `hookSpecificOutput.additionalContext` | `context` |
| `notification` | `on_outbound_message: 重写消息 |
| `systemMessage` | `add_warning` (用户面注释通道) |
<empty> | 继续，无更改 |

**`context` 是代理端**（进入提示符，`pre_llm_call` 仅限）。**`systemMessage` / `add_warning` 是用户端**（向人类显示在工具结果 / 完成 / 出站表面上）——永远不会注入提示符。 |

只有输出 **负载** 被转换——事件名称保持不变 (`pre_tool_call`，不是 `PreToolUse`)。Claude Code 的 **`Stop`** 钩子映射到我们的 `on_stop`（阻止 → 强制重做）；它的 **`UserPromptSubmit` 映射到 `on_user_message`。一个 `Stop` 脚本返回 `{"decision":"block","reason":…"}` 或退出 2 并在连接到 `on_stop` 时工作。 |

## 故障排除 "我的钩子从未触发"

1. 它是上表中 12 个事件之一吗？（拼写错误会导致静默无操作）
2. **主开关** 打开吗？`/hooks list` 显示它。自批准 API 自动启用它；否则 `/hooks on`。
3. 钩子 **已批准** 吗？`/hooks list` 中的 `✗ NOT approved` → 重新运行自批准 API 为该命令（或 `/hooks approve` 作为回退）。 |
4. `matcher` 正则表达式实际上匹配吗？太窄 = 从不启动。
5. 运行 `/hooks doctor` — 它会标记非可执行 / 修改 / 超时 / 非JSON。
6. **手动测试 "允许所有"**？你的测试负载可能缺少 `event` 字段——多事件脚本根据它进行调度，所以省略它会导致每个情况都跳转到 "继续" 并你会错误地认为保护器没有触发。这是一个测试辅助工具的错误，而不是钩子错误；实际运行时始终设置 `event`。
7. **`can't open file '/app/skills/…'` / "挂载" 但什么都没阻止？钩子命令是相对路径或错误。桥接程序以 *服务器* 当前工作目录（`/app`）启动脚本，所以 `skills/…` 解析为 `/app/skills` 的空目录，并且每个启动都失败——因为桥接程序失败 OPEN，保护器在 `/hooks list` 仍然显示它 "挂载" 的情况下静默地保护什么。修复：在 yaml 和批准调用中始终使用绝对路径 `/data/workspace/hooks/<script>.py`，然后重新批准并确认 `/hooks doctor`。 (`/app/skills` 不是技能目录；真正的目录是 `/data/workspace/skills/`（通过符号链接称为 `/app/workspace/skills/`）。 |

## 深入参考

完整的协议、安全模型和每个事件的负载细节都存在于代理自己的文档中：`config/context/references/agent-hooks.md`（阅读它以处理边缘情况，此技能总结了它）。
