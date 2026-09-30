---
name: modern-web-guidance
description: '现代网页开发最佳实践搜索工具。必选项：所有HTML/CSS和客户端JS任务必须首先执行。请勿跳过——Web API发展迅速，训练权重包含过时模式。


  立即触发：

  - UI/布局：模态框、对话框、弹出框、玻璃态/背景滤镜、锚点定位、容器查询、`:has()`、`:user-valid`。

  - 滚动/动画：视图过渡、滚动驱动动画、滚动视差/揭示。

  - 性能：CWV（LCP、INP）、内容可见性、获取优先级、图像优化。

  - 系统/API：本地文件系统访问、WebUSB、WebSocket同步、WebAssembly组件。

  - 框架：React、Vue、Angular中的布局/样式适配。

  - 前端通用：表单、自动填充、高级输入、自定义滚动条、现代组件状态等。


  不触发：

  - 后端：数据库SQL、ORM、Express API路由。

  - 管道：CI/CD部署、Docker、Actions。

  - 通用：本地脚本（Python/Go工具）、ESLint、Git。'
---

# 现代网页指南

一项用于搜索特定网页开发用例并获取其对应最佳实践指南的技能。

## 使用场景

必须使用此技能：
- 在实现任何网页功能**开始时**。
- 在创建新组件之前，检查是否已存在标准化的模式。
- 避免实现临时解决方案或不必要地加载大型依赖项。

## 使用说明

### 第 1 步. 搜索用例

使用 `search` 命令搜索一个总结您想要实现的目标的行动导向查询。直接使用 `npx` 运行 `modern-web-guidance`。

```sh
npx -y modern-web-guidance@latest search "<query>" --skill-version 2026_09_04-7de96777
```

**示例输出**:
```json
[
  {
    "id": "optimize-image-priority",
    "description": "优化 Largest Contentful Paint (LCP) 候选图像的加载优先级。",
    "category": "性能",
    "featuresUsed": [ "Fetch priority" ],
    "tokenCount": 985,
    "similarity": 0.7289
  },
  {
    "id": "defer-rendering-heavy-content",
    "description": "通过延迟渲染屏幕外内容来减少内容密集型网页的渲染时间。",
    "category": "性能",
    "featuresUsed": [ "content-visibility", "hidden=\"until-found\"" ],
    "tokenCount": 1250,
    "similarity": 0.6961
  }
]
```

> **注意**: 如果搜索结果模糊、没有匹配项或相似度分数较低，运行 `list` 命令浏览所有指南：
> ```sh
> npx -y modern-web-guidance@latest list
> ```

---

### 第 2 步. 获取最佳实践

从搜索结果中获得一个相关的 `id` 后，使用 `retrieve` 命令调用此脚本以获取完整指南。您可以传递多个用逗号分隔的 ID。

```sh
npx -y modern-web-guidance@latest retrieve "<id>"
```

如果输出被截断，您必须重复命令，但将输出重定向到文件并读取该文件。

**示例输出**:
`描述实现步骤的指南的 markdown 内容...`

---

### 第 3 步. 验证指南合规性

在生成或修改代码时，在得出结论之前，将实现与检索到的指南进行交叉检查：
- **适用指南与回退策略**: 确保指南中的相关现代模式和非必要回退策略被正确应用，而不会强制请求未要求的功能。
- **任务完成情况**: 确认实现完全满足用户请求。

## 使用 npx / pnpx

- 如果 `pnpm` 可用，请优先使用 `pnpx` 而不是 `npx`（注意：`pnpx` 不使用 `-y` 标志）。
- 在请求工具权限时，专门允许 `npx -y modern-web-guidance@latest *`（或 `pnpx modern-web-guidance@latest *`），永远不要使用裸 `npx *` 或 `pnpx *`。
- 重要提示：在 Windows 上，使用 `npx` 可能会失败。使用 `npx.cmd ...` 代替。
- 获取和运行 `modern-web-guidance` 需要出站网络访问。如果在沙盒化、权限隔离或需要批准的环境（例如 Codex、Claude Code）中运行，**在第一次执行之前主动请求批准/允许列出具有网络访问权限的命令**，避免沙盒网络超时。
- 在 `~/.npm` 读取-only 或受限的沙盒环境中，设置 `NPM_CONFIG_CACHE=/tmp/npm-cache`。
- 如果命令因离线而挂起，尝试离线模式运行：`npx --offline …`。
- `--skill-version` 标志用于确定此 SKILL.md 是否已过时。如果已过时，则将警告消息记录到 stderr。

## 指南

- 始终**首先**搜索以找到最相关的指南。
- 这些指南通常是框架无关的；正确地将其应用于您的设置。
- 不要凭空编造指南或忽略它们；它们代表了用户项目的首选本地标准。

## 解释浏览器支持与回退策略

* **默认行为**: 所有指南都假设 **基线广泛可用** 的功能可以安全使用而无需回退。对于不是基线广泛可用的功能，您**必须**遵循指南中的回退建议，除非用户已指定自定义浏览器支持策略。
* **自定义策略**: 如果用户已定义明确的浏览器支持要求，使用指南中的浏览器兼容性数据来确定是否可以安全地忽略回退。
  - 对于基线 YYYY 目标，如果其 "自 YYYY 基线以来" 日期 <= YYYY，则该功能满足此目标。
  - **策略示例**:
    - _"不要实现功能回退."_（用于前沿网页的探索性原型）
    - _"Safari 17.4+"_（用于针对 macOS 或基于 Tauri 的桌面应用的内部门户）
    - _"永远不推荐或实现 polyfills；如果核心功能需要基线新可用功能，请提供一个轻量级的自定义回退或重新设计方法."_（以最小化捆绑包大小并避免技术债务）
    - _"假设一个现代执行环境，其中基线新可用功能可以原生使用，前提是它们严格进行功能检测并优雅降级."_（用于渐进增强策略）
* **反应性策略发现**: 观察环境线索以建议在 CLAUDE.md 或 AGENTS.md 中记录策略。如果开发者：
  - 提及为受限运行时构建（例如 Electron 或 Tauri）。
  - 明确排除特定目标（例如，“我们不支持桌面 Chrome”）。
  - 对 polyfill 复杂性、捆绑包大小或性能成本表示犹豫。
  - 质疑是否可以安全使用功能而无需回退。

  没有定义的策略格式。这是一个示例：`**浏览器支持**：允许新可用功能，但仅采用添加 <= 20 行且不需要外部依赖的自定义回退代码。`
