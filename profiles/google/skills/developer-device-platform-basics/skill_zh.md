# 开发者设备平台

开发者设备平台（DDP）是谷歌提供的完全托管的全球基础设施，可访问各种物理和虚拟设备。

> [!WARNING] 开发者设备平台（DDP）目前处于预览阶段。

> [!IMPORTANT] 对于所有 devicerun 和 devicestreaming API 操作（预留、状态检查、停止/取消、更新或列出会话），始终验证并使用链接参考 `.md` 文件中提供的确切说明和 curl 命令。

## 身份验证与设置

**关键提示**：在运行任何请求之前，您必须确保通过以下步骤正确初始化环境：

在运行任何请求之前，验证是否存在 `gcloud` 可执行文件。如果缺失，请参考官方
[Google Cloud CLI 安装指南](https://docs.cloud.google.com/sdk/docs/install-sdk.md.txt)
在当前平台（Linux、macOS、Windows 等）上安装它。

1.  **Google Cloud 身份验证**：使用您的 Google Cloud 凭据进行身份验证，并为开发者设备平台配置活动的应用默认凭证（ADC）：

    ```bash
    gcloud auth login --no-browser
    gcloud auth application-default login --no-browser
    ```

2.  **启用 API**（如果尚未启用）：

    ```bash
    gcloud services enable devicerun.googleapis.com devicestreaming.googleapis.com testing.googleapis.com --quiet
    ```

> [!NOTE] 在预览期间，需要 Cloud Testing API 才能使用 Device Streaming API。

3.  **启用 gcloud beta 组件**：

    ```bash
    gcloud components install beta
    ```

4.  **设置环境变量**：设置所需的项目变量和访问令牌：

    ```bash
    export PROJECT_ID=$(gcloud config get project)
    export ACCESS_TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null)
    ```

5.  **Python 环境**：有关设置 Python 虚拟环境的说明，请参阅 [start_adb_forwarder.md]。

## 列出可用设备

要找到在启动会话时使用的正确 `modelCode` 和 `osVersion`，您可以列出可用设备：

1.  **列出型号**：运行以下命令以列出可用的 Android 设备型号：

    ```bash
    gcloud beta device-run devices list
    ```

    使用 `ID` 列找到 `CATALOG_ID` 参数的值，以描述特定设备（例如，`shiba-36`）。

2.  **描述型号**：运行 API 请求以获取特定型号的更多详细信息（例如，supportedProducts、resolution）。始终依赖 [describe_device.md] 中提供的确切 curl 命令和说明。

## 启动设备会话

当用户要求预留或连接到设备时：

1.  **检查设备可用性**：

    使用“列出可用设备”说明查找设备的 `CATALOG_ID`。使用 [describe_device.md] 中提供的确切 curl 命令和说明检查 `CATALOG_ID` 的设备可用性。设备必须在 "supportedProducts" 中包含 "deviceStreaming" 才能被预留。

    如果未指定特定设备，请使用 `CATALOG_ID=shiba-34`（SDK 34 上的 Pixel 8）。

    如果用户未指定 `OS_VERSION`，请要求用户从设备列表中选择一个版本（优先选择可用性最高的版本 {"available": "AVAILABILITY_HIGH"}）。

    如果 `OS_VERSION` 对 deviceStreaming 不可用，则不要预留。提示用户选择其他 `OS_VERSION`。

2.  **提取参数**：

    *   `model_id`：设备详细信息中的 `modelCode`。必需。
    *   `version_id`：设备详细信息中的 `osVersion`。必需。

3.  **预留设备**：

    **规则**：**需要显式用户确认**。预留设备会产生计费费用并创建云资源。代理必须始终明确警告用户在活动的 Google Cloud 项目（例如，`${PROJECT_ID}`）上将要产生的计费费用。在继续任何会话创建命令之前，您必须停止并要求显式批准。

    然后，使用 `model_id` 和 `version_id` 运行 API 请求以预留设备。始终依赖 [reserve_device.md] 中提供的确切 curl 命令和说明。

    解析响应以获取 `session_name`（会话名称，例如，`projects/${PROJECT_ID}/deviceSessions/session-xxxxxx`）。如果预留失败，请报告错误。

4.  **等待会话变为活动状态**：

    在等待设备会话配置期间，轮询会话状态，直到 `"state"` 为 `"ACTIVE"`。有关确切 curl 命令，请参阅 [session_status.md]。

    每隔 5 秒重复此检查，以防止达到 API 速率限制。如果它在 2 分钟内（通常不到 1 分钟）未变为活动状态，请报告失败并取消会话。一旦变为活动状态，从会话 JSON 响应中提取 `expireTime` 并将其转换为用户本地时间的可读格式（例如，“2026 年 6 月 9 日下午 2:44 PDT”）。

5.  **启动连接转发器**：启动 ADB 转发器脚本以将连接转发到远程设备。始终依赖 [start_adb_forwarder.md] 中提供的确切命令和说明。确保您记录了**命令 ID**。

6.  **等待在线并解析端口**：等待转发器上线并提取监听端口。始终依赖 [start_adb_forwarder.md] 中提供的确切逻辑和说明。

7.  **向用户提供说明**：

    一旦上线，运行 `adb -s localhost:{port} shell getprop ro.product.model` 以检索设备型号名称。然后，直接在聊天中向用户打印消息（不要创建任何工件文件）以下说明：

    ### 设备已准备就绪！

    ```
    设备型号: {device_model}
    操作系统版本: {version_id}
    ADB 地址: localhost:{port}
    会话过期时间: {expire_time_human_readable_local}
    ```

8.  **保存会话状态**：将 `{session_name}` 和 `{command_id}` 保存到您的对话内存/上下文中，以便稍后清理。

## 查看预留设备的屏幕

编码代理可以使用 `adb` 直接与远程设备交互。用户可以使用实用工具在 DDP 中显示屏幕并手动控制预留的设备。有关示例实用工具的说明，请参阅 [view_device.md]。

## 停止设备会话

当用户要求停止、清理或释放设备时：

1.  **识别会话**：从您的上下文中检索活动的 `{session_name}` 和 `{command_id}`。如果您没有它们，请首先列出活动会话（见下方的辅助命令）以找到会话名称。

2.  **通过 API 取消会话**：通过 API 取消会话。始终依赖 [cancel_session.md] 中提供的确切 curl 命令和说明。

3.  **终止连接转发器**：使用您的环境的过程管理功能终止与 `{command_id}` 匹配的背景进程。

4.  **确认**：向用户确认会话已取消并释放了资源。

## 更改设备会话过期时间

当用户要求更改活动设备会话的过期时间时：

**规则**：**需要显式用户确认**。延长设备会话会产生额外计费费用并创建云资源。代理必须始终明确警告用户在活动的 Google Cloud 项目（例如，`${PROJECT_ID}`）上将要产生的额外计费费用。在继续任何会话扩展命令之前，您必须停止并要求显式批准。

1.  **提取参数**：

    *   `session_name`：活动的会话名称。
    *   `ttl`：新的剩余持续时间（例如，`3600s`）。如果以其他格式提供，请推导出 `ttl`。

2.  **通过 API 更改会话**：使用 `updateMask=ttl` 通过 API 更改会话。始终依赖 [update_session_expiration.md] 中提供的确切 curl 命令和说明。

3.  **重新启动连接转发器**：

    *   运行 `adb disconnect localhost:{port}` 以确保旧的转发器连接已关闭。
    *   停止与 `{command_id}` 对应的旧连接转发器。
    *   按照“启动设备会话”中的第 5 步启动新的连接转发器（计算新的 `--ttl` 持续时间（以秒为单位）并存储新返回的命令 ID）。

4.  **确认**：向用户确认会话持续时间已更新，并且连接转发器已使用新的 TTL 重新启动。

## 辅助：列出活动会话

如果您丢失了上下文，请始终依赖 [list_sessions.md] 中提供的 curl 命令和说明来查找活动会话。

## 参考

*   [gcloud device-run CLI]
*   [Device Streaming API]
*   [describe_device.md]
*   [reserve_device.md]
*   [session_status.md]
*   [start_adb_forwarder.md]
*   [view_device.md]
*   [cancel_session.md]
*   [update_session_expiration.md]
*   [list_sessions.md]

[gcloud device-run CLI]: https://docs.cloud.google.com/sdk/gcloud/reference/beta/device-run
[Device Streaming API]: https://docs.cloud.google.com/device-streaming/docs/reference/rest.md.txt
[describe_device.md]: references/describe_device.md
[reserve_device.md]: references/reserve_device.md
[session_status.md]: references/session_status.md
[start_adb_forwarder.md]: references/start_adb_forwarder.md
[view_device.md]: references/view_device.md
[cancel_session.md]: references/cancel_session.md
[update_session_expiration.md]: references/update_session_expiration.md
[list_sessions.md]: references/list_sessions.md
