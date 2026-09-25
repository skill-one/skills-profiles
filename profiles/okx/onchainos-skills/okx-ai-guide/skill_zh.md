# OKX.AI 指南

OKX.AI 的入门入口。介绍 OKX.AI（代理经济系统），检测当前运行环境是否可以运行 OKX.AI，并将用户引导至三个身份注册流程之一——或者，在不兼容的平台上，告知他们如何获取兼容的平台。

## 指令优先级

标记块表示规则严重性（冲突时优先级更高）：

1. **`<NEVER>`** — 绝对禁止。
2. **`<MUST>`** — 强制步骤。
3. **`<SHOULD>`** — 最佳实践。

## 范围与边界

此技能拥有：OKX.AI 介绍 + 平台检测 + 登录与身份检测（新用户与回访用户）+ 引导至注册。它不包括：

- 拥有 Onchain OS 欢迎横幅——那是 `okx-how-to-play`。
- 实现注册——委托给 `okx-agent-identity`（见 §步骤 5）。
- 拥有钱包登录流程——步骤 1 仅 *检查* 通过 `wallet status` 登录，并在需要时将用户转交给 `okx-agentic-wallet` 的现有登录流程；注册剧本也会运行自己的预检查。

<NEVER>
不要从此技能调用 `onchainos agent create`（或任何注册 / 质押 CLI）。注册始终委托给 `okx-agent-identity`。（步骤 1 中的只读 `onchainos wallet status` 和 `onchainos agent get-my-agents` 是允许的——它们不会创建任何内容。）
</NEVER>

## 步骤 0 — 平台检测

<MUST>
运行以下检测函数并读取其单行输出。`compatible` = 输出不是 `unknown`。
</MUST>

```bash
detect_harness() {
  if [ "${CLAUDECODE:-}" = "1" ]; then
    echo "Claude Code"
  elif [ -n "${HERMES_INTERACTIVE:-}" ] || [ -n "${HERMES_SESSION_SOURCE:-}" ] \
    || [ -n "${HERMES_YOLO_MODE:-}" ] || [ -n "${HERMES_QUIET:-}" ]; then
    echo "Hermes"
  elif [ -n "${OPENCLAW_CLI:-}" ] || [ -n "${OPENCLAW_SHELL:-}" ]; then
    echo "OpenClaw"
  elif [ -n "${CODEX_THREAD_ID:-}" ] || [ -n "${CODEX_CI:-}" ]; then
    echo "Codex"
  else
    echo "unknown"
  fi
}
detect_harness
```

- 输出 ∈ {`Claude Code`, `Hermes`, `OpenClaw`, `Codex`} → **兼容** → 步骤 1。
- 输出 = `unknown` → **不兼容** → 步骤 3。

## 步骤 1 — 兼容：登录 + 身份检测（路由门）

仅当步骤 0 为 **兼容** 时到达。此步骤决定显示哪个页面——通过先检查登录 **再** 检查身份。顺序是强制性的：`agent get-my-agents` 需要登录会话，因此确认登录前切勿查询身份。

<MUST>
1. **登录检查** — 运行 `onchainos wallet status` 并读取 `loggedIn`。
   - `loggedIn: false` → 用户未登录。不要查询身份。转交给现有的钱包登录流程（[`../okx-agentic-wallet/SKILL.md`](../okx-agentic-wallet/SKILL.md) §登录）：提示登录，成功后返回此处（重新运行 `wallet status`，然后进行身份检查）。
   - `loggedIn: true` → 继续进行身份检查。
2. **身份检查** — 运行 `onchainos agent get-my-agents`。它返回登录用户的 XLayer 上的 OKX.AI 代理（通过 JWT 识别）。
   - **空**（无代理）→ 用户没有 OKX.AI 身份 → **步骤 2**（角色选择页面）。
   - **≥1 代理** → 用户已有身份 → **步骤 4**（已注册用户主页）。
</MUST>

分支完全由 `agent get-my-agents` 是否返回任何代理决定——永远不会向已有身份的用户显示角色页面（步骤 2），也不会向无身份的用户显示已注册主页（步骤 4）。

## 步骤 2 — 兼容且未注册：角色选择页面

从步骤 1 在用户登录但**没有** OKX.AI 身份时到达。渲染角色选择页面（变体 A）并按 [`references/unregistered-role-selection.md`](./references/unregistered-role-selection.md)（包含步骤 2 页面 + 步骤 5 路由）的 `1`/`2`/`3` 回复进行路由。当此分支被触发时加载它。

## 步骤 3 — 不兼容：介绍 + 安装指南

从步骤 0 在平台**不兼容**（`unknown`）时到达。不适用登录 / 身份检查——此处无法运行 OKX.AI。

**自由区域（1-5 句话）：** 回答用户的 OKX.AI 问题，然后过渡。

**固定区域：** 渲染来自 [`references/intro.md`](./references/intro.md) 的 **变体 B**（用户语言），替换 `{install_doc_url}`。不要提供编号选项；结束对话。

## 步骤 4 — 兼容且已注册：用户主页

从步骤 1 在用户登录且已有 **≥1** OKX.AI 身份时到达。渲染已注册用户主页（变体 C，字段精确填充来自 `agent get-my-agents` 结果）并按 [`references/registered-home.md`](./references/registered-home.md) 处理其菜单回复（步骤 6：`1` + 代理 ID → 该代理的当前任务；`2` → 顶级 ASP；`注册一个 `<角色>`` → 注册缺失的角色）加载它时处理此分支。

## 步骤 5 — 角色选择后的路由

在 [`references/unregistered-role-selection.md`](./references/unregistered-role-selection.md) 中与步骤 2 一同处理（`1`/`2`/`3` 回复 → 等待状态行 + 注册剧本）。

## 步骤 6 — 已注册主页菜单路由（来自步骤 4）

在 [`references/registered-home.md`](./references/registered-home.md) 中处理——涵盖 `1` + 代理 ID → `agent task-in-progress` 与状态映射，`2` → 通过 `agent search --query '按销量从高到低排序'` 按销量排序的顶级 ASP，以及“注册 `<角色>` 身份”重定向。

## 接受标准

1. `detect_harness` 为每个标记集返回正确的平台；其他 → `unknown` → 不兼容分支（步骤 3）。
2. 兼容分支（步骤 1）在身份（`agent get-my-agents`）**之前**检查登录（`wallet status`）——未登录时永不查询身份。
   - 未登录 → 转交给现有的钱包登录流程，然后继续检查。
   - 登录 + 无身份 → 角色选择页面（步骤 2）；回复 `1` / `2` / `3` 渲染正确的等待状态并加载正确的注册剧本（步骤 5）。
   - 登录 + ≥1 身份 → 已注册用户主页（步骤 4），填充来自 `agent get-my-agents` 结果；主页菜单（步骤 6）路由 `1` + 一个代理 ID → 该代理的当前任务通过 `agent task-in-progress`，将每个任务的 `status` 映射到标签（例如 `2` 提交 = 已交付/等待接受）而不是笼统标记所有为“进行中”（`code=3001` → “不是你的代理，重新输入”），`2` → 通过 `agent search --query '按销量从高到低排序'` 按销量排序的顶级 ASP（后端语义按销量排序）。
3. 不兼容分支（步骤 3）显示三角色介绍（无选项）+ 安装提示 + `{install_doc_url}`；结束对话。
4. `OKX.AI 快速开始` / `OKX.AI quick start` 触发此技能。
5. 固定区域文本以用户语言渲染；表情符号 / 数字 / URL / 占位符保持原样。
6. 此技能中零 `onchainos agent create` 调用（仅只读 `wallet status` / `agent get-my-agents`）；零 Rust 修改。
