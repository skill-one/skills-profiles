# 研究技能

对任何主题进行全面研究，通过自动收集来源、分析和生成带引用的回复。

## 认证

脚本通过 Tavily MCP 服务器使用 OAuth。**无需手动设置** - 首次运行时，它将：
1. 检查 `~/.mcp-auth/` 中的现有令牌
2. 如果未找到，将自动打开浏览器进行 OAuth 认证

> **注意**：您必须拥有一个现有的 Tavily 账户。OAuth 流仅支持登录 - 通过此流程无法创建账户。如果您没有账户，请先在 [tavily.com](https://tavily.com) 注册。

### 替代方案：API 密钥

如果您更喜欢使用 API 密钥，请在 https://tavily.com 获取一个，并添加到 `~/.claude/settings.json`：
```json
{
  "env": {
    "TAVILY_API_KEY": "tvly-your-api-key-here"
  }
}
```

## 快速入门

> **提示**：研究可能需要 30-120 秒。按 **Ctrl+B** 在后台运行。

### 使用脚本

```bash
./scripts/research.sh '<json>' [输出文件]
```

**示例**：

```bash
# 基本研究
./scripts/research.sh '{"input": "量子计算趋势"}'

# 使用专业模型进行综合分析
./scripts/research.sh '{"input": "AI 代理比较", "model": "pro"}'

# 保存到文件
./scripts/research.sh '{"input": "电动汽车市场分析", "model": "pro"}' ./ev-report.md

# 快速目标研究
./scripts/research.sh '{"input": "气候变化影响", "model": "mini"}'
```

## 参数

| 字段 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `input` | 字符串 | 必填 | 研究主题或问题 |
| `model` | 字符串 | `"mini"` | 模型：`mini`、`pro`、`auto` |

## 模型选择

**经验法则**： "X 是什么做的？" -> mini。 "X vs Y vs Z" 或 "如何...的最佳方法？" -> pro。

| 模型 | 用例 | 速度 |
|------|------|------|
| `mini` | 单个主题、目标研究 | ~30s |
| `pro` | 综合多角度分析 | ~60-120s |
| `auto` | API 根据复杂性选择 | 变化 |

## 示例

### 快速概述

```bash
./scripts/research.sh '{"input": "检索增强生成是什么？", "model": "mini"}'
```

### 技术比较

```bash
./scripts/research.sh '{"input": "LangGraph vs CrewAI 用于多代理系统", "model": "pro"}'
```

### 市场研究

```bash
./scripts/research.sh '{"input": "2025 年金融科技创业格局", "model": "pro"}' fintech-report.md
```
