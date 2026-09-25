# 查找暴露的服务

互联网范围内的扫描器已经扫描了你的目标。查询他们的结果是被动的——你永远不会向目标发送数据包，所以他们的日志中不会出现任何内容，也没有任何内容可以归因于你。代价是每个结果都是一个关于过去某个时刻的断言，初学者的错误是读取横幅作为活动主机的当前状态。

## 首先从哪个平台开始

| 你持有 | 寻求 | 原因 |
|---|---|---|
| 一个 IP | Shodan 主机查询，或免费的 InternetDB 端点 | 一个请求提供端口、主机名和 CPE |
| 一个网段或 ASN | Shodan `net:`/`asn:` 带端口细分 | 显示你在查看单个主机之前资产的结构 |
| CDN 背后的主机名 | Censys 证书到主机的连接 | Censys 将证书链接到观察到的主机，这就是你找到源头的方式 |
| 证书或一个独特的页面 | Favicon 哈希和证书主题/序列搜索 | 找到 DNS 从未链接的兄弟基础设施 |
| 一个组织名称 | Shodan 上的 `org:`，Censys 上的 `autonomous_system` | 两者都是通过网络注册进行归因，因此两者都会继承其错误 |
| 覆盖范围怀疑 | 第二个具有不同传感器的平台 | 这些平台不断意见不一致；分歧是信号 |

Shodan 具有最广泛的设备和协议覆盖范围，以及最友好的查询语言。Censys 具有更结构化的主机记录、更好的证书连接和更严格的查询语法。FOFA、ZoomEye、Netlas、Onyphe、BinaryEdge 和 LeakIX 看到互联网的不同切片，当前两者为空时值得尝试——特别是非西方扫描器会索引前两者遗漏的主机。

## Shodan

```bash
shodan init <api-key>
shodan host 203.0.113.10                                 # 关于一个 IP 的所有已知信息
shodan search --fields ip_str,port,org,hostnames 'ssl.cert.subject.CN:example.com'
shodan count 'net:203.0.113.0/24'                        # 廉价：无结果积分
shodan stats --facets port,org 'net:203.0.113.0/24'      # 网段的结构
shodan download results.json.gz 'asn:AS64500 port:3389'
shodan parse --fields ip_str,port,product results.json.gz
```

免费且未经身份验证，针对单个 IP：

```bash
curl -s https://internetdb.shodan.io/203.0.113.10 | jq .   # 端口、主机名、cpes、漏洞
```

值得知道的过滤器：`net:`，`port:`，`hostname:`，`asn:`，`org:`，`isp:`，
`country:`，`city:`，`product:`，`version:`，`os:`，`http.title:`，`http.html:`,
`http.status:`，`http.favicon.hash:`，`ssl.cert.subject.CN:`,
`ssl.cert.issuer.CN:`，`ssl.cert.expired:`，`ssl.jarm:`，`ssl:`，`tag:`，`vuln:`,
`has_screenshot:`，以及 `before:`/`after:` 用于扫描日期。`vuln:` 和一些其他过滤器需要付费等级。

Censys 使用结构化字段路径语法而不是主机文档——`services.port`，`services.service_name`，`services.http.response.html_title`，
`services.tls.certificates.leaf_data.subject_dn`，`dns.names`，
`autonomous_system.asn`，`location.country`——结合 `and`/`or`/`not`。其 API v2 暴露 `https://search.censys.io/api/v2/hosts/search?q=…` 和
`https://search.censys.io/api/v2/hosts/{ip}`，使用 API-ID/secret 基本身份验证。

跨平台的查询等效项在
[reference/query-cookbook.md](reference/query-cookbook.md)。

## 读取返回的内容

一个结果是横幅加上元数据，而不是一个裁决。对特定服务横幅的解读——版本字符串的含义，哪些字段是自我报告的，哪些是观察到的——在
[reference/banner-interpretation.md](reference/banner-interpretation.md)。一般原则：

- **检查每条记录的扫描时间戳。** Shodan 记录带有时间戳；Censys 带有最后观察时间。重新扫描的频率因端口和地址空间而异，因此记录可能几天或几个月旧。报告发现时作为“在 <日期> 观察到”，而不是“是”。
- **区分观察到的和声称的。** 打开端口和 TLS 证书是观察到的事实。产品名称和版本是从主机选择发送的横幅中解析的，主机会撒谎——故意地，或者因为发行版回滚了补丁而没有更改版本字符串。
- **CVE 标签是推断。** 它们来自将版本字符串与漏洞数据库进行匹配。它们是报告的线索，永远不会确认可利用性，并且回滚的补丁通常会使它们在两个方向上都出错。
- **记录中的主机名来自反向 DNS 和证书**，这意味着它们可以属于 IP 的前一个租户。

## 重要的转换点

这是使扫描平台不仅仅是端口列表的原因。

**Favicon 哈希。** Shodan 索引网站 favicons 的哈希（网站的 favicons 的 MurmurHash3，base64 编码的图标字节的 MurmurHash3；FOFA 的 `icon_hash` 使用相同的构造）。因为 favicons 通常与应用程序一起发送，而不是每个主机配置，所以搜索哈希可以找到运行相同设备、框架或目标自己的品牌门户的每个主机——跨不相关的 IPs、ASN 和域名。它是找到组织分散的同一产品的最佳方式。

**TLS 证书。** 在证书的 CN、其主题组织或其序列号上搜索，你会找到每个提供该证书的主机。证书序列对每个发行商是唯一的，所以序列匹配是近乎精确的身份。Shodan 还暴露了一个证书指纹过滤器；检查其文档以了解它期望的哈希，而不是猜测。与 `find-hidden-subdomains` 结合——CT 给你证书，扫描数据给你提供它的每个主机。

**JARM 和 TLS 堆栈指纹。** JARM 哈希服务器对一组 TLS 握手如何响应，所以它指纹化 TLS 堆栈而不是证书。它集群设备、负载均衡器和命令与控制框架。它不是组织特有的，所以将其视为缩小搜索范围的过滤器，而不是标识符。

**响应体指纹。** 目标页面上的唯一字符串——跟踪 ID、不寻常的版权行、自定义标题、构建哈希——通过 `http.html:` 搜索找到其他提供相同应用程序的主机，包括暂存副本和 CDN 背后的源头。

## 查找 CDN 背后的源头

当主机名解析到 Cloudflare 或其他代理时，源头仍然存在，并且通常可以通过 IP 访问。被动路由到它，按可靠性顺序：

1. 在 CDN 的 ASN **之外** 的 IP 上搜索扫描数据中目标的 TLS 证书。源头通常直接提供真实证书。
2. 搜索唯一的 HTTP 体字符串或 favicons 哈希，并过滤掉 CDN ASN。
3. 读取 CDN 采纳之前的歷史 DNS（`who-owns-this-domain`）。源头移动的频率比人们想象的要低。
4. 检查设计上绕过代理的服务：MX 主机、`ftp`、`cpanel`、`direct`、`origin`，以及同一网段的非 HTTP 端口。
5. 读取 SPF `ip4:` 机制——组织授权自己的发送主机，这有时是网络源头。

一个候选源头是一个假设。通过发送带有目标 `Host` 头部的请求来确认它是针对目标的主动步骤：它需要授权。请注意，一个正确配置的源头会拒绝非 CDN 流量，所以无法确认并不意味着排除候选者。

## 哪里会出错

- **陈旧性影响双向。** 一个关闭的端口可能在扫描时是打开的；一个打开的端口可能自扫描以来已关闭。没有结果并不意味着没有服务——扫描器不会覆盖每个地址上的每个端口。
- **蜜罐污染一切。** 故意暴露的诱饵会膨胀有趣服务的搜索结果。迹象：一个主机上不合理的服務组合，大量打开的端口，许多不相关产品的默认横幅，以及位于研究导向的网段。Shodan 在 `https://api.shodan.io/labs/honeyscore/{ip}?key=` 暴露一个蜜罐评分估计——将其视为一个提示，而不是一个裁决。
- **目标可以操纵扫描器。** 扫描器源地址是可发布的，所以一个防御者可以向它们专门提供伪造的横幅。高价值目标有时会这样做。
- **`org:` 和 `isp:` 是网络注册，不是所有权。** 在云网段上它们命名云提供者，在转售空间上它们命名转售商。仅通过 `org:` 归因是人们最终报告邻居的暴露数据库作为目标的原因。
- **共享主机和共享 IP。** 一个 IP 可以服务数百个不相关的主机。在那里找到的端口和漏洞属于主机，不一定属于你的目标。
- **屏幕截图和横幅包含个人数据。** 暴露的仪表板和摄像头索引真实的人。当你保存它时，这是一个数据保护问题。
- **平台意见不一致，并且每个免费等级都会截断。** 一个单平台搜索如果找不到任何东西，意味着一个传感器网络什么都没看到。

## 置信度分级

- **确认暴露**——同一个服务在同一个 IP 和端口上出现在两个独立的扫描平台中，或者在同一个平台上的多个扫描日期中，并且 IP 通过目标明确控制的证书或通过名称重新分配给目标的网段与目标关联。
- **可能**——在与目标通过 favicons 哈希、体字符串匹配或反向 DNS 关联的 IP 上进行单个最近的观察。或者跨平台的匹配在您尚未独立确认所有权 IP 上。
- **未确认**——仅基于 `org:`/`isp:`，共享主机 IP，单个陈旧记录，没有其他证据的 CVE 标签，或具有蜜罐特征的主机。

永远不要通过连接到服务来升级等级。记录平台、查询、扫描时间戳和记录标识符以供每个发现。

## 实例分析

目标：`example-fintech.test`，授权外部攻击表面审查，仅被动收集。

 apex 解析到 Cloudflare，所以扫描解析的 IP 只会描述 Cloudflare。相反，从 `find-hidden-subdomains` 中获取证书主题 CN 并在扫描数据中搜索提供它的主机。三个命中：两个 Cloudflare 地址，和一个在欧洲主机提供商的 ASN 中带有 443 和 22 打开的地址。第三个主机是可能的源头。

它的 favicons 哈希反向搜索返回六个更多主机。四个是目标的区域门户。两个是无关公司——favicon 是随框架一起发送的股票图标，而不是目标自己的。这是一个死胡同，也是教训：在将哈希匹配视为归因之前，检查 favicons 是否实际上独特。

`net:` 在源头的 /29 上显示第二个主机带有 3306 打开和 MySQL 横幅，扫描了四个月前。旧，所以它可能已经消失了，但它可以报告为观察到。网段的 RIR 记录显示重新分配给目标的法定名称，这就是将“具有正确证书的 IP”转换为归因的原因。

停止那里。不要连接到 3306，不要向源头发送 `Host` 头部。报告两者，附上日期和查询，并将重新分配的网段交还给 `who-owns-this-domain`。

## 转换点

| 新选择器 | 前往 |
|---|---|
| 发现主机上的证书主题和 SANs | `find-hidden-subdomains` |
| 网段、ASN、反向 DNS 主机名 | `who-owns-this-domain` |
| 从证书主题和 RIR 记录中的组织名称 | `x-ray-a-company`，`who-really-owns-it` |
| 暴露的存储库、CI 或注册表服务 | `secrets-in-git-history` |
| 发现主机上的歷史内容 | `read-deleted-pages` |
| 发现服务上的索引路径 | `google-like-a-spy` |
| 要布局的主机/证书/ASN 集群 | `graph-the-network` |

## 法律和 ToS 注意事项

查询扫描平台是合法的被动研究。采取行动是关键：连接到暴露的数据库、打开管理面板、查看暴露的摄像头馈送或从打开的共享中获取文件可能构成大多数司法管辖区计算机滥用法下的未经授权访问，并且没有密码不是一种辩护。一个发现授权你**报告**——向网段的 RIR 记录的滥用联系人或相关 CERT——并且无他物。扫描平台的条款也限制了他们数据的重新分发，所以请在报告中引用发现，而不是重新发布数据集。包含个人数据的屏幕截图和横幅受 [../../ETHICS.md](../../ETHICS.md) 中的最小化规则约束。
