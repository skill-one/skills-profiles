---
name: cloudflare-one
description: 设计、配置、排错或审查 Cloudflare One 零信任和 SASE 部署。使用 cloudflare-one-migrations 进行从其他供应商的迁移规划。
---

# Cloudflare One

在引用限制、设置、API 字段、类别 ID 或确切 UI 路径之前，请从 [Cloudflare One 文档](https://developers.cloudflare.com/cloudflare-one/)、Cloudflare 文档 MCP 服务器或 Cloudflare API 模式中检索当前信息。

## 工作流程

1.  对需求进行分类：架构、配置、故障排除、迁移或审查。
2.  收集上下文：账户 ID、用户/站点/应用程序、身份提供程序、SCIM/组同步、设备管理、流量路径、合规性约束和发布范围。
3.  仅检索与所涉及产品相关的当前文档：Access、Gateway、WARP/设备客户端、Tunnel/Mesh、Cloudflare WAN、DLP、CASB、设备姿态或身份。
4.  如果有账户访问权限，则在提出或进行更改之前检查现有资源：Access 应用/策略/组/IdP、Gateway 规则/列表/类别、设备配置文件/姿态检查、隧道/路由、DNS/解析器设置以及位置/站点。
5.  提出更改集，包括先决条件、验证和回滚。对于有风险更改，除非用户明确要求否则应将其禁用或限定在试点组/站点内。

## 评估提示

使用这些提示来避免直接跳转到配置。仅询问与用户任务相关的提示。

### 架构和当前状态

- 站点和用户：办公室、分支机构、数据中心、VPC、远程用户、承包商、用户数量以及当前连接模型。
- 应用程序和目的地：SaaS、公共应用程序、私有应用程序、API、基础设施目标、协议、端口、主机名和 IP 范围。
- 连接性：VPN、MPLS、SD-WAN、直接互联网出站、集中式回程、站点到站点需求以及私有 DNS 架构。
- 安全堆栈：当前的 SWG、NGFW、VPN/ZTNA、DLP、CASB、电子邮件安全、日志记录和合规性要求。
- 身份：IdP、SCIM/组同步、组命名、多 IdP 需求、服务账户以及承包商/合作伙伴访问。
- 发布：试点用户/站点、发布范围、回滚路径、支持所有者以及成功标准。

### Access 和 SaaS 联邦

- 应用程序形状：Web 应用程序、API、SSH/RDP/VNC、数据库、SaaS 应用程序、公共主机名、私有 IP 或私有主机名。在选择之前，请检索 [Access 应用程序类型](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/) 文档。
- Access 模型：无客户端浏览器访问、私有网络与设备客户端、对等连接、使用服务令牌或相互 TLS 的服务连接，或 SaaS SSO 联邦。
- 策略需求：用户组、设备姿态、会话持续时间、mTLS、服务令牌和应用程序启动器可见性。在配置选择器或评估顺序之前，请检索 [Access 策略](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/) 文档。
- SaaS 详细信息：SAML 与 OIDC 支持、ACS/重定向 URL、实体 ID/客户端 ID、所需属性以及租户控制要求。

### Tunnel 和私有网络

- 站点和段：哪些数据中心、VPC、办公室或网络段需要连接。
- 高可用性：开发/测试单个连接器、生产多个连接器或高级多隧道/站点冗余。
- 运行时：cloudflared 或 WARP Connector/Mesh 将在何处运行：VM、容器、Kubernetes、裸金属或其他目标。
- 出站：连接器是否可以通过所需的出站端口/协议连接到 Cloudflare。在命名确切端点之前，请检索 [Tunnel 连接预检查](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/troubleshoot-tunnels/connectivity-prechecks/)。
- 源可达性：连接器是否可以解析并到达每个私有源。
- 路由：所需的 CIDR/主机名、重叠的 IP 空间、[虚拟网络](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/tunnel-virtual-networks/)、[Split Tunnels](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/) 以及私有 DNS/[解析器策略](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/) 需求。
- 管理模型：对于新部署，除非有明确的本地配置原因，否则请使用远程管理/基于令牌的隧道，除非当前 API 文档明确要求应用程序范围的策略。

### Gateway、TLS 和 DLP

- 流量控制：DNS 类别、HTTP URL/路径检查、L4 端口/协议、出站 IP 要求、自定义列表以及允许/阻止例外。检索 [Gateway 流量策略](https://developers.cloudflare.com/cloudflare-one/traffic-policies/) 文档以获取当前的 选择器和执行顺序。
- 身份：Gateway 策略是否需要用户或组选择器，以及用户是否将通过 WARP/IdP 上下文进行身份验证。当涉及组时，请检查 [Gateway 身份选择器](https://developers.cloudflare.com/cloudflare-one/traffic-policies/identity-selectors/) 和 [SCIM 提供项](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/scim/)。
- TLS 检查：根 CA 部署路径、证书固定应用程序、合规性例外和 FIPS 要求。在启用之前，请检索 [TLS 解密](https://developers.cloudflare.com/cloudflare-one/traffic-policies/http-policies/tls-decryption/) 文档。
- DLP：敏感数据类型、要检查的通道、TLS 检查准备情况、DLP 配置文件、有效负载日志记录要求以及误报容忍度。在创建执行之前，请检索 [DLP](https://developers.cloudflare.com/cloudflare-one/data-loss-prevention/) 文档。

### CASB、设备姿态和风险

- CASB：SaaS 供应商、管理员访问级别、扫描策略、组织规模、修复负责人，以及是否还需要内联保护。在推荐修复之前，请检索 [CASB 查找](https://developers.cloudflare.com/cloudflare-one/cloud-and-saas-findings/manage-findings/) 文档。
- 设备姿态：所需检查、第三方 EDR/MDM 集成、入组规则、设备配置文件和 Split Tunnel 对齐。
- 风险评分：相关行为信号、VPN 或服务账户等误报来源，以及风险是用于调查还是执行。在将风险用于策略之前，请检索 [用户风险评分](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/risk-score/) 文档。

### Cloudflare WAN / 站点连接性

- 站点拓扑、上载类型、路由所有权、隧道冗余、静态与 BGP 管理路由、网络防火墙需求以及设备/配置文件所有权。在提出站点连接性更改之前，请检索 [Cloudflare WAN](https://developers.cloudflare.com/cloudflare-wan/) 和 [Cloudflare 网络防火墙](https://developers.cloudflare.com/cloudflare-network-firewall/) 文档。

## 安全边界

- Access 控制应用授权；Gateway 控制流量检查/过滤。当需求跨越身份感知应用程序访问和网络/Web 安全时，请同时使用两者。
- 对于新的 Access 部署，请通过可重用策略 API (`/access/policies`) 创建策略，并将它们附加到应用程序。除非当前 API 文档明确要求应用程序范围的策略，否则不要在应用程序创建/更新请求中发送内联 `policies`。
- 将报告为 `reusable: false` 的应用程序范围策略视为遗留。使用文档中记录的 `make_reusable` 端点迁移现有策略，或用可重用策略替换它们；不要创建新的遗留策略。区分遗留策略和已弃用的遗留私有网络应用程序类型。
- 公共主机名 Access 应用程序可以是无客户端的。私有目的地应用程序需要 WARP/设备客户端或另一个网络上载加上路由和 DNS 解析。在配置私有目的地之前，请检索 [self-hosted private app](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/self-hosted-private-app/) 文档。
- Cloudflare Tunnel 是从私有网络到 Cloudflare 的一个上载。Cloudflare WAN 和 Mesh 也是其他上载，它们也可以用作上载。
- 基于组的策略取决于 IdP 组声明或 SCIM。如果组同步缺失，请不要编造组选择器。
- 私有主机名需要显式 DNS 路由/解析；仅创建 Access 应用程序是不够的。使用 [解析器策略](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/) 并查看 [连接私有主机名](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/connect-private-hostname/)
- HTTP 检查和加密 Web 流量的 DLP 需要 TLS 检查和计划的 Do Not Inspect 例外。
- Gateway DNS、网络、HTTP 和出站策略具有不同的评估语义。在解释优先级之前，请检索当前的执行顺序文档。
- 从宽泛的阻止/允许/DLP/TLS 策略开始，禁用并限制在特定目标用户或组上的试点，除非用户批准更广泛的发布。

### 身份和访问

- Access 组是 Cloudflare 对象；IdP/SCIM 组是身份声明。Gateway 组选择器使用同步的 IdP 组，而不是 Access 组。
- 组名和 SAML/OIDC 属性区分大小写。在创建基于组的规则之前，请验证确切的声明名和值。
- SCIM 更改和组成员资格可能直到同步和重新身份验证完成才会过时。使用用户的最后身份验证身份进行故障排除，而不仅仅是 IdP 状态。
- Access 策略默认为拒绝访问。具有路由但没有允许策略的私有应用程序仍然会阻止访问。
- Access 策略选择器可以使用 IP 列表，而不是 Gateway 域名或 URL 列表。
- SaaS 联邦处理对 SaaS 应用程序的认证。SaaS 授权和租户限制通常需要在 SaaS 端的角色和/或 Gateway 租户控制。
- 浏览器渲染 SSH/VNC/RDP 是 Access 功能。浏览器隔离远程渲染通用 Web 内容。不要将它们混淆。

### 设备客户端部署

- [Cloudflare One 设备客户端](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/) 是用户设备的上载。两个组件控制它：**入组规则**（谁可以连接）和 **设备配置文件**（入组后客户端的行为）。
- 入组规则是一个类型为 `warp` 的 Access 应用程序，而不是设备设置。它接受可重用的 Access 策略。在 Access 中查找入组调试，而不是设备。
- 对于无头或自主设备（服务、自助服务终端、Linux 主机），请使用服务令牌入组。非人类设备作为 `non_identity@[team-domain].cloudflareaccess.com` 进行身份验证，并且没有组成员资格 - 目标 IdP 组的设备配置文件将不会匹配它们。请使用非身份电子邮件、特定于设备（操作系统信息等）的约定或让它们落入默认配置文件来显式目标无头设备。
- 设备配置文件控制连接模式、[Split Tunnel](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/) 配置、用户权限（禁用、切换锁定）、自动重连和捕获门户行为。配置文件按用户组或设备属性的优先级顺序匹配 - 第一个匹配的将获胜，默认配置文件将捕获其余部分。
- Split Tunnel 模式是影响客户端设置的最关键的设置。根据部署目标选择模式：

  | 目标 | 模式 | 理由 |
  |---|---|---|
  | 仅 VPN 替换（私有应用程序） | **Include** | 仅将指定的私有 CIDR 和主机名通过客户端路由。其他所有内容都直接发送。最小的发布范围。 |
  | 仅 SWG（互联网安全） | **Exclude** | 所有流量通过客户端。仅排除导致中断的内容（本地打印机、证书固定应用程序）。 |
  | VPN 替换 + SWG | **Exclude** | 所有流量通过客户端。最常见的 企业配置。 |
  | 与另一个 VPN 共存 | **Include** | 避免与其他 VPN 的隧道接口和 DNS 控制冲突。 |
  | 仅 DNS 过滤 | DNS-only 模式 | 仅 DNS 查询发送到 Gateway。不进行流量代理。 |

- Include 与 exclude 是按配置文件而不是按条目区分的。您不能在同一配置文件中混合模式。在部署期间切换模式需要重新评估每个条目。
- Split Tunnel 条目必须与隧道路由双向对齐。Include 列表中的 CIDR 没有匹配的隧道路由会导致黑洞。没有匹配的设备配置文件条目的隧道路由意味着流量永远不会进入隧道。
- MDM 参数（`mdm.xml` / 受管首选项）会覆盖仪表板配置的配置文件设置中指定的任何设置。如果仪表板更改似乎对受管设备没有影响，请检查 MDM 配置。检索 [MDM 部署](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/deployment/mdm-deployment/) 文档以获取特定于平台的文件位置和参数。
- 如果另一个 VPN 客户端或代理控制设备的 DNS，则设备客户端的 DNS 截获将发生冲突。在对等场景中，使用“仅流量”模式以避免路由表和 DNS 冲突。
- 捕获门户检测在检测到门户（酒店 WiFi、机场）时暂时断开客户端连接。这是导致最终用户摩擦的常见来源，应谨慎管理。

### 私有网络

- Split Tunnel 模式会改变每个路由决策的含义：Exclude 模式在从排除列表中移除时将流量发送到 Cloudflare；Include 模式仅在添加到 Include 列表时才发送流量。
- 虚拟网络主要用于 IP 子网重叠且不使用基于主机名的路由时。它可以用于控制其他用户连接行为，但建议通过安全策略进行管理。
- 健康的隧道仅证明 cloudflared 可以到达 Cloudflare。隧道必须具有适当发布的应用程序路由、网络路由或主机名路由才能使连接功能正常工作。
- Cloudflare Tunnel 和 Cloudflare Mesh 都可用于促进对内部网络的连接。Cloudflare WAN 也可以，但它受企业订阅限制。在考虑 Tunnel 类型时，请检索 [选择一个上载](https://developers.cloudflare.com/learning-paths/secure-internet-traffic/connect-devices-networks/choose-on-ramp/)。
- 对于生产高可用性，请运行多个 cloudflared 连接器，最好在单独的主机上。新部署的默认是基于令牌的远程管理隧道。

### Gateway、TLS 和 DLP

- `dns.domains` 匹配域和子域；`dns.fqdn` 仅精确匹配。
- DNS 预解析选择器和解析器后选择器不会像单个严格优先级列表一样行为。在更改规则顺序之前，请检索当前的评估文档。
- HTTP Do Not Inspect 规则在 HTTP Allow/Block/Isolate 行为之前运行。较后的阻止规则不会覆盖较早的检查绕过。
- 证书固定应用程序需要在 broad TLS 检查之前添加 Do Not Inspect 例外。在启用检查之前，请部署 Cloudflare 根 CA 到受管设备。
- DLP 配置文件仅是检测定义。它们在 Gateway HTTP 策略或 CASB 扫描设置引用它们之前什么也不做。在单个传递中，可能多次评估具有有效负载检查的规则。
- 适当情况下，请从有效负载日志记录开始 DLP，调整误报，然后阻止。
- Gateway 网络策略是严格的 L4 控制。需要经过身份验证的设备上下文的 L4 匹配。

- API CASB 是离线的，并且是定期的。它不提供实时内联执行，尽管某些集成支持“修复”；使用网关粒度应用控制为支持的应用提供内联 CASB 功能。在为特定 SaaS 应用中的特定操作创建安全策略时，请获取 [粒度应用控制](https://developers.cloudflare.com/cloudflare-one/traffic-policies/http-policies/granular-controls/)。
- CASB 发现与特定资产和实例相关联。在建议修复之前，先深入调查受影响的资产。
- 使用当前仪表板的修复指导来修复 CASB 问题。大多数修复操作都在 SaaS 管理控制台中进行，而不是在 Cloudflare 中。
- 大型 SaaS 集成进行初始扫描可能需要 24-48 小时。重新授权可以重新启动扫描状态；在重新连接之前检查凭证健康状况。
- 用户风险评分基于行为，并且是异步的。CASB 发现并不自动意味着用户风险高。

### 基础设施访问

- [零信任基础设施访问](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/infrastructure-apps/) (ZTIA) 是专为通过设备客户端进行 SSH 访问而设计的解决方案。它提供了自托管应用无法提供的功能：按键记录、控制用户如何身份验证到目标机器、[短期证书](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-infrastructure-access/#generate-a-cloudflare-ssh-ca)（用临时证书替换静态 SSH 密钥，这些证书与 Access 身份关联），以及轻量级特权访问管理。当设备客户端部署时，使用基础设施访问应用进行 SSH。
- [浏览器渲染](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/browser-rendering/) 通过浏览器提供无客户端 SSH、RDP 和 VNC，而无需设备客户端。无客户端 RDP 包括会话录制和文件传输控制。当无法安装设备客户端时（承包商、合作伙伴访问、未管理的设备）使用无客户端访问——通常不作为已安装客户端的受管理用户的默认选项。
- [审计 SSH](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-infrastructure-access/#enable-ssh-command-logging) 是一种网关网络策略操作，它记录 SSH 命令而不阻止。它要求会话通过 Cloudflare 代理。
- 短期证书需要在目标主机上配置 CA，并且 `sshd` 需要配置为信任 Cloudflare CA 公钥。在配置之前，请获取 [短期证书设置](https://developers.cloudflare.com/cloudflare-one/identity/users/short-lived-certificates/) 文档。
- 对于私有网络后面的 kubectl 和数据库访问，使用具有私有目的地路由的设备客户端。目前还没有基础设施访问或浏览器渲染的任意 TCP 协议的等效方案。

### 日志、分析和 DEX

- [网关活动日志](https://developers.cloudflare.com/cloudflare-one/analytics/logs/gateway-logs/) 记录 DNS、HTTP 和网络策略决策。按规则名称、用户身份、目的地、操作和时间范围进行筛选。这些是“为什么被阻止/允许”的主要故障排除工具。
- [访问审计日志](https://developers.cloudflare.com/cloudflare-one/insights/logs/dashboard-logs/access-authentication-logs/) 按每个应用记录身份验证决策——谁进行了身份验证、哪个策略匹配以及会话详细信息。用于验证策略行为和调查访问失败。
- [影子 IT 发现](https://developers.cloudflare.com/cloudflare-one/insights/analytics/shadow-it-discovery/) 使用网关 HTTP 日志来暴露未管理的 SaaS 应用。需要 TLS 检查才能查看 HTTPS 可见性。
- [DEX（数字体验监控）](https://developers.cloudflare.com/cloudflare-one/insights/dex/) 提供舰队级和每设备的连接诊断。使用 [DEX 测试](https://developers.cloudflare.com/cloudflare-one/insights/dex/tests/)（HTTP、traceroute）主动监控对关键来源和内部应用的可达性。舰队状态显示设备客户端健康状况、连接模式以及注册人群中连接状态。
- [Logpush](https://developers.cloudflare.com/cloudflare-one/analytics/logs/logpush/) 将网关、Access、网络和 DEX 日志导出到外部 SIEM 或存储。如果客户需要集中式日志保留或合规报告，请在上线前进行配置。
- 在故障排除时，从日志开始，逐步追溯到配置：识别显示失败的日志条目（网关阻止、Access 拒绝、隧道错误、DNS 解析失败），然后追溯到负责的规则、路由或策略。

### Cloudflare WAN / 站点连接

- Cloudflare WAN 是连接性，而不是一项安全服务。在需要时，使用网关和网络防火墙应用检查和策略。
- WAN 防火墙表达式与网关线过滤器表达式不是同一种语言。在编辑前，请获取当前语法。
- 生成的 IPsec PSK 和某些 OAuth/客户端密钥只返回一次。立即存储它们。

## 输出默认值

- 设计：当前假设、目标架构、产品责任、发布阶段、验证和开放决策。
- 配置工作：先决条件、要检查/创建/更改的确切资源、测试用例和回滚。
- 故障排除：流量路径、可能的故障点、要收集的证据和下一个测试。

## 验证提示

- 访问：在适用的情况下，测试授权、未授权、立场失败、服务令牌和多 IDP 流；检查日志和政策优先级。对于新策略，请验证它们是通过可重用策略集合管理的，而不是作为返回 `reusable: false` 应用范围的策略。
- 私有网络访问：验证路由查找、隧道健康状况、来源可达性、分裂隧道行为、DNS 解析以及从设备客户端测试设备到端端的访问。
- 网关：在广泛启用之前，验证规则类型、操作、流量表达式、优先级/评估阶段、引用的列表和网关设置。
- TLS/DLP：在启用检查之前，测试不要检查例外和根 CA 信任；在阻止之前，使用已知样本测试 DLP 并监控误报。
- CASB/风险：在宣布修复完成之前，确认集成健康状况、凭证过期、资产发现、扫描时间、发现实例和风险评分信号延迟。
- Cloudflare WAN：验证隧道健康状况、路由优先级/所有权、流量、防火墙表达式语法以及在适用的情况下连接器/设备遥测。

## API 安全

- 当 MCP 工具可用时，使用完全限定名称的 MCP 工具。
- 不要猜测类别 ID、应用 ID、线过滤器字段或 API 请求正文。获取当前架构/文档和现有帐户对象。
- 不要在未经明确批准的情况下启用广泛的生产策略。
