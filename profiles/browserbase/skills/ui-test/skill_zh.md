# UI 测试 — 代理式 UI 测试技能

在真实浏览器中测试 UI 变更。你的工作是**尝试破坏东西**，而不是确认它们能正常工作。

三种工作流程：
- **差异驱动** — 分析 git 差异，仅测试已更改的内容
- **探索式** — 导航应用程序，发现开发者未考虑到的错误
- **并行** — 将独立的测试组分发到多个 Browserbase 浏览器

## 测试工作原理

主要代理**协调** — 它规划测试策略，委派给子代理，并合并结果。子代理执行实际的浏览器测试。

### 规划：多角度，然后执行一次

**你必须亲自完成所有三个规划阶段，并在启动任何子代理之前输出它们。** 规划发生在你自己的响应中 — 它**不**委派给子代理。不要跳过执行阶段。

**第一轮 — 功能性：** 核心用户流程是什么？应该做什么？将每个测试写成：操作 → 预期结果。

**第二轮 — 对抗性：** 重新阅读第一轮。你遗漏了什么？思考：不同的用户类型/角色，错误路径，空状态，竞争条件，边缘输入（空，巨大，特殊字符，快速点击）。

**第三轮 — 覆盖范围缺口：** 重新阅读第一轮至第二轮。考虑：可访问性（axe-core，仅键盘），移动视图端口，控制台错误，与应用程序的其余部分视觉一致性？

**去重：** 将所有三个轮次合并为一个编号的测试列表。删除重复项。将每个测试分配到一组（例如，组 A，组 B）。

**然后执行一次** — 为每组启动一个子代理。每个子代理接收其特定的测试列表来运行，除此之外什么也不做。子代理不探索或规划 — 它们执行分配的测试并报告结果。

在调用任何 Agent 工具之前，在你的响应中输出三个轮次，合并的计划和组分配。

### 分割工作的原则

- **子代理运行分配的测试，而不是开放探索。** 主要代理将每个特定的编号测试列表交给子代理。子代理不规划，探索或决定要测试什么 — 它们执行列表并停止。
- **瓶颈是最慢的代理** — 分割工作，以便没有单个代理承担不成比例的份额。许多小代理 > 少数大代理。
- **根据变更规模调整工作量** — 单个组件修复不需要许多代理或许多步骤。全页面的重新设计需要。让差异的范围驱动计划。
- **失败时不提前停止** — 在分配的测试范围内尽可能多地找到错误。

### 给子代理分配步骤预算

**主要代理必须在每个子代理提示中包含明确的浏览步骤限制。** 子代理不自我限制 — 它们将运行直到完成，除非另有指示。

作为粗略的经验法则：~25 步用于几个有针对性的检查，~40 步用于包含功能性 + 对抗性 + a11y 的全页面，~75 步用于多个页面或广泛的类别。**根据分配的测试实际要求进行调整** — 这些是起点，不是规则。

作为粗略的经验法则：~25 步用于几个有针对性的检查，~40 步用于包含功能性 + 对抗性 + a11y 的全页面，~75 步用于多个页面或广泛的类别。**根据分配的测试实际要求进行调整** — 这些是起点，不是规则。

每个子代理提示必须包含：
```
你有 N 个浏览步骤的预算（每个 `browse` 命令 = 1 步）。逐步计算你的步骤。当你达到 N 时，立即停止并报告：
- 对于你完成的每个测试：`STEP_PASS|<step-id>|<证据>`
- 对于你没有完成的每个测试：`STEP_SKIP|<test-id>|预算达到`

不要重试或继续执行预算后。
仅运行这些测试：[来自合并计划的编号列表]
不要超出分配的测试范围进行探索。
不要生成 HTML 报告或写入任何文件。仅以文本形式返回步骤标记和你的发现。
```

主要代理不应自己运行 `browse` 命令（除了验证开发服务器是否正常）。所有测试都在子代理中发生。

**当子代理达到其预算时，主要代理接受部分结果。** 不要重新运行或重试子代理。在最终报告中包含 SKIPPED 测试，以便开发者知道哪些内容未涵盖。

### 报告

**每个子代理都使用以下方式报告：**
```
测试：8 | 通过：5 | 失败：2 | 跳过：1 | 访问的页面：2
```

**主要代理合并为最终报告：**
```
测试：20 | 通过：14 | 失败：4 | 跳过：2 | 代理：3 | 通过率：70%
```

不要报告“使用的步骤” — 浏览命令计数是实施管道，而不是对审阅者有意义的指标。

## 测试理念

**你是一个对抗性测试者。** 你的目标是找到错误，而不是证明正确性。

- **尝试破坏你测试的每个功能。** 不要只是检查“按钮是否存在？” — 快速点击两次，提交空表单，粘贴 500 个字符，在流程中途按 Esc。
- **测试开发者未考虑的内容。** 空状态，错误恢复，仅键盘导航，移动溢出。
- **每个断言都必须基于证据。** 比较前后快照。通过引用检查特定元素。在没有来自可访问性树或确定性检查的具体证据的情况下，永远不要报告 PASS。
- **使用足够的详细信息报告失败，以便可以重现。** 包括确切的操作，你预期的结果，你得到的结果，以及建议的修复。

## 断言协议

每个测试步骤必须产生一个结构化的断言。不要写自由形式的“看起来不错。”

### 步骤标记

对于每个测试步骤，发出一个标记：

```
STEP_PASS|<step-id>|<证据>
```
或
```
STEP_FAIL|<step-id>|<预期> → <实际>|<截图路径>
```

- `step-id`：简短标识符，如 `homepage-cta`，`form-validation-error`，`modal-cancel`
- `证据`：证明步骤通过时你观察到的内容（元素引用，文本内容，URL，评估结果）
- `预期 → 实际`：你预期的结果与实际结果
- `截图路径`：保存截图的路径（仅失败 — 见下文截图捕获）

### 失败的截图捕获

**每个 STEP_FAIL 必须附带一个截图**，以便开发者可以直观地看到出了什么问题。

当测试步骤失败时：

```bash
# 1. 观察到失败后立即拍摄截图
browse screenshot --path .context/ui-test-screenshots/<step-id>.png

# 如果 --path 不受支持，手动拍摄截图：
browse screenshot
# 浏览器 CLI 将输出截图路径 — 移动/复制：
cp /tmp/browse-screenshot-*.png .context/ui-test-screenshots/<step-id>.png
```

在测试运行开始时设置截图目录：

```bash
mkdir -p .context/ui-test-screenshots
```

**规则：**
- 文件名 = 步骤 ID（例如，`double-submit.png`，`axe-audit.png`，`modal-focus-trap.png`）
- 存储在 `.context/ui-test-screenshots/` — 此目录被 git 忽略，并且对开发者和其他代理可访问
- 对于并行运行，包含会话名称：`<会话>-<step-id>.png`（例如，`signup-double-submit.png`）
- 在失败时刻拍摄截图 — 捕获损坏状态，而不是恢复后
- 对于视觉/布局错误，也拍摄基线（工作状态）截图以进行比较：`<step-id>-baseline.png`

### 验证方法（按严格程度排序）

1. **确定性检查**（最强）— `browse eval` 返回你可以检查的结构化数据。示例：axe-core 违规计数，`document.title`，表单字段值，控制台错误数组。
2. **截图元素匹配** — 具有特定角色和文本的特定元素存在于可访问性树中。通过引用检查：`@0-12 button "Save"`。元素要么存在于树中，要么不存在。
3. **前后比较** — 在操作之前拍摄快照，操作，操作后拍摄快照。验证树按预期方式更改（元素出现，消失，文本更改）。
4. **截图 + 视觉判断**（最弱）— 仅用于无法捕获的可访问性树的可视化属性（颜色，间距，布局）。始终附带你正在评估的具体内容。

### 前后比较模式

这是核心验证循环。对每个交互使用它：

```bash
# 1. 前提：捕获状态
browse snapshot
# 记录当前状态：元素，引用，文本

# 2. 操作：执行交互
browse click @0-ref
# 或：browse fill "selector" "value"
# 或：browse type "text"
# 或：browse press Enter

# 3. 后续：捕获新状态
browse snapshot
# 比较与前提：发生了什么变化？

# 4. 断言：根据比较发出标记
# STEP_PASS|step-id|证据  OR  STEP_FAIL|step-id|预期 → 实际
```

## 设置

```bash
which browse || npm install -g browse
```

### 避免权限疲劳

此技能运行许多 `browse` 命令（截图，点击，evals）。为了避免逐个批准，请将 `browse` 添加到您的允许命令：

将两种模式都添加到 `.claude/settings.json`（项目级）或 `~/.claude/settings.json`（用户级）：
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

第一种模式涵盖普通的 `browse` 命令。第二种模式涵盖并行会话（`BROWSE_SESSION=signup browse open ...`）。两者都需要以避免批准提示。

## 模式选择

| 目标 | 模式 | 命令 | 认证 |
|------|------|------|------|
| `localhost` / `127.0.0.1` | 本地 | `browse open <url> --local` | 无需认证（默认情况下干净隔离的本地浏览器） |
| 部署/预发布站点 | 远程 | `browse open <url> --remote` | Browserbase 凭据；在支持的地方使用上下文 |

**规则：如果目标 URL 包含 `localhost` 或 `127.0.0.1`，则在第一个 `browse open` 中传递 `--local`。**

### 本地模式（localhost 的默认值）

```bash
browse open http://localhost:3000 --local
```

`browse open ... --local` 默认使用干净的隔离本地浏览器，这对于可重复的 localhost QA 运行最佳。

仅在需要时使用本地模式变体：

- `browse open <url> --auto-connect` — 自动发现现有的可调试本地 Chrome。仅在测试明确需要现有的本地登录/cookies/状态时使用此选项。
- `browse open <url> --cdp <端口|url>` — 连接到特定的 CDP 目标（显式本地浏览器连接）。

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

Cookie 同步标志：`--domains`，`--context`，`--verified`，`--proxy "City,ST,US"`

## 工作流程 A：差异驱动测试

### 第一阶段：分析差异

```bash
git diff --name-only HEAD~1          # 或：git diff --name-only / git diff --name-only main...HEAD
git diff HEAD~1 -- <file>            # 读取实际更改
```

对已更改的文件进行分类：

| 文件模式 | UI 影响 | 要测试的内容 |
|-------------|-----------|--------------|
| `*.tsx`, `*.jsx`, `*.vue`, `*.svelte` | 组件 | 渲染，交互，状态，边缘情况 |
| `pages/**`, `app/**`, `src/routes/**` | 路由/页面 | 导航，页面加载，内容，404 处理 |
| `*.css`, `*.scss`, `*.module.css` | 样式 | 视觉外观（截图），响应式 |
| `*form*`, `*input*`, `*field*` | 表单 | 验证，提交，空输入，长输入，特殊字符 |
| `*modal*`, `*dialog*`, `*dropdown*` | 交互式 | 打开/关闭，Esc，焦点陷阱，取消 vs 确认 |
| `*nav*`, `*menu*`, `*header*` | 导航 | 链接，活动状态，路由，键盘导航 |
| 仅 UI 文件 | 无 | 跳过 — 报告“无需 UI 测试” |

### 第二阶段：将文件映射到 URL

检测框架：`cat package.json | grep -E '"(next|react|vue|nuxt|svelte|@sveltejs|angular|vite)"'`

| 框架 | 默认端口 | 文件 → URL 模式 |
|-----------|-------------|-----|
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

# 如果它不是 PR 分支，切换到它
git fetch origin <branch> && git checkout <branch>

# 安装依赖 — 锁文件可能在分支之间不同
yarn install  # 或 npm install / pnpm install
```

如果开发服务器已经在不同的分支上运行，在签出后重新启动它。

**查找正在运行的开发服务器：**
```bash
for port in 3000 3001 5173 4200 8080 8000 5000; do
  s=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" 2>/dev/null)
  if [ "$s" != "000" ]; then echo "开发服务器在端口 $port (HTTP $s)"; fi
done
```

如果没有找到：告诉用户启动他们的开发服务器。

**验证它实际上可以渲染：**
在 `browse open` + `browse snapshot` 后，检查可访问性树是否包含真实的页面内容（导航，标题，交互元素） — 而不是错误覆盖或空的正文。Next.js 开发服务器可以返回 HTTP 200，同时显示全屏构建错误对话框。如果快照为空或由错误对话框主导，则服务器已损坏 — 在测试之前修复构建。

### 第四阶段：生成测试计划

对于每个更改区域，规划**既快乐路径又对抗性测试**：

```
测试计划（基于 git diff）
=============================
更改：src/components/SignupForm.tsx（添加了电子邮件验证）

1. [快乐] 有效电子邮件成功提交
   URL: http://localhost:3000/signup
   步骤：填写有效电子邮件 → 提交 → 验证成功消息出现

2. [对抗性] 无效电子邮件显示错误
   步骤：填写 "not-an-email" → 提交 → 验证错误消息出现

3. [对抗性] 空表单提交
   步骤：不填写任何内容就点击提交 → 验证错误，没有崩溃

4. [对抗性] 电子邮件字段的 XSS
   步骤：填写 "<script>alert(1)</script>" → 提交 → 验证清理/拒绝

5. [对抗性] 快速双提交
   步骤：快速点击两次提交 → 验证没有重复提交

6. [对抗性] 仅键盘流程
   步骤：Tab 到电子邮件 → 输入 → Tab 到提交 → Enter → 验证成功
```

### 第五阶段：执行测试

```bash
browse stop 2>/dev/null
mkdir -p .context/ui-test-screenshots
# 本地/默认 QA → 干净，可重复的本地运行
browse open http://localhost:3000 --local
```

对于每个测试，按照 **前后模式** 执行：

```bash
# 导航
browse open http://localhost:3000/path --local
browse wait load

# 前提快照
browse snapshot
# 记录当前状态：元素，引用，文本

# 操作
browse click @0-ref
# 或: browse fill "selector" "value"
# 或: browse type "text"
# 或: browse press Enter

# 后续快照
browse snapshot
# 与前提比较：发生了什么变化?

# 断言：根据比较发出标记
# STEP_PASS|step-id|证据  OR  STEP_FAIL|step-id|预期 → 实际
```

### 第六阶段：报告结果

```
## UI 测试结果

### STEP_PASS|valid-email-submit|status "Thanks!" appeared at @0-42 after submit
- URL: http://localhost:3000/signup
- 前提：表单带有电子邮件输入 @0-3，提交按钮 @0-7
- 操作：填写 "user@test.com", 点击 @0-7
- 后续：表单被替换为状态元素，显示 "Thanks! 我们会联系。"

### STEP_FAIL|double-submit|expected single submission → form submitted twice|.context/ui-test-screenshots/double-submit.png
- URL: http://localhost:3000/signup
- 前提：表单带有提交按钮 @0-7
- 操作：快速点击 @0-7 两次
- 后续：出现两个成功提示，表明重复提交
- 截图：.context/ui-test-screenshots/double-submit.png
- 建议：在第一次点击后禁用提交按钮，或者处理处理程序

---
**总结：4/6 通过，2 失败**
失败：double-submit, xss-sanitization

截图保存到 `.context/ui-test-screenshots/` — 打开任何失败的步骤的截图以查看损坏状态。
```

完成时始终 `browse stop`。

### 第七阶段：生成 HTML 报告

在生成文本报告后，生成一个独立的 HTML 报告，审阅者可以在浏览器中打开它。报告嵌入截图（base64），因此它作为一个文件工作 — 没有外部依赖。

**原因：** 文本报告适合代理对话，但审阅者（产品经理，设计师，其他工程师）想要一个他们可以打开，扫描和共享的视觉工件。嵌入的截图使失败立即显而易见。

#### 如何生成

1. 读取 HTML 模板在 [参考资料/report-template.html](references/report-template.html)
2. 通过替换模板占位符为实际测试数据构建报告：

| 占位符 | 值 |
|-------------|-------|
| `{{TITLE}}` | 报告标题用于 `<title>` 标签（例如，"UI 测试：PR #1234 — OAuth 设置”） |
| `{{TITLE_HTML}}` | 可见 `<h1>` 的报告标题。如果提供 PR URL，请将 PR 引用包装在 `<a>` 标签中使其可点击（例如，`UI 测试: <a href="https://github.com/org/repo/pull/1234">PR #1234</a> — OAuth 设置`）。如果没有 URL，请使用与 `{{TITLE}}` 相同的纯文本。 |
| `{{META}}` | 一行上下文：日期，应用程序 URL，用户，分支 |
| `{{TOTAL_TESTS}}` | STEP_PASS + STEP_FAIL 计数总和 |
| `{{AGENT_COUNT}}` | 运行的子代理数量 |
| `{{PASS_COUNT}}` | STEP_PASS 数量 |
| `{{FAIL_COUNT}}` | STEP_FAIL 数量 |
| `{{PASS_RATE}}` | 整数百分比（例如，"92"） |
| `{{RATE_CLASS}}` | `good`（≥90%），`warn`（70–89%），`bad`（<70%） |
| `{{FAILURES_SECTION}}` | 失败测试卡的 HTML（见下文） |
| `{{PASSES_SECTION}}` | 通过测试卡的 HTML |

对于每个测试结果，生成一个 `<details>` 卡。失败测试卡应**默认打开**，以便审阅者立即看到它们：

```html
<!-- 失败测试卡（默认打开） -->
<div class="section">
  <h2>失败 <span class="count">{{FAIL_COUNT}}</span></h2>
  <details class="test-card fail" open>
    <summary>
      <span class="badge fail">失败</span>
      <span class="step-id">step-id-here</span>
      <span class="evidence">expected → actual</span>
    </summary>
    <div class="body">
      <dl>
        <dt>URL</dt><dd>http://localhost:3000/path</dd>
        <dt>操作</dt><dd>做了什么</dd>
        <dt>预期</dt><dd>应该发生什么</dd>
        <dt>实际</dt><dd>实际发生了什么</dd>
      </dl>
      <div class="suggestion">修复：描述建议的修复</div>
      <div class="screenshot">
        <img src="data:image/png;base64,..." alt="失败截图">
        <div class="caption">step-id.png — 在失败时刻捕获</div>
      </div>
    </div>
  </details>
</div>

<!-- 通过测试卡（默认折叠） -->
<div class="section">
  <h2>通过 <span class="count">{{PASS_COUNT}}</span></h2>
  <details class="test-card pass">
    <summary>
      <span class="badge pass">通过</span>
      <span class="step-id">step-id-here</span>
      <span class="evidence">证据摘要</span>
    </summary>
    <div class to be translated
