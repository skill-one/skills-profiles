# Cloud Firestore 数据库与运维

在设置依赖、编写数据模型或配置安全规则之前，您必须始终确定 Firestore 实例的版本。

## 1. 实例选择与版本检测

运行以下命令以列出当前的 Firestore 数据库：

```bash
npx -y firebase-tools@latest firestore:databases:list
```

### A. 实例已找到

1. 对于每个找到的数据库，检查其版本和详细信息：

    ```bash
    npx -y firebase-tools@latest firestore:databases:get <database-id>`
    ```
1. 询问用户希望针对哪个数据库实例，或者是否更倾向于创建新的实例。
1. 确定目标实例后：
   - 如果 **`edition`** 为 `STANDARD`，请查阅 `references/standard/` 下的指南。
   - 如果 **`edition`** 为 `ENTERPRISE` 或原生模式，请查阅 `references/enterprise/` 下的指南。

### B. 未找到实例（或请求创建新实例）

如果没有数据库或用户请求创建新的数据库，默认配置 **Enterprise** 版本的数据库，并询问用户使用什么位置。运行 `npx -y firebase-tools@latest firestore:locations` 以获取选项列表。如适用，建议与其他资源共置。

确定位置后，创建数据库：

```bash
npx -y firebase-tools@latest firestore:databases:create <database-id>` --edition="enterprise" --location="`
```

随后使用 `references/enterprise/` 下的指南继续操作。

______________________________________________________________________

## 2. 专业指南

根据已识别或创建的实例版本，打开并阅读相应的参考指南：

### 标准版本（`references/standard/`）

- **配置（Provisioning）**：阅读 [provisioning.md](references/standard/provisioning.md)
- **安全规则**：参见 `firestore-rules-creation` 技能
- **SDK 使用**：阅读 [web_sdk_usage.md](references/standard/web_sdk_usage.md)、
  [android_sdk_usage.md](references/standard/android_sdk_usage.md)、
  [ios_setup.md](references/standard/ios_setup.md) 或
  [flutter_setup.md](references/standard/flutter_setup.md)
- **索引**：阅读 [indexes.md](references/standard/indexes.md)

### 企业版 / 原生模式（`references/enterprise/`）

- **配置（Provisioning）**：阅读
  [provisioning.md](references/enterprise/provisioning.md)

- **数据模型**：阅读 [data_model.md](references/enterprise/data_model.md)

- **安全规则**：参见 `firestore-rules-creation` 技能

- **SDK 使用**：

  > [!CRITICAL] **强制查阅参考资料** 在编写或修改任何
  > Firestore Enterprise Edition 应用程序代码之前，您 **必须** 阅读以下目标平台/语言的相关参考文档中的至少一份，以了解特定的架构要求和流水线初始化模式。

  Read [web_sdk_usage.md](references/enterprise/web_sdk_usage.md)、
  [python_sdk_usage.md](references/enterprise/python_sdk_usage.md)、
  [android_sdk_usage.md](references/enterprise/android_sdk_usage.md)、
  [ios_setup.md](references/enterprise/ios_setup.md) 或
  [flutter_setup.md](references/enterprise/flutter_setup.md)

- **索引**：阅读 [indexes.md](references/enterprise/indexes.md)
