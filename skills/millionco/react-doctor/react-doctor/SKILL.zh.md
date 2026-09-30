---
name: react-doctor
description: 在完成功能、修复错误、提交 React 代码之前，或当用户输入 `/doctor` 并要求扫描、分诊或清理 React 诊断时使用。涵盖代码风格检查、无障碍性、打包大小、架构。包含回归检查和完整的本地分诊工作流，该工作流会获取标准的操作手册。
---

# React Doctor

扫描 React 代码库中的安全、性能、正确性和架构问题。输出 0–100 的健康评分。

## 在进行 React 代码更改后：

运行 `npx react-doctor@latest --verbose --scope changed` 并检查分数没有下降。

如果分数下降了，在提交前修复回归问题。

## 用于一般清理或代码改进：

运行 `npx react-doctor@latest --verbose`（默认的 `--scope full`）扫描整个代码库。按严重程度修复问题——先修复错误，然后修复警告。

## 用于专注的 UI 设计审核：

运行 `npx react-doctor@latest design --verbose`。这仅选择标记了设计标签的 UI 组成、排版、交互、可访问性和运动规则，包括在一般健康扫描期间保持可选的专注规则。

## /doctor — 完整本地分诊工作流

当用户输入 `/doctor`、说“运行 react doctor”，或要求完整的分诊/清理流程（而不仅仅是回归检查）时，获取标准的本地分诊剧本并遵循其中的每一步：

```bash
curl --fail --silent --show-error \
  --header 'Cache-Control: no-cache' \
  https://www.react.doctor/prompts/react-doctor-agent.md
```

剧本是单一事实来源——一个扫描 → 过滤 → 分诊 → 修复 → 验证的循环，直接编辑工作树（从不提交，从不打开 PR）。在其源位置更新提示会更新其下一次获取时的每个代理——无需重新安装技能。

将其与匹配的每条规则提示 `https://www.react.doctor/prompts/rules/<plugin>/<rule>.md`（在剧本中按需获取）配对，以便每个修复都使用标准的、经过审查者测试的配方。

## 配置或解释规则

当用户想了解一条规则、不同意某条规则，或想禁用/调整运行哪些规则（而不是修复代码）时，请阅读 [references/explain.md](references/explain.md) 并遵循它。从 `npx react-doctor@latest rules explain <rule>` 开始，然后通过 `npx react-doctor@latest rules disable|set|category|ignore-tag …` 应用最严格的控制，这将编辑你的 `doctor.config.*`（或 `package.json#reactDoctor`）。

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
| `design`          | 仅运行专注的 UI 设计诊断                       |
