---
name: ui-test
description: 通过浏览器的 CLI 实现人工智能驱动的对抗式 UI 测试。分析 git 差异，仅测试变更内容，或探索完整应用程序以发现错误。测试功能正确性、可访问性、响应式布局和用户体验启发式规则。当用户要求测试 UI 变更、审核拉取请求、审计可访问性或运行探索性测试时使用。支持本地浏览器（localhost）和远程 Browserbase（已部署站点）。
---

# UI 测试 — 代理式 UI 测试技能

在真实浏览器中测试 UI 变更。你的工作是**尝试找出问题**，而不是确认它们能正常工作。

三种工作流程：
- **差异驱动** — 分析 git 差异，仅测试已更改的部分
- **探索式** — 导航应用，找出开发者未考虑到的 Bug
- **并行** — 将独立的测试组分发到多个 Browserbase 浏览器

## 测试工作原理

主要代理**进行协调** — 它规划测试策略，分配给子代理，并合并结果。子代理执行实际的浏览器测试。

### 规划：多角度分析，然后执行一次

**你必须自己完成所有三个规划阶段，并在启动任何子代理之前输出它们。** 规划在你的响应中进行 — 它不会被分配给子代理。不要跳过执行阶段。

**第一轮 — 功能性：** 核心用户流程是什么？应该能正常工作什么？将每个测试写成：操作 → 预期结果。

**第二轮 — 对抗性：** 重新阅读第一轮。你遗漏了什么？思考：不同的用户类型/角色、错误路径、空状态、竞态条件、边缘输入（空、巨大、特殊字符、快速点击）。

**第三轮 — 覆盖范围缺口：** 重新阅读 1-2 轮。考虑：可访问性（axe-core、仅键盘）、移动视图端口、控制台错误、与应用其他部分的视觉一致性？

**去重：** 将所有三轮合并为一个编号的测试列表。删除重复项。将每个测试分配到一组（例如 A 组、B 组）。

**然后执行一次** — 为每组启动一个子代理。每个子代理接收其特定的测试列表来运行，除此之外不再需要其他信息。子代理不探索或规划 — 它们执行分配的测试并报告结果。

在调用任何 Agent 工具之前，在你的响应中输出三轮、合并的计划和组分配。

### 分配工作的原则

- **子代理执行分配的测试，而不是开放探索。** 主要代理将每个子代理分配一个特定的编号测试列表。子代理不规划、探索或决定要测试什么 — 它们执行列表并停止。
- **瓶颈是速度最慢的代理** — 分配工作，以便没有单个代理承担不成比例的份额。许多小代理 > 少数大代理。
- **根据变更规模调整工作量** — 单个组件修复不需要许多代理或许多步骤。全页面的重新设计需要。让差异的范围驱动计划。
- **失败时不提前停止** — 在分配的测试范围内尽可能多地找出 Bug。

### 为子代理分配步骤预算

**主要代理必须在每个子代理提示中包含一个明确的浏览步骤限制。** 子代理不会自我限制 — 它们会一直运行，除非被告知停止。

作为粗略的经验法则：~25 步用于几个目标检查，~40 步用于包含功能性 + 对抗性 + a11y 的全页面，~75 步用于多个页面或一个广泛类别。**根据分配的测试实际需要调整** — 这些是起点，不是规则。

作为粗略的经验法则：~25 步用于几个目标检查，~40 步用于包含功能性 + 对抗性 + a11y 的全页面，~75 步用于多个页面或一个广泛类别。**根据分配的测试实际需要调整** — 这些是起点，不是规则。

每个子代理提示必须包含：
```
你有 N 个浏览步骤的预算（每个 `browse` 命令 = 1 步）。边走边计数。当你达到 N 时，立即停止并报告：
- STEP_PASS/STEP_FAIL 对于你完成的每个测试
- STEP_SKIP|<test-id>|预算达到 对于你没有完成的每个测试

达到预算后不要重试或继续。
仅运行这些测试：[编号列表来自合并的计划]
不要超出分配的测试进行探索。
不要生成 HTML 报告或写入任何文件。仅以文本形式返回步骤标记和你的发现。
```

主要代理不应自己运行 `browse` 命令（除了验证开发服务器是否正常）。所有测试都在子代理中发生。

**当子代理达到其预算时，主要代理将部分结果原样接受。** 不要重新运行或重试子代理。在最终报告中包含 SKIPPED 测试，以便开发者知道哪些内容未被覆盖。

### 报告

**每个子代理都使用以下格式报告：**
```
测试：8 | 通过：5 | 失败：2 | 跳过：1 | 访问的页面：2
```

**主要代理合并为最终报告：**
```
测试：20 | 通过：14 | 失败：4 | 跳过：2 | 代理：3 | 通过率：70%
```

不要报告“使用的步骤” — 浏览命令计数是实施管道，不是对审阅者有意义的指标。

## 测试理念

**你是一个对抗性测试者。** 你的目标是找出 Bug，而不是证明正确性。

- **尝试破坏你测试的每个功能。** 不要只检查“按钮是否存在？” — 快速点击两次，提交空表单，粘贴 500 个字符，在流程中按 Esc。
- **测试开发者未考虑的内容。** 空状态、错误恢复、仅键盘导航、移动溢出。
- **每个断言都必须基于证据。** 比较快照前/后。通过引用检查特定元素。在没有来自可访问性树或确定性检查的具体证据的情况下，永远不要报告 PASS。
- **报告失败时提供足够的信息以便重现。** 包括确切的操作、你预期的结果、你得到的结果以及建议的修复方案。

## 断言协议

每个测试步骤必须生成一个结构化的断言。不要写自由形式的“看起来不错。”

### 步骤标记

对于每个测试步骤，发出一个标记：

```
STEP_PASS|<step-id>|<证据>
```
或
```
STEP_FAIL|<step-id>|<预期> → <实际>|<截图路径>
```

- `step-id`：简短标识符，如 `homepage-cta`、`form-validation-error`、`modal-cancel`
- `证据`：证明步骤通过时你观察到的内容（元素引用、文本内容、URL、评估结果）
- `预期 → 实际`：你预期的结果与实际结果
- `截图路径`：保存截图的路径（仅失败 — 见下文截图捕获）

### 失败的截图捕获

**每个 STEP_FAIL 必须有一个相应的截图**，以便开发者可以直观地看到问题所在。

当测试步骤失败时：

```bash
# 1. 观察到失败后立即截图
browse screenshot --path .context/ui-test-screenshots/<step-id>.png

# 如果 --path 不支持，手动截图并保存：
browse screenshot
# 浏览器 CLI 将输出截图路径 — 移动/复制它：
cp /tmp/browse-screenshot-*.png .context/ui-test-screenshots/<step-id>.png
```

在测试运行开始时设置截图目录：

```bash
mkdir -p .context/ui-test-screenshots
```

**规则：**
- 文件名 = 步骤 ID（例如 `double-submit.png`、`axe-audit.png`、`modal-focus-trap.png`）
- 存储在 `.context/ui-test-screenshots/` — 此目录被 git 忽略，并且对开发者和其他代理可访问
- 对于并行运行，包含会话名称：`<会话>-<step-id>.png`（例如 `signup-double-submit.png`）
- 在失败时截图 — 捕获损坏状态，而不是恢复后
- 对于视觉/布局 Bug，也截图基线（工作状态）以供比较：`<step-id>-baseline.png`

### 验证方法（按严谨程度排序）

1. **确定性检查**（最强）— `browse eval` 返回你可以检查的结构化数据。示例：axe-core 违规计数、`document.title`、表单字段值、控制台错误数组、元素计数。
2. **快照元素匹配** — 具有特定角色和文本的特定元素存在于可访问性树中。通过引用检查：`@0-12 button "Save"`。元素要么存在于树中，要么不存在。
3. **快照前/后比较** — 在操作前快照，操作，操作后快照。验证树是否按预期方式更改（元素出现、消失、文本更改）。
4. **截图 + 视觉判断**（最弱）— 仅用于无法捕获的可访问性树无法捕获的视觉属性（颜色、间距、布局）。始终伴随具体评估内容。

### 快照前/后比较模式

这是核心验证循环。对每个交互使用它：

```bash
# 1. BEFORE：捕获状态
browse snapshot
# 记录：存在的元素、它们的引用、它们的文本

# 2. ACT：执行交互
browse click @0-12

# 3. AFTER：捕获新状态
browse snapshot
# 比较：发生了什么变化？什么出现了？什么消失了？

# 4. ASSERT：根据比较发出标记
# 如果对话框出现：STEP_PASS|modal-open|对话框 "Confirm" 出现在 @0-20
# 如果没有变化：
browse screenshot --path .context/ui-test-screenshots/modal-open.png
# STEP_FAIL|modal-open|预期对话框出现 → 快照未更改|.context/ui-test-screenshots/modal-open.png
```

## 设置

```bash
which browse || npm install -g browse
```

### 避免权限疲劳

此技能运行许多 `browse` 命令（快照、点击、eval）。为了避免逐个批准，将 `browse` 添加到你的允许命令：

将以下模式添加到 `.claude/settings.json`（项目级）或 `~/.claude/settings.json`（用户级）：
```json
{
  "permissions": {
    "allow": [
      "Bash(browse:*)",
      "Bash(BROWSE_SESSION=*)"
    ]
  }
}
```

第一个模式覆盖普通的 `browse` 命令。第二个模式覆盖并行会话（`BROWSE_SESSION=signup browse open ...`）。两者都需要以避免批准提示。

## 模式选择

| 目标 | 模式 | 命令 | 认证 |
|------|------|------|------|
| `localhost` / `127.0.0.1` | 本地 | `browse open <url> --local` | 无需认证（默认情况下干净隔离本地浏览器） |
| 部署/预发布站点 | 远程 | `browse open <url> --remote` | Browserbase 凭证；在支持的地方使用上下文 |

**规则：如果目标 URL 包含 `localhost` 或 `127.0.0.1`，在第一个 `browse open` 中传递 `--local`。**

### 本地模式（localhost 默认）

```bash
browse open http://localhost:3000 --local
```

`browse open ... --local` 默认使用干净的隔离本地浏览器，这对于可重复的 localhost QA 运行最佳。

仅当需要时使用本地模式变体：

- `browse open <url> --auto-connect` — 自动发现现有的可调试本地 Chrome。仅在测试明确需要现有本地登录/cookie/状态时使用。
- `browse open <url> --cdp <端口|url>` — 附加到特定的 CDP 目标（显式本地浏览器连接）。

### 远程模式（通过 cookie 同步的部署站点）

```bash
# 第一步：从本地 Chrome 同步 cookie 到 Browserbase
node .claude/skills/cookie-sync/scripts/cookie-sync.mjs --domains your-app.com
# 输出：上下文 ID：ctx_abc123

# 第二步：使用同步的上下文以远程模式打开
SESSION_JSON="$(browse cloud sessions create --context-id ctx_abc123 --persist --keep-alive)"
SESSION_ID="$(echo "$SESSION_JSON" | jq -r .id)"
CONNECT_URL="$(echo "$SESSION_JSON" | jq -r .connectUrl)"

browse open https://staging.your-app.com --cdp "$CONNECT_URL"
browse snapshot
# ... 运行测试 ...
browse stop
browse cloud sessions update "$SESSION_ID" --status REQUEST_RELEASE
```

Cookie 同步标志：`--domains`、`--context`、`--verified`、`--proxy "City,ST,US"`

## 工作流程 A：差异驱动测试

### 第一阶段：分析差异

```bash
git diff --name-only HEAD~1          # 或：git diff --name-only / git diff --name-only main...HEAD
git diff HEAD~1 -- <文件>            # 读取实际变更
```

对更改的文件进行分类：

| 文件模式 | UI 影响 | 要测试什么 |
|---------|---------|-----------|
| `*.tsx`、`*.jsx`、`*.vue`、`*.svelte` | 组件 | 渲染、交互、状态、边缘情况 |
| `pages/**`、`app/**`、`src/routes/**` | 路由/页面 | 导航、页面加载、内容、404 处理 |
| `*.css`、`*.scss`、`*.module.css` | 样式 | 视觉外观（截图）、响应式 |
| `*form*`、`*input*`、`*field*` | 表单 | 验证、提交、空输入、长输入、特殊字符 |
| `*modal*`、`*dialog*`、`*dropdown*` | 交互式 | 打开/关闭、Esc、焦点陷阱、取消 vs 确认 |
| `*nav*`、`*menu*`、`*header*` | 导航 | 链接、活动状态、路由、键盘导航 |

非 UI 文件仅 | 无 | 跳过 — 报告“不需要 UI 测试”

### 第二阶段：将文件映射到 URL

检测框架：`cat package.json | grep -E '"(next|react|vue|nuxt|svelte|@sveltejs|angular|vite)"'`

| 框架 | 默认端口 | 文件 → URL 模式 |
|------|---------|-----|
| Next.js App Router | 3000 | `app/dashboard/page.tsx` → `/dashboard` |
| Next.js Pages Router | 3000 | `pages/about.tsx` → `/about` |
| Vite | 5173 | 检查路由配置 |
| Nuxt | 3000 | `pages/index.vue` → `/` |
| SvelteKit | 5173 | `src/routes/+page.svelte` → `/` |
| Angular | 4200 | 检查路由模块 |

### 第三阶段：确保运行正确的代码

在测试之前，验证开发服务器正在提供来自差异的代码 — 而不是陈旧的分支。

**如果测试 PR 或特定分支：**
```bash
# 检查当前签出的分支
git branch --show-current

# 如果不是 PR 分支，切换到它
git fetch origin <分支> && git checkout <分支>

# 安装依赖 — 锁文件可能在分支之间不同
yarn install  # 或 npm install / pnpm install
```

如果开发服务器已经在不同的分支上运行，在签出后重启它。

**查找正在运行的开发服务器：**
```bash
for port in 3000 3001 5173 4200 8080 8000 5000; do
  s=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" 2>/dev/null)
  if [ "$s" != "000" ]; then echo "开发服务器在端口 $port (HTTP $s)"; fi
done
```

如果没有找到：告诉用户启动他们的开发服务器。

**验证它确实渲染：**
在 `browse open` + `browse snapshot` 后，检查可访问性树是否包含真实的页面内容（导航、标题、交互元素） — 而不是错误覆盖或空主体。Next.js 开发服务器即使显示全屏构建错误对话框也可以返回 HTTP 200。如果截图为空或被错误对话框主导，服务器已损坏 — 在测试前修复构建。

### 第四阶段：生成测试计划

对于每个更改区域，规划**快乐路径和对抗性测试**：

```
测试计划（基于 git diff）
=============================
更改：src/components/SignupForm.tsx（添加了电子邮件验证）

1. [快乐] 有效电子邮件成功提交
   URL：http://localhost:3000/signup
   步骤：填写有效电子邮件 → 提交 → 验证成功消息出现

2. [对抗性] 无效电子邮件显示错误
   步骤：填写 "not-an-email" → 提交 → 验证错误消息出现

3. [对抗性] 空表单提交
   步骤：不填写任何内容就点击提交 → 验证错误，没有崩溃

4. [对抗性] 电子邮件字段的 XSS
   步骤：填写 "<script>alert(1)</script>" → 提交 → 验证清理/拒绝

5. [对抗性] 快速双提交
   步骤：快速点击两次提交 → 验证不会重复提交

6. [对抗性] 仅键盘流程
   步骤：Tab 到电子邮件 → 输入 → Tab 到提交 → Enter → 验证成功
```

### 第五阶段：执行测试

```bash
browse stop 2>/dev/null
mkdir -p .context/ui-test-screenshots
# 本地/默认 QA → 干净、可重复的本地运行
browse open http://localhost:3000 --local
```

对于每个测试，遵循 **前/后模式**：

```bash
# 导航
browse open http://localhost:3000/path --local
browse wait load

# BEFORE 快照
browse snapshot
# 记录当前状态：元素、引用、文本

# ACT
browse click @0-ref
# 或：browse fill "selector" "value"
# 或：browse type "text"
# 或：browse press Enter

# AFTER 快照
browse snapshot
# 与 BEFORE 比较：发生了什么变化？

# ASSERT 与标记
# STEP_PASS|step-id|证据  OR  STEP_FAIL|step-id|预期 → 实际
```

### 第六阶段：报告结果

## UI 测试结果

### STEP_PASS|valid-email-submit|状态在提交后@0-42出现"谢谢！"
- URL: http://localhost:3000/signup
- 提交前: 表单包含邮箱输入@0-3, 提交按钮@0-7
- 操作: 填写"user@test.com", 点击@0-7
- 提交后: 表单被状态元素替换, 显示"谢谢！我们会联系。"

### STEP_FAIL|double-submit|预期单次提交→表单提交两次|.context/ui-test-screenshots/double-submit.png
- URL: http://localhost:3000/signup
- 提交前: 表单包含提交按钮@0-7
- 操作: 快速连续点击@0-7两次
- 提交后: 出现两个成功提示, 暗示重复提交
- 截图: .context/ui-test-screenshots/double-submit.png
- 建议: 提交后禁用按钮, 或对处理函数进行防抖

---
**总结: 4/6 通过, 2 失败**
失败: double-submit, xss-sanitization

截图保存到 `.context/ui-test-screenshots/` — 打开任何失败步骤的截图即可查看问题状态。

始终在完成时使用 `browse stop`。

### 第 7 步: 生成 HTML 报告

在生成文本报告后, 生成一个独立的 HTML 报告, 审查人员可以在浏览器中打开。报告内嵌截图 (base64), 因此可以作为单个文件使用 — 无需外部依赖。

**原因:** 文本报告适用于代理对话, 但审查人员 (产品经理、设计师、其他工程师) 希望查看可打开、扫描和共享的视觉文档。内嵌截图使失败情况一目了然。

#### 如何生成

1. 阅读 HTML 模板 [references/report-template.html](references/report-template.html)
2. 通过用实际测试数据替换模板占位符来构建报告:

| 占位符 | 值 |
|-------------|-------|
| `{{TITLE}}` | `<title>` 标签的报告标题 (例如, "UI 测试: PR #1234 — OAuth 设置") |
| `{{TITLE_HTML}}` | 可见 `<h1>` 的报告标题。如果提供 PR URL, 将 PR 引用包裹在 `<a>` 标签中以使其可点击 (例如, `UI 测试: <a href="https://github.com/org/repo/pull/1234">PR #1234</a> — OAuth 设置`)。如果没有 URL, 使用与 `{{TITLE}}` 相同的纯文本。 |
| `{{META}}` | 一行上下文: 日期、应用 URL、用户、分支 |
| `{{TOTAL_TESTS}}` | STEP_PASS + STEP_FAIL 的总数 |
| `{{AGENT_COUNT}}` | 运行的子代理数量 |
| `{{PASS_COUNT}}` | STEP_PASS 的数量 |
| `{{FAIL_COUNT}}` | STEP_FAIL 的数量 |
| `{{PASS_RATE}}` | 整数百分比 (例如, "92") |
| `{{RATE_CLASS}}` | `good` (≥90%), `warn` (70–89%), `bad` (<70%) |
| `{{FAILURES_SECTION}}` | 失败测试卡片的 HTML (见下文) |
| `{{PASSES_SECTION}}` | 通过测试卡片的 HTML (见下文) |

3. 为每个测试结果生成一个 `<details>` 卡。失败测试应默认展开, 以便审查人员立即看到它们:

```html
<!-- 失败测试卡片 (默认展开) -->
<div class="section">
  <h2>失败 <span class="count">{{FAIL_COUNT}}</span></h2>
  <details class="test-card fail" open>
    <summary>
      <span class="badge fail">失败</span>
      <span class="step-id">step-id-here</span>
      <span class="evidence">预期→实际</span>
    </summary>
    <div class="body">
      <dl>
        <dt>URL</dt><dd>http://localhost:3000/path</dd>
        <dt>操作</dt><dd>做了什么</dd>
        <dt>预期</dt><dd>应该发生什么</dd>
        <dt>实际</dt><dd>实际发生了什么</dd>
      </dl>
      <div class="suggestion">修复: 建议修复的描述</div>
      <div class="screenshot">
        <img src="data:image/png;base64,..." alt="失败的截图">
        <div class="caption">step-id.png — 在失败时捕获</div>
      </div>
    </div>
  </details>
</div>

<!-- 通过测试卡片 (默认折叠) -->
<div class="section">
  <h2>通过 <span class="count">{{PASS_COUNT}}</span></h2>
  <details class="test-card pass">
    <summary>
      <span class="badge pass">通过</span>
      <span class="step-id">step-id-here</span>
      <span class="evidence">证据摘要</span>
    </summary>
    <div class="body">
      <dl>
        <dt>URL</dt><dd>http://localhost:3000/path</dd>
        <dt>证据</dt><dd>观察到的内容</dd>
      </dl>
    </div>
  </details>
</div>
```

4. **将截图嵌入为 base64**, 使 HTML 完全自包含:

```bash
# 将截图转换为 base64 数据 URI
base64 -i .context/ui-test-screenshots/step-id.png | tr -d '\n'
# 使用: src="data:image/png;base64,<输出>"
```

读取 STEP_FAIL 标记中引用的每个截图文件, base64 编码, 并将其嵌入为 `<img src="data:image/png;base64,...">` 在相应的测试卡片中。对于 STEP_PASS, 只有在明确捕获截图时才嵌入 (例如, 基线截图)。

5. 将最终 HTML 写入 `.context/ui-test-report.html`:

```bash
# 写入生成的 HTML
cat > .context/ui-test-report.html << 'REPORT_EOF'
<!DOCTYPE html>
...生成的报告...
REPORT_EOF

# 为审查人员打开它
open .context/ui-test-report.html  # macOS
# xdg-open .context/ui-test-report.html  # Linux
```

6. 告知用户: `报告保存到 .context/ui-test-report.html` 并提供打开选项。

**规则:**
- 失败部分在通过部分之前 — 审查人员首先关心什么已损坏
- 失败卡片默认为 `open`; 通过卡片折叠
- 每个 STEP_FAIL 卡片必须有一个嵌入的截图 — 如果截图文件丢失, 在卡片中注明
- 如果提供, 在每个失败卡片中包含建议/修复
- 报告必须离线工作 — 无 CDN 链接, 无外部资源
- 保持 HTML 小于 5MB — 如果截图使其超出范围, 降低图像质量或为通过部分跳过基线截图

## 对抗性测试模式

将它们应用于你测试的每个交互元素。阅读 [references/adversarial-patterns.md](references/adversarial-patterns.md) 获取完整的模式库 (表单、模态框、导航、错误状态、键盘可访问性)。

## 确定性检查

这些产生结构化数据, 而非判断。将它们用作最强的断言形式。

| 检查 | 捕获的内容 | 断言 |
|-------|----------------|-----------|
| axe-core | WCAG 违规 | `violations.length === 0` |
| 控制台错误 | 运行时异常、失败的请求 | 空错误数组 |
| 破坏性图片 | 缺失/失败的图片加载 | 没有图片的 `naturalWidth === 0` |
| 表单标签 | 没有可访问标签的输入 | 每个输入都有 `hasLabel: true` |

对于确切的 `browse eval` 配方, 阅读 [references/browser-recipes.md](references/browser-recipes.md)。

## 工作流 B: 探索性测试

无差异, 无计划 — 直接打开应用并尝试使其崩溃。在用户说 "测试我的应用"、"找 Bug" 或 "测试这个网站" 时使用。

### 方法

1. **发现应用** — 阅读 `package.json` 检测框架, 然后打开根 URL 并快照查看有什么内容
2. **导航一切** — 点击导航链接, 访问每个可访问页面, 记录存在的内容
3. **测试你发现的内容** — 对于每个页面, 应用以下对抗性模式 (表单、模态框、导航、键盘、错误状态)
4. **运行确定性检查** — axe-core、控制台错误、破坏性图片、表单标签在每页上
5. **报告发现** — 使用 STEP_PASS/STEP_FAIL 标记, 失败时包含重放步骤

不要试图系统地覆盖范围。像用户一样探索, 但意图是使其崩溃。代理擅长此操作 — 让它自由漫游。

### 探索性运行的技巧

- 从主页开始, 自然跟随导航
- 尝试 404 页 (`/does-not-exist`) — 它是自定义的还是默认的?
- 查找空状态 (没有数据的页面)
- 在有效输入之前测试带有垃圾输入的表单
- 每页检查移动视口 (375px) — 是否溢出?
- 如果应用有认证, 首先使用 cookie-sync

## 工作流 C: 并行测试

使用命名的 `browse` 会话 (`BROWSE_SESSION=<name>`) 并发运行独立的测试组。每个会话都有自己的浏览器。适用于本地和远程模式。

在测试多个页面或类别并希望更快墙时钟时间时使用。

阅读 [references/parallel-testing.md](references/parallel-testing.md) 获取完整的工作流: 会话设置、代理发散、认证的 cookie-sync 和结果合并。

## 设计一致性

检查更改的 UI 在视觉上是否与应用的其余部分匹配。在执行视觉或设计检查时阅读 [references/design-consistency.md](references/design-consistency.md)。

## 测试类别

| 类别 | 如何 | 断言类型 |
|-------|-----|---------------|
| 可访问性 | axe-core + 键盘导航 | 确定性 (违规计数) |
| 视觉质量 | 截图 + 启发式评估 | 视觉判断 (最弱 — 注明具体细节) |
| 响应式 | 视口扫描 + 截图 | 视觉 + 确定性 (溢出检查) |
| 控制台健康 | 控制台捕获评估 | 确定性 (错误计数) |
| UX 启发式 | 截图 + UX 定律 + Nielsen's | 结构化判断 (引用特定启发式) |
| 错误状态 | 导航到空/错误状态 | 前/后比较 |
| 数据显示 | 表格/仪表板的截图 | 元素匹配 (列数、格式) |
| 设计一致性 | 截图基线 + 更改页面比较 | 视觉判断 (引用特定属性) |
| 探索性 | 自由导航 + 对抗性测试 | 前/后 + 判断 |

参考指南 (按需加载):
- **对抗性模式** — [references/adversarial-patterns.md](references/adversarial-patterns.md) — 测试表单、模态框、导航或键盘 a11y 时加载
- **浏览器配方** — [references/browser-recipes.md](references/browser-recipes.md) — 运行确定性检查 (axe-core、控制台、图片、表单标签) 时加载
- **探索性测试** — [references/exploratory-testing.md](references/exploratory-testing.md) — 用于工作流 B (无差异, 开放式探索)
- **UX 启发式** — [references/ux-heuristics.md](references/ux-heuristics.md) — 评估 UX 质量或引用特定启发式时加载
- **设计系统** — [references/design-system.example.md](references/design-system.example.md) — 用户自定义的模板
- **设计一致性** — [references/design-consistency.md](references/design-consistency.md) — 执行视觉一致性检查时加载
- **并行测试** — [references/parallel-testing.md](references/parallel-testing.md) — 用于工作流 C (并发会话)
- **报告模板** — [references/report-template.html](references/report-template.html) — 用于第 7 步报告生成的 HTML 模板

对于包含确切命令的示例, 如果需要查看断言协议的实际操作, 阅读 [EXAMPLES.md](EXAMPLES.md)。

## 最佳实践

1. **保持对抗性** — 尝试使其崩溃, 不要只是确认它们工作
2. **每个断言都需要证据** — 快照引用、eval 结果或前/后差异
3. **每个交互前/后** — 快照, 操作, 快照, 比较
4. **每个失败都截图** — `browse screenshot` 立即在 STEP_FAIL, 保存到 `.context/ui-test-screenshots/<step-id>.png`
5. **先进行确定性检查** — axe-core、控制台错误、表单标签在视觉判断之前
6. **对于 localhost, 从干净的本地模式开始** — 在第一个 `browse open` 时传递 `--local` 以获得可重复的运行; 仅在需要现有本地状态时使用 `--auto-connect`
7. **完成时始终使用 `browse stop`** — 对于并行运行, 停止每个命名会话
8. **用重放步骤报告失败** — 操作、预期、实际、截图路径、建议
9. **并行化独立测试** — 使用工作流 C 和命名会话测试部署站点的多个页面或类别

## 故障排除

- **"没有活动页面"**: `browse stop`, 重试。对于僵尸: `pkill -f "browse.*daemon"`
- **开发服务器无响应**: `curl http://localhost:<port>` — 请用户启动它
- **`browse eval` 与 `await` 失败**: 使用 `.then()` 而不是 — `browse eval` 不支持顶级 await
- **元素引用未找到**: `browse snapshot` 再次 — 引用在页面更新后更改
- **空白快照**: `browse wait load` 或 `browse wait selector ".expected"` 在快照前等待
- **SPA 深链接 404**: 首先导航到 `/`, 然后点击
- **远程认证失败**: 使用 `--context <id>` 重新运行 cookie-sync, 尝试 `--verified`
- **并行会话冲突**: 确保每个 `browse` 命令使用 `BROWSE_SESSION=<name>` — 如果没有, 命令将发送到默认会话
- **会话未停止**: `BROWSE_SESSION=<name> browse stop`。对于僵尸: `pkill -f "browse.*<name>.*daemon"`
