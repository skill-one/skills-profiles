---
name: hack
description: 条目 P0 主要路由器和 HackSkills 的操作准则。当任务涉及 Web 应用测试、API 安全评估、侦察、漏洞筛选、利用路径规划、授权渗透测试、代码审计、源码泄露挖掘、中间件审计、SOC 筛选、检测工程、事件响应，或在深入学习任何特定主题技能之前选择正确的下一类技能时使用。此外，当用户提及“安全工程师”、“渗透测试”、“红队”、“蓝队”、“代码审计”、“源码泄露”、“SRC”时也使用。强制执行影响优先测试，完成当前资产簇后再扩展，遵循半链路到实际控制，并要求对密钥进行实时验证。
---

# 突破技巧 / HackSkills

## 概述

这是**高质量门槛和技术路由器**，用于授权的漏洞赏金、Web/API安全、渗透测试、代码审计、源代码泄露工作，以及在任务为蓝色时进行SOC/检测/响应。

它不能替代专业技术。它使代理能够：

1.  通过起始门槛（授权、角色、范围、成功定义）
2.  在能够达到实际控制的路径上投入精力
3.  根据观察到的行为路由到正确的类别/深入主题技能
4.  优先考虑结构化方法而不是基线模型记忆和扫描器转储

此文件是一个质量门槛，而不是能力上限。如果现场证据存在，未列出的表面仍然有效。

此文件不是漏洞利用手册。武器化细节存在于深入主题技能中，并且仅用于授权目标。

按需加载：

-   红队执行 → [RED_TEAM.md](./RED_TEAM.md)
-   测试矩阵和精力 → [TEST_MATRIX.md](./TEST_MATRIX.md)
-   蓝队执行 → [BLUE_TEAM.md](./BLUE_TEAM.md)
-   代码审计 → [CODE_AUDIT.md](./CODE_AUDIT.md)
-   源代码泄露 → [SOURCE_LEAK.md](./SOURCE_LEAK.md)
-   证据和报告 → [EVIDENCE_REPORT.md](./EVIDENCE_REPORT.md)

## 0. 任务起始门槛

按顺序完成。如果任何项目缺失，则停止：

1.  **授权**：书面授权、行动准则、范围、禁止事项、联系方式、紧急停止。无授权 → 拒绝。
2.  **角色**：红队测试 / 代码审计 / 源代码泄露 / 中间件审计 / 蓝色分类 / 检测工程 / 响应。允许并行工作；只有一个主要角色。
3.  **范围模式**：
    -   用户给出了固定URL/系统/仓库 → **锁定范围**：遵循同一产品的主机、网关、API域和业务流程自然暴露的相同主机额外路径。不要扫描无关的品牌线。
    -   用户给出了组织名称并要求找到边界资产 → **探索性范围**：在打开下一个之前完成当前资产集群。不要浅层搜索许多种子。
4.  **成功定义**：此任务中“完成”的含义。扫描器完成、报告发出和工单关闭不是成功。
5.  **破坏边界**：列出绝不能发生的操作。
6.  **工作目录**：在任何测试之前 → `assets/`（URLs、API清单、脚本摘录）、`evidence/`（请求、差异、截图）、`reports/`（仅确认的发现）。
7.  **问题**：如果范围不明确，仅询问1-3个技术障碍（目标、堆栈、是否存在账户）。不要使用“我是否应该继续”作为停止的方式。缺少第二个账户 → 降级到可测试的内容；不要闲置等待账户B。

不要扩展到未授权的资产。

## 1. 严格约束

-   留在范围内。范围外线索：记录，然后请求扩展。没有沉默的扩展。
-   不进行破坏性测试或破坏性隔离：删除其他人的业务数据、DROP/TRUNCATE、批量配置更改、加密/勒索类操作、无限制的DoS、擦除日志、擦除图像。
-   证明访问的写操作：仅创建可识别的测试对象，立即删除该对象。不要更改其他人的订单、地址、密码、角色或绑定。没有收费、库存清除或账户锁定。
-   不要注销、撤销或停用用户提供的会话。如果需要密码/绑定更改来证明影响，请立即恢复；如果恢复失败，请在响应处停止——不要损坏账户。
-   不要因证明漏洞而造成不可逆的损害。优先考虑只读、复制或低权限证明。
-   证据必须是可读的和可复制的。没有可重复步骤的结论是假设。
-   不要编造PoC、日志或漏洞利用链。如果路径、文件、查询和截图不一致，请降级或撤回。
-   复制的密钥是线索，直到它们通过**活性门槛**：生产接受实际值（拒绝假值），并且一个只读调用返回身份或对象列表。
-   使用会话发现的发现不是“匿名未授权”。匿名仅当漏洞没有登录状态时。
-   对于内部用户，除非时间线证明否则假设为误报或错误。
-   如果安全控制阻止实际工作，它将被绕过。修复必须包括一个可用的安全路径。

## 2. 角色路由

| 用户意图 | 主要流程 | 加载 |
|---|---|---|
| 渗透测试 / 红队 / 站点 / SRC | §§3–5 | [RED_TEAM.md](./RED_TEAM.md), [TEST_MATRIX.md](./TEST_MATRIX.md) |
| 代码审计 / 白盒 / 寻找数据泄露点 | §3 R6 | [CODE_AUDIT.md](./CODE_AUDIT.md) |
| 源代码泄露 / Git泄露 / 密钥泄露 | §3 R5 | [SOURCE_LEAK.md](./SOURCE_LEAK.md), [insecure-source-code-management](../insecure-source-code-management/SKILL.md) |
| 中间件 / 网关 / 组件审计 | §3 R7 | [RED_TEAM.md](./RED_TEAM.md) 中间件部分, [unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md) |
| 消息分类 / SOC / 搜索 | 蓝色质量门槛 | [BLUE_TEAM.md](./BLUE_TEAM.md) |
| 检测规则 | 蓝色 B6 | [BLUE_TEAM.md](./BLUE_TEAM.md), [EVIDENCE_REPORT.md](./EVIDENCE_REPORT.md) 中的模板 |
| 响应 / 法医 / 隔离 | 蓝色 B7 | [BLUE_TEAM.md](./BLUE_TEAM.md), [memory-forensics-volatility](../memory-forensics-volatility/SKILL.md), [traffic-analysis-pcap](../traffic-analysis-pcap/SKILL.md) |
| 撰写报告 | §6 | [EVIDENCE_REPORT.md](./EVIDENCE_REPORT.md) |

当任务跨越红队和蓝队时，在切换角色之前冻结当前阶段的证据。

## 3. 运作模式

### 第一步：从应用程序中绘制表面

拿到URL或应用程序后，首先绘制表面：[attack-surface-mapping](../attack-surface-mapping/SKILL.md)。肖像、业务平面、JS/流量清单（不仅是路径的密钥）、响应类、对象图。不要扫描空白肖像。不要用目录暴力或载荷喷雾打开。

### 第二步：根据观察到的行为路由

| 信号 | 首次方向 | 加载 |
|---|---|---|
| 输入反映到HTML / JS | XSS / SSTI | [injection-checking](../injection-checking/SKILL.md) |
| 服务器获取URL / 主机名 | SSRF | [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) |
| 接受XML / Office / SVG | XXE | [xxe-xml-external-entity](../xxe-xml-external-entity/SKILL.md) |
| 路径、文件名或下载是可控的 | 路径遍历 / LFI | [path-traversal-lfi](../path-traversal-lfi/SKILL.md) |
| API中有许多对象ID | IDOR / BOLA / BFLA | [auth-sec](../auth-sec/SKILL.md), [idor-broken-object-authorization](../idor-broken-object-authorization/SKILL.md) |
| 登录、重置、2FA、会话 | 认证绕过 / JWT / OAuth | [auth-sec](../auth-sec/SKILL.md) |
| 多步骤资金、优惠券、库存、审批 | 业务逻辑 / 竞态 | [business-logic-vuln](../business-logic-vuln/SKILL.md) |
| MongoDB / JSON查询语法 | NoSQL | [nosql-injection](../nosql-injection/SKILL.md) |
| CLI工具、图像处理、导入器 | 命令注入 | [cmdi-command-injection](../cmdi-command-injection/SKILL.md) |
| HTTP解析 / 前后端框架不匹配 | 请求走私 | [request-smuggling](../request-smuggling/SKILL.md) |
| Node JSON / 可控的 `__proto__` | 原型污染 | [prototype-pollution](../prototype-pollution/SKILL.md) |
| PHP弱比较 / `0e`哈希 | 类型转换 | [type-juggling](../type-juggling/SKILL.md) |
| 重复的参数名 / WAF-应用解析不匹配 | HPP | [http-parameter-pollution](../http-parameter-pollution/SKILL.md) |
| 一次性优惠券 / 库存 / 重置 / 邀请 | 竞态 | [race-condition](../race-condition/SKILL.md) |
| XML/XSLT模板 | XSLT | [xslt-injection](../xslt-injection/SKILL.md) |
| `.git` / `.svn` / `.env` / 备份 / 公共存储桶 | 源代码泄露 | [SOURCE_LEAK.md](./SOURCE_LEAK.md) |
| CSV/Excel导出 | CSV公式 | [csv-formula-injection](../csv-formula-injection/SKILL.md) |
| WebSocket升级 | WebSocket | [websocket-security](../websocket-security/SKILL.md) |
| 内部包名 | 依赖混淆 | [dependency-confusion](../dependency-confusion/SKILL.md) |
| 业务API返回401/403 | 路径 / 方法 / 头绕过 | [401-403-bypass-techniques](../401-403-bypass-techniques/SKILL.md) |
| 公共中间件管理 / 默认端口 | 默认凭证、调试、版本缺陷 | [unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md) |
| 带有命令工具的聊天助手 | 工具是否实际执行 | [llm-prompt-injection](../llm-prompt-injection/SKILL.md) |
| 文件上传 / 预览 / 转换 | 上传链——不要在存储+下载时停止 | [upload-insecure-files](../upload-insecure-files/SKILL.md) |
| GraphQL / OAuth JWT / 网关 | 匹配专业技能；完成或写入N/A | [api-sec](../api-sec/SKILL.md), [jwt-oauth-token-attacks](../jwt-oauth-token-attacks/SKILL.md) |

打开一个检查类别并不意味着只发射那一枪。走完矩阵的其余部分。

### 第三步：按此顺序投入精力

完整通过/失败规则：[TEST_MATRIX.md](./TEST_MATRIX.md)。默认顺序：

1.  对其他用户、租户或主题的非认证访问
2.  认证接管（发出会话、重置、重新绑定、交换工单）——会话内或密码更改计算
3.  交换对象标识符（任何字段名：`id` / `userId` / `tenantId` / `fileKey` / `openid` / 密文PK）
4.  使用会话，遍历对象图：列表 → 详情 → 附件/导出/批准，然后写入和业务逻辑
5.  仅在显示**差异**的表面上进行注入 / SSRF / XSS / 命令或模板执行
6.  盐、硬编码密钥、页面和脚本中的演示账户

**不要在半链上停止。** 上传存储、OTP发送或复制的密钥字符串未完成。在对象上确认的中等程度：跟随它到写入 / 跨用户 / 接管 / 执行之前再更改目标。

一个完整的“请登录”而没有业务字段不是注入表面。空列表、错误和超时不是“请登录”。

在扩展之前完成当前资产集群。

### R1. 影响，而不是合规

首先找到影响控制的最短路径。每个候选者：攻击者现在能伤害真实用户或系统吗？报告叙述是攻击链；CVSS是附录。租户管理员“允许在角色中”如果它达到平台管理员、其他租户或其他用户，仍然是一个发现。用[RED_TEAM.md](./RED_TEAM.md)中的影响阶梯对发现进行排名；第7层（纯粹的合规性）是附录仅。

### R5. 源代码泄露：挖掘线索到尽头

不要在“`.git`暴露”或“仓库是公共的”时停止。[SOURCE_LEAK.md](./SOURCE_LEAK.md)：完整树加历史 → 清单密钥和隐藏表面 → 用最小的只读调用验证仍然有效的密钥 → 将泄露视为新的攻击表面列表。

### R6. 代码审计：从数据泄露点→源代码，或源代码向前

[CODE_AUDIT.md](./CODE_AUDIT.md)。没有完整的污染路径，或者清理器被证明有效 → 不要作为确认提交。

### R7. 中间件审计是文档驱动的

阅读官方文档以获取确切的**主要版本**，构建清单，每项留痕。没有比较表的中间件结论未完成。

### 蓝色质量门槛（当主要角色是蓝色时）

成功是停留时间更短，而不是关闭率。详情：[BLUE_TEAM.md](./BLUE_TEAM.md)。

-   **B1.** 首先询问这是否会丢失数据、权限或业务*现在*。一个高置信度事件加上时间线比一百个无上下文警报更有说服力。
-   **B2.** 消息疲劳是主要风险。在人类之前丰富；每个规则都有一个所有者、FP配置文件、回溯窗口和退役条件。六个月沉默 → 首先检查日志源。
-   **B3.** 隔离默认为可逆。保留证据，然后隔离，然后清除。擦除日志不是隔离。
-   **B4.** 结论需要一个可重复的查询、时区、资产/用户/源IP、原始摘录和一个标签（TP / 良性TP / FP / 不足证据）。
-   **B5.** 在窗口内扩展相同的用户、主机、IP、令牌、哈希。进入案例的情报、IOCs和泄露样本按源代码泄露严重性处理。
-   **B6.** 检测工程从必须捕获的行为向后追溯。严格的**高置信度规则**优先。质量门槛在[BLUE_TEAM.md](./BLUE_TEAM.md)中。
-   **B7.** 响应遵循批准的剧本。新日志源在规则发货前获得字段字典、覆盖图、已知FP、所有者和退役条。

## 4. 核心技能地图

如果完整存储库存在，优先选择这些一起。以前分开的迷你技能（载荷选择、暴力选择）已合并回其主技能。

-   [攻击表面映射](../attack-surface-mapping/SKILL.md) · [侦察和方法](../recon-and-methodology/SKILL.md)
-   [XSS](../xss-cross-site-scripting/SKILL.md) · [SQLi](../sqli-sql-injection/SKILL.md) · [SSRF](../ssrf-server-side-request-forgery/SKILL.md) · [XXE](../xxe-xml-external-entity/SKILL.md) · [SSTI](../ssti-server-side-template-injection/SKILL.md)
-   [IDOR](../idor-broken-object-authorization/SKILL.md) · [CMDi](../cmdi-command-injection/SKILL.md) · [路径遍历 / LFI](../path-traversal-lfi/SKILL.md) · [CSRF](../csrf-cross-site-request-forgery/SKILL.md)
-   [API安全路由器](../api-sec/SKILL.md) · [JWT / OAuth](../jwt-oauth-token-attacks/SKILL.md) · [OAuth / OIDC](../oauth-oidc-misconfiguration/SKILL.md) · [SAML](../saml-sso-assertion-attacks/SKILL.md) · [认证绕过](../authbypass-authentication-flaws/SKILL.md)
-   [业务逻辑](../business-logic-vulnerabilities/SKILL.md) · [上传](../upload-insecure-files/SKILL.md) · [NoSQL](../nosql-injection/SKILL.md) · [请求走私](../request-smuggling/SKILL.md)
-   [原型污染](../prototype-pollution/SKILL.md) · [类型转换](../type-juggling/SKILL.md) · [HPP](../http-parameter-pollution/SKILL.md) · [竞态](../race-condition/SKILL.md)
-   [XSLT](../xslt-injection/SKILL.md) · [不安全的源代码管理](../insecure-source-code-management/SKILL.md) · [CSV公式](../csv-formula-injection/SKILL.md) · [WebSocket](../websocket-security/SKILL.md) · [依赖混淆](../dependency-confusion/SKILL.md)
-   [CORS](../cors-cross-origin-misconfiguration/SKILL.md) · [幽灵位转换攻击](../ghost-bits-cast-attack/SKILL.md) · [401/403绕过](../401-403-bypass-techniques/SKILL.md) · [常见服务](../unauthorized-access-common-services/SKILL.md)

## 5. 高价值专家直觉

基线模型遗漏但在实际赏金工作中经常命中：

1.  **相同的过滤器跨页面重复使用**：一个绕过通常可以扩展。
2.  **参数名是攻击表面**：WAF通常检查值而不是名称。
3.  **二级常见**：在存储时安全，在稍后读取到危险上下文中不安全。
4.  **BOLA是“已认证但未授权”**：在切换账户A/B时重放。
5.  **旧API版本缺少补丁**：修复v2不会退役v1。
6.  **业务逻辑漏洞通常具有最高影响**：扫描器会遗漏它们；它们持续时间更长。
7.  **竞态条件：优先考虑一次性操作**：兑换、申领、重置、邀请、试用、库存减少。
8.  **JWT：首先检查密钥和算法上下文**：`alg`、`kid`、JWKS、密钥来源——不要盲目喷射。

## 6. 输出标准

默认按受众分为三层：

1.  决策：发生了什么，影响，现在该做什么（一页）
2.  技术：攻击链或事件时间线，可重复或查询，证据
3.  改进：修复 / 检测 / 日志差距 / 流程差距，每项都有所有者和验证

使用[刘证报告.md](./EVIDENCE_REPORT.md)中的模板。中等及以上：立即写入磁盘。严重：立即通知授权联系人。

在发现之前有两个门槛是“确认”：

-   **会话归属门槛**：如果破坏请求携带了会话，请写入IDOR/认证——不是“匿名未授权”。
-   **密钥活性门槛**：假拒绝+真接受，并且一个只读调用返回身份或列表。否则它是一个线索。

## 7. 反模式

- 将扫描结果作为渗透测试报告；用CVSS代替业务影响；提交无法利用的理论来增加计数
- 将`.git`或秘密字符串报告为信息泄露；代码审计仅列出危险函数名称而不提供源→汇路径
- 中间件结论基于内存，未与官方文档进行对比
- 在读取锁定策略之前喷洒密码；每条路径使用一个引号作为"注入完成"的标记
- 在上传存储、OTP发送或复制密钥时停止扫描
- 将会话发现写为匿名未授权
- 使用空肖像扫描，或仅提取路径的脚本进行扫描
- 将完整矩阵倾倒入相同的"请登录"响应中
- 蓝队通过关闭率衡量；将证据不足的警报标记为误报并遗忘；发布规则从未在真实日志上测试；在隔离期间擦除唯一证据
- 设计一个无人能用的"安全"流程，强制使用影子IT
- 假装未列出的字段表面不存在
- 将此文件遗漏的任何内容视为禁止

## 建议提示

- "我只拥有这个URL；在测试前从应用程序中绘制攻击面。"
- "使用赏金方法论，以影响为先，规划此目标的测试路线。"
- "这是一个REST API；优先考虑BOLA、BFLA、批量赋值和JWT。"
- "此参数触发服务器端请求；列出SSRF验证点。"
- "支付/优惠券/库存流程：业务逻辑和竞争优先。"
- "我只看到登录和密码重置：身份绕过+OAuth/JWT+CSRF。"
- "审计此仓库源→汇；没有污染路径则不报告发现。"
- "`.git`暴露：挖掘历史记录和实时验证密钥，然后将其视为新的表面列表。"

## 安装说明

推荐技能名称：`hack`

搜索关键词：`HackSkills`，`HACKING SKILLS`，`bug bounty`，`security engineer ops`

## 指南

- 按目标类型和观察到的行为进行路线规划，而不是随机枚举有效载荷。
- 有效载荷：在匹配的深度技能中使用第一遍样本；不要添加另一个中间路由器。
- 优先使用可重用过滤器、共享组件和跨页面复现。
- 在更深层次利用之前确认身份验证、授权和版本边界。
- 保持过程可解释、可审计和可重复。
- 在拥有完整仓库上下文时，返回主题文档以获取利用细节。
