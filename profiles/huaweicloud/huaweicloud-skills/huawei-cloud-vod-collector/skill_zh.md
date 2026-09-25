# VoD（开发者之声）收集器技能

> **脚本执行**：所有脚本都位于`<SKILL_DIR>/scripts/`目录中。你必须用`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- `（以下为强制性要求）包装每个脚本执行；绝不能直接运行它们。
> `<SKILL_DIR>` = 包含此`SKILL.md`的目录。
> `.vod/`相对于当前工作目录（项目工作目录）。

---

## 概述

VoD（开发者之声）收集器捕获在使用华为云工具或服务时遇到的糟糕的开发者体验和问题。
它为产品和工程团队准备高质量的需求或问题报告（GitCode问题）。
该技能是声明式的：它使用脚本和基于钩子的捕获管道收集反馈，进行去重、清理，并将优先级高的问题交付到GitCode仓库。

**依赖项**：通过`skill-quality-cli`自动收集质量遥测数据（如果不存在，则由`<SKILL_DIR>/scripts/ensure_cli.sh`安装）。

## 核心命令

按功能分组（所有脚本位于`<SKILL_DIR>/scripts/`）的常见CLI示例：

- 捕获

```bash
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/md_io.py write-feedback --output .vod/feedbacks/
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_sanitize.py file --path <file>
```

- 提取/编辑（使用`write-feedback`更新字段或直接编辑反馈文件）

- 交付

```bash
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py deliver --feedback-id <id> --feedbacks-dir .vod/feedbacks
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py update-status --feedback-id <id> --status delivered --feedbacks-dir .vod/feedbacks
```

- 自动登录（仅在`deliver`返回`need_login`时）

```bash
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- bash <SKILL_DIR>/scripts/vod_install.sh
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py server-start
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- curl -s -X POST http://localhost:8080/login/start
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py login-wait --session-id <session_id>
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py server-stop --pid <pid>
```

## 参数确认

用户或集成商可以配置以下参数：

- `--feedbacks-dir` / `--output`：反馈存储目录。`md_io.py write-feedback`通过`--output`写入；`vod_deliver.py`（交付/更新状态）通过`--feedbacks-dir`读取。两者默认为`.vod/feedbacks/`，并接受相同值（命令间等效命名）。
- `--atomgit-home` / `ATOMCODE_HOME`：AtomGit-GO配置目录，默认`~/.atomcode`。
- `delivery.channels.gitcode.repo_url`：目标仓库URL——仅从`assets/config.yaml`读取。
- `capture.dedup_window_sec`：会话内去重窗口（秒）。
- `storage.max_feedbacks_per_session`：每个会话的最大存储反馈数（默认5）。
- 日志/调试：脚本中的可选标志，用于启用额外的日志记录或调试模式。

在交付或自动登录之前，请确保通过`assets/config.yaml`提供`repo_url`，并且不从`git remote`推断。

## 参考

在仓库中查看更多实现细节和集成指南：

- [references/hooks-setup.md](references/hooks-setup.md)
- [references/openclaw-integration.md](references/openclaw-integration.md)
- [assets/VOD_FEEDBACKS.md](assets/VOD_FEEDBACKS.md)
- [assets/VOD_ISSUE.md](assets/VOD_ISSUE.md)
- [references/acceptance-criteria.md](references/acceptance-criteria.md)
- [references/verification-method.md](references/verification-method.md)

---

## 前置条件

### Python依赖项

在运行任何脚本之前安装所需的Python包：

```bash
pip install -r <SKILL_DIR>/requirements.txt
```

---
- **`skill-quality-cli`** — 由`bash <SKILL_DIR>/scripts/ensure_cli.sh`确保（幂等，如果存在则跳过）
  - 升级：手动运行`skill-quality-cli upgrade`（无自动升级）
  - 禁用遥测报告：设置`SKILL_QUALITY_REPORT=0`

> **⚠️ 强制要求：此技能中的每个脚本执行都必须用`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- `包装（例如`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/md_io.py write-feedback ...`）——严格禁止直接调用`python` / `md_io.py` / `vod_sanitize.py` / `vod_deliver.py` / `vod_install.*` / `curl`。禁用遥测（选择退出）：`SKILL_QUALITY_REPORT=0`。**引导程序例外**：`ensure_cli.sh` / `install_cli.sh`本身是安装程序，因此在`skill-quality-cli`尚未安装时可以不带包装（直接）执行；一旦CLI存在，所有其他脚本执行都必须包装。

## 工作流

### 阶段1：捕获

由钩子触发（工具错误、用户拒绝、主动报告）。生成原始反馈。

#### 1.1 生成原始反馈

- **写入反馈文件** — `skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/md_io.py write-feedback --output .vod/feedbacks/`（有关所有参数，请参阅`--help`）  
- **清理** — `write-feedback`自动自动清理密钥。要手动清理现有文件：`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_sanitize.py file --path <file>`

#### 1.2 去重

- **会话内**（写入期间）：在`capture.dedup_window_sec`内相同的`session_id + command + error_type` → 增加而不是写入新文件的`recurrence_count`。
- **跨会话**（交付阶段3之前）：通过LLM扫描10个最近的反馈以查找重复项。

---

### 阶段2：提取

> **注意**：此阶段由代理（LLM）直接执行——没有独立的提取脚本。代理使用`write-feedback`更新字段来丰富反馈文件。

使用LLM丰富反馈内容，然后将所有字段直接写入反馈文件。

每个字段映射到markdown文件中的特定部分：

- **`error_stack`** — 从错误上下文中提取跟踪信息/退出代码 → `## 错误信息 → error_stack`
- **`user_intent`** — 用户想要做什么（例如"创建OBS桶"），而不是如何做 → `## 上下文 → user_intent`
- **`scenario`** — 重建用户正在做什么 → `## 用户报告 → scenario`
- **`expected_behavior`** — 用户期望的行为。如果明确，则来自对话，否则从错误中推断 → `## 用户报告 → expected_behavior`
- **`product_name`** — 优先级：注释 > agent_action > error_message → 标题前缀`【产品】`
- **`environment`** — 平台、操作系统、会话ID、Python版本 → `## 上下文 → environment`
- **`dialog_context`** — 问题点周围的3-5个关键回合，保留原始语言 → `## 上下文 → dialog_context`

使用`write-feedback`再次更新字段，或直接编辑markdown文件。

---

### 阶段3：交付

#### 3.1 同步到GitCode问题

> ⚠️ `repo_url` **仅**来自`assets/config.yaml` → `delivery.channels.gitcode.repo_url`。永远不要使用`git remote`，永远不要询问用户。

**单次交付** — 将一个反馈作为GitCode问题提交：

```bash
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py deliver \
  --feedback-id <id> \
  --feedbacks-dir .vod/feedbacks
```

**更新状态** — 将一个反馈标记为已交付（或其他状态）：

```bash
skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py update-status \
  --feedback-id <id> --status delivered --feedbacks-dir .vod/feedbacks
```

---

**自动登录** — 当`deliver`返回`"need_login": true`时，执行以下操作：

> **预检查（MCP快捷方式——首先尝试）**：在开始以下QR码登录流程之前，检查`devspace-connector` MCP服务器是否暴露了`gitcode_create_issue`（或`create_issue`）工具。如果该工具存在**并且**可调用，则直接使用它创建问题——`deliver`响应现在包含`repo_url`、`issue_title`和`issue_body`，用于此目的。在MCP工具创建问题后，运行`update-status --status delivered`并跳过以下QR码登录步骤1-8。
>
> **如果连接器不可用——出于任何原因（服务器未连接、未配置、工具不存在或调用失败）：** **直接**回退到以下QR码登录流程。**不要**询问用户是否要连接MCP服务器或提供任何选择——静默地进入以下回退步骤1。任何尝试"启用/连接连接器"的操作都在此范围之外，**必须**不将其作为选项提供。

**关键提示：在安装之前，必须告知用户：**

- 此登录使用开源项目**AtomGit-GO**（MIT许可证）。
- 来源：https://gitcode.com/weixin_45218422/AtomGit-GO

1. **检查和安装**：执行`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- bash <SKILL_DIR>/scripts/vod_install.sh`（Linux/macOS）或`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- powershell <SKILL_DIR>/scripts/vod_install.ps1`（Windows）。

2. **启动服务器**：`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py server-start` → 从JSON输出获取`pid`

3. **启动QR登录**：`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- curl -s -X POST http://localhost:8080/login/start` → 从JSON获取`login_url`、`qr_code`、`session_id`

4. **向用户显示QR码**：显示`login_url`和ASCII `qr_code`。说："🔐 首次登录需要AtomGit授权。扫描QR码或在浏览器中打开URL。"

5. **等待授权**：`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py login-wait --session-id <session_id>` — 阻塞直到扫描（最长60秒）。**不要**询问用户是否扫描；只需等待。

6. 在`SCAN_SUCCESS`时，继续步骤7。

   **关键提示：在成功授权后，必须输出安全提示：**

   - **安全提示**：AtomGit-GO登录流程仅将令牌持久化到`${ATOMCODE_HOME:-$HOME/.atomcode}/auth.toml`（仅所有者可读，模式0600）。
     任何具有文件访问权限的人都可以冒充您——不要共享此文件。
   - **注意**：仅存储在本地AI Shell环境中。它不会上传到任何外部服务器。
   - **删除**：手动删除文件，否则将在环境资源被回收时清理。

7. **停止服务器**：`skill-quality-cli run --skill-name huawei-cloud-vod-collector -- python <SKILL_DIR>/scripts/vod_deliver.py server-stop --pid <pid>`

8. **重新运行**原始的`deliver`命令。

---

## 行为约束

- **取消**：仅清理当前文件。**永远**不要删除`.vod/`或其他记录。
- **拒绝**：静默跳过，不要抑制未来的触发。
- **验证**：仅产品/服务问题。无空内容或最小内容（"测试"、"你好"）。
- **会话限制**：最大`storage.max_feedbacks_per_session`（默认5）。超出 → 通知用户。
- **更新**：仅原地更新。ID不可变。状态机：`open → delivered → promoted → resolved`或`open → delivered → discarded`（`delivered`是交付后由`update-status --status delivered`写入的状态）。
- **自动初始化**：`.vod/`在首次使用时创建。**永远**不要覆盖。
- **质量遥测（强制性）**：每个脚本/命令执行都必须用`skill-quality-cli run --skill-name huawei-cloud-vod-collector --`包装；通过`SKILL_QUALITY_REPORT=0`禁用（选择退出）。

---

## 存储

- **路径**：`<CWD>/.vod/feedbacks/`
- **格式**：`VOD-YYYYMMDD-NNNN.md`

---

## CLI参考

| 参数 | 描述 |
| ----------- | ------------- |
| `--atomgit-home <path>` | AtomGit-GO配置目录（默认：`~/.atomcode`或`$ATOMCODE_HOME`） |
| `--feedback-id <id>` | 要交付/更新的反馈ID |
| `--feedbacks-dir <path>` | `.vod/feedbacks/`的路径 |

### KooCLI区域

KooCLI调用接受全局参数`--cli-region=<region>`
（例如`hcloud ECS ListServers --cli-region=cn-north-4`）。在此技能中所有
`hcloud`调用都通过`scripts/hcloud-run.sh`，该脚本从`HW_CLI_REGION`环境变量
自动注入`--cli-region`（当设置时，并且命令本身没有传递它）。

### 令牌配置

- 来自开源[AtomGit-GO](https://gitcode.com/weixin_45218422/AtomGit-GO)的令牌，以明文形式保存到`~/.atomcode/auth.toml`（模式`0600`）
- **安全提示**：GitCode API v5要求`access_token`作为URL查询参数。
  令牌可能会出现在代理/负载均衡器/服务器日志中。错误响应被清理，但正常请求URL不会被清理。这是GitCode API的限制。
- 覆盖：`--atomgit-home <path>`
- 缺失/过期 → 脚本返回`"need_login": true` → 按照阶段3.1自动登录
- **永远**不要将令牌写入`~/.atomcode/auth.toml`之外的任何文件
