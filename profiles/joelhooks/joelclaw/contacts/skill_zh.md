# 联系人

在 `~/Vault/Contacts/` 目录中管理联系人。每个联系人是一个带有 YAML 前置的 Markdown 文件。

## 联系人文件位置

```
~/Vault/Contacts/<Name>.md
```

索引文件：`~/Vault/Contacts/index.md` — 所有联系人的维基链接列表。

## 前置 Schema

```yaml
---
name: 全名
aliases: [昵称, 处理名]
role: 当前角色/职位
organizations: [组织1, 组织2]
vip: true  # 或 false
slack_user_id: U0XXXXXXX
slack_dm_channel: D0XXXXXXX  # 如果未知则为 null
website: https://example.com
github: 用户名
twitter: 处理名
email: user@example.com
tags: [vip, 讲师, 创作者, 家庭, 员工]
---
```

## 部分

```markdown
# 名称

## 联系人渠道
- Slack, 邮箱, 社交处理名, 网站

## 项目
- 活动项目, 课程, 合作

## 关键背景
- 关系笔记, 工作风格, 历史记录

## 近期活动
- YYYY-MM-DD | 渠道 | 摘要
```

参考 `~/Vault/Contacts/Matt Pocock.md` 获取一个完全丰富的示例。

## 添加联系人

### 选项 1: 启动丰富化管道（推荐）

发送一个 Inngest 事件。`contact-enrich` 函数会跨 Slack、Roam、Web/GitHub、Granola、Brain 支持的回忆和其他索引源进行扩展，与 LLM 结合，并写入 Vault 文件。

```bash
# 通过 curl（CLI 在 Bun v1.3.9 下存在 OTEL 导入错误）
curl -s -X POST "http://localhost:8288/e/$INNGEST_EVENT_KEY" \
  -H "Content-Type: application/json" \
  -d '[{
    "name": "contact/enrich.requested",
    "data": {
      "name": "Person Name",
      "depth": "full",
      "hints": {
        "slack_user_id": "U0XXXXXXX",
        "github": "username",
        "twitter": "handle",
        "email": "user@example.com",
        "website": "https://example.com"
      }
    },
    "ts": EPOCH_MS
  }]'
```

**深度模式：**
- `full` (~60s, ~$0.05): 所有 7 个源 + LLM 合成。用于新联系人或定期刷新。
- `quick` (~10s, ~$0.01): 仅 Slack + 记忆。适用于实时 VIP 检测。

**提示是可选的但有助于：** 任何已知的标识符（Slack ID、GitHub、邮箱、Twitter、网站）会启动搜索并提高结果。

### 选项 2: 快速手动创建

对于简单联系人，丰富化是过度设计的：

```markdown
---
name: Person Name
aliases: []
role: Role
organizations: [Org]
vip: false
slack_user_id: null
website: null
github: null
twitter: null
email: null
tags: [tag1]
---

# Person Name

## 联系人渠道
- ...

## 关键背景
- ...
```

写入 `~/Vault/Contacts/Person Name.md` 并将 `[[Person Name]]` 添加到 `index.md`。

## 更新联系人

重新运行丰富化，使用现有的 Vault 路径：

```json
{
  "name": "contact/enrich.requested",
  "data": {
    "name": "Person Name",
    "vault_path": "Contacts/Person Name.md",
    "depth": "full"
  }
}
```

合成器会将新数据与现有内容合并——除非被矛盾地否定，否则不会丢弃现有事实。

## VIP 联系人 (ADR-0151)

在前置中标记 `vip: true`。VIP 将获得 **深度丰富化 + 持续监控**。

### 深度丰富化剧本（一次性）

每个 VIP 都会得到全面处理。这是我们对 Kent C. Dodds（2026 年 2 月 26 日）所做的工作：

| 步骤 | 源 | 捕获内容 |
|---|---|---|
| 1. 网络存在 | 网络搜索 `{name} + {org}` | 传记, 角色, 地点, 个人细节 |
| 2. 播客/访谈 | 网络搜索 `{name} podcast interview` | 出现列表, 自己的播客, 受众 |
| 3. Joel 合作 | 他们的网站, 出现页面 | 联合播客, 共同组织的活动, 共享项目 |
| 4. 职业时间线 | Defuddle 2-3 个关键访谈记录 | 起源故事, 职业轨迹, 关键决策, 价值观 |
| 5. GitHub 个人资料 | GitHub API 或网络 | 仓库, 关注者, 组织, 贡献模式 |
| 6. X/Twitter 个人资料 | X API v2（使用 x-api 技能） | 传记, 关注者, 最近推文, 参与度 |
| 7. 关键关系 | 跨参考记录 + 联系人 | 他们与谁合作, 他们提到谁, 我们与谁有共同认识 |
| 8. 内容目录 | 网站爬取（defuddle） | 课程, 博客文章, 开源项目 |
| 9. 受众范围 | 播客数量, 社交关注者 | 会议巡回, 社区存在 |

**丰富化后索引到 Typesense：**
- 批量导入出现/内容到 `discoveries` 集合（NDJSON, `action=upsert`）
- 用个人名称缩写（例如 `kent-c-dodds`）为所有文档打标签以进行过滤
- 字段：`id`, `title`, `url`, `summary`, `tags[]`, `timestamp`
- 写一个 `Vault/Resources/{name}-media-appearances.md` 参考文档，链接回联系人

**Vault 笔记中的输出部分：**
- 背景 & 故事（起源, 职业时间线）
- 教学/工作哲学（或非教育者的等效内容）
- 关键关系（跨链接 `[[维基链接]]` 到其他联系人）
- 受众 & 范围
- 内容/产品
- 播客/与 Joel 的合作历史
- 近期活动（带时间戳）

### 持续监控（ADR-0151 的第 2-4 阶段）

| 渠道 | 工具 | 信号 |
|---|---|---|
| Google Alerts | joelclawbot Google 账户 | 新闻、博客、媒体中的名称提及 |
| X/Twitter 列表 | joelclawbot X 账户 | 推文, 参与度 |
| GitHub 活动 | GitHub API（轮询） | 新仓库, 发布 |
| 播客 RSS | 源监控 | 新节目 |
| 网站变化 | 定期 defuddle + 差异 | 博客文章, 发起新项目, 传记变化 |

**高信号**（立即）：课程发布, 职位变化, 提及 Joel/egghead/Skill, 融资。
**低信号**（每日/每周摘要）：常规推文, 博客文章, OSS 活动。

### 当前 VIP
- 丰富化后通过网关通知 Joel
- 每周通过计划 cron 刷新
- 在渠道智能管道中优先处理（ADR-0131, ADR-0132）
- 当 ADR-0151 第 2+ 阶段实施时进行持续监控

## Roam Research 丰富化

Joel 的 Roam 存档 (`~/Code/joelhooks/egghead-roam-research/`) 包含完整的 egghead 时代图谱（2019-2024）。许多联系人那里有详细的历史记录。

### 快速搜索（Python 正则表达式）
```bash
cd ~/Code/joelhooks/egghead-roam-research
python3 -c "
import re
with open('egghead-2026-01-19-13-09-38.edn', 'r') as f:
    content = f.read()
pattern = r':block/string\s+\"([^\"]*?)\"'
matches = []
for m in re.findall(pattern, content):
    if '[[SEARCH_TAG]]' in m.lower():
        matches.append(m)
print(f'Found {len(matches)} blocks')
for m in matches[:30]:
    print(f'  - {m[:200]}')
"
```

### 人物分类法
在 Roam 中，人们用关系前缀标记：
- `[[collaborator/Name]]` — 战略合作伙伴（Ian Jones, Alex Hillman）
- `[[client/Name]]` — egghead 讲师（Matt Pocock, Jacob Paris）
- `[[staff/Name]]` — egghead 团队（Will Johnson, Daniel Miller, Maggie Appleton）
- `[[name]]`（无前缀） — 非正式参考（Zac 是 `[[zac]]`）

### 页面标题搜索
```bash
python3 -c "
import re
with open('egghead-2026-01-19-13-09-38.edn', 'r') as f:
    content = f.read()
pattern = r':node/title\s+\"([^\"]*?SEARCH_TERM[^\"]*?)\"'
for m in re.findall(pattern, content):
    print(f'  页面: {m}')
"
```

### 添加到联系人
从 Roam 中提取人物数据时，在前置中添加 `roam_tag`：
```yaml
roam_tag: "[[collaborator/Ian Jones]]"
```
这启用了未来的重新查询和交叉引用。

### Datalog 查询（高级）
EDN 文件是 Datomic 风格的。Clojure 脚本存在于 `scripts/` 中，用于结构化分析。参考 `roam-research` 技能获取完整的 Datalog 模式。

## 解决未知人物

当你遇到一个 Slack 用户 ID (`<@U0XXXXXXX>`):

```bash
# 租赁令牌并查找个人资料
SLACK_USER=$(secrets lease slack_user_token --ttl 5m)
curl -s "https://slack.com/api/users.info?user=U0XXXXXXX" \
  -H "Authorization: Bearer $SLACK_USER" | jq '.user.real_name, .user.profile.email'
# 仅撤销本次任务获取的确切租赁 ID；永远不要撤销所有会话的租赁。
```

然后使用解析的名称和提示启动丰富化。

## Inngest 函数

- 函数: `contact-enrich` (`packages/system-bus/src/inngest/functions/contact-enrich.ts`)
- 事件: `contact/enrich.requested`
- ADR: `~/Vault/docs/decisions/0133-contact-enrichment-pipeline.md`
- 并发: 最大 3
- 源: Slack, Slack Connect, Roam 存档, GitHub/网络, Granola 会议, Brain 支持的回忆和其他索引源

## 隐私

- 联系人文件在 Vault 中（私密，不在公共存储库中）
- Slack 数据保持私密——永远不会出现在公共内容中
- 邮箱/电话仅存储供 Joel 参考
