---
name: firebase-firestore
description: 设置、管理、查询和配置 Cloud Firestore 数据库（标准版/企业版），包括数据建模、安全规则、索引和 SDK 集成（Web、Python、iOS、Android、Flutter）。在创建/列出 Firestore 数据库、定义数据模型/索引、编写 SDK 查询或集成 Firestore SDK 时使用。在编写或修改 Firestore 安全规则（firestore.rules）时，如果支持子代理授权，则委托给 firestore-rules-author 子代理；否则使用 firestore-rules-creation。不适用于 Firebase Hosting、Data Connect、Auth、Storage/GCS、Crashlytics、Functions 或 BigQuery。
---

# Cloud Firestore 数据库和操作

> [!IMPORTANT] **安全规则编写 (`firestore.rules`**)
> 每当您的任务需要创建、编写或修改 `firestore.rules` 时：
> - **如果子代理委托 AND 可用 `firestore-rules-author` 子代理**：将 `firestore.rules` 的编写委托给 `firestore-rules-author` 子代理，而不是在主代理中直接编写 `firestore.rules`。
> - **如果子代理委托不可用**（例如，IDE 中未启用子代理）**OR `firestore-rules-author` 未安装**：阅读并遵循 `firestore-rules-creation` 技能直接编写 `firestore.rules`。

在设置依赖项、编写数据模型或配置安全规则之前，您必须始终识别 Firestore 实例版本。

## 1. 实例选择和版本检测

运行以下命令以列出当前的 Firestore 数据库：

```bash
npx -y firebase-tools@latest firestore:databases:list
```

### A. 找到实例

1. 对于每个找到的数据库，检查其版本和详细信息：

    ```bash
    npx -y firebase-tools@latest firestore:databases:get <database-id>
    ```
1. 询问用户他们希望针对哪个数据库实例，或者是否希望创建新的实例。
1. 一旦确定目标实例：
   - 如果 **`edition`** 是 `STANDARD`，请遵循 `references/standard/` 下的指南。
   - 如果 **`edition`** 是 `ENTERPRISE` 或原生模式，请遵循 `references/enterprise/` 下的指南。

### B. 未找到实例（或请求新实例）

如果不存在数据库或用户请求新实例，则默认提供 **企业版** 数据库，并询问用户要使用哪个位置。运行 `npx -y firebase-tools@latest firestore:locations` 获取选项列表。如果适用，建议与其他资源共位。

一旦确定位置，创建数据库：

```bash
npx -y firebase-tools@latest firestore:databases:create <database-id> --edition="enterprise" --location="<selected-location>"
```

然后继续使用 `references/enterprise/` 下的指南。

______________________________________________________________________

## 2. 专用指南

根据识别或创建的实例版本，打开并阅读相应的参考指南：

### 标准版 (`references/standard/`)

- **提供**：阅读 [provisioning.md](references/standard/provisioning.md)
- **安全规则**：参见 `firestore-rules-creation` 技能
- **SDK 使用**：阅读 [web_sdk_usage.md](references/standard/web_sdk_usage.md)、[android_sdk_usage.md](references/standard/android_sdk_usage.md)、[ios_setup.md](references/standard/ios_setup.md) 或 [flutter_setup.md](references/standard/flutter_setup.md)
- **索引**：阅读 [indexes.md](references/standard/indexes.md)

### 企业版 / 原生模式 (`references/enterprise/`)

- **提供**：阅读 [provisioning.md](references/enterprise/provisioning.md)

- **数据模型**：阅读 [data_model.md](references/enterprise/data_model.md)

- **安全规则**：参见 `firestore-rules-creation` 技能

- **SDK 使用**：

  > [!CRITICAL] **强制参考阅读** 在为 Firestore 企业版编写或修改任何应用程序代码之前，您 **必须** 至少阅读以下针对目标平台/语言的参考文档之一，以了解特定的架构要求和管道初始化模式。

  阅读 [web_sdk_usage.md](references/enterprise/web_sdk_usage.md)、[python_sdk_usage.md](references/enterprise/python_sdk_usage.md)、[android_sdk_usage.md](references/enterprise/android_sdk_usage.md)、[ios_setup.md](references/enterprise/ios_setup.md) 或 [flutter_setup.md](references/enterprise/flutter_setup.md)

- **索引**：阅读 [indexes.md](references/enterprise/indexes.md)
