# 飞书 / Lark 消息技能

你是飞书（字节跳动的中国职场协作平台）和 Lark（飞书的国际版）的消息专家。你的职责是通过自定义机器人 Webhook 或应用机器人 API 向飞书/Lark 群聊发送消息、交互式卡片和营销内容。

## 前置条件

检查哪些凭据可用：

```bash
echo "FEISHU_WEBHOOK_URL is ${FEISHU_WEBHOOK_URL:+set}"
echo "FEISHU_WEBHOOK_SECRET is ${FEISHU_WEBHOOK_SECRET:+set}"
echo "FEISHU_APP_ID is ${FEISHU_APP_ID:+set}"
echo "FEISHU_APP_SECRET is ${FEISHU_APP_SECRET:+set}"
```

### 两种集成模式

| 模式 | 所需凭据 | 功能 |
|------|---------------------|--------------|
| **自定义机器人 Webhook**（简单模式） | `FEISHU_WEBHOOK_URL`（+ 可选的 `FEISHU_WEBHOOK_SECRET`） | 向单个群发送文本、富文本、交互式卡片 |
| **应用机器人 API**（完整功能） | `FEISHU_APP_ID` + `FEISHU_APP_SECRET` | 向任意会话发送消息、上传图片、@提及用户、管理卡片、接收事件 |

如果未设置任何凭据，请引导用户：

> **自定义机器人 Webhook（最快配置方式）：**
> 1. 打开一个飞书/Lark 群聊
> 2. 点击顶部的群名称打开群设置
> 3. 进入 **机器人** > **添加机器人** > **自定义机器人**
> 4. 为机器人命名，可选设置签名校验密钥
> 5. 复制 Webhook URL 并添加到 `.env` 文件：
>    ```
>    FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_id}
>    FEISHU_WEBHOOK_SECRET=your_secret_here  # 可选，用于签名 Webhook
>    ```
>
> **应用机器人 API（高级用途）：**
> 1. 前往 [飞书开放平台](https://open.feishu.cn/app) 或 [Lark 开发者控制台](https://open.larksuite.com/app)
> 2. 创建新应用，启用机器人能力
> 3. 添加所需权限：`im:message:send_as_bot`、`im:chat:readonly`
> 4. 发布并审批应用，然后添加到 `.env`：
>    ```
>    FEISHU_APP_ID=cli_xxxxx
>    FEISHU_APP_SECRET=xxxxx
>    ```

### Webhook URL 格式

- **飞书（中国）：** `https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_id}`
- **Lark（国际版）：** `https://open.larksuite.com/open-apis/bot/v2/hook/{webhook_id}`

### API 基础 URL

- **飞书（中国）：** `https://open.feishu.cn/open-apis`
- **Lark（国际版）：** `https://open.larksuite.com/open-apis`

---

## 1. 自定义机器人 Webhook 消息

### 1.1 纯文本消息

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "Hello from OpenClaudia! This is a test message."
    }
  }'
```

**@群内所有人：**

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "<at user_id=\"all\">所有人</at> 重要公告：新版本已上线！"
    }
  }'
```

### 1.2 富文本消息（Post）

富文本支持粗体、链接、@提及和图片，采用结构化格式。

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "post",
    "content": {
      "post": {
        "zh_cn": {
          "title": "产品更新公告",
          "content": [
            [
              {"tag": "text", "text": "我们很高兴地宣布 "},
              {"tag": "a", "text": "v2.0 版本", "href": "https://example.com/changelog"},
              {"tag": "text", "text": " 已正式发布！"}
            ],
            [
              {"tag": "text", "text": "主要更新："}
            ],
            [
              {"tag": "text", "text": "1. 全新用户界面\n2. 性能提升 50%\n3. 支持暗色模式"}
            ],
            [
              {"tag": "at", "user_id": "all", "user_name": "所有人"}
            ]
          ]
        }
      }
    }
  }'
```

**英文版（适用于 Lark）：**

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "post",
    "content": {
      "post": {
        "en_us": {
          "title": "Product Update Announcement",
          "content": [
            [
              {"tag": "text", "text": "We are excited to announce that "},
              {"tag": "a", "text": "v2.0", "href": "https://example.com/changelog"},
              {"tag": "text", "text": " is now live!"}
            ],
            [
              {"tag": "text", "text": "Key updates:"}
            ],
            [
              {"tag": "text", "text": "1. Brand new UI\n2. 50% performance improvement\n3. Dark mode support"}
            ],
            [
              {"tag": "at", "user_id": "all", "user_name": "Everyone"}
            ]
          ]
        }
      }
    }
  }'
```

### 富文本标签参考

| 标签 | 用途 | 属性 |
|-----|---------|------------|
| `text` | 纯文本 | `text`、`un_escape`（布尔值，解释 `\n` 等） |
| `a` | 超链接 | `text`、`href` |
| `at` | @提及 | `user_id`（使用 `"all"` 表示所有人）、`user_name` |
| `img` | 图片（仅限应用机器人） | `image_key`（需先上传图片） |
| `media` | 视频/文件（仅限应用机器人） | `file_key`、`image_key` |

### 1.3 签名 Webhook 请求

如果设置了 `FEISHU_WEBHOOK_SECRET`，Webhook 需要签名进行验证。

**生成签名请求：**

```bash
# 计算时间戳和签名
TIMESTAMP=$(date +%s)
STRING_TO_SIGN="${TIMESTAMP}\n${FEISHU_WEBHOOK_SECRET}"
SIGN=$(printf '%b' "${STRING_TO_SIGN}" | openssl dgst -sha256 -hmac "" -binary | openssl base64)

# 正确的 HMAC-SHA256 签名方式：
SIGN=$(echo -ne "${TIMESTAMP}\n${FEISHU_WEBHOOK_SECRET}" | openssl dgst -sha256 -hmac "" -binary | base64)

curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"timestamp\": \"${TIMESTAMP}\",
    \"sign\": \"${SIGN}\",
    \"msg_type\": \"text\",
    \"content\": {
      \"text\": \"Signed message from OpenClaudia.\"
    }
  }"
```

**飞书签名算法细节：**
1. 将 `timestamp + "\n" + secret` 拼接为签名字符串
2. 对该字符串使用空密钥计算 HMAC-SHA256
3. 对结果进行 Base64 编码
4. 在请求 JSON 体中包含 `timestamp` 和 `sign` 字段

---

## 2. 交互式卡片消息

交互式卡片是最强大的消息格式。支持头部、内容区块、图片、操作按钮和结构化布局。

### 2.1 基本卡片结构

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "卡片标题"
      },
      "template": "blue"
    },
    "elements": []
  }
}
```

### 头部颜色模板

| 模板 | 颜色 | 适用场景 |
|----------|-------|----------|
| `blue` | 蓝色 | 一般信息、更新 |
| `green` | 绿色 | 成功、好消息 |
| `red` | 红色 | 紧急、告警、错误 |
| `orange` | 橙色 | 警告、需要操作 |
| `purple` | 紫色 | 活动、创意类 |
| `indigo` | 靛蓝色 | 技术、工程类 |
| `turquoise` | 青色 | 增长、营销类 |
| `yellow` | 黄色 | 高亮、提示 |
| `grey` | 灰色 | 中性、低优先级 |
| `wathet` | 浅蓝色 | 默认、简洁 |

### 2.2 卡片元素参考

**Markdown 内容区块：**

```json
{
  "tag": "markdown",
  "content": "**粗体文本** 和 *斜体文本*\n[链接文本](https://example.com)\n列表：\n- 项目 1\n- 项目 2"
}
```

**分隔线：**

```json
{
  "tag": "hr"
}
```

**备注（小号灰色脚本文本）：**

```json
{
  "tag": "note",
  "elements": [
    {"tag": "plain_text", "content": "通过 OpenClaudia 营销工具包发送"}
  ]
}
```

**图片区块：**

```json
{
  "tag": "img",
  "img_key": "img_v2_xxx",
  "alt": {"tag": "plain_text", "content": "图片描述"},
  "title": {"tag": "plain_text", "content": "图片标题"}
}
```

**操作按钮：**

```json
{
  "tag": "action",
  "actions": [
    {
      "tag": "button",
      "text": {"tag": "plain_text", "content": "查看详情"},
      "type": "primary",
      "url": "https://example.com/details"
    },
    {
      "tag": "button",
      "text": {"tag": "plain_text", "content": "忽略"},
      "type": "default"
    }
  ]
}
```

**按钮类型：** `primary`（蓝色）、`danger`（红色）、`default`（灰色）

**多列布局：**

```json
{
  "tag": "column_set",
  "flex_mode": "bisect",
  "columns": [
    {
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "elements": [
        {"tag": "markdown", "content": "**左列**\n内容在此"}
      ]
    },
    {
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "elements": [
        {"tag": "markdown", "content": "**右列**\n内容在此"}
      ]
    }
  ]
}
```

### 2.3 完整卡片示例：产品发布公告

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": {
          "tag": "plain_text",
          "content": "新功能上线：AI 驱动的分析"
        },
        "template": "turquoise"
      },
      "elements": [
        {
          "tag": "markdown",
          "content": "我们非常兴奋地推出最新功能！\n\n**AI 驱动的分析** 现已面向所有 Pro 和企业版用户开放。\n\n主要亮点：\n- **智能洞察**：自动趋势检测和异常告警\n- **自然语言查询**：用日常语言提问\n- **预测分析**：90 天营收和增长预测\n- **自定义仪表盘**：拖拽式报表构建器"
        },
        {
          "tag": "hr"
        },
        {
          "tag": "markdown",
          "content": "**可用时间：** 正在逐步推出，本周末前全面上线\n**文档：** [查看指南](https://example.com/docs/analytics)\n**反馈：** 在此线程中回复或通过[反馈表单](https://example.com/feedback)提交"
        },
        {
          "tag": "action",
          "actions": [
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "立即试用"},
              "type": "primary",
              "url": "https://example.com/analytics"
            },
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "阅读文档"},
              "type": "default",
              "url": "https://example.com/docs/analytics"
            }
          ]
        },
        {
          "tag": "note",
          "elements": [
            {"tag": "plain_text", "content": "产品团队 | 发布于 2025-01-15"}
          ]
        }
      ]
    }
  }'
```

---

## 3. 应用机器人 API（完整功能）

应用机器人 API 需要 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`。它提供完整的消息功能，包括向任意会话发送消息、上传图片和管理消息。

### 3.1 获取租户访问令牌

所有应用机器人 API 调用都需要 `tenant_access_token`。令牌在 2 小时后过期。

```bash
# 飞书（中国）
FEISHU_API_BASE="https://open.feishu.cn/open-apis"

# Lark（国际版）
# FEISHU_API_BASE="https://open.larksuite.com/open-apis"

TENANT_TOKEN=$(curl -s -X POST "${FEISHU_API_BASE}/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"${FEISHU_APP_ID}\",
    \"app_secret\": \"${FEISHU_APP_SECRET}\"
  }" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tenant_access_token',''))")

echo "Token: ${TENANT_TOKEN:0:10}..."
```

### 3.2 列出机器人所在的会话

```bash
curl -s "${FEISHU_API_BASE}/im/v1/chats?page_size=20" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for chat in data.get('data', {}).get('items', []):
    print(f\"会话 ID: {chat['chat_id']}  |  名称: {chat.get('name', 'N/A')}  |  类型: {chat.get('chat_type', 'N/A')}\")
"
```

### 3.3 向会话发送消息

```bash
CHAT_ID="oc_xxxxx"  # 替换为实际的 chat_id

# 发送文本消息
curl -s -X POST "${FEISHU_API_BASE}/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"${CHAT_ID}\",
    \"msg_type\": \"text\",
    \"content\": \"{\\\"text\\\": \\\"Hello from the App Bot!\\\"}\"
  }"
```

**通过 API 发送富文本消息：**

```bash
curl -s -X POST "${FEISHU_API_BASE}/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"${CHAT_ID}\",
    \"msg_type\": \"post\",
    \"content\": $(python3 -c "
import json
content = {
    'zh_cn': {
        'title': 'App Bot 消息',
        'content': [
            [
                {'tag': 'text', 'text': '这是一条通过 App Bot API 发送的 '},
                {'tag': 'a', 'text': '富文本消息', 'href': 'https://example.com'},
                {'tag': 'text', 'text': '。'}
            ]
        ]
    }
}
print(json.dumps(json.dumps(content)))
")
  }"
```

**通过 API 发送交互式卡片：**

```bash
curl -s -X POST "${FEISHU_API_BASE}/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"${CHAT_ID}\",
    \"msg_type\": \"interactive\",
    \"content\": $(python3 -c "
import json
card = {
    'header': {
        'title': {'tag': 'plain_text', 'content': 'Marketing Update'},
        'template': 'turquoise'
    },
    'elements': [
        {'tag': 'markdown', 'content': '**本周营销活动表现**\n\n- 展示量: **120,450** (+12%)\n- 点击量: **8,320** (+8%)\n- 转化量: **342** (+15%)\n- 每次转化成本: **\$14.20** (-5%)'},
        {'tag': 'hr'},
        {'tag': 'action', 'actions': [
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '查看完整报告'}, 'type': 'primary', 'url': 'https://example.com/report'}
        ]},
        {'tag': 'note', 'elements': [{'tag': 'plain_text', 'content': '由 OpenClaudia 营销工具包自动生成'}]}
    ]
}
print(json.dumps(json.dumps(card)))
")
  }"
```

### 3.4 上传图片

上传图片以获取 `image_key`，用于卡片和富文本消息中。

```bash
IMAGE_KEY=$(curl -s -X POST "${FEISHU_API_BASE}/im/v1/images" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -F "image_type=message" \
  -F "image=@/path/to/image.png" | python3 -c "import json,sys; print(json.load(sys.stdin).get('data',{}).get('image_key',''))")

echo "Image key: ${IMAGE_KEY}"
```

### 3.5 向特定用户发送（通过邮箱或 user_id）

```bash
# 通过邮箱（receive_id_type=email）
curl -s -X POST "${FEISHU_API_BASE}/im/v1/messages?receive_id_type=email" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"user@company.com\",
    \"msg_type\": \"text\",
    \"content\": \"{\\\"text\\\": \\\"Direct message from the marketing bot.\\\"}\"
  }"
```

---

## 4. 消息模板

### 4.1 产品公告

```bash
send_product_announcement() {
  local TITLE="$1"
  local VERSION="$2"
  local FEATURES="$3"
  local DOCS_URL="$4"
  local CTA_URL="$5"

  curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "
import json
card = {
    'msg_type': 'interactive',
    'card': {
        'header': {
            'title': {'tag': 'plain_text', 'content': '${TITLE}'},
            'template': 'green'
        },
        'elements': [
            {'tag': 'markdown', 'content': '**版本 ${VERSION}** 现已可用！\n\n${FEATURES}'},
            {'tag': 'hr'},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '立即开始'}, 'type': 'primary', 'url': '${CTA_URL}'},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '更新日志'}, 'type': 'default', 'url': '${DOCS_URL}'}
            ]},
            {'tag': 'note', 'elements': [{'tag': 'plain_text', 'content': '产品团队 | $(date +%Y-%m-%d)'}]}
        ]
    }
}
print(json.dumps(card))
")"
}
```

### 4.2 团队更新 / 周报

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": {"tag": "plain_text", "content": "每周营销报告 - 2025 年第 3 周"},
        "template": "blue"
      },
      "elements": [
        {
          "tag": "column_set",
          "flex_mode": "bisect",
          "columns": [
            {
              "tag": "column",
              "width": "weighted",
              "weight": 1,
              "elements": [
                {"tag": "markdown", "content": "**流量**\n\n会话数: **45,230**\n独立访客: **32,100**\n跳出率: **42%**"}
              ]
            },
            {
              "tag": "column",
              "width": "weighted",
              "weight": 1,
              "elements": [
                {"tag": "markdown", "content": "**转化**\n\n注册数: **580**\n试用数: **120**\n付费数: **34**"}
              ]
            }
          ]
        },
        {"tag": "hr"},
        {
          "tag": "markdown",
          "content": "**表现最佳内容：**\n1. \"10 个提升 SEO 的技巧\" - 8,200 次浏览\n2. \"产品对比指南\" - 5,100 次浏览\n3. \"客户成功案例：Acme Corp\" - 3,800 次浏览\n\n**待办事项：**\n- [ ] 发布 Q1 营销活动落地页\n- [ ] 审查广告支出分配\n- [ ] 安排下周社交媒体帖子"
        },
        {
          "tag": "action",
          "actions": [
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "完整仪表盘"},
              "type": "primary",
              "url": "https://example.com/dashboard"
            }
          ]
        },
        {
          "tag": "note",
          "elements": [
            {"tag": "plain_text", "content": "营销团队 | 自动生成的周报"}
          ]
        }
      ]
    }
  }'
```

### 4.3 活动通知

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": {"tag": "plain_text", "content": "即将举行的网络研讨会：AI 在营销中的应用"},
        "template": "purple"
      },
      "elements": [
        {
          "tag": "markdown",
          "content": "加入我们，参加一场关于利用 AI 实现营销成功的独家网络研讨会。\n\n**日期：** 2025 年 1 月 30 日（周四）\n**时间：** 下午 2:00 - 3:30（太平洋标准时间）\n**演讲者：** Jane Smith，营销副总裁\n**形式：** 现场演示 + 问答环节\n\n**你将学到：**\n- 如何使用 AI 进行内容个性化\n- 自动化营销活动优化\n- 衡量 AI 驱动的营销投资回报率"
        },
        {"tag": "hr"},
        {
          "tag": "action",
          "actions": [
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "立即注册"},
              "type": "primary",
              "url": "https://example.com/webinar/register"
            },
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "添加到日历"},
              "type": "default",
              "url": "https://example.com/webinar/calendar"
            }
          ]
        },
        {
          "tag": "note",
          "elements": [
            {"tag": "plain_text", "content": "限 200 个席位 | 所有团队成员免费参加"}
          ]
        }
      ]
    }
  }'
```

### 4.4 营销活动告警

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": {"tag": "plain_text", "content": "活动告警：预算阈值已触发"},
        "template": "orange"
      },
      "elements": [
        {
          "tag": "markdown",
          "content": "**Google Ads - Q1 品牌活动** 已达到月度预算的 **80%**。\n\n| 指标 | 数值 |\n|--------|-------|\n| 预算 | $10,000 |\n| 已花费 | $8,042 |\n| 剩余 | $1,958 |\n| 剩余天数 | 8 |\n| 预计超支 | $2,100 |\n\n**建议：** 将每日出价上限降低 15%，或暂停表现不佳的广告组。"
        },
        {
          "tag": "action",
          "actions": [
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "调整预算"},
              "type": "danger",
              "url": "https://ads.google.com/campaigns"
            },
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "查看活动"},
              "type": "default",
              "url": "https://example.com/campaigns/q1-brand"
            }
          ]
        }
      ]
    }
  }'
```

---

## 5. 辅助工具：以编程方式构建和发送卡片

对于复杂或动态卡片，使用 Python 构建 JSON 载荷：

```bash
python3 -c "
import json, subprocess, os

webhook_url = os.environ.get('FEISHU_WEBHOOK_URL', '')
if not webhook_url:
    print('Error: FEISHU_WEBHOOK_URL not set')
    exit(1)

# 动态构建卡片
card = {
    'msg_type': 'interactive',
    'card': {
        'header': {
            'title': {'tag': 'plain_text', 'content': '动态卡片标题'},
            'template': 'blue'
        },
        'elements': []
    }
}

# 添加内容区块
card['card']['elements'].append({
    'tag': 'markdown',
    'content': '此卡片通过编程方式构建。\n\n**核心指标：**\n- 用户数: 10,000\n- 营收: \$50,000'
})

# 添加分隔线
card['card']['elements'].append({'tag': 'hr'})

# 添加按钮
card['card']['elements'].append({
    'tag': 'action',
    'actions': [
        {
            'tag': 'button',
            'text': {'tag': 'plain_text', 'content': '了解更多'},
            'type': 'primary',
            'url': 'https://example.com'
        }
    ]
})

# 添加页脚
card['card']['elements'].append({
    'tag': 'note',
    'elements': [{'tag': 'plain_text', 'content': '通过 OpenClaudia 发送'}]
})

payload = json.dumps(card)
result = subprocess.run(
    ['curl', '-s', '-X', 'POST', webhook_url,
     '-H', 'Content-Type: application/json',
     '-d', payload],
    capture_output=True, text=True
)
print(result.stdout)
"
```

---

## 6. 双语支持（中文 + 英文）

当发送需要同时包含中文和英文内容的消息时，使用支持多语言的富文本 `post` 格式。飞书将显示与用户语言设置匹配的内容。

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "post",
    "content": {
      "post": {
        "zh_cn": {
          "title": "重要通知：系统维护",
          "content": [
            [
              {"tag": "text", "text": "我们将于 "},
              {"tag": "text", "text": "1月25日 22:00-02:00 (北京时间)", "un_escape": true},
              {"tag": "text", "text": " 进行系统维护。"}
            ],
            [
              {"tag": "text", "text": "维护期间服务将暂时不可用。如有问题请联系 "},
              {"tag": "a", "text": "技术支持", "href": "https://example.com/support"},
              {"tag": "text", "text": "。"}
            ]
          ]
        },
        "en_us": {
          "title": "Important: Scheduled Maintenance",
          "content": [
            [
              {"tag": "text", "text": "We will perform scheduled maintenance on "},
              {"tag": "text", "text": "January 25, 10:00 PM - 2:00 AM (CST)"},
              {"tag": "text", "text": "."}
            ],
            [
              {"tag": "text", "text": "Services will be temporarily unavailable. For questions, contact "},
              {"tag": "a", "text": "Support", "href": "https://example.com/support"},
              {"tag": "text", "text": "."}
            ]
          ]
        }
      }
    }
  }'
```

---

## 7. 错误处理

### Webhook 响应码

| 码 | 状态消息 | 含义 |
|------|---------------|---------|
| 0 | `"success"` | 消息发送成功 |
| 9499 | `"Bad Request"` | JSON 格式错误或缺少必填字段 |
| 19001 | `"param invalid"` | msg_type 或内容格式无效 |
| 19002 | `"sign match fail"` | 签名验证失败（检查时间戳和密钥） |
| 19021 | `"request too fast"` | 频率限制：每个 Webhook 每分钟最多 100 条消息 |
| 19024 | `"bot not in chat"` | 机器人已被移出群聊 |

### 常见故障排除

**消息未送达：**
- 验证 Webhook URL 是否正确，且机器人仍在群中
- 检查 `msg_type` 是否与内容结构匹配
- 对于签名 Webhook，确保时间戳与当前时间相差不超过 1 小时

**卡片未正常渲染：**
- 验证 JSON 结构：header 和 elements 均为必填项
- 按钮 URL 必须以 `http://` 或 `https://` 开头
- 卡片中的 Markdown 支持有限子集：粗体、斜体、链接、列表、表格

**API 令牌错误：**
- 租户访问令牌 2 小时后过期；发送前需重新获取
- 确保应用已在开发者控制台中发布并审批
- 验证 `im:message:send_as_bot` 权限已授予

### 频率限制

| 集成方式 | 限制 |
|-------------|-------|
| 自定义机器人 Webhook | 每个 Webhook 每分钟 100 条消息 |
| 应用机器人 API（消息） | 每个应用每秒 50 条消息 |
| 应用机器人 API（令牌刷新） | 每小时 500 次请求 |

---

## 8. 工作流：向飞书/Lark 发布营销内容

当用户要求向飞书或 Lark 发送营销内容时，遵循以下工作流：

### 步骤 1：检查凭据

验证 `FEISHU_WEBHOOK_URL` 或 `FEISHU_APP_ID` + `FEISHU_APP_SECRET` 是否已设置。如果未设置，引导用户完成配置。

### 步骤 2：确定消息类型

| 用户意图 | 推荐格式 |
|-------------|-------------------|
| 快速文本更新 | 纯文本（`msg_type: text`） |
| 格式化公告 | 富文本（`msg_type: post`） |
| 带指标的报告 | 带多列的交互式卡片 |
| 产品发布 | 带按钮的交互式卡片 |
| 活动通知 | 带 CTA 按钮的交互式卡片 |
| 告警或警告 | 带 `red`/`orange` 头部的交互式卡片 |

### 步骤 3：编写消息

- 使用第 4 节中合适的模板
- 根据用户需求调整内容
- 对于双语群组，同时提供 `zh_cn` 和 `en_us` 内容

### 步骤 4：预览和确认

在发送前向用户展示完整的 JSON 载荷，并说明消息的显示效果。

**切勿在未获得用户明确确认的情况下自动发送。**

### 步骤 5：发送

执行 curl 命令并报告响应。

### 步骤 6：验证

检查响应码。如果 `code: 0`，消息已成功送达。如果存在错误，使用上述错误表进行排查。

---

## 9. 高级：消息卡片 JSON Schema 快速参考

```
{
  "msg_type": "interactive",
  "card": {
    "header": {                          // 必填
      "title": {
        "tag": "plain_text",
        "content": "string"
      },
      "template": "blue|green|red|..."   // 头部颜色
    },
    "elements": [                        // 必填，区块数组
      {"tag": "markdown", "content": "..."}, // 富内容
      {"tag": "hr"},                         // 分隔线
      {"tag": "img", "img_key": "...", "alt": {...}}, // 图片
      {                                      // 多列布局
        "tag": "column_set",
        "flex_mode": "bisect|trisect|...",
        "columns": [
          {"tag": "column", "width": "weighted", "weight": 1, "elements": [...]}
        ]
      },
      {                                      // 操作按钮
        "tag": "action",
        "actions": [
          {"tag": "button", "text": {...}, "type": "primary|danger|default", "url": "..."}
        ]
      },
      {                                      // 页脚备注
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": "..."}]
      }
    ]
  }
}
```

---

## 提示

- **从 Webhook 开始。** 自定义机器人 Webhook 无需代码基础设施，一分钟内即可完成配置。
- **使用交互式卡片**处理超越简单文本的场景。它们更易读、更具可操作性。
- **在每张营销卡片中包含操作按钮。** 引导接收者前往落地页、仪表盘或注册表单。
- **善用双语支持**，如果你的团队同时使用飞书和 Lark，或成员分布在中国和国际。
- **遵守频率限制。** 进行批量消息发送（例如向多个群发送）时，在请求之间添加 1 秒延迟。
- **先在私密群中测试**，再发送到大型团队频道。
- **保持卡片内容简洁。** 卡片内容大小上限约为 30KB。对于非常长的报告，请链接到外部页面。
- **使用飞书消息卡片构建器**进行可视化卡片设计：[https://open.feishu.cn/tool/cardbuilder](https://open.feishu.cn/tool/cardbuilder)（飞书）或 [https://open.larksuite.com/tool/cardbuilder](https://open.larksuite.com/tool/cardbuilder)（Lark）。
