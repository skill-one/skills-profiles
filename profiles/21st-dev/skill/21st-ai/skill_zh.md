# 21st AI — 绘制草图、迭代并从终端获取代码

21st AI 是一个快速 UI 草图绘制板。心智模型：**在此处绘制，然后完成** — 从提示中绘制几个变体，预览它们，使用纯英文编辑来完善您喜欢的那个，并将它的代码拉入仓库。整个循环通过 `21st` CLI（或匹配的 MCP 工具）运行，因此您永远不会离开编辑器。

草图模式生成自包含的 **HTML + Tailwind** 草图（快速，无需构建）。推荐的手工交接方式是 **复制提示**：一个告诉您在目标项目的真实堆栈中重建设计的规范 — 不要直接粘贴原始 HTML。

## 认证

与 CLI 的其他部分使用相同的凭证：`21st login`（保存的令牌）或通过 `--api-key` / `TWENTYFIRST_TOKEN` 的 `21st_sk_` 密钥。`21st usage`（MCP：`get_usage`）显示账户层级、`aiGenerationEnabled` 和剩余的免费每日组件代码检索配额。它不会报告 AI 信用余额。（有关完整的认证说明，请参阅 `21st-cli-use` 技能。）

在生成或迭代之前，检查 MCP `get_usage.aiGenerationEnabled` 或 `21st usage` 中的 `21st AI generation` 行。CLI 1.17.1 还支持 `21st usage --json`。仅在明确启用 AI 时才继续；缺失或未知状态不授予访问权限。基础 Builder 订阅不会启用 AI。当其为 `false` 时，使用 `search` → `get_component` 并使用用户的代理自定义代码。不要尝试 `generate` 或 `iterate_generation`，包括通过 CLI 作为后备。

## 循环

```bash
# 1) 草图 — 从提示中生成变体（“尝试”）。在浏览器中打开预览并打印 projectId。
21st generate "一个包含 3 个层级的定价部分和月度/年度切换"

# 2) 列出尝试（1-based 编号 + 每个是否已渲染）。
21st generation <projectId>

# 3) 使用自然语言更改就地编辑一个尝试（付费 — 请参阅计费）。
21st iterate <projectId> "使其具有企业特色，添加一个年度切换" --take 3

# 4) 获取代码以带入项目（免费）。
21st take <projectId> --take 3            # 复制就绪的复制提示（推荐）
21st take <projectId> --take 3 --code     # 原始自包含 HTML
```

在 `generate` 打印的预览 URL（或 `iterate` 返回的）中打开编辑器内置浏览器，以观察变体就地渲染和更新。

## 何时使用哪个

- **generate** — 从提示开始全新绘制。返回预览 URL + projectId。
- **generation** — 列出尝试，以便您知道要操作哪个 `--take N`。
- **iterate** — 完善现有的尝试（就地编辑；新版本会追加，因此可以在工作区中逐步返回）。使用此方法更改已生成的某物，而不是重新开始。
- **take** — 拉取尝试的代码。默认打印复制提示（适应我的堆栈规范）；`--code` 打印原始 HTML。两者免费且无限。

## 计费

- **generate** — 需要账户上启用 AI 并有可用的 AI 信用。Builder 和 Team 开始于 AI 关闭状态；仅会员资格不会启用它。
- **iterate** — 按每次编辑的实际令牌成本计费（共享的 21st AI 信用池）；每次调用都会进行实际模型工作，因此将批量更改合并为一个清晰的指令，而不是许多微小的指令。
- **generation**（列出）和 **take**（获取代码）是 **免费** 的。

## MCP 兼容性

相同的循环作为 MCP 工具为 MCP 主机（Cursor、Claude Desktop、Claude Code）暴露：`generate`（使用 `mode: "sketch"`）、`get_generation`、`iterate_generation` 和 `get_take`。`iterate_generation` 还返回新编辑的 `html` + `copyPrompt`，因此您可以在没有第二次调用的情况下获取代码。使用 `21st init --client <name> --write` 将服务器连接起来。

MCP 工具列表取决于账户：仅当 AI 启用时才列出 `generate` 和 `iterate_generation`。`get_generation` 和 `get_take` 始终可用于读取现有草图。启用 AI 后，刷新客户端的工具列表或重新连接 MCP 服务器。如果缓存的工具调用返回 `ai_subscription_required`，停止生成尝试并使用上述组件搜索和检索工作流。

## 小贴士

- 草图是一个 **草稿，不是生产代码** — 将复制提示视为设计规范，并在项目的真实组件中重建它；不要直接粘贴 HTML。
- 参考 `generation` 中的 1-based 编号或预览中的“Take N”标签。`--take` 必须是 ≥ 1 的整数（无效值会报错，而不是静默编辑尝试 1）。
