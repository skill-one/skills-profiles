# OKX 活动指南 — OKX 营销活动注册与参与

每个活动的流程、CLI 参考文档、常见问题解答（FAQ）和参与门槛都位于此技能的 `references/` 目录下，并以 `<活动名>-*.md` 作为前缀。此 SKILL.md 仅路由，不包含模板、CLI 标志或每个活动的独立副本——因此添加活动永远不会改变现有活动的规则。

## 预检查

在您首次使用 onchainos 命令之前，请阅读 `../okx-agentic-wallet/_shared/preflight.md`。如果不存在，请阅读 `_shared/preflight.md`。

**阻断性** — 它在会话中的首次 `onchainos` 命令之前运行，包含针对每个活动的只读列表调用。

## 意图路由

| 用户意图 | 活动 | 参考文档 |
|---|---|---|
| 注册、报名、加入、参与或参加黑客马拉松（任何语言） | OKX.AI 交易黑客马拉松 | [hackathon-core.md](references/hackathon-core.md)，然后 [hackathon-registration.md](references/hackathon-registration.md) |
| 黑客马拉松参与要求或资格（任何语言）——非注册中 | OKX.AI 交易黑客马拉松 | [hackathon-core.md](references/hackathon-core.md)，然后 [hackathon-faq.md](references/hackathon-faq.md) |

**在生成任何关于活动的用户界面消息之前，必须加载该活动的 `*-core.md`** (**阻断性**)。它包含该活动的参与门槛、输出规则和发送门槛——流程和 FAQ 文件**不会**重复这些内容，因此首先打开 `-registration.md` / `-faq.md` 并非捷径，而是跳过了参与门槛。不要仅凭此文件、记忆或 CLI 的 `--help` 输出来临时编造流程、模板或资格答案。

如果请求指定了**上方无对应行**（没有为其创建参考文件）的活动，请说明该活动目前不受此技能支持——切勿将其他活动的流程适配到它，也切勿猜测其 CLI 子命令。

## 命令索引

此技能驱动 `onchainos <活动>` 子命令（黑客马拉松 → `onchainos hackathon`）。**从 CLI 而非记忆中学习精确语法**：运行 `onchainos hackathon --help` 获取子命令列表，运行 `onchainos hackathon <子命令> --help` 获取子命令的标志。完整参数表、返回字段模式和工作示例位于 [hackathon-registration.md](references/hackathon-registration.md)。

## 错误技能防护

在此处定义的活动进入**该活动定义的主题**（黑客马拉松 → 现有的交易 ASP 代理）。`competition join` (`okx-growth-competition`) 为标准交易竞赛注册**钱包账户**。不同系统，不同主题——**绝对禁止**：互相替换，因为这两个命令注册不同的事物，且均无法撤销。

如果一条请求包含**两者**的信号（例如，同时命名为 "hackathon" *和* "competition" 或 "cup"），请在运行任何命令之前询问用户具体指哪个。

## 安全

- **每项活动注册都是不可逆的**——没有列表、更新、状态或撤销子命令。**必须**在提交前获得用户的明确确认回复；切勿代表用户回答确认提示，也切勿将已指定主题的单次请求视为已预先回答。完整的参与门槛位于活动的 `-registration.md` 中。
- **绝对禁止**：记录、打印或在标志中传递 JWT——它由客户端层从密钥链注入，泄露它将允许攻击者冒充用户。活动流程不会创建新的密钥。
- **必须**在回显执行的命令时遮盖用户标识符（OKX UID 等）（`--uid <隐藏>`）——它们永远不会由 CLI 返回，也永远不会原始粘贴到对话中。
- **绝对禁止**：以任何格式通过内部活动 ID 识别活动——使用名称。CLI 不会返回该 ID；不要从任何其他地方获取它。
- 创建代理身份永远不会是活动流程的一部分——那是 `okx-ai`。此技能仅进入已存在的主题。

## 全局说明

- **使用用户的语言回复。** 此技能参考中的每个模板均以英语作为*结构指南*编写——在发送前翻译它，保持布局和字段不变，且每个 URL 字节不变，仍然是链接。
- 每个活动的 `-core.md` 拥有自身的参与门槛、输出规则和预交付检查清单；这些是此文件的补充，而非替代。

### 添加活动（维护者）

1. 添加 `references/<活动>-core.md`——其参与门槛、阅读顺序、输出规则和预交付检查清单——以及 `references/<活动>-*.md` 用于流程和 FAQ。
2. 为该活动服务的每个用户意图添加一行 Intent Routing，每行是一个完整的 Markdown 链接。
3. 扩展此文件的 `description`，添加新活动的触发词。
