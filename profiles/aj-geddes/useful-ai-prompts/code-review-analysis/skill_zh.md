# 代码审查分析

## 目录

- [概述](#概述)
- [使用场景](#使用场景)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

系统化的代码审查流程，涵盖代码质量、安全性、性能、可维护性，并遵循行业标准最佳实践。

## 使用场景

- 审查拉取请求和合并请求
- 在合并前分析代码质量
- 识别安全漏洞
- 向开发者提供建设性反馈
- 确保编码规范符合要求
- 通过代码审查进行指导

## 快速入门

最小工作示例：

```bash
# 检查变更
git diff main...feature-branch

# 审查文件变更
git diff --stat main...feature-branch

# 检查提交历史
git log main...feature-branch --oneline
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [初步评估](references/initial-assessment.md) | 初步评估 |
| [代码质量分析](references/code-quality-analysis.md) | 代码质量分析 |
| [安全审查](references/security-review.md) | 安全审查 |
| [性能审查](references/performance-review.md) | 性能审查 |
| [测试审查](references/testing-review.md) | 测试审查 |
| [最佳实践](references/best-practices.md) | 最佳实践 |

## 最佳实践

### ✅ 应该做

- 保持建设性和尊重
- 解释建议背后的原因
- 提供代码示例
- 如有不清楚的地方请提问
- 肯定良好实践
- 关注重要问题
- 考虑上下文
- 对复杂问题提议结对编程

### ❌ 不应该做

- 过度批评或涉及个人
- 抓小节式风格问题（使用自动化工具）
- 固守主观偏好
- 一次性审查过多变更（>400行）
- 忘记检查测试
- 忽略安全影响
- 草率完成审查
