# Cloudflare One 迁移

在生成精确配置之前，检索当前的 Cloudflare 文档、Cloudflare API 模式和源供应商导出文档。

## 工作流程

1. 识别源堆栈：Zscaler ZIA、Zscaler ZPA、Palo Alto NGFW/Prisma/GlobalProtect、传统 VPN/SWG/SD-WAN 或其他。
2. 在映射之前请求导出和日志。优先选择结构化导出而不是截图或文本摘要。
3. 构建清单：身份、组、应用程序、目标、连接器/隧道、DNS/URL/防火墙/DLP/TLS 策略、对象/列表、位置/站点、例外、命中次数和合规日志记录。
4. 生成映射计划：源对象、Cloudflare One 目标资源、置信度、先决条件、不支持的/部分映射和手动决策。
5. 首先创建依赖项：身份/[SCIM](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/scim/)、连接器/上坡、路由/DNS、列表/对象、TLS 跳过、Access 应用/策略、网关策略、DLP/CASB、日志记录。
6. 安全地分阶段：使用迁移前缀，默认创建禁用/审计模式规则，使用小组/站点进行试点，比较日志，然后扩展推广。
7. 考虑每个源规则。每个规则必须映射到 Cloudflare 对象或显式的未迁移行（原因和安全影响）。

## 请求的导出

- ZIA：URL 过滤、防火墙过滤、SSL 检查、DLP、自定义 URL 类别、IP 组、网络服务/服务组、用户/组/部门、位置、GRE 隧道和静态 IP。
- ZPA：应用程序分段、分段组、服务器组、应用程序连接器/连接器组、访问策略、IdP/组映射、私有 DNS 域名、端口和协议。
- Palo Alto/Prisma：安全/NAT/解密规则、地址/服务对象和组、URL 类别、HIP 配置文件、GlobalProtect 配置、Prisma Access 远程网络/服务连接配置、区域、标签、日志和命中次数。

## 映射启发式方法

- ZIA/SWG 策略通常映射到 [网关流量策略](https://developers.cloudflare.com/cloudflare-one/traffic-policies/) 和网关列表。
- ZPA 私有应用程序访问通常映射到 [Access 应用类型](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/)、[Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/)、私有网络路由/DNS 和 [Access 策略](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/)。
- Palo Alto 规则只有在理解流量方向、区域、对象、用户、应用程序、解密和命中次数后才能映射。不要盲目地将区域扁平化为列表。
- 传统 VPN 替换通常是 Access + Cloudflare One 客户端 / WARP + Tunnel 或 Mesh 用于应用程序访问。仅在需要站点到站点流量时使用 [Cloudflare WAN](https://developers.cloudflare.com/cloudflare-wan/)；使用 [网络 VPN 迁移设计指南](https://developers.cloudflare.com/reference-architecture/design-guides/network-vpn-migration/) 和 [替换您的 VPN](https://developers.cloudflare.com/cloudflare-one/setup/replace-vpn/) 文档进行当前模式。

## 迁移评估提示

- 源覆盖范围：哪些产品在范围内、哪些导出可用，以及是否截图/文本摘要隐藏了缺失的对象文件。
- 规则数量和命中数据：按规则类型计数的数量、禁用/过时的规则、无命中规则、高命中规则和业务关键例外。
- 对象依赖项：地址对象、服务对象、组、自定义类别、网络服务、应用程序 ID、区域、标签、连接器和服务器组。
- 身份准备情况：IdP、SCIM/组同步、组名规范化、单个用户规则、本地组、服务帐户和承包商身份。
- TLS/DLP 准备情况：源解密规则、证书固定跳过、[DLP](https://developers.cloudflare.com/cloudflare-one/data-loss-prevention/) 引擎/配置文件、自定义正则表达式、精确匹配数据和有效负载日志记录预期。
- 连接性准备情况：源隧道/连接器、私有 DNS、[分割隧道](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/) 或跳过行为、源 IP 保留、[出口 IP](https://developers.cloudflare.com/cloudflare-one/traffic-policies/egress-policies/) 允许列表和站点到站点要求。
- 推广准备情况：试点小组/站点、并行运行期、回滚负责人、源堆栈退役标准以及监控/日志比较计划。

## 源特定陷阱

### Zscaler ZIA / SWG

- 自定义 URL 类别通常拆分为单独的 IP、域和 URL 列表。计算生成的列表，而不仅仅是源类别。
- ZIA 位置带有 IP 地址可用于源 IP 列表；它们不会自动成为 [网关 DNS 位置](https://developers.cloudflare.com/cloudflare-one/networks/resolvers-and-proxies/dns/locations/) 用于 DNS 策略作用域。
- GRE 隧道源 IP 可以提供策略条件，但传输迁移是单独的 WARP 连接器或 Cloudflare WAN 工作流。
- CAUTION/warn 行为没有精确的网关等效项。将其视为显式的客户决策，而不是静默的允许/阻止选择。
- DLP 引擎和自定义正则表达式通常需要手动重新创建 Cloudflare DLP 配置文件。占位符策略不得启用，好像 DLP 已完成。
- 网络应用程序组和不受支持的协议是部分映射。启用之前请审查它们。
- 如果 SCIM 不可用，身份范围的源规则变得过于广泛，除非您添加一个可执行的替代方案，例如用户/邮件列表。在创建这些规则之前检查 [网关身份选择器](https://developers.cloudflare.com/cloudflare-one/traffic-policies/identity-selectors/)。

### Zscaler ZPA / 私有访问

- ZPA 应用程序分段、服务器组和连接器组不 1:1 映射。Cloudflare 将 Access 应用程序、隧道路由、DNS 和策略分开。
- 通过 API 创建隧道不会完成连接器部署。单独计划 cloudflared 安装、身份验证和原始可达性。
- 每个ZPA连接器组创建一个 Cloudflare Tunnel，无论连接器运行状态如何（AUTHENTICATED、DISCONNECTED 或禁用）。状态是操作性的，而不是架构性的。在隧道描述中标记断开连接或传统的组，并在验证后让客户决定退役什么。
- 每个组内的 ZPA 连接器实例映射到一个针对该隧道令牌运行的 cloudflared 副本。将副本数量与每个组的连接器实例数量匹配以保留相同的拓扑。单个隧道令牌支持多个同时运行的 cloudflared 进程。建议在同一个数据中心的不同主机或子网上安装副本。
- 对于每个连接器组，识别所有与其链接的服务器组以及分配给这些服务器组的所有应用程序分段。这些应用程序分段中的 IP 地址和 CIDR 成为相应隧道的 CIDR 路由；域名成为同一隧道的主机名路由。优先选择每个子网一个 CIDR 路由，而不是每个主机 /32 路由，其中广泛的子网覆盖所有应用程序分段 IP。
- ZPA 跳过意味着 Cloudflare 中的分割隧道跳过，而不是 Access `跳过` 决策。跳过规则映射到 WARP [分割隧道](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/) 排除条目。这是一个需要手动配置的步骤，没有 API 自动化 - 客户必须通过仪表板将跳过的域名和 IP 添加到设备配置文件分割隧道排除列表中。
- 无代理/浏览器应用程序可能成为每个域的单独公共主机名 Access 应用程序。WARP 私有应用程序仍然是私有目标应用程序。
- 默认 Cloudflare Access 应用程序目标限制是每个应用程序 5 个主机名。对于具有大型应用程序分段的 ZPA 迁移，请在实施前联系 Cloudflare 账户团队请求增加（最多 50）。在创建应用程序之前确认帐户上存在此限制 - 如果没有，大型分段必须拆分为多个具有相同策略的应用程序，这将显著增加对象数量。
- IP 锚定的应用程序在迁移之前需要显式的出口决策：通过客户出口保留源 IP，使用 Cloudflare [专用出口](https://developers.cloudflare.com/cloudflare-one/traffic-policies/egress-policies/)（如果可用），或接受目标服务必须更新以允许新的源 IP。这是一个客户决策，如果未解决，将阻止实施。
- 解析器策略可以是帐户范围的。小心处理跨站点或虚拟网络的重叠私有 DNS 命名空间；在做出 DNS 变更之前检索 [解析器策略](https://developers.cloudflare.com/cloudflare-one/traffic-policies/resolver-policies/) 文档。
- 每个 ZPA 访问策略规则映射到 Cloudflare 可重用 Access 策略。在将它们附加到 Access 应用程序之前创建所有可重用策略。在默认拒绝的网关网络环境中，此外创建一个网络允许规则，选择器为“存在私有地址的自托管 Access 应用程序”（wirefilter: `any(access.private_app[*] in {"*"})`），其优先级高于任何广泛的 L4 阻止规则 - 如果没有，网关会在 Access 策略评估之前阻止私有应用程序流量。
- 在 ZIA 和 ZPA 组合迁移中，网关网络规则可能会意外阻止 Access 私有应用程序流量。上述网关网络允许规则是修复方法 - 将其置于比 ZIA 迁移的阻止规则更高的优先级（编号更低）。在启用广泛的 L4 阻止之前添加并验证此规则。

### Palo Alto / Prisma / NGFW

- 一个 Palo Alto 规则可以生成多个 Cloudflare 资源。保留规则意图，而不是规则数量。
- App-ID、URL 类别、区域、HIP、计划和解密行为很少精确翻译。标记部分映射，而不是强迫虚假等价。
- 带有规则的导出地址/服务对象和组。缺少对象导出会导致看似无声的丢失，除非明确检测到。
- 广泛的 `any` 目标/服务规则和非常广泛的 CIDR 需要手动审查。不要自动创建广泛的 catchall。
- HIP/设备检查需要在执行之前使用 Cloudflare [设备姿态](https://developers.cloudflare.com/cloudflare-one/reusable-components/posture-checks/) 集成。

## 注意事项

- 源导出通常将引用拆分到多个文件中。在声明规则无法映射之前，先解决 ID 对象、服务和组文件。
- 单个用户、本地组、部门和动态应用程序 ID 通常需要身份规范化。SCIM/组同步是组选择器的关键先决条件。
- Zscaler 谨慎/warn 行为、Palo Alto App-ID 行为和 TLS/解密例外可能没有精确的等效项。将它们标记为决策点，而不是强制 1:1 映射。
- 保留源规则顺序和命中次数（如果可用）。只有在获得用户批准的情况下才禁用或删除过时的/无命中规则。
- 除非明确请求并有时间限制，否则不要创建广泛的允许所有 catchall 以保留连接性。

## 验证门

- 在每个迁移阶段后，比较 Cloudflare 对象计数与解析的源计数。在出现不匹配时停止。
- 在启用策略之前，审查每个 `unsupported`、`partial`、`unmapped`、`needs_identity`、`needs_posture` 和 `manual_review` 项。
- 在 SCIM 同步和重新身份验证后，使用真实试点用户验证组匹配。
- 在启用 HTTP/DLP 阻止之前测试 TLS 检查和 Do Not Inspect 行为。
- 保持回滚路径明确：通过前缀禁用已迁移规则，恢复源路由，或回滚试点小组/站点。
- 在宣布完成之前，生成一个源规则会计表：已迁移对象、部分映射、未迁移原因、安全影响以及每个手动操作的负责人。

## 评估模板

```markdown
## 迁移评估

源堆栈：
审查的工件：
假设 / 缺失导出：
推荐的 Cloudflare One 目标：
映射摘要：
风险 / 部分映射：
未迁移：
试点计划：
验证：
回滚：
```
