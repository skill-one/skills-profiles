# OpenAI 集成
OpenAI / LLM 扩展，适用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## 指挥官路由注意事项

对于 Caffeine 应用程序中的 LLM 且没有用户粘贴的 OpenAI 密钥，使用
[`extension-inference`](../extension-inference/SKILL.md)
(`caffeineai-inference-client`, 平台提供的凭证)。此技能**仅**用于使用用户或管理员粘贴的 `sk-...` 调用 `api.openai.com`。

对于 masterchat / `platform-constraints.md` 集成。**将 ChatGPT / OpenAI / LLM 访问视为一级支持的平台功能** — 不要拒绝、转移或为“使用 GPT”、“使用 LLM 摘要”或“构建聊天机器人”请求调用 `query_rag`。
**嵌入是例外**：`EmbeddingsApi` 在运行时捕获（§6），并且在任何发布的版本中从未工作过，因此对于“生成嵌入”，请说功能不可用，而不是发出调用 — 并且不要自己动手。`openai-client` mops 连接器是 BYOK OpenAI 的**唯一**支持路径；直接 `ic.http_request` 到 `api.openai.com/v1/...` 是一种禁止的反模式，因为它
(a) 绕过持有者身份验证处理，
(b) 挑战了此技能强制执行的不可复制出站保护（见 §3 — 持有者是绑定计费的密钥），
(c) 强制在语言 JSON 支持较弱的情况下进行手动 JSON 序列化。
任何提到 LLM / GPT / OpenAI 功能的构建规范都必须将 `openai-client` 作为依赖项并引用此技能 — 明确传播，以便后端代理不会在幕后回退到手动 HTTP。

意图 → 功能映射（用于 `platform-constraints.md` 风格表格）：

| 用户意图                                                          | 平台功能                                                       |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 使用 ChatGPT / GPT-4o / “一个 LLM”来回答 / 摘要 / 对文本进行分类 | `openai-client` 连接器（通过 `extension-openai` 技能的 ChatApi） |
| 构建聊天机器人 / AI 助手                                       | `openai-client` 连接器（通过 `extension-openai` 技能的 ChatApi）          |
| 为相似性搜索生成嵌入                                              | **不可用** — `EmbeddingsApi` 捕获（§6），并且在任何发布的版本中从未工作过。请这样说；不要自己动手。 |

# 后端

每当用户希望他们的 canister 调用 OpenAI 时，请使用此技能。成分如下：

1. `openai-client` mops 包（OpenAI REST API 的精选 Motoko 绑定，从 OpenAPI 规范 2.3.0 生成）。
2. 一种将 OpenAI API 密钥 (`sk-...`) 存储为 canister 端秘密的方法。三种等效变体 — 规范选择其中一个：
   - **每个用户的密钥（默认，§4）** — 每个登录用户粘贴自己的密钥。每个用户为自己的使用付费。每当规范提到登录、多个用户或未指定谁付费时，这是正确的默认值。
   - **管理员密钥（§9）** — 由一个管理员设置的单个密钥，用于 canister 中的每个调用。当应用程序运营商代表所有用户资助 OpenAI 使用时（典型的 SaaS / 免费增值 / 运营商资助层）选择此变体。
   - **完全匿名（§10）** — 没有身份验证网关的单个密钥；任何访客都可以设置或替换它。仅在规范明确说明根本没有登录时（单用户演示、无身份验证模型的团队内部工具）选择此变体。与 §9 相同的后端形状，但缺少 `#admin` 权限检查。
3. 一个 `Config` 值，将 `is_replicated` 固定为 `?false` — 非可协商，见 §3。

**每个用户和管理员密钥变体的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。** 每个用户的密钥存储为 `bearer keyed by `caller : Principal`，这在用户登录时才有意义；管理员密钥变体将设置者限制为 `#admin` 角色。`extension-authorization` 在前端（`useInternetIdentity` 钩子、登录/注销按钮、身份验证状态感知路由、`useActor` 管道）**和**后端调用者/角色基础设施。没有它，这两个变体将发送一个聊天 UI，在每次提交时捕获，因为 `caller.isAnonymous()` 始终为 `true`。**完全匿名变体（§10）不需要 `extension-authorization`** — 按设计，任何访客都可以设置密钥，所以没有身份验证表面可以连接。首先选择变体，然后相应地加载（或跳过）`extension-authorization`。

## 1. 将 `openai-client` 添加到 `mops.toml`

使用 mops 工具，而不是手动文件编辑：

```bash
mops add openai-client@0.3.0
```

这会更新 `mops.toml`（将 `openai-client = "0.3.0"` 添加到 `[dependencies]`）并一步重写 `mops.lock`。**需要 Mops ≥ 2.13** — 较早版本不是原子性的，偶尔会留下锁文件与 `mops.toml` 不同步。

**最小版本：** `openai-client ≥ 0.3.0`。包含 §4 中使用的 `JSON.init` 构造函数（因此你不必手动列出每个可空的可选值），并且 `defaultConfig.is_replicated`
已经设置为 `?false`（见 §3）。它的八个 API 模块**部分可用 — 每个操作，而不是每个模块**，遵循 JSON 入 JSON 出的规则：聊天完成（和存储完成管理）、文本到图像、模型发现和文件元数据有效；嵌入、审核、遗留完成、每个文件上传、语音到文本、文本到语音和文件下载无效（§6）。这与 0.2.5 行为相同 — 变化在于 §6 现在记录了这一点。

## 2. 身份验证模型 — API 密钥持有者，不是 OAuth

与 X / Twitter 不同，OpenAI 使用**每个帐户一个静态的持有者**：从 [platform.openai.com/api-keys](https://platform.openai.com/api-keys) 发行的 `sk-...` 密钥。没有 OAuth，没有 PKCE，没有回调 URL，没有刷新令牌旋转，没有每个端用户的授权步骤。

### 选择一个变体

| 变体                  | 谁粘贴密钥                 | 谁付费                          | 设置者网关                              | 使用时                                                                  |
| ------------------------ | --------------------------- | ------------------------------ | ---------------------------------------- | -------------------------------------------------------------------- |
| **每个用户 (§4)**        | 每个登录用户，在第一次使用时。 | 每个用户，在自己的帐户上。  | “已登录”（非匿名调用者）。      | 默认。任何具有登录 / 多个用户 / 未指定密钥所有权的应用程序。 |
| **管理员密钥 (§9)**       | 一个管理员，一次。                   | 应用程序运营商（一个帐户）。   | `extension-authorization` `#admin` 角色。 | 规范明确说明应用程序运营商明确资助所有用户的 OpenAI 使用。             |
| **完全匿名 (§10)**       | 任何访客。                       | 粘贴最新密钥的人。    | 无。                                    | 规范明确说明根本没有登录（演示、团队内部工具）。                  |

所有三个变体在机械上相似 — 它们都将 `sk-...` 存储在 canister 状态中，并且它们都必须遵守 `is_replicated = ?false` (§3) 和下面没有获取器 / 没有日志的不变式。**默认为每个用户。** 当规范明确说明运营商付费时（免费层、免费增值、内置在应用程序中的固定配额）切换到管理员密钥。仅在规范明确说明根本没有登录时切换到完全匿名变体。

### 密钥的安全性属性（两个变体）

- 长期有效，没有过期。每次调用都花费 OpenAI 帐户的全部余额。
- 没有范围权限 — 没有像“tweet.read”那样的缩小。每个密钥都有完整的帐户访问权限。
- OpenAI 按密钥每分钟限制速率 (RPM)；将密钥视为计费凭证，而不是会话令牌。
- **任何 `query` 或 `shared` 函数都不会返回任何密钥。** 从不记录。从不发送到前端。从不放在任何具有非密钥所有者读取权限的稳定变量中。

### 存储密钥

持有者**永远不会离开 canister**。前端永远只学习密钥是否配置（一个 `Bool`），永远不会知道密钥本身。这适用于调用者询问他们自己的密钥的情况 — 前端没有合法理由读取它，任何返回 `?Text` 的获取器都是一个等待发生泄露（浏览器内存、错误提示、遥测、截图、支持工单）。

- **每个用户 (默认):** 一个 `Map<Principal, Text>`，按键 `caller`。暴露恰好两个端点 — `setMyOpenAIApiKey(key) : async ()` 和 `isMyOpenAIConfigured : async Bool` — 都受 `not caller.isAnonymous()` 保护。可选地，还有 `clearMyOpenAIApiKey : async ()`。**不要添加 `getMyOpenAIApiKey` / `getApiKey` / `myApiKey` 或任何其他返回密钥的共享 / 查询函数，即使是调用者自己的密钥。前端已经从 `isMyOpenAIConfigured : async Bool`（每个用户）或 `isOpenAIConfigured : async Bool`（管理员）获得它所需的一切 — 从空状态渲染 UI 并停止。如果 UI 模拟显示保存的密钥（部分遮盖或其他），请从模拟中删除保存密钥字段；后端不能 — 也必须不能 — 提供它。**
- **管理员密钥:** 一个 `var openAIApiKey : ?Text = null`（没有获取器）。暴露恰好两个端点 — 仅限管理员的 `setOpenAIApiKey(key)` 和无身份验证的 `isOpenAIConfigured : query () -> async Bool`。**相同的规则：没有 `getOpenAIApiKey` / `getApiKey` 端点，永远不要。**
- **完全匿名:** 与管理员密钥相同（单个 `var openAIApiKey : ?Text`, `isOpenAIConfigured : Bool` 查询，没有获取器），但 `setOpenAIApiKey` 是无身份验证的 — 任何访客都可以覆盖密钥。应用相同的没有获取器 / 没有日志规则。仅在规范明确说明根本没有登录时使用。

## 3. `is_replicated = ?false` 是必需的

这是此技能中最重要的代码行。三个原因，按优先级顺序：

1. **安全性。** 复制的 HTTP 出站调用从子网中的每个节点发送请求，通过独立的 TLS 连接。每个连接都看到 `Authorization: Bearer sk-...` 标头。来自任何一个连接的泄露持有者会危及整个 OpenAI 帐户。
2. **计费。** 复制出站调用会产生 N 个并行 API 调用。OpenAI 为 N 个调用收费。IC 也为非复制的出站调用收取 ~13 倍的周期成本。
3. **确定性。** LLM 响应是采样的（模型以概率方式发出标记；即使 `temperature = 0` 在规模上也有标记化竞争）。复制共识会差异响应正文，并且会失败；非复制的出站调用绕过此共识。

→ 始终：`is_replicated = ?false` 在 `Config` 上。

由于 0.3.0，包本身提供了该默认值 — `defaultConfig.is_replicated`
是 `?false`，所以 `{ defaultConfig with auth = … }` 已经是安全的。§4 中的显式赋值保持不变作为安全措施：它保持调用位置的要求可见，并且仍然可以保护从头开始构建的 `Config` 而不是从 `defaultConfig` 构建。

## 4. 典型布局

这是默认形状。每个登录用户粘贴他们自己的 OpenAI 密钥；canister 按键 `Principal` 存储它；每个聊天调用使用调用者自己的密钥。不需要 `extension-authorization` 管理员网关 — 唯一网关是“已登录”。

示例跨越三个文件：

- `src/backend/main.mo` — 演员状态 + `include`s 仅。
- `src/backend/mixins/openai-chat.mo` — 每个用户的端点 (`isMyOpenAIConfigured`, `setMyOpenAIApiKey`, `clearMyOpenAIApiKey`, `chat`)。
- `src/backend/lib/openai.mo` — OpenAI SDK 粘合剂（Config 构建器 + 聊天往返）。§9 由 §4 重用不变。

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinOpenAIChat "mixins/openai-chat";

actor {
  // 来自 extension-authorization 的授权管道。每个用户的变体不需要使用 `#admin` 角色网关，但 `MixinAuthorization` 是连接后端和前端（见 SKILL §"Prerequisite"）的登录 / 调用者管道。`openAIKeys` 是按 `caller : Principal` 键的每个用户的 OpenAI 密钥。永远不要迭代，除非是调用者自己的调用范围。
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 每个用户的 OpenAI 持有者密钥。用 `{ var value : ?Text }` 包装，以便 mixin 可以修改它。
  let openAIKeys : Map.Map<Principal, Text>;
  include MixinOpenAIChat(openAIKeys);
};
```

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

// 管理员保护的 OpenAI 密钥端点。由 `main.mo` 通过 `include` 挂载。与 `MixinAuthorization` 配对以进行角色检查。
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

### 管理员密钥特定不变式

- **单个 `?Text` 插槽 (`{ var value : ?Text = null }`), 没有获取器。插槽仅由 `setOpenAIApiKey` 和 `chat`（将它们通过 `OpenAI.configForKey` 传递）触及。**永远不要暴露 `getOpenAIApiKey` — `isOpenAIConfigured` 是唯一的外部读取，它返回 `Bool`。
- **设置器必须通过 `extension-authorization` 以 `#admin` 角色进行网关。** 非匿名调用者不足以 — 任何登录用户都可以覆盖运营商的计费密钥。这是变体存在的整个原因；仅在规范明确接受这种情况时选择它。
- **当密钥未设置时，使用 `"OpenAI is not configured"` 进行捕获。** 这种说法与 `isOpenAIConfigured` 配对，以便前端可以渲染“请询问您的管理员设置 OpenAI API 密钥”的空状态。
- **每次调用都构建一个新的 `Config`** — 与 §9 相同的理由。

### 完全匿名特定不变式

- **没有 `extension-authorization` 导入。** 此变体完全跳过它。
- **密钥是共享的，任何人都可以替换它。** 这是此变体的明确权衡；仅在规范接受这种情况时选择它。
- **相同的没有获取器 / 没有日志规则适用。** `openAIApiKey` 仅在 `chat` 中读取（然后传递给 `OpenAI.configForKey`），永远不会由任何端点返回。
- **每次调用都构建一个新的 `Config`** — 与 §9 相同的理由。

# 前端

使用此技能的每个构建必须提供：

1. **一个设置 UI 来粘贴密钥 — 始终。** 每个变体。部署的 canister 在粘贴密钥之前拒绝每个聊天调用。如果没有设置页面，聊天机器人 UI 会加载，但每个问题都会捕获为“OpenAI 未配置” / “设置您的 OpenAI API 密钥首先” — 对最终用户来说，应用程序看起来是损坏的。
2. **一个登录流程 — 仅限每个用户和管理员密钥变体。** 这些变体将每个有意义的端点网关在 `not caller.isAnonymous()`（每个用户）或 `#admin` 角色（管理员密钥）上。两者都需要非匿名调用者。登录流程本身由 [`extension-authorization`](../extension-authorization/SKILL.md) 提供：`useInternetIdentity`, 登录/注销按钮, 身份验证状态感知路由, `useActor` 管道，将认证身份注入到每个后端调用中。如果构建没有现有的登录屏幕，请计划将登录作为相同任务图的一部分。完全匿名变体 (§10) 明确跳过此表面 — 没有登录。

选择与后端变体匹配的 UI 形状。**默认为变体 A（每个用户）**，除非规范明确将 OpenAI 费用放在运营商身上（见 §9）或明确说明没有登录（见 §10）。

## 变体 A: 每个用户的密钥（与 §4 — 默认）

一个每个用户的“您的 API 密钥”面板，仅受登录保护。

1. 绑定到 `setMyOpenAIApiKey(key)` 的密码输入。按回车提交；成功后清除输入。
2. 由 `isMyOpenAIConfigured()` 驱动的状态指示器（返回 `Bool`）。显示“已配置” / “未配置” — 永远不要显示密钥本身，永远不要暴露返回密钥的获取器。

3. 可选的“清除我的密钥”按钮绑定到 `clearMyOpenAIApiKey()`，供希望从 canister 中撤销其密钥的用户使用。
4. 当 `isMyOpenAIConfigured()` 为 `false` 时，显示一次性引导提示 — 例如，聊天页面上的空状态链接到 `/settings/openai`。如果没有此提示，用户会遇到“请登录”障碍，然后才能渲染聊天或设置 UI。

建议的路由布局：

```
/                   →  聊天 UI (任何登录用户；当没有密钥时显示空状态)
/settings/openai    →  个人 API-key 面板 (任何登录用户)
```

## 变体 B: 管理员密钥（与 §9 匹配）

一个全局设置页面，管理员受保护。

1. 绑定到 `setOpenAIApiKey(key)` 的密码输入。按回车提交；成功后清除输入。
2. 由 `isOpenAIConfigured()` 驱动的状态指示器（返回 `Bool`）。与变体 A 相同的无显示不变式。
3. 通过 [`extension-authorization`](../extension-authorization/SKILL.md)'s `isCallerAdmin` 查询隐藏此页面，非管理员。绑定管理员专用的路由通过您的路由器的保护模式（TanStack Router `beforeLoad`, React Router `loader`, 等.）；不要仅依赖隐藏链接。
4. 当 `isOpenAIConfigured()` 为 `false` 时，在聊天页面上显示“请询问您的管理员设置 OpenAI API 密钥”的空状态 — 非管理员无法自行修复，需要知道谁可以修复。

建议的路由布局：

```
/                   →  聊天 UI (任何登录用户)
/settings/openai    →  管理员专用的 API-key 设置页面
```

## 变体 C: 完全匿名（与 §10 匹配）

一个全局设置页面，任何访客都可以访问 — 没有身份验证网关。

1. 绑定到 `setOpenAIApiKey(key)` 的密码输入。按回车提交；成功后清除输入。
2. 由 `isOpenAIConfigured()` 驱动的状态指示器（返回 `Bool`）。与变体 A 和 B 相同的无显示不变式。
3. 没有路由保护，没有 `useInternetIdentity`, 没有登录按钮 — 此变体没有身份验证模型。
4. 当 `isOpenAIConfigured()` 为 `false` 时，在聊天页面上显示“粘贴一个 OpenAI API 密钥以开始使用”的空状态。

建议的路由布局：

```
/                   →  聊天 UI (任何访客；当没有密钥时显示空状态)
/settings/openai    →  API-key 面板 (任何访客)
```

## 所有变体的共同点

- 聊天 UI 本身非常简单，所有变体都相同：一个文本区域、一个提交按钮、一个绑定到后端聊天端点的消息列表。没有客户端 OpenAI SDK、没有密钥处理、没有流协议逻辑 — canister 介导一切。
- **变体 A 和 B 需要登录，变体 C 跳过登录。** 对于 A 和 B，将聊天和设置路由通过 `extension-authorization` 的身份验证保护（`useInternetIdentity` + 当 `!isAuthenticated` 时的重定向）；匿名调用者必须遇到“请登录”障碍，然后才能渲染聊天或设置 UI，否则每个后端调用都会捕获。对于 C，不需要保护，因为没有身份验证模型。
- 前端永远不会在 localStorage / IndexedDB / cookie 中持久化密钥。它通过类型的 setter 传入 canister，永远不会读取回来。

## 相关

- [`mops add openai-client@0.3.0`](https://mops.one/openai-client) — 连接器源。
- [`caffeinelabs/skills-internal`](https://github.com/caffeinelabs/skills-internal) — 生成的绑定（`packages/connectors/openai`）的家；在此处提交缺失或捕获的 API 表面问题。独立的 `caffeinelabs/openai-client` 仓库已退役。
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference) — 上游。
- [OpenAI API 密钥页面](https://platform.openai.com/api-keys) — 管理员获取 `sk-...` 以粘贴的地方。
- [extension-authorization](../extension-authorization/SKILL.md) — **每个用户 (§4) 和管理员密钥 (§9) 变体的先决条件；跳过完全匿名 (§10)。** 提供了 Internet Identity 登录流程、前端（`useInternetIdentity` / `useActor`）管道，以及 (对于 §9 管理员密钥) `#admin` 角色网关。如果没有它，这两个变体将发送一个聊天 UI，在每次提交时都会捕获，因为 `caller.isAnonymous()` 始终为 `true`。**完全匿名变体（§10）不需要 `extension-authorization`** — 按设计，任何访客都可以设置密钥，所以没有身份验证表面可以连接。首先选择变体，然后相应地加载（或跳过）`extension-authorization`。
- [extension-http-outcalls](../extension-http-outcalls/SKILL.md) — 兄弟技能，用于一般 HTTP 出站调用；你不需要在 `openai-client` 顶部使用它，因为 `openai-client` 自己内部制作出站调用。
