基于OWASP提示系列（CC BY-SA 4.0）
https://cheatsheetseries.owasp.org/

# 安全审查技能

识别代码中的可利用安全漏洞。仅报告**高置信度**的发现——具有明确漏洞模式且攻击者可控制的输入。

## 范围：研究 vs. 报告

**关键区别：**

- **报告**：仅针对用户提供的特定文件、差异或代码
- **研究**：整个代码库，以在报告前建立信心

在标记任何问题之前，你必须研究代码库以理解：
- 这个输入实际上来自哪里？（追踪数据流）
- 是否存在其他地方的验证/清理？
- 如何配置的？（检查设置、配置文件、中间件）
- 存在哪些框架保护？

**不要仅基于模式匹配来报告问题。** 先调查，然后仅报告你确信是可利用的问题。

## 置信度级别

| 级别 | 标准 | 操作 |
|------|------|------|
| **高** | 漏洞模式 + 攻击者可控制的输入已确认 | **报告**并附带严重性 |
| **中** | 漏洞模式，输入来源不明确 | **标记**为“需要验证” |
| **低** | 理论性，最佳实践，纵深防御 | **不报告** |

## 不要标记

### 一般规则
- 测试文件（除非明确审查测试安全）
- 死代码、注释代码、文档字符串
- 使用**常量**或**服务器控制的配置**的模式
- 需要先进行身份验证才能访问的代码路径（标记身份验证要求）

### 服务器控制值（非攻击者控制）

这些由操作员配置，而不是攻击者控制：

| 来源 | 示例 | 为什么安全 |
|------|------|----------|
| Django设置 | `settings.API_URL`, `settings.ALLOWED_HOSTS` | 部署时通过配置/环境设置 |
| 环境变量 | `os.environ.get('DATABASE_URL')` | 部署配置 |
| 配置文件 | `config.yaml`, `app.config['KEY']` | 服务器端文件 |
| 框架常量 | `django.conf.settings.*` | 不可用户修改 |
| 硬编码值 | `BASE_URL = "https://api.internal"` | 编译时常量 |

**SSRF示例 - 不是漏洞：**
```python
# 安全：URL来自Django设置（服务器控制）
response = requests.get(f"{settings.SEER_AUTOFIX_URL}{path}")
```

**SSRF示例 - 是漏洞：**
```python
# 漏洞：URL来自请求（攻击者控制）
response = requests.get(request.GET.get('url'))
```

### 框架缓解模式
标记前请检查语言指南。常见误报：

| 模式 | 通常安全的原因 |
|------|--------------|
| Django `{{ variable }}` | 默认自动转义 |
| React `{variable}` | 默认自动转义 |
| Vue `{{ variable }}` | 默认自动转义 |
| `User.objects.filter(id=input)` | ORM参数化查询 |
| `cursor.execute("...%s", (input,))` | 参数化查询 |
| `innerHTML = "<b>Loading...</b>"` | 常量字符串，无用户输入 |

**仅在这些情况下标记：**
- Django: `{{ var|safe }}`, `{% autoescape off %}`, `mark_safe(user_input)`
- React: `dangerouslySetInnerHTML={{__html: userInput}}`
- Vue: `v-html="userInput"`
- ORM: `.raw()`, `.extra()`, `RawSQL()`带字符串插值

## 审查过程

### 1. 检测上下文

我在审查什么类型的代码？

| 代码类型 | 加载这些参考 |
|------|------------|
| API端点、路由 | `authorization.md`, `authentication.md`, `injection.md` |
| 前端、模板 | `xss.md`, `csrf.md` |
| 文件处理、上传 | `file-security.md` |
| 加密、密钥、令牌 | `cryptography.md`, `data-protection.md` |
| 数据序列化 | `deserialization.md` |
| 外部请求 | `ssrf.md` |
| 业务流程 | `business-logic.md` |
| GraphQL、REST设计 | `api-security.md` |
| 配置、标头、CORS | `misconfiguration.md` |
| CI/CD、依赖项 | `supply-chain.md` |
| 错误处理 | `error-handling.md` |
| 审计、日志 | `logging.md` |

### 2. 加载语言指南

根据文件扩展名或导入：

| 指示器 | 指南 |
|------|------|
| `.py`, `django`, `flask`, `fastapi` | `languages/python.md` |
| `.js`, `.ts`, `express`, `react`, `vue`, `next` | `languages/javascript.md` |
| `.go`, `go.mod` | `languages/go.md` |
| `.rs`, `Cargo.toml` | `languages/rust.md` |
| `.java`, `spring`, `@Controller` | `languages/java.md` |

### 3. 加载基础设施指南（如适用）

| 文件类型 | 指南 |
|------|------|
| `Dockerfile`, `.dockerignore` | `infrastructure/docker.md` |
| K8s清单、Helm图表 | `infrastructure/kubernetes.md` |
| `.tf`, Terraform | `infrastructure/terraform.md` |
| GitHub Actions, `.gitlab-ci.yml` | `infrastructure/ci-cd.md` |
| AWS/GCP/Azure配置、IAM | `infrastructure/cloud.md` |

### 4. 标记前研究

**对于每个潜在问题，研究代码库以建立信心：**

- 这个值实际上来自哪里？追踪数据流。
- 是在部署时配置（设置、环境变量）还是来自用户输入？
- 是否存在其他地方的验证、清理或允许列表？
- 适用哪些框架保护？

仅报告在理解更广泛上下文后具有高置信度的问题。

### 5. 验证可利用性

对于每个潜在发现，确认：

**输入是否攻击者控制？**

| 攻击者控制（调查） | 服务器控制（通常安全） |
|-------------------|----------------------|
| `request.GET`, `request.POST`, `request.args` | `settings.X`, `app.config['X']` |
| `request.json`, `request.data`, `request.body` | `os.environ.get('X')` |
| `request.headers`（大多数标头） | 硬编码常量 |
| `request.cookies`（未签名） | 来自配置的内部服务URL |
| URL路径段：`/users/<id>/` | 来自管理/系统的数据库内容 |
| 文件上传（内容和名称） | 签名会话数据 |
| 来自其他用户的数据库内容 | 框架设置 |
| WebSocket消息 | |

**框架是否缓解此问题？**
- 检查语言指南中的自动转义、参数化
- 检查清理中间件/装饰器

**是否有上游验证？**
- 此代码之前的输入验证
- 清理库（DOMPurify、bleach等）

### 6. 仅报告高置信度

跳过理论性问题。仅报告研究后确认的可利用问题。

---

## 严重性分类

| 严重性 | 影响 | 示例 |
|------|------|------|
| **严重** | 直接利用，严重影响，无需身份验证 | RCE、SQL注入到数据、身份验证绕过、硬编码密钥 |
| **高** | 满足条件即可利用，重大影响 | 存储型XSS、SSRF到元数据、IDOR到敏感数据 |
| **中** | 需要特定条件，中等影响 | 反射型XSS、CSRF在状态更改操作上、路径遍历 |
| **低** | 纵深防御，最小直接影响 | 缺少标头、冗长错误、非关键上下文中的弱算法 |

---

## 快速模式参考

### 总是标记（严重）
```
eval(user_input)           # 任何语言
exec(user_input)           # 任何语言
pickle.loads(user_data)    # Python
yaml.load(user_data)       # Python（不安全的load）
unserialize($user_data)    # PHP
deserialize(user_data)     # Java ObjectInputStream
shell=True + user_input    # Python subprocess
child_process.exec(user)   # Node.js
```

### 总是标记（高）
```
innerHTML = userInput              # DOM XSS
dangerouslySetInnerHTML={user}     # React XSS
v-html="userInput"                 # Vue XSS
f"SELECT * FROM x WHERE {user}"    # SQL注入
`SELECT * FROM x WHERE ${user}`    # SQL注入
os.system(f"cmd {user_input}")     # 命令注入
```

### 总是标记（密钥）
```
password = "hardcoded"
api_key = "sk-..."
AWS_SECRET_ACCESS_KEY = "..."
private_key = "-----BEGIN"
```

### 先检查上下文（必须标记前调查）
```
# SSRF - 仅当URL来自用户输入，而非设置/配置时
requests.get(request.GET['url'])     # 标记：用户控制的URL
requests.get(settings.API_URL)       # 安全：服务器控制的配置
requests.get(f"{settings.BASE}/{x}") # 检查：'x'是否用户输入？

# 路径遍历 - 仅当路径来自用户输入
open(request.GET['file'])            # 标记：用户控制的路径
open(settings.LOG_PATH)              # 安全：服务器控制的配置
open(f"{BASE_DIR}/{filename}")       # 检查：'filename'是否用户输入？

# 开放重定向 - 仅当URL来自用户输入
redirect(request.GET['next'])        # 标记：用户控制的重定向
redirect(settings.LOGIN_URL)         # 安全：服务器控制的配置

# 弱加密 - 仅当用于安全目的
hashlib.md5(file_content)            # 安全：文件校验和、缓存
hashlib.md5(password)                # 标记：密码哈希
random.random()                      # 安全：非安全用途（UI、采样）
random.random() for token            # 标记：安全令牌需要密钥模块
```

---

## 输出格式

```markdown
## 安全审查：[文件/组件名称]

### 摘要
- **发现**：X（Y严重，Z高，...）
- **风险级别**：严重/高/中/低
- **置信度**：高/混合

### 发现

#### [VULN-001] [漏洞类型]（严重性）
- **位置**：`file.py:123`
- **置信度**：高
- **问题**：[漏洞是什么]
- **影响**：[攻击者可以做什么]
- **证据**：
  ```python
  [漏洞代码片段]
  ```
- **修复**：[如何缓解]

### 需要验证

#### [VERIFY-001] [潜在问题]
- **位置**：`file.py:456`
- **问题**：[需要验证什么]
```

如未发现高置信度漏洞，则说明：“未发现高置信度漏洞。”

---

## 参考文件

### 核心漏洞（`references/`）
| 文件 | 涵盖 |
|------|------|
| `injection.md` | SQL、NoSQL、OS命令、LDAP、模板注入 |
| `xss.md` | 反射型、存储型、DOM型XSS |
| `authorization.md` | 授权、IDOR、权限提升 |
| `authentication.md` | 会话、凭证、密码存储 |
| `cryptography.md` | 算法、密钥管理、随机性 |
| `deserialization.md` | Pickle、YAML、Java、PHP反序列化 |
| `file-security.md` | 路径遍历、上传、XXE |
| `ssrf.md` | 服务器端请求伪造 |
| `csrf.md` | 跨站请求伪造 |
| `data-protection.md` | 密钥暴露、PII、日志 |
| `api-security.md` | REST、GraphQL、批量赋值 |
| `business-logic.md` | 竞态条件、工作流绕过 |
| `modern-threats.md` | 原型污染、LLM注入、WebSocket |
| `misconfiguration.md` | 标头、CORS、调试模式、默认值 |
| `error-handling.md` | 开放式、信息泄露 |
| `supply-chain.md` | 依赖项、构建安全 |

### 语言指南（`languages/`）
- `python.md` - Django、Flask、FastAPI模式
- `javascript.md` - Node、Express、React、Vue、Next.js
- `go.md` - Go特定安全模式
- `rust.md` - Rust不安全块、FFI安全
- `java.md` - Spring、Java EE模式

### 基础设施（`infrastructure/`）
- `docker.md` - 容器安全
- `kubernetes.md` - K8s RBAC、密钥、策略
- `terraform.md` - IaC安全
- `ci-cd.md` - 管道安全
- `cloud.md` - AWS/GCP/Azure安全
