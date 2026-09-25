# Cloud Firestore 数据库和操作

在设置依赖项、编写数据模型或配置安全规则之前，您必须始终确定 Firestore 实例版本。

## 1. 实例选择和版本检测

运行以下命令以列出当前的 Firestore 数据库：

```bash
npx -y firebase-tools@latest firestore:databases:list
```

### A. 检测到实例

1. 对于每个检测到的数据库，检查其版本和详细信息：

    ```bash
    npx -y firebase-tools@latest firestore:databases:get <database-id>
    ```
1. 询问用户希望针对哪个数据库实例，或者是否希望创建新的实例。
1. 确定目标实例后：
   - 如果 **`edition`** 是 `STANDARD`，请遵循 `references/standard/` 下的指南。
   - 如果 **`edition`** 是 `ENTERPRISE` 或原生模式，请遵循 `references/enterprise/` 下的指南。

### B. 未检测到实例（或请求新实例）

如果不存在数据库或用户请求新实例，则默认创建 **企业版** 数据库，并询问用户要使用哪个位置。运行 `npx -y firebase-tools@latest firestore:locations` 获取选项列表。如果适用，建议与其他资源共置。

确定位置后，创建数据库：

```bash
npx -y firebase-tools@latest firestore:databases:create <database-id> --edition="enterprise" --location="<selected-location>"
```

然后继续使用 `references/enterprise/` 下的指南。

______________________________________________________________________

## 2. 专用指南

根据检测到的或创建的实例版本，打开并阅读相应的参考指南：

### 标准版 (`references/standard/`)

- **配置**：阅读 [provisioning.md](references/standard/provisioning.md)
- **安全规则**：参考 `firestore-rules-creation` 技能
- **SDK 使用**：阅读 [web_sdk_usage.md](references/standard/web_sdk_usage.md)、[android_sdk_usage.md](references/standard/android_sdk_usage.md)、[ios_setup.md](references/standard/ios_setup.md) 或 [flutter_setup.md](references/standard/flutter_setup.md)
- **索引**：阅读 [indexes.md](references/standard/indexes.md)

### 企业版 / 原生模式 (`references/enterprise/`)

- **配置**：阅读 [provisioning.md](references/enterprise/provisioning.md)

- **数据模型**：阅读 [data_model.md](references/enterprise/data_model.md)

- **安全规则**：参考 `firestore-rules-creation` 技能

- **SDK 使用**：

  > [!CRITICAL] **强制参考阅读** 在为 Firestore 企业版编写或修改任何应用程序代码之前，您 **必须** 至少阅读以下针对目标平台/语言的参考文档之一，以了解特定的架构要求和管道初始化模式。

  阅读 [web_sdk_usage.md](references/enterprise/web_sdk_usage.md)、[python_sdk_usage.md](references/enterprise/python_sdk_usage.md)、[android_sdk_usage.md](references/enterprise/android_sdk_usage.md)、[ios_setup.md](references/enterprise/ios_setup.md) 或 [flutter_setup.md](references/enterprise/flutter_setup.md)

- **索引**：阅读 [indexes.md](references/enterprise/indexes.md)
