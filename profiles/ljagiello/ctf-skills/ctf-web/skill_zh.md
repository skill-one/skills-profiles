# CTF Web Exploitation

将此技能用作针对以网络为主挑战的路线和执行指南。保持第一轮扫描简短：映射应用程序，确认信任边界，然后才深入详细的技术笔记。

## 前置条件

**Python 包（所有平台）：**
```bash
pip install sqlmap flask-unsign requests httpx
```

**Linux (apt)：**
```bash
apt install hashcat jq curl
```

**macOS (Homebrew)：**
```bash
brew install hashcat jq curl
```

**Go 工具（所有平台，需要 Go）：**
```bash
go install github.com/ffuf/ffuf/v2@latest
```

**手动安装：**
- ysoserial — [GitHub](https://github.com/frohoff/ysoserial)，需要 Java（Java 反序列化有效载荷）
- PayloadsAllTheThings — git clone 到 ctf-web/payloads/PayloadsAllTheThings（通过安装脚本自动或懒克隆）
  ```bash
  bash scripts/install_ctf_tools.sh pat   # 仅 PAT
  bash scripts/install_ctf_tools.sh all   # 所有工具包括 PAT
  # 手动回退：
  git clone --depth 1 https://github.com/swisskyrepo/PayloadsAllTheThings.git ctf-web/payloads/PayloadsAllTheThings
  ```
  > PAT 是可选的，按需使用 — 加载时不需要。该技能在没有 PAT 的情况下也能工作（优雅降级）：`pat-reference.md` 提供离线索引和示例有效载荷；批量单词列表需要上述克隆。

## 额外资源

- [sql-injection.md](sql-injection.md) - SQL 注入技术：认证绕过、UNION 提取、过滤绕过、二次序 SQLi、截断、竞争条件辅助泄露、INSERT ON DUPLICATE KEY UPDATE 密码覆盖、innodb_table_stats WAF 绕过
- [server-side.md](server-side.md) - PHP 类型转换、php://filter LFI、Python str.format 遍历、SSTI（Jinja2、Twig、ERB、Mako、EJS、Vue.js、Smarty）、SSRF（Host 头、DNS 重绑定、curl 重定向、未转义点正则、SNI FTP 滑翔、mod_vhost_alias）、PHP hash_hmac NULL
- [server-side-2.md](server-side-2.md) - XXE（基本、OOB、DOCX 上传）、通过 X-Forwarded-For 的 XML 注入、PHP 变量变量、PHP uniqid 可预测文件名、顺序正则替换绕过、命令注入（换行符、黑名单、sendmail CGI、多条码、git CLI）、GraphQL 注入（内省、批处理、插值）
- [server-side-exec.md](server-side-exec.md) - 直接代码执行路径、上传到 RCE、反序列化相邻执行、LaTeX 注入、头部和 API 滥用
- [server-side-exec-2.md](server-side-exec-2.md) - 更多执行链：SQLi 片段化、路径解析技巧、多语言上传、包装器滥用、文件名注入、BMP 像素 webshell 带文件名截断
- [server-side-deser.md](server-side-deser.md) - Java/Python/PHP 反序列化和竞争条件剧本、PHP SoapClient CRLF SSRF 通过反序列化
- [server-side-advanced.md](server-side-advanced.md) - 高级 SSRF、遍历、归档、解析器、框架和现代应用服务器问题、Nginx 别名遍历
- [server-side-advanced-2.md](server-side-advanced-2.md) - Docker API SSRF、Castor/XML、Apache 表达式读取、解析器差异、Windows 路径技巧、流氓 MySQL 服务器文件读取
- [server-side-advanced-3.md](server-side-advanced-3.md) - 第 3 部分（CSAW/35C3/ASIS/PlaidCTF 2018）：WAV 多语言上传、多斜杠 URL `path.startswith` 绕过、Xalan XSLT `math:random()` 种子猜测、SoapClient `_user_agent` CRLF 方法滑翔、`gopher:///` 无主机 URL 方案绕过、SSRF 凭据泄露通过攻击者指定的出站 URL
- [server-side-advanced-4.md](server-side-advanced-4.md) - 第 4 部分：WeasyPrint SSRF/文件读取（CVE-2024-28184）、MongoDB 正则/$where 盲目预言机、Pongo2 Go 模板注入、ZIP PHP webshell、basename() 绕过、wget CRLF SSRF→SMTP、Gopher SSRF 到 MySQL 盲目 SQLi、React Server 组件 Flight RCE（CVE-2025-55182）、AMQP/TLS 中断通过 sslsplit+arpspoof、CairoSVG XXE、Bazaar 仓库重建
- [client-side.md](client-side.md) - XSS、CSRF、缓存中毒、DOM 技巧、管理员机器人滥用、请求滑翔、付费墙绕过
- [client-side-advanced.md](client-side-advanced.md) - CSP 绕过、Unicode 技巧、XSSI、CSS 提取、浏览器规范化怪癖、postMessage null 来源绕过
- [auth-and-access.md](auth-and-access.md) - 认证/授权绕过、隐藏端点、IDOR、重定向链、子域名接管、AI 聊天机器人越狱
- [auth-and-access-2.md](auth-and-access-2.md) - 第 2 部分（2018 年代）：`std::unordered_set` 桶碰撞认证绕过、`nodeprep.prepare` Unicode 字形相似用户名碰撞、SRP A=0/A=N 认证绕过、ArangoDB AQL MERGE 权限提升
- [auth-jwt.md](auth-jwt.md) - JWT/JWE 操作、弱密钥、头部注入、密钥混淆、重放
- [auth-infra.md](auth-infra.md) - OAuth/OIDC、SAML、CORS、CI/CD 密钥、IdP 滥用、登录中毒
- [node-and-prototype.md](node-and-prototype.md) - 原型污染、JS 沙盒逃逸、Node.js 攻击链
- [web3.md](web3.md) - Solidity 和 Web3 挑战笔记
- [cves.md](cves.md) - CVE 驱动的技术，可以与挑战横幅、头部、依赖泄露或版本字符串匹配
- [field-notes.md](field-notes.md) - 长格式利用笔记：SQLi、XSS、LFI、JWT、SSTI、SSRF、命令注入、XXE、反序列化、竞争条件、认证绕过和多阶段链的快速参考
- [python-requests.md](python-requests.md) - Python requests 工具包：会话骨架、类似 Burp-Intruder 的模糊器（同步 + ThreadPoolExecutor + httpx 异步）、从 pat-reference.md 单词列表部署有效载荷、头部/参数喷雾、cookie/JWT、代理
- [pat-reference.md](pat-reference.md) — PayloadsAllTheThings 索引：XSS/SQLi/SSRF/SSTI/LFI/命令注入/上传的批量有效载荷（需要 PAT 克隆，见前置条件）

## 何时转向

- 如果目标是原生二进制、自定义 VM 或固件镜像，首先切换到 `/ctf-reverse`。
- 如果 HTTP 错误只给你代码执行，而难点变成内存损坏或 seccomp 逃逸，切换到 `/ctf-pwn`。
- 如果“网络”挑战真的涉及 JWT 数学、自定义 MAC 或加密原语，切换到 `/ctf-crypto`。
- 如果网络挑战涉及分析日志、PCAP 或从网络服务器恢复工件，切换到 `/ctf-forensics`。
- 如果挑战需要在利用前从公共网络来源、DNS 记录或社交媒体收集情报，切换到 `/ctf-osint`。

## 第一轮工作流程

1. 确定真实边界：仅浏览器、仅后端、混合应用或认证流程。
2. 在模糊之前，为每个主要功能捕获一个正常请求/响应对。
3. 从 JS 包、响应头部、路由和替代方法中枚举隐藏功能。
4. 分类可能的错误类型：注入、授权、解析器不匹配、上传、信任代理、状态机或客户端执行。
5. 首先构建最小的证据：泄露、绕过或原始操作。将完整的利用链保留到以后。

### 批量有效载荷（PayloadsAllTheThings — 按需）

此技能在加载时无需 PAT 即可工作（优雅降级）：`pat-reference.md` 和内联示例可在离线使用；批量有效载荷需要 PAT 克隆。在映射信任边界（第一轮工作流程）后，检查 [pat-reference.md](pat-reference.md) 以匹配您的错误类型，然后搜索批量有效载荷：

```bash
# PAT 有效载荷搜索（需要 PAT 克隆 — 见前置条件；如果缺失则优雅跳过）
ls ctf-web/payloads/PayloadsAllTheThings 2>/dev/null | head
grep -R "onerror" "ctf-web/payloads/PayloadsAllTheThings/XSS Injection" 2>/dev/null | head
```

或通过代理工具（无需克隆索引本身）：

```
Glob ctf-web/payloads/PayloadsAllTheThings/**/*.md
Grep "union select" ctf-web/payloads/PayloadsAllTheThings
```

如果 `ctf-web/payloads/PayloadsAllTheThings/.git` 缺失，代理按需懒克隆：

```bash
[ -d "ctf-web/payloads/PayloadsAllTheThings/.git" ] || git clone --depth 1 https://github.com/swisskyrepo/PayloadsAllTheThings.git ctf-web/payloads/PayloadsAllTheThings
```

## 快速启动命令

```bash
# 侦察
curl -sI https://target.com
ffuf -u https://target.com/FUZZ -w wordlist.txt
curl -s https://target.com/robots.txt

# SQLi 快速测试
sqlmap -u "https://target.com/page?id=1" --batch --dbs

# JWT 解码（无验证）
echo '<token>' | cut -d. -f2 | base64 -d 2>/dev/null | jq .

# Cookie 解码（Flask）
flask-unsign --decode --cookie '<cookie>'
flask-unsign --unsign --cookie '<cookie>' --wordlist rockyou.txt

# SSTI 探测
curl "https://target.com/page?name={{7*7}}"
curl "https://target.com/page?name={{config}}"

# 请求检查
curl -v -X POST https://target.com/api -H "Content-Type: application/json" -d '{}'
```

## 首要问题

- 旗帜可能在浏览器、API 响应、本地文件、数据库行或内部服务中？
- 应用程序是否信任用户控制的数据在模板、重定向、文件路径、头部、序列化对象或后台作业中？
- 是否有多个解析器相互矛盾：代理与应用程序、URL 解析器与获取器、清理器与浏览器、序列化器与过滤器？
- 能否将错误转化为更小的原始操作：读取一个文件、伪造一个令牌、调用一个内部端点、触发一个机器人访问？

## 高价值侦察检查

- 在猜测 API 表面之前，读取 HTML、内联脚本和捆绑 JS。
- 比较用户界面提交的内容与后端接受的内容；可选的 JSON 字段通常解锁隐藏路径。
- 早期检查明显的元数据和辅助路径：`/robots.txt`、`/sitemap.xml`、`/.well-known/`、`/admin`、`/debug`、`/.git/`、`/.env`。
- 在有趣的路径上尝试交替动词和内容类型：`GET`、`POST`、`PUT`、`PATCH`、`TRACE`、JSON、表单、多部分、XML。
- 将文件上传、PDF/导出、webhook、OAuth 回调和管理员机器人功能视为可能的利用乘数。

## 快速模式映射

- SQL 错误、异常过滤或状态依赖的 DB 行为：从 [sql-injection.md](sql-injection.md) 开始。
- 模板化、文件读取、SSRF、命令执行、XML 或解析器错误：从 [server-side.md](server-side.md) 和 [server-side-exec.md](server-side-exec.md) 开始。
- XSS、CSP 绕过、管理员机器人、客户端路由、DOM 问题或脚本less提取：从 [client-side.md](client-side.md) 开始。
- 会话伪造、隐藏管理员路由、JWT、OAuth、SAML 或弱信任边界：从 [auth-and-access.md](auth-and-access.md)、[auth-jwt.md](auth-jwt.md) 和 [auth-infra.md](auth-infra.md) 开始。
- Node.js 应用程序、原型污染、VM 沙盒或 SSRF 到内部服务：添加 [node-and-prototype.md](node-and-prototype.md)。
- 智能合约前端或集成了区块链的应用程序：添加 [web3.md](web3.md)。

## 常见链形状

- 侦察 -> 隐藏路由 -> 认证绕过 -> 内部文件读取 -> 令牌或旗帜
- XSS 或 HTML 注入 -> 管理员机器人 -> 特权操作 -> 密钥泄露
- 遍历或上传 -> 配置/源泄露 -> 密钥恢复 -> 会话伪造
- SSRF -> 元数据或内部 API -> 凭据泄露 -> 代码执行
- SQLi 或 NoSQL 注入 -> 凭据绕过 -> 第二阶段模板或上传滥用

## 深入笔记

一旦确认挑战确实是网络为主的，并且您需要长利用目录，请使用 [field-notes.md](field-notes.md)。

- 侦察、SQLi、XSS、遍历、JWT、SSTI、SSRF、XXE 和命令注入快速笔记
- 反序列化、竞争条件、上传到 RCE 和多阶段链示例
- Node、OAuth/SAML、CI/CD、Web3、机器人滥用、CSP 绕过和现代浏览器技巧
- CVE 形状的剧本和仍然出现在现代 CTF 中的旧挑战模式

## 常见旗帜位置

- 文件：`/flag.txt`、`/flag`、`/app/flag.txt`、`/home/*/flag*`
- 环境：`/proc/self/environ`、进程命令行、调试配置转储
- 数据库：名为 `flag`、`flags`、`secret` 或种子挑战内容的表
- HTTP：自定义头部、存档响应、隐藏路由、管理员导出
- 浏览器：隐藏 DOM 节点、`data-*` 属性、内联状态对象、源映射
