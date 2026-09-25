# 打包现有的 UI Bundle (2GP)

如何将当前项目中已存在的 **UI Bundle**（位于 `<packageDir>/uiBundles/<name>/`，其中 `<packageDir>` 是 `sfdx-project.json` 中的包目录——通常为 `force-app/main/default`）作为 **第二代包** (2GP) 进行打包，然后在另一个组织中安装/升级/卸载它。

**这是参考知识，不是按顺序执行的运行指南。** 用户已经有一个项目和可以构建（或可构建）的 Bundle。根据他们的意图，只应用匹配的部分：

**只回答所问。** 提供用户需要的那个部分的命令，以及它们各自针对的组织以及任何真实的注意事项——其他任何内容都不提供。不要重述其他部分，不要解释风味表，或者当用户询问单个步骤时不要重播完整的构建→创建→安装→发布序列。调试问题需要的是修复方案，而不是打包教程；安装问题需要的是 `sf package install` 命令和订阅者与开发中心之间的区别，而不是第一部分和第二部分。在这里，简洁就是正确。

| 用户想要…… | 前往…… |
|---|---|
| 决定托管与未托管 | [选择风味](#选择风味) |
| 使 Bundle 可打包 / 连接 CustomApplication | [第一部分](#第一部分--使现有-bundle-可打包) |
| 创建包或新版本 | [第二部分](#第二部分--创建包-开发中心独有) |
| 安装 / 升级 / 卸载 / 发布 | [第三部分](#第三部分--安装-升级-卸载-发布) |
| 调试失败 | [第四部分](#第四部分--调试-检查) + [故障排除](#故障排除) |

这项技能用于 **打包和跨组织分发** (`sf package …`)。对于将 Bundle 平移到一个组织中的简单源部署 (`sf project deploy …`)，请使用 **experience-ui-bundle-deploy**。在这里，永远不要使用 `sf project generate` 或 `sf template generate ui-bundle`——项目和 Bundle 已存在。
`MyReactApp` / `force-app` / `force-app/main/default` 是占位符；在下面它们出现的地方，替换用户的实际 Bundle 名称和他们的 `<packageDir>`。
确定性地解析 `<packageDir>`——永远不要在多包项目中猜测 `[0]`：
```bash
packageDir="$(scripts/find-bundle-package-dir.sh <bundleName>)"   # 遍历 packageDirectories；选择包含 uiBundles/<bundleName>/ 的条目
```

---

## 第 0 步 — 确认组织 (在触摸任何组织之前执行此操作)

不要假设默认组织。询问用户，或者读取 `sf org list`，然后重申您将使用的内容：

- **开发中心** (`devhub`) — 包创建、版本构建和源部署的位置。**始终需要。**
- **订阅者** (`subscriber`) — 您要安装到的组织。**仅安装 / 升级 / 卸载时需要。**

```bash
sf org list                                            # 连接的组织 + 默认开发中心
sf org list --json | jq -r '.result.nonScratchOrgs[]?.alias'
```

规则：
- **仅创建任务**（包或版本）→ 一个开发中心就足够了；**不要请求订阅者。**
- **安装任务** → 确认**两者**，并确认*哪一个是哪一个*。错误地安装到开发中心是一个常见且混乱的错误。

在下面将 `devhub` / `subscriber` 替换为实际别名。

**打包 ID 图例：** `0Ho…` 包 · `04t…` 可安装版本 (SubscriberPackageVersionId) · `05i…` Package2Version · `08c…` 版本创建请求 · `0Hf…` 安装请求 · `06y…` 卸载请求。

**运行时 ID 图例（在调试损坏的订阅者时有用）：** `9YE…` UI Bundle 行 · `9YF…` UIBundleApplication 连接 · `02u…` CustomApplication / TabSet · `0Zu…` ManagedContentSpace（工作区）· `0ap…` ManagedContentChannel (WEB_APP)。安装后 App Launcher 图标丢失几乎总是追溯到其中之一缺失或配置不当。

---

## 前提条件 — 每个人都忘记的 2GP 开关

2GP 需要在开发中心上有一个**手动 Setup 开关**，CLI 命令或元数据部署都无法切换它。**Setup → Dev Hub**，两者都需要：

1. **启用开发中心**，以及
2. **启用未托管的包和第二代托管包** ← 真正的开关。

直到 #2 开启，`sf package create` 返回 `NOT_FOUND`，并且任何 `Package2` 查询都返回 `sObject type 'Package2' is not supported`。没有 CLI 解决方案——切换开关。在开始之前进行验证：
```bash
# 清除 "0 records" = 2GP 开启； "sObject type 'Package2' is not supported" = 开关关闭
sf data query --target-org devhub --use-tooling-api --query "SELECT Id FROM Package2 LIMIT 1"
sf org display --target-org devhub --json | jq '.result.isDevHub'
```

---

## 选择风味

所有三种都是 2GP（相同的 `sf package` CLI）。在创建之前选择——它决定了命名空间、Bundle 在安装时的命名方式以及共存方式。

| | **托管** | **未托管—命名空间** | **未托管—组织依赖** |
|---|---|---|---|
| 命名空间 | 需要 | 需要 | 无（空 `""`） |
| 源可见性 | 隐藏（IP 保护） | 可见 / 可编辑 | 可见 / 可编辑 |
| 安装为 | `ns__Name` | `ns__Name` | 纯 `Name`（扁平） |
| 与本地同名的 Bundle 共存 | 是（命名空间过滤） | 是（命名空间过滤） | 否——冲突 |
| 升级行为 | 清除替换（锁定） | 替换，**覆盖订阅者编辑** | 替换，**覆盖订阅者编辑** |
| 失败升级时的回滚风险 | 是 | 是 | 无 |
| 典型用途 | ISV / AppExchange 分发 | 组织无关共享，源开放 | 包依赖于目标组织中已有的元数据 |

命名空间风味（托管、未托管命名空间）需要一个命名空间**注册并链接到此开发中心**（App Launcher → *命名空间注册表*）。没有注册的命名空间？使用**组织依赖的未托管**——它不需要任何命名空间。

### 链接如何工作（命名空间 ⇄ 开发中心）

命名空间存在于一个单独的 **开发者版 (DE) 组织**中，该组织拥有它；开发中心*借用*它通过链接注册。具体来说：

1. 注册一个 DE 组织并在其上注册一个命名空间（Setup → 包管理器 → 命名空间注册）。
2. 在开发中心中，App Launcher → *命名空间注册表* → **链接命名空间**，使用 DE 组织的凭据登录以将命名空间链接到此开发中心。
3. 将 `namespace` 设置在 `sfdx-project.json` 中为链接的命名空间缩写。如果这里的值未链接到目标开发中心，`sf package version create` 会因命名空间错误而失败（见 [故障排除](#故障排除)）。

一个 DE 组织可以承载多个命名空间，一个开发中心可以链接多个 DE 组织——因此，单个开发中心可以在多个命名空间下构建包。命名空间在版本创建时**锁定**，并随着构建版本中的每个 UI Bundle 行一起移动；您无法稍后更改它。

---

## 运行时模型——为什么风味很重要

您不必向回答常规问题解释这一点。当用户问*为什么*时，请使用它：为什么托管隐藏源，为什么命名空间安装是 `ns__Name`，为什么某些 URL 看起来不同，或者为什么未托管的升级擦除了他们的编辑。

- **源隔离。** 每个安装的 UI Bundle 都从其自己的 `*.salesforce.app` 原点渲染，与 `salesforce.com` 核心用户界面不同。层级：
  - `salesforce.com` — 1st-party 核心用户界面
  - `*.salesforce.app` — 2nd-party AFS 托管的 Bundle（无命名空间）
  - `<ns>.salesforce.app` — 3rd-party / 命名空间（托管 + 未托管命名空间）
  由于每个命名空间都获得自己的子域，来自不同包的两个 Bundle 可以共存而不会出现跨域泄漏。
- **IP 保护是仅托管属性。** 对于**托管**包，`getSourceZip()` 在订阅者组织中返回 null——编译的 `dist/` 存储为不透明内容，并且永远不会交还。对于**未托管**（命名空间或组织依赖），提供的二进制文件可被订阅者完全读取。
- **安装语义。** 托管和未托管命名空间安装为 `ns__Name`，并且可以与本地同名的 Bundle 共存。组织依赖的未托管没有命名空间——它安装为纯 `Name` 并与同名的本地 Bundle 冲突。
- **增量升级。** 在 `sf package install` 新的 `04t…` 中，平台比较每个传入 `dist/` 资产的 content-index 哈希与已存储的内容，并**跳过哈希未更改的任何资产**——一个触摸一个 Bundle 的补丁只重写该 Bundle 的更改文件。开发者拥有的工件（`dist/`，`ui-bundle.json`，ISV 基本权限集）被替换；订阅者拥有的状态（订阅者创建的权限集、自定义元数据、配置的域）被保留。
- **关闭开关。** Setup → 安全 → *多框架域* → 禁用一个配置的域。立即 404；元数据保持安装；可逆。

---

## 第一部分 — 使现有 Bundle 可打包

准备项目，以便它可以被打包并在组织中使用。只应用请求需要的部分。

### 1a. 在 `sfdx-project.json` 中设置 API 版本 + 命名空间

这里的 `namespace` 决定了您可以构建的风味（见上表），因此故意设置它——没有安全的默认值。将用户的真实注册命名空间替换为 `<ns>`；使用 `""` 表示组织依赖。

```bash
# 命名空间（托管 / 未托管命名空间）：<ns> 必须注册并链接到此开发中心
node -e "const fs=require('fs'),f='sfdx-project.json',j=JSON.parse(fs.readFileSync(f)); j.sourceApiVersion='68.0'; j.namespace='<ns>'; fs.writeFileSync(f,JSON.stringify(j,null,2))"

# 组织依赖的未托管：无命名空间
node -e "const fs=require('fs'),f='sfdx-project.json',j=JSON.parse(fs.readFileSync(f)); j.sourceApiVersion='68.0'; j.namespace=''; fs.writeFileSync(f,JSON.stringify(j,null,2))"

cat sfdx-project.json    # 在打包之前确认命名空间 + sourceApiVersion
```

- 托管 / 未托管命名空间 → `namespace` = 一个注册的、链接到此开发中心的命名空间。
- 组织依赖的未托管 → 将 `namespace` 设置为 `""`。
- 设置一个未链接到此开发中心的命名空间会导致稍后构建失败（见 [故障排除](#故障排除)）。

### 1b. 构建 Bundle — 在打包之前 `dist/` 必须存在

```bash
cd force-app/main/default/uiBundles/MyReactApp        # 真实的 Bundle 目录
npm install --no-audit --no-fund
npm run build
cd -
```

在 `dist/` 存在并且应用程序安装但**渲染为空白**之前进行打包或部署——Bundle 随其构建的资产一起打包。总是先构建。

### 1c. 连接 CustomApplication（如果 Bundle 必须作为 Salesforce 应用程序启动）

当 Bundle 以其他方式引用时（嵌入在 FlexiPage、Experience Cloud 站点中等）跳过此步骤。否则**阅读** `<SKILL_DIR>/assets/CustomApplication.app-meta.xml`（其中 `<SKILL_DIR>` 是此技能自己的目录的绝对路径），将每个 `MyReactApp` 替换为真实的 Bundle 开发者名称，并将结果写入用户的项目的 `<packageDir>/applications/` 下。使用 Bundle 的**开发者名称**编写 `<uiBundle>`——在同一包中不需要前缀；跨命名空间它解析为 `ns__Name`（命名空间）或 `c__Name`（无命名空间）。

App Launcher 图标实际关心的三个字段——如果它们设置正确，安装的订阅者不会看到损坏的图标：

- `<uiType>Lightning</uiType>` — App Launcher 渲染它所需的
- `<navType>Standard</navType>` — 标准导航容器
- `<formFactors>Large</formFactors>` — 桌面表单因素（验证仅在安装时进行，因此缺少/错误的值通过部署通过，但隐藏图标）

```bash
mkdir -p force-app/main/default/applications
# 然后写入替换的模板到：
#   force-app/main/default/applications/<BundleName>.app-meta.xml
```

### 1d. 将源部署到开发中心（以便在 `package create` 之前存在元数据）

```bash
sf project deploy start --source-dir force-app --target-org devhub --api-version 68.0 --wait 30
```

### 1e. 通过权限集授予权限（如果 1c 添加了 CustomApplication 并且应用程序必须无需手动 Setup 点击即可访问）

读取 `<SKILL_DIR>/assets/PermissionSet.permissionset-meta.xml`，将 `MyReactApp` 替换为真实的 Bundle 名称（在 `<application>` 和标签中），将结果写入用户的项目的，然后部署和分配：

```bash
mkdir -p force-app/main/default/permissionsets
# 写入替换的模板到：
#   force-app/main/default/permissionsets/<BundleName>_Access.permissionset-meta.xml
sf project deploy start --source-dir force-app/main/default/permissionsets/MyReactApp_Access.permissionset-meta.xml --target-org devhub --api-version 68.0 --wait 30
sf org assign permset --name MyReactApp_Access --target-org devhub
```

---

## 第二部分 — 创建包（仅开发中心）

不涉及订阅者组织。`sf package create` 运行**一次**（注册 `0Ho…` 容器）；之后可以多次构建可安装的 `04t…` 版本。选择上面的一种风味：

```bash
# 托管
sf package create --name MyReactApp --package-type Managed --path force-app --target-dev-hub devhub

# 未托管，命名空间  (命名空间来自 sfdx-project.json)
sf package create --name MyReactApp --package-type Unlocked --path force-app --target-dev-hub devhub

# 未托管，组织依赖 (无命名空间)
sf package create --name MyReactApp --package-type Unlocked --org-dependent --path force-app --target-dev-hub devhub
```

然后构建一个版本：

```bash
sf package version create --package MyReactApp --installation-key-bypass --wait 20 --target-dev-hub devhub
# 一个特定/补丁版本：
sf package version create --package MyReactApp --version-number 1.0.1 --wait 20 --target-dev-hub devhub
```

`--version-number 1.0.0.NEXT` 自动递增构建号；固定的 `1.0.1` 会固定它。`--installation-key-bypass` 构建一个未受保护的版本（没有安装密钥）；省略它并通过 `--installation-key <key>` 来控制安装。

### 鲁棒的版本创建（即使在缓慢的开发中心队列中也能生存）

`--wait` 可能会在构建排队时超时，丢失请求句柄。异步提交，捕获 `08c…` id，轮询：

```bash
REQ=$(sf package version create --package MyReactApp --installation-key-bypass \
  --skip-validation --target-dev-hub devhub --json | jq -r '.result.Id')
echo "request: $REQ"
while :; do
  J=$(sf package version create report -i "$REQ" --target-dev-hub devhub --json)
  ST=$(echo "$J" | jq -r '.result[0].Status'); echo "status: $ST"
  case "$ST" in
    Success) echo "$J" | jq -r '.result[0].SubscriberPackageVersionId'; break;;
    Error)   echo "$J" | jq -r '.result[0].Error[]? // "build failed"'; break;;
  esac
  sleep 30
done
```

`--skip-validation` 更快，但会产生一个**测试版**（不能发布，测试版不能升级测试版——见第三部分）。为了可发布的构建，放弃它。随时恢复排队的构建：
`sf package version create report -i 08c… --target-dev-hub devhub`

---

## 第三部分 — 安装 / 升级 / 卸载 / 发布

**首先确认订阅者别名（第 0 步）。** 这里的一切都针对订阅者——除了**发布**，它在开发中心上运行。

```bash
# 新安装
sf package install --package 04t… --target-org subscriber --wait 10
#   如果版本使用密钥构建，请添加 --installation-key <key>
#   添加 --publish-wait 10 以等待版本完成发布

# 升级（新版本覆盖旧版本）
sf package install --package 04t…v2 --target-org subscriber --upgrade-type Mixed --wait 10
#   --upgrade-type: Mixed (默认) | DeprecateOnly | Delete (破坏性——小心)

# 卸载
sf package uninstall --package 04t… --target-org subscriber --wait 20

# 发布一个托管版本为已发布/不可变——在开发中心上运行，不可逆
sf package version promote --package 04t… --target-dev-hub devhub
```

**测试版不能升级测试版。** 一个 `--skip-validation` (测试版) v0.2 覆盖一个测试版 v0.1 会失败，提示 *"Cannot upgrade beta package."* 要么**发布** v0.1（托管），要么**卸载** v0.1，然后安装 v0.2。

**未托管的升级会覆盖订阅者对 Bundle 的编辑**。组织依赖的没有失败升级时的回滚；命名空间风味有。

### 鲁棒的安装（确认它实际上已落地）

`sf package install --wait` 可能会退出 0，而请求仍在 IN_PROGRESS 状态——一个虚假的成功。验证：

```bash
sf package install --package 04t… --target-org subscriber --wait 20 --no-prompt
sf package installed list --target-org subscriber --json \
  | jq -r '.result[]? | select(.SubscriberPackageVersionId=="04t…") | .SubscriberPackageVersionId'
```

打印为空 → 服务器端仍在处理；在几分钟后轮询 `sf package installed list` 才能得出它失败的结论。

---

## 第四部分 — 调试 / 检查

主要是只读的。当诊断失败或检查状态时，请使用这些。

```bash
# 开发中心状态
sf org display --target-org devhub --json | jq '{isDevHub:.result.isDevHub, user:.result.username, instance:.result.instanceUrl, api:.result.apiVersion}'

# 2GP 开启？ (第一个根本原因)
sf data query --target-org devhub --use-tooling-api --query "SELECT Id, Name, NamespacePrefix, ContainerOptions FROM Package2"

# 开发中心上的包和版本
sf package list --target-dev-hub devhub
sf package version list --packages MyReactApp --target-dev-hub devhub --verbose

# 版本创建失败——状态 + Error[]
sf package version create list --target-dev-hub devhub
sf package version create report -i 08c… --target-dev-hub devhub
sf data query --target-org devhub --use-tooling-api \
  --query "SELECT Id, Status, Package2Id, Error FROM Package2VersionCreateRequest ORDER BY CreatedDate DESC LIMIT 5"

# 一个版本的详细信息
sf package version report --package 04t… --target-dev-hub devhub

# 订阅者中安装了什么
sf package installed list --target-org subscriber --json \
  | jq -r '.result[]? | "\(.SubscriberPackageName) \(.SubscriberPackageVersionNumber) \(.SubscriberPackageVersionId)"'

# 安装/卸载卡在 IN_PROGRESS
sf package install report   --request-id 0Hf… --target-org subscriber
sf package uninstall report --request-id 06y… --target-org subscriber

# 部署失败（在您甚至无法打包之前）
sf project deploy start --source-dir force-app --target-org devhub --dry-run --wait 30
sf project deploy report --target-org devhub

# Bundle 渲染为空白——确认构建的资产已发货
ls -la force-app/main/default/uiBundles/MyReactApp/dist
```

---

## 故障排除

| 症状 | 原因 / 修复 |
|---|---|
| `sObject type 'Package2' is not supported` | 2GP 开关关闭 — **Setup → Dev Hub** → 启用 "Unlocked & Second-Gen Managed Packages"（手动，没有 CLI 修复）。 |
| `sf package create` → `NOT_FOUND` | 同上 — 2GP 未配置。启用开关，重新认证。 |
| `isDevHub: false/null` 启用后 | 缓存的 CLI 登录 — 重新认证。信任 `Package2` 查询 + `package create`，而不是缓存的标志。 |
| `version create` 挂起 / `--wait` 超时 | 构建排队。使用异步提交 + `version create report -i 08c…` 轮询；稍后使用相同的 id 恢复。 |
| `install --wait` 退出 0 但应用程序缺失 | 服务器端仍在处理。使用 `sf package installed list` 进行确认；几分钟后再轮询。 |
| "Cannot upgrade beta package" | 测试版不能升级测试版。发布 v0.1（托管）或卸载它，然后安装 v0.2。 |
| 托管/命名空间构建时的命名空间错误 | 命名空间未注册/链接到此开发中心（App Launcher → *命名空间注册表*），或者切换到组织依赖的未托管（无命名空间）。 |
| 应用程序安装但渲染为空白 | 在部署/打包之前未构建 Bundle — `npm run build`，确认 `dist/`，重新部署，重新构建版本。 |
| 安装到错误的组织 | 在第 0 步中确认了错误的别名。重新检查 `sf org list`；`subscriber` ≠ `devhub`。 |
| 组织依赖的 Bundle 与本地 Bundle 冲突 | 两者都使用一个裸（空前缀）名称。使用命名空间风味，或者重命名。 |

## 注意事项

- **首先确认组织。** 开发中心始终；仅安装/升级/卸载时才需要订阅者。在仅创建任务上不要请求订阅者。
- **完整运行的顺序：** 构建 Bundle → 部署源 → `package create`（一次）→ `package version create`（每个发布）→ `install` → `promote`（仅托管）。
- 对于内部 Salesforce 打包问题，权威渠道是 **#packaging**。
- **权威外部文档**（用于更深入的参考）：
  - 第二代托管打包开发者指南 — <https://developer.salesforce.com/docs/atlas.en-us.pkg2_dev.meta/pkg2_dev/sfdx_dev_dev2gp.htm>
    （托管 / AppExchange 风味：工作流、组件、分发、推送升级、1GP→2GP 间隙）。
  - 未托管的包共享相同的 `sf package` CLI；查看同一指南的“未托管包”部分，以了解未托管命名空间和组织依赖的风味。
