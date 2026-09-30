---
name: connector-spotify
description: 每個 Caffeine 构建的必須配方，用於讀取 Spotify 目錄數據或從容器驅動用戶的 Spotify 账戶。支持的路徑是 `spotify-client` mops 套件（Spotify Web API），通過出站 HTTPS 使用鏈下生成的 OAuth 2.0 授權碼。手動編寫 `ic.http_request` 調用至 `api.spotify.com` 是一種禁止的反模式——它繞過了非複製出調用保護（每個節點的播放狀態和 `progress_ms` 不同且無法達成共識）、生成的 JSON 解碼以及授權碼處理。當用戶、規範或任何先前任務提及 Spotify、歌曲、曲目、藝術家、專輯、播放列表、音樂搜索、新發行、流派、市場、正在播放、最近播放、隊列、播放器控制（播放/暫停/跳過/隨機/重複）、已保存庫、播客（節目或集數）、章節或有聲書時，請載入此技能——並在編寫任何觸及 Spotify 端點的代碼之前。
---

# Spotify with `spotify-client`

Motoko 绑定库用于
[Spotify Web API](https://developer.spotify.com/documentation/web-api)，
从 Spotify 官方 OpenAPI 规范生成：**15 个 API 模块，270 个操作**。该包以 **icp-cli 模式** 构建 (`mo:ic/Types` 用于管理 canister 接口)，因此将 `ic` 作为依赖项并固定 PocketIC 在 `[toolchain]` 中。

# 后端

读取目录数据并驱动播放器。令牌始终来自调用者——canister 永远不持有 Spotify 客户机密：

```motoko filepath=src/backend/main.mo
import { getTrack } "mo:spotify-client/Apis/TracksApi";
import { getInformationAboutTheUsersCurrentPlayback; skipUsersPlaybackToNextTrack } "mo:spotify-client/Apis/PlayerApi";
import { type Config; defaultConfig } "mo:spotify-client/Config";

persistent actor {
  func config(accessToken : Text) : Config = { defaultConfig with auth = ?#bearer accessToken };

  // 目录读取——客户端凭证令牌足够。`market = ""` 省略该参数；空字符串和零是如何丢弃可选查询参数的，
  // 没有 `?Text` 留空。
  public func trackName(accessToken : Text, id : Text) : async ?Text {
    let track = await* getTrack(config accessToken, id, "");
    track.name;
  };

  // 用户读取——需要带有 `user-read-playback-state` 的用户令牌。空闲的播放器以 204 和空正文响应，
  // 生成的解码器无法解析，因此它拒绝；将其视为“没有播放”，而不是错误。
  public func nowPlaying(accessToken : Text) : async ?Bool {
    try {
      let state = await* getInformationAboutTheUsersCurrentPlayback(config accessToken, "", "");
      state.is_playing;
    } catch (_err) {
      null;
    };
  };

  // 用户写入——需要 `user-modify-playback-state`。返回 `()`, 并且从 0.3.0 开始非 2xx 状态拒绝，
  // 因此缺少范围或过期令牌在这里显示，而不是看起来像成功。
  public func skip(accessToken : Text) : async () {
    await* skipUsersPlaybackToNextTrack(config accessToken, "");
  };
}
```

## 认证：canister 永远不看到客户机密

每个调用都需要一个 **OAuth 2.0 带有访问令牌**，链下生成并在传入。两个流程很重要：

1. **客户端凭证**——服务器到服务器，没有用户。仅读取公共目录：`search`, `getTrack`, `getAnAlbum`, `getAnArtist`, `getNewReleases`, `getCategories`, `getAvailableMarkets`, 公共播放列表，公共节目。它**不能**触及任何 `/me/*` 端点，库或播放器。
2. **授权码与 PKCE**——面向用户。每个 `/me/*` 调用、播放列表修改、库写入和播放器命令都需要，每个都由其自己的范围 (`user-read-playback-state`, `user-modify-playback-state`, `playlist-modify-public`, `user-library-read`, …) 控制范围。令牌中缺少范围会显示为 403，而不是验证错误。

令牌在**一小时**后过期，刷新也是链下。将 401 视为“要求客户端刷新并重试”，永远不要将其视为永久性失败，并且永远不要在 canister 中存储客户机密。

## 调用默认情况下不复制

该包在 `defaultConfig` 中提供 `is_replicated = ?false`，并且**135 个操作中的 91 个依赖于它**。生成器已经针对 27 个 `PUT` 和 17 个 `DELETE` 操作固定了每个请求的非复制，因为 IC 要求这样做——因此播放列表编辑和库保存从未处于风险中。默认值涵盖了其余部分：

- **7 个 `POST`**，包括 `addToQueue` 和两个跳过端点。这些不是幂等的，因此复制它们会排队 ~13 次曲目并跳过 ~13 个曲目；
- 所有 **84 个 `GET`**，这些对于播放器是非确定性的——当前播放携带 `timestamp` 和 `progress_ms`，每个节点都不同——并且即使它们一致，成本也会增加 ~13 倍。

您不需要自己设置标志；默认值是正确的。使用 `is_replicated = ?true` 仅与 `transform` 一起使用，该 `transform` 删除易失性字段。

**从 0.2.x 升级——旧的建议是相反的**。该技巧告诉调用者保持 `is_replicated = null` 用于修改“因为共识很重要”，并显示 `let userCfg = { cfg with is_replicated = null }`。继续这样做现在会主动造成伤害：`null` 意味着复制，因此每个 `addToQueue` 和跳过都会在每个副本上触发。删除任何此类覆盖，并接受 `defaultConfig` 的样子。

## 响应中的所有内容都是可选的

Spotify 几乎不标记响应字段为必需，因此模型都是可选的：`TrackObject.name : ?Text`, `.artists : ?[SimplifiedArtistObject]`, `CurrentlyPlayingContextObject.is_playing : ?Bool`。通过 `do ?` 块而不是嵌套 `switch`es 来访问，并决定您的调用者“缺失”的含义——Spotify 会省略令牌的范围不涵盖的字段。

## ID，而不是 URI

端点参数使用 Spotify 的**62 进制 ID** (`11dFghVXANMlKmJXsNCbNl`)，而不是 URI (`spotify:track:11dFghVXANMlKmJXsNCbNl`) 和 URL。当用户粘贴 Spotify 链接时，提取最后一个 `/` 后面的部分和任何 `?` 之前的部分。播放列表操作上的 `uris` 参数是例外——那些确实使用完整的 `spotify:track:…` URI。

## 开始播放

`PlayerApi.startAUsersPlayback` 接受四个字段作为标量——`context_uri : ?Text`, `uris : ?[Text]`, `position_ms : ?Int`——`transferAUsersPlayback` 接受 `play : ?Bool`。选择 `uris`（显式曲目）或 `context_uri`（专辑、艺术家或播放列表）中的一个，永远不要两者都使用。

`offset` 是例外：它是规范中的一个自由形式对象，因此生成器将其映射到 `?Map<Text, Text>` 并将**每个值作为字符串**序列化。`{"uri": "spotify:track:…"}` 因此有效，而 Spotify 的其他文档形式 `{"position": 5}` 会作为 `{"position": "5"}` 发送并被拒绝。通过 URI 而不是索引偏移到上下文中。

## 一个操作不起作用

`PlaylistsApi.uploadCustomPlaylistCover`——规范声明正文为 `image/jpeg` (`format: byte`)，但生成器只发出 JSON 请求正文，因此调用发送 `Content-Type: application/json` 并将 base64 用 JSON 引号括起来。Spotify 拒绝它。这不是 0.3.0 中的新内容：0.2.2 将原始 `Blob` 用 JSON 括起来，这在网络上同样错误。不要提供自定义播放列表封面上传，并且不要用 `ic.http_request` 手动制作；在
[`caffeinelabs/skills-internal`](https://github.com/caffeinelabs/skills-internal) 上引发它。

表面上的其他内容都是正确的——与某些连接器不同，没有模拟的 `oneOf` 转换器，没有静默丢弃请求正文的操作，也没有端点通过 JSON 解码器返回非 JSON 正文。

## 空闲播放器拒绝而不是返回“没有播放”

`PlayerApi.getInformationAboutTheUsersCurrentPlayback` 和
`getTheUsersCurrentlyPlayingTrack` 在播放不活动时回答 **204 并带有空正文**。生成的代码将每个 2xx 视为 200 模式并在其上运行 JSON 解码器，因此空闲播放器产生
`Error.reject(… Failed to parse JSON …)` 而不是缺失值。将两者包装在 `try`/`catch` 中，并将拒绝读取为“没有播放”，就像 §Backend 示例那样。

这是一个代码生成器差距，而不是 Spotify 的怪癖：规范声明 `'204': Playback not available or active` 为第一个操作（生成器忽略无内容 2xx 响应并且没有 `?T` 返回形状），而对于第二个操作 Spotify 实际上返回 204 而没有声明它。建模声明的无内容响应将更改生成签名以 `?CurrentlyPlayingContextObject`，因此它属于插件作为自己的更改。

## 每个写入现在报告其状态

直到 0.3.0，43 个返回 `async* ()` 的操作——`skip`, `pause`, `addToQueue`, 每个库和播放列表修改——完全丢弃 HTTP 响应，因此 401、403 或 429 与成功无法区分。它们现在在非 2xx 状态上拒绝。预期 `try`/`catch` 围绕写入实际上会触发：缺少范围现在显示为 403，而以前看起来像成功的无操作。

## 周期和响应大小

`defaultConfig.cycles = 30_000_000_000` 适合典型的单个对象读取。需要更多：`search` 与 `limit=50`，`getAnAlbum` 在长曲目列表上，或 `getAudioAnalysis`（它返回一个非常大的对象）需要 `cycles = 100_000_000_000` 和显式的
`max_response_bytes = ?2_000_000`。

## 错误

非 2xx 响应和解码失败 `throw Error.reject(…)`。客户端使用 `diagnostics` 生成，因此消息是
`HTTP <status> body[<n>B]=<first 100 chars>: <reason>`——足够区分 401（过期令牌）与 403（缺少范围）与 404（错误 ID）而无需额外日志。使用 `try`/`catch` 捕获并显示 `Error.message(err)`。
