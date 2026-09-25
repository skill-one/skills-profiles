# WordPress 设置

连接到 WordPress 站点，并通过 WP-CLI 或 REST API 验证可访问性。生成一个经过验证的连接配置，以便进行内容管理和 Elementor 编辑。

## 工作流程

### 第 1 步：检查 WP-CLI

```bash
wp --version
```

如果未安装，请指导用户：

```bash
# macOS/Linux
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp
```

同时确保 SSH 扩展可用（远程站点需要）：

```bash
wp package install wp-cli/ssh-command
```

### 第 2 步：连接到站点

**选项 A：通过 SSH 的 WP-CLI（推荐）**

```bash
wp --ssh=user@hostname/path/to/wordpress option get siteurl
```

常见模式：
- Rocket.net：`wp --ssh=user@hostname/www/sitename/public option get siteurl`
- cPanel：`wp --ssh=user@hostname/public_html option get siteurl`
- 自定义：询问用户 SSH 用户名、主机名和 WordPress 路径

先用一个简单命令测试：

```bash
wp --ssh=user@host/path core version
```

**选项 B：使用应用密码的 REST API**

如果 SSH 不可用：

1. 导航到 `https://example.com/wp-admin/profile.php`（或使用浏览器自动化）
2. 滚动到“应用密码”部分
3. 输入一个名称（例如“Claude Code”），然后点击“添加新应用密码”
4. 复制生成的密码（空格是其一部分，但在认证中可选）

测试连接：

```bash
curl -s https://example.com/wp-json/wp/v2/posts?per_page=1 \
  -u "username:xxxx xxxx xxxx xxxx xxxx xxxx" | jq '.[0].title'
```

### 第 3 步：存储凭证

**对于 WP-CLI SSH** — 在项目根目录中创建 `wp-cli.yml`：

```yaml
ssh:
  sitename:
    cmd: ssh -o StrictHostKeyChecking=no %pseudotty% user@hostname %cmd%
    url: /path/to/wordpress
```

然后使用：`wp @sitename option get siteurl`

**对于 REST API** — 存储在 `.dev.vars` 中：

```
WP_SITE_URL=https://example.com
WP_USERNAME=admin
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

确保 `.dev.vars` 在 `.gitignore` 中。对于跨项目使用，存储在您喜欢的密钥管理器中（环境变量、1Password CLI 等）。

### 第 4 步：验证完全访问权限

运行综合检查：

```bash
# 站点信息
wp @sitename option get siteurl
wp @sitename option get blogname

# 内容访问
wp @sitename post list --post_type=page --posts_per_page=5 --fields=ID,post_title,post_status

# 插件状态（检查 Elementor）
wp @sitename plugin status elementor

# 主题信息
wp @sitename theme status
```

### 第 5 步：保存站点配置

创建 `wordpress.config.json` 以供其他技能参考：

```json
{
  "site": "example.com",
  "siteUrl": "https://example.com",
  "accessMethod": "ssh",
  "sshAlias": "sitename",
  "wpPath": "/path/to/wordpress",
  "hasElementor": true,
  "elementorVersion": "3.x.x"
}
```

---

## 关键模式

### SSH 连接问题

| 症状 | 解决方法 |
|------|---------|
| `Permission denied (publickey)` | 检查 SSH 密钥：`ssh -v user@host` |
| 通过 SSH 的 `wp: command not found` | WP-CLI 未在远程 PATH 中 — 使用完整路径：`/usr/local/bin/wp` |
| `Error: This does not appear to be a WordPress installation` | 路径错误 — 检查 `wp-path` 参数 |
| 大型操作超时 | 添加 `--ssh=user@host/path --allow-root` 或增加 SSH 超时 |

### WP-CLI 别名

在 `~/.wp-cli/config.yml` 中定义常用站点的别名：

```yaml
@client1:
  ssh: user@client1.example.com/www/public
@client2:
  ssh: user@client2.rocketcdn.me/www/client2/public
```

然后：`wp @client1 post list`

### REST API 注意事项

- 应用密码需要 HTTPS（HTTP 上无效）
- 某些安全插件会阻止 REST API — 检查 401/403 响应
- 缓存插件可能会提供过时的 REST 响应 — 使用 `?_=${timestamp}` 缓存破坏器
- 自定义帖子类型需要 `show_in_rest: true` 才能在 API 中显示

---

## 参考文件

- `references/wp-cli-essentials.md` — SSH 别名模式、常用标志和故障排除
