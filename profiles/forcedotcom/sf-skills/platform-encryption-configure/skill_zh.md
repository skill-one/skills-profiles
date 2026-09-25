# 配置平台加密

通过生成启用它的元数据并选择正确的设置来配置 Salesforce Shield 平台加密：字段应使用哪种加密方案、哪种密钥管理模型符合要求，以及租户密钥生命周期如何工作。这是一个**混合**技能——它发出可部署的 `*.settings-meta.xml` / `*.field-meta.xml`，其中平台加密暴露了真实的元数据 API 界面，并返回基于实际的指导，其中操作仅限于 UI/REST。

## 范围

- **在范围内**：在字段上选择和应用 `encryptionScheme`；通过 `PlatformEncryptionSettings` / `EncryptionKeySettings` 启用确定性加密、缓存密钥、外部密钥管理和重放检测；解释 BYOK / BYOKMS / EKM / 缓存密钥模型；租户密钥轮换和销毁语义；加密字段的查询行为。
- **超出范围**：一个没有加密的普通自定义字段（使用 `platform-custom-field-generate`）；原始元数据 API 字段引用（使用 `platform-metadata-api-context-get`）；经典加密（`EncryptedText` 字段）——这是一个单独的、遗留功能；将元数据部署/推送到组织（这属于部署生命周期技能）。

---

## 必需输入

在进行下一步之前收集或推断：

- **问题类型**：用户是在询问可部署的工件（设置文件、加密字段）还是指导（哪种模型、当我轮换密钥时会发生什么）？可部署 → 从 `assets/` 生成 XML。指导 → 从 `references/` 获取答案。**当问题是解释、确认或比较时，它就是指导**——"对吗？"、"关系是什么？"、"我们可以…吗？"、"是否有排序要求？"**"解释 X 和 Y 的区别"、"我们应该使用哪种密钥模型？"**——**即使用户也提到他们即将编写、部署或编写设置，也是如此。编写设置是*用户*的操作；它不会使技能的交付成果成为文件。只有明确的"生成/创建/给我文件/这是我的字段，加密它"才是工件请求。**
- **密钥模型选择问题是指导，不是可部署元数据。** "解释 BYOK 与外部密钥管理 / BYOKMS / EKM / 缓存密钥"、"哪个模型将密钥材料保留在 Salesforce 之外"、"我们应该使用 BYOK 还是 EKM？"→ 用**单个 markdown 答案文件**（指导编写）回答它们，而不是可部署的 `*.settings-meta.xml`。**在答案中命名启用设置（例如 `canExternalKeyManagement`、`enableCacheOnlyKeys`）不会将其变成设置工件**——在答案文件中内联引用字段名；**不要**发出 `EncryptionKey.settings-meta.xml`，除非用户明确说"生成/创建设置文件。"
- **字段加密目标**（用于字段工作）：对象和字段 API 名称，以及用户是否需要*过滤、排序或分组*字段（驱动确定性 vs 概率性）。
- **密钥模型**（用于密钥工作）：密钥是 Salesforce 派生的（默认）、客户提供的（BYOK）、存储在外部 KMS（BYOKMS/EKM）还是按需获取（缓存密钥）。

如果请求很明确，请立即生成或回答——不要询问用户。

---

## 工作流程

1. **分类请求**——可部署工件 vs 指导，使用上述必需输入。然后**将输出范围限定为确切请求的内容**：
   - 一个**指导**问题产生**恰好一个 markdown 答案文件**——一个包含完整诊断/解释的单个文件（例如 `answer.md`）——以及**什么也不**。不要同时发出 `*.settings-meta.xml`、`*.field-meta.xml` 或第二个辅助文档。这涵盖了所有 "当…会发生什么？"、"我该如何…"、"哪个模型…"、"X 对吗…"、"我们可以…"、"关系/排序…" 的问题，包括加密字段的查询行为和缓存密钥/重放问题。**"在我编写我们的设置之前"或"在我编写文件之前"描述了*用户*的下一步操作，并且不会将问题变成可部署元数据请求——编写答案文件，而不是设置文件。**
   - **在指导答案中命名元数据更改不代表发出可部署文件。** 一个补救或诊断问题——*"我如何使字段可查询?"*"我的查询失败的原因是什么以及我如何修复它?"*"哪个密钥模型将材料保留在 Salesforce 之外?"*——在**一个 markdown 答案文件**内回答，内联引用相关元素/方案（例如"切换到 `Deterministic*` 方案并启用 `enableDeterministicEncryption`"，或"使用外部密钥管理——`canExternalKeyManagement`"）。**不要**额外生成 `*.field-meta.xml` 或 `*.settings-meta.xml` 来*演示*该更改——在答案中提及元素是完整的交付成果。只有在用户明确说生成/创建/给我字段或设置文件时，才生成可部署元数据文件。
   - 一个**工件**请求只获得**特定元数据文件**——不要添加 `DEPLOYMENT_GUIDE.md`/`README.md`/`EXPLANATION.md` 或额外的 `settings` 文件用户没有请求。如果部署步骤或组织设置是先决条件，请在**一个答案文件**内（对于指导）或**在工件内的代码注释**中（对于工件请求）说明——永远不会作为额外文件说明。
   - 如果部署步骤或组织设置是先决条件，请在**一个答案文件**内（对于指导）或**在工件内的代码注释**中（对于工件请求）说明——永远不会作为额外文件说明。

2. **对于字段加密**——阅读 `references/encryption-schemes.md` 以选择方案，然后加载 `assets/encrypted-field.field-meta.xml` 作为起始模板。将 `encryptionScheme` 设置为四个有效枚举值中的**一个**（见参考）。只有 `Deterministic*` 方案是可过滤的。

   > **在 SFDX 源路径而不是根目录处编写字段文件。** `*.field-meta.xml` **必须**位于 `objects/<ObjectApiName>/fields/<FieldApiName>__c.field-meta.xml`（例如 `objects/Patient__c/fields/Diagnosis_Notes__c.field-meta.xml`）——对象文件夹使用对象的 API 名称（自定义对象为 `Patient__c`，标准对象为 `Contact`），文件按字段 API 名称命名。即使在 XML 本身正确的情况下，在仓库根目录、扁平目录或任何其他文件夹下发出文件也是结构错误。

3. **对于组织级加密设置**——加载 `assets/PlatformEncryption.settings-meta.xml`（确定性加密、字段历史加密、MEK 权限）或 `assets/EncryptionKey.settings-meta.xml`（缓存密钥、EKM、数据 360、事务数据库、重放检测）。在设置任何密钥模型字段之前，阅读 `references/key-models.md`。

   > **按设置*成员*而不是根元素命名输出文件，并写入 `settings/` 下。** 一个 `Settings` 文件必须为 `settings/<member>.settings-meta.xml`，其中 `<member>` 是组织的元数据成员名称——**`EncryptionKey`**（根 `<EncryptionKeySettings>`）和**`PlatformEncryption`**（根 `<PlatformEncryptionSettings>`）。将其放在 `settings/` 源文件夹中（例如 `settings/EncryptionKey.settings-meta.xml`），而不是仓库根目录。将密钥设置文件命名为 `Encryption.settings-meta.xml` 或 `EncryptionKeySettings.settings-meta.xml` 会因 *"类型为 Settings 的对象 '…' 不存在"* 而失败部署。

   > **缓存密钥和重放检测是一方依赖关系，而不是自动启用。** 您只能在 `enableCacheOnlyKeys` 为 `true` 后设置 `enableReplayDetection`；启用缓存密钥本身不会自动启用重放检测。组织可以有效地以重放检测关闭的方式运行缓存密钥。

4. **对于租户密钥操作**（轮换、销毁、BYOK 上传、缓存密钥调用设置）——阅读 `references/tenant-secret-lifecycle.md`。这些是 UI/REST 仅限的；将指导捕获在单个 markdown 答案文件中，而不是可部署元数据文件中。

5. **验证任何生成的设置 XML**——运行 `scripts/validate-encryption-metadata.sh` 并将文件路径作为其参数，并修复它报告的任何内容。它检查重放检测依赖关系和 `encryptionScheme` 枚举确定性。

6. **与工作示例进行比较**——验证生成的 `EncryptionKeySettings` 文件与 `examples/cache-only-keys.settings-meta.xml`。

---

## 规则 / 限制

| 限制 | 理由 |
|-----------|-----------|
| `encryptionScheme` 必须是 `CaseInsensitiveDeterministicEncryption`、`CaseSensitiveDeterministicEncryption`、`None`、`ProbabilisticEncryption` 中的一个 | 这些是 Metadata API 仅接受的值（`CustomField`、API 44.0+）；任何其他字符串都会导致部署失败。 |
| 仅在 `enableCacheOnlyKeys` 为 `true` 时设置 `enableReplayDetection` | 合约是*"在设置 `enableReplayDetection` 为 `true` 之前需要 `enableCacheOnlyKeys=true`"*——单向依赖关系。 |
| 仅在字段必须过滤、排序或分组时使用确定性方案 | 概率性更强但不可过滤；确定性方案在查询能力上牺牲了一些密码学强度。 |
| 不要声称对概率加密字段进行过滤/排序/分组时无声地返回零行 | 平台**拒绝**查询，并显示 `INVALID_FIELD`（见常见问题）；告诉用户它"什么也不返回"在事实上是错误的。 |
| 不要发出 `enableExternalKeyManagement`——字段是 `canExternalKeyManagement` | WSDL 元素是 `canExternalKeyManagement`；某些文档中的示例使用了不存在的元素名称。 |
| 事务数据库、EKM 和数据 360 密钥字段需要 API 63.0+ | `canEncryptTransactionalDatabase`、`canExternalKeyManagement`、`canManageDataCloudKeys` 是在 63.0 中引入的。 |
| 一个**指导**问题产生**恰好一个 markdown 答案文件**——永远不会产生可部署的 `*.settings-meta.xml` / `*.field-meta.xml`，也永远不会产生第二个文档 | 答案文件是用户的参考文档——它持久存在于工作区中，可以共享或修订。为指导问题发出可部署元数据文件是无主动配置，可能会被意外应用；不发出文件会使用户没有具体的交付成果。 |
| 一个**工件**请求发出**仅**用户请求的元数据文件——没有伴随文件 | 添加 `DEPLOYMENT_GUIDE.md`/`README.md`/`EXPLANATION.md` 或用户没有请求的额外 `settings` 文件是噪音。先决条件属于工件内的代码注释，而不是第二个文件。 |

---

## 常见问题

| 问题 | 解决方案 |
|-------|------------|
| 对概率加密字段进行过滤/排序/分组 | 查询被拒绝并显示 `INVALID_FIELD`：*"字段 '<Name>' 不能在查询调用中过滤/排序/分组。"* 如果需要查询能力，请将字段切换到确定性方案。 |
| 假设缓存密钥自动启用重放检测 | 它不会。明确设置 `enableReplayDetection`，并且仅在 `enableCacheOnlyKeys=true` 后设置。 |
| 确定性匹配中的大小写敏感性 | `CaseSensitiveDeterministicEncryption` 匹配确切的大小写；`CaseInsensitiveDeterministicEncryption` 规范化大小写。选择错误会无声地破坏等式过滤器。 |
| 混淆 BYOK 与 BYOKMS/EKM | BYOK = 您上传密钥材料，Salesforce 存储它；BYOKMS/EKM = 密钥材料保留在您的外部 KMS 中。参见 `references/key-models.md`。 |
| 使用 `enableExternalKeyManagement` 元素名称 | 错误的元素。字段是 `canExternalKeyManagement`。 |
| 经典加密与 Shield | `encryptionScheme` 仅适用于 Shield。`EncryptedText` 自定义字段是遗留的经典功能，超出范围。 |

---

## 输出预期

交付成果取决于请求——**恰好**生成这些，并且不要更多：

- **指导问题产生恰好一个 markdown 答案文件。** 任何 "当…会发生什么？"、"我该如何…"、"哪个模型…"、"X 对吗…" 的问题——包括加密字段的查询行为、缓存密钥/重放检测关系、租户密钥/ BYOK / 缓存密钥生命周期以及密钥模型选择——都通过编写一个包含完整诊断/解释的单个 markdown 文件（例如 `answer.md`）来回答。**不要**额外发出可部署的 `*.settings-meta.xml` / `*.field-meta.xml` 或第二个文档，并且**不要**完全不回答文件——答案文件是用户的持久参考文档。
- **字段加密工件**：**仅**带有设置 `encryptionScheme` 的 `*.field-meta.xml`，写入 `objects/<ObjectApiName>/fields/<FieldApiName>__c.field-meta.xml`。不是设置文件，不是部署指南。选择 `<type>` 以匹配请求：**`Text`** 用于最多 255 个字符的字符串字段；**`LongTextArea`** 仅当字段必须超过 255 个字符（256+）时使用。"长文本…最多 255 个字符"是 `Text` 字段，不是 `LongTextArea`。从交付文件中删除模板的说明性注释块——发送干净的元数据。**保持伴随的聊天文本简洁——一两个句子命名所选方案及其原因（例如 "ProbabilisticEncryption — 最强的静态保护；字段不能过滤/排序/分组，这符合您的无查询要求"）。不要重述整个提示、枚举每个方案或添加设置/部署演练；交付成果是文件，不是文章。**
- **组织设置工件**：**仅**请求需要的设置文件，位于 `settings/<member>.settings-meta.xml`，按其 Metadata API 成员命名——`settings/PlatformEncryption.settings-meta.xml`（根 `<PlatformEncryptionSettings>`）和/或 `settings/EncryptionKey.settings-meta.xml`（根 `<EncryptionKeySettings>`）。**不要**按根元素命名文件，**不要**将其放在仓库根目录。

**不要**添加用户没有请求的伴随文件（`DEPLOYMENT_GUIDE.md`、`README.md`、额外的 org-设置文件）——在工件内的代码注释中或在单个答案文件中说明先决条件。文件结构遵循 `assets/` 中的模板。

---

## 跨技能集成

| 需要 | 委托给 |
|------|-------------|
| 一个没有加密的自定义字段 | `platform-custom-field-generate` |
| 原始 Metadata API 类型/字段引用 | `platform-metadata-api-context-get` |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `assets/encrypted-field.field-meta.xml` | 在生成加密自定义字段之前 |
| `assets/PlatformEncryption.settings-meta.xml` | 在生成组织加密策略设置（成员 `PlatformEncryption`）之前 |
| `assets/EncryptionKey.settings-meta.xml` | 在生成密钥管理设置之前——缓存密钥、EKM、数据 360（成员 `EncryptionKey`） |
| `references/encryption-schemes.md` | 在选择确定性 vs 概率性，或解释加密字段的查询行为时 |
| `references/key-models.md` | 在配置或解释 BYOK / BYOKMS / EKM / 缓存密钥模型时 |
| `references/tenant-secret-lifecycle.md` | 当用户询问密钥轮换、销毁或 BYOK 上传时 |
| `examples/cache-only-keys.settings-meta.xml` | 以验证生成的缓存密钥设置文件 |
| `scripts/validate-encryption-metadata.sh` | 在生成任何设置 XML 之后——验证重放依赖关系和方案枚举 |
