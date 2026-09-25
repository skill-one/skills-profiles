# Tavily 搜索

使用 Tavily API 优化的 AI 代理网络搜索。

## 使用方法

```bash
./scripts/search "你的搜索查询"
```

## 脚本

| 脚本 | 使用方法 |
|------|---------|
| `scripts/search <查询>` | 网络搜索 |
| `scripts/search "最新 AI 新闻" --format json` | JSON 输出 |

## 环境

```bash
export TAVILY_API_KEY="你的 API 密钥"
```

获取 API 密钥：https://tavily.com/

## 示例

```bash
./scripts/search "Claude AI 最新功能"
# 返回：针对 AI 上下文优化的搜索结果
```
