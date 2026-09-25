# Caffeine 推理
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的 LLM 扩展。

## 指挥器路由说明

将“使用 LLM / GPT / 聊天机器人 / 使用 AI 摘要”视为一级平台功能。默认路径是 **Caffeine 推理**：一个兼容 OpenAI 的聊天端点，由 Caffeine 托管、认证并计费。Canister 在运行时从平台获取凭证；无人粘贴 API 密钥，应用程序也永远不会存储或返回密钥。

| 用户意图 | 功能 |
| --- | --- |
| 在 Caffeine 应用中使用 LLM 进行聊天 / 摘要 / 分类 | 通过此技能使用 `caffeineai-inference-client` `ChatApi.createChatCompletion` |
| 使用用户粘贴的 `sk-...` 调用 `api.openai.com` | 仅使用 [`extension-openai`](../extension-openai/SKILL.md) |

不要为普通 Caffeine 应用 LLM 加载 `extension-openai`。不要要求用户输入 OpenAI API 密钥。不要添加 `setApiKey` 端点、密钥设置页面或模型选择器。

# 后端

## 1. 将 `caffeineai-inference-client` 添加到 `mops.toml`

```bash
mops add caffeineai-inference-client@0.1.0
```

需要 Mops ≥ 2.13。**最低版本**：`caffeineai-inference-client ≥ 0.1.0`。

## 2. 配置来自平台

`Config.fromEnv<system>()` 返回一个完整的 `Config` — 端点、bearer 和 `is_replicated = ?false` — 来自平台为应用程序提供的凭证。没有需要收集的密钥，也没有需要配置的内容。

- 在 `shared` 方法**内部**或在一个 `<system>` 参数化的辅助函数中，在**每个**请求时调用 `fromEnv<system>()`。模块级的 `let config = fromEnv` 将无法编译，并且当平台在一个运行的 canister 上旋转凭证时，缓存的 `Config` 可能会过时。
- 当应用程序没有推理凭证时，它会捕获异常。这是一个平台条件，不是应用程序可以修复的东西 — 不要添加“配置 AI”的空状态或密钥输入回退。
- 不要记录 `Config`，不要将 `auth` 复制到 actor 状态，并且不要从 `query` / `shared` 函数返回它（或它的任何部分）。

## 3. `is_replicated = ?false` 是必需的

`fromEnv` 已经设置了它。不要将其覆盖为 `?true` 或 `null`。

1. **安全性。** 一个复制的出调用会从每个副本发送 bearer。
2. **计费。** 复制的出调用会根据子网大小乘以推理支出。
3. **确定性。** LLM 正文是采样的；共识会失败。

## 4. 标准布局

```motoko filepath=src/backend/main.mo
import Inference "lib/inference";

actor {
  public shared func chat(prompt : Text) : async Text {
    await* Inference.runChat<system>(prompt);
  };
};
```

```motoko filepath=src/backend/lib/inference.mo
import { fromEnv } "mo:caffeineai-inference-client/Config";
import ChatApi "mo:caffeineai-inference-client/Apis/ChatApi";
import ChatCompletionRequest "mo:caffeineai-inference-client/Models/ChatCompletionRequest";
import ChatCompletionRequestMessageOneOf2 "mo:caffeineai-inference-client/Models/ChatCompletionRequestMessageOneOf2";
import Runtime "mo:core/Runtime";

module {
  public func runChat<system>(prompt : Text) : async* Text {
    let config = fromEnv<system>();
    let userMessage = ChatCompletionRequestMessageOneOf2.JSON.init({
      content = #string(prompt);
      role = #user;
    });
    let req = ChatCompletionRequest.JSON.init({
      messages = [#user(userMessage)];
      model = "router";
    });
    let resp = await* ChatApi.createChatCompletion(config, req);
    if (resp.choices.size() == 0) {
      Runtime.trap("Inference returned no choices");
    };
    resp.choices[0].message.content
      ?? Runtime.trap("Inference returned no text content");
  };
};
```

## 5. `model = "router"` — 平台选择模型

`"router"` 是唯一公开的模型 ID，它是一个路由层而不是模型名称。Caffeine 推理根据查询的复杂性调整每个请求的大小 — 简单提示使用小型快速模型，复杂的推理使用更强的模型 — 并将 `"router"` 作为响应 `model` 报告回来，因此提供者名称永远不会到达应用程序。

- 始终发送 `model = "router"`。
- 不要添加模型下拉菜单、“使用 GPT-4”切换或后端端点上的 `model` 参数。用户没有可选择的。
- 通过提示和声明的采样字段（`temperature`、`top_p`、`max_completion_tokens`）引导质量，而不是通过模型选择。

## 6. 调用形式

- **函数形式**：`ChatApi.createChatCompletion(config, req) : async*` — 使用 `await*`。
- **套件形式**：`let api = ChatApi(config); api.createChatCompletion(req) : async`。

## 7. 可用的 API 表面 — 聊天完成

`caffeineai-inference-client@0.1.0` 是从
[`public-api-v0.1.0`](https://github.com/caffeinelabs/inference/releases/tag/public-api-v0.1.0) 生成的：

| 模块 | 入口点 | 路径 |
| --- | --- | --- |
| `ChatApi` | `createChatCompletion` | `POST /v1/chat/completions` |
| `ModelsApi` | `listModels` | `GET /v1/models` — 目录仅限；模型始终是 `"router"`，因此应用程序永远不会需要这个 |

<!-- motoko-check:skip -->
```motoko
import ChatApi "mo:caffeineai-inference-client/Apis/ChatApi";
import { fromEnv } "mo:caffeineai-inference-client/Config";
```

聊天完成是整个产品表面。**不可用**在此主机上（404，并且不在包中）：嵌入、图像、音频、审核、文件、遗留完成、Assistants、Responses 和原始 `ic.http_request`。如果规范确实需要一个仅限 OpenAI 的 API 并带有粘贴的 `sk-...`，请切换到
[`extension-openai`](../extension-openai/SKILL.md)。

## 8. 周期

`defaultConfig.cycles = 30_000_000_000`。对于长完成，增加：

<!-- motoko-check:skip -->
```motoko
{ fromEnv<system>() with cycles = 100_000_000_000 }
```

流式传输（`stream = ?true`）不受支持 — 管理可以器 HTTP 返回完整正文。保留 `stream = null`。

## 9. 会咬你的事情

- 在 `shared` 方法**内部**调用 `fromEnv<system>()`（或一个 `<system>` 辅助函数）。模块级的 `let config = fromEnv` 将无法编译。
- `model = "router"` — 不是 `"gpt-4o-mini"`。见 §5。
- 用户回合是 `#user(ChatCompletionRequestMessageOneOf2.JSON.init({ content = #string(prompt); role = #user }))`。
- 使用 `JSON.init` 为必需字段；使用记录更新分层可选字段。不要手动列出每个 `null`。
- `resp.choices[0].message.content` 是 `?Text`。首先检查 `choices.size()`。
- 一个聊天调用是一个更新调用内部的 HTTP 出调用：预算秒数，不是毫秒。

# 前端

应用程序在第一次加载时即可聊天 — 没有需要配置的内容。

1. **没有 API 密钥 UI。** 没有设置页面，没有密码输入，没有“已配置？”指示器，没有 localStorage。如果规范或模拟显示“AI 设置”屏幕，请放弃它。
2. **没有模型选择器。** 见 §5。
3. 调用后端聊天端点（`chat(prompt)`）并渲染返回的文本。没有前端 LLM SDK — canister 是客户端，因此凭证永远不会到达浏览器。
4. 在调用进行中（出调用往返需要秒数）显示一个挂起状态，并在捕获时显示重试。
