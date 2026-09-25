> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# 网络搜索与提取

通过 [inference.sh](https://inference.sh) CLI 搜索网络并提取内容。

![网络搜索与提取](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgndqjxd780zm2j3rmada6y8.jpeg)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 搜索网络
belt app run tavily/search-assistant --input '{"query": "2024年最新的AI发展"}'
```

## 可用应用

### Tavily

| 应用 | 应用ID | 描述 |
|-----|--------|-------------|
| 搜索助手 | `tavily/search-assistant` | 带答案的AI驱动搜索 |
| 提取 | `tavily/extract` | 从URL中提取内容 |

### Exa

| 应用 | 应用ID | 描述 |
|-----|--------|-------------|
| 搜索 | `exa/search` | 带AI的智能网络搜索 |
| 答案 | `exa/answer` | 直接提供事实性答案 |
| 提取 | `exa/extract` | 提取和分析网络内容 |

## 示例

### Tavily 搜索

```bash
belt app run tavily/search-assistant --input '{
  "query": "构建AI代理的最佳实践是什么？"
}'
```

返回带来源和图片的AI生成答案。

### Tavily 提取

```bash
belt app run tavily/extract --input '{
  "urls": ["https://example.com/article1", "https://example.com/article2"]
}'
```

从多个URL中提取干净的文本和图片。

### Exa 搜索

```bash
belt app run exa/search --input '{
  "query": "机器学习框架比较"
}'
```

返回高度相关的链接和上下文。

### Exa 答案

```bash
belt app run exa/answer --input '{
  "question": "东京的人口是多少？"
}'
```

返回直接的事实性答案。

### Exa 提取

```bash
belt app run exa/extract --input '{
  "url": "https://example.com/research-paper"
}'
```

提取和分析网页内容。

## 工作流：研究 + LLM

```bash
# 1. 搜索信息
belt app run tavily/search-assistant --input '{
  "query": "量子计算最新发展"
}' > search_results.json

# 2. 使用Claude分析
belt app run openrouter/claude-sonnet-45 --input '{
  "prompt": "根据这项研究，总结关键趋势：<search-results>"
}'
```

## 工作流：提取 + 总结

```bash
# 1. 从URL提取内容
belt app run tavily/extract --input '{
  "urls": ["https://example.com/long-article"]
}' > content.json

# 2. 使用LLM总结
belt app run openrouter/claude-haiku-45 --input '{
  "prompt": "用3个要点总结这篇文章：<content>"
}'
```

## 应用场景

- **研究**：收集任何主题的信息
- **RAG**：检索增强生成
- **事实核查**：带来源验证声明
- **内容聚合**：从多个来源收集数据
- **代理**：构建具备研究能力的AI代理

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# LLM模型（与搜索结合用于RAG）
npx skills add inference-sh/skills@llm-models

# 图像生成
npx skills add inference-sh/skills@ai-image-generation
```

浏览所有应用：`belt app list`

## 文档

- [为代理添加工具](https://inference.sh/docs/agents/adding-tools) - 为代理添加搜索功能
- [构建研究代理](https://inference.sh/blog/guides/research-agent) - LLM + 搜索集成指南
- [工具集成税](https://inference.sh/blog/tools/integration-tax) - 为什么预构建工具很重要
