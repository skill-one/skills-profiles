# Brave Search

使用官方 Brave Search API 进行网页搜索和内容提取，无需浏览器。

## 设置

需要拥有 Brave Search API 账户并开通免费订阅。创建免费订阅需要信用卡信息（不会扣费）。

1. 在 https://api-dashboard.search.brave.com/register 创建账户
2. 创建 "免费 AI" 订阅
3. 为订阅创建 API 密钥
4. 添加到您的 shell 配置文件 (`~/.profile` 或 `~/.zprofile` 对于 zsh):
   ```bash
   export BRAVE_API_KEY="your-api-key-here"
   ```
5. 安装依赖（运行一次）:
   ```bash
   cd {baseDir}
   npm install
   ```

## 搜索

```bash
{baseDir}/search.js "query"                         # 基本搜索（5 条结果）
{baseDir}/search.js "query" -n 10                   # 更多结果（最多 20 条）
{baseDir}/search.js "query" --content               # 包含页面内容作为 markdown
{baseDir}/search.js "query" --freshness pw          # 过去一周的结果
{baseDir}/search.js "query" --freshness 2024-01-01to2024-06-30  # 日期范围
{baseDir}/search.js "query" --country DE            # 来自德国的结果
{baseDir}/search.js "query" -n 3 --content          # 组合选项
```

### 选项

- `-n <num>` - 结果数量（默认：5，最大：20）
- `--content` - 获取并包含页面内容作为 markdown
- `--country <code>` - 两个字母的国家代码（默认：US）
- `--freshness <period>` - 按时间筛选：
  - `pd` - 过去一天（24 小时）
  - `pw` - 过去一周
  - `pm` - 过去一个月
  - `py` - 过去一年
  - `YYYY-MM-DDtoYYYY-MM-DD` - 自定义日期范围

## 提取页面内容

```bash
{baseDir}/content.js https://example.com/article
```

获取 URL 并提取可读内容作为 markdown。

## 输出格式

```
--- 结果 1 ---
标题: 页面标题
链接: https://example.com/page
年龄: 2 天前
摘要: 搜索结果中的描述
内容: （如果使用了 --content 标志）
  从页面中提取的 markdown 内容...

--- 结果 2 ---
...
```

## 使用场景

- 搜索文档或 API 参考
- 查找事实或当前信息
- 从特定 URL 获取内容
- 任何需要网页搜索但无需交互式浏览的任务
