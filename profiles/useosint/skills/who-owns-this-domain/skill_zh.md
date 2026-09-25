# 谁拥有这个域名

注册数据会告诉你谁购买了该名称；DNS会告诉你谁在运营该服务。它们通常是不同的当事人，将它们混淆是导致归属错误的错误。这里的一切都是被动的，除非有标记——但请注意，针对目标自己的名称服务器的`dig`会出现在目标的查询日志中，所以当你关心保持安静时，要通过公共递归解析器或被动DNS进行解析。

## 哪个来源优先

| 你持有 | 寻求 | 原因 |
|---|---|---|
| 域名，其他无 | RDAP，然后注册商WHOIS | 结构化，一次命中即可获得日期+注册商+状态 |
| 被编辑的WHOIS | 历史WHOIS + 被动DNS | 编辑不是跨存档的逆作用 |
| 你怀疑是众多域名之一的域名 | 域名服务器对+MX+反向WHOIS | 基础设施复用胜过联系隐私 |
| 一个IP | RIR的IP RDAP，然后是ASN查找 | 它告诉你网段所有者，而不是网站所有者 |
| 一个ccTLD | 注册商自己的WHOIS/网络服务 | ccTLD忽略gTLD政策；覆盖范围波动极大 |
| 一个全新的域名 | 创建日期+注册商+NS | 年龄加上批量友好的注册商是网络钓鱼的迹象 |

## WHOIS与RDAP

WHOIS是一个在TCP/43上的明文协议，没有模式。每个注册中心发出不同的字段布局，客户端不一致地遵循注册中心到注册商的引用，速率限制是沉默的——你会得到截断或被封锁，而不是可以解析的错误。

RDAP是HTTPS上的相同注册数据，以JSON格式，具有真实的HTTP语义：404表示没有此对象，429表示你被限流，并且每个对象都有域名、名称服务器、实体、IP和AS号码的端点。通过引导重定向器或直接通过注册中心查询它：

```bash
curl -s https://rdap.org/domain/example.com | jq .
curl -s https://rdap.org/ip/203.0.113.10 | jq '.name, .handle, .country'
curl -s https://rdap.org/autnum/64500 | jq '.name, .entities'
```

阅读这些字段：

- `events` — `registration`，`expiration`，`last changed`，`transfer`。注册后很长时间发生的`transfer`事件意味着当前注册商的记录从那里开始；任何更旧的记录只存在于历史WHOIS中。
- `entities[].roles` — `registrant`，`technical`，`abuse`，`registrar`。注册商实体在其`publicIds`中携带其IANA ID。
- `status` — EPP代码。`clientTransferProhibited`是常规的。`clientHold`意味着注册商从DNS中撤回了域名（非付款或滥用投诉）。`serverHold`意味着注册中心这样做——通常是法律或执法行动。`redemptionPeriod`和`pendingDelete`意味着它正在到期并且即将变为可用。
- `nameservers`和`secureDNS` — 运营商指纹加上DNSSEC立场。

一些服务器还返回一个机器可读的哪些字段被编辑的列表，这比从`REDACTED FOR PRIVACY`字符串猜测更有用。

对于`.com`和`.net`，注册中心很薄：它只返回注册商、日期、状态和名称服务器。联系块，如果有的话，来自注册商自己的服务器。当它们不一致时，查询两者——注册中心对日期和转让具有权威性，注册商对联系具有权威性。

## 编辑实际上移除了什么

根据当前的gTLD注册数据政策，注册人姓名、街道、电话和电子邮件通常被删除并用转发地址或网页表单替换。仍然存在并仍然起作用：记录的注册商和其IANA ID、当存在时，转售字段、创建/更新/到期/转让日期、名称服务器、DNSSEC状态、EPP状态代码、注册人州/省和国家（许多注册商保留这些）、注册人组织（一些注册商保留它用于法律实体，认为公司名称不是个人数据），以及注册商滥用联系人，它永远不会被编辑，并且是报告的正确途径。

区分**记录的注册商**（ICANN认证的方，例如Tucows、PDR、Namecheap）与实际出售域名的**转售商**，以及两者与**隐私服务**，隐私服务以自己的公司名称和管辖区出现在注册人字段下。隐私服务的身份本身就是一个线索：它告诉你你所在的注册商生态系统以及披露请求必须去哪里。

## DNS通行

```bash
dig +short example.com A; dig +short example.com NS
dig example.com MX +noall +answer
dig example.com SOA +noall +answer          # RNAME邮箱，序列通常是YYYYMMDDnn
dig example.com TXT +short                  # SPF和验证令牌
dig _dmarc.example.com TXT +short
dig google._domainkey.example.com TXT +short
dig example.com CAA +short
dig -x 203.0.113.10 +short
```

不要基于`ANY`构建工作流程——现在大多数权威服务器用最小或合成响应回答它，而不是完整的记录集。

每种记录类型泄漏不同的信息：解释表在[reference/dns-record-types.md](reference/dns-record-types.md)中，从SPF包含主机、DKIM选择器和TXT令牌到命名供应商的映射在[reference/vendor-fingerprints.md](reference/vendor-fingerprints.md)中。简而言之：TXT是组织SaaS资产的可公开查阅清单，MX命名邮件安全供应商，DMARC `rua`命名他们的DMARC报告供应商，CAA命名他们标准化的CA。

## IP、ASN和共享主机成本你什么

```bash
whois -h whois.cymru.com " -v 203.0.113.10"        # ASN，前缀，国家，AS名称
whois -h whois.radb.net -- '-i origin AS64500'     # 由该AS路由的前缀
```

RIR记录给出网段所有者。如果这是一个托管提供商或云区域，你什么也没学到关于所有权——共享IP将一个域名与数千个无关的租户关联起来，所以“相同IP”作为归属证据是无用的。当RIR记录显示重新分配或子分配给命名客户时，或者当块很小时且组织名称是目标时，它才成为证据。

PTR由控制IP的人设置，而不是域名所有者。云机械地从地址生成它们，这只能告诉你平台。托管和 企业块通常携带客户名称，并且遍历已知主机的/24的PTR可以给你整个机架的组织。

## 历史WHOIS和被动DNS

这就是真正的转折点所在。编辑是从某个时间点开始的，所以捕获记录的数据库在编辑之前仍然保留名称、电子邮件和电话号码；被动DNS保留每个观察到的答案，所以你得到IP和主机名，该区域不再提供服务。问三个问题：注册人字段在私有化之前说了什么，其他哪些域名共享该注册人电子邮件或名称（反向WHOIS），这个名称随时间解析到哪些IP。DomainTools、SecurityTrails、WhoisXML、Validin、Silent Push和VirusTotal的域名报告包含这两种情况的某种组合——大多数情况下，有用的深度被付费密钥封锁。

## 区域传输和区域遍历

`dig AXFR example.com @ns1.example.com`向名称服务器请求整个区域。它是一个交互式TCP请求到目标控制的设施，它被记录，并且它超出了被动工作的范围——只有在授权参与中，并且期望被拒绝。使用NSEC而不是NSEC3签名的区域同样可以遍历以枚举每个名称，并且NSEC3哈希可以在离线状态下破解；两者都需要直接查询权威服务器。将两者都视为主动的，并在需要保持被动时使用`find-hidden-subdomains`。

## 哪里会出错

- **注册人是占位符。** 批量注册商、转售商、隐私服务和公司注册商都将自己的详细信息写入联系字段。跨域名的匹配注册人字符串可能意味着一个所有者或一个转售商。
- **日期关于年龄撒谎。** 已过期并重新注册的域名在注册中心重置其创建日期，所以一个长的存档历史加上一个最近的创建日期意味着该名称通过掉落转让。
- **缓存和伪装的DNS。** 响应是TTL范围快照，并且提供者根据地理位置、解析器和通过您永远不会看到的分割视图提供不同的记录。一个解析器是一个视点。
- **SPF和TXT记录腐烂。** SPF中存在意味着“曾经配置过”，而不是“现在正在使用”；验证令牌几乎从未被清理。
- **MX和NS是外包的。** 它们识别供应商。它们只有在特定的分配名称服务器对或邮件租户标签跨多个域名时才成为所有权信号。
- **停放域名**显示注册商DNS和市集IP。没有所有者基础设施可以找到。**抢占者**将目标的SPF和MX全部复制以看起来合法，所以镜像记录不是关系。

## 置信评级

- **确认** — 注册中心或RIR直接声明它，并且它不是联系字段：创建日期、注册商、EPP状态、名称服务器、网段所有者。或者：一个未编辑的注册人由第二个独立来源（公司文件、历史快照、存档页面）证实。
- **可能** — 跨域名的独特共享指纹：相同的分配名称服务器对、相同的邮件租户标签、相同的DKIM密钥、相同的CAA `accounturi`、相同的不寻常TXT令牌。相同的运营商，可能相同的所有者。
- **未确认** — 共享主机上的共享IP、共享注册商、共享公共DNS提供者，或者一个可能是转售商的注册人字符串。此外，来自历史数据库的任何内容，您都没有看到原始记录。

始终记录查询时间戳和哪个服务器回答。没有检索时间的WHOIS记录不是证据。

## 工作示例

目标：`northwind-logistics.example`，由欺诈团队提及。

RDAP：创建于11个月前，注册商Namecheap，注册人被编辑但国家是`PA`，状态`clientTransferProhibited`，名称服务器是一对Cloudflare（`dana`，`rex`）。年轻、便宜、代理、起源隐藏。

DNS：根本没有MX，这完全否定了“他们从这个域名开票”的理论。TXT包含一个`google-site-verification`令牌和一个SPF记录，其唯一的包含是一个交易性电子邮件供应商。DMARC是`p=none`，没有`rua`，所以没有报告供应商可以转向。邮件方面是死胡同。

历史WHOIS是突破：一个在注册后两个月拍摄的快照，在隐私服务之前，包含一个Gmail地址和一个名称。对该地址进行反向WHOIS返回六个更多域名，其中四个共享相同的`dana`/`rex`对——Cloudflare按账户分配这对，所以这是一个运营商，而不是偶然。

评级：注册人身份**可能**（一个快照，由名称服务器集群证实，尚未由文件证实）。七域名集群**确认**为一个运营商。

## 转折点

| 新选择器 | 去往 |
|---|---|
| 子域名、共享证书上的兄弟 | `find-hidden-subdomains` |
| IP、网段、ASN | `find-exposed-servers` |
| 注册人电子邮件、邮件供应商、转发地址 | `what-an-email-reveals` |
| 注册人组织、隐私服务管辖区 | `who-really-owns-it`，`x-ray-a-company` |
| 从编辑前快照的注册人电话 | `whose-number-is-this` |
| 在恢复的IP和主机名上的历史内容 | `read-deleted-pages` |
| 在发现的主机名上的索引文件 | `google-like-a-spy` |
| 一组域名、IP和注册人以展示 | `graph-the-network` |

## 法律和ToS注意事项

批量WHOIS访问在合同上受到限制：注册中心和注册商禁止将其用于营销或用于构建可重新分配的数据库，并通过速率限制和封锁来执行。RDAP支持差异化访问，其中经过审核的认证请求者看到比匿名请求者更多——这种审核存在的确切原因就是防止个人数据被匿名批量收集。从历史数据库中提取的编辑前注册人数据在GDPR下仍然是个人数据：您需要一个合法依据，并且[../../ETHICS.md](../../ETHICS.md)中的最小化规则适用。未经书面授权的AXFR可能构成未经授权的访问。
