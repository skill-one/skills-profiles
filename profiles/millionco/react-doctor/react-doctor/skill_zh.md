# React Doctor

扫描 React 代码库中的安全、性能、正确性和架构问题。输出 0–100 的健康评分。

## 在进行 React 代码更改后：

运行 `npx react-doctor@latest --verbose --scope changed` 并检查分数没有下降。

如果分数下降，请在提交前修复回归问题。

## 用于一般清理或代码改进：

运行 `npx react-doctor@latest --verbose`（默认 `--scope full`）扫描整个代码库。按严重程度修复问题——先修复错误，然后修复警告。

## 用于聚焦的 UI 设计审核：

运行 `npx react-doctor@latest design --verbose`。这将仅选择标记为设计的 UI 组件、排版、交互、可访问性和动画规则，包括在一般健康扫描期间保持可选的聚焦规则。

## 用于运行时性能问题：

在交互式终端中运行 `npx react-doctor@latest scan <url> --format json`。React Doctor 会打开一个隔离的 Chrome 配置文件，在用户重现慢速交互时记录 DevTools 跟踪，并以紫色轮廓显示组件名称，React 在渲染时显示。当用户按下 Enter 时停止。先阅读结构化摘要，然后检查返回的本地 `.json.gz` 跟踪文件中的 CPU、浏览器和 React 组件证据。

如果用户需要其认证的浏览器状态，请使用 `--cdp <remote-debugging-url>`。这需要 Chrome 已经以远程调试模式运行。永远不要要求 cookie 或复制用户的浏览器配置文件。将跟踪视为敏感的本地应用程序数据，未经明确许可永远不要上传它。

## /doctor — 完整本地分诊工作流

当用户输入 `/doctor`、说出“运行 react doctor”或要求完整的分诊/清理流程（而不仅仅是回归检查）时，获取标准的本地分诊剧本并按照其中的每个步骤执行：

```bash
curl --fail --silent --show-error \
  --header 'Cache-Control: no-cache' \
  https://www.react.doctor/prompts/react-doctor-agent.md
```

剧本是单一事实来源——一个扫描 → 过滤 → 分诊 → 修复 → 验证的循环，直接编辑工作树（从不提交，从不打开 PR）。在其源位置更新提示会更新其下一次获取时的每个代理——无需重新安装技能。

将其与 `https://www.react.doctor/prompts/rules/<plugin>/<rule>.md`（在剧本中按需获取的匹配每条规则的提示）配对，以便每个修复都使用规范、经过审查者测试的配方。

## 配置或解释规则

当用户想要理解一条规则、不同意某条规则或想要禁用/调整运行哪些规则（而不是修复代码）时，请阅读 [references/explain.md](references/explain.md) 并遵循它。从 `npx react-doctor@latest rules explain <rule>` 开始，然后通过 `npx react-doctor@latest rules disable|set|category|ignore-tag …` 应用最严格的控制，这将编辑您的 `doctor.config.*`（或 `package.json#reactDoctor`）。

## 命令

```bash
npx react-doctor@latest --verbose --scope changed
```

| 标志              | 目的                                                          |
| ----------------- | ---------------------------------------------------------------- |
| `.`               | 扫描当前目录                                           |
| `--verbose`       | 显示受影响的文件和每条规则的行号                    |
| `--scope changed` | 仅报告与基本分支引入的问题 (默认: full)                 |
| `--scope lines`   | 仅报告更改行上的问题                          |
| `--score`         | 仅输出数值分数                                    |
| `design`          | 仅运行聚焦的 UI 设计诊断                       |
