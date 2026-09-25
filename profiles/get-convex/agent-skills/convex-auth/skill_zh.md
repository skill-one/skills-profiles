<!-- GENERATED from convex-agents content/capabilities/auth.json — do not edit by hand. -->

# 为应用添加登录功能

为当前应用安装并配置 @convex-dev/auth：一个提供者（默认为 Passkeys，或 OAuth/密码）、服务器配置、客户端钩子以及登录界面——正确配置，包括 auth.config.ts（这是最常见的真实世界认证陷阱）。

## 工作流程

1.  安装 @convex-dev/auth（固定版本）并将其添加到 convex.config.ts。使用 pnpm 时，还需要 `pnpm add jose`（否则不会提升），用于步骤 3。
2.  在 convex/auth.ts 中添加提供者（默认为 Passkey；按需使用密码或 OAuth，如 Google）。
3.  无交互地生成认证密钥。**不要**运行交互式 `npx @convex-dev/auth` 向导：它需要登录/TTY，并在非交互式、匿名或 CI 运行中挂起（认证耗时的主要原因）。使用 `jose` 以确定性方式生成 JWT_PRIVATE_KEY + JWKS：
   ```bash
   node -e 'import("jose").then(async({generateKeyPair,exportPKCS8,exportJWK})=>{const k=await generateKeyPair("RS256",{extractable:true});const priv=await exportPKCS8(k.privateKey);const pub=await exportJWK(k.publicKey);process.stdout.write(JSON.stringify({JWT_PRIVATE_KEY:priv.trimEnd().replace(/\n/g," "),JWKS:JSON.stringify({keys:[{use:"sig",...pub}]})}))})' > .auth-keys.json
   ```
   然后，在部署时设置 JWT_PRIVATE_KEY 和 JWKS（来自 .auth-keys.json）以及 SITE_URL。推荐使用 Convex MCP 的 `envSet` 工具，每个变量调用一次，以避免对多行密钥进行 shell 引用。CLI 降级方案：使用 NAME=VALUE 形式 (`npx convex env set "JWT_PRIVATE_KEY=$JWT"`), **绝对不要** `env set JWT_PRIVATE_KEY "$JWT"`（值以 `-----BEGIN` 开头，CLI 将 `-` 解析为未知标志）。SITE_URL 是开发 URL（例如 http://localhost:3000）。部署后删除 .auth-keys.json。
4.  编写 convex/auth.config.ts（如果配置错误，这里会存在静默始终未登录的 Bug）。
5.  配置客户端：ConvexAuthProvider、登录组件和路由守卫。如果你导入 shadcn/ui 基础组件（按钮、输入框、文本区域、标签等），请先用 `npx shadcn@latest add <name>` 添加它们；缺少 @/components/ui/* 会导致构建失败。
6.  在宣布完成前，验证一次完整的登录流程。

## 规则

-  使用 `jose` 生成 JWT_PRIVATE_KEY/JWKS（可提取的 RS256；PKCS8 中的换行符替换为空格；JWKS = {keys:[{use:"sig", ...publicJwk}]}）。**不要**运行交互式 `npx @convex-dev/auth` 向导：它在无交互/匿名模式下挂起。通过 Convex MCP 的 `envSet` 工具或 NAME=VALUE CLI 形式设置变量。
-  始终编写 auth.config.ts：缺少/错误的配置会导致应用静默始终未登录且无错误提示。
-  默认使用 Passkeys；只有在明确请求时才切换到密码/OAuth。
-  在导入任何 shadcn/ui 基础组件前添加它们 (`npx shadcn@latest add ...`)；缺少 @/components/ui/* 会导致构建失败。
-  在完成前验证一次真实的登录是否正常工作。
