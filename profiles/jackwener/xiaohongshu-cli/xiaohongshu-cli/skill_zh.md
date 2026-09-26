# xiaohongshu-cli — 小红书CLI工具

**二进制文件:** `xhs`
**凭证:** 浏览器Cookie（自动提取）或浏览器辅助二维码登录 (`--qrcode`)

## 安装

```bash
# 安装（需要Python 3.10+）
uv tool install xiaohongshu-cli
# 或者: pipx install xiaohongshu-cli

# 升级到最新版本（推荐以避免API错误）
uv tool upgrade xiaohongshu-cli
# 或者: pipx upgrade xiaohongshu-cli
```

## 认证

**代理注意事项**: 在执行任何 `xhs` 命令之前，请先检查凭证是否存在。不要假设Cookie已配置。

### 第0步：检查是否已认证

```bash
xhs status --yaml >/dev/null && echo "AUTH_OK" || echo "AUTH_NEEDED"
```

如果 `AUTH_OK`，跳转到 [命令参考](#命令参考)。
如果 `AUTH_NEEDED`，继续第1步。当浏览器Cookie提取不可用时，但可以启动浏览器时，优先使用 `--qrcode`。

### 第1步：引导用户进行认证

确保用户在任何支持 [browser_cookie3](https://github.com/borisbabic/browser_cookie3) 的浏览器中登录了 xiaohongshu.com。支持的浏览器：Chrome、Arc、Edge、Firefox、Safari、Brave、Chromium、Opera、Opera GX、Vivaldi、LibreWolf、Lynx、w3m。然后：

```bash
xhs login                              # 自动检测带有有效Cookie的浏览器
xhs login --cookie-source arc          # 显式指定浏览器
xhs login --qrcode                     # 浏览器辅助二维码登录，终端输出二维码
```

验证：

```bash
xhs status
xhs whoami
```

### 第2步：处理常见的认证问题

| 症状 | 代理操作 |
|------|---------|
| `NoCookieError: 未找到'a1' Cookie` | 指导用户在浏览器中登录 xiaohongshu.com |
| `NeedVerifyError: 需要验证码` | 要求用户打开浏览器，完成验证码，然后重试 |
| `IpBlockedError: IP被封锁` | 建议切换网络（热点/VPN） |
| `SessionExpiredError` | 运行 `xhs login` 刷新Cookie |

## 代理默认设置

所有机器可读的输出使用 [SCHEMA.md](./SCHEMA.md) 中记录的封套。
有效负载存储在 `.data` 下。

- 非TTY标准输出 → 自动YAML
- `--json` / `--yaml` → 显式格式
- `OUTPUT=json` 环境变量 → 全局覆盖
- `OUTPUT=rich` 环境变量 → 强制人类输出

## 命令参考

### 读取

| 命令 | 描述 | 示例 |
|------|------|------|
| `xhs search <关键词>` | 搜索笔记 | `xhs search "美食" --sort popular --type video` |
| `xhs read <id_or_url_or_index>` | 通过ID、URL或短索引读取笔记 | `xhs read 1` / `xhs read "https://...?xsec_token=xxx"` |
| `xhs comments <id_or_url_or_index>` | 通过ID、URL或短索引获取评论 | `xhs comments 1` / `xhs comments "https://...?xsec_token=..."` |
| `xhs comments <id_or_url> --all` | 获取所有评论（自动分页） | `xhs comments "<url>" --all --json` |
| `xhs sub-comments <note_id> <comment_id>` | 获取评论的回复 | `xhs sub-comments abc 123` |
| `xhs user <user_id>` | 查看用户资料 | `xhs user 5f2e123` |
| `xhs user-posts <user_id>` | 列出用户的笔记 | `xhs user-posts 5f2e123 --cursor ""` |
| `xhs feed` | 浏览推荐信息流 | `xhs feed --yaml` |
| `xhs hot` | 浏览热门笔记 | `xhs hot -c food` |
| `xhs topics <关键词>` | 搜索话题/标签 | `xhs topics "旅行"` |
| `xhs search-user <关键词>` | 搜索用户 | `xhs search-user "摄影"` |
| `xhs my-notes` | 列出自己发布的笔记 | `xhs my-notes --page 0` |
| `xhs notifications` | 查看通知 | `xhs notifications --type likes` |
| `xhs unread` | 显示未读数量 | `xhs unread --json` |

### 交互（写入）

| 命令 | 描述 | 示例 |
|------|------|------|
| `xhs like <id_or_url_or_index>` | 点赞笔记 | `xhs like 1` / `xhs like abc123` |
| `xhs like <id_or_url_or_index> --undo` | 取消点赞笔记 | `xhs like 1 --undo` |
| `xhs favorite <id_or_url_or_index>` | 收藏笔记 | `xhs favorite 1` |
| `xhs unfavorite <id_or_url_or_index>` | 取消收藏 | `xhs unfavorite 1` |
| `xhs comment <id_or_url_or_index> -c "text"` | 发布评论 | `xhs comment 1 -c "好看！"` |
| `xhs reply <id_or_url_or_index> --comment-id ID -c "text"` | 回复评论 | `xhs reply 1 --comment-id 456 -c "谢谢"` |
| `xhs delete-comment <note_id> <comment_id>` | 删除自己的评论 | `xhs delete-comment abc 123 -y` |

### 社交

| 命令 | 描述 | 示例 |
|------|------|------|
| `xhs follow <user_id>` | 关注用户 | `xhs follow 5f2e123` |
| `xhs unfollow <user_id>` | 取消关注用户 | `xhs unfollow 5f2e123` |
| `xhs favorites [user_id]` | 列出收藏的笔记（默认为自身） | `xhs favorites --json` |

### 创作者

| 命令 | 描述 | 示例 |
|------|------|------|
| `xhs post --title "..." --body "..." --images img.png` | 发布笔记 | `xhs post --title "Test" --body "Hello"` |
| `xhs delete <id_or_url>` | 删除自己的笔记 | `xhs delete abc123 -y` |

### 账户

| 命令 | 描述 |
|------|------|
| `xhs login` | 从浏览器提取Cookie（自动检测） |
| `xhs login --qrcode` | 浏览器辅助二维码登录 — 终端输出二维码，浏览器完成登录 |
| `xhs status` | 检查认证状态 |
| `xhs logout` | 清除缓存的Cookie |
| `xhs whoami` | 显示当前用户资料 |

## 代理工作流示例

### 搜索 → 读取 → 点赞流程

```bash
NOTE_ID=$(xhs search "美食推荐" --json | jq -r '.data.items[0].id')
xhs read "$NOTE_ID" --json | jq '.data'
xhs like "$NOTE_ID"
```

### 浏览热门美食笔记

```bash
xhs hot -c food --json | jq '.data.items[:5] | .[].note_card | {title, likes: .interact_info.liked_count}'
```

### 获取用户信息然后关注

```bash
xhs user 5f2e123 --json | jq '.data.basic_info | {nickname, user_id}'
xhs follow 5f2e123
```

### 检查通知

```bash
xhs unread --json | jq '.data'
xhs notifications --type mentions --json | jq '.data.message_list[:5]'
```

### 分析笔记的所有评论

```bash
# 获取所有评论并分析主题
xhs comments "$NOTE_URL" --all --json | jq '.data.comments | length'
# 统计问题数量
xhs comments "$NOTE_URL" --all --json | jq '[.data.comments[] | select(.content | test("[\uff1f?]"))] | length'
```

### 每日阅读工作流

```bash
# 浏览推荐信息流
xhs feed --yaml

# 交互式短索引工作流
xhs search "旅行"
xhs read 1
xhs comments 1
xhs like 1
xhs favorite 1
xhs comment 1 -c "收藏了"

# 按类别浏览热门
xhs hot -c food --yaml
xhs hot -c travel --yaml
```

### 二维码登录

```bash
# 当浏览器Cookie提取不可用时
xhs login --qrcode
# → 启动浏览器辅助登录流程
# → 使用Unicode半块在终端渲染二维码
# → 使用小红书应用扫描 → 确认 → 导出Cookie
```

### URL到洞察流程

```bash
# 用户粘贴URL → 读取 + 所有评论
xhs read "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --json
xhs comments "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --all --json
```

## 热门类别

可用于 `xhs hot -c <类别>`:
`fashion`、`food`、`cosmetics`、`movie`、`career`、`love`、`home`、`gaming`、`travel`、`fitness`

## 错误代码

结构化错误代码返回在 `error.code` 字段：
- `not_authenticated` — Cookie过期或缺失
- `verification_required` — 需要验证码/验证
- `ip_blocked` — IP速率限制
- `signature_error` — 请求签名失败
- `api_error` — 上游API错误
- `unsupported_operation` — 操作不可用

## 限制

- **无法下载视频** — 无法下载笔记图片/视频
- **无法访问私信** — 无法访问私信
- **无法直播** — 不支持直播功能
- **无法查看关注/粉丝列表** — XHS网页API不暴露这些端点
- **单账户** — 一次一组Cookie
- **速率限制** — 内置高斯抖动延迟（~1-1.5秒）请求之间；激进使用可能触发验证码或IP封锁

## 代理反检测注意事项

- **不要并行化请求** — 内置速率限制延迟存在是为了账户安全
- **验证码恢复**: 如果 `NeedVerifyError` 发生，客户端会自动冷却，延迟逐渐增加（5s→10s→20s→30s）。要求用户在浏览器中完成验证码后重试
- **批量操作**: 当进行大量工作（例如，读取许多笔记）时，在CLI调用之间添加 `time.sleep()`
- **会话稳定性**: 会话中的所有请求共享一致的浏览器指纹。重启CLI会创建新的指纹会话

## 安全注意事项

- 不要要求用户在聊天记录中分享原始Cookie值。
- 优先使用本地浏览器Cookie提取，而不是手动复制/粘贴密钥。
- 如果认证失败，要求用户通过 `xhs login` 重新登录。
- 代理应将Cookie值视为密钥（不要不必要的输出到stdout）。
- 内置速率限制延迟保护账户；不要绕过它。
