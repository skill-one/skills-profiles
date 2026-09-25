# 网页内容抓取器

给定一个 URL，将其主要内容以干净的 Markdown 格式返回——标题、链接、图片、列表、代码块等均保持原样。

## 抓取策略

始终对每个 URL 尝试**一种方法**——不要盲目级联。从一开始就选择正确的方法。

```
URL
 │
 ├─ 1. Scrapling 脚本（首选）
 │     运行 fetch.py — 检查域名路由表以决定使用 fast 还是 --stealth。
 │     适用于大多数网站。直接返回干净的 Markdown。
 │
 └─ 2. Jina Reader（备用——仅当 Scrapling 失败或依赖未安装时使用）
       web_fetch("https://r.jina.ai/<url>")
       免费套餐：每天 200 次请求。快速（~1-2 秒），Markdown 输出良好。
       不适用于：微信（403）、某些中文平台。
```

### Scrapling 脚本

```bash
python3 <SKILL_DIR>/scripts/fetch.py "<url>" [max_chars] [--stealth]
```

`<SKILL_DIR>` 是存放此 SKILL.md 的目录。调用脚本前需解析它。

该脚本内置两种模式：
- **默认（快速）：** HTTP 抓取，~1-3 秒，适用于大多数网站
- **`--stealth`：** 无头浏览器，~5-15 秒，用于 JS 渲染或反爬网站

当未使用 `--stealth` 运行时，若快速结果内容过少，脚本会自动切换至 stealth 模式。因此你很少需要手动指定 `--stealth`——唯一需要强制使用的情况是当已知网站需要（见路由表），这可以节省初始快速尝试的时间。

## 域名路由

使用此表在首次调用时选择正确的模式：

| 域名                     | 命令                     | 原因               |
|--------------------------|--------------------------|--------------------|
| `mp.weixin.qq.com`       | `fetch.py <url> --stealth` | JS 渲染内容       |
| `zhuanlan.zhihu.com`    | `fetch.py <url> --stealth` | 反爬 + JS         |
| `juejin.cn`             | `fetch.py <url> --stealth` | JS 渲染 SPA       |
| `sspai.com`             | `fetch.py <url>`         | 静态 HTML         |
| `blog.csdn.net`         | `fetch.py <url>`         | 静态 HTML         |
| `ruanyifeng.com`        | `fetch.py <url>`         | 静态博客         |
| `openai.com`            | `fetch.py <url>`         | 静态 HTML         |
| `blog.google`           | `fetch.py <url>`         | 静态 HTML         |
| 其他所有                 | `fetch.py <url>`         | 自动回退处理     |

## 脚本选项

```bash
# 基本——自动选择 fast 或 stealth
python3 <SKILL_DIR>/scripts/fetch.py "https://sspai.com/post/73145"

# 对已知 JS 重的网站强制 stealth
python3 <SKILL_DIR>/scripts/fetch.py "https://mp.weixin.qq.com/s/xxx" --stealth

# 限制输出为 15000 字符（默认：30000）
python3 <SKILL_DIR>/scripts/fetch.py "https://example.com/article" 15000

# 带元数据的 JSON 输出（url、mode、selector、content_length）
python3 <SKILL_DIR>/scripts/fetch.py "https://example.com" --json
```

## 安装依赖

首先单独使用——脚本会检查并告知缺失项：

```bash
pip install scrapling html2text
```

若在系统管理的 Python（macOS/Linux）上，请添加 `--break-system-packages` 或使用 venv。

## 失败规则

- 同一 URL 失败一次 → 放弃，告知用户“无法从该 URL 抽取内容”
- 不要重试——每次失败都会消耗上下文 token
