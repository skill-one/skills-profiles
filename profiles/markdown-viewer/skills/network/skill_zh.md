# 网络拓扑图生成器

**快速入门：** 选择拓扑类型 → 声明网络设备的模板图标 → 使用箭头语法连接 → 使用 `rectangle` 或 `package` 将设备分组 → 用 ` ```plantuml ` 分隔符包裹。

> ⚠️ **重要提示：** 始终使用 ` ```plantuml ` 或 ` ```puml ` 代码分隔符。绝对不要使用 ` ```text ` — 它将不会渲染为图形。

## 关键规则

- 每个图形以 `@startuml` 开头并以 `@enduml` 结尾
- 使用 `mxgraph.*` 模板语法表示网络设备图标（路由器、交换机、防火墙等）
- 默认颜色会自动应用 — 你不需要指定 `fillColor` 或 `strokeColor`
- 使用 `rectangle "区域" { ... }` 或 `package "区域" { ... }` 将设备分组到网络区域
- 使用 `cloud "名称" { ... }` 表示云/互联网形状
- 双向物理链路使用 `--`（无箭头）；有向流量使用 `-->`
- 虚线表示 VPN/无线/逻辑链路使用 `..` 或 `..>`
- 使用 `skinparam` 进行全局样式设置

**完整模板参考：** 请参阅 [stencils/README.md](../uml/stencils/README.md) 了解 9500+ 可用图标。

## Mxgraph 模板语法

```
mxgraph.<命名空间>.<图标> "标签" as <别名>
mxgraph.<命名空间>.<图标> "标签" as <别名> #颜色
mxgraph.<命名空间>.<图标> <别名>
```

### 常见网络模板系列

| 系列 | 前缀 | 典型图标 |
|------|------|----------|
| 网络 | `mxgraph.networks.*` | `switch`, `router`, `firewall`, `server`, `pc`, `laptop`, `wireless_hub`, `cloud` |
| Cisco | `mxgraph.cisco.*` | `routers.router`, `switches.layer_3_switch`, `security.firewall`, `servers.fileserver` |
| Cisco 19 | `mxgraph.cisco19.*` | `nexus_9300`, `nexus_5k`, `fabric_interconnect`, `ucs_5108_blade_chassis`, `storage` |
| Cisco SAFE | `mxgraph.cisco_safe.security_icons.*` | `ngfw`, `waf`, `ids`, `siem`, `nac`, `vpn`, `ddos`, `malware_sandbox` |
| Citrix | `mxgraph.citrix2.*` | `netscaler_gateway`, `storefront`, `delivery_controller`, `vda` |

### 连接类型

| 语法 | 含义 | 用例 |
|------|------|------|
| `A -- B` | 实线，无箭头 | 物理以太网 / LAN 链路 |
| `A --> B` | 实线带箭头 | 有向流量 |
| `A .. B` | 虚线，无箭头 | VPN 隧道 / 无线链路 |
| `A ..> B` | 虚线带箭头 | 有向 VPN / 逻辑流量 |
| `A -- B : "标签"` | 带标签的连接 | 链路描述 |

### 快速示例

```plantuml
@startuml
mxgraph.networks.cloud "Internet" as inet
mxgraph.networks.firewall "防火墙" as fw
mxgraph.networks.router "路由器" as rtr
mxgraph.networks.switch "交换机" as sw

rectangle "办公网络" {
  mxgraph.networks.pc "PC 1" as pc1
  mxgraph.networks.pc "PC 2" as pc2
  mxgraph.networks.server "服务器" as srv
}

inet -- fw
fw -- rtr
rtr -- sw
sw -- pc1
sw -- pc2
sw -- srv
@enduml
```

## 网络图形类型

| 类型 | 目的 | 关键模板 | 示例 |
|------|------|----------|------|
| LAN | 局域网拓扑 | `mxgraph.networks.*` | [lan-topology.md](examples/lan-topology.md) |
| WAN | 广域网 | `mxgraph.cisco.*` | [wan-topology.md](examples/wan-topology.md) |
| 企业 | 企业基础设施 | `mxgraph.cisco.*` | [enterprise-network.md](examples/enterprise-network.md) |
| Cisco | Cisco 特定图标 | `mxgraph.cisco.*` | [cisco-network.md](examples/cisco-network.md) |
| 无线 | WiFi 网络 | `mxgraph.networks.*` | [wireless-network.md](examples/wireless-network.md) |
| 云混合 | 本地 + 云 | `mxgraph.cisco.*` | [hybrid-cloud.md](examples/hybrid-cloud.md) |
| Citrix | 虚拟应用/桌面 | `mxgraph.citrix2.*` | [citrix-network.md](examples/citrix-network.md) |
| 安全 | 深度防御 | `mxgraph.cisco_safe.security_icons.*` | [security-architecture.md](examples/security-architecture.md) |
| 数据中心 | Spine-Leaf / UCS / SAN | `mxgraph.cisco19.*` | [datacenter-network.md](examples/datacenter-network.md) |
