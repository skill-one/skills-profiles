# Appwrite CLI

`appwrite <command> --help` 已经列出了标志。直接阅读它，而不是猜测。

## 配置 vs `client`

一个**实际项目**（仓库、架构、函数、部署、CI）生活在 `appwrite.config.json` 中。初始化一次。之后进行拉取和推送。不要在每次命令中都使用 `appwrite client --project-id` — 配置已经指定了项目。

一个**一次性**（检查一个用户、修补一行、触碰一个你不会返回的远程）使用 `appwrite client`。不要为单个 API 调用搭建项目。

```bash
# 良好 — 项目
appwrite login
appwrite list-projects --json
appwrite init project --project-id <ID>
appwrite pull table
# 编辑 appwrite.config.json，然后：
appwrite push table --force

# 不良 — 将项目视为一堆 API 调用
appwrite tablesdb create-table --database-id main --table-id songs ...
appwrite tablesdb create-varchar-column --database-id main --table-id songs ...
# 下一次克隆没有记录这些

# 良好 — 一次性（已经登录）
appwrite client --project-id <ID>
appwrite users get --user-id <ID> --json

# 不良 — 一次性且会污染仓库
cd ~/some-unrelated-app && appwrite init project
```

没有会话？`appwrite client --endpoint https://<REGION>.cloud.appwrite.io/v1 --key "$APPWRITE_API_KEY" --project-id <ID>`。

`appwrite client --project-id` 在此目录（或向上查找找到的）中写入 `appwrite.config.json`。这就是快速链接文件夹的方式。不要在无关仓库的根目录下运行它。`APPWRITE_PROJECT_ID` / `APPWRITE_ENDPOINT` 会覆盖文件而不修改它 — 当你已经在一个项目中并需要针对其他内容进行一次性操作时，使用这些。

## 认证不是项目

| 层级 | 存在于 | 设置为 |
|---|---|---|
| 你是谁（会话或 API 密钥） | 全局 CLI 偏好设置 | `appwrite login` 或 `appwrite client --key` |
| 哪个项目 | `appwrite.config.json` | `init project`, `pull`, 或 `client --project-id` |

`init project` 与 **控制台** 通信。它需要一个登录会话。API 密钥无法列出组织。

```bash
# 良好 — CI 针对一个已提交的配置
appwrite client --key "$APPWRITE_API_KEY"
appwrite push function --force

# 不良 — CI 将密钥嵌入仓库
appwrite client --key 'standard_....'
# 并提交包含密钥的 appwrite.config.json
```

环境变量优于配置：`APPWRITE_PROJECT_ID`, `APPWRITE_ENDPOINT`, `APPWRITE_ORGANIZATION_ID`。将配置提交到仓库（不包含密钥）。将密钥放在环境中。

`--force` 跳过提示。代理和 CI 没有终端，所以需要确认的推送会失败（`Pass --force instead`）。询问用户，然后传递 `--force`。不要用它来跳过本地列为空的表更改。

`appwrite login --switch` 旋转保存的账户。`appwrite client --debug` 打印带有凭证屏蔽的有效端点/项目。`appwrite client --reset` 退出所有。

## 云端端点

`appwrite whoami` 显示 `https://cloud.appwrite.io/v1` 是**账户**登录主机。保留它。项目 API 调用使用区域主机（`https://fra.cloud.appwrite.io/v1`，等等）。`init project` 和 `client --project-id` 将该区域固定到配置中。自托管：一个端点用于两者。

```bash
# 良好 — 项目工作使用配置的区域端点
cat appwrite.config.json   # "endpoint": "https://fra.cloud.appwrite.io/v1"

# 不良 — “修复” whoami
appwrite client --endpoint https://fra.cloud.appwrite.io/v1
# 现在登录/会话调用会去一个它们不属于的区域主机
```

## 架构 vs 行

| 拉取 / 推送（配置） | 服务命令（不在配置中） |
|---|---|
| 设置、函数、站点、表和列、桶、团队、Webhook、主题 | 行、用户、文件、执行、消息 |

如果它应该能在全新克隆后存活，它应该属于配置。编辑文件，然后推送。使用 `tablesdb create-*` 或 `functions create` 创建相同资源会绕过下一次 `pull` / `push` 期望的文件。

`databases` 已弃用。使用 `tablesdb` 和 `push table`。

如果更改表显示远程值与本地空值，配置缺少这些字段。拉取该资源，然后推送。不要通过它使用 `--force`，也不要例行拉取所有内容 — `pull settings` 很慢。

```text
   id            │ key             │ remote │ local
  ───────────────┼─────────────────┼────────┼───────
   Service       │ account         │ true   │
   Auth method   │ email-password  │ true   │
```

```bash
# 良好 — 本地列是空的，所以先同步，然后推送
appwrite pull settings
appwrite push settings --force

# 不良 — 空本地，强制通过
appwrite push settings --force
```

`push all --all --force` 推送每个资源。除非你打算这样做，否则请限定范围（`push function --function-id api`）。

`unique()` 适用于一次性行或用户。你将要推送的资源需要一个在配置中稳定的 `$id`，以便下一次拉取匹配。

## 类型安全的应用程序代码

在针对 TablesDB 编写应用程序代码时，在发明接口、数据库 ID、表 ID 或列名之前，先检查 `appwrite.config.json`。生成器读取本地配置；它们不会检查远程架构。过时的配置会产生过时的代码。

如果远程架构是事实来源，请先用 `appwrite pull table` 更新配置。不要覆盖本地未推送的架构编辑进行拉取。如果本地配置领先，则按原样生成。

对于 TypeScript，优先使用 `appwrite generate`。它发出一个完整的 TablesDB 包装器：数据库和表选择、创建/更新有效载荷、返回的行、查询字段和查询值都由 TypeScript 检查。这比生成的模型接口更强。

```bash
appwrite generate
```

使用生成的 API 而不是退回到原始字符串 ID 和手写有效载荷类型：

```typescript
import { databases, type Songs } from "./generated/appwrite/index.js";

// 数据库查找使用其 ID；表查找使用配置中的其名称。
const songs = databases.use("main").use("Songs");

const page = await songs.list({
  queries: (query) => [
    query.equal("published", true),
    query.orderDesc("createdAt"),
    query.limit(20),
  ],
});

const first: Songs | undefined = page.rows[0];
```

不要猜测该示例中的字面量：读取生成的类型或配置。特别是，`.use()` 用于表时，它使用其 `name`，这可能与其 `$id` 不同。让编译器暴露拼写错误的表、列或错误的查询值。生成后运行项目的类型检查器。

`generate` 目前为 TypeScript 提供完整的包装器。它根据安装的 Appwrite 包检测客户端与服务器输出。服务器输出读取 `APPWRITE_API_KEY`；永远不要将此密钥放在生成的常量中或提交它。仅在检测错误时覆盖语言、导入源、模块扩展或客户端/服务器模式 — 阅读 `appwrite generate --help` 获取这些标志。

对于另一种支持的语言，或在项目故意直接使用常规 SDK 时，使用 `appwrite types <output-directory>`。它支持 TypeScript (`ts`)、JavaScript (`js`)、PHP (`php`)、Kotlin (`kotlin`)、Swift (`swift`)、Java (`java`)、Dart (`dart`) 和 C# (`cs`)。将这些短值传递给 `--language`；名称如 `typescript` 和 `csharp` 不是命令接受的值。生成的文件类型行数据，但它们**不**类型检查原始数据库/表 ID 或 `Query` 调用：

对于 TypeScript，在结果将作为模块导入时传递 `.ts` 目标。传递目录而不是文件会在其中创建 `appwrite.d.ts`。

```bash
appwrite types ./src/appwrite-types.ts --language ts
```

```typescript
import { Client, TablesDB } from "appwrite";
import type { Songs } from "./appwrite-types.js";

// 从 appwrite.config.json 读取这些值，并通过应用程序现有的配置机制公开它们。
const client = new Client()
  .setEndpoint("https://<REGION>.cloud.appwrite.io/v1")
  .setProject("<PROJECT_ID>");
const tablesDB = new TablesDB(client);

const page = await tablesDB.listRows<Songs>({
  databaseId: "main", // 仍然是一个未检查的字符串
  tableId: "songs",  // 仍然是一个未检查的字符串
});
```

不要将 `types --strict` 描述为“完全类型安全”。它仅将字段名转换为目标语言的命名约定。当目标是完全类型化的 TypeScript 表 API 时，请使用 `generate`。

生成的代码是派生输出。不要修补它以修复架构或命名问题；修复 `appwrite.config.json` 或生成器输入并重新生成。在每次表或列更改后，重新运行仓库使用的相同生成命令并运行其格式化器/类型检查器。保留仓库现有的输出路径和提交约定。

## 函数和站点

变量生活在 `<path>/.env` 中，而不是在 `appwrite.config.json` 中。`--with-variables` **替换**从该文件远程设置的值。除非你打算同步密钥，否则省略它。

```bash
# 良好 — 发送代码，保留远程变量不变
appwrite push function --function-id api --activate --force

# 不良 — 你没有在本地列出的远程变量消失了
appwrite push function --function-id api --with-variables --force

# 良好 — 部署而不会切换实时流量
appwrite push function --function-id api --activate=false --force
```

`--async` 在构建完成前返回。本地：`appwrite run function`。

## 查询和输出

优先使用 `--filter`, `--sort-asc` / `--sort-desc`, `--limit`, `--select`, `--cursor-after`。`--where` 已弃用。`--queries` 仅用于无法用标志表达的查询 JSON。

```bash
# 良好
appwrite users list \
  --filter 'emailVerification=true' \
  --sort-desc '$createdAt' \
  --limit 20 \
  --json

# 不良
appwrite users list --queries '[{"method":"equal","attribute":"emailVerification","values":[true]}]'
```

`--filter` 解析 `true` / `false` / `null`、数字和 JSON 数组。重复标志以进行 AND。列表页上限为 100；优先使用 `--cursor-after <lastId>` 而不是大的 `--offset`。

`--json` 用于脚本（空字段被丢弃）。`--raw` 用于未过滤的有效载荷。除非 `--show-secrets`，否则密钥保持屏蔽。

## 配置文件本身

CLI 从当前工作目录向上查找 `appwrite.config.json`（或遗留的 `appwrite.json`）。从 `functions/api/` 推送仍然会命中项目根目录。父目录中的随机配置会捕获你。

使用 `includes` 分割大型项目 — 每个值都是一个相对的 `.json` 数组。资源不能同时是内联和包含。函数和站点 `path` 值相对于包含文件解析，而不是仓库根目录。

不要凭记忆发明文件。使用 `init project` 或 `pull` 写入一个有效的文件。然后编辑。
