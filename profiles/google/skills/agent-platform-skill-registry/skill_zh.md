# 技能注册中心

本技能提供与 Gemini 企业代理平台上的 **技能注册中心** 交互的说明。

## 核心功能

-   **技能发现** - 查询注册中心，轻松搜索、列出、获取特定技能，并检查修订历史记录。
-   **技能生命周期管理** - 上传、更新或永久删除技能。
-   **操作监控** - 实用工具，用于检查长时间运行的状态变化（LRO）的完成状态。
-   **生成技能** - 本地自动化新代理技能的初始脚手架搭建。

## 核心指令

-   **强制验证**：在进行任何操作之前，始终执行环境验证检查。

    在任何操作之前，你必须验证核心环境。

    ```bash
    # 执行验证脚本
    python3 scripts/validate_env.py
    ```

## 前置条件与认证

### 库与认证

确保已安装最新的 Google Cloud 凭证和库。

```bash
# 安装所需库
pip install google-auth requests

# 使用 Google Cloud 进行认证
gcloud auth application-default login
```

### 环境变量

以下变量用于操作：

-   `GCP_PROJECT_ID`：你的 Google Cloud 项目 ID。
-   `GCP_LOCATION`：区域（例如，`us-central1`）。

--------------------------------------------------------------------------------

## 快速入门

快速搜索注册中心中的可用技能：

```bash
python3 scripts/skill_registry_ops.py search \
  --query "test skill" \
  --top-k 5
```

--------------------------------------------------------------------------------

## 操作

-   **技能发现**：[query-skills.md](references/query-skills.md)
-   **技能生命周期**：[manage-skills.md](references/manage-skills.md)
-   **监控操作**：
    [monitor-operations.md](references/monitor-operations.md)
-   **生成技能**：[generate-skill.md](references/generate-skill.md)
