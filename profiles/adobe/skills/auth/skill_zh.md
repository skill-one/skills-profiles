# AEM Edge Delivery Services 认证

认证以获取用于所有 Edge Delivery Services 管理操作的令牌。自动检测身份提供者，从 org+site 自动检测 — 无需询问内容源。打开用户的默认浏览器进行登录，并通过本地回调服务器接收令牌。

## 令牌使用

`authToken` 对管理 API 有效：

| API | 头部 | 使用 |
|-----|------|------|
| `admin.hlx.page` | `x-auth-token: ${AUTH_TOKEN}` | 预览、发布、状态、代码同步、作业、日志、配置 |
| 配置服务 | `x-auth-token: ${AUTH_TOKEN}` | 网站、配置、密钥、API 密钥、配置文件 |

> **注意：** `admin.da.live` 使用单独的 Adobe IMS 令牌，带有 `Authorization: Bearer` 头部。请参阅 `ops/resources/da.md` 中的 DA 特定登录流程。

## 何时使用此技能

- API 返回 401 未授权
- 用户说“登录”、“认证”、“auth”
- 在缺少/过期令牌时进行任何管理操作之前
- 在生成需要 API 访问的指南之前

## 前置条件

- 已安装 Node.js

---

## 认证流程

### 第 1 步：检查现有令牌

令牌在 **用户级别** (`~/.aem/ims-token.json`) 缓存，跨所有项目共享。

```bash
mkdir -p "${HOME}/.aem"

AUTH_TOKEN=$(node -e "
  const fs = require('fs');
  try {
    const t = JSON.parse(fs.readFileSync(process.env.HOME + '/.aem/ims-token.json', 'utf8'));
    if (t.authToken && t.authTokenExpiry > Math.floor(Date.now()/1000) + 60) {
      process.stdout.write(t.authToken);
    }
  } catch (e) {}
")

if [ -n "$AUTH_TOKEN" ]; then
  echo "令牌有效"
  exit 0
fi

echo "令牌缺失或过期。开始登录..."
```

### 第 2 步：解析 Org 和 Site

自动登录端点 `/login/{org}/{site}/main` 自动重定向到正确的身份提供者 — 无需知道内容源。

**从可用来源解析 org 和 site（项目配置、操作配置、git 远程）：**

```bash
# 首先尝试项目配置（传递上下文）
ORG=$(cat .claude-plugin/project-config.json 2>/dev/null | node -e "
  const d = require('fs').readFileSync(0,'utf8');
  try { process.stdout.write(JSON.parse(d).org || ''); } catch(e) {}
")

# 回退到操作配置（操作上下文）
if [ -z "$ORG" ]; then
  ORG=$(node -e "
    const fs = require('fs');
    try {
      const c = JSON.parse(fs.readFileSync(process.env.HOME + '/.aem/ops-config.json', 'utf8'));
      process.stdout.write(c.org || '');
    } catch(e) {}
  ")
fi

# 网站：首先尝试 git 远程，然后操作配置
SITE=$(basename -s .git $(git remote get-url origin 2>/dev/null) 2>/dev/null)
if [ -z "$SITE" ]; then
  SITE=$(node -e "
    const fs = require('fs');
    try {
      const c = JSON.parse(fs.readFileSync(process.env.HOME + '/.aem/ops-config.json', 'utf8'));
      process.stdout.write(c.site || '');
    } catch(e) {}
  ")
fi

echo "org=${ORG:-未设置} site=${SITE:-未设置}"
```

**如果 `ORG` 为空**，询问用户：

> "我需要您的组织名称进行认证。您可以提供：
> - 组织名称（`https://main--site--{org}.aem.page` 中的 `{org}`）
> - 预览/实时 URL，如 `https://main--mysite--myorg.aem.page/`"

**如果用户提供 URL**，从 URL 解析 org 和 site：

```bash
URL="$USER_INPUT"
if echo "$URL" | grep -q '\.aem\.page\|\.aem\.live'; then
  HOST_PART=$(echo "$URL" | cut -d'/' -f3 | cut -d'.' -f1)
  ORG=$(echo "$HOST_PART" | awk -F'--' '{print $NF}')
  SITE=$(echo "$HOST_PART" | awk -F'--' '{print $(NF-1)}')
  echo "从 URL 解析：org=$ORG site=$SITE"
fi
```

**如果 `SITE` 仍然为空**（不在 git 仓库中且未提供 URL），询问用户：

> "我还需要一个网站名称来自动检测您的登录提供者。您的网站名称是什么？（`https://main--{site}--{org}.aem.page` 中的 `{site}` 部分）"

**在 org 和 site 都可用之前，不要继续进行。**

### 第 3 步：通过 Loopback 重定向捕获令牌

打开用户的默认浏览器进行登录。一个临时的本地 HTTP 服务器在登录完成后接收令牌回调。用户必须点击确认页面的“发送”按钮才能传递令牌。适用于所有身份提供者（Adobe IMS、Google、Microsoft）。

**面向用户的消息（在运行以下脚本之前显示）：**

> **浏览器已打开用于登录 `{org}/{site}`。认证后点击“发送”——完成后可以关闭标签页。**

使用粗体/高亮格式，使指令清晰突出。

```bash
mkdir -p "${HOME}/.aem"

node -e "
const http = require('http');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const TOKEN_PATH = path.join(process.env.HOME, '.aem', 'ims-token.json');
const ORG = '${ORG}';
const SITE = '${SITE}';
const STATE = crypto.randomUUID();

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method === 'POST') {
    let body = '';
    req.on('data', (chunk) => { body += chunk; });
    req.on('end', () => {
      try {
        const parsed = JSON.parse(body);
        if (parsed.state !== STATE) {
          console.error('State mismatch — ignoring callback');
          res.writeHead(403);
          res.end('State mismatch');
          return;
        }
        const authToken = parsed.authToken;
        if (authToken) {
          const expiresAt = Math.floor(Date.now() / 1000) + 86400;
          fs.writeFileSync(TOKEN_PATH, JSON.stringify({
            authToken,
            authTokenExpiry: expiresAt,
          }, null, 2));
          try { fs.chmodSync(TOKEN_PATH, 0o600); } catch (e) {}
          console.log('认证成功');
          console.log('令牌缓存于：' + TOKEN_PATH);
          console.log('过期时间：' + new Date(expiresAt * 1000).toISOString());
        } else {
          console.error('回调中没有 authToken。helix-admin authToken 支持可能尚未部署。');
          console.error('接收的键：' + Object.keys(parsed).join(', '));
        }
        res.writeHead(200, { 'content-type': 'text/plain' });
        res.end('OK');
      } catch (e) {
        console.error('解析回调失败：' + e.message);
        res.writeHead(400);
        res.end('Bad request');
      }
      server.close(() => process.exit(0));
    });
  } else if (req.method === 'GET') {
    res.writeHead(200, { 'content-type': 'text/html' });
    res.end('<html><body><p>登录完成。您可以关闭此标签页。</p><script>window.close()</script></body></html>');
  }
});

server.listen(0, () => {
  const port = server.address().port;
  const redirectUri = 'http://localhost:' + port + '/.aem/cli/login/ack';
  const loginUrl = 'https://admin.hlx.page/login/' + ORG + '/' + SITE + '/main?client_id=aem-cli&redirect_uri=' + encodeURIComponent(redirectUri) + '&state=' + STATE + '&selectAccount=true';

  console.log('打开浏览器进行登录...');
  console.log('URL: ' + loginUrl);
  console.log('');
  console.log('登录后，点击发送按钮完成认证。');
  try { execSync('open \"' + loginUrl + '\"'); } catch (e) {
    try { execSync('xdg-open \"' + loginUrl + '\"'); } catch (e2) {
      console.log('无法打开浏览器。请手动打开此 URL：');
      console.log(loginUrl);
    }
  }
});

setTimeout(() => {
  console.error('登录超时（5 分钟）。未收到回调。');
  process.exit(1);
}, 300000);
"
```

---

## 令牌存储

**用户级令牌缓存** — `~/.aem/ims-token.json`：

```json
{
  "authToken": "eyJ...",
  "authTokenExpiry": 1780489855
}
```

| 字段 | 描述 |
|------|------|
| `authToken` | 登录回调中的管理 JWT |
| `authTokenExpiry` | 令牌过期时的 Unix 时间戳（约 24 小时） |

跨此计算机上的每个项目共享。文件以 `0600` 权限写入。

---

## 使用令牌

```bash
# 从用户级缓存读取令牌
AUTH_TOKEN=$(node -e "
  const fs = require('fs');
  try {
    const t = JSON.parse(fs.readFileSync(process.env.HOME + '/.aem/ims-token.json', 'utf8'));
    process.stdout.write(t.authToken || '');
  } catch (e) {}
")

# admin.hlx.page 和 Config Service 使用相同的头部
curl -H "x-auth-token: ${AUTH_TOKEN}" "https://admin.hlx.page/status/{org}/{site}/main/"
curl -H "x-auth-token: ${AUTH_TOKEN}" "https://admin.hlx.page/config/{org}/sites.json"
```

---

## 故障排除

| 问题 | 解决方案 |
|------|--------|
| 浏览器未打开 | 手动打开终端中打印的 URL |
| “发送”按钮无效 | 检查浏览器控制台错误；确保没有广告拦截器阻止本地请求 |
| 回调中没有 authToken | 添加 authToken 到 CLI 登录响应的 helix-admin PR 尚未部署 |
| 未收到令牌 | 确保在 5 分钟超时前点击了确认页面的“发送” |
| 登录后返回 401 | 令牌过期，重新认证 |
| API 返回 403 | 用户对该 org/site 缺乏权限 |
| State mismatch | 另一个进程可能发送了恶意的回调；重新运行登录 |

---

## 工作原理

1. CLI 在随机本地端口上启动临时 HTTP 服务器
2. 打开用户的默认浏览器到 `admin.hlx.page/login/{org}/{site}/main`，带有 `client_id=aem-cli` 和 `redirect_uri=http://localhost:{port}/...`
3. 管理 API 自动检测 IDP（Google、Microsoft、Adobe）并重定向到登录
4. 用户在他们的真实浏览器中认证
5. 登录后，管理 API 显示一个带有“发送”按钮的确认页面
6. 用户点击“发送”——浏览器 POST `{ state, authToken }` 到本地
7. CLI 验证 state nonce，将 `authToken` 保存到 `~/.aem/ims-token.json`，退出

---

## 集成

被调用：`ops`、`handover-admin`、`handover-author`、`handover-developer`、`handover`

```
Skill({ skill: "aem-project-management:auth" })
```
