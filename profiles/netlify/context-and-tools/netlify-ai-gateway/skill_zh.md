# Netlify AI Gateway

使用提供方的官方 SDK 从 Netlify 计算环境中调用 AI 模型。网关会自动注入提供方凭证 — 无需参数实例化 SDK 即可使用。

**使用注入了环境凭证的提供方 SDK。** 不要直接使用 `fetch()` 对网关 URL 进行调用，也不要将调用 `NETLIFY_AI_GATEWAY_KEY` / `NETLIFY_AI_GATEWAY_URL` 作为默认路径进行线路连接 — 这些仅适用于第三方/不支持的库（见下文）。

## 警示（首先阅读）

- **不可在浏览器中调用。** 网关调用属于函数或边缘函数 — 绝不可以在客户端代码中使用。浏览器没有注入的凭证。
- **仅限运行时凭证。** 不要从构建脚本、预渲染/SSG 或构建插件中调用网关 — 这些调用将不会获得凭证并失败。在请求时进行 AI 工作；如果输出必须看起来像是预计算的，请将结果缓存到 Netlify Blobs 中。
- **60 秒同步超时。** 同步函数中的网关调用受限于 60 秒的函数超时。流式传输长时间生成（SDK 流式传输 + `ReadableStream`），或使用一个持久化输出以供客户端获取的背景函数。绝不要留下未流式传输的慢速生成。
- **需要至少一次生产部署。** 网关在项目至少有一次生产部署后才会激活。即使是本地开发，也必须先运行一次 `netlify deploy --prod`。
- **不要硬编码模型列表。** 可用模型会发生变化。检查实时提供方端点（`https://api.netlify.com/api/v1/ai-gateway/providers/detailed`）而不是内置静态列表。
- **OpenRouter SDK 需要 1.2.43+。** 更早版本会忽略 `OPENROUTER_BASE_URL`，直接调用 openrouter.ai，并以 `401 Missing Authentication header` 失败。

## 代码存放位置

编写正常的函数/处理器代码 — 没有专门的 AI 文件类型。位于 `netlify/functions/joke.js` 的函数导出 `config = { path: "/api/joke" }` 会在 `netlify dev` 和生产环境下都提供 `/api/joke` 服务。

## 提供方 SDK（无需参数实例化）

网关会注入每个提供方自己的环境变量，因此官方 SDK 可以零配置工作。

Anthropic Claude:
```js
import Anthropic from '@anthropic-ai/sdk';
const anthropic = new Anthropic(); // 使用 ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL

const message = await anthropic.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello!' }]
});
```

OpenAI:
```js
import OpenAI from 'openai';
const openai = new OpenAI(); // 使用 OPENAI_API_KEY, OPENAI_BASE_URL

const completion = await openai.chat.completions.create({
  model: 'gpt-5',
  messages: [{ role: 'user', content: 'Hello!' }]
});
```

Google Gemini:
```js
import { GoogleGenAI } from '@google/genai';
const genAI = new GoogleGenAI({}); // 使用 GEMINI_API_KEY, GOOGLE_GEMINI_BASE_URL

const result = await genAI.models.generateContent({
  model: 'gemini-2.5-pro',
  contents: 'Hello!'
});
```

TypeSafe (Jev) — 结构化决策（例如路由/分类表单提交）:
```ts
import type { Config, Context } from '@netlify/functions';
import { choice, TypeSafeClient } from '@typesafe-ai/sdk';

export default async (req: Request, context: Context) => {
  const body = await req.json().catch(() => undefined);
  if (body === undefined)
    return Response.json({ error: 'Request body must be valid JSON.' }, { status: 400 });

  const client = new TypeSafeClient(); // 使用 TYPESAFE_API_KEY, TYPESAFE_BASE_URL
  const { answers } = await client.systemOne({
    state: body,
    questions: {
      team: choice('Route this contact form submission', {
        sales: null,
        support: null,
        spam: null,
      }),
    },
  });

  return Response.json({ team: answers.team.choice, requestId: context.requestId });
};

export const config: Config = { path: '/api/route', method: 'POST' };
```
`systemOne` 默认使用 `jev-latest` 模型。每个问题都是一个 `choice(prompt, options)` 映射，将选项命名为 `null`；结果位于 `answers.<question>.choice`。以 JSON 正文（例如 `{"message":"Can someone help us upgrade to 200 seats?"}`）和 `Content-Type: application/json` 发送 POST 请求。

OpenRouter（需要 SDK 1.2.43+ — 见警示）:
```js
import { OpenRouter } from '@openrouter/sdk';
const openRouter = new OpenRouter(); // 使用 OPENROUTER_API_KEY, OPENROUTER_BASE_URL

const result = await openRouter.chat.send({
  chatRequest: {
    model: 'x-ai/grok-4.5',
    messages: [{ role: 'user', content: 'Hello!' }]
  }
});
```

通过 OpenRouter 可用的模型可以使用 OpenRouter SDK 或 OpenAI SDK 以 OpenRouter 模型 ID 表示（例如 `deepseek/deepseek-v4-flash-0731`）— 只需将 ID 作为 `model` 传递。

上述模型 ID（`gpt-5`、`claude-sonnet-4-5-20250929`、`gemini-2.5-pro`、`x-ai/grok-4.5` 等）是示例，会发生变化 — 请检查实时提供方端点。

## 环境变量 — 哪些需要使用

**默认:** 支持的提供方 SDK 会自动消耗注入的提供方特定变量。像上面那样无参数实例化 SDK（`new OpenAI()`、`new Anthropic()`、`new GoogleGenAI({})`、`new TypeSafeClient()`、`new OpenRouter()`）并为您读取相应的对：

- OpenAI: `OPENAI_API_KEY`, `OPENAI_BASE_URL`
- Anthropic: `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`
- Google Gemini: `GEMINI_API_KEY`, `GOOGLE_GEMINI_BASE_URL`
- OpenRouter: `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`
- TypeSafe: `TYPESAFE_API_KEY`, `TYPESAFE_BASE_URL`

**显式配置路径:** `NETLIFY_AI_GATEWAY_KEY` 和 `NETLIFY_AI_GATEWAY_URL` 始终会被注入，并且永远不会与用户设置的提供方变量冲突。仅在第三方或不支持的库需要显式密钥/基础 URL 配置时使用此对 — 作为构造函数参数传递。这不是默认值；支持的 SDK 应该使用上面提到的提供方特定变量。

**优先级:** Netlify 不会覆盖您在项目或团队级别设置的密钥或基础 URL。如果您设置了您自己的提供方密钥，网关会使用它。对于 Gemini 特定的情况，如果设置了 `GOOGLE_API_KEY` 或 `GOOGLE_VERTEX_BASE_URL`，则会跳过注入（Vertex/Google-API-key 设置优先）。

要停止所有注入，禁用 AI 功能：https://docs.netlify.com/build/build-with-ai/manage-ai-for-your-team/manage-ai-features/#disable-ai-features

## 完整示例（Vite + React + Function）

通过检查注入的变量来检测网关的可用性，然后调用 SDK。

首先安装客户端：`npm install openai`。然后创建 `netlify/functions/joke.js`:
```js
import process from "process";
import OpenAI from "openai";

export default async () => {
  if (!process.env.OPENAI_BASE_URL)
    return Response.json({ error: "AI Gateway not active — deploy to prod once on a credit-based plan" });

  try {
    const client = new OpenAI();
    const res = await client.responses.create({
      model: "gpt-5-mini",
      input: [{ role: "user", content: "Give me a short dad joke about coffee" }],
      reasoning: { effort: "minimal" },
    });
    return Response.json({
      joke: res.output_text?.trim() || "Out of jokes",
      model: res.model,
      tokens: { input: res.usage.input_tokens, output: res.usage.output_tokens },
    });
  } catch (e) {
    return Response.json({ error: `${e}` }, { status: 500 });
  }
};

export const config = { path: "/api/joke" };
```

`src/App.jsx` 获取 `/api/joke`:
```jsx
import { useState } from "react";

export default function App() {
  const [joke, setJoke] = useState();
  const [loading, setLoading] = useState(false);

  const getJoke = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/joke");
      setJoke(res.ok ? await res.json() : { error: res.status });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button onClick={getJoke} disabled={loading}>
        {loading ? "Thinking..." : "Get joke"}
      </button>
      <pre>{JSON.stringify(joke, null, 2)}</pre>
    </>
  );
}
```

## 本地开发

两个选项 — 都需要至少一次先前的生产部署：

1. **Netlify CLI:** `netlify dev` 提供完整的网关支持。
2. **Vite 插件:** 无需 `netlify dev` 就可以本地访问网关。添加 `@netlify/vite-plugin` 并运行您的原生开发命令（`npm run dev`）:
```js
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import netlify from "@netlify/vite-plugin";

export default defineConfig({ plugins: [react(), netlify()] })
```

设置流程:
```shell
npm install -g netlify-cli@latest
netlify login
npm create vite@latest dad-jokes -- --template react --no-interactive
cd dad-jokes && npm install
netlify init
netlify deploy --prod --open   # required: activates the gateway
```

## 计费、限制、约束

- **套餐:** 仅限基于积分的套餐（免费、个人、专业）。企业：请联系您的账户经理。遗留套餐必须先切换。默认启用，除非您禁用了 AI 功能或设置了您自己的提供方密钥。
- **成本:** tokens → USD（提供方公布费率）→ 积分。**$1 USD = 180 积分。**
- **速率限制**（每分钟、每个团队、跨所有项目）：免费 90，个人 450，专业 1,800，企业 9,000 积分。
- **上下文窗口:** 输入限制为 200k tokens。
- **提示缓存:** Anthropic — 仅默认 5 分钟的临时缓存；OpenAI — 为您设置每个账户的 `prompt_cache_key`；Gemini — 不支持显式上下文缓存。
- **无转发头**（无法启用基于头的实验性功能）、**无批量推理**、**无 OpenAI 优先处理**。
- **OpenRouter ZDR 仅限:** Netlify 仅路由到具有零数据保留政策的提供方。OpenRouter 目录中列出的模型如果没有 ZDR 保证的主机则不会被提供。浏览 ZDR 合格的模型：https://openrouter.ai/models?zdr=true
- **隐私:** 网关不会存储提示或模型输出。

**成本控制:** 在 AI 调用函数/边缘函数上设置速率限制规则，以防止访客滥用和成本失控：https://docs.netlify.com/manage/security/secure-access-to-sites/rate-limiting/ — 并配置自动充值或积分包：https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/configure-auto-recharge/ · https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/buy-credit-packs/

监控使用情况：https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/monitor-usage-for-credit-based-plans

## 参考

- 概述：https://docs.netlify.com/build/ai-gateway/overview.md
- 快速入门：https://docs.netlify.com/build/ai-gateway/quickstart-for-ai-gateway.md
- 示例：https://docs.netlify.com/build/ai-gateway/examples.md — 包括 AI SEO 图片生成器（Gemini 图片生成）：https://github.com/netlify/examples/tree/main/examples/ai-seo-image-generator 和一个 TanStack Start 聊天应用：https://github.com/netlify-templates/tanstack-template

<!-- Gap: 直接服务的模型名称（Anthropic/OpenAI/Gemini/TypeSafe）不是静态可枚举的 — 在构建时从实时提供方端点渲染。 -->

<!-- system: agent-context/ai-gateway/system.md — 人类拥有，由 ctx-gen 合并；编辑 system.md，不要编辑此部分 -->
# Netlify house rules (ai-gateway)

这些都是组织约定，不是文档事实 — 由 ctx-gen 合并到渲染的技能中，并且永远不会生成。由技能维护者拥有。

1. 使用提供方 SDK 并注入环境凭证 — 不要直接使用 `fetch()` 对网关进行调用，尽管原始 REST 是一个受支持的接口。正文必须不呈现原始 REST 或 `NETLIFY_AI_GATEWAY_KEY` / `NETLIFY_AI_GATEWAY_URL` 对作为推荐路径 — 但它仍然必须将这对作为事实进行文档化：始终会被注入，永远不会与用户设置的提供方变量冲突，并且在第三方或不支持的库需要显式配置时是正确的选择。降低推荐优先级；保留知识。
2. 网关不可在浏览器中调用：调用属于函数或边缘函数，绝不在客户端代码中。
3. 模型可用性会变化：不要硬编码模型列表；检查实时提供方端点。
4. 网关凭证仅限运行时：不要从构建脚本、预渲染/SSG 或构建插件中调用网关 — 这些调用将不会获得凭证并失败。在请求时进行 AI 工作，如果必须看起来像是预计算的，请将结果缓存（例如到 Netlify Blobs）。
5. 同步函数中的网关调用受限于 60 秒超时：流式传输长时间生成（SDK 流式传输 + `ReadableStream`），或使用一个持久化输出以供客户端获取的背景函数 — 绝不要留下未流式传输的慢速生成并假设它完成。
6. 当被问及需要使用哪些环境变量时 — 即使明确询问网关对 — 也应先以默认值回答，然后再回答字面问题：支持的提供方 SDK 会自动消耗其注入的提供方特定变量（`OPENAI_API_KEY`/`OPENAI_BASE_URL` 等）使用正文显示的确切每提供方实例化 — 重申正文设置，不要在此处编造构造函数细节。然后给出 `NETLIFY_AI_GATEWAY_KEY` / `NETLIFY_AI_GATEWAY_URL` 作为第三方或不支持的库的显式配置路径。单独回答网关对会将手拉手连接作为默认值，它不是。
