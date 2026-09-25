# 招揽潜在客户

使用 Apify Actors 从多个平台抓取潜在客户。

## 前置条件
（无需提前检查）

- 包含 `APIFY_TOKEN` 的 `.env` 文件
- Node.js 20.6+（用于原生 `--env-file` 支持）
- `mcpc` 命令行工具：`npm install -g @apify/mcpc`

## 工作流程

复制此清单并跟踪进度：

```
任务进度：
- [ ] 第 1 步：确定潜在客户来源（选择 Actor）
- [ ] 第 2 步：通过 mcpc 获取 Actor 架构
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行潜在客户查找脚本
- [ ] 第 5 步：总结结果
```

### 第 1 步：确定潜在客户来源

根据用户需求选择合适的 Actor：

| 用户需求 | Actor ID | 适用于 |
|---------|----------|----------|
| 本地企业 | `compass/crawler-google-places` | 餐厅、健身房、商店 |
| 联系人丰富 | `vdrmota/contact-info-scraper` | 从 URL 中提取电子邮件、电话 |
| Instagram 个人资料 | `apify/instagram-profile-scraper` | 影响者发现 |
| Instagram 帖子/评论 | `apify/instagram-scraper` | 帖子、评论、标签、地点 |
| Instagram 搜索 | `apify/instagram-search-scraper` | 地点、用户、标签发现 |
| TikTok 视频/标签 | `clockworks/tiktok-scraper` | 全面提取 TikTok 数据 |
| TikTok 标签/个人资料 | `clockworks/free-tiktok-scraper` | 免费 TikTok 数据提取器 |
| TikTok 用户搜索 | `clockworks/tiktok-user-search-scraper` | 通过关键词查找用户 |
| TikTok 个人资料 | `clockworks/tiktok-profile-scraper` | 创作者联系 |
| TikTok 关注者/关注 | `clockworks/tiktok-followers-scraper` | 受众分析、细分 |
| Facebook 页面 | `apify/facebook-pages-scraper` | 企业联系人 |
| Facebook 页面联系人 | `apify/facebook-page-contact-information` | 提取电子邮件、电话、地址 |
| Facebook 群组 | `apify/facebook-groups-scraper` | 购买意向信号 |
| Facebook 活动 | `apify/facebook-events-scraper` | 活动网络、合作 |
| Google 搜索 | `apify/google-search-scraper` | 广泛的潜在客户发现 |
| YouTube 频道 | `streamers/youtube-scraper` | 创作者合作 |
| Google 地图电子邮件 | `poidata/google-maps-email-extractor` | 直接电子邮件提取 |

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
   - **快速回答** - 在聊天中显示前几个结果（不保存文件）
   - **CSV** - 所有字段的完整导出
   - **JSON** - JSON 格式的完整导出
2. **结果数量**：根据用例特性

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

### 第 5 步：总结结果

完成后报告：
- 发现的潜在客户数量
- 文件位置和名称
- 可用关键字段
- 建议的下一步操作（过滤、丰富）

## 错误处理

`APIFY_TOKEN 未找到` - 请用户创建包含 `APIFY_TOKEN=your_token` 的 `.env` 文件
`mcpc 未找到` - 请用户安装 `npm install -g @apify/mcpc`
`Actor 未找到` - 检查 Actor ID 拼写
`运行失败` - 请用户检查错误输出中的 Apify 控制台链接
`超时` - 减少输入大小或增加 `--timeout`
