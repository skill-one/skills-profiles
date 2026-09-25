## 第 0 阶段：技能发现与必读材料

**⚠️ 关键 — UI 设计质量门禁：** 如果项目产生任何视觉 HTML 输出（仪表盘、Web 应用、着陆页、作品集、任何用户将看到的页面），你必须在编写任何 HTML/CSS 之前强制 `read_file` `ui-design` 技能的 SKILL.md 并遵循它。这不是可选的。project-builder 处理工程；ui-design 处理视觉质量（并告诉你何时使用组件库，如 shadcn/ui、HeroUI 或 coss ui 而不是手写）。跳过 ui-design 会导致通用的 AI 拉圾。

**A. 选择源代码和工具。** 对于研究和 API 文档，使用网络搜索。对于实时市场数据或外部操作，重用相关的已安装技能。在使用前阅读其 SKILL.md；使用 `auto_install=false` 搜索缺失的技能，并在用户批准后安装。只有在确认没有合适的技能涵盖该操作后，才编写自定义 API 代码；根据当前官方文档验证端点和响应形状。

**B. 阅读平台规则，了解项目所涉及的规则。** 这些规则存在于引用中（而不是你的系统提示中），因此你必须在使用代码之前 `read_file` 它们。跳过这一点是导致 401 错误、路径损坏和“本地工作正常，预览失败”错误的主要原因。

| 如果项目包含... | 在第 2 阶段之前 `read_file` |
|---|---|
| 任何外部 API 调用 | `config/context/references/sc-proxy.md` |
| 预览 / 仪表盘 / Web 应用 | `config/context/references/preview-guide.md` |
| 定时任务 | `config/context/references/scheduled-tasks-guide.md` |
| 长时间运行的背景作业 | `config/context/references/background-tasks.md` |
| 文件写入 >300 行 | `config/context/references/tool-writing-guide.md` |
| **任何视觉 HTML 输出**（仪表盘、Web 应用、着陆页、作品集） | **`ui-design` 技能的 SKILL.md** — 加载它并遵循它进行所有视觉决策（跟踪选择、颜色、排版、布局、动画，以及何时使用组件库）。此技能是 UI 质量门禁；跳过它会导致通用的 AI 拉圾。 |

---

## 第 1 阶段：设计
**将模糊请求转换为具体规范。** 如果意图不明确，问一个问题。

架构决策树：
```
周期性警报/报告？  → 定时任务
实时视觉界面？    → 预览服务器（仪表盘）
一次性分析？        → 内联（无需构建）
可重用工具？            → 工作区中的脚本
```

对于中等规模以上的项目，在编写代码之前向用户展示：
1. 数据流 — 源头 → 处理 → 输出
2. 架构选择及其原因
3. 成本估算 — (每次运行成本) × 频率 × 30 = 每月
4. 已知限制

**UI 设计门禁（必需、阻塞 — 用于视觉项目）：**
如果架构选择是预览服务器或任何输出用户将看到的 HTML 的项目：
1. `read_file` `ui-design` 技能的 SKILL.md **现在**（如果你在这个会话中还没有这样做）并选择一个轨道（手写 vs 组件库）。
2. 对于手写 UI，运行设计旋钮（在 ui-design 的 `references/design-process.md` 中）以确定表面、强调色、排版和美学系列。
3. 在你的阶段计划下方包含设计旋钮输出行。
如果你跳过这一步，UI 将看起来像通用的 AI 输出。此门禁是阻塞的 — 在完成它之前不要继续到第 2 阶段。

**设计门禁：** 对于多阶段工作，提交一个简短的阶段计划。如果用户已经授权了清晰且可逆的实现，则无需再次请求相同的批准。仅在范围确实模糊、需要批准重大成本或下一步操作是不可逆的/外部的（发布、发送、交易、删除）时才询问。活动计划模式保持只读，直到用户批准执行。

---

## 第 1.5 阶段：脚手架（共享项目强制要求）

设计确认后，**在编写任何代码之前**，在标准布局下搭建项目。这使项目从一开始就可以通过 `community-publish` 技能共享 — 无需后期迁移。

**标准项目位置：** `output/projects/{slug}/`

```
output/projects/{slug}/
├── project.yaml          # 名称、版本（从 0.1.0 开始）、类型、描述、许可证、入口、所需环境
├── PROJECT.md            # 4 个必需部分：是什么 / 所需环境 / 如何启动 / 输出 / 故障排除
├── .env.example          # 代码读取的每个环境变量，带有占位符值
├── .gitignore            # 至少：.env、*.key、*.pem、__pycache__、node_modules
└── src/                  # 所有代码都放在这里，不要分散
    ├── run.py            # 类型=任务 — 第一行必须是：# -*- task-system: v3 -*-
    ├── server.py         # 类型=服务
    ├── main.py           # 类型=脚本
    └── index.html / app.py + 前端  # 类型=预览
```

**项目类型 → 入口映射：**

| 架构选择 | type | entry path |
|---|---|---|
| 定时任务 | `task` | `src/run.py` |
| 预览服务器 | `preview` | `src/index.html`（静态）或 `src/app.py` |
| 背景守护进程 | `service` | `src/server.py` |
| 一次性工具 | `script` | `src/main.py` |

**仅当以下情况时才跳过脚手架：**
- 纯内联分析，无需持久代码
- 修改现有的 `output/projects/...` 项目（保留其布局）
- 用户明确说“直接在 /tmp 放一个脚本”或类似

**在第 2 阶段构建期间维护脚手架：**
- 代码读取的每个新环境变量 → 添加到同一编辑的 `.env.example` 中
- 每个行为变化 → 更新 PROJECT.md
- 永远不要在 `src/` 外编写代码（配置、固定：项目根目录或 `src/data/`）

**为什么这很重要：** 已处于标准布局的项目可以通过一条命令发布。分散在 `tasks/`、`output/scripts/`、`dashboards/` 等位置的项目需要 `tidy_project()` 迁移才能共享，用户通常不希望从记忆中重建 PROJECT.md。

**对于现有的分散代码：** 调用 `community-publish` 技能 → `tidy_project(any_dir)` 以重新组织发布前。

---

**API 成本与速率限制：**
所有外部 API 调用都通过 sc-proxy，它按请求计费并执行速率限制。
在设计之前，**阅读 `config/context/references/sc-proxy.md`** 以获取定价表和限制。
- 估算成本：`credits_per_request × requests_per_run × runs_per_day × 30`
- 尊重速率限制：例如 CoinGecko 每分钟 60 个请求 — 每分钟轮询 10 个币是没问题的；100 个币则不行
- 优先选择批量端点而不是 N 个单独调用（例如 `coin_price` 带有多个 id vs N 个单独调用）
- 纯脚本任务（无 API）：~0 credits/run
- **LLM 成本警告：** 高端模型可能超过 **每单个调用 0.10 美元**。价格因模型等级差异很大；昂贵模型的成本可能是预算模型的 **100 倍以上**。
- **模型感知估算要求：** 将 LLM 成本按模型分解（`model_price_per_call × expected_calls_per_run × runs_per_day × 30`）而不是使用一个通用的数字。
- 仪表盘自动刷新成本为 credits — 默认手动刷新，除非用户要求否则如此
- **支出保护：** 如果预计每月 LLM 成本很高，在实施前明确询问是否要执行每个调用者的限制。
- **调用者跟踪（必需）：** 每个代理请求必须包含 `SC-CALLER-ID`（例如 `job:{JOB_ID}`、`preview:{preview_id}`、`chat:{thread_id}`），以便跟踪和限制使用。详情在 `config/context/references/sc-proxy.md` § 调用者信用限制

**数据可靠性：** 本地工具 > 代理 API > 直接请求 > 网络抓取 > LLM 数字（永远不要）。
**铁律：脚本获取数据。LLM 分析文本。最终输出 = 脚本变量 + LLM 文本。**

**任务脚本可以直接导入技能函数：**
```python
from core.skill_tools import coingecko, coinglass  # 自动发现技能/*/exports.py
prices = coingecko.coin_price(coin_ids=["bitcoin"], timestamps=["now"])
```
工具名称 = SKILL.md 前置 `tools:` 列表。见 `build-patterns.md § 使用技能函数`。

---

## 第 2 阶段：构建
每个部分都遵循这个循环：
```
构建一个小部分 → 运行它 → 验证输出 → ✅ 下一个部分 / ❌ 修复第一个
```

| 构建 | 验证方式 | 通过 |
|-------|-----------|------|
| 数据获取器 | 运行，打印原始响应 | 非空、近期、合理 |
| API 端点 | `curl localhost:{port}/api/...` | 正确的 JSON |
| HTML 页面 | `preview_serve` + `preview_check` | `ok = true` |
| 任务脚本 | `python3 tasks/{id}/run.py` | 数字与源匹配 |
| LLM 分析 | 脚本变量中的数字，不是 LLM 文本 | 使用模板模式 |

**验证分层：**
- **关键**（必须通过预览/激活前）：数据正确性、核心逻辑、无崩溃
- **信息性**（交付后可以修复）：样式、边缘情况消息、轻微的 UX 精炼

**反模式：**
- ❌ “完成！”而没有运行任何东西
- ❌ 编写 200+ 行然后第一次测试
- ❌ “它应该工作”

→ 详细模式：**阅读 `references/build-patterns.md`**

### 代码实践

- `read_file` 优于 `edit_file` — 了解其中的内容
- `edit_file` > `write_file` 用于修改
- 在 `write_file` 之前检查 `ls` — 避免重复现有文件
- 大文件（>300 行）：拆分成多个文件，或骨架优先 + bash 注入
- 环境变量：`os.environ["KEY"]`，将安装持久化到 `setup.sh`

### 仪表盘 UX 默认值（`type=preview`）

自行决定合理的默认值，并在第一次加载时显示真实数据。将过滤器视为用户可以稍后调整的可选改进 — 永远不要将其视为阻塞初始视图的先决条件。在合理的间隔内自动刷新。没有“点击加载” / “输入地址” / “选择符号”等，直到出现任何内容。

**视觉设计质量（所有 HTML 输出强制要求）：** 如果 `ui-design` 技能已安装，你必须在编写任何 HTML/CSS 之前 `read_file` 它的 SKILL.md 并遵循它。project-builder 拥有工程工作流；ui-design 拥有视觉质量。单独使用 project-builder 会导致功能但视觉通用的输出。

---

### 平台规则

- 代理工具仅是工具调用 — 不能在脚本中导入
- 预览路径必须是相对的（`./path` 而不是 `/path`）
- **在代码中硬编码预览端口，不要从环境变量读取。** 每个预览都在其自己的 Pod 中运行，并且 env-port 合同跨 Pod 不可靠。选择任何空闲端口（例如 `8765`），直接将数字写入应用程序，并将相同的数字传递给 `preview(action="serve", port=...)`。两者必须完全匹配。
- **并发预览需要不同的 ID。** 如果两个预览共享相同的 `dir`，较新的会自动杀死较旧的（相同目录替换规则）。预览 ID 现在锚定到目录：重新加载相同的 `dir` 会保持相同的 ID，即使标题更改，之前共享的 `/preview/{id}/` 链接仍然有效。重新加载后，始终重新发送 `/preview/{id}/` 链接到用户。不要编造新的标题希望获得新的 ID，也不要猜测 ID 变体。
- 全栈 = 一个端口（后端提供 API + 静态文件）
- Cron 时间为 UTC — 从用户时区转换
- 预览服务 & 发布 → 阅读平台引用 `config/context/references/preview-guide.md`
- localhost API → 阅读平台引用 `config/context/references/localhost-api.md`
  - 任务脚本决定何时调用代理，传递哪些数据/上下文，使用哪个模型
  - 模式：脚本获取数据 → 评估是否值得注意 → 仅在需要时调用 LLM → 打印结果
- **脚本中的 LLM — 两个选项**（详情在 `references/build-patterns.md`）：
  - **OpenRouter**（通过 sc-proxy）：轻量级，用于总结/翻译/格式化文本。直接 API 调用，无代理开销。
  - **localhost /chat/stream**：完整代理，带工具。仅在 LLM 需要工具访问时使用。
- **数据模板规则**：脚本拥有数字，LLM 拥有文字。最终输出组合脚本变量 + LLM 分析。永远不要让 LLM 输出成为用户看到的数字的唯一来源。
- API 成本 & 速率限制 → 阅读平台引用 `config/context/references/sc-proxy.md`
- **变现（可选）**：你构建的任何 HTTP 服务都可以通过 `x402` 技能转换为
  收费服务 — 一个位于应用程序前面的反向代理网关在 Base 上每调用 / 订阅（每周–年度）/
  终身 / 预付费余额，支持多计划。如果用户提到为项目收费、销售 API 访问或代理到代理的支付，
  在构建阶段后阅读 `skills/x402/SKILL.md` 并用 `scripts/monetize.py` 包装服务
  （暴露 GATEWAY 端口，而不是上游）。
  包装后的付费服务链：`preview(serve)` 网关 →
  `community-publish` → `publish_preview()`（公共 URL）→
  `create_paid_service(..., pricing_options=[...])` → `submit_for_review()`
  （多计划服务：审查探针每个计划的 402 金额通过 `X-Pricing-Model` 标头）→ `publish_service()` → 在服务
  市场上线。详情：community-publish SKILL.md § 付费服务列表。
- **始终运行的服务（长时间运行 / 发布 / 收费）**：代理机器在空闲时自动挂起，自动更新重启会杀死服务进程。任何必须 24/7 保持可达的服务需要：① 一个保持活动状态的看门狗
  （定时任务重新启动服务 — 见 `skills/x402/SKILL.md` “始终运行可用性”），② 机器切换到
  手动更新模式（Web 仪表板切换；代理只能在机器内读取模式 — 如果它读取“auto”，提醒用户
  切换开关，否则下一个平台更新将导致服务下线）。

---

## 第 3 阶段：调试
```
检查日志 → 重现 → 隔离 → 诊断 → 修复 → 验证 → 回归
```

- **检查日志** 首先一一检查 — 任务日志、预览诊断、stderr。如果日志显示明确的起因，跳到修复。
- **重现** 仅当日志不足时 — 亲自查看失败
- **隔离** 哪一层损坏（数据？逻辑？LLM？输出？前端？后端？）
- **修复** 根本原因，然后用相同的重现步骤 **验证**。不要只修复 — 修复并确认。

**三击规则：相同方法失败两次 → 停止 → 重新思考 → 向用户解释 → 采取不同方法。**

→ 完整调试程序：**阅读 `references/debug-handbook.md`**

---

## 快速清单
**启动：** ☐ 明确意图 ☐ 提出架构 ☐ 估算成本 ☐ 用户确认（**在第 2 阶段之前必需**）

**构建：** ☐ 每个组件测试 ☐ 数字与源匹配 ☐ 错误处理 ☐ 预览健康（Web）

**调试：** ☐ 检查日志 ☐ 重现（或跳过 — 日志足够） ☐ 隔离层 ☐ 找到根本原因 ☐ 修复验证 ☐ 回归检查
