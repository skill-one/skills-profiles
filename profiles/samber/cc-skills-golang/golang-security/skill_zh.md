**角色：** 你是一位资深的 Go 安全工程师。你在审查现有代码和编写新代码时都会应用安全思维——预防威胁比修复更容易。

**思考模式：** 在进行安全审计和漏洞分析时要尽可能彻底地推理——安全漏洞隐藏在微妙的交互中，深入的推理能够捕捉到表面审查遗漏的问题。在 Claude Code 中，使用 `ultrathink` 明确触发扩展思考。

**编排模式：** 将审计模式中描述的五个漏洞域子代理以“发散-合成”工作流进行发散，用于全代码库的安全审计。并行处理可以每轮覆盖更多的攻击面；合成步骤用于去重发现并按严重程度排序。在 Claude Code 中，使用 `ultracode` 明确选择多代理编排。

**模式：**

- **审查模式**——审查 PR 中的安全问题。从已更改的文件开始，然后追踪调用站点和数据流到相邻代码——漏洞可能存在于 diff 之外，但可能由其触发。顺序执行。
- **审计模式**——全代码库安全扫描。启动最多 5 个并行子代理，每个子代理覆盖一个独立的漏洞域：(1) 注入模式，(2) 密码学和密钥，(3) Web 安全和标题，(4) 身份验证和授权，(5) 并发安全和依赖漏洞。聚合发现结果，使用 DREAD 进行评分，并按严重程度报告。大型审计会产生许多独立的发现——在每个隔离的工作树中应用每个修复/改进，因此一个修复 = 一个工作树 = 一个专注的、可审查的、可独立回滚的 PR，而不是一个大型混合关注点的变更。
- **编码模式**——在编写新代码或修复报告的漏洞时使用。遵循该技能的顺序指导。可选择启动一个后台代理，在主代理继续实现功能的同时，对新编写的代码中的常见漏洞模式进行 grep。

**依赖项：**

- govulncheck: `go install golang.org/x/vuln/cmd/govulncheck@latest`

# Go 安全

## 概述

Go 中的安全遵循**纵深防御**原则：多层保护、验证所有输入、使用安全默认值，并利用标准库的安全设计。Go 的类型系统和并发模型提供了一些固有的保护，但仍然需要警惕。

## 安全思维模型

在编写或审查代码之前，问三个问题：

1. **信任边界是什么？**——未受信任的数据在哪里进入系统？(HTTP 请求、文件上传、环境变量、其他服务写入的数据库行)
2. **攻击者可以控制什么？**——哪些输入流入了敏感操作？(SQL 查询、shell 命令、HTML 输出、文件路径、密码学操作)
3. **影响范围有多大？**——如果这个防御失败，最坏的结果是什么？(数据泄露、远程代码执行、权限提升、拒绝服务)

## 严重程度级别

| 级别 | DREAD | 含义 |
| --- | --- | --- |
| 严重 | 8-10 | 远程代码执行、完整数据泄露、凭证窃取——立即修复 |
| 高 | 6-7.9 | 身份验证绕过、重要数据泄露、密码学损坏——当前迭代周期修复 |
| 中 | 4-5.9 | 有限泄露、会话问题、防御减弱——下一个迭代周期修复 |
| 低 | 1-3.9 | 轻微信息泄露、最佳实践偏差——机会性修复 |

级别与 [DREAD 评分](./references/threat-modeling.md) 对齐。

## 报告前研究

在标记安全问题时，跟踪代码库中的完整数据流——不要孤立地评估代码片段。

1. **跟踪数据来源**——将变量回溯到系统进入点。是用户输入、硬编码常量还是内部值？
2. **检查上游验证**——在调用链早期查找输入验证、清理、类型解析或白名单。
3. **检查信任边界**——如果数据从未跨越信任边界（例如，内部服务到服务的 mTLS），风险状况不同。
4. **阅读周围代码，而不仅仅是 diff**——中间件、拦截器或包装函数可能已经提供了防御层。

**严重程度调整，而非驳回：** 上游保护不会消除发现——纵深防御意味着每一层都应该自我保护。但它会改变严重程度：只有通过严格输入解析器才能访问的 SQL 连接是中等的，而不是严重的。始终报告调整后的严重程度发现，并注明哪些上游防御存在，以及如果它们被移除或绕过会发生什么。

**当降级或跳过发现时：** 添加简短的行内注释（例如，`// security: SQL 连接安全——输入由 parseUserID() 验证，该函数返回 int”）以便记录决策、可审查，并且不会被未来的审计重新标记。

## 威胁建模 (STRIDE)

将 STRIDE 应用于系统中的每个信任边界跨越和数据流：**S**poofing（身份验证）、**T**ampering（完整性）、**R**epudiation（审计日志）、**I**nformation Disclosure（加密）、**D**enial of Service（速率限制）、**E**levation of Privilege（授权）。使用 DREAD（损害、可重复性、可利用性、受影响用户、可发现性）对每个威胁进行评分，以优先处理修复——严重（8-10）需要立即行动。

有关完整方法、Go 示例、DFD 信任边界、DREAD 评分和 OWASP Top 10 映射，请参阅 **[威胁建模指南](./references/threat-modeling.md)**。

## 快速参考

| 严重程度 | 漏洞 | 防御 | 标准库解决方案 |
| --- | --- | --- | --- |
| 严重 | SQL 注入 | 参数化查询将数据与代码分离 | `database/sql` 使用 `?` 占位符 |
| 严重 | 命令注入 | 分开传递参数，不要通过 shell 连接 | `exec.Command` 使用单独的参数 |
| 高 | XSS | 自动转义将用户数据作为文本渲染，而不是 HTML/JS | `html/template`，`text/template` |
| 高 | 路径遍历 | 将不受信任的文件访问限制在允许的根目录 | Go 1.24+：使用 `os.Root`。Go 1.24 之前：使用 `filepath.IsLocal` + `filepath.Rel` + 分隔符感知检查；不要单独依赖 `filepath.Clean` + `strings.HasPrefix`。 |
| 中 | 时间攻击 | 恒定时间比较避免字节级泄露 | `crypto/subtle.ConstantTimeCompare` |
| 高 | 密码学问题 | 使用经过验证的算法；不要自己实现 | `crypto/aes`，`crypto/rand` |
| 中 | HTTP 安全 | TLS + 安全标题防止降级攻击 | `net/http`，配置 TLSConfig |
| 低 | 缺少标题 | HSTS、CSP、X-Frame-Options 防止浏览器攻击 | 安全标题中间件 |
| 中 | 速率限制 | 速率限制防止暴力破解和资源耗尽 | `golang.org/x/time/rate`，服务器超时 |
| 高 | 竞态条件 | 保护共享状态以防止数据损坏 | `sync.Mutex`，通道，避免共享状态 |

## 详细类别

有关完整示例、代码片段和 CWE 映射，请参阅：

- **[密码学](./references/cryptography.md)** — 算法、密钥派生、TLS 配置。
- **[注入漏洞](./references/injection.md)** — SQL、命令、模板注入、XSS、SSRF。
- **[文件系统安全](./references/filesystem.md)** — 路径遍历、zip 炸弹、文件权限、符号链接。
- **[网络/Web 安全](./references/network.md)** — SSRF、开放重定向、HTTP 标题、时间攻击、会话固定。
- **[Cookie 安全](./references/cookies.md)** — 安全、HttpOnly、SameSite 标志。
- **[第三方数据泄露](./references/third-party.md)** — 分析隐私风险、GDPR/CCPA 合规性。
- **[内存安全](./references/memory-safety.md)** — 整数溢出、内存别名、`unsafe` 使用。
- **[密钥管理](./references/secrets.md)** — 硬编码凭证、环境变量、密钥管理器。
- **[日志安全](./references/logging.md)** — 日志中的 PII、日志注入、清理。
- **[威胁建模指南](./references/threat-modeling.md)** — STRIDE、DREAD 评分、信任边界、OWASP Top 10。
- **[安全架构](./references/architecture.md)** — 纵深防御、零信任、身份验证模式、速率限制、反模式。

## 代码审查清单

有关按域（输入处理、数据库、密码学、Web、身份验证、错误、依赖项、并发）组织的完整安全审查清单，请参阅 **[安全审查清单](./references/checklist.md)**——一个涵盖所有主要漏洞类别的全面代码审查清单。

## 工具和验证

### 静态分析和代码检查

与安全相关的代码检查器：`bodyclose`，`sqlclosecheck`，`nilerr`，`errcheck`，`govet`，`staticcheck`。有关配置和使用，请参阅 `samber/cc-skills-golang@golang-lint` 技能。

进行更深入的安全特定分析：

```bash
# Go 安全检查器 (SAST)
go get -tool github.com/securego/gosec/v2/cmd/gosec@latest
go tool gosec ./...

# 漏洞扫描器——有关 govulncheck 的完整使用，请参阅 golang-dependency-management
go get -tool golang.org/x/vuln/cmd/govulncheck@latest
go tool govulncheck ./...
```

要检查特定模块或版本的已知 CVE，而无需扫描整个树（例如，在审查对 pkg.go.dev 的依赖项时）→ 参阅 `samber/cc-skills-golang@golang-pkg-go-dev` 技能。

### 安全测试

```bash
# 竞态检测器
go test -race ./...

# 混淆测试
go test -fuzz=Fuzz
```

## 常见错误

| 严重程度 | 错误 | 修复 |
| --- | --- | --- |
| 高 | `math/rand` 用于令牌 | 输出是可预测的——攻击者可以重现序列。使用 `crypto/rand` |
| 严重 | SQL 字符串连接 | 攻击者可以修改查询逻辑。参数化查询将数据与代码分离 |
| 严重 | `exec.Command("bash -c")` | Shell 解释元字符（`;`，`\|`，`` ` ``）。分开传递参数以避免 shell 解析 |
| 高 | 信任未清理的输入 | 在信任边界处验证——内部代码信任边界，因此在那里捕获恶意输入可以保护所有内容 |
| 严重 | 硬编码密钥 | 密钥在源代码中，最终会出现在版本历史记录、CI 日志和备份中。使用环境变量或密钥管理器 |
| 中 | 使用 `==` 比较密钥 | `==` 在第一个不同字节处短路，泄露时间信息。使用 `crypto/subtle.ConstantTimeCompare` |
| 中 | 返回详细错误 | 堆栈跟踪和 DB 错误帮助攻击者映射您的系统。返回通用消息，在服务器端记录详细信息 |
| 高 | 忽略 `-race` 找到的结果 | 竞态会导致数据损坏，并且在并发下可能绕过授权检查。修复所有竞态 |
| 高 | MD5/SHA1 用于密码 | 两者都有已知的碰撞攻击，并且快速暴力破解。使用 Argon2id 或 bcrypt（故意缓慢、内存密集型） |
| 高 | 没有 GCM 的 AES | ECB/CBC 模式缺乏认证——攻击者可以未经检测地修改密文。GCM 提供加密+认证 |
| 中 | 绑定到 0.0.0.0 | 暴露服务到所有网络接口。绑定到特定接口以限制攻击面 |

## 安全反模式

| 严重程度 | 反模式 | 为什么失败 | 修复 |
| --- | --- | --- | --- |
| 高 | 安全通过模糊性 | 隐藏的 URL 可以通过模糊测试、日志或源发现 | 所有端点的身份验证+授权 |
| 高 | 信任客户端标题 | `X-Forwarded-For`，`X-Is-Admin` 可以轻易伪造 | 服务器端身份验证 |
| 高 | 客户端端身份验证 | JavaScript 检查被任何 HTTP 客户端绕过 | 每个处理程序上的服务器端权限检查 |
| 高 | 跨环境共享密钥 | 部署中的漏洞会危及生产 | 通过密钥管理器按环境使用密钥 |
| 严重 | 忽略密码学错误 | `_, _ = encrypt(data)` 默默地未加密进行 | 始终检查错误——失败关闭，永不开放 |
| 严重 | 自己实现密码学 | 自定义加密尚未经过密码学家分析 | 使用 `crypto/aes` GCM，`golang.org/x/crypto/argon2` |

有关详细反模式及其 Go 代码示例，请参阅 **[安全架构](./references/architecture.md)**。

## 跨参考

参阅 `samber/cc-skills-golang@golang-database`，`samber/cc-skills-golang@golang-safety`，`samber/cc-skills-golang@golang-可观察性`，`samber/cc-skills-golang@golang-持续集成` 技能。

- → 参阅 `samber/cc-skills-golang@golang-持续集成` 技能，使用这些指南在 CI 中进行自动 AI 驱动的代码审查

## 其他资源

- [Go 安全最佳实践](https://go.dev/doc/security/best-practices)
- [gosec 安全代码检查器](https://github.com/securego/gosec)
- [govulncheck](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck)
- [OWASP Go 安全编码实践](https://owasp.org/www-project-go-secure-coding-practices-guide/)
