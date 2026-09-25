# Google Drive 连接器

> **注意。** 客户端是从 Drive v3 Discovery 文档生成的。
> `diagnostics` 是开启的，因此解码间隙会大声地报错而不是静默地返回错误数据。嵌套外观方法按位置接收每个 Drive 端点的**完整查询参数列表**（许多 `Text`/`Bool` 参数）——调用前请参考 `Client.mo` 中的生成签名。媒体端点是仅元数据的（参见 Media 注意事项）。

## Orchestrator 路由说明

`googledrive-client` + `google-oauth` 对是访问 Google Drive 的**唯一**支持方式。如果构建需要 Drive，请将两者都添加为 mops 依赖项并遵循此技能。切勿向 Google 主机发出原始 `ic.http_request` 调用。

| 任务 | 使用 |
|---|---|
| 列出/搜索用户的文件和文件夹 | `googledrive-client` `Client(cfg).files.list(...)` + `google-oauth` |
| 读取文件元数据 | `Client(cfg).files.get(...)`（仅元数据——参见 Media 注意事项） |
| 创建文件夹/文件元数据 | `Client(cfg).files.create(...)` |
| 移动/重命名/删除 | `Client(cfg).files.update(...)` / `.delete(...)` |
| 共享文件/管理访问权限 | `Client(cfg).permissions.create/list/update/delete(...)` |
| 评论和回复 | `Client(cfg).comments.*` / `Client(cfg).replies.*` |
| 共享驱动器 | `Client(cfg).drives.*` |
| 变更通知/同步令牌 | `Client(cfg).changes.*` |

> **此客户端不支持：** 文件字节传输（上传/下载内容）。参见末尾的 Media 注意事项。用于元数据、组织和管理。

# 后端

连接器有两个 mops 包：

1. **`googledrive-client`** — 为 Drive REST API v3 生成的 Motoko 客户端。
   OAuth 无关：每个调用都通过其 `Config` 接收一个 bearer 令牌。
2. **`google-oauth`** — Google OAuth 2.0 机制（PKCE、授权 URL、代码交换、令牌刷新）。与其他 Google 连接器共享。这是一个**单独的 mops 包，与客户端一起添加**——它**不是** `googledrive-client` 本身的依赖项。

## 1. 添加依赖项

```bash
mops add googledrive-client
mops add google-oauth@0.2.0
```

## 2. 认证模型 — OAuth 2.0 PKCE，链上交换 + 刷新

Canister 通过 `google-oauth` 在链上执行 OAuth 流程：

1. 生成 PKCE `code_verifier` / `code_challenge`。
2. 构建 Google 授权 URL（`google-oauth`），重定向用户。
3. 用返回的授权代码交换访问 + 刷新令牌（`google-oauth.exchangeAuthorizationCode`）——**非复制**出调用。
4. 在 `401`/过期时，刷新访问令牌（`google-oauth.refreshAccessToken`）并重试。

**范围**（请求最严格的那个）：
- `https://www.googleapis.com/auth/drive.file` — 对应用创建/打开的文件进行文件级访问（首选，最低权限）。
- `.../auth/drive.readonly` — 对所有文件进行只读访问。
- `.../auth/drive.metadata.readonly` — 仅元数据。
- `.../auth/drive` — 完全访问（除非任务确实需要，否则避免）。

**刷新令牌不会轮换**——存储您收到的第一个刷新令牌（对每个用户稳定）；将其持久化到 canister 的稳定状态中，切勿存储在 Wasm 全局变量中。

## 3. `is_replicated = ?false` 是必需的

每个 Drive 出调用都携带 `Authorization: Bearer <token>`。在默认复制执行下，子网中的每个副本独立发出请求——增加成本，对于写入操作，会导致重复的副作用（例如创建 N 个文件副本）。**生成的 `defaultConfig` 已经设置 `is_replicated = ?false`**（通过客户端的 `isReplicated` 生成器选项），因此从 `defaultConfig` 开始即可获得正确的值，适用于**读取和写入**——保持 `?false` 并不要将其覆盖为 `?true`。（写入操作——PUT/DELETE/PATCH——由客户端为每次调用强制非复制。）

## 4. 使用客户端——嵌套外观

`googledrive-client` 提供一个 `Client.mo` 外观（使用 `fluentHierarchical` 生成），它一次性捕获 `Config` 并将 Drive 的资源层次结构作为嵌套类公开：

<!-- motoko-check:skip -->
```motoko
import { Client } "mo:googledrive-client/Client";
import { type Config; defaultConfig } "mo:googledrive-client/Config";

// 唯一与生成的 `defaultConfig` 不同的是 bearer 令牌，后者已经设置 `is_replicated = ?false`（非复制读取和写入）。
let cfg : Config = {
  defaultConfig with
  auth = ?(#bearer accessToken);   // 通过 google-oauth 获取/刷新的令牌
};

let drive = Client(cfg);

// 外观方法是 `async`（使用 `await` 而不是 `await*`）并按位置接收 Drive 端点的完整查询参数列表——参考 `mo:googledrive-client/Client` 中的生成签名。例如 `FilesResource.list` 开始 `uploadType : Text, oauthToken : Text, key : Text, fields : Text,
// accessToken : Text, alt : ?DriveAboutGetAltParameter, …`。
let files = await drive.files.list(/* …参见 FilesResource.list 签名… */);
let perm  = await drive.permissions.create(/* fileId, …, permission */);
```

（如果更喜欢扁平调用，也可以使用每个标签的 API 模块——`mo:googledrive-client/Apis/FilesApi`、`…/PermissionsApi` 等——外观只是为您捕获 `Config`。）

## 5. 可用的 API 表面

资源组（14），以 `Client(cfg).<group>.<method>` 的形式访问：

- **files** — 复制、创建、删除、获取、列出、更新、监视、生成 ID、列出标签、修改标签（元数据/组织；参见 Media 注意事项，用于创建/更新/获取/导出）
- **permissions** — 创建、删除、获取、列出、更新（共享）
- **comments** / **replies** — 创建、删除、获取、列出、更新
- **drives** — 创建、删除、获取、隐藏、列出、取消隐藏、更新（共享驱动器）
- **revisions** — 删除、获取、列出、更新
- **changes** — getStartPageToken、列出、监视（同步）
- **about** — 获取；**apps** — 获取、列出；**channels** — 停止

## 6. Media 注意事项（此客户端仅支持元数据）

`files.create` / `files.update`（上传）、`files.get?alt=media` /
`files.export` / `revisions.get`（下载）被生成为**JSON 类型**操作。它们将**不会**移动文件字节——多部分/可恢复上传和二进制下载不在客户端的 JSON-over-HTTPS 模型之外（并且会超出 IC 出调用大小限制）。仅用于元数据。如果构建确实需要移动文件内容，则必须手动编写（使用适当的二进制正文进行与内容主机分离的请求），并且此连接器目前不在此范围内。
