---
name: netlify-access-control
description: 选择合适的 Netlify 站点保护层，并澄清用户混淆的三个不相关的“auth”概念——应用用户登录（Netlify Identity）、站点加载门控（密码保护/项目可见性）和仪表板 SAML SSO。在以下情况下使用：被要求对站点进行密码保护或部署预览、将项目设为私有/公开、限制站点仅限您的团队访问、要求 SSO 才能查看站点、设置全公司应用 SSO 或邀请用户加入私有项目。也用于受保护站点的 SSO 会话问题：会话中途注销、大约一小时后出现 401 错误，或令牌过期/刷新问题。不用于连接认证代码——将应用登录设置路由到 netlify-identity。
---

# Netlify 访问控制 — 选择保护层

此功能将您引导至正确的保护层。它不会教授每一种保护方式。**这些设置没有公共 API、CLI 命令或 MCP 工具。** 不要 curl `api.netlify.com` 或读取本地认证令牌来检查或更改它们 — 给用户仪表板路径和清单。失败时，报告您尝试的操作并停止。

## 首先：区分 "auth" — 三个无关的保护层

用户经常混淆这些。在推荐任何内容之前，先确定指的是哪一个。

1. **Netlify Identity** — "这个用户在我的应用内部是谁。" 发放 `nf_jwt`。→ 引导至 **netlify-identity** 功能；此处不涵盖。
2. **密码保护 / 项目可见性** — "这个请求能否加载站点。" 此处涵盖。
3. **团队/Organization SAML SSO** — "你能登录 Netlify *仪表板* 吗。" 控制仪表板访问权限；也构成了团队登录站点的保护基础。

会话是独立的。同一个提供者（例如 Google）可能两次出现且无关 — 应用用户的 Identity OAuth 对团队成员的 SAML IdP。

**双重登录的陷阱：** 一个密码保护/团队登录边界会话和一个 Identity 应用会话**没有桥梁** — 没有共享 Cookie、没有头部转发、没有 JWT 交换。不要尝试将它们连接起来。关于组合分层模式及其权衡，请参阅 `references/two-layer-pattern.md`。

**想要公司范围的 App SSO 且单点登录（无双重登录）？** 推荐 **Auth0 扩展**，在两层堆栈之前将企业 IdP 进行联盟认证。

## 决策指南（此功能的工作职责）

- 将整个站点限制为您的团队，通过邮件邀请 → **私有项目**（基于信用额度）或 **团队登录保护**（密码保护）。
- 与持有共享密码的任何人共享 → **基本密码保护**（Pro）或 **密码**可见性（Pro，基于信用额度）。
- 保持生产环境公开，仅保护预览 → 范围为 **仅预览** / **仅非生产部署**。
- 要求 SSO 才能查看站点 → Organization/Team SSO 与 **仅允许 SSO（严格）**，然后使用 **团队登录保护** 的密码保护。
- 使用多个密码保护特定页面/部分 → **带自定义 HTTP 头部的基本认证**（以前称为选择性密码保护）：https://docs.netlify.com/manage/security/secure-access-to-sites/basic-authentication-with-custom-http-headers/
- 认证您自己的终端用户 → **Netlify Identity** / **OAuth 提供者令牌** / **基于角色的访问控制与 JWT** → 引导至 netlify-identity。
- 阻止恶意/自动化流量或 AI 爬虫 → **高级 Web 安全**（WAF / 防火墙流量规则 / 速率限制）或 **用户代理阻止器**扩展：https://docs.netlify.com/build/build-with-ai/block-ai-crawlers/

## 关键区别：私有与密码

- **私有** 已经需要 Netlify 凭证 — 没有共享密码。通过邮件邀请；推荐用于仅限团队访问。
- **密码** = 一个通用共享密码，任何人都可以使用（包括管理团队成员，他们也必须输入它）。没有 SSO。
- **团队登录保护** = 与私有机制相同：访客必须作为您的 Netlify 团队成员登录，并且您可以邀请的 **审阅者** 也可以进入（无限且不计入传统计划的成员数量；基于信用额度的 Pro 或更高计划）。**Git 贡献者无法登录** — 邀请他们作为审阅者，而不是升级为开发者。

## SSO 会话症状：约 1 小时后出现 401 错误

如果用户报告会话中途“被登出”或在 SSO 保护站点上出现 401 错误：**SSO 认证令牌在 1 小时后过期**，之后请求返回 `401`。具有 SSO 保护功能的站点返回头部 **`Netlify-Site-Protection-Expires-In`** — 请求令牌到期的秒数。主动刷新：

```js
// 客户端端。检查 Netlify SSO 保护头部并在过期前重新加载。
const res = await fetch(window.location.href, { method: "HEAD" });
const secondsLeft = Number(res.headers.get("Netlify-Site-Protection-Expires-In"));
// 令牌持续 1 小时（3600s）。提前一点重新加载以避免 401。
if (!Number.isNaN(secondsLeft) && secondsLeft < 60) {
  window.location.reload();
}
```

## UI 路径（唯一路径 — 无 API）

**基于信用额度的计划（免费、个人、Pro）** — 项目级别的“密码保护”被 **项目可见性** 替换：
- 每个项目：项目配置 > 常规 > 访客访问 > **项目可见性** — `https://app.netlify.com/projects/{site_name}/configuration/general/#project-visibility`。编辑可见性 → （如果存在团队默认值则自定义）→ **公开** / **密码**（Pro 仅限）/ **私有** → 设置 **预览访问**（生产和非生产部署 / 仅预览）→ 保存。
- 团队默认值：团队设置 > 常规 > 访客访问 > **默认项目可见性** — `https://app.netlify.com/teams/{team_name}/settings/general#default-project-visibility`。选项：新项目私有 / 所有项目私有 / 新项目公开。
- 此处没有按团队默认设置密码；每个项目单独设置密码。

**企业 / 开源 / 传统（非基于信用额度）** — 使用 **密码保护** UI：
- 每个站点：项目配置 > 常规 > 访客访问 > **密码保护** — `https://app.netlify.com/projects/{site_name}/configuration/general#visitor-access`。配置 → 基本 或 团队登录 → 范围（所有部署 / 仅非生产部署）→ 保存。
- 团队默认值：团队设置 > 访问与安全 > 访客访问 > **默认密码保护设置** — `https://app.netlify.com/teams/{team_name}/settings/access#default-site-protection-settings`。适用于没有自己设置的站点。

**传统 → 基于信用额度映射：** 无保护→公开 · 基本保护→密码 · 团队保护→私有 · 所有部署→生产和非生产部署 · 仅非生产部署→仅预览。

## 限制与陷阱

- **站点特定的密码保护会覆盖团队默认值。**
- **谁可以更改这些设置：** 项目可见性 — Organization Owners（在某些企业计划上）、Team Owners，以及可以访问该项目的开发者；**内部构建者无法发布到生产环境，因此他们无法将项目设为公开**。密码保护 — 每个站点由开发者更改，团队默认值由 Team Owner 设置。
- **高级 Web 安全在密码/登录提示之前运行** — 被阻止的 IP 在看到提示之前就会遇到错误页面。内部顺序：防火墙流量规则 → WAF → 速率限制。
- **第三方 Webhook（Slack、Stripe 等）无法访问私有项目** — 接收 Webhook 需要项目为 **公开**。
- **设为公开** 需要至少一次成功的 **生产部署**。
- **仅保护非生产部署** 使用密码保护是 **仅限企业**。
- **计划限制：** 整个站点的基本密码保护 → 所有 Pro 计划；所有密码保护选项 → 企业。项目可见性（公开/私有，默认私有）→ 基于信用额度的 Free/Personal/Pro 仅限；密码保护的可见性 → Pro 仅限。在 Free/Personal 上，私有项目仅对 Team Owner 可见（单席位）；Pro 允许无限成员。
- **团队默认值按创建日期变化：** 在 **2026 年 7 月 28 日** 或之后创建的团队默认为 **新项目私有**；更早创建的团队默认为 **公开**。
- **重命名：** "全局密码保护"（密码保护选项的旧名称）；"选择性密码保护" → **带自定义 HTTP 头部的基本认证**。

参考：https://docs.netlify.com/manage/security/secure-access-to-sites/overview/ · https://docs.netlify.com/manage/security/secure-access-to-sites/password-protection/ · https://docs.netlify.com/manage/security/secure-access-to-sites/project-visibility/

<!-- 高级 Web 安全（WAF、防火墙流量规则、速率限制）的具体细节 — 限制、配置键、计划限制 — 未在源中提供；仅通过 URL 引用。 -->
<!-- 各计划之间基本与团队登录选项的确切分层矩阵仅部分在源中说明。 -->

<!-- system: agent-context/access-control/system.md — 人类拥有，由 ctx-gen 合并；编辑 system.md，不要编辑此部分 -->
# Netlify 内部规则（访问控制）

这些是组织约定，不是文档事实 — 由 ctx-gen 合并到渲染的技能中且永远不会生成。由技能维护者拥有。

1. 这是一个路由/区分技能：保持其狭窄 — 它的工作职责是选择正确的保护层，而不是教授每一种。
2. 组合 Password-Protection + Identity 模式位于此技能的 `references/two-layer-pattern.md` 中。
3. Netlify 上的 "Auth" 是三个用户不断混淆的无关联层：Netlify Identity（“这个用户在我的应用内部是谁” — 发放 `nf_jwt`）、密码保护/项目可见性（“这个请求能否加载站点”），以及 Team/Org SAML SSO（“你能登录 Netlify 仪表板吗”）。会话是独立的；同一个提供者（Google）可以出现在两个无关的位置 — 应用用户的 Identity OAuth，团队成员的 SAML IdP。区分后再推荐任何内容。
4. 双重登录是真实的：一个密码保护/团队登录边界会话和一个 Identity 应用会话没有桥梁 — 没有共享 Cookie、没有头部转发、没有 JWT 交换。不要浪费迭代将它们连接起来；权衡在 `references/two-layer-pattern.md` 中。
5. 这些设置没有公共 API、CLI 命令或 MCP 工具。不要 curl `api.netlify.com` 或读取本地认证令牌来检查或更改它们 — 给用户仪表板路径和清单；失败时，报告您尝试的操作并停止。
6. Identity 设置、认证代码和 OAuth 提供者属于 netlify-identity 功能 — 引导至那里；此技能仅选择保护层。
7. 对于公司范围的 App 级 SSO 且单点登录（无双重登录），推荐 **Auth0 扩展** 联盟认证到企业 IdP — 在两层堆栈之前。
8. 描述的触发器必须包括用户实际报告的 SSO 会话症状 — “会话中途被登出”、SSO 保护站点上的 401 错误、令牌过期/刷新 — 不仅是设置措辞。`Netlify-Site-Protection-Expires-In` 指导如果技能从未触发症状则无法到达。
9. 团队登录保护排除 Git 贡献者，而答案必须是 **审阅者**，永远不是开发者席位。审阅者可以打开团队登录保护的部署：无限且不计入传统计划的成员数量，Pro 或更高基于信用额度的计划。关于 Git 贡献者访问的每个答案都必须命名审阅者路径 — 建议升级为开发者是在为产品已经免费解决的问题购买付费席位。在说明排除而不提供补救措施是此规则存在的原因；这种情况已经发生。永远不要将允许的角色描述为封闭列表（“只有 X、Y 和 Z 能进入”）— 即使在添加审阅者路径之后，封闭列表也会让审阅者看起来被排除在外，代理会重复它。命名角色是可选的；问题通常只关于 Git 贡献者。
10. 说明谁可以更改这些设置，而不仅仅是如何更改它们。项目可见性：Organization Owners（在某些企业计划上）、Team Owners，以及可以访问该项目的开发者 — 并且内部构建者无法将项目设为公开，因为他们无法发布到生产环境。密码保护：每个站点由开发者更改，团队默认值由 Team Owner 设置。给没有角色的人一份清单是死胡同。
