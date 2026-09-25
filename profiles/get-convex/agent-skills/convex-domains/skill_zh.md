<!-- GENERATED from convex-agents content/capabilities/domains.json — do not edit by hand. -->

# 使用自己的服务商设置自定义域名

引导用户自己的注册商将域名指向 Convex 应用：识别目标（托管或部署 URL），创建 DNS 记录，附加自定义域名，如果应用使用认证则重新绑定认证原点。

## 工作流程

1. 识别目标：发布站点的托管地址（用于 `*.convex.app` 静态托管）或部署的 HTTP 动作 URL。
2. 检测用户服务商的已认证的 DNS CLI，并提供自动创建记录的选项：Cloudflare → `flarectl dns create`（注意：`wrangler` 本身不管理 DNS 记录）或通过他们的令牌环境使用 CF API；Route53 → `aws route53 change-resource-record-sets`；Google Cloud DNS → `gcloud dns record-sets create`；DigitalOcean → `doctl compute domain records create`；Vercel DNS → `vercel dns add`。首先检查认证只读权限（`flarectl user info` / `aws sts get-caller-identity` / `doctl account get`）；显示确切命令并在运行前确认。
3. 如果没有认证的 CLI（或用户拒绝），告知用户在他们的注册商处创建的确切记录：CNAME（或在根域名处创建 A/ALIAS）以及 TXT 验证记录——使用具体的 host 和 value 字符串，而不是占位符。
4. 将域名作为 Convex 自定义域名附加（控制台或 CLI），并等待验证；注意 DNS 传播可能需要几分钟到几小时。使用 `dig +short` 验证记录是否生效。
5. 如果应用使用认证（passkeys/OAuth），将认证原点（SITE_URL / RP_ID / ORIGIN 环境变量）重新绑定到新域名，并重新部署/重新发布。
6. 验证：域名通过 HTTPS 提供应用，包括根域名 → www 重定向（如果配置了）。

## 规则

- 不要请求或处理注册商凭证。用户机器上已认证的 CLI 是可以的——凭证保留在工具中；不要安装 CLI 或运行其登录/认证流程，也不要输出令牌。
- 活域名上的 DNS 变更对用户可见：显示确切命令并在运行前确认；之后使用 dig 验证。
- 始终包含 TXT 验证记录，而不仅仅是 CNAME。
- 重新绑定域名会改变认证原点——之后重新发布，否则登录会中断。
