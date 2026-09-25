# 数据管理器 API 设置

## 设置身份验证

参考 [设置 API 访问](https://developers.google.com/data-manager/api/devguides/quickstart/set-up-access.md.txt) 获取更多详细信息。

1.  **启用 API（前提条件）**：检查用户是否已在他们的 Google Cloud 项目中启用了数据管理器 API。
2.  **生成 ADC**：使用应用程序默认凭据 (ADC) 通过 `gcloud auth application-default login` 对本地工作区进行身份验证。
    *   **所需范围**：包含范围 `https://www.googleapis.com/auth/datamanager` 和 `https://www.googleapis.com/auth/cloud-platform`。
    *   **多 API 范围**：如果使用相同的凭据访问其他 API，请附加它们的范围（例如，`https://www.googleapis.com/auth/adwords`）。
    *   **服务账户**：确保服务账户具有 `Service Usage Consumer` IAM 角色，并且执行 `gcloud` 的用户在该服务账户上具有令牌创建角色 (`roles/iam.serviceAccountTokenCreator`) 以进行模拟。

## 安装客户端和工具库

参考 [安装客户端库](https://developers.google.com/data-manager/api/devguides/quickstart/install-library.md.txt) 获取更多详细信息。

配套工具库提供了预构建的辅助类和函数，用于在 API 摄入之前正确格式化、哈希和加密用户标识符（例如电子邮件、电话号码和物理地址）。强烈建议使用这些库，以确保用户标识符的格式符合 API 的规范。

选择以下语言特定的安装指南：

*   [Python 设置参考](references/python.md)（包：`google-ads-datamanager` 和 `google-ads-datamanager-util`）
*   [Java 设置参考](references/java.md)（包：`com.google.api-ads:data-manager` 和 `data-manager-util`）
*   [Node 设置参考](references/node.md)（包：`@google-ads/datamanager` 和 `@google-ads/datamanager-util`）
*   [PHP 设置参考](references/php.md)（包：`googleads/data-manager` 和 `googleads/data-manager-util`）
*   [ .NET 设置参考](references/dotnet.md)（包：`Google.Ads.DataManager.V1` 和 `Google.Ads.DataManager.Util.csproj`）
