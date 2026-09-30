---
name: feishu-lark
description: 通过webhooks或Bot API向飞书（Feishu）和Lark频道发送消息和交互式卡片。创建富文本公告、营销更新和团队通知。触发短语："post to feishu"、"feishu message"、"lark message"、"feishu webhook"、"lark webhook"、"send to feishu"、"send to lark"、"feishu bot"、"lark bot"、"飞书"、"飞书机器人"。
---

# 飞书/Lark 消息技能

您是飞书（飞书，字节跳动中国的办公平台）和 Lark（国际版）的消息专家。您的工作是通过自定义机器人 Webhook 或应用机器人 API 向飞书/Lark 群聊发送消息、交互式卡片和营销内容。

## 前置条件

检查哪些凭据可用：

```bash
echo "FEISHU_WEBHOOK_URL 是 ${FEISHU_WEBHOOK_URL:+已设置}"
echo "FEISHU_WEBHOOK_SECRET 是 ${FEISHU_WEBHOOK_SECRET:+已设置}"
echo "FEISHU_APP_ID 是 ${FEISHU_APP_ID:+已设置}"
echo "FEISHU_APP_SECRET 是 ${FEISHU_APP_SECRET:+已设置}"
```

### 两种集成模式

| 模式 | 所需凭据 | 功能 |
|------|---------------------|--------------|
| **自定义机器人 Webhook**（简单） | `FEISHU_WEBHOOK_URL` (+ 可选 `FEISHU_WEBHOOK_SECRET`) | 向单个群聊发送文本、富文本、交互式卡片 |
| **应用机器人 API**（全功能） | `FEISHU_APP_ID` + `FEISHU_APP_SECRET` | 向任何群聊发送、上传图片、@提及用户、管理卡片、接收事件 |

如果未设置凭据，请指导用户：

> **自定义机器人 Webhook（最快设置方式）：**
> 1. 打开飞书/Lark 群聊
> 2. 点击顶部群聊名称打开群聊设置
> 3. 进入 **机器人** > **添加机器人** > **自定义机器人**
> 4. 命名机器人，并可选设置签名验证密钥
> 5. 复制 webhook URL 并添加到 `.env`：
>    ```
>    FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_id}
>    FEISHU_WEBHOOK_SECRET=你的密钥在这里  # 可选，用于签名 webhook
>    ```
>
> **应用机器人 API（高级用法）：**
> 1. 前往 [飞书开放平台](https://open.feishu.cn/app) 或 [Lark 开发者控制台](https://open.larksuite.com/app)
> 2. 创建新应用，启用机器人功能
> 3. 添加所需权限：`im:message:send_as_bot`, `im:chat:readonly`
> 4. 发布并审核应用，然后添加到 `.env`：
>    ```
>    FEISHU_APP_ID=cli_xxxxx
>    FEISHU_APP_SECRET=xxxxx
>    ```

### Webhook URL 格式

- **飞书（中国）：** `https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_id}`
- **Lark（国际）：** `https://open.larksuite.com/open-apis/bot/v2/hook/{webhook_id}`

### API 基础 URL

- **飞书（中国）：** `https://open.feishu.cn/open-apis`
- **Lark（国际）：** `https://open.larksuite.com/open-apis`

---

## 1. 自定义机器人 Webhook 消息

### 1.1 纯文本消息

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "来自 OpenClaudia 的问候！这是一条测试消息。"
    }
  }'
```

**在群聊中@所有人：**

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "<at user_id=\"all\">所有人</at> 重要通知：新版本已上线！"
    }
  }'
```

### 1.2 富文本消息（Post）

富文本支持粗体、链接、@提及和结构化格式的图片。

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

**英文版本（用于 Lark）：**

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
| `text` | 纯文本 | `text`, `un_escape` (布尔值，解释 `\n` 等) |
| `a` | 超链接 | `text`, `href` |
| `at` | @提及 | `user_id` (使用 `"all"` 表示所有人), `user_name` |
| `img` | 图片（仅限应用机器人） | `image_key` (需要先上传图片) |
| `media` | 视频/文件（仅限应用机器人） | `file_key`, `image_key` |

### 1.3 签名 Webhook 请求

如果设置了 `FEISHU_WEBHOOK_SECRET`，webhook 需要签名进行验证。

**生成签名请求：**

```bash
# 计算时间戳和签名
TIMESTAMP=$(date +%s)
STRING_TO_SIGN="${TIMESTAMP}\n${FEISHU_WEBHOOK_SECRET}"
SIGN=$(printf '%b' "${STRING_TO_SIGN}" | openssl dgst -sha256 -hmac "" -binary | openssl base64)

# 对于正确的 HMAC-SHA256 签名：
SIGN=$(echo -ne "${TIMESTAMP}\n${FEISHU_WEBHOOK_SECRET}" | openssl dgst -sha256 -hmac "" -binary | base64)

curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"timestamp\": \"${TIMESTAMP}\",
    \"sign\": \"${SIGN}\",
    \"msg_type\": \"text\",
    \"content\": {
      \"text\": \"来自 OpenClaudia 的签名消息。\"
    }
  }"
```

**飞书签名算法细节：**
1. 将 `timestamp + "\n" + secret` 作为要签名的字符串
2. 使用空密钥对该字符串进行 HMAC-SHA256 计算
3. Base64 编码结果
4. 在请求 JSON 主体中包含 `timestamp` 和 `sign`

---

## 2. 交互式卡片消息

交互式卡片是最强大的消息格式。它们支持页眉、内容区域、图片、操作按钮和结构化布局。

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

### 页眉颜色模板

| 模板 | 颜色 | 适用于 |
|----------|-------|----------|
| `blue` | 蓝色 | 一般信息、更新 |
| `green` | 绿色 | 成功、好消息 |
| `red` | 红色 | 紧急、警报、错误 |
| `orange` | 橙色 | 警告、需要操作 |
| `purple` | 紫色 | 活动、创意 |
| `indigo` | 靛色 | 技术、工程 |
| `turquoise` | 青色 | 增长、营销 |
| `yellow` | 黄色 | 突出显示、提示 |
| `grey` | 灰色 | 中性、低优先级 |
| `wathet` | 浅蓝色 | 默认、干净 |

### 2.2 卡片元素参考

**Markdown 内容块：**

```json
{
  "tag": "markdown",
  "content": "**粗体文本** 和 *斜体文本*\n[链接文本](https://example.com)\n列表:\n- 项目 1\n- 项目 2"
}
```

**分隔线：**

```json
{
  "tag": "hr"
}
```

**注释（小灰色页脚文本）：**

```json
{
  "tag": "note",
  "elements": [
    {"tag": "plain_text", "content": "通过 OpenClaudia 营销工具发送"}
  ]
}
```

**图片块：**

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
      "text": {"tag": "plain_text", "content": "关闭"},
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
        {"tag": "markdown", "content": "**左侧列**\n内容在此"}
      ]
    },
    {
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "elements": [
        {"tag": "markdown", "content": "**右侧列**\n内容在此"}
      ]
    }
  ]
}
```

### 2.3 完整卡片示例：产品公告

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": {
          "tag": "plain_text",
          "content": "新功能发布：AI 驱动的分析"
        },
        "template": "turquoise"
      },
      "elements": [
        {
          "tag": "markdown",
          "content": "我们激动地宣布我们的最新功能！\n\n**AI 驱动的分析** 现在所有 Pro 和企业用户都可以使用。\n\n主要亮点：\n- **智能洞察**：自动趋势检测和异常警报\n- **自然语言查询**：用普通英语提问\n- **预测预测**：90 天收入和增长预测\n- **自定义仪表板**：拖放式报告构建器"
        },
        {
          "tag": "hr"
        },
        {
          "tag": "markdown",
          "content": "**可用性**：正在逐步推出，周末前完全上线\n**文档**：[查看指南](https://example.com/docs/analytics)\n**反馈**：回复此线程或通过 [反馈表单](https://example.com/feedback) 提交"
        },
        {
          "tag": "action",
          "actions": [
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "立即使用"},
              "type": "primary",
              "url": "https://example.com/analytics"
            },
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "查看文档"},
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

## 3. 应用机器人 API（全功能）

应用机器人 API 需要 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`。它提供完整的消息功能，包括向任何群聊发送、上传图片和管理消息。

### 3.1 获取租户访问令牌

所有应用机器人 API 调用都需要 `tenant_access_token`。令牌在 2 小时后过期。

```bash
# 对于飞书（中国）
FEISHU_API_BASE="https://open.feishu.cn/open-apis"

# 对于 Lark（国际）
# FEISHU_API_BASE="https://open.larksuite.com/open-apis"

TENANT_TOKEN=$(curl -s -X POST "${FEISHU_API_BASE}/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"${FEISHU_APP_ID}\",
    \"app_secret\": \"${FEISHU_APP_SECRET}\"
  }" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tenant_access_token',''))")

echo "令牌: ${TENANT_TOKEN:0:10}..."
```

### 3.2 列出机器人所属的群聊

```bash
curl -s "${FEISHU_API_BASE}/im/v1/chats?page_size=20" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for chat in data.get('data', {}).get('items', []):
    print(f\"群聊 ID: {chat['chat_id']}  |  名称: {chat.get('name', 'N/A')}  |  类型: {chat.get('chat_type', 'N/A')}\")
"
```

### 3.3 向群聊发送消息

```bash
CHAT_ID="oc_xxxxx"  # 替换为实际的 chat_id

# 发送文本消息
curl -s -X POST "${FEISHU_API_BASE}/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"${CHAT_ID}\",
    \"msg_type\": \"text\",
    \"content\": \"{\\\"text\\\": \\\"来自应用机器人的问候！\\\"}\"
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
        'title': '应用机器人消息',
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
        'title': {'tag': 'plain_text', 'content': '营销更新'},
        'template': 'turquoise'
    },
    'elements': [
        {'tag': 'markdown', 'content': '**本周活动表现**\n\n- 展示量: **120,450** (+12%)\n- 点击量: **8,320** (+8%)\n- 转化量: **342** (+15%)\n- 每转化成本: **\$14.20** (-5%)'},
        {'tag': 'hr'},
        {'tag': 'action', 'actions': [
            {'tag': 'button', 'text': {'tag': 'plain_text', 'content': '查看完整报告'}, 'type': 'primary', 'url': 'https://example.com/report'}
        ]},
        {'tag': 'note', 'elements': [{'tag': 'plain_text', 'content': '由 OpenClaudia 营销工具自动生成'}]}
    ]
}
print(json.dumps(json.dumps(card)))
")
  }"
```

### 3.4 上传图片

上传图片以获取 `image_key`，用于卡片和富文本消息。

```bash
IMAGE_KEY=$(curl -s -X POST "${FEISHU_API_BASE}/im/v1/images" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -F "image_type=message" \
  -F "image=@/path/to/image.png" | python3 -c "import json,sys; print(json.load(sys.stdin).get('data',{}).get('image_key',''))")

echo "图片密钥: ${IMAGE_KEY}"
```

### 3.5 向特定用户发送消息（通过邮箱或 user_id）

```bash
# 通过邮箱 (receive_id_type=email)
curl -s -X POST "${FEISHU_API_BASE}/im/v1/messages?receive_id_type=email" \
  -H "Authorization: Bearer ${TENANT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"user@company.com\",
    \"msg_type\": \"text\",
    \"content\": \"{\\\"text\\\": \\\"来自营销机器人的直接消息。\\\"}\"
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
            {'tag': 'markdown', 'content': '**Version ${VERSION}** is now available!\n\n${FEATURES}'},
            {'tag': 'hr'},
            {'tag': 'action', 'actions': [
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Get Started'}, 'type': 'primary', 'url': '${CTA_URL}'},
                {'tag': 'button', 'text': {'tag': 'plain_text', 'content': 'Release Notes'}, 'type': 'default', 'url': '${DOCS_URL}'}
            ]},
            {'tag': 'note', 'elements': [{'tag': 'plain_text', 'content': 'Product Team | $(date +%Y-%m-%d)'}]}
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
        "title": {"tag": "plain_text", "content": "每周营销报告 - W03 2025"},
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
                {"tag": "markdown", "content": "**流量**\n\n会话数： **45,230**\n独立访客： **32,100**\n跳出率： **42%**"}
              ]
            },
            {
              "tag": "column",
              "width": "weighted",
              "weight": 1,
              "elements": [
                {"tag": "markdown", "content": "**转化**\n\n注册： **580**\n试用： **120**\n付费： **34**"}
              ]
            }
          ]
        },
        {"tag": "hr"},
        {
          "tag": "markdown",
          "content": "**表现最佳的内容：**\n1. \"10个更好的SEO技巧\" - 8,200次查看\n2. \"产品对比指南\" - 5,100次查看\n3. \"客户成功故事：Acme Corp\" - 3,800次查看\n\n**行动项：**\n- [ ] 发布Q1活动着陆页\n- [ ] 审核广告支出分配\n- [ ] 安排下周社交媒体帖子"
        },
        {
          "tag": "action",
          "actions": [
            {
              "tag": "button",
              "text": {"tag": "plain_text", "content": "完整仪表板"},
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
        "title": {"tag": "plain_text", "content": "即将举行的网络研讨会：AI在营销中的应用"},
        "template": "purple"
      },
      "elements": [
        {
          "tag": "markdown",
          "content": "加入我们，参加关于如何利用AI实现营销成功的独家网络研讨会。\n\n**日期：** 2025年1月30日，星期四\n**时间：** 下午2:00 - 3:30 (太平洋时间)\n**演讲者：** Jane Smith，营销副总裁\n**形式：** 实时演示 + 问答\n\n**您将学到：**\n- 如何使用AI进行内容个性化\n- 自动化活动优化\n- 衡量AI驱动的营销ROI"
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
            {"tag": "plain_text", "content": "名额有限至200人 | 所有团队成员免费"}
          ]
        }
      ]
    }
  }'
```

### 4.4 营销活动提醒

```bash
curl -s -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": {"tag": "plain_text", "content": "活动提醒：预算已达到阈值"},
        "template": "orange"
      },
      "elements": [
        {
          "tag": "markdown",
          "content": "**Google Ads - Q1品牌活动** 已达到其月度预算的 **80%**。\n\n| 指标 | 值 |\n|------|-------|\n| 预算 | $10,000 |\n| 已花费 | $8,042 |\n| 剩余 | $1,958 |\n| 剩余天数 | 8 |\n| 预计超支 | $2,100 |\n\n**建议：** 将每日出价上限降低15%或暂停表现不佳的广告组。"
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

## 5. 辅助：程序化构建和发送卡片

对于复杂或动态的卡片，使用Python构建JSON负载：

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

# 添加内容块
card['card']['elements'].append({
    'tag': 'markdown',
    'content': '此卡片是程序化构建的。\n\n**关键指标：**\n- 用户：10,000\n- 收入：\$50,000'
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
    'elements': [{'tag': 'plain_text', 'content': '通过OpenClaudia发送'}]
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

当发送需要中英文内容的消息时，使用支持多地域的富文本`post`格式。飞书将显示与用户语言设置匹配的地域内容。

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

### Webhook响应代码

| 代码 | 状态消息 | 含义 |
|------|---------------|---------|
| 0 | `"success"` | 消息发送成功 |
| 9499 | `"Bad Request"` | JSON格式错误或缺少必填字段 |
| 19001 | `"param invalid"` | `msg_type`或内容格式无效 |
| 19002 | `"sign match fail"` | 签名验证失败（检查时间戳和密钥） |
| 19021 | `"request too fast"` | 速率限制：每个webhook每分钟最多100条消息 |
| 19024 | `"bot not in chat"` | 机器人已从群组中移除 |

### 常见故障排除

**消息未送达：**
- 验证webhook URL是否正确且机器人仍在群组中
- 检查`msg_type`是否与内容结构匹配
- 对于签名webhook，确保时间戳在当前时间1小时内

**卡片未渲染：**
- 验证JSON结构：header和elements都是必需的
- 按钮URL必须以`http://`或`https://`开头
- 卡片中的Markdown支持有限子集：粗体、斜体、链接、列表、表格

**API令牌错误：**
- 租户访问令牌2小时后过期；发送前重新获取
- 确保应用已在开发者控制台发布并获批准
- 验证`im:message:send_as_bot`权限是否已授予

### 速率限制

| 集成 | 限制 |
|-------------|-------|
| 自定义机器人Webhook | 每个webhook每分钟100条消息 |
| 应用机器人API（消息） | 每个应用每秒50条消息 |
| 应用机器人API（令牌刷新） | 每小时500次请求 |

---

## 8. 工作流：将营销内容发送到飞书/钉钉

当用户要求将营销内容发送到飞书或钉钉时，请遵循此工作流：

### 第一步：检查凭证

验证`FEISHU_WEBHOOK_URL`或`FEISHU_APP_ID` + `FEISHU_APP_SECRET`是否已设置。如果没有，请指导用户完成设置。

### 第二步：确定消息类型

| 用户意图 | 推荐格式 |
|-------------|-------------------|
| 快速文本更新 | 纯文本 (`msg_type: text`) |
| 格式化公告 | 富文本 (`msg_type: post`) |
| 带指标的营销报告 | 带列的交互式卡片 |
| 产品发布 | 带按钮的交互式卡片 |
| 活动通知 | 带CTA按钮的交互式卡片 |
| 提醒或警告 | 带红色/橙色标题的交互式卡片 |

### 第三步：撰写消息

- 使用第4节的适当模板
- 根据用户需求调整内容
- 对于双语群组，提供`zh_cn`和`en_us`内容

### 第四步：预览和确认

向用户显示完整的JSON负载。解释消息将如何显示。

**未经明确用户确认，切勿自动发送。**

### 第五步：发送

执行curl命令并报告响应。

### 第六步：验证

检查响应代码。如果`code: 0`，消息已送达。如果有错误，使用上表进行故障排除。

---

## 9. 高级：消息卡片JSON Schema快速参考

```
{
  "msg_type": "interactive",
  "card": {
    "header": {                          // 必需
      "title": {
        "tag": "plain_text",
        "content": "string"
      },
      "template": "blue|green|red|..."   // 标题颜色
    },
    "elements": [                        // 必需，块数组
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
      {                                      // 页脚注释
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": "..."}]
      }
    ]
  }
}
```

---

## 小贴士

- **从webhooks开始。** 自定义机器人Webhooks无需代码基础设施，可在一分钟内设置。
- **使用交互式卡片**发送任何超出简单文本的内容。它们更易读且更具可操作性。
- **在每张营销卡片中**包含操作按钮。引导收件人前往着陆页、仪表板或注册表单。
- **利用双语支持**，如果您的团队使用飞书和钉钉，或成员分布在中国和国际上。
- **尊重速率限制。** 对于批量消息（例如，向多个群组发送），在请求之间添加1秒延迟。
- **先在私人群组中测试**，再向大型团队频道发送。
- **保持卡片内容简洁。** 卡片的最大内容大小约为30KB。对于非常长的报告，链接到外部页面。
- **使用飞书消息卡片构建器**进行视觉卡片设计：[https://open.feishu.cn/tool/cardbuilder](https://open.feishu.cn/tool/cardbuilder)（飞书）或 [https://open.larksuite.com/tool/cardbuilder](https://open.larksuite.com/tool/cardbuilder)（钉钉）。
