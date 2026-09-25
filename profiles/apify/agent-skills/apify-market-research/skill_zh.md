# 市场调研

使用 Apify Actors 进行市场调研，从多个平台提取数据。

## 前置条件
（无需提前检查）

- 包含 `APIFY_TOKEN` 的 `.env` 文件
- Node.js 20.6+（用于原生 `--env-file` 支持）
- `mcpc` 命令行工具：`npm install -g @apify/mcpc`

## 工作流程

复制此清单并跟踪进度：

```
任务进度：
- [ ] 第 1 步：确定市场调研类型（选择 Actor）
- [ ] 第 2 步：通过 mcpc 获取 Actor 架构
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行分析脚本
- [ ] 第 5 步：总结调研结果
```

### 第 1 步：确定市场调研类型

根据调研需求选择合适的 Actor：

| 用户需求 | Actor ID | 适用于 |
|---------|----------|--------|
| 市场密度 | `compass/crawler-google-places` | 地点分析 |
| 地理空间分析 | `compass/google-maps-extractor` | 商业地图 |
| 区域兴趣 | `apify/google-trends-scraper` | 趋势数据 |
| 价格和需求 | `apify/facebook-marketplace-scraper` | 市场定价 |
| 活动市场 | `apify/facebook-events-scraper` | 活动分析 |
| 消费者需求 | `apify/facebook-groups-scraper` | 群组调研 |
| 市场格局 | `apify/facebook-pages-scraper` | 商业页面 |
| 商业密度 | `apify/facebook-page-contact-information` | 联系数据 |
| 文化洞察 | `apify/facebook-photos-scraper` | 视觉研究 |
| 狭义定位 | `apify/instagram-hashtag-scraper` | 标签研究 |
| 标签统计 | `apify/instagram-hashtag-stats` | 市场规模 |
| 市场活动 | `apify/instagram-reel-scraper` | 活动分析 |
| 市场情报 | `apify/instagram-scraper` | 全量数据 |
| 产品发布调研 | `apify/instagram-api-scraper` | API 访问 |
| 酒店市场 | `voyager/booking-scraper` | 酒店数据 |
| 旅游洞察 | `maxcopell/tripadvisor-reviews` | 评论分析 |

### 第 2 步：获取 Actor 架构

使用 mcpc 动态获取 Actor 的输入架构和详细信息：

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

将 `ACTOR_ID` 替换为选择的 Actor（例如，`compass/crawler-google-places`）。

这将返回：
- Actor 描述和 README
- 必填和选填的输入参数
- 输出字段（如果可用）

### 第 3 步：询问用户偏好

运行前询问：
1. **输出格式**：
   - **快速回答** - 在聊天中显示前几条结果（不保存文件）
   - **CSV** - 完整导出所有字段
   - **JSON** - 以 JSON 格式完整导出
2. **结果数量**：根据用例特性确定

### 第 4 步：运行脚本

**快速回答（在聊天中显示，不生成文件）：**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT'
```

**CSV：**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_OUTPUT_FILE.csv \
  --format csv
```

**JSON：**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_OUTPUT_FILE.json \
  --format json
```

### 第 5 步：总结调研结果

完成后报告：
- 找到的结果数量
- 文件位置和名称
- 关键市场洞察
- 建议的下一步（深度分析、验证）

## 错误处理

`APIFY_TOKEN not found` - 提示用户创建包含 `APIFY_TOKEN=your_token` 的 `.env` 文件
`mcpc not found` - 提示用户安装 `npm install -g @apify/mcpc`
`Actor not found` - 检查 Actor ID 是否拼写正确
`Run FAILED` - 提示用户检查错误输出中的 Apify 控制台链接
`Timeout` - 减少输入大小或增加 `--timeout`
