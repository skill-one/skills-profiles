# 模拟会话并分析差异

本技能涵盖单个模拟运行和结果解释。有关 `simulate` 命令的完整选项参考，请参阅 `meticulous-cli` 技能的 [`simulate` 参考](../meticulous-cli/references/simulate.md)。

> 开始之前，运行 `meticulous-cli-update` 技能以确保 Meticulous CLI 和技能保持最新——除非它已经在此对话中更早运行过，在这种情况下可以跳过。

## 前置条件

- 一个 `sessionId` 用于回放
- 一个 `appUrl`（本地开发服务器，或留空使用原始录制的 URL）
- 可选：一个 `baseReplayId`——先前回放（用于与屏幕截图进行比较的 ID）。如果没有此 ID，屏幕截图将被存储但不会进行比较。

如果您没有 `baseReplayId`，可以从下载的测试运行中找到：

```bash
meticulous download test-run
# 然后检查 ~/.meticulous/test-runs/<testRunId>/coverage.json
# 或检查 testCases[].replayId 字段
```

## 第 1 步——运行模拟

### 使用基础回放（差异模式）

```bash
meticulous simulate \
  --sessionId=<sessionId> \
  --appUrl=<url> \
  --baseReplayId=<baseReplayId> \
  --headless
```

捕获完整的 stdout。关键信息如下：

```
# 每个屏幕截图的差异结果（每行一个）：
0.412% 像素不匹配的屏幕截图 screenshot-1234.png（阈值为 0.100%）=> 失败！
0.000% 像素不匹配的屏幕截图 screenshot-5678.png（阈值为 0.100%）=> 通过

# 最终摘要块：
=======
查看模拟：https://app.meticulous.ai/projects/<org>/<project>/simulations/<headReplayId>
查看与基础比较：https://app.meticulous.ai/projects/<org>/<project>/simulations/<baseReplayId>/compare-to/<headReplayId>
=======
```

**如果没有 `失败！` 行：** 会话在视觉上与基础相同——报告没有回归，然后继续第 6 步。

继续第 2-6 步以定位和分析任何差异，然后提交反馈。

### 不使用基础回放（快速检查模式）

如果没有 `baseReplayId`，则省略它。屏幕截图仍然会本地存储以供直接视觉检查：

```bash
meticulous simulate \
  --sessionId=<sessionId> \
  --appUrl=<url> \
  --headless
```

然后定位回放目录（第 2 步），并在 `<replayDir>/screenshots/` 中打开屏幕截图以验证 UI 是否正确。在此模式下没有差异图像——检查完全是视觉的。第 3-5 步不适用；检查后仍需完成第 6 步。

## 第 2 步——提取头部回放 ID 并定位回放目录

从 `查看模拟：` URL 中提取 `<headReplayId>`（最后一个路径段）。

要找到此运行创建的本地回放目录：

```bash
ls -lt ~/.meticulous/replays/ | head -5
```

最新创建的条目将是头部回放目录（以时间戳命名，例如 `2024-01-15T12-30-45.123Z-abc123/`）。记下此路径——它将在下面称为 `<replayDir>`。

## 第 3 步——识别哪些屏幕截图发生了差异

```bash
ls ~/.meticulous/replays/<replayDir>/diffs/<baseReplayId>/
```

这里的每个 `.png` 文件对应于检测到视觉差异的屏幕截图。像素差异图像以颜色突出显示更改的像素。还有 `thumb_` 前缀的缩略版本。

记下文件名——它们与屏幕截图标识符匹配（例如 `screenshot-after-event-42.png`）。

## 第 4 步——分析每个发生差异的屏幕截图的 HTML 差异

每个屏幕截图都有一个相应的元数据文件，其中包含在捕获屏幕截图之前页面完整 HTML 快照。这些文件已经保存在磁盘上：

- **头部元数据：** `~/.meticulous/replays/<replayDir>/screenshots/<screenshotFilename>.metadata.json`
- **基础元数据：** `~/.meticulous/replays/<baseReplayId>/screenshots/<screenshotFilename>.metadata.json`

基础元数据在模拟下载基础回放时永久缓存，因此无需额外下载。

读取两个 `.metadata.json` 文件。相关字段是：

- `before.dom` — 屏幕截图时间的页面完整 HTML；比较这两个字符串以了解发生了什么变化
- `before.routeData.url` — 屏幕截图是在哪个页面/路由上捕获的

比较 HTML 时，关注标签的添加/删除、`class` 属性的变化和文本内容的变化。

每行屏幕截图的 stdout 也报告 `mismatchFraction`（更改像素的比例）。如果有像素差异但 `before.dom` 字符串相同，则更改是纯视觉的（例如颜色偏移），而不是结构的。

## 第 5 步——总结发现

本技能的关键输出是**高级人类可读的描述，说明视觉上发生了什么变化以及为什么**。使用上述像素差异计数、路由 URL、更改的类名和 HTML 差异来回答：_用户体验发生了什么变化，哪个 UI 部分负责？_

以适合当前上下文的格式呈现（对话答案、结构化报告、调用工作流的输入等）。有用的信号包括：

- 哪些路由受到影响
- 哪些 CSS 类出现在更改的 DOM 区域（这些通常直接映射到组件）
- 变化是否是结构的（DOM 添加/删除）或纯视觉的（像素偏移且没有 HTML 差异）
- 变化是否出现在多个屏幕截图中（表明共享组件发生了变化）还是仅限于一个屏幕截图

stdout 记录的比较 URL 值得呈现，因为它允许人类快速视觉验证差异：
`https://app.meticulous.ai/.../simulations/<baseReplayId>/compare-to/<headReplayId>`

## 注意事项

- `~/.meticulous/replays/<replayDir>/diffs/<baseReplayId>/` 中的像素差异图像可以直接打开进行视觉检查。
- 如果省略 `--baseReplayId`，则无法进行差异分析。屏幕截图仍然会本地存储，并且可以通过重新运行并将 `--baseReplayId` 设置为第一次运行的头回放 ID 来进行比较。
- 对于完整的迭代开发工作流（会话发现、每步提交和最终云端运行），请参阅 `meticulous-iterative-dev` 技能。

## 第 6 步——向 Meticulous 提交反馈

作为最后一步，在总结发现后，向 Meticulous 团队提交一条简短的反馈笔记：模拟和差异是否帮助您验证了更改，是否有任何令人困惑的地方，以及哪些信息会使任务更容易？

```bash
# CLI
meticulous agent submit-feedback --message="<一句话或两句>" --outcome=<helped|neutral|hindered> --skill=meticulous-simulate-and-diff

# MCP
submit_feedback(message="<一句话或两句>", outcome="<helped|neutral|hindered>", skill="meticulous-simulate-and-diff")
```
