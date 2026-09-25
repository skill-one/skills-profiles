# 微信文章发布工具

通过 API 将 Markdown 或 HTML 内容发布到微信公众号草稿箱，并自动转换格式。

## 前置条件

- 设置 WECHAT_API_KEY 环境变量（来自 .env 文件）
- Python 3.9+
- 在 wx.limyai.com 上已授权的微信公众号

## 脚本

位于 `~/.claude/skills/wechat-article-publisher/scripts/`：

### wechat_api.py
微信 API 客户端，用于列出账号和发布文章：
```bash
# 列出授权账号
python wechat_api.py list-accounts

# 从 Markdown 文件发布
python wechat_api.py publish --appid <wechat_appid> --markdown /path/to/article.md

# 从 HTML 文件发布（保留格式）
python wechat_api.py publish --appid <wechat_appid> --html /path/to/article.html

# 使用自定义选项发布
python wechat_api.py publish --appid <appid> --markdown /path/to/article.md --type newspic
```

### parse_markdown.py
解析 Markdown 并提取结构化数据（可选，用于高级使用）：
```bash
python parse_markdown.py <markdown_file> [--output json|html]
```

## 工作流程

**策略："API 优先发布"**

与基于浏览器的发布不同，此技能使用直接 API 调用以实现可靠、快速的发布。

1. 从环境加载 WECHAT_API_KEY
2. 列出可用的微信公众号（如果用户未指定）
3. 检测文件格式（Markdown 或 HTML）并相应解析
4. 调用发布 API 在微信中创建草稿
5. 报告成功并附带草稿详情

**支持的文件格式：**
- `.md` 文件 → 解析为 Markdown，由微信 API 转换
- `.html` 文件 → 作为 HTML 发送，保留格式

## 分步指南

### 第 1 步：检查 API 密钥

在进行任何操作之前，验证 API 密钥是否可用：

```bash
# 检查 .env 文件是否存在且包含 WECHAT_API_KEY
cat .env | grep WECHAT_API_KEY
```

如果未设置，提醒用户：
1. 将 `.env.example` 复制到 `.env`
2. 设置他们的 `WECHAT_API_KEY` 值

### 第 2 步：列出可用账号

获取授权的微信公众号列表：

```bash
python ~/.claude/skills/wechat-article-publisher/scripts/wechat_api.py list-accounts
```

输出示例：
```json
{
  "success": true,
  "data": {
    "accounts": [
      {
        "name": "我的公众号",
        "wechatAppid": "wx1234567890",
        "username": "gh_abc123",
        "type": "subscription",
        "verified": true,
        "status": "active"
      }
    ],
    "total": 1
  }
}
```

**重要**：
- 如果只有一个账号，自动使用
- 如果有多个账号，要求用户选择
- 记下 `wechatAppid` 用于发布

### 第 3 步：发布文章

**对于 Markdown 文件：**
```bash
python ~/.claude/skills/wechat-article-publisher/scripts/wechat_api.py publish \
  --appid <wechatAppid> \
  --markdown /path/to/article.md
```

**对于 HTML 文件（保留格式）：**
```bash
python ~/.claude/skills/wechat-article-publisher/scripts/wechat_api.py publish \
  --appid <wechatAppid> \
  --html /path/to/article.html
```

**对于 小绿书（图文模式）：**
```bash
python ~/.claude/skills/wechat-article-publisher/scripts/wechat_api.py publish \
  --appid <wechatAppid> \
  --markdown /path/to/article.md \
  --type newspic
```

成功响应：
```json
{
  "success": true,
  "data": {
    "publicationId": "uuid-here",
    "materialId": "uuid-here",
    "mediaId": "wechat-media-id",
    "status": "published",
    "message": "文章已成功发布到公众号草稿箱"
  }
}
```

### 第 4 步：报告结果

发布成功后：
- 确认草稿已创建
- 提醒用户在微信管理后台手动预览并发布
- 提供任何相关 ID 以供参考

## API 参考

### 认证

所有 API 请求都需要 `X-API-Key` 头：
```
X-API-Key: WECHAT_API_KEY
```

### 获取账号列表

```
POST https://wx.limyai.com/api/openapi/wechat-accounts
```

### 发布文章

```
POST https://wx.limyai.com/api/openapi/wechat-publish
```

参数：
| 参数 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| wechatAppid | string | 是 | 微信 AppID |
| title | string | 是 | 文章标题（最多 64 字符） |
| content | string | 是 | 文章内容（Markdown/HTML） |
| summary | string | 否 | 文章摘要（最多 120 字符） |
| coverImage | string | 否 | 封面图片 URL |
| author | string | 否 | 作者名称 |
| contentFormat | string | 否 | 'markdown'（默认）或 'html' |
| articleType | string | 否 | 'news'（默认）或 'newspic' |

### 错误代码

| 代码 | 描述 |
|------|------|
| API_KEY_MISSING | 未提供 API 密钥 |
| API_KEY_INVALID | API 密钥无效 |
| ACCOUNT_NOT_FOUND | 账号不存在或未授权 |
| ACCOUNT_TOKEN_EXPIRED | 账号授权已过期 |
| INVALID_PARAMETER | 无效参数 |
| WECHAT_API_ERROR | 微信 API 调用失败 |
| INTERNAL_ERROR | 服务器错误 |

## 严格规则

1. **绝不自动发布** - 仅保存到草稿，用户手动发布
2. **先检查 API 密钥** - 配置不当则快速失败
3. **先列出账号** - 用户可能有多个账号
4. **优雅处理错误** - 显示清晰的错误信息
5. **保留原始内容** - 不必要地修改用户 Markdown

## 支持的格式

### Markdown 文件 (.md)
- H1 标题 (# ) → 文章标题
- H2/H3 标题 (##, ###) → 章节标题
- 粗体 (**text**)
- 斜体 (*text*)
- 链接 [text](url)
- 引用 (> )
- 代码块 (``` ... ```)
- 列表 (- 或 1.)
- 图片 ![alt](url) → 自动上传到微信

### HTML 文件 (.html)
- `<title>` 或 `<h1>` → 文章标题
- 保留所有 HTML 格式（样式、表格等）
- `<img>` 标签 → 图片自动上传到微信
- 第一个 `<p>` → 自动提取为摘要
- 支持内联样式和丰富格式

**HTML 标题提取优先级：**
1. `<title>` 标签内容
2. 第一个 `<h1>` 标签内容
3. "Untitled" 作为备用

**HTML 内容提取：**
- 如果存在 `<body>`，使用 body 内容
- 否则，移除 `<html>`、`<head>`、`<!DOCTYPE>` 并使用剩余内容

## 文章类型

### news (普通文章)
- 标准 WeChat 文章格式
- 支持 Markdown/HTML
- 富文本与图片

### newspic (小绿书/图文消息)
- 图片导向格式（类似 Instagram 发布）
- 最多提取 20 张图片
- 文字内容限制为 1000 字符
- 图片自动上传到微信

## 示例流程

### Markdown 文件
用户: "把 ~/articles/ai-tools.md 发布到微信公众号"

```bash
# 第 1 步：验证 API 密钥
cat .env | grep WECHAT_API_KEY

# 第 2 步：列出账号
python ~/.claude/skills/wechat-article-publisher/scripts/wechat_api.py list-accounts

# 第 3 步：发布（假设单个账号 appid 为 wx1234567890）
python ~/.claude/skills/wechat-article-publisher/scripts/wechat_api.py publish \
  --appid wx1234567890 \
  --markdown ~/articles/ai-tools.md

# 第 4 步：报告
# "文章已成功发布到公众号草稿箱！请登录微信公众平台预览并发布。"
```

### HTML 文件
用户: "把这个 HTML 文章发布到公众号：~/articles/newsletter.html"

```bash
# 第 1 步：验证 API 密钥
cat .env | grep WECHAT_API_KEY

# 第 2 步：列出账号
python ~/.claude/skills/wechat-article-publisher/scripts/wechat_api.py list-accounts

# 第 3 步：发布 HTML（自动检测格式）
python ~/.claude/skills/wechat-article-publisher/scripts/wechat_api.py publish \
  --appid wx1234567890 \
  --html ~/articles/newsletter.html

# 第 4 步：报告
# "文章已成功发布到公众号草稿箱！HTML 格式已保留。请登录微信公众平台预览并发布。"
```

## 错误处理

### API 密钥未找到
```
Error: WECHAT_API_KEY 环境变量未设置。
```
**解决方案**：要求用户设置包含 API 密钥的 `.env` 文件。

### 账号未找到
```
Error: ACCOUNT_NOT_FOUND - 公众号不存在或未授权
```
**解决方案**：要求用户在 wx.limyai.com 授权账号。

### 令牌过期
```
Error: ACCOUNT_TOKEN_EXPIRED - 公众号授权已过期
```
**解决方案**：要求用户在 wx.limyai.com 重新授权。

### 微信 API 错误
```
Error: WECHAT_API_ERROR - 微信接口调用失败
```
**解决方案**：可能是临时问题，重试或检查微信服务状态。

## 最佳实践

### 为什么使用 API 而不是浏览器自动化？

1. **可靠性**：直接 API 调用比浏览器自动化更稳定
2. **速度**：无需启动浏览器、加载页面或 UI 交互
3. **简单性**：单条命令即可发布
4. **可移植性**：任何有 Python 的系统均可运行（无 macOS 专属依赖）

### 内容指南

1. **图片**：尽可能使用公共 URL；本地图片将自动上传
2. **标题**：保持在 64 字符以内
3. **摘要**：未提供时自动提取第一段
4. **封面**：Markdown 中的第一张图片将作为封面（如果未指定）

### 工作流程效率

```
最小化工作流程（1 条命令）：
- list-accounts → 获取 appid → publish → 完成

完整工作流程（带验证）：
1. 检查 .env → 列出账号 → 确认用户
2. 带选项发布 → 报告结果
```

## 故障排除

### Q: 如何获取 WECHAT_API_KEY？
A: 在 wx.limyai.com 注册并授权您的微信公众号以获取 API 密钥。

### Q: 我可以发布到多个账号吗？
A: 是的，使用 `list-accounts` 查看所有授权账号，然后指定目标 `--appid`。

### Q: 图片在微信中不显示？
A: 确保图片是可访问的 URL。本地图片将自动上传，但路径错误可能导致失败。

### Q: 标题太长？
A: WeChat 标题限制为 64 字符。脚本将使用 H1 的前 64 个字符。

### Q: news 和 newspic 有什么区别？
A: `news` 是标准文章格式；`newspic`（小绿书）是图片导向，文字限制为 1000 字符。

## 新手上路（用户不知道该输入什么时，走这里）

**触发**：`/公众号发布 新手`、「这个怎么用」「第一次用」「能干嘛」「带我走一遍」，
以及用户输入了技能名却没有给任何任务的时候。

这个模式的铁律：**不假设、不索取**。用户可能什么都没准备，
不要一上来就问他要文件、要 API key、要具体需求。按下面四步走：

**一、先说清楚这是什么（三句话以内）**

一句话：**把 Markdown 文章直接发进公众号草稿箱**，图片自动上传。
走的是微信官方接口，不是模拟点击，所以稳定。
发的是草稿，最终点「发表」的还是你。

**二、给编号选项，让他按回车就能继续**

不要问开放式问题（「你想做什么？」对新手是负担）。给 3 个选项加一个默认：

```
想先看哪个？（直接回车 = 1）
  1. 先看看发出去长什么样（示例）
  2. 把我的 Markdown 发成草稿
  3. 先讲讲要准备什么
```

**三、直接演示一遍，边做边解释**

选完立刻做给他看，用**示例数据**，不需要他提供任何东西。
每做完一步，加一行「💡 刚才发生了什么」，一句话说明这步的意义。

**四、毕业**

演示完只问一个是非题：「要不要用你自己的文章真跑一遍？」
答是就进正常流程；答否就告诉他随时回来输 `/公众号发布 新手`。

**关于前置条件**：这个技能需要 公众号的 API 凭据（写在 .env 里的 WECHAT_API_KEY）。
**新手模式下不要提前索取**——先用示例数据演示完，到第四步真跑的时候再引导他配置，
并说清楚在哪配、怎么拿。新手最容易在这一步流失。
