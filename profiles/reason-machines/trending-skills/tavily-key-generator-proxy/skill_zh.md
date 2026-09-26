# Tavily Key Generator + API 代理

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能合集

使用 Playwright + CapSolver（Cloudflare Turnstile）自动化批量 Tavily 账户注册，然后将生成的 API 密钥集中到统一的代理网关，支持轮询轮换、使用跟踪、令牌管理和 Web 控制台。

---

## 功能概述

| 组件 | 位置 | 目的 |
|-------|------|------|
| **密钥生成器** | 根目录 `/` | Playwright 驱动的无头 Firefox 注册 Tavily 账户，解决 Turnstile 验证码，验证邮箱，提取 API 密钥 |
| **API 代理** | `proxy/` | FastAPI 服务，将请求在集中密钥间轮询分发，提供 `/api/search` 和 `/api/extract` 接口，并在 `/console` 提供控制台服务 |

每个免费 Tavily 账户每月可生成 **1,000 次 API 调用**。代理聚合配额：10 个密钥 = 每月 10,000 次调用，通过单一端点访问。

---

## 安装

### 密钥生成器

```bash
git clone https://github.com/skernelx/tavily-key-generator.git
cd tavily-key-generator
pip install -r requirements.txt
playwright install firefox
cp config.example.py config.py
# 使用 config.py 配置 CapSolver 密钥和邮箱后端
python main.py
```

### API 代理（Docker — 推荐）

```bash
cd proxy/
cp .env.example .env
# 在 .env 中设置 ADMIN_PASSWORD
docker compose up -d
# 控制台位于 http://localhost:9874/console
```

---

## 配置 (`config.py`)

### 验证码解决器（必需）

```python
# CapSolver — 推荐 (~$0.001/次解决，高成功率）
CAPTCHA_SOLVER = "capsolver"
CAPSOLVER_API_KEY = "CAP-..."   # 从 capsolver.com 获取

# 浏览器点击备选方案 — 免费，但成功率低
CAPTCHA_SOLVER = "browser"
```

### 邮箱后端（必需 — 选择一项）

**选项 A：Cloudflare Email Worker（自托管，免费）**

```python
EMAIL_BACKEND = "cloudflare"
EMAIL_DOMAIN = "mail.yourdomain.com"
EMAIL_API_URL = "https://mail.yourdomain.com"
EMAIL_API_TOKEN = "your-worker-token"
```

**选项 B：DuckMail（第三方临时邮箱）**

```python
EMAIL_BACKEND = "duckmail"
DUCKMAIL_API_BASE = "https://api.duckmail.sbs"
DUCKMAIL_BEARER = "dk_..."
DUCKMAIL_DOMAIN = "duckmail.sbs"
```

如果配置了两个后端，CLI 在运行时将提示您选择。

### 注册速率限制（防封禁）

```python
THREADS = 2                  # 最大 3 — 更多 = 更高的封禁风险
COOLDOWN_BASE = 45           # 注册间隔秒数
COOLDOWN_JITTER = 15         # 随机附加秒数
BATCH_LIMIT = 20             # 此数量注册后暂停
```

### 自动上传到代理（可选）

```python
PROXY_AUTO_UPLOAD = True
PROXY_URL = "http://localhost:9874"
PROXY_ADMIN_PASSWORD = "your-admin-password"
```

---

## 运行密钥生成器

```bash
python main.py
# 提示：生成多少密钥，选择哪个邮箱后端
# 输出：包含所有生成密钥的 api_keys.md
# 如果 PROXY_AUTO_UPLOAD=True，密钥将自动推送到代理
```

生成的 `api_keys.md` 格式（用于批量导入代理）：

```
tvly-abc123...
tvly-def456...
tvly-ghi789...
```

---

## API 代理使用

### 调用代理（即插即用的 Tavily 替代方案）

```bash
# 搜索 — 仅替换基础 URL
curl -X POST http://your-server:9874/api/search \
  -H "Authorization: Bearer tvly-YOUR_PROXY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "最新 AI 新闻", "search_depth": "basic"}'

# 提取
curl -X POST http://your-server:9874/api/extract \
  -H "Authorization: Bearer tvly-YOUR_PROXY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com/article"]}'
```

令牌也可以作为请求体传递 `api_key`（兼容 Tavily SDK）：

```python
import requests

response = requests.post(
    "http://your-server:9874/api/search",
    json={
        "query": "Python 网络爬虫",
        "api_key": "tvly-YOUR_PROXY_TOKEN"
    }
)
print(response.json())
```

### Python SDK 集成

```python
from tavily import TavilyClient

# 将 SDK 指向您的代理 — 无需其他更改
client = TavilyClient(
    api_key="tvly-YOUR_PROXY_TOKEN",
    base_url="http://your-server:9874"
)

results = client.search("2025 机器学习趋势")
```

---

## 管理员 API 参考

所有管理员端点需要头部：`X-Admin-Password: your-password`

### 密钥管理

```bash
# 列出所有密钥
curl http://localhost:9874/api/keys \
  -H "X-Admin-Password: secret"

# 添加单个密钥
curl -X POST http://localhost:9874/api/keys \
  -H "X-Admin-Password: secret" \
  -H "Content-Type: application/json" \
  -d '{"key": "tvly-abc123..."}'

# 批量从 api_keys.md 文本导入
curl -X POST http://localhost:9874/api/keys \
  -H "X-Admin-Password: secret" \
  -H "Content-Type: application/json" \
  -d '{"bulk": "tvly-abc...\ntvly-def...\ntvly-ghi..."}'

# 切换密钥启用/禁用
curl -X PUT http://localhost:9874/api/keys/{id}/toggle \
  -H "X-Admin-Password: secret"

# 删除密钥
curl -X DELETE http://localhost:9874/api/keys/{id} \
  -H "X-Admin-Password: secret"
```

### 令牌管理

```bash
# 创建访问令牌
curl -X POST http://localhost:9874/api/tokens \
  -H "X-Admin-Password: secret" \
  -H "Content-Type: application/json" \
  -d '{"label": "my-app"}'
# 返回：{"token": "tvly-...", "id": "..."}

# 列出令牌
curl http://localhost:9874/api/tokens \
  -H "X-Admin-Password: secret"

# 删除令牌
curl -X DELETE http://localhost:9874/api/tokens/{id} \
  -H "X-Admin-Password: secret"
```

### 统计

```bash
curl http://localhost:9874/api/stats \
  -H "X-Admin-Password: secret"
# 返回：total_quota, used, remaining, active_keys, disabled_keys
```

### 修改管理员密码

```bash
curl -X PUT http://localhost:9874/api/password \
  -H "X-Admin-Password: current-password" \
  -H "Content-Type: application/json" \
  -d '{"new_password": "new-secure-password"}'
```

---

## 代理行为

- **轮询轮换**：请求均匀分配到活跃密钥
- **自动禁用**：连续 3 次失败后禁用密钥
- **配额跟踪**：总计 = 活跃密钥 × 每月 1,000 次；添加/删除/切换时自动更新
- **令牌格式**：代理令牌使用 `tvly-` 前缀，对客户端与真实 Tavily 密钥无法区分

---

## 代理 `.env` 配置

```env
ADMIN_PASSWORD=change-this-immediately
PORT=9874
# 可选：限制 CORS 源
CORS_ORIGINS=https://myapp.com,https://app2.com
```

---

## Nginx 反向代理 + HTTPS

```nginx
server {
    listen 443 ssl;
    server_name tavily-proxy.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:9874;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 集成模式：自动补充池

```python
# replenish.py — 在 Cron 中低配额时运行
import requests

PROXY_URL = "http://localhost:9874"
ADMIN_PASSWORD = "your-password"
MIN_ACTIVE_KEYS = 10

def get_stats():
    r = requests.get(f"{PROXY_URL}/api/stats",
                     headers={"X-Admin-Password": ADMIN_PASSWORD})
    return r.json()

def trigger_registration(count: int):
    """调用您的密钥生成器作为子进程或直接导入"""
    import subprocess
    subprocess.run(["python", "main.py", "--count", str(count)], check=True)

stats = get_stats()
active = stats["active_keys"]
if active < MIN_ACTIVE_KEYS:
    needed = MIN_ACTIVE_KEYS - active
    print(f"池低 ({active} 密钥)，注册更多 {needed} 个...")
    trigger_registration(needed)
```

---

## 故障排除

| 问题 | 原因 | 解决方法 |
|-------|------|---------|
| 验证码解决失败 | Tavily 提升了机器人检测 | 暂停数小时，将 `THREADS` 减至 1 |
| 邮箱验证超时 | 邮件发送缓慢 | 在配置中增加轮询超时 |
| 密钥在代理中立即禁用 | Tavily 账户被标记/暂停 | 从不同 IP 注册 |
| `playwright install firefox` 失败 | 缺少系统依赖 | 先运行 `playwright install-deps firefox` |
| Docker compose 端口冲突 | 9874 正在使用 | 在 `.env` 和 `docker-compose.yml` 中更改 `PORT` |
| `X-Admin-Password` 401 | 密码错误 | 检查 `.env`，更改后重启容器 |
| 注册期间 IP 被封 | 注册过多 | 使用 `BATCH_LIMIT=10`，批次间等待数小时 |

### 安全设置

```python
# 保守 — 最小化封禁风险
THREADS = 1
COOLDOWN_BASE = 60
COOLDOWN_JITTER = 30
BATCH_LIMIT = 10
```

---

## 安全检查清单

- [ ] 部署后立即更改 `ADMIN_PASSWORD` 从默认值
- [ ] 将 `config.py` 添加到 `.gitignore`（已包含，推送前验证）
- [ ] 生产环境部署在 HTTPS 后面
- [ ] 定期轮换代理令牌
- [ ] 永远不要将 `api_keys.md` 提交到公共仓库
