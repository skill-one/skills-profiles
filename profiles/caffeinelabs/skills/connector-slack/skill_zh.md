# Slack 连接器（实验性）

从 Caffeine 容器向 Slack 工作区发送消息。

> ⚠️ **实验性 (`slack-client@0.1.0`)。** **已针对实时 Slack 进行验证：** 请求路径 — 一个真实的 `chat.postMessage` 发送（早期的查询与表单错误已解决；POST 参数在 `application/x-www-form-urlencoded` 正文内）。
> **在 0.1.0 中实现但尚未在实时环境中进行验证：** 成功响应解码（`{"ok":true,…}` → 成功模式）和 `{"ok":false}` 错误信封路由（参见 *已知限制* 了解每个的作用）。因此，响应端是代码完整的但未经证实 — `diagnostics` 已开启，因此解码失败会暴露原始 Slack 正文。在**一个实时运行确认解码成功回复**之前，不要将 Slack 作为完全支持的平台功能呈现；这个条件，而不是版本号，是决定因素。

## 协调器路由说明

在用户、规范或先前的任务提及 Slack、向频道发送消息或通知 Slack 工作区时加载此技能。生成的 `slack-client` 包是首选路径；原始 `ic.http_request` 到 `https://slack.com/api/*` 是反模式，它手动重新实现了身份验证、百分比编码和 JSON 解析。

意图 → 能力映射：

| 用户意图 | 能力 |
| --- | --- |
| 以应用程序身份向 Slack 频道发送消息 | `slack-client` `chatPostMessage` 使用机器人令牌（`xoxb-`） |
| 以命名人员的身份向 Slack 发送消息 | `slack-client` `chatPostMessage` 使用用户令牌（`xoxp-`） |

在生成代码之前，**向提示用户报告令牌选择**（机器人 vs 用户 — 参见 *身份验证模型* 获取单行规则和权衡）并告诉他们在哪里获取它。他们必须粘贴令牌才能继续，因此尽早暴露这一点可以避免应用程序在首次使用时卡住。

令牌是**人类必须去创建**的东西，因此当后端编译时构建并未完成。当应用程序本身告诉管理员如何获取令牌并给他们一个地方粘贴它时才完成 — 参见 *获取机器人令牌* 获取步骤，*请求的范围* 获取要勾选的内容，*寻址频道* 获取频道 ID，以及 *前端* 获取必须包含的页面。在完成消息中重复这些步骤；聊天既不会持续应用程序也不会持续管理员的记忆。

此生成代码的范围：消息核心家族 `chat`、`conversations`、`users`、`files`、`reactions` 和 `pins`（10 个 API 模块）— 参见 *可用 API 表面* 获取每个模块的细分。
其他 Slack 方法在规范重新生成之前暂不受范围限制。

## 身份验证模型 — 机器人令牌（`xoxb-`）或用户令牌（`xoxp-`）

两者都是担保证书，客户端将它们视为相同，但它们在工作区看到的操作者不同。**在编写代码之前询问提示用户他们想要哪一个，并说明权衡** — 回答会改变他们的应用程序在 Slack 中的外观，并且无法在不重新安装的情况下交换。

| 用户希望消息显示为… | 令牌 | 需要报告的后果 |
| --- | --- | --- |
| **应用程序本身**（帖子显示应用程序的名称和 `APP` 徽章） | **`xoxb-`** *(默认 — 优先选择此选项)* | 一个全局工作区凭证，独立于任何员工。机器人必须被邀请到它要发布的每个频道（`/invite @YourApp`），否则 Slack 会回答 `not_in_channel`。无法查看它不在其中的私密频道或 DM。 |
| **特定人员**（帖子显示该人员的姓名和头像） | **`xoxp-`** | 每个操作都将归因于该人员并作为该人员进行审计。它可以到达任何他们可以到达的地方，无需频道邀请。当他们在工作区离开或撤销应用程序时即失效。需要一些仅限用户的 API（例如 `search.messages`）。 |

如果请求是“从我的应用程序发布通知/警报”，那么那是 `xoxb-`。仅在用户明确希望消息看起来像它们来自人类，或需要仅限用户的 API 时选择 `xoxp-`。说明你选择了什么以及原因。

### 获取机器人令牌（`xoxb-`）

1. <https://api.slack.com/apps> → **创建新应用** → *从零开始*，选择工作区。
2. **OAuth & 权限** → *范围* → **机器人令牌范围**：添加构建需要的范围 — 至少 `chat:write`；参见 *请求的范围* 获取其余范围，并立即获取正确的列表（后来的添加将强制重新安装）。
3. **安装到工作区** → 授权 → 复制 **机器人用户 OAuth 令牌**，它以 `xoxb-` 开头。
4. 在 Slack 中，邀请应用程序到每个目标频道：`/invite @YourApp`。跳过这是最常见的首次失败（`not_in_channel`）。

### 请求的范围

上述步骤 2 决定了应用程序可以做什么 — 管理员无法猜测列表，因此**根据构建实际使用的功能导出它**，并在设置 UI 中显示确切的范围（参见 *前端*）。机器人令牌范围：

| 应用程序需要… | 机器人范围 |
| --- | --- |
| 向机器人已被邀请到的频道发送消息 | `chat:write` |
| 向任何不需要邀请的公共频道发送消息 | `chat:write.public` |
| 解析频道名称 → ID，列出公共频道 | `channels:read` |
| 列出机器人所在的私密频道 | `groups:read` |
| 读取消息（`conversationsHistory` / `conversationsReplies`） | `channels:history`，加上 `groups:history` 用于私密频道 |
| 列出/查找用户 | `users:read`，加上 `users:read.email` 用于 `usersLookupByEmail` |
| 与某人 DM（`conversationsOpen` → `chatPostMessage`） | `im:write` |
| 添加表情符号反应 | `reactions:write` |
| 固定消息 | `pins:write` |
| 上传/读取文件 | `files:write`，`files:read` |

> ⚠️ **添加范围后会使令牌失效。** Slack 要求在范围更改后进行**重新安装**，并且重新安装会发出一个新的 `xoxb-` — 旧的令牌将继续工作现有范围，但永远不会获得新的范围，因此应用程序会以 `missing_scope` 失败，直到管理员粘贴新令牌。第一次获取范围列表要正确，并使设置页面可重新粘贴，而不是一次性完成。

### 获取用户令牌（`xoxp-`）

1. 相同的应用程序 → **OAuth & 权限** → *范围* → **用户令牌范围**（与机器人范围*分离*的列表）：添加例如 `chat:write`、`search:read`。
2. **安装到工作区**（如果应用程序已存在则*重新安装*）并授权 — 该令牌代表**点击允许的任何人**。
3. 复制 **用户 OAuth 令牌**，它以 `xoxp-` 开头。

此配方支持单个管理员提供的 `xoxp-`：它通过相同的 setter 和相同的 `config.auth` — 参见 *身份验证模型* — 处理：客户端中的每个方法都是如此。

一个端到端 OAuth 流程，即每个最终用户授权自己的帐户，目前还没有 Slack 辅助程序。不要尝试手动编写它。

### 将令牌交给容器

无论哪种类型，工作区管理员都通过**管理员控制的 setter** 将其粘贴到容器中 — 基于
`AccessControl.hasPermission(state, caller, #admin)`。令牌仅由容器持有，并且**永远不会**返回到前端。

> ⚠️ **永远不要基于首次调用者声称拥有所有权来控制 setter。** 在 IC 上，每个未经身份验证的调用者都是*相同的匿名主体*，因此如果匿名调用者首先声称拥有所有权，则每个匿名调用者都可以通过 `caller == owner` 检查并可以覆盖工作区令牌。使用授权组件的 `#admin` 权限，如下面的示例所示。

然后容器仅通过 `config.auth = ?#bearer(token)` 将该令牌交给客户端，该方法将每个方法转换为 `Authorization: Bearer …` 标头。没有方法接受令牌参数，也没有方法将凭证放在 URL 中，因此它不可能通过记录的查询字符串泄露。

## 出站调用已经是非复制的

`defaultConfig` 提供 `is_replicated = ?false`，因此从它派生的任何记录更新都是正确的 — 无需记忆，无需添加。

不要将其覆盖为 `?true` 或 `null`。一个复制的出站调用会从子网中的每个节点重复请求，对于 Slack 这意味着每个副本都会发布一次消息（~13 个副本），`Authorization: Bearer xoxb-…`/`xoxp-` 标头会离开每个节点，并且由于 Slack 的回复包含每个请求的 `ts`，因此共识会失败。

# 后端

## 添加依赖项

配方中的管理员门控需要授权组件与客户端一起使用：

```bash
mops add slack-client@0.1.0
mops add caffeineai-authorization@1.0.1
```

生成的函数是
`ChatApi.chatPostMessage(config, channel, asUser, attachments, blocks,
iconEmoji, iconUrl, linkNames, mrkdwn, parse, replyBroadcast, text, threadTs,
unfurlLinks, unfurlMedia, username)`。对于不使用的选项，请传递空字符串 / `false`。令牌**不是**参数 — 它仅在 `config.auth` 中传输（参见 *身份验证模型*）；客户端中的每个方法都是如此。

```motoko filepath=src/backend/main.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinSlackConfig "mixins/slack-config";
import MixinSlackMessaging "mixins/slack-messaging";

actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 管理员持有的 Slack 令牌，`xoxb-…` 或 `xoxp-…` — 永远不返回到前端。
  let slackConfig : { var token : Text };
  include MixinSlackConfig(accessControlState, slackConfig);
  include MixinSlackMessaging(slackConfig);
};
```

迁移链头：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    slackConfig : { var token : Text };
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      slackConfig = { var token = "" };
    };
  };
};
```

```motoko filepath=src/backend/mixins/slack-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

mixin (
  accessControlState : AccessControl.AccessControlState,
  slackConfig : { var token : Text },
) {
  public query func isSlackConfigured() : async Bool {
    slackConfig.token.size() > 0;
  };

  // 仅限管理员；接受任何令牌类型。注意：`#admin` — 永远不是
  // 首次调用者声称拥有所有权的检查，
  // 这会被共享的匿名主体击败。
  public shared ({ caller }) func setSlackToken(token : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set the Slack token");
    };
    slackConfig.token := token;
  };
};
```

```motoko filepath=src/backend/mixins/slack-messaging.mo
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import { chatPostMessage } "mo:slack-client/Apis/ChatApi";
import { defaultConfig; type Config } "mo:slack-client/Config";

mixin (slackConfig : { var token : Text }) {
  // 令牌通过 `config.auth` 传输；`defaultConfig` 已经是非复制的。
  func slackClientConfig(token : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer(token);
      max_response_bytes = ?(1_000_000 : Nat64);
    };
  };

  // 将 `text` 发送到 `channel`（频道 ID 像是 "C012AB3CD" 或 "#general"）。
  // 返回发布的消息时间戳 (`ts`)。
  public shared ({ caller }) func postSlackMessage(channel : Text, text : Text) : async Text {
    if (caller.isAnonymous()) Runtime.trap("Sign in to post to Slack");
    if (slackConfig.token.size() == 0) {
      Runtime.trap("Slack is not configured (an admin must set the token)");
    };
    let res = await* chatPostMessage(
      slackClientConfig(slackConfig.token), // 令牌通过 config.auth 传输 — 永远不是 URL 参数
      channel,
      "", "", "", "", "", // asUser, attachments, blocks, iconEmoji, iconUrl
      false, // linkNames
      true, // mrkdwn
      "", // parse
      false, // replyBroadcast
      text, // text
      "", // threadTs
      false, // unfurlLinks
      false, // unfurlMedia
      "", // username
    );
    res.ts;
  };
};
```

## 寻址频道 — 一个 ID，并且机器人必须在其中

`chatPostMessage` 的第一个参数是一个**频道 ID**：`C…` 用于公共或私密频道，`D…` 用于 DM，`G…` 用于旧式群组。`#general` 风格的名称仍然解析为*公共*频道，但已弃用，并且对私密频道永远无效 — 优先选择 ID 并存储它，不要硬编码名称。

**人类在哪里找到 ID**（将这些文字放入 UI 中，而不仅仅是完成消息中）：

- 打开频道 → 点击其标题中的名称 → **关于**选项卡 → 面板底部是 ID（`C012AB3CD`），有一个复制按钮。
- 或者，在侧边栏中右键单击频道 → *复制链接* → ID 是最后一段路径的一部分 `…/archives/C012AB3CD`。

**容器如何获取一个**：`ConversationsApi.conversationsList` 并根据 `name` 匹配（需要 `channels:read`）。解析一次并缓存 ID 在一个稳定的变量中 — 不要在每次发布时解析；它会将出站调用和周期加倍。

**机器人必须是成员**，否则 `chatPostMessage` 会回答 `not_in_channel` — 最常见的首次失败。三种方法，按首选顺序：

1. 管理员在目标频道中运行 `/invite @YourApp`；
2. 授予 `chat:write.public`，这允许机器人无需邀请即可发布到任何*公共*频道；
3. 调用 `conversationsJoin`（仅限公共频道，需要 `channels:join`）。

**要 DM 某个人**：`usersLookupByEmail`（需要 `users:read.email`）或 `usersList` → 用户 ID → `conversationsOpen` → 发布到它返回的 `D…` 频道。需要 `im:write`。

## 可用 API 表面

生成的代码包含 **10 个 API 模块 / ~140 个操作**。只有 `chatPostMessage` 是运行时验证的（参见 *已知限制*）；其余的是从相同的规范生成并执行类型检查，但将它们的响应解码视为未经证实。

| 模块 | 用途 | 代表性函数 |
| --- | --- | --- |
| `ChatApi` | 发布、编辑、删除、永久链接 | `chatPostMessage`、`chatUpdate`、`chatDelete`、`chatPostEphemeral`、`chatScheduleMessage`、`chatGetPermalink` |
| `ChatScheduledMessagesApi` | 定时消息队列 | `chatScheduledMessagesList` |
| `ConversationsApi` | 频道：列出、读取、成员资格、生命周期 | `conversationsList`、`conversationsHistory`、`conversationsReplies`、`conversationsInfo`、`conversationsOpen`、`conversationsJoin`、`conversationsInvite`、`conversationsCreate` |
| `UsersApi` | 目录查找、在线状态 | `usersList`、`usersInfo`、`usersLookupByEmail`、`usersConversations`、`usersGetPresence` |
| `UsersProfileApi` | 个人资料字段 | `usersProfileGet`、`usersProfileSet` |
| `ReactionsApi` | 表情符号反应 | `reactionsAdd`、`reactionsRemove`、`reactionsList` |
| `PinsApi` | 固定消息 | `pinsAdd`、`pinsRemove`、`pinsList` |
| `FilesApi` | 文件列表 / 元数据 / 共享 | `filesList`、`filesInfo`、`filesDelete` |
| `FilesCommentsApi` | 文件评论 | `filesCommentsDelete` |
| `FilesRemoteApi` | 外部文件注册中心 | `filesRemoteAdd`、`filesRemoteInfo`、`filesRemoteList` |

二进制上传/下载在此客户端中**不可用**（multipart 正文超出生成的 JSON/form 表面）。`filesRemoteAdd`，它注册一个位于外部 URL 的文件，是支持的替代方案。

# 前端

Slack 需要**没有 OAuth 回调**：凭证是一个管理员粘贴的长寿命令牌，因此没有重定向 URI，没有 `/connect/slack` 路由，也没有每个用户的握手。不要构建一个。Slack 构建必须包含允许管理员*获取*和*输入*令牌的页面 — 这些是**验收标准，而不是建议**，缺少它们的构建是**有缺陷的，而不仅仅是未完成的**：

- **存在令牌页面且可访问。** 没有“发布到 Slack”功能且没有输入令牌页面的“发布到 Slack”功能是不可用的。登录的管理员必须从导航或从未配置的提示中到达 `/settings/slack`。
- **令牌生成步骤在 UI 中**，而不仅仅是在代理的聊天回复中。管理员几周后返回此页面，此时聊天已经消失。
- **显示确切的范围列表。** 管理员无法推断此应用程序需要哪些范围；显示构建实际使用的范围（*请求的范围*）。

1. **一个登录流程 — 必须的。** `setSlackToken` 基于 `#admin`，因此应用程序需要非匿名调用者。获取登录、`useInternetIdentity` / `useActor` 管理管道，以及令牌设置需要的 `#admin` 角色门控，需要从
   [`extension-authorization`](../extension-authorization/SKILL.md) 获取。

2. **一个管理员设置页面** — `/settings/slack`（管理员门控）。需要：
   - 一个“如何获取您的 Slack 机器人令牌”面板**位于输入上方**，将其框定为一次性的 ~5 分钟设置，包含以下编号步骤（代理的完成消息必须逐字重复它们）：
     1. 打开 <https://api.slack.com/apps> → **创建新应用** → *从零开始* → 命名它并选择工作区；
     2. **OAuth & 权限** → *范围* → **机器人令牌范围** → 添加此页面列出的范围；
     3. **安装到工作区** → *允许* → 复制 **机器人用户 OAuth 令牌**（它以 `xoxb-` 开头）；
     4. 在下方粘贴并保存；
     5. 在 Slack 中，在每个应用程序要发布到的频道中运行 `/invite @YourApp`。
     包含一个方便的链接，打开 <https://api.slack.com/apps>。
   - 渲染为可复制文本的范围列表 — 正是此构建使用的范围，而不是整个表格。
   - 一个**密码输入**绑定到 `setSlackToken(token)`。按回车提交，成功后清除，并使其可重新粘贴：范围更改将强制重新安装并粘贴新令牌，因此这不是一次性表单。
   - 由 `isSlackConfigured()` (`Bool`) 驱动的状态 — “已配置” / “未配置”。**永远**不要渲染令牌，即使用后缀掩码。
   - 如果应用程序发布到固定频道，其 ID 应该也在此页面上：扩展配置 mixin 为 `{ var token : Text; var channel : Text }` 并添加一个管理员门控的 `setSlackChannel`，并将“如何找到频道 ID”提示（参见 *寻址频道*）直接放在字段旁边。不要让用户输入原始 ID 而没有任何解释它来自哪里。
   - **确保页面可访问。** 共享的 Layout 导航必须在 `isCallerAdmin` 为 true 时链接到这里，否则隐藏它。在定义导航的地方添加链接，而不是在此页面内部。

3. **空状态提示。** 当 `isSlackConfigured()` 为 `false` 时，永远不要渲染一个无效的“发送到 Slack”按钮：管理员会得到一个“设置 Slack”链接到 `/settings/slack`；非管理员会得到一个解释 — 例如“Slack 尚未设置 — 管理员需要在设置中添加工作区令牌”。

4. **翻译 Slack 的错误。** 逻辑失败作为*拒绝*调用到达，其消息包含 Slack 自己的 `error` 字符串（参见 *已知限制*）。至少将这三个映射为操作而不是显示原始拒绝：
   - `not_in_channel` → “邀请应用程序加入频道：`/invite @YourApp`”
   - `invalid_auth` / `not_authed` → “Slack 令牌无效 — 在设置中粘贴一个新的令牌”（管理员会得到链接）
   - `channel_not_found` → “检查频道 ID”（带有如何找到提示）
   - `missing_scope` → “应用程序需要另一个 Slack 范围 — 添加它，重新安装，并粘贴新令牌”

建议的路由布局：

```
/                →  主 UI（任何登录用户；未配置时显示空状态）
/settings/slack  →  管理员令牌 + 默认频道（仅限管理员）
# 没有 /connect/slack: Slack 使用粘贴的长寿命令牌，而不是重定向流程。
```

## 作曲家必须告诉 Caffeine 用户的

应用程序无法工作，直到人类创建 Slack 应用并粘贴令牌，因此**作曲家中的完成消息是交付的一部分，而不是它的摘要**。它必须包含，按此顺序：

1. **需要一个令牌，以及谁输入它** — 一个管理员，在
   `/settings/slack`，登录后可通过导航访问。
2. **从 *前端* 项目 2 中**的**五个编号步骤逐字**：在 <https://api.slack.com/apps> 创建应用，添加机器人范围，*安装到工作区*，复制 `xoxb-…` 令牌，粘贴，然后在每个目标频道中运行 `/invite @YourApp`。
3. **此构建需要的确切范围列表**，从 *请求的范围* — 用户可以将其直接复制到 Slack 的范围选择器中的文本，而不是对其的描述。
4. **在哪里找到频道 ID** — *关于*选项卡 / 复制链接配方（参见 *寻址频道*）— 每当用户必须命名频道时。
5. **失败映射，每行一个**：`not_in_channel` → 邀请应用程序；`invalid_auth` → 重新粘贴令牌；`channel_not_found` → 检查 ID；`missing_scope` → 添加范围，重新安装，粘贴新令牌。

不要将其压缩为“在设置中配置 Slack”，也不要用 Slack 的文档链接替换它。用户正在构建中，很可能从未见过 Slack 应用控制面板，并且作曲家是他们正在寻找的地方。在此处使用与设置页面面板相同的措辞，以防止两者出现差异。

## 已知限制（实验性）

- **报告 `{"ok": false}`，作为一个拒绝调用。** Slack 将逻辑失败（无效令牌、缺少范围、频道未找到）作为 HTTP **200** 上的 `{"ok": false, "error": "…"}` 信号。由于 0.1.0，客户端检测到这一点并路由到错误路径，因此拒绝消息命名 Slack 自己的 `error` 字符串 — 例如 `not_authed`、`invalid_auth`、`channel_not_found` — 而不是解码失败。将其作为拒绝调用处理：
  `try { … } catch (e) { Error.message(e) }`。**不要**写 `if (res.ok) …`：返回值已经解码，因此 `ok` 始终为 `true`，检查是死代码。将它们转换为 `#ok`/`#err` 返回*值*将改变每个方法的签名，因此等待一个主要版本。
- **可达性 (IPv4) — 无需代理。** `slack.com` 仅支持 IPv4，这曾经使它无法通过 IC HTTPS 出站调用。由于 **2025-08-04**，IC 尝试直接连接（IPv6），并在失败时自动通过 IC 管理的 SOCKS 代理重试，因此仅支持 IPv4 的主机工作：将 `config.baseUrl` 保持默认 `https://slack.com/api`。TLS 会话是节点和 Slack 之间的端到端，因此代理只看到密文。预期在回退路径上会有一些额外的延迟（非复制的出站调用也是较慢的路径 — 参见上文）。
- **身份验证基于标头，适用于每个方法。** 令牌仅通过 `Authorization: Bearer` 标头传输 — 永远不在 URL 中，因此它不可能出现在记录的查询字符串中，并且它永远不会是方法参数。
- **部分运行时验证。** 请求形状针对实时 Slack 已证明（一个真实的发布到达）；成功响应解码尚未运行时确认 — `diagnostics` 已开启，因此任何解码失败都会暴露原始 Slack 正文。模式也是从存档（~2020）的规范修订版本生成的。

## 相关

- [`mops add slack-client@0.1.0`](https://mops.one/slack-client) — 生成的 Slack Web API 绑定。
- [Slack Web API 参考](https://api.slack.com/methods) — 每个方法，其范围和其错误字符串。
- [`chat.postMessage`](https://api.slack.com/methods/chat.postMessage) — 仅运行时验证的路径；其 `channel`/`text`/`blocks` 语义。
- [Slack 令牌类型](https://api.slack.com/concepts/token-types) — 机器人 (`xoxb-`) 与用户 (`xoxp-`), 以及重新安装对它们的影响。
- [Slack 应用管理](https://api.slack.com/apps) — 管理员创建应用、设置范围并将应用安装到工作区。
- [extension-authorization](../extension-authorization/SKILL.md) — **必需的先决条件**。Internet Identity 登录，`useInternetIdentity` / `useActor` 管理管道，以及令牌设置需要的 `#admin` 角色门控。
