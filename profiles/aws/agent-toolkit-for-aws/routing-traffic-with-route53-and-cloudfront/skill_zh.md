# 使用 Route 53 和 CloudFront 路由流量

## 概述

关于配置 Amazon Route 53 以使用自定义域名将流量路由到 Amazon CloudFront 分发的域名专业知识。涵盖托管区域管理、别名 A/AAAA 记录、备用域名（CNAME）配置以及 ACM 证书设置以用于 HTTPS。

## 配置 Route 53 以将流量路由到 CloudFront 分发

要使用 Route 53 DNS 为 CloudFront 分发设置自定义域名，请严格按照以下步骤操作。
参见 [Route 53 CloudFront 路由步骤](references/route53-cloudfront-routing.md)。

该步骤涵盖：

- 验证 CloudFront 分发状态和 CNAME 配置
- 请求并验证 ACM 证书（必须位于 us-east-1）
- 创建或定位公共托管区域
- 创建指向 CloudFront 的别名 A 和 AAAA 记录
- 监控 DNS 传播

## 故障排除

### 域名不在 CloudFront CNAME 中

在创建 Route 53 记录之前，请在 CloudFront 分发配置中将域名添加为备用域名。

### SSL 证书问题

CloudFront 的 ACM 证书必须位于 us-east-1。确保证书已验证并关联到分发。

### 私有托管区域

CloudFront 仅与公共托管区域配合使用。如果仅存在私有区域，请创建公共托管区域。

### DNS 传播延迟

更改通常在 60 秒内传播，但完全的全球传播可能需要长达 48 小时。使用 `nslookup` 或 `dig` 进行验证。
