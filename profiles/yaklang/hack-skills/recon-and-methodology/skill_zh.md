# 技能：侦察与方法论 — 专家 Bug Bounty 播客

> **AI 加载指令**：来自顶尖 Bug 搜索者的系统化侦察和 Bug 搜索方法论。涵盖子域名枚举、端点发现、技术指纹识别，以及猎人发现他人遗漏的 Bug 的思维模型。关键洞察：大多数高严重性 Bug 都是通过系统化覆盖发现的，而不仅仅是巧妙的载荷。

---

## 1. 侦察层级

```
目标选择
└── 范围定义（在范围内的资产）
    └── 资产发现（子域名、IP、域名）
        └── 技术指纹识别（运行什么）
            └── 端点发现（攻击面）
                └── 漏洞测试（按漏洞类型）
```

---

## 2. 子域名枚举（关键第一步）

### 被动（不向目标发送 DNS 查询）
```bash
# Subfinder（聚合多个来源）：
subfinder -d target.com -o subdomains.txt

# Amass 被动：
amass enum -passive -d target.com

# Certsh（证书透明度）：
curl -s "https://crt.sh/?q=%.target.com&output=json" | jq -r '.[].name_value' | sort -u

# SecurityTrails API、Shodan：
# Web: https://securitytrails.com/list/apex_domain/target.com
```

### 主动（DNS 暴力破解 + 解析）
```bash
# Massdns + 字典：
massdns -r /path/to/resolvers.txt -t A -o S -w output.txt \
  <(cat wordlist.txt | sed 's/$/.target.com/')

# ffuf 用于子域名暴力破解：
ffuf -w subdomains-wordlist.txt -u https://FUZZ.target.com \
  -mc 200,301,302,403 -H "Host: FUZZ.target.com"

# DNSx 用于批量解析：
cat subdomains.txt | dnsx -a -resp -o resolved.txt

# 推荐的字典：SecLists/Discovery/DNS/
```

### 虚拟主机发现
```bash
# ffuf 虚拟主机模式：
ffuf -w wordlist.txt -u https://target.com \
  -H "Host: FUZZ.target.com" -mc 200,301,403

# gobuster 虚拟主机：
gobuster vhost -u https://target.com -w wordlist.txt
```

---

## 3. 服务和端口发现

```bash
# 快速端口扫描（常用端口）：
nmap -T4 -F target.com -oN ports.txt

# 在解析的子域名上执行全面扫描：
cat resolved_ips.txt | nmap -iL - --open -p 80,443,8080,8443,8888,3000,5000 -oG scan.txt

# httpx 用于 HTTP 探测：
cat subdomains.txt | httpx -title -tech-detect -status-code -o live_hosts.txt

# masscan 用于大 IP 范围的高速扫描：
masscan -p 80,443,8080,8443 10.0.0.0/8 --rate=1000
```

---

## 4. Web 技术指纹识别

```bash
# Wappalyzer（浏览器扩展）或：
whatweb https://target.com

# httpx 带技术检测：
httpx -u https://target.com -tech-detect

# 手动检查头部：
curl -sI https://target.com | grep -i "server\|x-powered-by\|x-generator\|cf-ray"

# 指纹来源：
- 服务器头部：nginx/1.18、Apache/2.4、IIS/10.0
- X-Powered-By：PHP/7.4、ASP.NET
- Cookies：PHPSESSID（PHP）、JSESSIONID（Java）、_rails_session（Rails）
- HTML 注释：<!-- Drupal 9 -->
- Meta generator：<meta name="generator" content="WordPress 6.2">
- JS 框架文件：/static/js/angular.min.js
```

---

## 5. 端点发现

### 目录暴力破解
```bash
# ffuf（最快）：
ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt \
  -mc 200,301,302,403 -t 50 -o dirs.txt

# Gobuster：
gobuster dir -u https://target.com -w wordlist.txt -x php,html,js,json

# feroxbuster（递归）：
feroxbuster -u https://target.com -w wordlist.txt -x php,html,txt -r
```

### 参数发现
```bash
# Arjun（隐藏参数查找器）：
arjun -u https://target.com/api/endpoint

# x8：
x8 -u https://target.com/api/endpoint -w params-wordlist.txt
```

### JavaScript 源码挖掘
```bash
# 从 JS 文件中提取端点：
gau target.com | grep '\.js$' | httpx -mc 200 | xargs -I{} curl -s {} | \
  grep -oE '"/[a-zA-Z0-9/_-]+"' | sort -u

# LinkFinder：
python3 linkfinder.py -i https://target.com -d -o output.html

# GetAllURLs（gau）：
gau target.com | sort -u > all_urls.txt

# Wayback URLs：
waybackurls target.com | sort -u > wayback_urls.txt
```

### API 端点发现
```bash
# 常见 API 路径：
ffuf -u https://target.com/FUZZ -w /SecLists/Discovery/Web-Content/api/api-endpoints.txt

# Swagger/OpenAPI：
test: /swagger.json /api-docs /openapi.json /v2/api-docs /.well-known/ /docs/

# GraphQL：
test: /graphql /gql /v1/graphql /api/graphql
```

---

## 6. 源代码侦察

### GitHub / GitLab 暴露
```bash
# trufflehog（Git 历史中的秘密扫描器）：
trufflehog git https://github.com/target-org/target-repo

# gitleaks：
gitleaks detect --source /path/to/cloned/repo

# 手动 GitHub 搜索：
# site:github.com "target.com" "api_key" OR "secret" OR "password"
# site:github.com "target.com" ".env" OR "config.php" OR "db_password"

# GitHub 搜索：
# "target.com" 扩展：env
# "target.com" 文件名：*.config password
# org:target-org secret OR password OR apikey
```

### 暴露的环境文件
```
# 检查常见路径：
https://target.com/.env
https://target.com/.git/config
https://target.com/config.json
https://target.com/config.yaml
https://target.com/credentials.json
https://target.com/secrets.json
https://target.com/wp-config.php
https://target.com/backup.sql
https://target.com/backup.zip
```

---

## 7. ZSEANO 的测试方法论

### 核心理念
1. **深入一个程序** 而不是分散在许多程序上 — 彻底了解应用程序
2. **构建公司画像** — 技术栈、开发者、流程
3. **去别人不去的地方** — 检查错误页面、管理路径、旧版本、移动 API
4. **跟随过滤器** — 如果输入在某处被过滤，那么该功能存在且可能被绕过

### 测试顺序（一个页面/功能）
```
对于每个输入点：
1. 非恶意的 HTML 标签（<h2>、<img>）→ 它们是否反射？
2. 不完整的标签 → 发生了什么？(<iframe src=//evil.com )
3. 编码测试 → %0d、%0a、%09、<%00
4. 观察输出（不只是响应）— 你的输入出现在哪里？
5. 在所有类似结构的页面上测试相同输入（共享代码 → 共享漏洞）
6. 检查相同参数是否存在于移动/API 端点（保护较少）
```

### 参数洞察
```
- 每个参数都讲述一个故事： "服务器端做什么？"
- 文件名 → OS 交互 → 路径遍历 / CMDi
- URL/位置 → HTTP 获取 → SSRF
- 模板/HTML 参数 → 渲染函数 → SSTI
- XML 字段 → 解析器 → XXE
- SQL 过滤器 → 查询 → SQLi
- 用户内容 → 存储 → 存储型 XSS
```

---

## 8. Bug Bounty 项目筛选（在哪里花费时间）

### 高价值目标选择
```
✓ 范围较大的程序 (*.target.com)
✓ 支付 P2/P3 的程序（不只是 RCE）
✓ 技术最近有变化的程序（迁移 = 新漏洞）
✓ 活跃开发的程序（新功能 = 新攻击面）
× 避免：冻结/旧的代码库，已知 CVE（已被占用）
× 避免：范围严格的程序（较少攻击面）
```

### 高价值功能重点（按漏洞概率）
```
优先级 1：认证、密码重置、2FA → 账户接管
优先级 2：文件上传、个人资料编辑、API 端点 → 存储型 XSS、IDOR
优先级 3：管理面板、用户管理 → BFLA、权限提升
优先级 4：支付流程、订阅 → 业务逻辑
优先级 5：导入/导出、模板渲染 → XXE、SSTI
```

---

## 9. NUCLEI 模板（自动化扫描）

```bash
# 在目标上运行所有：
nuclei -u https://target.com -t /nuclei-templates/ -o nuclei-results.txt

# 特定类别：
nuclei -u https://target.com -t cves/ -severity critical,high
nuclei -u https://target.com -t exposures/
nuclei -u https://target.com -t misconfiguration/

# 在子域名列表上：
cat subdomains.txt | nuclei -t exposures/ -t misconfiguration/ -o exposed.txt
```

---

## 10. 常见配置错误（快速获胜）

```
□ CORS：Access-Control-Allow-Origin: * 带凭证 → CSRF + 数据窃取
□ S3 桶公开：curl https://target.s3.amazonaws.com/
□ 目录列表：响应包含 "Index of /"
□ .git 暴露：curl https://target.com/.git/config
□ .env 暴露：curl https://target.com/.env
□ 调试模式：生产环境中的堆栈跟踪（源代码暴露）
□ 默认凭证：管理面板上的 admin:admin、admin:password
□ phpinfo.php：curl https://target.com/phpinfo.php
□ 备份文件：config.bak、database.sql.gz、app.zip
□ GraphQL 内省启用：POST /graphql {"query":"{__schema{types{name}}}"}
□ 管理面板：/admin /manager /console /phpmyadmin /wp-admin
```

---

## 11. 快速参考工具

| 类别 | 工具 |
|---|---|
| 子域名枚举 | subfinder、amass、massdns |
| 端口扫描 | nmap、masscan |
| HTTP 探测 | httpx |
| 目录暴力破解 | ffuf、feroxbuster、gobuster |
| JS 挖掘 | LinkFinder、gau、waybackurls |
| 秘密扫描 | trufflehog、gitleaks |
| 参数模糊测试 | arjun、x8 |
| 漏洞扫描 | nuclei |
| 代理/拦截 | Burp Suite Pro |
| JWT 攻击 | jwt_tool |
| SQLi | sqlmap |
| XSS | dalfox、XSStrike |
| SSRF | SSRFmap、Gopherus |

---

## 12. Java 中间件指纹矩阵

| 中间件 | 检测路径 | 关键指标 |
|---|---|---|
| Apache Tomcat | `/manager/html`、`/manager/status` | 默认凭证：`tomcat:tomcat`、`admin:admin` |
| JBoss / WildFly | `/jmx-console/`、`/web-console/` | JMX MBean 访问、WAR 部署 |
| WebLogic | `/console/`、`/wls-wsat/` | T3 协议在 7001/7002、IIOP |
| Spring Boot Actuator | `/actuator/`、`/actuator/env`、`/actuator/heapdump` | JSON 端点列表、堆转储包含秘密 |
| Spring Boot（其他路径） | `/actuator/jolokia`、`/actuator/gateway/routes` | Jolokia JMX 桥接、Gateway 路由注入 |
| Jenkins | `/script`、`/manage` | Groovy 控制台、API 令牌在 Cookie 中 |
| GlassFish | `/common/`、`/theme/` | 管理 4848、默认空密码 |
| Jetty | `/jolokia/` | JMX 访问 |
| Resin | `/resin-admin/` | 管理面板 |

### Spring Boot Actuator 利用优先级

```
/actuator/env          → 泄露环境变量（DB 凭证、API 密钥）
/actuator/heapdump     → 下载 JVM 堆 → 在内存中搜索密码
/actuator/jolokia      → JMX → 可能通过 MBean 操作实现 RCE
/actuator/gateway/routes → Spring Cloud Gateway → SpEL 注入（CVE-2022-22947）
/actuator/configprops  → 所有配置属性
/actuator/mappings     → 所有 URL 映射（隐藏端点）
/actuator/beans        → 所有 Spring bean
/actuator/threaddump   → 线程转储（可能泄露会话令牌/秘密在堆栈帧中）
```

---

## 13. 信息泄露检测清单

### 版本控制 & 备份泄露

```
/.git/HEAD                    → Git 仓库暴露
/.svn/entries                 → SVN 元数据
/.svn/wc.db                   → SVN SQLite 数据库
/.hg/requires                 → Mercurial
/.bzr/README                  → Bazaar
/.DS_Store                    → macOS 目录列表
```

### 备份文件模式

```
/backup.zip    /backup.tar.gz    /backup.sql
/wwwroot.rar   /www.zip          /web.zip
/db.sql        /database.sql     /dump.sql
/config.php.bak    /config.php~    /config.php.swp
/.config.php.swp   /wp-config.php.bak
/.env          /.env.bak         /.env.production
```

### API 文档 & 调试

```
/swagger-ui.html              → Swagger/OpenAPI
/swagger-ui/                  → Swagger UI
/api-docs                     → API 文档
/graphql                      → GraphQL 演示场
/graphiql                     → GraphQL IDE
/debug/                       → 调试端点
/phpinfo.php                  → PHP 配置
/server-status                → Apache 状态
/server-info                  → Apache 信息
/nginx_status                 → Nginx 状态
```

### 云 & 基础设施

```
/.aws/credentials             → AWS 凭证
/.docker/config.json          → Docker 注册库认证
/robots.txt                   → 禁止路径（提示列表）
/sitemap.xml                  → 完整 URL 列表
/crossdomain.xml              → Flash 跨域策略
/.well-known/                 → 各种已知 URI
```
