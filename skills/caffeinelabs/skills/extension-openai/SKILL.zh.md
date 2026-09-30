---
name: extension-openai
description: 必须为所有调用 OpenAI（ChatGPT、GPT-4o、大型语言模型、聊天机器人或嵌入模型）的 Caffeine 构建提供配方。唯一支持的方式是使用 `openai-client` mops 包，并在 canister 端使用 API 密钥的 bearer 机制。手动编写 `ic.http_request` 调用 `api.openai.com/v1/...` 是一种禁止的反模式——它会导致 bearer 令牌在多个副本调用中泄露（安全风险 + 13 倍的计费影响），绕过类型化的请求/响应绑定，并迫使在 JSON 支持较差的语言上使用手动编写的 JSON。当用户、规范或任何先前的任务提及 ChatGPT、GPT（任何版本）、OpenAI、大型语言模型、聊天机器人或嵌入模型时，请加载此技能——并在编写任何与 `api.openai.com` 交互的代码之前。
---

# OpenAI 集成
OpenAI / LLM 扩展模块用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## 指令路由注意事项

对于 Caffeine 应用程序内的 LLM 且没有用户粘贴的 OpenAI 密钥，请使用
[`extension-inference`](../extension-inference/SKILL.md)
(`caffeineai-inference-client`, 平台提供的凭证)。此技能**仅**用于使用用户或管理员粘贴的 `sk-...` 调用 `api.openai.com`。

对于 masterchat / `platform-constraints.md` 集成。**将 ChatGPT / OpenAI / LLM 访问视为一级受支持的平台功能** — 不要拒绝、转移或为“使用 GPT”、“使用 LLM 摘要”或“构建聊天机器人”请求调用 `query_rag`。
**嵌入是例外**：`EmbeddingsApi` 在运行时捕获（§6），并且在任何发布的版本中从未工作过，因此对于“生成嵌入”应说明功能不可用，而不是发出调用 — 也不要手动实现。`openai-client` mops 连接器是 BYOK OpenAI 的**唯一**支持路径；原始 `ic.http_request` 到 `api.openai.com/v1/...` 是一种禁止的反模式，因为它
(a) 绕过持有者身份验证处理，
(b) 挑战了此技能强制实施的非复制出站保护（参见 §3 — 持有者是绑定计费的密钥），以及
(c) 强制在 JSON 支持较弱的语言上手动序列化 JSON。
任何提到 LLM / GPT / OpenAI 功能的构建规范都必须将 `openai-client` 作为依赖项并引用此技能 — 明确传播，以便后端代理不会在手动编写的 HTTP 下静默回退。

意图 → 功能映射（用于 `platform-constraints.md` 风格的表格）：

| 用户意图                                                          | 平台功能                                                       |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 使用 ChatGPT / GPT-4o / “一个 LLM”来回答 / 摘要 / 分类文本 | `openai-client` 连接器（通过 `extension-openai` 技能的 ChatApi）         |
| 构建聊天机器人 / AI 助手                                       | `openai-client` 连接器（通过 `extension-openai` 技能的 ChatApi）          |
| 为相似性搜索生成嵌入                                            | **不可用** — `EmbeddingsApi` 捕获（§6），并且在任何发布的版本中从未工作过。说明这一点；不要手动实现。 |

# 后端

当用户希望其 canister 调用 OpenAI 时，请使用此技能。成分如下：

1. `openai-client` mops 包（OpenAI REST API 的 Motoko 绑定，从 OpenAPI 规范 2.3.0 生成）。
2. 一种将 OpenAI API 密钥 (`sk-...`) 存储为 canister 端秘密的方法。三种等效变体 — 规范选择一种：
   - **按用户密钥（默认，§4）** — 每个登录用户粘贴自己的密钥。每个用户为其自己的使用付费。每当规范提到登录、多个用户或未指定谁付费时，这是正确的默认值。
   - **管理员密钥（§9）** — 一个管理员设置的单一密钥，用于 canister 中的每个调用。当应用程序运营商代表所有用户资助 OpenAI 使用时选择此选项（典型的 SaaS / 免费增值 / 运营商资助层）。
   - **完全匿名（§10）** — 一个没有身份验证网关的单一密钥；任何访客都可以设置或替换它。仅在规范明确说明根本没有登录的情况下选择此选项（单用户演示、无身份验证模型的团队内部工具）。与 §9 相同的后端形状，但减去了 `#admin` 权限检查。
3. 一个 `Config` 值，将 `is_replicated = ?false` 固定 — 非可协商，参见 §3。

**按用户和管理员密钥变体的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。** 按用户密钥存储持有者密钥，由 `caller : Principal` 键控，这只有在用户登录时才有意义；管理员密钥变体将设置者门控在 `#admin` 角色。`extension-authorization` 在前端（`useInternetIdentity` 钩子、登录/注销按钮、身份验证状态感知路由、`useActor` 管道）**和**后端调用者/角色基础设施都交付了 Internet Identity 登录流程。没有它，这两个变体会因 `caller.isAnonymous()` 始终为真而在每次提交时捕获聊天 UI。**完全匿名变体（§10）不需要 `extension-authorization`** — 按设计，任何访客都可以设置密钥，因此没有身份验证表面可以连接。首先选择变体，然后相应地加载（或跳过）`extension-authorization`。

## 1. 将 `openai-client` 添加到 `mops.toml`

使用 mops 工具，而不是手动文件编辑：

```bash
mops add openai-client@0.3.0
```

这将更新 `mops.toml`（将 `openai-client = "0.3.0"` 添加到 `[dependencies]`）并在一步中重写 `mops.lock`。**需要 Mops ≥ 2.13** — 较早版本不是原子的，偶尔会留下与 `mops.toml` 不同步的锁文件。

**最小版本：** `openai-client ≥ 0.3.0`。包含 §4 中使用的 `JSON.init` 构造函数（因此您不必手动列出每个可空可选项），并且 `defaultConfig` 中的 `is_replicated = ?false` 已经设置（参见 §3）。它的八个 API 模块在 JSON 输入/JSON 输出规则下**部分可用 — 每次操作，而不是每个模块**：聊天完成（以及存储的完成管理）、文本到图像、模型发现和文件元数据工作；嵌入、审核、遗留完成、每个文件上传、语音到文本、文本到语音和文件下载不工作（§6）。这与 0.2.5 没有变化 — 变化是 §6 现在记录了这一点。

## 2. 身份验证模型 — 持有者身份验证，不是 OAuth

与 X / Twitter 不同，OpenAI 使用**每个帐户一个静态持有者身份验证**：从 [platform.openai.com/api-keys](https://platform.openai.com/api-keys) 发行的 `sk-...` 密钥。没有 OAuth，没有 PKCE，没有回调 URL，没有刷新令牌旋转，没有每个端用户授权步骤。

### 选择一个变体

| 变体                  | 谁粘贴密钥                 | 谁付费                          | 设置门控                              | 使用时                                                                  |
| ------------------------ | ---------------------------- | ------------------------------- | ------------------------------------- | ---------------------------------------------------------------------- |
| **按用户 (§4)**        | 每个登录用户，首次使用时。   | 每个用户，在其自己的帐户上。     | “已登录”（非匿名调用者）。            | 默认。任何具有登录 / 多个用户 / 未指定密钥所有权的应用程序。             |
| **管理员密钥 (§9)**     | 一个管理员，一次。           | 应用程序运营商（一个帐户）。     | `extension-authorization` `#admin` 角色。 | 应用程序运营商明确为所有用户资助 OpenAI 使用。                         |
| **完全匿名 (§10)**     | 任何访客。                  | 粘贴最新密钥的人。             | 无。                                  | 规范明确说明没有登录（演示、无身份验证模型的团队内部工具）。             |

所有三个变体在机械上相似 — 它们都将 `sk-...` 存储在 canister 状态中，并且它们都必须遵守 `is_replicated = ?false` (§3) 和下面的无获取器 / 无日志不变量。**默认为按用户。** 当规范明确说明运营商付费时（免费层、免费增值、固定配额嵌入到应用程序中）切换到管理员密钥。仅在规范明确说明完全没有登录时切换到完全匿名。

### 密钥的安全属性（两个变体）

- 长寿命，无过期。每次调用都花费整个 OpenAI 帐户余额。
- 无作用域权限 — 没有类似“tweet.read”的缩小。每个密钥都有完整的帐户访问权限。
- OpenAI 按密钥每分钟限制速率；将密钥视为计费凭证，而不是会话令牌。
- **永远不会通过任何 `query` 或 `shared` 函数返回。** 从不记录。从不发送到前端。从不放在另一个端点可以读取的稳定变量中。

### 存储密钥

持有者**永远不会离开 canister**。前端只学习密钥是否配置（一个 `Bool`），永远不会知道密钥本身。即使调用者询问自己的密钥 — 前端没有合法理由读取它，任何返回 `?Text` 的获取器都会导致泄露（浏览器内存、错误提示、遥测、截图、支持工单）。

- **按用户（默认）：** 一个 `Map<Principal, Text>`，由调用者键控。暴露恰好两个端点 — `setMyOpenAIApiKey(key) : async ()` 和 `isMyOpenAIConfigured : async Bool` — 都基于 `not caller.isAnonymous()`。可选地，还 `clearMyOpenAIApiKey : async ()`。**不要添加 `getMyOpenAIApiKey` / `getApiKey` / 任何其他返回密钥的读取端点，即使是调用者自己的密钥。** 从不迭代映射，除非在调用者自己的调用范围内。
- **管理员密钥：** 一个单一的 `var openAIApiKey : ?Text = null`（无获取器）。暴露恰好两个端点 — 仅管理员 `setOpenAIApiKey(key)` 和无身份验证 `isOpenAIConfigured : query () -> async Bool`。**相同规则：永远没有 `getOpenAIApiKey` / `getApiKey` 端点。**
- **完全匿名：** 与管理员密钥相同（单个 `var openAIApiKey : ?Text`，`isOpenAIConfigured : Bool` 查询，无获取器），但 `setOpenAIApiKey` 是无身份验证的 — 任何访客都可以覆盖密钥。相同的无获取器 / 无日志不变量适用。仅在规范明确说明没有登录时使用。

## 3. `is_replicated = ?false` 是必需的

这是此技能中最重要的代码行。三个原因，按优先级排序：

1. **安全性。** 复制的 HTTP 出站调用会从子网中的每个节点通过独立的 TLS 连接发送请求。每个连接看到 `Authorization: Bearer sk-...` 标头。任何连接中的泄露持有者都会危及整个 OpenAI 帐户。
2. **计费。** 复制出站调用产生 N 个并行 API 调用。OpenAI 收到 N 倍。IC 也收取 ~13× 非复制出站调用的周期。
3. **确定性。** LLM 响应是采样的（模型以概率方式发出标记；即使 `temperature = 0` 在规模上也有标记化竞争）。复制共识会差异响应正文并失败；非复制出站调用绕过此共识。

→ 始终：`is_replicated = ?false` 在 `Config` 上。

自 0.3.0 以来，包本身发送了该默认值 — `defaultConfig.is_replicated` 是 `?false`，因此 `{ defaultConfig with auth = … }` 已经安全。§4 中的显式赋值保持为安全措施：它将要求在调用点可见，并且仍然可以保护从 `defaultConfig` 而不是从头开始构建的 `Config`。

## 4. 标准布局

这是默认形状。每个登录用户粘贴自己的 OpenAI 密钥；canister 按调用者存储它；每个聊天调用使用调用者自己的密钥。不需要 `extension-authorization` 管理员门控 — 唯一的门控是“已登录”。

示例跨越三个文件：

- `src/backend/main.mo` — 演员状态 + `include`s 仅。
- `src/backend/mixins/openai-chat.mo` — 按用户端点 (`isMyOpenAIConfigured`, `setMyOpenAIApiKey`, `clearMyOpenAIApiKey`, `chat`)。
- `src/backend/lib/openai.mo` — OpenAI SDK 粘合（Config 构建器 + 聊天往返）。§9 不变。

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinOpenAIChat "mixins/openai-chat";

actor {
  // 来自 extension-authorization 的授权管道。按用户变体不使用 `#admin` 角色门控，但 `MixinAuthorization` 是连接
  // 后端和前端登录 / 调用者管道的东西（参见 SKILL
  // §"Prerequisite"）。
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 按用户 OpenAI 密钥。除了调用者外，从不迭代。
  let openAIKeys : Map.Map<Principal, Text>;
  include MixinOpenAIChat(openAIKeys);
};
```

迁移链头部：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    openAIKeys : Map.Map<Principal, Text>;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      openAIKeys = Map.empty<Principal, Text>();
    };
  };
};
```

```motoko filepath=src/backend/mixins/openai-chat.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import OpenAI "../lib/openai";

// 按用户 OpenAI 密钥端点。由 `main.mo` 通过 `include` 挂载。
// 与 `MixinAuthorization` 配对，以在已登录的调用者上门控每个端点。
mixin (openAIKeys : Map.Map<Principal, Text>) {
  public query ({ caller }) func isMyOpenAIConfigured() : async Bool {
    openAIKeys.containsKey(caller);
  };

  public shared ({ caller }) func setMyOpenAIApiKey(key : Text) : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("登录以使用此功能");
    };
    openAIKeys.add(caller, key);
  };

  public shared ({ caller }) func clearMyOpenAIApiKey() : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("登录以使用此功能");
    };
    openAIKeys.remove(caller);
  };

  public shared ({ caller }) func chat(prompt : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("登录以使用此功能");
    };
    let ?key = openAIKeys.get(caller) else {
      Runtime.trap("首先设置您的 OpenAI API 密钥");
    };
    await* OpenAI.runChatCompletion(OpenAI.configForKey(key), prompt);
  };
};
```

```motoko filepath=src/backend/lib/openai.mo
import { defaultConfig; type Config } "mo:openai-client/Config";
import ChatApi "mo:openai-client/Apis/ChatApi";
import CreateChatCompletionRequest "mo:openai-client/Models/CreateChatCompletionRequest";
import ChatCompletionRequestUserMessage "mo:openai-client/Models/ChatCompletionRequestUserMessage";
import Runtime "mo:core/Runtime";

module {
  // 构建一个绑定到单个持有者的 Config。`is_replicated = ?false` 是
  // 必需的 — 参见 §3：安全性、计费和非确定性都迫使它。
  // 0.3.0 还在 `defaultConfig` 中默认它；在这里重申它是故意的。
  public func configForKey(key : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer key;
      is_replicated = ?false;
    };
  };

  public func runChatCompletion(config : Config, prompt : Text) : async* Text {
    let userMessage = ChatCompletionRequestUserMessage.JSON.init({
      content = #string(prompt);
      role = #user;
    });

    // `JSON.init` 默认每个可选为 `null` — 不要手动列出它们。
    // 使用记录更新语法层可选：
    //   { CreateChatCompletionRequest.JSON.init {...} with temperature = ?0.7 }
    let req = CreateChatCompletionRequest.JSON.init({
      messages = [#user(userMessage)];
      model = "gpt-4o-mini"; // ModelIdsShared = Text — 任何 OpenAI 模型 ID
    });

    let resp = await* ChatApi.createChatCompletion(config, req);

    if (resp.choices.size() == 0) {
      Runtime.trap("OpenAI 返回了没有选择");
    };
    resp.choices[0].message.content
      ?? Runtime.trap("OpenAI 返回了没有文本内容（拒绝或工具调用）");
  };
};
```

### 按用户特定不变量

- **按 `caller` 键映射，而不是按用户提供的 ID 键。** 前端提供的 `Text` 用户 ID 可能会被欺骗；来自 `shared ({ caller })` 的 `Principal` 则不能。
- **任何端点都不会返回密钥——不是另一个用户的，甚至不是调用者自己的。** 前端通过 `isMyOpenAIConfigured : async Bool` 学习“是否配置？是/否”，除此之外不再需要更多信息。具体来说：不要生成 `getMyOpenAIApiKey`、`getApiKey`、`myApiKey` 或任何其他共享/查询函数，其返回类型为 `?Text` / `Text`。内部读取映射（在 `chat`、`configFor` 等内部）使用 `openAIKeys.get(caller)` 并且永远不会超出可器边界。迭代器或返回键的端点会泄露每个用户的 bearer。
- **当密钥缺失时，应干净地捕获异常。** 使用 `Runtime.trap("Set your OpenAI API key first")`（或返回一个类型化的错误）——消息标识了缺失的是谁的密钥，而不会泄露密钥本身。
- **匿名调用者不得存储密钥。** `caller.isAnonymous()` 在任何 `openAIKeys.add` 之前就会短路——否则，通过 `2vxsx-fae` 读取可器的每个人都会共享一个密钥槽。
- **`stable var` / 迁移。** `Map<Principal, Text>` 与任何其他可器字段一样存储在稳定内存中；在升级时，决定是否保留、轮换或丢弃密钥。默认（保留）对于几乎所有的应用程序都是正确的。如果你确实需要轮换，则丢弃整个映射——永远不要部分轮换。

## 5. 两种调用形式——函数形式与套件形式

每个 Apis 模块都提供：

- **函数形式**（在 §4 中使用）：`ChatApi.createChatCompletion(config, req) : async* T`。注意 `async*`——调用站点使用 `await*`。这是 `shared` 可器方法中常见的情况，它们会自行处理自己的配置。
- **套件形式**：`let api = ChatApi(config); api.createChatCompletion(req) : async T`。注意 `async`，而不是 `async*`。当单个 `shared` 方法进行多个 OpenAI 调用，并且你希望绑定一次配置时，这很有用。用较少的配置线程样板代码换取一个额外的 `await` 边界。

这两种形式可以互换；选择对调用者来说读起来更清晰的。不要在同一个 `shared` 身体内部混合它们。

## 6. 可用的 API 表面

什么有效是**按操作，而不是按模块**：大多数模块混合了有效和无效的调用，所以请阅读操作，而不是模块名称。经验法则是**JSON 输入，JSON 输出**——当操作请求体是 JSON，并且成功响应是 JSON 模型时，该操作才有效。

| 操作 | 它的作用 |
| --- | --- |
| `ChatApi.createChatCompletion` | 聊天 / GPT-4o / GPT-4 / GPT-3.5——95% 的情况。将 `tool_choice` 和 `function_call` 设置为 `null`。 |
| `ChatApi.getChatCompletion` / `listChatCompletions` / `getChatCompletionMessages` / `updateChatCompletion` / `deleteChatCompletion` | 存储完成管理。 |
| `ImagesApi.createImage` | DALL·E / `gpt-image-1` 文本到图像（JSON 响应：`url` 或 `b64_json`）。 |
| `ModelsApi.listModels` / `retrieveModel` / `deleteModel` | 发现和管理模型。 |
| `FilesApi.listFiles` / `retrieveFile` / `deleteFile` | 文件元数据和删除。 |

`AudioApi`、`EmbeddingsApi`、`ModerationsApi` 或 `CompletionsApi` 中的任何内容都不起作用，并且 `FilesApi`/`ImagesApi` 仅适用于上面列出的操作。

### 无效的操作——永远不要将构建路由到这些操作

生成器为其通用 `oneOf` 模式填充了转换器（分支混合原始类型、数组和数组数组不会通过一个模块分发），所以 `toCandidValue` / `fromCandidValue` 是 `Runtime.unreachable()`。这些文件可以类型检查，这就是为什么它们会提供；在第一个真实请求时触发陷阱。

两个不同的原因。**填充的通用 `oneOf` 转换器**——`toCandidValue` / `fromCandidValue` 是 `Runtime.unreachable()`，所以调用会陷阱：

| 操作 | 原因 | 可达性 |
| --- | --- | --- |
| `EmbeddingsApi.createEmbedding` | `input : CreateEmbeddingRequestInput` 是 **必需** 的 | 总是 |
| `ModerationsApi.createModeration` | `input : CreateModerationRequestInput` 是 **必需** 的 | 总是 |
| `CompletionsApi.createCompletion` | `prompt : CreateCompletionRequestPrompt` | 只要 `prompt` 被设置 |
| `ChatApi` 与 `tool_choice` 或 `function_call` | 两者都是填充的 `oneOf` 模型 | 只有当你设置它们——将它们设置为 `null` |

**没有多部分支持**——这些操作将文件作为 `Blob` 参数传递，然后发送 `body = null` 并带有 JSON 内容类型，所以上传会静默地变为空。它们不会触发陷阱；它们在 API 处失败：

| 操作 |
| --- |
| `FilesApi.createFile` |
| `ImagesApi.createImageEdit` / `createImageVariation` |
| `AudioApi.createTranscription` / `createTranslation`（还填充了响应解码） |

**非 JSON 响应体强制通过 JSON 解码器**——成功路径始终是 `Text.decodeUtf8` → `JSON.toCandid` → 期望原始类型，这在端点返回字节或原始文件内容时无法工作。这些在每次调用时都会抛出 `Error.reject`：

| 操作 | 它实际返回的内容 |
| --- | --- |
| `AudioApi.createSpeech` | MP3/Opus/AAC 音频——不是有效的 UTF-8，更不用说 JSON 了 |
| `FilesApi.downloadFile` | 原始文件内容（微调文件为 JSONL），不是 JSON 字符串 |

这两种失败都不是回归：**0.2.5 的行为完全相同**——相同的填充、相同的 `body = null`——所以这些在发布的版本中从未起作用。0.3.0 改变的是这一部分现在说明了这一点。

`ChatApi` 本身是安全的，因为这两个字段是可选的，序列化器会跳过 `null`（§4 将它们排除在外）。如果规范需要嵌入、审核、遗留完成或语音到文本，**请声明它们在 0.3.0 中不可用**，并在 [`caffeinelabs/skills-internal`](https://github.com/caffeinelabs/skills-internal) 上提出问题。不要替代手工编写的 `ic.http_request`，也不要“绕过”陷阱——在调用站点没有解决方法。

导入遵循以下模式：

```mo:openai-client
import ChatApi "mo:openai-client/Apis/ChatApi";
import { defaultConfig } "mo:openai-client/Config";
import CreateChatCompletionRequest "mo:openai-client/Models/CreateChatCompletionRequest";
```

**`openai-client@0.3.0` 未提供**：助手、实时、响应、批量、审核日志、评估、微调、邀请、项目、上传、使用情况、用户、向量存储。如果构建规范需要其中任何一个，请在 [`caffeinelabs/skills-internal`](https://github.com/caffeinelabs/skills-internal) 上提出问题——不要用手工编写的 `ic.http_request` 来掩盖它。

## 7. 循环和响应大小

`defaultConfig.cycles = 30_000_000_000`——大约 0.04 美元，按 4 美元/每周期计算。足以进行典型的聊天完成。对于：

- 长完成（`max_completion_tokens > 2000`）：设置 `cycles = 100_000_000_000`。
- 图像生成：响应可能超过 1 MiB，设置 `max_response_bytes = ?2_000_000` 和 `cycles = 100_000_000_000`。

## 8. 会咬你的事情

- **`is_replicated = ?false`**——参见 §3。这不是可选的。
- **不要暴露 API 密钥。** 永远不要从任何 `query` / `shared` 方法返回它，永远不要记录它，永远不要把它放在任何非密钥所有者可读取的数据结构中。在每用户默认（§4）中，`openAIKeys` 的唯一合法读取是 `openAIKeys.get(caller)` 对调用者的调用本身；在管理员密钥变体（§9）中，`openAIApiKey` 的唯一合法读取是在 `chat` 中的解构，它将密钥传递给 `OpenAI.configForKey`。没有迭代器，没有调试打印，没有管理员列表端点。
- **永远不要有 `getApiKey` / `getMyOpenAIApiKey` 端点——即使是返回调用者自己的密钥。** 这是前端“需要知道用户是否设置了密钥”时最常见的错误：代理会调用 `getApiKey() : async ?Text`，将 bearer 返回给 React 应用，并且一个 `console.log` / 错误提示 / Sentry 面包屑 / 截图会泄露计费凭证。前端已经从 `isMyOpenAIConfigured : async Bool`（每用户）或 `isOpenAIConfigured : async Bool`（管理员）中获得了它需要的一切——从布尔值中渲染空状态并停止。如果 UI 模拟显示了保存的密钥（掩码或否则），请从模拟中删除保存的密钥字段；后端不能——而且必须不能——提供它。
- **不要手工列出每个可选的 null。** 使用 `CreateChatCompletionRequest.JSON.init({ messages; model })` 并使用记录更新层可选——包为每个多可选模型生成一个 `JSON.init` 辅助函数。（这与 `x-client@0.1.2` 不同，它缺少 `JSON.init` 并强制列出所有 `null` 值站点。不要反射性地复制那种模式。）
- **不要自己编写 JSON。** 绑定已经通过 serde-core / Candid 跳转序列化请求体并解析响应。如果你需要一个绑定没有暴露的字段，请在 `skills-internal` 上提出问题，而不是手动解析——Motoko 的 JSON 支持太薄弱，无法使其可靠。
- **流式传输不受支持。** `stream = ?true` 将不会工作——IC 管理可器 `http_request` 原子地返回完整的响应体，没有分块 / SSE 原始类型。将 `stream` 设置为 `null`。
- **速率限制。** OpenAI 按密钥每分钟（RPM）和每天（RPD）进行速率限制。复制出调用会乘以子网大小 RPM——这是 `is_replicated = ?false` 的另一个原因。在 HTTP 429 时减慢速度。
- **`resp.choices[0].message.content` 是 `?Text`，而不是 `Text`。** 拒绝、工具调用或仅音频响应会将其设置为 `null`。始终 `switch` 它；永远不要在索引数组之前不先检查 `choices.size() > 0`。
- **`ChatCompletionRequestUserMessageContent` 是一个变体**——`#string(text)` 用于纯文本，`#array([...])` 用于多模式（文本 + 图像 URL 部分）。对于常见情况使用 `#string`。
- **`ModelIdsShared = Text`**——它是一个扁平字符串别名，而不是变体。直接传递 `"gpt-4o-mini"` 等。
- **前端永远不会持有密钥。** React 应用调用后端 `chat(prompt)`（或聊天端点的任何其他名称），并返回答案。设置 UI 调用 `setMyOpenAIApiKey(key)`（每用户默认）或 `setOpenAIApiKey(key)`（管理员密钥变体）。没有 SDK 或前端 npm 包——可器就是 OpenAI 客户端。

## 9. 变体：管理员密钥

仅在规范明确将 OpenAI 账单放在操作员身上时使用此变体。具体来说：

- 单个 OpenAI 账户资助所有内容（典型的 SaaS）。
- 应用提供免费/免费增值层，操作员为其付费。
- 应用在可器内部实施其自己的每用户配额，并单独向用户计费。

在其他所有情况下——尤其是每当规范提到登录、多个用户或未说明谁付费时——使用 §4 中的每用户默认。管理员密钥变体只有在“操作员付费”是一个故意、声明的选择时才有意义。

相对于 §4 的唯一规则是：单个 `?Text` 替换了 `Map<Principal, Text>`，并且设置器通过 [`extension-authorization`](../extension-authorization/SKILL.md) 中的 `#admin` 角色进行限制，而不是“任何已登录的调用者”。可器和混入文件是新的；§4 中的 `src/backend/lib/openai.mo` 保持不变。这个 `main.mo` 替换了 §4 的，其链头提供 `AccessControl.initState()` 和 `{ var value = null }`。

<!-- motoko-check:skip -->
```motoko
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinOpenAIAdminChat "mixins/openai-admin-chat";

actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 管理员设置的 OpenAI bearer 密钥。用 `{ var value : ?Text }` 包装，以便混入可以修改它。
  let openAIApiKey : { var value : ?Text };
  include MixinOpenAIAdminChat(accessControlState, openAIApiKey);
};
```

```motoko filepath=src/backend/mixins/openai-admin-chat.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";
import OpenAI "../lib/openai";

// 管理员保护的 OpenAI 密钥端点。通过 `main.mo` 的 `include` 挂载。
// 与 `MixinAuthorization` 配对以支持角色检查。
mixin (
  accessControlState : AccessControl.AccessControlState,
  openAIApiKey : { var value : ?Text },
) {
  public query func isOpenAIConfigured() : async Bool {
    openAIApiKey.value != null;
  };

  public shared ({ caller }) func setOpenAIApiKey(key : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set the OpenAI API key");
    };
    openAIApiKey.value := ?key;
  };

  public shared ({ caller }) func chat(prompt : Text) : async Text {
    if (not AccessControl.hasPermission(accessControlState, caller, #user)) {
      Runtime.trap("Unauthorized");
    };
    let ?key = openAIApiKey.value else Runtime.trap("OpenAI is not configured");
    await* OpenAI.runChatCompletion(OpenAI.configForKey(key), prompt);
  };
};
```

### 管理员密钥特定不变量

- **单个 `?Text` 槽 (`{ var value : ?Text = null }`)，没有获取器。** 该槽仅被 `setOpenAIApiKey` 和 `chat`（它通过 `OpenAI.configForKey` 传递它）触及。永远不要暴露 `getOpenAIApiKey`——`isOpenAIConfigured` 是唯一的外部读取，它返回 `Bool`。
- **设置器必须通过 `extension-authorization` 进行 `#admin` 保护。** 非仅匿名门控是不够的——任何已登录的用户都可能覆盖操作员的计费密钥。这是变体的整个原因依赖于 `extension-authorization`。
- **当密钥未设置时，使用 `"OpenAI is not configured"` 捕获异常。** 这种措辞与 `isOpenAIConfigured` 配对，以便前端可以渲染“请询问您的管理员设置 OpenAI API 密钥”的空状态。
- **每次调用都构建一个新的 `Config`。** `chat` 读取 `openAIApiKey` 并在每次调用时通过 `OpenAI.configForKey(key)` 传递它；不要在可器级别缓存 `Config` 值。Bearer 允许在生命周期中途通过 `setOpenAIApiKey` 旋转，缓存的 `Config` 会静默地保持旧密钥。

## 10. 变体：完全匿名

仅在规范明确声明完全没有登录时使用（单用户演示、团队内部工具、一次性沙盒）。机制上与 §9 相同——单个 `?Text` 密钥，没有获取器，`isOpenAIConfigured` 查询——但移除了认证导入 / `#admin` 门控；任何访客都可以覆盖密钥。

取 §9 的两个文件并应用这些差异（§4 的 `lib/openai.mo` 辅助函数保持不变）：

在 `src/backend/main.mo` 中：

- 删除对 `mo:caffeineai-authorization/access-control` 和 `mo:caffeineai-authorization/MixinAuthorization` 的导入。
- 从可器体中删除 `let accessControlState : AccessControl.AccessControlState;` 和 `include MixinAuthorization(accessControlState, null);`（并从迁移链头中删除 `accessControlState`）。
- 从混入 `include` 中删除 `accessControlState` 参数，留下 `include MixinOpenAIAdminChat(openAIApiKey);`。

在 `src/backend/mixins/openai-admin-chat.mo` 中：

- 删除 `AccessControl` 导入和混入参数 `accessControlState`。
- 将受保护的设置器替换为非认证形式：

  ```
  public shared ({ caller }) func setOpenAIApiKey(key : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set the OpenAI API key");
    };
    openAIApiKey.value := ?key;
  };
  ```

  为：

  ```
  public func setOpenAIApiKey(key : Text) : async () {
    openAIApiKey.value := ?key;
  };
  ```

- 删除 `chat` 顶部的 `#user` 权限检查。`chat`、`isOpenAIConfigured` 和 `OpenAI.configForKey(...)` 调用与 §9 完全相同。

### 匿名特定不变量

- **不导入 `extension-authorization`。** 这种变体完全跳过它。
- **密钥是共享且可被任何人替换的。** 这是这种变体的明确权衡；只有在规范接受这一点时才选择它。
- **相同的无获取器 / 无日志规则适用。** `openAIApiKey` 仅在 `chat` 内部读取（然后传递给 `OpenAI.configForKey`），任何端点都不会返回它。
- **每次调用构建一个全新的 `Config`** — 与 §9 的理由相同。

# 前端

使用此技能的每个构建都必须提供：

1. **一个用于粘贴密钥的设置界面 — 永远。** 每个变体。部署的 canister 在粘贴密钥之前会拒绝每个聊天调用。如果没有设置页面，聊天机器人界面会加载，但每个问题都会捕获“OpenAI 未配置” / “请先设置您的 OpenAI API 密钥” — 对最终用户来说应用程序看起来是损坏的。
2. **一个登录流程 — 仅适用于每个用户和管理员密钥变体。** 这些变体在 `not caller.isAnonymous()`（每个用户）或 `#admin` 角色上（管理员密钥）上封锁每个有意义的端点；两者都需要非匿名调用者。登录流程本身由 [`extension-authorization`](../extension-authorization/SKILL.md) 提供：`useInternetIdentity`，登录/注销按钮，`useActor` 接口将认证身份注入到每个后端调用中。如果构建还没有一个登录界面，将其作为同一任务图的一部分进行规划。完全匿名变体（§10）明确跳过此界面 — 没有登录。

选择与后端变体匹配的 UI 形状。**默认为变体 A（每个用户）**，除非规范明确将 OpenAI 费用放在操作员身上（见 §9）或明确说明没有登录（见 §10）。

## 变体 A：每个用户的密钥（匹配 §4 — 默认）

一个仅由登录控制的每个用户的“您的 API 密钥”面板。

1. 绑定到 `setMyOpenAIApiKey(key)` 的密码输入。按回车提交；成功后清除输入。
2. 由 `isMyOpenAIConfigured()`（返回 `Bool`）驱动的状态指示器。显示“已配置” / “未配置” — 永远不显示密钥本身，永远不暴露返回它的获取器。
3. 可选的“清除我的密钥”按钮绑定到 `clearMyOpenAIApiKey()`，供希望从 canister 中撤销其密钥的用户使用。
4. 当 `isMyOpenAIConfigured()` 为 `false` 时显示一次性引导提示 — 例如，在聊天页面上显示内联空状态，链接到 `/settings/openai`。没有此提示，用户会遇到“请先设置您的 OpenAI API 密钥”而没有明显的下一步。

建议的路由布局：

```
/                   →  聊天 UI（任何已登录用户；无密钥时显示空状态）
/settings/openai    →  个人 API 密钥面板（任何已登录用户）
```

## 变体 B：管理员密钥（匹配 §9）

一个由管理员控制的单一全局设置页面。

1. 绑定到 `setOpenAIApiKey(key)` 的密码输入。按回车提交；成功后清除输入。
2. 由 `isOpenAIConfigured()`（返回 `Bool`）驱动的状态指示器。与变体 A 相同的无显示不变量。
3. 通过 [`extension-authorization`](../extension-authorization/SKILL.md) 的 `isCallerAdmin` 查询隐藏页面，非管理员不应在导航中看到设置链接，更不用说页面了。通过路由器的保护模式（TanStack Router `beforeLoad`，React Router `loader` 等）绑定管理员专有路由；不要仅依赖隐藏链接。
4. 当 `isOpenAIConfigured()` 为 `false` 时，在聊天页面上显示“请向您的管理员设置 OpenAI API 密钥”的空状态 — 非管理员无法自行修复，需要知道谁可以。

建议的路由布局：

```
/                   →  聊天 UI（任何已登录用户）
/settings/openai    →  管理员专有 API 密钥设置页面
```

## 变体 C：完全匿名（匹配 §10）

一个任何访客都可以访问的单一全局设置页面 — 无认证网关。

1. 绑定到 `setOpenAIApiKey(key)` 的密码输入。按回车提交；成功后清除输入。
2. 由 `isOpenAIConfigured()`（返回 `Bool`）驱动的状态指示器。与变体 A 和 B 相同的无显示不变量。
3. 无路由保护，无 `useInternetIdentity`，无登录按钮 — 这种变体没有认证模型。
4. 当 `isOpenAIConfigured()` 为 `false` 时，在聊天页面上显示“粘贴 OpenAI API 密钥以开始使用”的空状态。

建议的路由布局：

```
/                   →  聊天 UI（任何访客；无密钥时显示空状态）
/settings/openai    →  API 密钥面板（任何访客）
```

## 所有变体的公共部分

- 聊天 UI 本身非常简单且跨变体相同：一个文本区域，一个提交按钮，一个绑定到后端聊天端点的消息列表。没有客户端 OpenAI SDK，没有密钥处理，没有流协议逻辑 — canister 调解一切。
- **变体 A 和 B 需要登录，变体 C 跳过登录。** 对于 A 和 B，通过 `extension-authorization` 的认证保护（`useInternetIdentity` + 当 `!isAuthenticated` 时重定向）连接聊天和设置路由；匿名调用者必须在聊天或设置 UI 渲染之前遇到“请登录”的障碍，否则每个后端调用都会捕获。对于 C，不需要保护，因为没有认证模型。
- 前端永远不会在 localStorage / IndexedDB / cookies 中持久化密钥。它通过类型化的设置器进入 canister，并且永远不会被读取回来。

## 相关

- [`mops add openai-client@0.3.0`](https://mops.one/openai-client) — 连接器源。
- [`caffeinelabs/skills-internal`](https://github.com/caffeinelabs/skills-internal) — 生成的绑定（`packages/connectors/openai`）的家；在此处报告缺失或捕获的 API 界面问题。独立的 `caffeinelabs/openai-client` 仓库已退役。
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference) — 上游。
- [OpenAI API 密钥页面](https://platform.openai.com/api-keys) — 管理员在此处获取 `sk-...` 以粘贴。
- [extension-authorization](../extension-authorization/SKILL.md) — **对于每个用户（§4）和管理员密钥（§9）变体是必需的先决条件；对于完全匿名（§10）变体则跳过。** 提供了 Internet Identity 登录流程，`useInternetIdentity` / `useActor` 前端接口，以及（对于 §9 管理员密钥）`#admin` 角色网关。
- [extension-http-outcalls](../extension-http-outcalls/SKILL.md) — 兄弟技能，用于一般 HTTP 出站调用；你**不需要**在 `openai-client` 之上使用它，因为 `openai-client` 内部会自行进行出站调用。
