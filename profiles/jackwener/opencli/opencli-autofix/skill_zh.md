# OpenCLI 自动修复 — 适配器自动自愈

当 `opencli` 命令因网站更改其 DOM、API 或响应模式而失败时，**自动诊断、修复适配器并重试** —— 不要只是报告错误。

## 安全边界

**在开始任何修复之前，检查以下硬性停止条件：**

- **`AUTH_REQUIRED`** (退出码 77) — **停止。** 不要修改代码。告诉用户在 Chrome 中登录网站。
- **`BROWSER_CONNECT`** (退出码 69) — **停止。** 不要修改代码。告诉用户运行 `opencli doctor`。
- **验证码 / 速率限制** — **停止。** 不是适配器问题。

**范围限制：**
- **仅修改 `adapterSourcePath` 处的文件**，在 `summary.md` 的前端元数据中 — 这是权威的适配器位置（可能是在仓库中的 `clis/<site>/` 或 npm 安装时的 `~/.opencli/clis/<site>/`）
- **永远不要修改** `src/`、`extension/`、`tests/`、`package.json` 或 `tsconfig.json`

**重试预算：** 每次失败最多 **3 次修复轮次**。如果 3 轮诊断 → 修复 → 重试无法解决，停止并报告尝试了什么。

## 前置条件

```bash
opencli doctor    # 验证扩展程序 + 守护进程连接性
```

## 何时使用此技能

当 `opencli <site> <command>` 因可修复的错误失败时使用：
- **SELECTOR** — 元素未找到（DOM 已更改）
- **EMPTY_RESULT** — 未返回数据（API 响应已更改）
- **API_ERROR** / **NETWORK** — 端点已移动或已损坏
- **PAGE_CHANGED** — 页面结构不再匹配
- **COMMAND_EXEC** — 适配器逻辑中的运行时错误
- **TIMEOUT** — 页面加载方式不同，适配器等待错误的事物

## 进入修复前：“空” ≠ “损坏”

`EMPTY_RESULT` — 以及有时是结构有效的 `SELECTOR` 但返回空值 — 通常**不是适配器错误**。平台在反爬虫启发式算法下主动降低结果质量，网站返回“未找到”响应并不意味着内容实际上缺失。在提交修复轮次之前排除这种情况：

- **使用替代查询或入口点重试。** 如果 `opencli xiaohongshu search "X"` 返回 0，但 `opencli xiaohongshu search "X 攻略"` 返回 20，适配器是正常的 — 平台对第一个查询进行了结果塑形。
- **在正常的 Chrome 标签中检查。** 如果数据在用户的浏览器中可见，但适配器返回为空，问题通常是认证状态、速率限制或软阻止 — 不是代码错误。修复方法是 `opencli doctor` / 重新登录，而不是编辑源代码。
- **查找软 404。** 像小红书 / 微博 / 抖音这样的网站在项目隐藏或删除时返回 HTTP 200 和空负载，而不是真实的 404。快照将看起来结构正确。几秒后重试通常可以区分“暂时隐藏”和“实际上已消失”。
- **来自搜索的“0 结果”是一个答案。** 如果适配器成功到达搜索端点，获得 HTTP 200，并且平台返回 `results: []`，这是一个有效答案 — 将其报告给用户为“此查询无匹配项”，而不是修补适配器。

只有当空/选择器缺失的结果在**重试和替代入口点中可重现**时，才进行步骤 1。否则，你正在修补一个正常工作的适配器以追逐噪音，修补后的版本将破坏下一个工作路径。

## 步骤 1：收集跟踪上下文

使用失败保留跟踪运行失败的命令：

```bash
opencli <site> <command> [args...] --trace retain-on-failure 2>trace-error.yaml
```

失败时，stderr 包含正常错误包加上一个小的 `trace` 块：

```yaml
ok: false
error:
  code: SELECTOR
  message: "Could not find element: .old-selector"
trace:
  schemaVersion: 1
  opencliVersion: "..."
  traceId: "..."
  dir: "/path/to/.opencli/profiles/default/traces/..."
  summaryPath: "/path/to/.opencli/profiles/default/traces/.../summary.md"
  receiptPath: "/path/to/.opencli/profiles/default/traces/.../receipt.json"
```

首先读取 `summaryPath`。它是面向 LLM 的入口点，并包括前端元数据：

```yaml
---
schemaVersion: 1
opencliVersion: "..."
traceId: "..."
status: failure
site: "example"
command: "example/search"
adapterSourcePath: "/path/to/clis/example/search.js"
errorCode: "SELECTOR"
errorMessage: "Could not find element: .old-selector"
---
```

工件目录包含：

```text
summary.md      # 从这里开始
receipt.json    # 机器可读的跟踪收据
trace.jsonl     # 完整的脱敏时间线
network.jsonl   # 脱敏网络事件
console.jsonl   # 脱敏控制台事件
state/          # 最终快照（当可用时）
screenshots/    # 最终截图（当可用时）
```

如果你将 stderr 重定向到文件，读取该文件并复制 `trace.summaryPath`。

不要要求用户使用旧的诊断环境变量重新运行。跟踪是修复证据路径。

## 步骤 2：分析失败

阅读跟踪摘要和适配器源代码。分类根本原因：

| 错误代码 | 可能原因 | 修复策略 |
|-----------|-------------|-----------------|
| SELECTOR | DOM 重组，类/ID 重命名 | 探索当前 DOM → 找到新选择器 |
| EMPTY_RESULT | API 响应模式已更改，或数据已移动 | 检查网络 → 找到新的响应路径 |
| API_ERROR | 端点 URL 已更改，需要新参数 | 通过网络拦截发现新 API |
| AUTH_REQUIRED | 登录流程已更改，cookie 已过期 | **停止** — 告诉用户登录，不要修改代码 |
| TIMEOUT | 页面加载方式不同，加载指示器/懒加载 | 添加/更新等待条件 |
| PAGE_CHANGED | 大型改版 | 可能需要完全重写适配器 |

**需要回答的关键问题：**
1. 适配器试图做什么？（读取位于 `adapterSourcePath` 的文件）
2. 当失败时页面看起来像什么？（读取 `summary.md`，如果需要，则读取 `state/`）
3. 发生了哪些网络请求？（读取 `summary.md` 中的 `Failed Network`，如果需要，则读取 `network.jsonl`）
4. 适配器期望与页面提供之间的差距是什么？

## 步骤 3：探索当前网站

使用 `opencli browser` 检查实时网站。**永远不要使用损坏的适配器** — 它将再次失败。

### DOM 已更改（SELECTOR 错误）

```bash
# 打开页面并检查当前 DOM
opencli browser open https://example.com/target-page && opencli browser state

# 查找与适配器意图匹配的元素
# 将快照与适配器期望进行比较
```

### API 已更改（API_ERROR、EMPTY_RESULT）

```bash
# 使用网络拦截器打开页面，然后手动触发操作
opencli browser open https://example.com/target-page && opencli browser state

# 交互以触发 API 调用
opencli browser click <N> && opencli browser network

# 通过其 body 应该具有的字段将网络请求缩小到您关心的请求
opencli browser network --filter author,text,likes

# 检查特定的 API 响应（键是默认 JSON 输出的 `key` 字段）
opencli browser network --detail <key>
```

## 步骤 4：修补适配器

从跟踪摘要前端元数据中读取 `adapterSourcePath` 处的适配器源文件并执行有针对性的修复。此路径是权威的 — 它可能在仓库中 (`clis/`) 或用户本地 (`~/.opencli/clis/`)。

使用 `Read` 工具在摘要.md 前端元数据中的确切路径上。

### 常见修复

**选择器更新：**
```typescript
// 之前：page.evaluate('document.querySelector(".old-class")...')
// 之后：  page.evaluate('document.querySelector(".new-class")...')
```

**API 端点更改：**
```typescript
// 之前：const resp = await page.evaluate(`fetch('/api/v1/old-endpoint')...`)
// 之后：  const resp = await page.evaluate(`fetch('/api/v2/new-endpoint')...`)
```

**响应模式更改：**
```typescript
// 之前：const items = data.results
// 之后：  const items = data.data.items  // API 现在嵌套在 "data" 下
```

**等待条件更新：**
```typescript
// 之前：await page.wait({ selector: '.loading-spinner', hidden: true })
// 之后：  await page.wait({ selector: '[data-loaded="true"]' })
```

### 修补规则

1. **进行最小更改** — 仅修复损坏的部分，不要重构
2. **保持相同的输出结构** — `columns` 和返回格式必须保持兼容
3. **优先使用 API 而不是 DOM 爬取** — 如果在探索中发现 JSON API，则切换到它
4. **仅使用 `@jackwener/opencli/*` 导入** — 永远不要添加第三方包导入
5. **修补后测试** — 再次运行命令以验证
6. **永远不要放宽 `verify/<cmd>.json` 固定件以消除失败。** 失败的 `patterns` / `notEmpty` / `mustNotContain` / `mustBeTruthy` 规则意味着适配器的输出已损坏。收紧适配器以使其产生正确的值；不要放宽固定件以接受损坏的值。唯一合法的编辑固定件的原因是当**网站本身**已更改形状（例如 URL 格式迁移）时 — 在这种情况下更新固定件并在 `~/.opencli/sites/<site>/notes.md` 中记录更改。否则编辑固定件是在掩盖一个沉默的正确性回归。

## 步骤 5：验证修复

```bash
# 正常运行命令
opencli <site> <command> [args...]
```

如果它仍然失败，返回步骤 1 并收集新的跟踪。你有 **3 次修复轮次**（跟踪 → 修复 → 重试）的预算。如果修复后同一错误仍然存在，尝试不同的方法。3 轮后停止并报告尝试了什么。

## 步骤 6：提交上游问题

如果重试**通过**，本地适配器已与上游脱节。提交 GitHub 问题以便修复流回 `jackwener/OpenCLI`。

**不要提交：**
- `AUTH_REQUIRED`、`BROWSER_CONNECT`、`ARGUMENT`、`CONFIG` — 环境/使用问题，不是适配器错误
- 验证码或速率限制 — 无法上游修复
- 你无法实际修复的失败（3 轮用尽）

**只有在验证本地修复后**才提交 — 重试必须首先通过。

**程序：**

1. 使用你已有的跟踪摘要准备问题内容：
   - **标题：** `[autofix] <site>/<command>: <error_code>`（例如 `[autofix] zhihu/hot: SELECTOR`）
   - **正文**（使用此模板）：

```markdown
## 摘要
OpenCLI 自动修复本地修复了此适配器，并且重试通过。

## 适配器
- 网站：`<site>`
- 命令：`<command>`
- OpenCLI 版本：`<opencli --version>`

## 原始失败
- 错误代码：`<error_code>`

~~~
<error_message>
~~~

## 本地修复摘要

~~~
<1-2 句描述你更改的内容和原因>
~~~

_Issue 由 OpenCLI 自动修复在验证本地修复后提交。_
```

2. **在提交前询问用户。** 向他们展示草稿标题和正文。只有在他们确认时才继续。

3. 如果用户批准并且 `gh auth status` 成功：

```bash
gh issue create --repo jackwener/OpenCLI \
  --title "[autofix] <site>/<command>: <error_code>" \
  --body "<上述正文>"
```

如果 `gh` 未安装或未认证，告诉用户并跳过 — 不要出错。

## 何时停止

**硬停止（不要修改代码）：**
- **AUTH_REQUIRED / BROWSER_CONNECT** — 环境问题，不是适配器错误
- **网站需要验证码** — 无法自动化
- **速率限制 / IP 阻止** — 不是适配器问题

**软停止（尝试后报告）：**
- **3 次修复轮次用尽** — 停止，报告尝试了什么和什么失败
- **功能完全移除** — 数据不再存在
- **大型改版** — 需要通过 `opencli-adapter-author` 技能完全重写适配器

在所有停止情况下，向用户清楚地传达情况，而不是进行徒劳的修补。

## 示例修复会话

```
1. 用户运行：opencli zhihu hot
   → 失败：SELECTOR "Could not find element: .HotList-item"

2. AI 运行：opencli zhihu hot --trace retain-on-failure 2>trace-error.yaml
   → 获取包含最终状态和失败操作证据的跟踪摘要

3. AI 读取摘要/状态：页面加载但使用 ".HotItem" 而不是 ".HotList-item"

4. AI 探索：opencli browser open https://www.zhihu.com/hot && opencli browser state
   → 确认新的类名 ".HotItem" 及其子项 ".HotItem-content"

5. AI 修补：编辑位于 `adapterSourcePath` 的适配器 — 将 ".HotList-item" 替换为 ".HotItem"

6. AI 验证：opencli zhihu hot
   → 成功：返回热门话题

7. AI 准备上游问题草稿，展示给用户

8. 用户批准 → AI 运行：gh issue create --repo jackwener/OpenCLI --title "[autofix] zhihu/hot: SELECTOR" --body "..."
```
