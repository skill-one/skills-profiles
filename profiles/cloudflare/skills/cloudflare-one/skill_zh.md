# Cloudflare One

在引用限制、设置、API 字段、类别 ID 或确切 UI 路径之前，请从 [Cloudflare One 文档](https://developers.cloudflare.com/cloudflare-one/)、Cloudflare 文档 MCP 服务器或 Cloudflare API 模式中检索当前信息。

## 工作流程

1.  对需求进行分类：架构、配置、故障排除、迁移或审核。
2.  收集上下文：账户 ID、用户/站点/应用程序、身份提供程序、SCIM/组同步、设备管理、流量路径、合规性约束和发布范围。
3.  仅检索与所涉及产品相关的当前文档：Access、Gateway、WARP/设备客户端、Tunnel/Mesh、Cloudflare WAN、DLP、CASB、设备姿态或身份。
4.  如果有账户访问权限，则在提出或进行更改之前检查现有资源：Access 应用/策略/组/IdP、Gateway 规则/列表/类别、设备配置文件/姿态检查、隧道/路由、DNS/解析器设置以及位置/站点。
5.  提出更改集，包括先决条件、验证和回滚。对于有风险更改，除非用户明确要求否则将其禁用或限制为试点组/站点。

## 评估提示

使用这些提示以避免直接跳转到配置。仅询问与用户任务相关的提示。

### 架构和当前状态

- 站点和用户：办公室、分支机构、数据中心、VPC、远程用户、承包商、用户数量以及当前连接模型。
- 应用程序和目的地：SaaS、公共应用程序、私有应用程序、API、基础设施目标、协议、端口、主机名和 IP 范围。
- 连接：VPN、MPLS、SD-WAN、直接互联网出站、集中式背haul、站点到站点需求以及私有 DNS 架构。
- 安全堆栈：当前的 SWG、NGFW、VPN/ZTNA、DLP、CASB、电子邮件安全、日志记录和合规性要求。
- 身份：IdP、SCIM/组同步、组命名、多 IdP 需求、服务账户以及承包商/合作伙伴访问。
- 发布：试点用户/站点、影响范围、回滚路径、支持所有者以及成功标准。

### Access 和 SaaS 联邦

- 应用程序形状：Web 应用程序、API、SSH/RDP/VNC、数据库、SaaS 应用程序、公共主机名、私有 IP 或私有主机名。在选择之前，请检索 [Access 应用程序类型](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/) 文档。
- Access 模型：无客户端浏览器访问、使用设备客户端的私有网络、对等连接、使用服务令牌或相互 TLS 的服务连接，或 SaaS SSO 联邦。
- 策略需求：用户组、设备姿态、会话持续时间、mTLS、服务令牌和应用程序启动器可见性。在配置选择器或评估顺序之前，请检索 [Access 策略](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/) 文档。
- SaaS 详细信息：SAML 与 OIDC 支持、ACS/重定向 URL、实体 ID/客户端 ID、所需属性以及租户控制要求。

### Tunnel 和私有网络

- 站点和段：哪些数据中心、VPC、办公室或网络段需要连接。
- 高可用性：开发/测试单个连接器、生产多个连接器或高级多隧道/站点冗余。
- 运行时：cloudflared 或 WARP Connector/Mesh 将在何处运行：VM、容器、Kubernetes、裸金属或其他目标。
- 出站：连接器是否可以通过所需的出站端口/协议连接到 Cloudflare。在命名确切端点之前，请检索 [Tunnel 连接预检查](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/troubleshoot-tunnels/connectivity-prechecks/)。
- 源可达性：连接器是否可以解析并到达每个私有源。
- 路由：所需的 CIDR/主机名、重叠的 IP 空间、[虚拟网络](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/tunnel-virtual-networks/)、[Split Tunnels](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/) 以及私有 DNS/[解析器策略](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/) 需求。
- 管理模型：对于新部署，除非有明确的本地配置原因，否则请使用远程管理/基于令牌的隧道，除非用户明确要求否则不要创建新的遗留策略。遗留策略与已弃用的遗留私有网络应用程序类型区分开来。
- 公共主机名 Access 应用程序可以无客户端。私有目的地应用程序需要 WARP/设备客户端或另一个网络接入点加上路由和 DNS 解析。在配置私有目的地之前，请检索 [自托管私有应用程序](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/self-hosted-private-app/) 文档。
- Cloudflare Tunnel 是从私有网络到 Cloudflare 的接入点。Cloudflare WAN 和 Mesh 也是其他接入点，但它们也可以作为接入点使用。
- 基于组的策略取决于 IdP 组声明或 SCIM。如果组同步缺失，请不要编造组选择器。
- 私有主机名需要显式 DNS 路由/解析；仅创建 Access 应用程序是不够的。使用 [解析器策略](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/) 并查看 [连接私有主机名](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/connect-private-hostname/)。
- HTTP 检查和 DLP 对于加密的 Web 流量需要 TLS 检查和计划的 Do Not Inspect 例外。
- Gateway DNS、网络、HTTP 和出站策略具有不同的评估语义。在更改规则顺序之前，请检索 [执行顺序](https://developers.cloudflare.com/cloudflare-one/traffic-policies/order-of-enforcement/) 文档。
- 除非用户批准更广泛的发布，否则请将广泛的阻止/允许/DLP/TLS 策略禁用并限制为特定目标用户或组。

### 身份和访问

- Access 组是 Cloudflare 对象；IdP/SCIM 组是身份声明。Gateway 组选择器使用同步的 IdP 组，而不是 Access 组。
- 组名和 SAML/OIDC 属性区分大小写。在创建基于组的规则之前，请验证确切的声明名和值。
- SCIM 更改和组成员资格可能直到同步和重新身份验证完成才会过时。使用用户的最后认证身份而不是仅使用 IdP 状态进行故障排除。
- Access 策略默认为拒绝。具有路由但没有允许策略的私有应用程序仍然会阻止访问。
- Access 策略选择器可以使用 IP 列表，而不是 Gateway 域名或 URL 列表。
- SaaS 联邦处理对 SaaS 应用程序的认证。SaaS 授权和租户限制通常需要在 SaaS 端的角色和/或 Gateway 租户控制。
- 浏览器渲染 SSH/VNC/RDP 是 Access 功能。浏览器隔离远程渲染一般 Web 内容。不要将它们混淆。

### 设备客户端部署

- [Cloudflare One 设备客户端](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/) 是用户设备的接入点。两个组件控制它：**注册规则**（谁可以连接）和**设备配置文件**（注册后客户端的行为）。
- 注册规则是类型为 `warp` 的 Access 应用程序，而不是设备设置。它接受可重用的 Access 策略。在 Access 中查找注册调试，而不是在设备中。
- 对于无头或自主设备（服务、自助服务亭、Linux 主机），请使用服务令牌注册。非人类设备通过 `non_identity@[team-domain].cloudflareaccess.com` 进行身份验证，并且没有组成员资格 - 目标 IdP 组的设备配置文件将不会匹配它们。使用非身份电子邮件、特定于设备的约定（OS 信息等）或让它们落入默认配置文件来显式针对无头设备。
- 设备配置文件控制连接模式、[Split Tunnel](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/) 配置、用户权限（禁用、切换锁定）、自动重连和强制门户行为。配置文件按用户组或设备属性优先级匹配 - 第一个匹配的将获胜，默认配置文件将捕获其余部分。
- Split Tunnel 模式是影响客户端设置的最关键的客户端设置。根据部署目标选择模式：

  | 目标 | 模式 | 理由 |
  |---|---|---|
  | 仅 VPN 替换（私有应用程序） | **包含** | 仅将指定的私有 CIDR 和主机名通过客户端路由。其他所有内容都直接发送。影响范围最小。 |
  | 仅 SWG（互联网安全） | **排除** | 所有流量通过客户端。仅排除会中断的流量（本地打印机、证书固定应用程序）。 |
  | VPN 替换 + SWG | **排除** | 所有流量通过客户端。最常见的 企业 配置。 |
  | 与其他 VPN 共存 | **包含** | 避免与其他 VPN 的隧道接口和 DNS 控制冲突。 |
  | 仅 DNS 过滤 | DNS-only 模式 | 仅 DNS 查询发送到 Gateway。不进行流量代理。 |

- 包含与排除是按配置文件而不是按条目区分的。您不能在同一配置文件中混合模式。在部署期间切换模式需要重新评估每个条目。
- Split Tunnel 条目必须与隧道路由双向对齐。包含列表中缺少匹配隧道路由的 CIDR 会导致黑洞。没有匹配设备配置文件条目的隧道路由意味着流量永远不会进入隧道。
- MDM 参数（`mdm.xml` / 管理偏好设置）会覆盖仪表板配置的配置文件设置中指定的任何设置。如果仪表板更改对受管设备似乎没有影响，请检查 MDM 配置。检索 [MDM 部署](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/deployment/mdm-deployment/) 文档以获取平台特定的文件位置和参数。
- 如果另一个 VPN 客户端或代理控制设备的 DNS，则设备客户端的 DNS 截取将发生冲突。在共存场景中，使用“仅流量”模式以避免路由表和 DNS 冲突。
- 强制门户检测在检测到门户（酒店 WiFi、机场）时暂时断开客户端连接。这是导致最终用户摩擦的常见原因，应谨慎管理。

### 私有网络

- Split Tunnel 模式会改变每个路由决策的含义：排除模式将流量发送到 Cloudflare，当它从排除列表中移除时；包含模式仅当它被添加到包含列表中时才发送流量。
- 虚拟网络主要用于 IP 子网重叠且不使用基于主机名的路由时。它可以用于控制其他用户连接行为，但建议通过安全策略进行管理。
- 健康的隧道仅证明 cloudflared 可以到达 Cloudflare。隧道必须具有适当发布的应用程序路由、网络路由或主机名路由才能使连接功能正常工作。
- Cloudflare Tunnel 和 Cloudflare Mesh 都可用于促进对内部网络的连接。Cloudflare WAN 也可以，但它受企业订阅限制。在考虑 Tunnel 类型时，请检索 [选择接入点](https://developers.cloudflare.com/learning-paths/secure-internet-traffic/connect-devices-networks/choose-on-ramp/)。
- 对于生产高可用性，请运行多个 cloudflared 连接器，最好在不同的主机上。新部署的默认是基于令牌的远程管理隧道。

### Gateway、TLS 和 DLP

- `dns.domains` 匹配域和子域；`dns.fqdn` 仅精确匹配。
- DNS 预解析选择器和解析后选择器不会像单个严格优先级列表一样行为。在更改规则顺序之前，请检索当前评估文档。
- HTTP Do Not Inspect 规则在 HTTP 允许/阻止/隔离行为之前运行。较后的阻止规则不会覆盖较早的检查绕过。
- 证书固定应用程序需要在启用检查之前配置 Do Not Inspect 例外。在受管设备上部署 Cloudflare 根 CA 之前启用检查。
- DLP 配置文件仅是检测定义。它们在 Gateway HTTP 策略或 CASB 扫描设置引用它们之前什么也不做。具有正文检查的规则可能在单次传递中多次评估。
- 在适当的地方开始 DLP 并记录有效载荷，然后调整误报，然后阻止。
- Gateway 网络策略是严格的 L4 控制。需要经过身份验证的设备上下文的 L4 匹配。

### CASB、风险和操作

- API CASB 是旁路且定期的。它不会提供实时内联执行，尽管某些集成支持“修复”；使用 Gateway 粒度应用程序控制为支持的应用程序提供内联 CASB 功能。在为特定 SaaS 应用程序中的特定操作创建安全策略时，请检索 [粒度应用程序控制](https://developers.cloudflare.com/cloudflare-one/traffic-policies/http-policies/granular-controls/)。
- CASB 发现与特定资产和实例相关联。在建议修复之前，请深入查看受影响的资产。
- 使用当前仪表板修复指导来修复 CASB 问题。大多数修复发生在 SaaS 管理控制台，而不是 Cloudflare。
- 大型 SaaS 集成可能需要 24-48 小时进行初始扫描。重新授权可以重新启动扫描状态；在重新连接之前检查凭证健康状况。
- 用户风险评分是基于行为异步的。CASB 发现不会自动意味着高风险用户。

### 基础设施访问

- [零信任基础设施访问](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/infrastructure-apps/) (ZTIA) 是专为通过设备客户端进行 SSH 访问而设计的解决方案。它提供了通过自托管应用程序无法提供的功能：按键记录、控制用户如何认证到目标机器、[短期证书](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-infrastructure-access/#generate-a-cloudflare-ssh-ca)（用与 Access 身份相关联的临时证书替换静态 SSH 密钥）以及轻量级特权访问管理。当设备客户端部署时，请使用 Infrastructure Access 应用程序进行 SSH。
- [浏览器渲染](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/non-http/browser-rendering/) 通过浏览器提供无客户端 SSH、RDP 和 VNC，而无需设备客户端。无客户端 RDP 包括会话记录和文件传输控制。当设备客户端无法安装时（承包商、合作伙伴访问、未管理设备）使用无客户端访问 - 通常不作为已安装客户端的受管用户的默认设置。
- [审核 SSH](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-infrastructure-access/#enable-ssh-command-logging) 是 Gateway 网络策略操作，它在不阻止的情况下记录 SSH 命令。它需要会话通过 Cloudflare 进行代理。
- 短期证书需要在目标主机上配置 CA，并且 `sshd` 需要信任 Cloudflare CA 公钥。在配置之前，请检索 [短期证书设置](https://developers.cloudflare.com/cloudflare-one/identity/users/short-lived-certificates/) 文档。
- 对于私有网络后面的 kubectl 和数据库访问，请使用设备客户端和私有目的地路由。今天还没有 Infrastructure Access 或浏览器渲染的任意 TCP 协议等效方案。

### 日志、分析和 DEX

- [Gateway 活动日志](https://developers.cloudflare.com/cloudflare-one/analytics/logs/gateway-logs/) 记录 DNS、HTTP 和网络策略决策。按规则名、用户身份、目的地、操作和时间范围过滤。这些是“为什么阻止/允许”的主要故障排除工具。
- [Access 审计日志](https://developers.cloudflare.com/cloudflare-one/insights/logs/dashboard-logs/access-authentication-logs/) 记录每个应用程序的认证决策 - 谁进行了认证、哪个策略匹配以及会话详细信息。用于验证策略行为和调查访问失败。
- [影子 IT 发现](https://developers.cloudflare.com/cloudflare-one/insights/analytics/shadow-it-discovery/) 使用 Gateway HTTP 日志来揭示未管理的 SaaS 应用程序。需要 TLS 检查才能获得 HTTPS 可见性。
- [DEX（数字体验监控）](https://developers.cloudflare.com/cloudflare-one/insights/dex/) 提供舰队级和每个设备的连接诊断。使用 [DEX 测试](https://developers.cloudflare.com/cloudflare-one/insights/dex/tests/)（HTTP、traceroute）主动监控对关键来源和内部应用程序的可达性。舰队状态显示设备客户端健康、连接模式以及注册人群中连接状态。
- [Logpush](https://developers.cloudflare.com/cloudflare-one/analytics/logs/logpush/) 将 Gateway、Access、网络和 DEX 日志导出到外部 SIEM 或存储。如果客户要求集中日志保留或合规性报告，请在上线前配置。
- 在故障排除时，从日志开始，然后是配置：识别显示失败的日志条目（Gateway 阻止、Access 拒绝、隧道错误、DNS 解析失败），然后追溯到负责的规则、路由或策略。

### Cloudflare WAN / 站点连接

- Cloudflare WAN 是连接，而不是安全服务。在需要的地方使用 Gateway 和 Network Firewall 应用检查和政策。
- WAN 防火墙表达式与 Gateway 线路过滤器表达式不是同一种语言。在编辑之前，请检索当前语法。
- 生成的 IPsec PSK 和某些 OAuth/客户端密钥返回一次。请立即存储它们。

## 输出默认值

- 设计：当前假设、目标架构、产品责任、发布阶段、验证和开放决策。
- 配置工作：先决条件、要检查/创建/更改的确切资源、测试用例和回滚。
- 故障排除：流量路径、可能的故障点、要收集的证据和下一个测试。

## 验证提示

- Access：在适用的情况下测试授权的、未授权的、姿态失败的、服务令牌和多个 IdP 流；检查日志和策略优先级。对于新策略，请验证它们是通过可重用策略集合管理的，而不是作为 `reusable: false` 应用程序范围策略返回。
- 私有网络访问：验证路由查找、隧道健康、源可达性、Split Tunnel 行为、DNS 解析和从设备客户端测试设备端到端的访问。
- Gateway：在启用广泛之前，验证规则类型、操作、流量表达式、优先级/评估阶段、引用的列表和 Gateway 设置。
- TLS/DLP：在启用检查之前测试 Do Not Inspect 例外和根 CA 信任；使用已知样本测试 DLP 并监控误报，然后再阻止。
- CASB/风险：在声明修复完成之前，确认集成健康状况、凭证过期、资产发现、扫描时间、发现实例和风险评分信号延迟。
- Cloudflare WAN：验证隧道健康、路由优先级/所有权、流量、防火墙表达式语法以及适用时的连接器/设备仪表板。
## API 安全

- 当 MCP 工具可用时，请使用完全限定的 MCP 工具名称。
- 永远不要猜测类别 ID、应用程序 ID、线路过滤器字段或 API 请求正文。检索当前模式/文档和现有账户对象。
- 不要在未经明确批准的情况下启用广泛的生产策略。
