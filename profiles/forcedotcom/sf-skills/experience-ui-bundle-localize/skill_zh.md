# 本地化 UI 包

本地化 UI 包：将面向用户字符串提取到 Salesforce 自定义标签中，在平台 SDK 后端连接运行时 i18n 库，并在不同区域之间验证标签。

此文件是**框架无关的工作流 + 护栏骨干**。框架特定的细节——哪个 i18n 库、翻译调用约定、扫描的文件、连接形状以及深度文档——存在于每个框架的参考中。

## 一段式的思维模型

UI 包不能像 LWC 那样使用编译时标签导入（`@salesforce/label/*` 在平台的编译器内部解析，而你的独立包不会通过编译器）。相反，你的应用通过 Salesforce GraphQL UI API 在运行时获取标签，并将它们交给标准的 i18n 库来渲染。平台 SDK 提供了运行时管道：一个检测用户语言的检测器、一个通过 GraphQL 获取标签的后端以及一个上下文获取器。你编写两个薄文件——一个简短的初始化文件将 SDK 组件连接到你的 i18n 库，一个清单列出你的应用使用的哪些标签——然后将标签本身作为 Salesforce 自定义标签元数据编写。确切的库和调用约定是框架特定的；请参阅你的框架参考。

---

## 第 0 步：路由任务

| 任务是… | 前往 |
|---|---|
| 包不存在 | **experience-ui-bundle-frontend-generate** 技能 |
| 部署带有其标签的应用 | **experience-ui-bundle-deploy** 技能 |
| 配置站点语言或 `sfdc_cms__languageSettings` | **experience-ui-bundle-site-generate** 技能 |
| 本地化现有包 | **确定框架（下方），然后是工作流** |

**确定框架。** 它通常已经由调用上下文决定——由调用此技能的协调器技能向下传递，或在用户的请求中声明。使用那个。

此技能支持的框架正好是 `<SKILL_DIR>/references/` 下方的参考文件夹，每个文件夹都包含一个 `localize.md`（所以 `react` → `<SKILL_DIR>/references/react/localize.md`）。这是唯一的真实来源——添加框架意味着添加参考文件夹，这里没有变化。

- **如果框架已知**——打开 `<SKILL_DIR>/references/<framework>/localize.md` 并将其与这个骨干一起保留。它提供了库、调用约定、要扫描的文件和连接代码。
- **如果未知**（一个独立的运行，没有人说哪个）——在询问任何人之前，在应用 / uiBundle 根目录上运行确定性检测器：

  ```bash
  bash "<SKILL_DIR>/scripts/detect-framework.sh" "<app-or-uiBundle-root>"
  ```

  它结合了根目录下方的 `angular.json`、任何非 `node_modules` `package.json` 中的 `@angular/core` / `react` 以及源文件签名，然后打印一个标记并设置匹配的退出代码：
  - `react` 或 `angular`（退出 0）→ 使用该框架。**不要询问用户**——检测是确定性的。打开 `<SKILL_DIR>/references/<framework>/localize.md`。
  - `ambiguous`（退出 2）→ 两个框架都存在。列出 `<SKILL_DIR>/references/` 并询问用户要本地化哪个。如果他们命名一个没有匹配参考文件夹的框架，它在这里不受支持——停止。
  - `unknown`（退出 3）→ **未检测到支持的框架。终止工作流。** 不要猜测，不要继续：报告在包中未发现 React 或 Angular 信号，因此无法继续本地化，并在此处停止。

在下面的步骤中，`<framework>` 指的是此处选择的文件夹。确定性检查脚本按耦合分割：
- **框架无关，共享在 `<SKILL_DIR>/scripts/`** — `detect-framework.sh`（上方的第 0 步检测器）、`check-org-api-version.sh` 和 `detect-bundle-type.sh`（纯组织/元数据检查），以及 `check-manifest-registered.sh`（无知的骨架；它需要 `--framework <framework>` 来选择调用站点语法）。
- **框架特定，在 `<SKILL_DIR>/references/<framework>/` 下** — `check-i18n-wired.sh`（它的清单到后端检测是 i18n 库形状的，所以每个框架都提供自己的）。

---

## 前置条件：编辑前验证

| # | 要求 | 验证 | 缺失 |
|---|---|---|---|
| 1 | 它是一个 `uiBundles/*/src/` 项目（React 或 Angular） | 项目结构匹配 | 不是 UI 包 → 路由到正确的技能 |
| 2 | 平台 SDK、UI 包和构建插件兄弟已安装并一致（≥11.49.3） | UI 包目录中的 `package.json` | 告知用户对齐和升级它们；不能继续 |
| 3 | 你可以识别应用挂载的位置 | 读取入口文件（见框架参考） | 没有明确的挂载点 → 询问用户指出它 |
| 4 | 目标组织实际上支持 API v68.0+（运行时标签 GraphQL 对于 UI 包随发布 264 提供） | 运行下方的运行时组织发布检查 | 组织的最大 API 版本低于 v68.0（发布 262 或更早）→ 不能继续；重新定位发布 264+ 的组织或升级组织 |
| 5 | 包是认证的 B2E 或请求/上下文明确标识 B2C 站点，而不是 B2B | 运行下方的包类型检测并使用请求/上下文识别站点产品身份 | 明确 B2B → 拒绝；站点类型未明确 → 询问用户并停止，直到确认；B2C 也需要前提条件 6 |
| 6 | 仅限 B2C，管理员已启用 `GraphQLApiOrgPrefForGuestUsers` | 询问管理员确认组织偏好已启用 | 不要启用它；解释没有它，没有它客座 GraphQL 返回 HTTP 403，并停止（依赖：W-23854208） |

**运行时组织发布检查（前提条件 4）。** 解析 UI 包在运行时标签的 `platform.labels` GraphQL 路径随 Salesforce 发布 264（API v68.0 或更高）提供。`sfdx-project.json` 中的 `sourceApiVersion` 记录了你声明的，而不是组织支持什么，所以一个指向较旧组织的较新 CLI 可以通过静态文件检查，然后在运行时失败。在连接任何东西之前，查询组织的实际最大 API 版本：

```bash
bash <SKILL_DIR>/scripts/check-org-api-version.sh <org-alias-or-username>
```

退出 `0` → 组织支持 v68.0+，继续。退出 `1` → 组织太旧或无法访问；不要编写 i18n 连接或标签，向用户报告版本不匹配并停止。 (`sf api request rest` 在脚本内部保持身份验证在 CLI 传输层，因此不会将访问令牌输入上下文。)

**包类型检测（前提条件 5）。** 包的类型决定哪个本地化分支适用。它是框架无关的（纯 Salesforce 元数据）。传递包目录的完整路径；脚本从它派生元数据根，所以当前目录无关紧要：

```bash
bash <SKILL_DIR>/scripts/detect-bundle-type.sh <path-to-uiBundles/<name>/ dir>
```

根据退出码合同采取行动：`0` → 认证应用（B2E 或核心内部内部），使用 B2E 分支；`10` → 绑定公共站点应用容器候选，这意味着元数据证明站点绑定和客座访问，但**不是** B2C 与 B2B；`11` → 绑定非公共/不支持站点，停止；`12` → 存在 CustomApplication 和一个站点绑定，询问哪个运行时上下文是本地化目标；`13` → 多个匹配的体验站点绑定，显示报告的站点名称并询问哪个站点/运行时上下文是目标；`2` → 未绑定/未知，报告脚本输出并停止，而不是猜测。

对于退出 `10`，通过显式请求/上下文路由：如果它说 **B2C**，请确认前提条件 6 并使用 B2C 分支；如果它说 **B2B**，则拒绝它；如果产品类型不明确，询问用户站点是 B2C 还是 B2B 并停止，直到确认。对于退出 `12` 和 `13`，要求用户选择运行时上下文（对于退出 `13` 还选择站点），然后应用该分支的回退和前提条件。永远不要从 `DigitalExperienceConfig`、`appSpace`、`appContainer` 或 `AUTHENTICATED_WITH_PUBLIC_ACCESS_ENABLED` 推断 B2C；认证值表示客座访问已启用。

对于 B2C，只有组织管理员可以启用 `GraphQLApiOrgPrefForGuestUsers`；永远不要配置或更改它。没有它，客座标签请求返回 HTTP 403。通过 W-23854208 跟踪可用性。

如果前提条件未满足，停止：向用户报告特定块并记录一项计划项目，一旦解决就返回。不要向 B2B 或未知包添加 i18n 连接或 TODO 标记。

---

## 工作流：五个步骤

每个步骤都有一个**完成标准**和一个**继续前的确认**暂停。框架特定细节（文件扩展名、翻译调用、安装、初始化代码）来自 `<SKILL_DIR>/references/<framework>/localize.md>`。

### 第 1 步：检测

**目标：** 扫描框架的组件文件以查找面向用户的硬编码字符串。（框架参考命名要扫描的文件扩展名。）

**要扫描的内容：**
- 在标记中向用户显示的字符串字面量：标题中的 `Welcome` → 候选
- 向用户显示的字符串属性：`placeholder="Enter name"` → 候选
- 面向用户的可访问文本：`aria-label`、`aria-describedby`、`alt` → 候选（屏幕阅读器用户听到这些，所以它们也必须本地化）

**要跳过的内容：**
- 导入语句
- 对象键 / 属性名
- `data-*` 属性（机器可读）
- 测试 ID（`data-testid`、`id` 属性）
- 已经用翻译调用包装的文本
- 控制台日志、向开发者抛出的错误消息（不是面向用户的）
- 类名、文件路径、技术常量

**操作：**
1. 扫描框架的组件文件的 `src/` 目录
2. 提取候选项，为每个显示文件路径 + 行号
3. 向开发者显示列表

**完成标准：**
开发者确认列表（或编辑它以删除误报）。

**暂停：** "我在 M 个组件中发现了 N 个面向用户的字符串。这里是列表：[显示文件:行 + 字符串]。看起来对吗？[确认 / 编辑列表 / 跳过一些]"

---

### 第 2 步：提取

**目标：** 对于每个确认的字符串，添加一个自定义标签并将字面量替换为翻译调用。

**每个字符串的操作：**
1. **提出一个键名**，格式：`<上下文>_<角色>`（例如，`"Welcome"` → `Welcome_Text`，`"Save"` → `Save_Button`，`"Failed to save"` → `Save_Failed_Message`）。遵循命名：PascalCase 单词，部分之间用下划线分隔，足够描述以唯一标识。
2. **将标签添加到** `force-app/main/default/labels/CustomLabels.labels-meta.xml`：
   ```xml
   <labels>
     <fullName>Welcome_Text</fullName>
     <language>en_US</language>
     <protected>false</protected>
     <shortDescription>Welcome banner heading</shortDescription>
     <value>Welcome</value>
   </labels>
   ```
   （完整的 XML 结构：`references/common/label-xml.md`）
3. **用你的框架的翻译调用替换字符串**，并添加任何必需的导入/注入。确切的调用约定在框架参考中。

**完成标准：**
每个确认的字符串都有一个 `CustomLabels` 条目和原始位置中的一个翻译调用。

**暂停：** "对于每个字符串，我将添加一个 Custom Label 并用翻译调用替换字面量。这里是我提出的键：[显示字符串 → 命名空间:键映射]。应用这些编辑？[是 / 审阅每个]"

---

### 第 3 步：注册

**目标：** 将每个键添加到标签清单中，以便 i18n 运行时知道要获取它。

**操作：**
1. 将每个键添加到 `src/i18n/label-manifest.ts` 中的清单数组：
   ```typescript
   export const labelManifest = [
     "c:Welcome_Text",
     "c:Save_Button",
     "c:Save_Failed_Message",
   ];
   ```
   如果文件不存在，第 4 步会创建它；完成检查下方会报告其缺失，所以不要手动测试文件是否存在。

**完成标准：**
从 UI 包目录运行 `check-manifest-registered.sh`（它相对于当前目录扫描 `src/`），并报告它返回的任何错误。它拥有确定性检查：它将每个翻译调用站点与清单进行交叉检查，并将缺少 `label-manifest.ts`（当存在调用站点时）视为失败。被调用但未注册的键在运行时显示为其自己的字面量名称，没有错误，这个静默失败陷阱保护了这一点。

```bash
cd <path-to-uiBundles/<name>/ dir>   # 脚本相对于此扫描 src/
bash <SKILL_DIR>/scripts/check-manifest-registered.sh --framework <framework>
```

根据退出码分支：`0`，每个键都已注册（或没有调用站点要门控），继续。`1`，清单缺失或列出的键不在其中；构建或添加它们（第 4 步会构建文件）并重新运行。`64`，使用错误：源目录不存在（当前工作目录错误或参数错误）。这**不是**“键缺失”的结果；不要构建。修复路径并重新运行。

**暂停：** "添加了 N 个条目到 label-manifest.ts。check-manifest-registered.sh 通过了：[确认]。"

---

### 第 4 步：连接

**目标：** 确保存在 i18n 连接；如果应用还没有 i18n，则构建它。安装命令、连接代码和 B2E 与 B2C 回退配置都在框架参考中 (`references/<framework>/localize.md` 和其 `i18n-setup.md`)。

**检查：**
从 UI 包目录运行 `check-i18n-wired.sh`（它相对于当前目录扫描 `src/`），并报告它返回的内容。脚本拥有整个确定性检查：它查找框架的 i18n 连接（React：在启动时被调用的 `initI18n()` 初始化文件；Angular：`provideTranslateService`/`TranslateModule.forRoot` 注册自定义 `TranslateLoader`，通过 `TranslateService.use` 在启动时加载），当存在时，它还报告标签清单是否导入并实际到达标签后端/加载器。不要通过读取文件自己重新推导任何内容。

```bash
cd <path-to-uiBundles/<name>/ dir>   # 脚本相对于此扫描 src/
bash <SKILL_DIR>/references/<framework>/check-i18n-wired.sh
```

根据**退出码**分支（打印的消息命名你的报告，但决定是代码）：
- 退出 `0` → 完全连接，清单到达标签后端/加载器；只需添加新键。
- 退出 `1` → 不存在 i18n 连接；根据框架参考构建整个设置。
- 退出 `2` → 连接存在但不完整（React：启动时未调用初始化；Angular：加载器未注册，或注册但未启动 `TranslateService.use`）；**不要**重新构建或覆盖它。仅添加消息命名的缺失连接，然后重新运行。
- 退出 `3` → 启动时连接，但脚本**无法确认**清单到达后端/加载器。最后一个检查是文本启发式：清单可能通过变量、展开、工厂或脚本无法看到的帮助程序连接，所以将退出 3 视为“编辑前验证”，而不是“确定损坏”。打开消息命名的文件并确认，然后协调；永远不要重新构建或重复已经工作的连接。
- 退出 `64` → 使用错误：源目录不存在（当前工作目录错误或参数错误）。这**不是**“没有连接”的结果；不要构建。修复路径并重新运行。

**B2C 覆盖——即使退出 `0` 也适用：** 连接检查仅证明 i18n *存在*，而不是它对 B2C 正确。一个带有 B2E 连接的种子——`dir = ctx.dir` 和一个**没有** `labelFallback` 的加载器——在退出 `0` 时通过 `check-i18n-wired.sh` 但对 B2C 站点是**错误的**。如果站点是 B2C，不要在“添加新键”时停止：打开 `src/i18n/index.ts`（或框架的初始化文件），使用 `resolvedLang`（=`SFDC_ENV.language || ctx.lang`；检测器不会读取 `SFDC_ENV.language`），(a) 添加 `labelFallback: "USER_DEFAULT"`，(b) 从它设置方向——`i18next.dir(resolvedLang)`，永远不要 `ctx.dir`，以及 (c) 在其中初始化——React `lng: resolvedLang` 在 `i18next.init`；Angular `translate.use(resolvedLang)`。见 `references/<framework>/i18n-setup.md`。永远不要在 B2C 站点上保留 B2E 连接。

**完成标准：**
i18n 连接存在并在启动时调用一次；清单连接到标签后端/加载器。对于 B2C，所有三个 `resolvedLang` 覆盖都应用——`USER_DEFAULT` 回退、显示语言（React `lng`，Angular `translate.use`），以及 `i18next.dir(resolvedLang)` 方向——不是种子的 B2E 默认。
遵循框架参考以获取确切的构建，并且永远不要覆盖现有的连接。

**暂停：** "i18n 设置[存在 / 创建]。它在启动时加载：[确认]。"

---

### 第 5 步：验证

**目标：** 指导开发者验证标签在第二种语言中渲染。

**操作：** 遵循 `references/common/verifying.md` 中分支特定的程序。

对于 **B2E**，激活第二种语言，编写或检索其翻译元数据，针对目标组织构建，仅部署目标包和标签元数据，然后更改认证用户的语言并重新加载。

对于 **B2C**，验证配置的站点语言、URL 路由、`SFDC_ENV.language`、完整重新加载语言切换器、本地化本地预览、客座 GraphQL 访问和缓存清除，如框架参考中详细说明。

部署包、标签和翻译不会发布体验站点。将 `sf community publish` 视为单独的 go-live 变化：显示确切的站点和目标组织，然后在立即运行它之前等待明确的用户确认。

**如果它不渲染：** 检查 `references/common/gotchas.md` 中的陷阱：
- 未注册的清单键（第 3 步遗漏了一个标签）
- API 版本不匹配（针对不同的组织构建）
- 过期的标签缓存（React：`i18next_res_*` 在 localStorage 中；Angular：内存中，重新加载会重新获取）
- B2C 客座 GraphQL 403（`GraphQLApiOrgPrefForGuestUsers` 没有管理员启用）
- B2C 路由、站点语言和 `SFDC_ENV.language` 不一致

**完成标准：**
标签在 ≥2 区域中渲染，或者识别了阻止的陷阱。

**暂停：** "为了验证：在 Translation Workbench 中激活第二种语言，编写一个翻译（我可以构建翻译文件），
构建/部署，并重新加载。我想我构建 [语言] 的翻译文件吗？[是 / 我会手动做]"

---

## 边缘情况：优雅处理

- **已经本地化的代码**：检测现有的翻译调用使用 / 一个填充的清单；提供添加到设置而不是重新构建所有内容。
- **没有找到字符串**：干净地报告并停止；不要发明工作。
- **应用还没有 i18n 设置**：第 4 步首先构建两个文件，然后第 3 步才能注册任何内容。
- **部分设置**（清单存在但初始化缺失，或反之），协调现有的内容；永远不要覆盖现有的连接。
- **B2B 站点**：明确拒绝它。B2C 支持不意味着 B2B 支持。

---

## 护栏：永远不要倒退这些

1. **永远不要机器翻译可部署元数据。** 构建一个格式良好的 `<Translations>` 文档，每个标签都有一个关闭的 `<customLabels>` 块，以及 XML 转义英语源文本。保留占位符，并在完成之前解析两个元数据文件。翻译者通过手动或通过 Translation Workbench 替换构建值；永远不要为它们调用 MT API。
2. **永远不要注册没有标签的键。** 清单条目计数必须等于标签计数（第 3 步标准）。未注册的键会将其自己的字面量名称渲染，没有控制台警告。这是最常见的本地化错误。
3. **永远不要覆盖现有的 i18n 连接。** 如果第 4 步发现现有的 `initI18n()`，则协调（如果缺失，则添加清单导入）而不是替换整个文件。
4. **每个文件都必须是客户安全的。** 不允许 `webapps`、核心仅路径或任何内部基础设施引用。像为外部客户在 SFDX 项目中编写一样。
5. **永远不要隐式发布 B2C 站点。** 元数据部署和站点发布是分开的。仅在显示站点和组织并收到明确确认后立即运行 `sf community publish`。
