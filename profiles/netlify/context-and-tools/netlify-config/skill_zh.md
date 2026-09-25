# Netlify 配置

配置文件位于仓库的**根目录**（对于单仓库项目，位于基础/包目录）：
- `netlify.toml` — 构建配置、上下文、插件、函数、重定向、头部、开发环境。
- `_redirects` — 纯文本重定向/重写规则，保存到**发布目录**，无扩展名。
- `_headers` — 纯文本响应头部，保存到**发布目录**。

当 `netlify.toml` 中的值与 Netlify UI 冲突时，**优先使用 `netlify.toml` 中的值**。`netlify.toml` 中的路径相对于**基础目录**（默认为根 `/`）是绝对路径。

## 现代语法与旧语法的选择
- 函数打包器：使用 `node_bundler = "esbuild"`。`zisi` 是旧版 JS 默认；TypeScript 总是使用 `esbuild`。
- 临时重定向：使用 `status = 302`。`307` 是**不支持的**。
- Gatsby 图片 CDN：使用 `NETLIFY_IMAGE_CDN`，而不是已弃用的 `GATSBY_CLOUD_IMAGE_CDN`。
- 将环境值注入 TOML：`key = "$VAR"` 是**不支持的**（代理重定向中的 `signed` 除外）。使用构建命令 `sed` 替换或构建插件（见下文）。

## `netlify.toml` 构建与上下文

```toml
[build]
  base = "frontend"
  publish = "dist"
  command = "npm run build"
  environment = { NODE_VERSION = "18" }

[context.production]
  publish = "output/"
  command = "make publish"

[context.deploy-preview]
  publish = "dist/"

[context."feat/branch"]        # 使用引号包含特殊字符的名称
  command = "npm run preview"
```

`[build]` 在 **Bash** 中运行。上下文感知键包括 `[build]` 和 `[[plugins]]` — 但**不包括** `[[redirects]]` 或 `[[headers]]`（这些始终是全局的）。优先级，从最不具体到最具体：UI < toml < 任何上下文属性 < `[context.<name>]` < `[context.branchname]`。

## 重定向和重写

`_redirects` 规则首先处理，然后是 `netlify.toml`；在每个规则中，**从上到下第一个匹配的规则生效** — 将特定规则放在通用规则之前。边缘函数在重定向之前运行。

SPA 历史记录 `pushState` 降级（需要干净的 URL）：
```
/*  /index.html  200
```
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

`_redirects` 语法 — `from to [status] [条件]`，`#` 注释，路径区分大小写，URL 编码特殊字符：
```
/home         /              301
/my-redirect  /              302
/ecommerce    /store-closed  404          # 为路径自定义 404
/pass-through /index.html    200          # 重写
/best-pets/dogs /best-pets/cats.html 200! # 强制/阴影 (! 或 force=true)
/news/*  /blog/:splat                     # splat
/news/:month/:date/:year/:slug  /blog/:year/:month/:date/:slug   # 占位符
/store id=:id  /blog/:id  301             # 查询参数
/  /anz  302  Country=au,nz               # 值列表中无空格
/israel/*  /israel/he/:splat  302  Language=he
/* /legacy/:splat 200 Cookie=is_legacy,my_other_cookie
```

`[[redirects]]` 关键字：`from`，`to`，`status`（默认 `301`），`force`（默认 `false`；`!`/阴影），`query` (`query = {path = ":path"}`)，`条件` (`{Language, Country, Role, Cookie}`)，`headers`（代理请求头部），`signed`（环境变量名称，用于签名代理）。

**注意事项：**
- 你**不能**通过重定向添加/删除尾随斜杠 — CDN 首先规范化 URL；`/x/ → /x 301!` 规则会无限循环。依赖漂亮的 URL（默认开启）。
- Splat 星号仅适用于段落的**末尾**（`/jobs/*`），不适用于路径中间（`/jobs/*.html` 无效）。占位符（`:x`）仅适用于段落的开始；不能在一个段落中混合通配符+占位符。
- 你不能排除 splat 中的路径；将更具体的规则放在前面。
- `Country` = ISO 3166-1 alpha-2；语言重定向仅匹配**第一个** `Accept-Language` 条目。
- 基于角色的重定向与外部身份验证提供程序**仅限企业版**。
- 10,000+ 重定向：使用通配符/占位符或边缘函数 — 过大的序列化输出会导致部署失败。

## 代理

```
/api/*           https://api.example.com/:splat        200
/netlify-site/*  https://my-other-site.netlify.app/:splat  200   # 使用 .netlify.app，而不是自定义域名
```
```toml
[[redirects]]                     # 自定义请求头部 + force
  from = "/search"
  to = "https://api.mysearch.com"
  status = 200
  force = true
  headers = {X-From = "Netlify"}
```
签名代理（`signed` 名称是作用域为**运行时**的环境变量；必须位于 `netlify.toml` 中；JWS 仅限外部，不能是 Netlify→Netlify）：
```toml
[[redirects]]
  from = "/search"
  to = "https://api.mysearch.com"
  status = 200
  force = true
  signed = "API_SIGNATURE_TOKEN_PLACEHOLDER"
```

**注意事项：** 不允许跨团队重写；相同密码站点重写是允许的，但不能跨不同的受保护站点；代理超时**26 秒**；默认单跳；相对路径资源会中断（使用绝对路径或 `<base>`）；静默忽略循环。

## 自定义头部

```
/*
  X-Frame-Options: DENY
/templates/index2.html
  X-Frame-Options: SAMEORIGIN
```
多值 — 重复键（`_headers`）或多行 TOML 字符串：
```toml
[[headers]]
  for = "/*"
  [headers.values]
  cache-control = '''
  max-age=0,
  no-cache,
  no-store,
  must-revalidate'''
```

**注意事项：**
- `_headers`/`netlify.toml` 中的头部是**全局的** — **不**作用域于分支/上下文。解决方法：删除全局头部，将头部文件保存在自定义目录，并从每个上下文的构建命令中复制它们到发布目录：
  ```toml
  [context.staging]
    command = "npm run build && cp ./custom-headers/_stagingHeaders ./dist/_headers"
  ```
- 头部仅适用于 Netlify 库中的文件 — **不**适用于代理内容或函数/边缘（SSR）响应；这些必须设置自己的头部。
- 忽略（服务器设置）的名称包括 `Content-Length`，`Content-Encoding`，`Location`（使用重定向），`Set-Cookie`，`Server` 等。
- 基本认证头部：**Pro/Enterprise 仅限**。跨子域 Cookie 需要自定义域名（`netlify.app` 在 Public Suffix List 中）。

## 函数

```toml
[functions]
  directory = "myfunctions/"          # 默认：<base>/netlify/functions
  node_bundler = "esbuild"
  external_node_modules = ["package-1"]  # esbuild 仅限；原生插件等。
  included_files = ["files/*.md"]        # ! 前缀排除

[functions."api_*"]                    # 通配符/命名块与顶层连接
  external_node_modules = ["package-2"]
  included_files = ["!files/post-1.md"]
```

## 环境变量

两种存储方法：
- **UI / CLI / API** — 存储在 Netlify（不在仓库中）。支持站点+共享变量，上下文值，作用域；可用于构建，函数/边缘/ODB，代码片段注入，表单，签名代理。**推荐用于任何敏感内容。**
- **`netlify.toml`** — 存储在仓库中。仅站点变量，上下文值，**无作用域选择**（所有内容都获得**构建** + **后处理**），仅用于构建+代码片段注入。

`netlify.toml` 环境变量**覆盖**相同键的 UI/CLI/API 变量。

TOML 中的上下文值：
```toml
[context.production]
  environment = { NODE_VERSION = "14.15.3" }
[context.deploy-preview.environment]
  NOT_PRIVATE_ITEM = "not so secret"
[context.branch-deploy.environment]
  NODE_ENV = "development"
```

CLI：
```bash
netlify env:set KEY value          # --secret 标记为敏感
netlify env:import .env             # 站点变量；--replace-existing 首先擦除其他变量
netlify env:unset KEY
netlify env:list --plain --context production > .env
netlify build                       # 使用 Netlify 环境变量的本地构建
```
API: `createEnvVars` / `updateEnvVar` (`is_secret: true`) / `setEnvVarValue` / `deleteEnvVar` / `deleteEnvVarValue`。

**访问语法：** Bash `$VAR` 在 `build.command`/`ignore.command` 中；`process.env.VAR` 在 Node 脚本和插件中。

**作用域**（Pro/Enterprise；默认全部）：构建（站点构建） · 函数（函数/边缘/ODB） · 运行时（表单，签名代理） · 后处理（代码片段注入）。共享变量是 Pro/Enterprise 和**仅团队所有者可读/编辑**。站点+共享键冲突的优先级按作用域解决 — 站点变量仅在它实际携带的作用域内获胜。

**命名/限制：** 键为字母数字+下划线，必须以字母开头（`1KEY`，`_KEY1` 无效）；键≤255 字符，值≤5,000 字符。保留只读变量名称。更改需要构建+部署。

**通过保留配置变量设置构建语言** — `NODE_VERSION`，`NPM_FLAGS`，`YARN_VERSION`，`BUN_VERSION`，`RUBY_VERSION`，`PHP_VERSION`，`PYTHON_VERSION`，`GO_VERSION`，`HUGO_VERSION`，`PNPM_FLAGS`，`NPM_TOKEN`（Yarn：`YARN_NPM_AUTH_TOKEN`），等。

**必须在 UI/CLI/API 中设置，不能在 `netlify.toml` 中**（在仓库克隆后或仅运行时变量之后读取）：`AWS_LAMBDA_JS_RUNTIME`，`GIT_LFS_ENABLED`，`GIT_LFS_FETCH_INCLUDE`，`NETLIFY_BUILD_DEBUG`。

**`CI` 注意事项：** 默认为 `true`；如果它破坏了构建，则在构建命令前添加 `CI='' `。

### 将环境值注入头部/重定向
`key = "$VAR"` 是不支持的。仅路径（作用域必须包括**构建**）：
```toml
[build]
  command = "sed -i \"s|HEADER_PLACEHOLDER|${PROD_API_LOCATION}|g\" netlify.toml && yarn build"
```
`sed` 替换仅在 `[[headers]]`/`[[redirects]]`（构建后读取）中有效，并且**对构建插件不可见**（它们在构建命令之前运行）。对于插件可见的更改，请使用本地构建插件编辑 `netlifyConfig`。

### 有用的只读构建变量
`CONTEXT` (`production`/`deploy-preview`/`branch-deploy`/`dev`), `BRANCH`, `COMMIT_REF`, `CACHED_COMMIT_REF`, `PULL_REQUEST`, `REVIEW_ID`, `URL`, `DEPLOY_URL`, `DEPLOY_PRIME_URL`, `SITE_ID`, `SITE_NAME`。

## 密钥控制器

将变量标记为敏感：`Contains secret values`（UI） / `--secret`（CLI） / `is_secret: true`（API）。强制执行，不可自定义的策略：
- 敏感值是**只写**的 — 设置后没有可读版本；无法删除标志以显示它。
- 敏感值需要明确上下文+作用域；**不能**携带 `post processing` 作用域。
- 仅 Netlify 上的代码（边缘/服务器less/构建）读取未掩码的值；Netlify 外部看到的是掩码的。`dev` 上下文值是例外（从 UI/CLI/API 未掩码）；`netlify build` 从不输出原始值。

**密钥扫描**在设置任何变量为敏感后自动运行（并通过智能检测）。在检测到时失败并记录位置。通过每个上下文设置的环境变量配置：
- `SECRETS_SCAN_ENABLED=false` — 禁用**所有**扫描（失去所有密钥保护）。
- `SECRETS_SCAN_SMART_DETECTION_ENABLED=false` — 仅禁用智能检测。
- `SECRETS_SCAN_OMIT_KEYS`, `SECRETS_SCAN_OMIT_PATHS`（逗号分隔；路径从仓库根目录，通配符有效）。
- `SECRETS_SCAN_SMART_DETECTION_OMIT_VALUES` — 安全列表误报（**优先**使用此方法而不是禁用）。智能检测适用于 Personal/Pro/Enterprise。

扫描覆盖所有构建文件，值>4 字符且非布尔值，搜索明文+base64+URI 编码的变体。

### 敏感变量策略（仅限公共仓库）
管理**不受信任**的部署（未识别的作者）是否获得敏感变量。站点成员的 Git 部署始终受信任，即使来自分支。在项目配置 > 环境变量 > 站点策略中设置：
- **需要批准**（默认）— 不受信任的部署等待成员的批准。
- **无敏感变量部署** — 构建运行，敏感变量被保留。
- **无限制部署** — 所有变量都存在。

不适用于 GitHub Enterprise Server / GitLab 自托管仓库（视为私有）。

## 忽略构建

`ignore` 在 `[build]` 下决定是否重新构建 — 从基础目录以 Bash（或 Node.js 18，固定；站点 `package.json` 依赖**不可用**）运行。**退出 `1` = 已更改 → 构建继续；退出 `0` = 未更改 → 构建停止。** 构建钩子始终构建，无论退出代码如何。
```toml
[build]
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF packages/blog-1 packages/common"
```
```toml
[build]
  ignore = "node ignore_build.js"   # 分离文件路径必须以 ./ 开头
```
```js
// ignore_build.js
process.exitCode = process.env.BRANCH.includes("debug") ? 0 : 1
```

## 单仓库项目

将站点子目录设置为**包目录**（将其 `netlify.toml` 放在那里），将基础保留在根 `/`，在子目录级别声明依赖。包目录是**仅 UI — 不能在 `netlify.toml` 中设置**（项目配置 > 开发设置 > 持续部署 > 构建设置）。配置文件发现顺序：包目录 → 基础目录 → 根。`netlify.toml` 中的路径相对于基础目录保持绝对路径。`netlify <cmd> --filter <site>` 选择站点。

## JavaScript SPAs

构建命令 `npm run <script>` / `yarn <script>`；发布目录通常为 `dist`（框架依赖）。添加 `/*  /index.html  200` 降级（如上所述）用于 `pushState` 路由。代码拆分+哈希文件名与原子部署可能导致 `Uncaught SyntaxError: Unexpected token` 在陈旧引用上 — 禁用哈希文件名，使用永久链接，或使用服务工作者。

## Netlify Dev `[dev]`

**不**在 Bash 中运行（`command` 中无 Bash 语法）。**没有 `environment` 键** — 在 `[context.dev.environment]` 下设置本地环境变量。
```toml
[dev]
  command = "yarn start"
  targetPort = 3000        # 如果同时设置 command + targetPort，框架必须为 "#custom"
  port = 8888
  framework = "#custom"
  [dev.https]
    certFile = "cert.pem"
    keyFile = "key.pem"
```

## 插件与扩展

```toml
[[plugins]]
package = "netlify-plugin-check-output-for-puppy-references"
  [plugins.inputs]
  breeds = ["pomeranian", "chihuahua"]

[[integrations]]              # 构建时扩展；团队首先安装
  name = "abc-performance-extension"
  [integrations.config]
    output_path = "reports/performance-reports.html"
```

完整参考页面：构建环境变量在 https://docs.netlify.com/build/configure-builds/environment-variables.md，环境变量概述在 https://docs.netlify.com/build/environment-variables/overview.md，密钥控制器在 https://docs.netlify.com/build/environment-variables/secrets-controller.md，重定向在 https://docs.netlify.com/manage/routing/redirects/overview.md，重定向选项在 https://docs.netlify.com/manage/routing/redirects/redirect-options.md，重写/代理在 https://docs.netlify.com/manage/routing/redirects/rewrites-proxies.md，自定义头部在 https://docs.netlify.com/manage/routing/headers.md，以及基于文件的配置在 https://docs.netlify.com/build/configure-builds/file-based-configuration.md。

<!-- 密钥控制器本身的计划未在来源中指定；仅其公共仓库要求和智能检测计划列表被记录。 -->

<!-- system: agent-context/config/system.md — 人类拥有，由 ctx-gen 合并；编辑 system.md，不要编辑此部分 -->
# Netlify 房间规则（配置）

这些是组织约定，不是文档事实 — 合并到渲染的技能中并由 ctx-gen 合并，永远不会生成。由技能维护者拥有。

1. 在 `netlify.toml` 中设置的环境变量**对函数或边缘函数在运行时不可用** — 在那里读取它们会返回 `undefined`。在 UI 或使用 `netlify env:set` 设置运行时变量，而不是 `netlify.toml`。
2. 永远不要在客户端前缀环境变量中放置密钥（`VITE_`，`NEXT_PUBLIC_`，`PUBLIC_`，...） — 它们会内联到客户端包中；`--secret` 不保护它们。
3. 当本地快照环境变量（`netlify env:list --plain > .env`）时，保持 `.env` git 忽略 — 永远不要提交它。
4. 明确声明状态环境变量作用域交互：站点变量作用域为构建的**不**会阴影其他作用域的共享变量 — 优先级按作用域独立解析（站点变量仅在它实际携带的作用域内获胜）。
