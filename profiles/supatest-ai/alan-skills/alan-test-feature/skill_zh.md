## 任务：测试功能并生成演示报告

分析当前分支的变更，与用户确定覆盖范围级别，制定明确的测试策略，启动应用的开发服务器，使用 `agent-browser` 在真实浏览器中测试功能，捕获截图和视频（**始终——无一例外**），将所有内容上传到 S3，并生成结构化的测试报告（**始终——绝不跳过**）。

---

## 第 0 阶段：环境设置

### 1. 获取工件上下文 ID

在提示中存在活动任务上下文时，使用该上下文。否则：

- 任务 ID 可从 `ALAN_TASK_ID` 环境变量获取。
- 对话 ID 可从 `ALAN_SESSION_ID` 环境变量获取。
- 在创建报告之前，使用 Alan MCP 上下文/工具解析 `teamId`。

调用 `create_test_report` 时，始终显式传递 `taskId`、`conversationId` 和 `teamId`。不要用一个 ID 替换另一个 ID。

### 2. 验证 agent-browser 是否可用

`agent-browser` 是 Vercel Labs 的一个 **命令行工具**（`npm: agent-browser`）——它**不是**技能或 MCP 工具。它通过 bash 命令提供无头浏览器自动化（打开、点击、填充、截图、录制）。在沙盒中，它由 `runtime-bootstrap.ts` 预装。

```bash
command -v agent-browser >/dev/null 2>&1 && echo "agent-browser: OK" || echo "agent-browser: MISSING"
```

**如果缺失**，则安装它：
```bash
npm install -g agent-browser && agent-browser install
```

如果安装失败（例如，无网络、无 npm），**停止**并告知用户：
> "agent-browser 不可用且无法安装。手动安装：`npm install -g agent-browser && agent-browser install`"

在没有可用的 `agent-browser` 之前**不要**进入第 2 阶段——所有浏览器测试都依赖于它。

### 3. 创建工作区

所有捕获（截图、视频）**必须**写入 `/tmp/alan-captures/`。

```bash
mkdir -p /tmp/alan-captures
```

> **关键——文件路径规则：**
> - **仅**将捕获文件写入 `/tmp/alan-captures/`。绝不能写入其他地方。
> - **绝不**写入 `.claude/`、项目目录、`reports/` 或仓库内的任何路径。
> - `.claude/` 是一个敏感的系统目录——写入它将被阻止并中止测试运行。
> - 如果你打算在其他地方（除 `/tmp/` 之外）创建 `reports/` 或 `screenshots/` 文件夹，停止并使用 `/tmp/alan-captures/`。

---

## 第 0.5 阶段：覆盖范围确定与上下文收集（强制执行——在任何其他操作之前必须执行）

**绝不跳过此阶段。** 你必须在编写任何测试步骤之前了解用户的需求。

### 1. 询问覆盖范围级别

使用 `AskUserQuestion` 向用户询问：

```
您希望为这个功能实现什么级别的测试覆盖？

- 轻量级       — 仅测试成功路径。快速冒烟测试以验证主流程是否正常工作。
- 标准级      — 成功路径 + 关键边界情况 + 基本错误状态。（默认）
- 全面级      — 完全覆盖：成功路径、所有边界情况、错误状态、非成功路径、边界值、可访问性、响应性。

另外：您是否有任何特定的流程、已知错误或高风险区域需要我重点关注？
```

在继续之前等待响应。

### 2. 询问有针对性的后续问题

根据功能（你可能还不知道——先快速执行 `git diff --stat` 获取提示），使用 `AskUserQuestion` 询问 1–3 个有针对性的后续问题。示例：

- "我应该测试认证状态吗？如果是，我应该使用什么测试凭证？"
- "这个功能有任何已知的边界情况或相关前错误吗？"
- "这个功能的“正常工作”定义是什么——我应该看到什么？"
- "您是否有任何特定的非成功路径（例如，无效输入、网络错误、空状态）您担心？"
- "是否有任何特定页面或用户角色我应该包含或排除？"

**如果上下文不明确，不要跳过问题。要问。一个范围明确的测试比盲目测试有价值 10 倍。**

### 3. 确认计划

收集答案后，向用户总结（无需工具调用——只需简短消息）：
- 选择的覆盖范围级别
- 要重点关注的特定区域/流程
- 任何已知的风险或边界情况
- 预计的测试场景数量

只有在确认后才能进入第 1 阶段。

---

## 第 1 阶段：发现要测试的内容

### 1. 分析分支

运行以下命令以了解发生了什么变更：

```bash
git log main..HEAD --oneline 2>/dev/null || git log HEAD~5..HEAD --oneline
git diff main...HEAD --stat 2>/dev/null || git diff HEAD~1 --stat
```

阅读实际的 diff 以了解功能或错误修复。识别：
- 受影响的应用部分（哪些页面、组件、API 路由）
- 预期行为变化是什么
- 测试时导航到的 URL 路径是什么

### 2. 发现并启动开发服务器

查看项目以确定如何运行它：

1. 读取 `package.json` — 检查 `scripts.dev`、`scripts.start`、`scripts.serve`
2. 检查 `docker-compose.yml` / `docker-compose.yaml` / `compose.yml`
3. 检查 `Makefile`（查找 `dev` 或 `serve` 目标）
4. 检查 `Procfile`、`.env`、`Pipfile`、`requirements.txt`、`Gemfile`
5. 检查框架特定文件：`next.config.*`、`vite.config.*`、`nuxt.config.*`、`angular.json`、`manage.py`、`config/routes.rb`

在后台启动开发服务器。常见模式：
```bash
# Node.js
npm run dev &
# 或: pnpm dev &, yarn dev &, npx next dev &, npx vite &

# Python
python manage.py runserver &
# 或: flask run &, uvicorn main:app &

# Ruby
bundle exec rails server &

# Docker
docker compose up -d
```

### 3. 等待服务器启动

轮询直到服务器响应：
```bash
# 将 PORT 替换为发现的端口
for i in $(seq 1 30); do
  curl -sf http://localhost:PORT >/dev/null 2>&1 && break
  sleep 2
done
```

如果不清楚，检查常见端口：3000、5173、8080、4200、8000、4000、3001、8888。

### 4. 确定应用 URL

- 解析开发服务器 stdout/stderr 中的 "Local:" 或 "ready on" 带有 URL 的消息
- 检查 `.env` 或 `.env.local` 中的 `PORT` 或 `VITE_PORT` 或类似项
- 使用 `curl -sf http://localhost:PORT >/dev/null` 测试常见端口
- 如果无法确定，通过 `AskUserQuestion` 询问用户

### 5. 在继续之前总结

告知用户：
- 你在 diff 中发现的内容（功能/修复摘要）
- 你将要测试的 URL
- 你计划覆盖的测试场景

---

## 第 1.5 阶段：构建测试策略并创建待办事项（强制执行）

在打开浏览器之前，你必须有一个明确的计划。不要在即兴测试步骤。

### 1. 起草测试策略

根据：
- 用户在第 0.5 阶段选择的覆盖范围级别
- 第 1 阶段的 diff 分析
- 从用户收集的上下文

将完整的测试计划作为结构化列表写出来。对于每个场景，注意：
- **场景名称** — 短标签（例如 "成功路径：创建项目"）
- **类型** — 成功路径 / 非成功路径 / 边界情况 / 错误状态 / 视觉 / 导航
- **步骤** — 要做什么
- **预期结果** — "通过"看起来像什么
- **需要截图** — 是/否

不同级别的覆盖要求：
- **轻量级**：仅成功路径（1–3 个场景）
- **标准级**：成功路径 + 2–4 个非成功路径 + 1–2 个错误状态
- **全面级**：成功路径 + 所有非成功路径 + 所有错误状态 + 边界值 + 空状态 + 响应性 + 导航

**非成功路径示例供考虑：**
- 无效/缺少必填输入
- 提交时无数据/空状态
- 重复条目（如果适用）
- 权限拒绝/未授权访问
- 网络错误/API 失败模拟（如果可测试）
- 快速重复操作（双击、重复提交）
- 长输入字符串/特殊字符
- 返回按钮/浏览器中途导航

### 2. 为每个场景创建待办事项

使用 `TodoWrite` 为每个测试场景创建一个待办事项条目，以便跟踪进度。每个待办事项应该是场景名称。

### 3. 展示策略

在继续之前输出完整的测试策略作为编号列表。用户应该能够看到将要测试的确切内容，在第 2 阶段开始之前。

---

## 第 2 阶段：使用 agent-browser 进行测试

> `agent-browser` 是一个命令行工具——通过 bash 调用它，而不是作为 MCP 工具或技能。
> 文档：https://github.com/vercel-labs/agent-browser
> 关键命令：`open`、`snapshot`、`click`、`fill`、`screenshot`、`record`、`wait`、`find`、`close`

### 1. 打开应用

```bash
agent-browser --session test-feature open http://localhost:PORT
agent-browser --session test-feature wait --load networkidle
```

### 2. 开始视频录制——强制执行

**始终在任何交互之前开始视频录制。无一例外。**

```bash
agent-browser --session test-feature record start /tmp/alan-captures/happy-path.webm
```

如果由于技术原因视频录制失败，请记录失败但继续——截图仍然是必需的。

### 3. 拍摄初始截图——强制执行

**始终在任何交互之前捕获初始页面状态。**

```bash
agent-browser --session test-feature screenshot /tmp/alan-captures/step-00-initial-state.png
```

### 4. 执行测试策略中的每个场景

逐个处理第 1.5 阶段定义的每个场景。对于每个场景：

- 将相应的待办事项标记为进行中
- 使用 `agent-browser snapshot -i` 发现交互元素
- 使用 `agent-browser click @eN`、`agent-browser fill @eN "text"` 等进行交互
- 使用 `agent-browser wait --load networkidle` 或 `agent-browser wait 1500` 在操作之间等待
- **在每次重要状态变化后拍摄截图**——不要超过 2 个有意义的操作没有截图：
  ```bash
  agent-browser --session test-feature screenshot /tmp/alan-captures/step-NN-description.png
  ```
  描述性命名截图：`step-02-form-filled.png`、`step-03-submit-clicked.png`、`step-04-success-state.png`
- 在导航或 DOM 变更后重新拍摄快照（引用会过期）
- 如果元素难以通过引用找到，使用语义定位器：
  ```bash
  agent-browser --session test-feature find text "Submit" click
  agent-browser --session test-feature find role button click --name "Save"
  ```
- 根据结果将每个待办事项标记为完成或失败

**强制执行覆盖清单（根据选择的覆盖范围级别执行所有适用项）：**

**成功路径（始终需要）：**
- [ ] 主要功能流程按预期端到端工作
- [ ] 成功状态/确认可见
- [ ] 数据被持久化/正确反映在操作后

**非成功路径（标准级 + 全面级需要）：**
- [ ] 空/缺少必填输入——表单验证触发，显示错误消息
- [ ] 无效输入值——正确拒绝，不会崩溃
- [ ] 边界值——最小和最大接受的值
- [ ] 重复/冲突数据（如果适用）
- [ ] 未授权/权限拒绝状态（如果适用）
- [ ] 空列表/零状态视图（如果适用）
- [ ] 快速重复操作（双击提交、重复点击按钮）
- [ ] 长字符串/特殊字符在文本输入中

**错误状态（标准级 + 全面级需要）：**
- [ ] API / 网络失败行为（如果可模拟）
- [ ] 部分失败——如果只有部分操作成功会发生什么
- [ ] 平滑降级——应用不会崩溃，用户会看到有意义的消息

**视觉与导航（全面级需要）：**
- [ ] 布局正确，没有溢出或损坏的 UI
- [ ] 在较窄视口上响应（如果可能，调整大小）
- [ ] 链接和导航正常工作；后退按钮不会破坏状态
- [ ] 加载状态/旋转器在异步工作正在进行时显示

### 5. 停止录制并清理

```bash
agent-browser --session test-feature record stop
agent-browser --session test-feature screenshot /tmp/alan-captures/final-state.png
agent-browser --session test-feature close
```

**保持录制时间少于 2 分钟。** 如果功能需要更多探索，分成多个录制（例如 `happy-path.webm`、`error-states.webm`）。

### 6. 修复 WebM 时长元数据（如果 ffmpeg 可用，强制执行）

agent-browser 录制的 WebM 文件在容器头部通常有 `duration = Infinity`——视频播放器显示 0:00。通过 ffmpeg 将每个 `.webm` 文件重新封装，ffmpeg 读取整个文件，计算实际时长，并将其写入输出头部来修复它：

```bash
for f in /tmp/alan-captures/*.webm; do
  if command -v ffmpeg >/dev/null 2>&1; then
    ffmpeg -y -i "$f" -c copy "${f%.webm}-fixed.webm" 2>/dev/null \
      && mv "${f%.webm}-fixed.webm" "$f" \
      || echo "ffmpeg remux failed for $f — uploading as-is"
  fi
done
```

如果 ffmpeg 不可用，跳过此步骤并继续——视频仍然可以播放，它只是不会在播放器中显示正确的时长。

---

## 第 3 阶段：将捕获内容上传到 S3

对于每个捕获的文件，使用 `mcp__alan__get_upload_url` MCP 工具获取预签名 S3 URL，然后直接使用 `curl PUT` 将文件上传到 S3。

### 每个文件的上传流程

1. **获取文件大小**（MCP 工具需要）：
   ```bash
   SIZE=$(stat -c%s "/tmp/alan-captures/step-01.png" 2>/dev/null || stat -f%z "/tmp/alan-captures/step-01.png")
   ```

2. **调用 MCP 工具** 获取预签名上传 URL：
   ```
   工具：mcp__alan__get_upload_url
   参数：{
     "taskId": "<活动任务 ID 或 ALAN_TASK_ID 的值>",
     "filename": "step-01.png",
     "mimeType": "image/png",
     "size": <来自步骤 1 的 SIZE>
   }
   ```
   返回：`{ "uploadUrl": "https://...", "s3Key": "sandbox-captures/..." }`

3. **使用预签名 URL 上传文件** 到 S3：
   ```bash
   curl -sf -X PUT "<uploadUrl>" \
     -H "Content-Type: image/png" \
     --data-binary @/tmp/alan-captures/step-01.png
   ```

4. **保存 `s3Key`** —— 你将在第 4 阶段将 `s3Key` 传递给 `create_test_report`。

对每个截图和视频文件重复。常见 MIME 类型：
- 截图：`image/png`
- 视频录制：`video/webm`

**如果上传失败**：继续到第 4 阶段——省略 `screenshotUrl`、`videoUrl` 和 `screenshotUrls`。没有媒体的结构化报告仍然很有价值。

---

## 第 4 阶段：创建结构化测试报告（强制执行——绝不跳过）

**关键：你必须调用 `mcp__alan__create_test_report` 来完成此技能。这是非协商的。**

- 不要将报告作为 markdown 文本输出
- 不要仅在聊天中总结发现
- 不要因为任何原因跳过此阶段——不是因为时间，不是因为上传失败，不是因为测试不完整
- 报告必须通过此 MCP 工具调用持久化，以便 UI 将其作为交互式工件显示
- **跳过此步骤意味着整个测试会话被浪费且无法跟踪**

如果在第 3 阶段上传失败，仍然创建报告——省略媒体 URL 但包含所有步骤、问题和摘要文本。

使用从之前阶段收集的结构化数据调用 `mcp__alan__create_test_report` 工具。

收集所有数据并调用工具：

```
工具：mcp__alan__create_test_report
参数：{
  "title": "<要测试内容的简短描述>",
  "taskId": "<活动任务 ID 或 ALAN_TASK_ID 的值，如果设置>",
  "conversationId": "<活动对话 ID 或 ALAN_SESSION_ID 的值>",
  "teamId": "<解析的 team ID>",
  "branch": "<git 当前分支名称>",
  "baseBranch": "main",
  "commits": [
    { "sha": "<提交 SHA>", "message": "<提交消息>" }
  ],
  "changedFiles": [
    { "path": "src/components/Feature.tsx", "description": "添加了新的功能组件" }
  ],
  "appUrl": "<你测试的 URL>",
  "summary": "<1-2 段关于测试内容和结果的摘要>",
  "status": "pass | fail | mixed",
  "steps": [
    {
      "name": "导航到功能页面",
      "status": "pass | fail | skip",
      "screenshotUrl": "<来自第 3 阶段的 s3Key — 例如 sandbox-captures/org/task/step-01.png — 如果上传失败则省略>",
      "notes": "页面加载正确"
    }
  ],
  "issues": [
    {
      "title": "按钮在移动设备上未对齐",
      "severity": "critical | high | medium | low",
      "description": "提交按钮在视口 < 375px 时溢出",
      "screenshotUrl": "<来自第 3 阶段显示问题的 s3Key — 如果上传失败则省略>"
    }
  ],
  "videoUrl": "<来自第 3 阶段的 happy-path 录制 s3Key — 如果上传失败则省略>",
  "screenshotUrls": ["<来自第 3 阶段的 s3Key 1>", "<来自第 3 阶段的 s3Key 2>"]
}
```

### 字段指南

- **status**：如果所有步骤通过则为 "pass"，如果任何关键步骤失败则为 "fail"，如果有些通过有些失败则为 "mixed"
- **steps**：每个独立测试动作（导航、点击、填充、验证）一个条目。如果为该步骤拍摄了截图，请包含截图 URL。
- **issues**：仅包含实际发现的问题。每个问题应有关键性和清晰的描述。
- **screenshotUrls**：所有截图 s3Keys 的扁平列表（用于画廊显示）。使用 `get_upload_url` 返回的 `s3Key`，**不要**使用 `uploadUrl`。如果上传失败则省略。
- **commits** 和 **changedFiles**：来自第 1 阶段的 git 分析

### 输出

调用 `mcp__alan__create_test_report` 后，告知用户：
- 测试报告标题，以便用户可以在 Alan UI 中找到生成的工件
- 当你拥有足够上下文形成链接时（通常 `/teams/<teamId>/docs?artifactId=<artifactId>`）的链接
- 简要摘要：测试了什么，通过了多少步骤/失败了多少步骤，发现了任何问题
- 列出在测试过程中发现的任何错误或关注点

不要以原始 UUID 开头。如果无法形成可用的标题或链接，则仅包含工件/报告 ID 作为次要调试上下文。
