---
name: tavily-search
description: Tavily AI 搜索 API - 专为 AI 代理优化的搜索服务。用于在网络上搜索实时信息、新闻、事实或任何需要实时数据的任务。
---

# Tavily 搜索

为 AI 代理优化的 Tavily API 网络搜索。

## 使用方法

```bash
./scripts/search "你的搜索查询"
```

## 脚本

| 脚本 | 使用方法 |
|------|---------|
| `scripts/search <查询>` | 网络搜索 |
| `scripts/search "最新 AI 新闻" --format json` | JSON 格式输出 |

## 环境

```bash
export TAVILY_API_KEY="你的 API 密钥"
```

获取 API 密钥：https://tavily.com/

## 示例

```bash
./scripts/search "Claude AI 最新功能"
# 返回：针对 AI 上下文的优化搜索结果
```
