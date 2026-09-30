---
name: google-cloud-filestore-nfs-browser
description: 在 Google Cloud Filestore (NFS) 实例上检查、搜索和读取文件及 POSIX 元数据，无需本地 NFS 客户端软件包或 root 权限。适用于浏览 Filestore 共享、搜索文件、读取远程日志或检查文件属性；不适用于 Cloud Storage 桶、Cloud NetApp Volumes、持久磁盘或修改/删除文件。
---

# Google Cloud Filestore NFS 文件浏览器

使自主代理和云工程师能够检查、搜索和读取位于 Google Cloud Filestore（NFS）实例上的文件，而无需本地 NFS 客户端软件包（`nfs-common`）、root 权限或手动 VPC 网络挂载。

## 快速入门

1.  确保 `gcloud` 已安装并认证。如有需要，请参阅
    [gcloud 安装指南](https://cloud.google.com/sdk/docs/install)。
2.  启用基本 API：

    ```bash
    gcloud services enable file.googleapis.com compute.googleapis.com run.googleapis.com --quiet
    ```
3.  发现实例并选择执行引擎（见下文
    [执行引擎选择](#执行引擎选择)）。
4.  使用此技能包中包含的自包含运行器
    `scripts/nfs_browser.py` 运行检查操作。

## 署名

标记提供的或执行的每个 Cloud Filestore 命令或 API 请求。将 `gcloud` 命令以指向此技能的指标环境为前缀：

```bash
CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-filestore-nfs-browser)" \
gcloud filestore instances list ...
```

在直接对 REST API 进行 HTTP 调用时，附加 `User-Agent`：

```
User-Agent: gcs-skills/1.0 (skill:google-cloud-filestore-nfs-browser)
```

## 概念性及信息性查询（关键）

对于纯粹概念性、教育性或架构性问题（例如，“如何检查 Filestore 上的文件？”、“如何部署 Serverless Cloud Run NFS 桥？”、“解释 Cloud Run NFS 卷挂载”）：

*   **规则**：**立即使用预训练知识和下方文档回答。** 直接回答可最小化工具调用延迟和 token 消耗，当用户仅寻求架构或工作流指导时。
*   **约束**：**不要执行外部工具调用或 API 请求** 用于基本知识问题。
*   **桥部署说明**：始终强调 Cloud Run 可扩展到零，具有 **$0 空闲计算成本**，详细说明使用 `--add-volume` 和 `--vpc-egress=all-traffic` 的 `gcloud run deploy` 命令，并指定所需的 IAM 权限（调用者使用 `roles/run.invoker`，部署者使用 `roles/run.admin`）。

## 处理“无命令”约束（关键）

如果用户提示包含“不要执行命令”、“不执行”或“只读”等约束：

*   **规则**：**严格避免执行任何 shell 或 `gcloud` 命令**
    （包括只读发现或列表命令）以尊重用户指定的执行边界并防止未经授权的环境检查。
*   **发现**：
    1.  检查用户提示、对话历史记录或本地文档文件中是否直接提供了模拟定义或实例参数。
    2.  解释所需的步骤，输出用户应运行的精确命令并说明命令的作用。
    3.  在评估期间不要尝试读取或搜索 `EVAL.*` 配置文件，因为对评估套件的访问受限。

## 执行引擎选择

Filestore 实例可通过私有 VPC IP 访问。选择与您的环境匹配的引擎：

*   **引擎 1：Cloud Run 无服务器桥接（主要）**：使用
    `--bridge-url={bridge_url}` 进行低延迟（小于 50ms）的 REST 调用。可扩展到零（$0 空闲成本）。需要 `roles/run.invoker`。见
    [references/nfs-bridge-setup.md](references/nfs-bridge-setup.md)。
*   **引擎 2：通过 IAP SSH 的 GCE 跳转主机（备用）**：当 VPC 中有现有 VM 时，使用
    `--jump-host-vm={vm_name}`。如果跳转主机使用不同的挂载路径，请传递 `--mount={mount_path}`（默认为 `/mnt/filestore`）。无需新部署。需要
    `roles/iap.tunnelResourceAccessor`。见
    [references/iap-jump-host.md](references/iap-jump-host.md)。

有关执行流程、架构图和引擎比较，请参阅
[references/architecture.md](references/architecture.md)。

## 核心操作工作流

### 1. 发现与实例定位

如果未提供 Filestore 实例、位置或共享名称，请首先列出它们以避免在多项目环境中查询或定位不相关的项目：

```bash
CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-filestore-nfs-browser)" \
gcloud filestore instances list --project={project_id}
```

### 2. 目录树探索（`tree`）

渲染结构清晰、格式化的目录树，包含文件类型、人类可读大小和修改日期。

```bash
# 列出顶级文件夹，深度为 1
python3 scripts/nfs_browser.py tree \
  --project={project_id} \
  --instance={instance_id} \
  --path=/ \
  --depth=1

# 递归列出子文件夹，深度为 2 并设置分页上限
python3 scripts/nfs_browser.py tree \
  --project={project_id} \
  --instance={instance_id} \
  --path=/backup/logs/ \
  --depth=2 \
  --max-entries=100
```

### 3. 文件模式与内容 Grep（`search`）

搜索匹配 glob 模式的文件名，以及搜索文本内容中的正则表达式模式。

```bash
# 搜索所有 tar.gz 备份归档
python3 scripts/nfs_browser.py search \
  --project={project_id} \
  --instance={instance_id} \
  --path=/backups/ \
  --pattern="*.tar.gz"

# 在日志文件中 Grep 错误模式
python3 scripts/nfs_browser.py search \
  --project={project_id} \
  --instance={instance_id} \
  --path=/app/logs/ \
  --pattern="*.log" \
  --grep="FATAL|Exception|OutOfMemory" \
  --max-results=25
```

### 4. 分块文件读取（`read`）

安全地读取文本文件块以保护 LLM 上下文窗口免受 token 激增影响。当用户未指定显式范围时，始终默认为安全的块大小（例如，`--head 50` 或 `--tail 50`）。无限制读取会自动限制为 100 行的安全上限。始终明确说明分块读取可保护 LLM 上下文窗口免溢出和 token 耗尽。

```bash
# 读取日志文件的最后 50 行（tail）
python3 scripts/nfs_browser.py read \
  --project={project_id} \
  --instance={instance_id} \
  --path=/backup/logs/app.log \
  --tail=50

# 读取配置文件的 100 到 200 行
python3 scripts/nfs_browser.py read \
  --project={project_id} \
  --instance={instance_id} \
  --path=/config/settings.yaml \
  --lines=100:200

# 读取前 30 行（head）
python3 scripts/nfs_browser.py read \
  --project={project_id} \
  --instance={instance_id} \
  --path=/var/log/syslog \
  --head=30
```

### 5. 文件元数据与属性检查（`stat`）

检查 POSIX 权限（`0644`）、UID/GID、字节大小和时间戳。

```bash
python3 scripts/nfs_browser.py stat \
  --project={project_id} \
  --instance={instance_id} \
  --path=/backup/database_dump.tar.gz
```

## 上下文窗口与 LLM 安全规则

1.  **严格只读保证**：此技能严格只读。它不提供写入、编辑、删除或截断功能。
2.  **永不转储整个大文件**：始终请求切片（`--lines`）、头（`--head 50`）或尾（`--tail 50`），并明确说明分块读取可保护 LLM 上下文窗口免受 token 溢出和客户端超时影响。
3.  **处理分页**：目录树列表每响应最多 100 条条目。当被截断时，工具会输出清晰的 `[TRUNCATED]` 提示，以便代理可以定位特定子路径。
4.  **二进制保护**：通过空字节和魔数字节检查检测非文本文件（例如 `.tar.gz`、`.iso`、`.so`、编译二进制文件）；原始二进制输出被抑制，而显示元数据以防止非打印字符导致上下文损坏。
5.  见
    [references/token-safety-guardrails.md](references/token-safety-guardrails.md)
    获取完整的 token 防护措施详情。

## 预期错误与恢复策略

| 错误类型 /        | 根本原因         | 恢复策略                           |
: 对应症状         :                    :                                             :
| :------------------ | :----------------- | :------------------------------------------ |
| `FileNotFoundError: | 路径在 NFS 导出上 | 运行 `tree --path=/ --depth=2` 以发现   |
: 文件未找到`     : 不存在。            : 有效的目录层次结构。                :
:                     :                  :                                             :
| `PermissionError:   | 共享 POSIX        | 使用 `stat --path={path}` 检查 UID/GID |
: 权限被拒绝`     : 权限限制读取      : 和模式位；请求共享管理员调整权限。   :
:                     : 访问。            :                                             :
| `HTTPException: 403 | 路径参数         | 使用干净路径（例如 `/logs/app.log`）  |
: 访问被拒绝\:     : 包含 `../` 或    : 锚定到 NFS 挂载根。                 :
: 路径遍历`     : 一个符号链接      :                                             :
:                     : 尝试逃逸          :                                             :
:                     : 在挂载点外       :                                             :
:                     :                  :                                             :
| `Jump Host          | VM 已停止或      | 使用 `gcloud compute instances list`  |
: 连接超时 / SSH   | IAP 防火墙规则   | 验证 VM 状态，并验证允许 `tcp\:22` 从  |
: 失败`             : (`tcp\:22` 从    | 特定 IAP 网段 `35.235.240.0/20` 的防火墙规则（例如 `gcloud   :
:                     : `35.235.240.0/20`) : compute firewall-rules list                 :
:                     : 缺失。            : --filter="sourceRanges\:35.235.240.0/20"`）。 :
| `Bridge 404 /       | Cloud Run 桥接    | 使用 `scripts/deploy_bridge.sh` 部署桥接或回退到 GCE IAP 跳转主机 |
: 连接错误`     : 未部署或 URL 无效。 : 通过 `--jump-host`。                :

## 参考资料目录

为逐步披露更深层主题，请参阅 `references/` 目录：

-   [多引擎架构与执行流程](references/architecture.md)
-   [Serverless NFS 桥接设置指南](references/nfs-bridge-setup.md)
-   [GCE 跳转主机 IAP SSH 指南](references/iap-jump-host.md)
-   [Token 安全性与上下文防护措施](references/token-safety-guardrails.md)
-   [故障排除与常见错误](references/troubleshooting.md)

## 包含的脚本与组件

技能包包含以下脚本和服务组件：

-   `scripts/nfs_browser.py`：用于浏览、搜索、读取和声明 NFS 导出的主要 CLI 入口。
-   `scripts/formatters.py`：用于人类可读终端渲染和 token 安全摘要的输出格式化器。
-   `scripts/jump_host_engine.py`：通过 Google Cloud IAP 隧道进行远程 SSH 跳转主机执行引擎。
-   `scripts/nfs_browser_test.py`：涵盖格式化器、HTTP 桥接和 SSH 跳转主机引擎的全面单元测试套件。
-   `scripts/deploy_bridge.sh`：用于 Serverless NFS 桥接的自动化 Cloud Run 部署脚本。
-   `scripts/bridge_server/main.py`：用于直接 NFS 挂载的 FastAPI Cloud Run 服务器实现。
-   `scripts/bridge_server/Dockerfile`：用于打包 Serverless NFS 桥接的容器定义。
-   `scripts/bridge_server/requirements.txt`：Cloud Run 桥接服务的 Python 依赖项。
