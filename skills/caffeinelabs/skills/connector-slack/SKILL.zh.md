---
name: connector-slack
description: 用于从 Caffeine 容器通过 `slack-client` mops 包（Slack Web API）向 Slack 工作区发送消息的实验性、未经测试的配方。当用户希望其应用程序向 Slack 频道发送消息时使用——例如“发布到 Slack”、“通知频道”、“发送 Slack 消息”或类似表述。该客户端是一个预发布版本 0.1.0 的版本（机器人 `xoxb-` 或用户 `xoxp-` 令牌）：其请求路径已与实时 Slack API 进行验证（可发送真实消息），但成功响应的解码尚未在运行时确认，因此将其视为起点，目前不要将 Slack 作为完全支持的平台功能呈现。手动编写 `ic.http_request` 调用至 `slack.com/api` 仍然是错误的做法——优先使用生成的客户端，以便令牌认证、百分比编码和 JSON 解析都能免费获得。
---

# Slack 连接器（实验性）

从 Caffeine 容器向 Slack 工作区发送消息。

> ⚠️ **实验性 (`slack-client@0.1.0`)。** **针对实时 Slack 进行验证：** 请求路径——真实的 `chat.postMessage` 发送（早期的查询与表单错误已解决；POST 参数在 `application/x-www-form-urlencoded` 正文内）。**在 0.1.0 中实现但尚未在实时环境中测试：** 成功响应解码（`{"ok":true,…}` → 成功模式）和 `{"ok":false}` 错误信封路由（参见 *已知限制* 了解每个的作用）。因此响应端是代码完整的但未经证实——`diagnostics` 已开启，因此解码失败会暴露原始 Slack 正文。在**一个实时运行确认解码成功回复**之前，不要将 Slack 作为完全支持的平台功能呈现；这个条件，而不是版本号，是关键。

## 协调器路由说明

当用户、规范或先前的任务提及 Slack、向频道发送消息或通知 Slack 工作区时，加载此技能。生成的 `slack-client` 包是首选路径；原始 `ic.http_request` 到 `https://slack.com/api/*` 是反模式，它手动重新实现了认证、百分比编码和 JSON 解析。

意图→功能映射：

| 用户意图 | 功能 |
| --- | --- |
| 以应用程序身份向 Slack 频道发送消息 | `slack-client` `chatPostMessage` 使用机器人令牌 (`xoxb-`) |
| 以指定人员身份向 Slack 发送消息 | `slack-client` `chatPostMessage` 使用用户令牌 (`xoxp-`) |

在生成代码之前，**将令牌选择反馈给提示用户**
（机器人 vs 用户——参见 *认证模型* 获取单行规则和权衡）并告诉他们在哪里获取它。他们无法在没有粘贴令牌的情况下继续，因此尽早暴露这一点可以避免应用程序在首次使用时卡住。

令牌是**人类必须去创建**的东西，因此构建不是在后台编译时完成的。它是在应用程序本身告诉管理员如何获取令牌并给他们一个粘贴的地方时完成的——参见 *获取机器人令牌* 获取步骤，*请求的范围* 了解要勾选的内容，*向频道发送消息* 了解频道 ID，以及 *前端* 了解必须包含的页面。在完成消息中也重复这些步骤；聊天会话既不会持续应用程序，也不会持续管理员的记忆。

生成的代码范围：消息核心家族 `chat`、`conversations`、`users`、`files`、`reactions` 和 `pins`（10 个 API 模块）——参见 *可用 API 表面* 获取每个模块的细分。
其他 Slack 方法在规范重新生成之前不在范围内。

## 认证模型——机器人令牌 (`xoxb-`) 或用户令牌 (`xoxp-`)

两者都是担保证书，客户端将它们视为相同，但它们在工作区看到的操作者不同。**在编写代码之前询问提示用户他们想要哪一个，并说明权衡**——答案会改变他们的应用程序在 Slack 中的外观，并且不能在没有重新安装的情况下交换。

| 用户希望消息显示为… | 令牌 | 需要报告的后果 |
| --- | --- | --- |
| **应用程序本身**（帖子显示应用程序的名称和 `APP` 徽章） | **`xoxb-`** *(默认——优先选择)* | 一个全局工作区凭证，独立于任何员工。机器人必须被邀请到它要发布的每个频道（`/invite @YourApp`），否则 Slack 会回答 `not_in_channel`。无法看到它不在的私密频道或 DM。 |
| **特定人员**（帖子显示该人的姓名和头像） | **`xoxp-`** | 每个操作都被归因于该人，并作为该人进行审计。可以触及他们能触及的任何内容，无需频道邀请。当他们离开工作区或撤销应用程序时失效。需要一些仅限用户的 API（例如 `search.messages`）。 |

如果请求是“从我的应用程序发布通知/警报”，那么是 `xoxb-`。只有在用户明确希望消息看起来像是从人类发送的，或者需要仅限用户的 API 时才选择 `xoxp-`。说明你选择了什么以及原因。

### 获取机器人令牌 (`xoxb-`)

1. <https://api.slack.com/apps> → **创建新应用** → *从空白开始*，选择工作区。
2. **OAuth & Permissions** → *范围* → **机器人令牌范围**：添加构建需要的范围——至少 `chat:write`；参见 *请求的范围* 获取其余范围，并立即获取列表（稍后的添加将强制重新安装）。
3. **安装到工作区** → 授权 → 复制 **机器人用户 OAuth 令牌**，它以 `xoxb-` 开头。
4. 在 Slack 中，邀请应用程序到每个目标频道：`/invite @YourApp`。跳过这一点是最常见的首次失败（`not_in_channel`）。

### 请求的范围

上述步骤 2 决定了应用程序可以做什么——管理员无法猜测列表，因此**根据构建实际使用的功能导出它**，并在设置 UI 中显示确切的内容（参见 *前端*）。机器人令牌范围：

| 应用程序需要… | 机器人范围 |
| --- | --- |
| 向机器人已被邀请到的频道发送消息 | `chat:write` |
| 向任何无需邀请的公共频道发送消息 | `chat:write.public` |
| 解析频道名称→ID，列出公共频道 | `channels:read` |
| 列出机器人所在的私密频道 | `groups:read` |
| 读取消息（`conversationsHistory` / `conversationsReplies`） | `channels:history`，加上 `groups:history` 用于私密 |
| 列出/查找用户 | `users:read`，加上 `users:read.email` 用于 `usersLookupByEmail` |
| 与某人 DM（`conversationsOpen` → `chatPostMessage`） | `im:write` |
| 添加表情符号反应 | `reactions:write` |
| 固定消息 | `pins:write` |
| 上传/读取文件 | `files:write`，`files:read` |

> ⚠️ **添加范围后会使令牌失效。** Slack 要求在范围更改后进行**重新安装**，并且重新安装会发出 *新的* `xoxb-`——旧的令牌会继续为现有范围工作，但永远不会获得新的范围，因此应用程序会因 `missing_scope` 而失败，直到管理员粘贴新令牌。第一次获取范围列表，并使设置页面可重新粘贴，而不是一次性使用。

### 获取用户令牌 (`xoxp-`)

1. 相同的应用程序 → **OAuth & Permissions** → *范围* → **用户令牌范围**（与机器人范围*分离*的列表）：添加例如 `chat:write`，`search:read`。
2. **安装到工作区**（如果应用程序已存在则*重新安装*）并授权——该令牌代表**点击允许的任何人**。
3. 复制 **用户 OAuth 令牌**，它以 `xoxp-` 开头。

此配方支持由管理员提供的单个 `xoxp-`：它通过相同的设置器和相同的 `config.auth`（参见 *认证模型*）；这适用于客户端中的每个方法。

一个由每个最终用户为其自己的帐户授权的 OAuth 不在此范围内，即需要完整的重定向+代码交换+刷新流程，目前还没有 Slack 辅助程序。不要尝试手动实现它。

### 将令牌交给容器

无论哪种类型，工作区管理员都通过**管理员控制的设置器**粘贴它——基于
`AccessControl.hasPermission(state, caller, #admin)`。令牌仅由容器持有，并且**永远不会**返回到前端。

> ⚠️ **永远不要基于首次调用者声称拥有所有权来控制设置器。** 在 IC 上每个未经身份验证的调用者都是*相同的匿名主体*，因此如果匿名调用者首先声称拥有所有权，则每个匿名调用者都会通过 `caller == owner` 检查，并且可以覆盖工作区令牌。使用授权组件的 `#admin` 权限，如下面的示例所示。

容器然后仅通过
`config.auth = ?#bearer(token)` 将该令牌交给客户端，该方法将每个方法转换为 `Authorization: Bearer …` 标头。没有方法接受令牌参数，也没有方法将凭证放在 URL 中，因此它无法通过登录查询字符串泄漏。

## 出站调用已经是非复制的

`defaultConfig` 提供 `is_replicated = ?false`，因此从它派生的任何记录更新都是正确的——无需记忆，无需添加。

不要将其覆盖为 `?true` 或 `null`。复制的出站调用会从子网中的每个节点重复请求，对于 Slack 来说这意味着每个副本都会发布一次消息（~13 个副本），`Authorization: Bearer xoxb-…`/`xoxp-…` 标头会离开每个节点，并且由于 Slack 的回复包含每个请求的 `ts`，因此共识会失败。

# 后端

## 添加依赖项

配方中的管理员门需要授权组件与客户端一起使用：

```bash
mops add slack-client@0.1.0
mops add caffeineai-authorization@1.0.1
```

生成的函数是
`ChatApi.chatPostMessage(config, channel, asUser, attachments, blocks,
iconEmoji, iconUrl, linkNames, mrkdwn, parse, replyBroadcast, text, threadTs,
unfurlLinks, unfurlMedia, username)`。对于不使用的选项，传递空字符串 / `false`。令牌**不是**参数——它仅在 `config.auth` 中传输（参见 *认证模型*）；客户端中的每个方法都是如此。

```motoko filepath=src/backend/main.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinSlackConfig "mixins/slack-config";
import MixinSlackMessaging "mixins/slack-messaging";

actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 由管理员持有的 Slack 令牌，`xoxb-…` 或 `xoxp-…`——永远不会返回到前端。
  let slackConfig : { var token : Text };
  include MixinSlackConfig(accessControlState, slackConfig);
  include MixinSlackMessaging(slackConfig);
};
```

迁移链头部：

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

  // 仅限管理员；接受任何令牌类型。注意：`#admin`——永远不会是首次调用者声称拥有所有权的检查，
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
  // 返回已发布的消息时间戳 (`ts`)。
  public shared ({ caller }) func postSlackMessage(channel : Text, text : Text) : async Text {
    if (caller.isAnonymous()) Runtime.trap("Sign in to post to Slack");
    if (slackConfig.token.size() == 0) {
      Runtime.trap("Slack is not configured (an admin must set the token)");
    };
    let res = await* chatPostMessage(
      slackClientConfig(slackConfig.token), // 令牌通过 config.auth 传输——永远不会是 URL 参数
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

## 向频道发送消息——一个 ID，并且机器人必须在其中

`chatPostMessage` 的第一个参数是**频道 ID**：`C…` 用于公共或私密频道，`D…` 用于 DM，`G…` 用于旧式群组。`#general` 风格的名称仍然解析为*公共*频道，但已弃用并且对私密频道永远无效——优先选择 ID 并存储它，不要硬编码名称。

**人类在哪里找到 ID**（将这些话放入 UI 中，而不仅仅是完成消息中）：

- 打开频道 → 点击其标题中的名称 → **关于**选项卡 → ID 位于面板底部（`C012AB3CD`），有一个复制按钮。
- 或者右键单击侧边栏中的频道 → *复制链接* → ID 是 `…/archives/C012AB3CD` 的最后一个路径段。

**容器如何获取一个：** `ConversationsApi.conversationsList` 并匹配 `name`（需要 `channels:read`）。解析一次并缓存 ID 在一个稳定的变量中——不要在每次发送时解析；它会将出站调用和周期翻倍。

**机器人必须是成员**，否则 `chatPostMessage` 会回答 `not_in_channel`——这是最常见的首次失败。三种方法，按偏好顺序：

1. 管理员在目标频道中运行 `/invite @YourApp`；
2. 授予 `chat:write.public`，这允许机器人无需邀请即可向任何*公共*频道发送消息；
3. 调用 `conversationsJoin`（仅限公共频道，需要 `channels:join`）。

**要 DM 某个人：** `usersLookupByEmail`（需要 `users:read.email`）或
`usersList` → 用户 ID → `conversationsOpen` → 发送到它返回的 `D…` 频道。需要 `im:write`。

## 可用 API 表面

生成的代码包提供**10 个 API 模块 / ~140 个操作**。只有 `chatPostMessage` 是实时验证的（参见 *已知限制*）；其余的是从相同的规范生成并类型检查的，但将它们的响应解码视为未经证实。

| 模块 | 用于 | 代表性函数 |
| --- | --- | --- |
| `ChatApi` | 发布、编辑、删除、永久链接 | `chatPostMessage`，`chatUpdate`，`chatDelete`，`chatPostEphemeral`，`chatScheduleMessage`，`chatGetPermalink` |
| `ChatScheduledMessagesApi` | 定时消息队列 | `chatScheduledMessagesList` |
| `ConversationsApi` | 频道：列出、读取、成员资格、生命周期 | `conversationsList`，`conversationsHistory`，`conversationsReplies`，`conversationsInfo`，`conversationsOpen`，`conversationsJoin`，`conversationsInvite`，`conversationsCreate` |
| `UsersApi` | 目录查找、在线状态 | `usersList`，`usersInfo`，`usersLookupByEmail`，`usersConversations`，`usersGetPresence` |
| `UsersProfileApi` | 个人资料字段 | `usersProfileGet`，`usersProfileSet` |
| `ReactionsApi` | 表情符号反应 | `reactionsAdd`，`reactionsRemove`，`reactionsList` |
| `PinsApi` | 固定消息 | `pinsAdd`，`pinsRemove`，`pinsList` |
| `FilesApi` | 文件列表/元数据/共享 | `filesList`，`filesInfo`，`filesDelete` |
| `FilesCommentsApi` | 文件评论 | `filesCommentsDelete` |
| `FilesRemoteApi` | 外部文件注册中心 | `filesRemoteAdd`，`filesRemoteInfo`，`filesRemoteList` |

二进制上传/下载从此客户端**不可用**（多部分正文不在生成的 JSON/form 表面之外）。`filesRemoteAdd`，它注册一个位于外部 URL 的文件，是支持的替代方案。

# 前端

Slack 需要**没有 OAuth 回调**：凭证是管理员粘贴的长寿命令牌，因此没有重定向 URI，没有 `/connect/slack` 路由，也没有每个用户的握手。不要构建一个。Slack 构建必须提供的页面是让管理员*获取*和*输入*令牌——这些是**验收标准，而不是建议**，缺少它们的构建是**有缺陷的，而不仅仅是未完成的**：

- **令牌页面存在且可访问。** 没有页面可以输入令牌的“发布到 Slack”功能无法使用。登录的管理员必须从导航栏或从未配置提示中访问 `/settings/slack`。
- **令牌生成步骤在 UI 中**，而不仅仅是在代理的聊天回复中。管理员几周后返回此页面，此时聊天记录已消失。
- **显示确切的权限范围列表。** 管理员无法推断该应用程序需要哪些权限；显示构建实际使用的权限（*请求的权限*）。

1. **登录流程 — 必须的。** `setSlackToken` 在 `#admin` 上进行控制，因此该应用程序需要非匿名调用者。获取登录、`useInternetIdentity` / `useActor` 的管道，以及管理员角色门控从 [`extension-authorization`](../extension-authorization/SKILL.md)。

2. **管理员设置页面** — `/settings/slack`（管理员门控）。必须：
   - 一个“如何获取您的 Slack 机器人令牌”的面板**位于输入上方**，将其框定为一次约 5 分钟的设置，包含以下编号步骤（代理的完成消息必须逐字重复它们）：
     1. 打开 <https://api.slack.com/apps> → **创建新应用程序** → *从空白开始* → 命名它并选择工作区；
     2. **OAuth & 权限** → *权限* → **机器人令牌权限** → 添加此页面列出的权限；
     3. **安装到工作区** → *允许* → 复制 **机器人用户 OAuth 令牌**（它以 `xoxb-` 开头）；
     4. 将其粘贴到下方并保存；
     5. 在 Slack 中，在每个应用程序发布到的频道中运行 `/invite @YourApp`。包含一个方便的链接，打开 <https://api.slack.com/apps>。
   - 渲染为可复制文本的权限列表 — 确切是此构建使用的权限，而不是整个表格。
   - 一个**密码输入**绑定到 `setSlackToken(token)`。按回车提交，成功时清除，并保持可重新粘贴：权限更改强制重新安装并输入新令牌，因此这不是一次性表单。
   - 由 `isSlackConfigured()` (`Bool`) 驱动的状态 — “已配置” / “未配置”。**永远**不要渲染令牌，即使是带后缀的掩码。
   - 如果应用程序发布到固定频道，其 ID 也应在此页面中：扩展配置混入到 `{ var token : Text; var channel : Text }`，并添加管理员门控的 `setSlackChannel`，并将“在哪里找到频道 ID”的提示（见 *寻址频道*）内联放置在字段旁边。不要让用户输入原始 ID 而没有对其来源的解释。
   - **使页面可访问。** 共享布局导航栏在 `isCallerAdmin` 为 true 时必须链接到此处，否则隐藏它。在导航栏定义的位置添加链接，而不是在此页面内部。

3. **空状态提示。** 当 `isSlackConfigured()` 为 `false` 时，永远不要渲染一个死掉的“发送到 Slack”按钮：管理员会获得一个“设置 Slack”链接到 `/settings/slack`；非管理员会获得解释 — 例如“Slack 尚未设置 — 管理员需要在设置中添加工作区令牌”。

4. **翻译 Slack 的错误。** 逻辑失败作为 *拒绝* 调用到达，其消息包含 Slack 自身的 `error` 字符串（见 *已知限制*）。至少将这些三个映射到操作而不是显示原始拒绝：
   - `not_in_channel` → “邀请应用程序到频道：`/invite @YourApp`”
   - `invalid_auth` / `not_authed` → “Slack 令牌无效 — 在设置中粘贴一个新的”（管理员会获得链接）
   - `channel_not_found` → “检查频道 ID”（带有如何找到的提示）
   - `missing_scope` → “应用程序需要另一个 Slack 权限 — 添加它，重新安装，并粘贴新令牌”

建议的路由布局：

```
/                →  主 UI（任何登录用户；未配置时为空状态）
/settings/slack  →  管理员令牌 + 默认频道（仅管理员）
# 没有 /connect/slack：Slack 使用粘贴的长寿命令牌，而不是重定向流程。
```

## 作曲家必须告诉 Caffeine 用户

应用程序在人类创建 Slack 应用并粘贴令牌之前无法工作，因此**作曲家中的完成消息是交付的一部分**，而不是它的摘要。它必须按以下顺序包含：

1. **需要一个令牌，以及谁输入它** — 一个管理员，在 `/settings/slack`，登录后可通过导航栏访问。
2. **五步编号的逐字内容** 从 *前端* 项目 2：在 <https://api.slack.com/apps> 创建应用程序，添加机器人权限，*安装到工作区*，复制 `xoxb-…` 令牌，粘贴，然后在每个目标频道中运行 `/invite @YourApp`。
3. **此构建需要的确切权限列表** 从 *请求的权限* — 作为用户可以直接复制到 Slack 权限选择器的文本，而不是对其的描述。
4. **在哪里找到频道 ID** — *关于*标签 / 复制链接配方从 *寻址频道* — 每当用户必须命名频道时。
5. **失败映射，每行一个**：`not_in_channel` → 邀请应用程序；`invalid_auth` → 重新粘贴令牌；`channel_not_found` → 检查 ID；`missing_scope` → 添加权限，重新安装，粘贴新令牌。

不要将其压缩为“在设置中配置 Slack”，也不要用 Slack 文档的链接来替代。用户正在构建中，很可能从未见过 Slack 应用程序控制面板，作曲家是他们正在查看的地方。在此处使用与设置页面面板相同的措辞，以便两者不会产生偏差。

## 已知限制（实验性）

- **报告 `{"ok": false}`，作为拒绝的调用。** Slack 将逻辑失败（无效令牌、缺少权限、频道未找到）作为 HTTP **200** 上的 `{"ok": false, "error": "…"}` 信号。自 0.1.0 起，客户端检测到这一点，并通过错误路径路由，因此拒绝消息命名 Slack 自身的 `error` 字符串 — 例如 `not_authed`，`invalid_auth`，`channel_not_found` — 而不是解码失败。将其作为拒绝调用处理：
  `try { … } catch (e) { Error.message(e) }`。**不要**写 `if (res.ok) …`：返回值已经解码，因此 `ok` 始终为 `true`，检查是死代码。将这些转换为 `#ok`/`#err` 返回*值*将改变每个方法的签名，因此那要等到主要版本。 
- **可达性（IPv4） — 不需要代理。** `slack.com` 仅支持 IPv4，这曾使其无法通过 IC HTTPS 出呼叫。自 **2025-08-04** 起，IC 尝试直接（IPv6）连接，并在失败时自动通过 IC 管理的 SOCKS 代理重试，因此仅支持 IPv4 的主机可以工作：将 `config.baseUrl` 保持默认 `https://slack.com/api`。TLS 会话是在节点和 Slack 之间端到端的，因此代理只看到密文。在回退路径上可能会增加一些延迟（非复制出呼叫也是较慢的路径 — 见上文）。
- **认证是基于请求头的，每个方法都是。** 令牌仅在 `Authorization: Bearer` 请求头中 — 永远不在 URL 中，因此它不可能出现在记录的查询字符串中，并且它永远不会是方法参数。
- **部分运行时验证。** 请求形状针对实时 Slack（真实的发布到达）；成功响应的解码尚未运行时确认 — `diagnostics` 是开启的，因此任何解码失败都会显示原始 Slack 正文。模式也是从存档（~2020）的规范修订版生成的。

## 相关

- [`mops add slack-client@0.1.0`](https://mops.one/slack-client) — 生成的 Slack Web API 绑定。
- [Slack Web API 参考](https://api.slack.com/methods) — 每个方法、其权限及其错误字符串。
- [`chat.postMessage`](https://api.slack.com/methods/chat.postMessage) — 唯一运行时验证的路径；其 `channel`/`text`/`blocks` 语义。
- [Slack 令牌类型](https://api.slack.com/concepts/token-types) — 机器人 (`xoxb-`) 与用户 (`xoxp-`)，以及重新安装对它们的影响。
- [Slack 应用程序管理](https://api.slack.com/apps) — 管理员在此创建应用程序、设置权限并安装到工作区。
- [extension-authorization](../extension-authorization/SKILL.md) — **必需的先决条件**。Internet Identity 登录、`useInternetIdentity` / `useActor` 的管道，以及令牌设置者需要的 `#admin` 角色门控。
