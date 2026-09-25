# 安全修复

查找并修复 **$ARGUMENTS** (如果未提供参数，则修复整个应用程序) 中的安全问题。按顺序执行以下每个步骤。发现任何问题的步骤都必须修复该问题。

---

## 第 1 步 — 映射攻击面

在检查任何内容之前，请阅读以下文件：

- `src/main.tsx` / `src/App.tsx` — 入口点、路由、认证网关
- `vite.config.ts` — 开发服务器代理、CORS、标头
- `package.json` — 第三方依赖项列表
- 任何匹配 `**/auth*`、`**/login*`、`**/token*`、`**/credential*` 的文件

识别：

- 所有页面/路由以及每个页面/路由是否由认证网关保护
- 应用程序中所有外部数据入口的位置 (CDF SDK 调用、`fetch`、用户表单输入)
- 所有将数据写回的位置 (CDF 插入/更新、`fetch` POST/PUT/DELETE)

---

## 第 2 步 — 将所有 CDF 访问迁移到 Cognite SDK

所有到 **Cognite Data Fusion (CDF)** 的流量都必须通过 **官方 Cognite SDK**。查找任何绕过 SDK 并调用 CDF 类主机或 API 的 HTTP、WebSocket 或其他网络调用，并将其重写为使用 SDK。

### 搜索原始 HTTP 调用

```bash
# 查找 fetch、axios、XMLHttpRequest 和其他 HTTP 客户端使用
grep -rn --include="*.ts" --include="*.tsx" --include="*.js" \
  -E "(fetch\(|axios\.|axios\(|XMLHttpRequest|\.ajax\(|http\.get\(|http\.post\(|request\()" src/

# 查找看起来像 CDF 端点的原始 URL 构造
grep -rn --include="*.ts" --include="*.tsx" \
  -E "(cognitedata\.com|cognite\.ai|/api/v1/projects|cdf\.|\.cognite\.)" src/

# 查找自定义 Authorization 或 api-key 标头
grep -rn --include="*.ts" --include="*.tsx" \
  -E "(Authorization|api-key|apikey|x-api-key)" src/ | grep -v "node_modules"
```

### 如何修复

对于每个找到的原始 CDF 调用，请阅读周围的代码以了解它针对的 CDF 资源和操作，然后使用适当的 SDK 方法进行重写。如果不再使用原始 HTTP 客户端，请删除原始 HTTP 客户端导入。

| 模式 | 操作 |
|------|------|
| `fetch()` 或 `axios` 调用 CDF URL (`*.cognitedata.com`, `/api/v1/projects/*`) | **重写**为使用 Cognite SDK (`cognite.files.getDownloadUrls(...)`、`cognite.timeseries.retrieve(...)`、`client.instances.search(...)` 等) |
| 自定义 `Authorization` 标头，其中包含 CDF 令牌 | **删除** — SDK 自动处理认证 |
| 到 CDF 端点的 WebSocket 连接 | **重写**为使用 SDK 流式传输方法 |
| 内部转发到 CDF 的代理端点 | **重写**代理以内部使用 SDK |
| 到非 CDF URL 的 `fetch()` (静态资源、文档化的第三方 API) | **保留** — 但添加注释说明为什么需要它 |

重写所有 CDF 调用后，删除不再使用的任何 `axios` 或 `fetch` 相关的导入。

### 可接受的内容

- 通过 `sdk.files.*`、`sdk.timeseries.*`、`client.instances.*` 等 CDF 读取/写入
- 非 CDF 网络调用，包括：
  - 到已知静态资源主机 (CDN、图像服务)
  - 到产品所需的文档化第三方 API
  - 在应用程序的 README 或架构文档中明确注明的

---

## 第 3 步 — 查找并修复凭证和密钥卫生问题

搜索硬编码的凭证和敏感值：

```bash
# 在源文件中查找任何看起来像密钥的内容
grep -rn --include="*.ts" --include="*.tsx" --include="*.js" \
  -E "(password|secret|apikey|api_key|token|bearer|private_key)\s*=\s*['\"]" src/
```

对于每个硬编码的密钥，用环境变量替换它。创建或更新 `.env.example` 以添加占位符。如果缺少，请将 `.env` 添加到 `.gitignore` 中。

### 如何修复

1. **用 `import.meta.env.VITE_*` 引用替换每个硬编码的密钥**。例如：
   - `const apiKey = "sk-abc123"` → `const apiKey = import.meta.env.VITE_API_KEY`
   - `const token = "eyJhbG..."` → `const token = import.meta.env.VITE_AUTH_TOKEN`

2. **将变量添加到 `.env.example`**，其中包含占位符值 (例如，`VITE_API_KEY=your-api-key-here`)。如果不存在，则创建 `.env.example`。

3. **确保 `.env` 和 `.env.local` 在 `.gitignore` 中** — 如果缺少，请添加它们。

4. **删除任何 `console.log`、`console.error` 或类似调用**，这些调用会打印 CDF 令牌、用户对象或 API 密钥。

---

## 第 4 步 — 查找并修复危险的 DOM API

搜索允许任意脚本执行或 HTML 注入的模式：

```bash
grep -rn --include="*.tsx" --include="*.ts" \
  -E "dangerouslySetInnerHTML|innerHTML\s*=|eval\(|new Function\(|setTimeout\(['\"]|setInterval\(['\"]" src/
```

对于每个危险的 DOM 模式，直接应用修复。如果需要，请使用 `pnpm add dompurify` 和 `pnpm add -D @types/dompurify` 安装 DOMPurify。

### 如何修复

- **`dangerouslySetInnerHTML`**：用 `DOMPurify.sanitize()` 包装值。将 `import DOMPurify from 'dompurify'` 添加到文件中。示例：
  ```tsx
  // 之前
  <div dangerouslySetInnerHTML={{ __html: userContent }} />
  // 之后
  import DOMPurify from 'dompurify';
  <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />
  ```

- **`eval()` / `new Function()`**：使用数据驱动方法重写。使用 `JSON.parse()` 进行数据解析，或使用查找表/switch 语句进行动态逻辑调度。永远不要将用户控制的字符串传递给代码评估。

- **`setTimeout`/`setInterval` 带有字符串参数**：转换为函数引用：
  ```ts
  // 之前
  setTimeout("doSomething()", 1000)
  // 之后
  setTimeout(() => doSomething(), 1000)
  ```

---

## 第 5 步 — 查找并修复认证和授权差距

阅读认证设置（可能是 `src/contexts/`、`src/hooks/` 或 `setup-flows-auth` 输出）：

- 每个显示 CDF 数据的路由都必须在 Flows 认证网关 (`useCogniteClient` 在渲染之前返回非空的 `sdk`) 后面。
- CDF 客户端必须使用短生命周期的 OIDC 令牌初始化，而不是静态 API 密钥。
- 用户角色/权限检查必须在服务器端 (CDF ACL) 进行 — 不要仅依赖隐藏 UI 元素。

检查 Atlas / agent：

- 优先使用 EOS 侧边栏 (`integrate-fusion-agent`)；应用程序内 `useAtlasChat` 是例外
- `agentExternalId` 不得来自用户输入；在 CDF 查询之前验证工具/操作参数
- 没有第三方 LLM API 使用 CDF 数据；没有对查询结果的无限制补全 (5 / 最大 50，缓存)

### 如何修复

对于每个未受保护的显示 CDF 数据的路由，用认证网关组件包装它。例如，确保路由元素被包装在一个检查 `useCogniteClient` 并在 SDK 未准备就绪时渲染加载/登录状态的组件中。

对于 Atlas 工具 `execute` 函数和 Fusion agent 动作处理程序，在每个函数的开头添加参数验证。在将 `args` 字段用于任何 CDF 查询之前，验证每个 `args` 字段是否为预期类型并在预期范围内。

---

## 第 6 步 — 查找并修复输入验证差距

任何从表单、URL 参数或查询字符串到达 CDF 调用或渲染到 DOM 的值都必须经过验证：

```bash
# 查找 useSearchParams、URLSearchParams 和表单 onChange 处理程序
grep -rn --include="*.tsx" --include="*.ts" \
  -E "useSearchParams|URLSearchParams|searchParams\.get|e\.target\.value" src/
```

对于每个未验证的外部输入，请添加运行时验证。如果不存在，请安装 Zod (`pnpm add zod`)。创建一个与预期形状匹配的模式，并使用 `.safeParse()` 而不是类型强制转换。

### 如何修复

1. **为 URL 参数和表单输入添加 Zod 模式**。示例：
   ```ts
   import { z } from 'zod';
   const paramSchema = z.object({
     id: z.string().min(1),
     page: z.coerce.number().int().positive().default(1),
   });
   const result = paramSchema.safeParse({ id: searchParams.get('id'), page: searchParams.get('page') });
   if (!result.success) { /* 处理错误 */ }
   ```

2. **用 Zod `.safeParse()` 替换外部数据上的 `as MyType` 强制转换** — 不要信任来自 URL 参数、表单输入或 API 响应的数据，除非经过验证。

3. **为 `searchParams.get()` 添加空值回退** — 始终处理参数缺失或为空的情况。

---

## 第 7 步 — 查找并修复 Vite / 服务器配置

阅读 `vite.config.ts` 和任何 `server.ts` / `express.ts` 文件。

### 如何修复

向 `vite.config.ts` 的 `server.headers` 部分添加任何缺少的安全标头。如果该部分不存在，请创建它。最低要求的安全标头是：

```ts
server: {
  headers: {
    'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://*.cognitedata.com",
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
  },
}
```

调整 `Content-Security-Policy` 以匹配应用程序的实际需求 (例如，添加特定的 CDN 主机用于字体或图像)。

此外：

- **删除 `vite.config.ts` 中的任何 `define` 条目**，这些条目将原始密钥嵌入到捆绑包中。使用 `import.meta.env` 代替。
- **确认开发代理** (`server.proxy`) 在生产构建中不会暴露内部端点。

---

## 第 8 步 — 查找并修复依赖项漏洞

```bash
pnpm audit --audit-level=high
```

### 如何修复

1. 首先运行 `pnpm audit fix` 以自动修复可能的情况。
2. 对于任何剩余的高危/关键 CVE，手动在 `package.json` 中更新包版本并运行 `pnpm install`。
3. 如果一个易受攻击的包没有可用的修复程序，请将其记录为已知风险，并检查是否有替代包。

---

## 第 9 步 — 报告剩余发现

仅报告无法自动修复的问题 (例如，需要人类判断的架构决策、没有可用修复程序的包，或需要重大重构的模式)。

总结每个步骤中修复的内容：

| 步骤 | 修复了什么 | 剩余问题 |
|------|------------|----------|
| 2 — CDF SDK | 将 N 个原始调用迁移到 SDK | (任何无法迁移的) |
| 3 — 凭证 | 用环境变量替换 N 个硬编码密钥 | (任何需要人类决策的) |
| 4 — DOM | 清理 N 个危险模式 | (任何需要重构的) |
| 5 — 认证 | 包装 N 个未受保护的路由 | (任何架构差距) |
| 6 — 验证 | 为 N 个输入添加 Zod 模式 | (任何需要自定义逻辑的) |
| 7 — Vite 配置 | 添加 N 个安全标头 | (任何需要 CSP 调整的) |
| 8 — 依赖项 | 修复 N 个易受攻击的包 | (任何没有可用修复程序的) |

如果任何剩余问题需要在部署前立即采取行动，请明确列出它们。

---

## 完成

说明已修复的内容，并确认应用程序更安全。列出在下次部署前需要人类判断的任何剩余项。
