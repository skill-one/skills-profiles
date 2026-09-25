> [!IMPORTANT]
> **对于任何华为云查询或管理任务：**
> 1. **搜索** — 使用此技能 (`huawei-cloud-find-skills`) 来查找相关技能。
> 2. **安装** — 安装匹配的技能（参见 [步骤 3](#步骤-3-安装技能)）。
> 3. **执行** — 按照已安装技能的说明来完成任务。

## 概述

此技能使用户能够高效地搜索、发现和安装华为云技能。

**依赖项**：Python 3.6+ 和访问 `gitcode.com` 的网络连接（技能索引的 API v5）以及 `github.com` / `raw.githubusercontent.com`（用于技能详情）。通过 `skill-quality-cli`（由 `scripts/ensure_cli.sh` 安装，如果不存在）自动收集质量遥测数据——不需要其他 CLI 或凭证。

## 场景描述

此技能使用户能够：

- **搜索技能**：通过关键字、类别或两者（匹配名称、描述和触发器）查找技能
- **浏览类别**：探索可用的技能类别
- **查看技能详情**：从 GitHub 获取特定技能的完整 SKILL.md 内容
- **安装技能**：通过 `npx skills add`（GitCode 默认）、`npx clawhub install` 或回退 GitHub 方法指导用户完成技能安装

**架构**：GitCode API v5 (`index.json` + `cn-en-map.json`) → HTTP GET（base64 解码）→ 内存搜索 → GitHub 原始获取详情 → 安装

### 用例

- "查找管理 ECS 实例的技能"
- "华为云 OBS 可用的技能有哪些？"
- "华为云有哪些与 VPC 相关的技能？"
- "浏览所有可用的华为云技能"
- "安装用于 RDS 管理的技能"
- "帮我找一个华为云网络相关的技能"

## 前置条件

- **必须安装并可用** Python 3.6+，并且 `python`（或 `python3`）在 `PATH` 中可用
- **网络访问** 到 `gitcode.com`（索引的 API v5）和 `github.com` / `raw.githubusercontent.com`（用于技能详情）
- **`skill-quality-cli`** — **必须（步骤 0.1）**：由 `bash scripts/ensure_cli.sh` 确保（幂等性，如果已存在则跳过）。**在执行任何搜索/安装命令之前，必须在此技能的每次执行中触发它**。
  - 升级：手动运行 `skill-quality-cli upgrade`（没有自动升级）
  - 禁用遥测报告：设置 `SKILL_QUALITY_REPORT=0`

### 步骤 0：检查 Python 环境

> **必须**：在运行任何脚本命令之前，验证 Python 是否可用。

> **⚠️ 必须执行**：此技能中的每个 `hcloud` 命令都必须用 `skill-quality-cli run --skill-name huawei-cloud-find-skills -- ` 包裹——严格禁止裸 `hcloud` 调用。

```bash
# 检查 Python 可用性
python --version   # 或：python3 --version
```

如果命令失败或返回 Python 2.x：

1. **安装 Python 3**：从 [python.org](https://www.python.org/downloads/) 下载或使用包管理器：
   ```bash
   # macOS
   brew install python3
   # Ubuntu/Debian
   sudo apt-get install python3
   # Windows — 从 python.org 下载安装程序，勾选 "添加 Python 到 PATH"
   ```
2. **安装后验证**：再次运行 `python --version` 以确认 Python 3.6+ 可用
3. **如果 `python` 指向 Python 2**：在所有以下命令中使用 `python3` 而不是 `python`

### 步骤 0.1：确保 `skill-quality-cli`（必须）

> **必须**：在运行任何搜索/安装命令之前，确保 `skill-quality-cli` 已安装并可用。**此步骤必须在执行此技能的每次操作中触发**，紧接在步骤 0 之后。它与 **步骤 0：检查 Python 环境** 具有相同的必须级别——即使您认为 CLI 已存在，也不要跳过它 (`ensure_cli.sh` 是幂等的，当一切就绪时静默退出)。

```bash
# 确保 skill-quality-cli 已准备就绪（幂等性：仅在缺失时安装）
bash scripts/ensure_cli.sh

# 验证可用性
command -v skill-quality-cli && skill-quality-cli version
```

| 结果 | 行为 |
|------|------|
| CLI 已安装且可用 | **静默通过** — 脚本立即退出 |
| CLI 缺失 | 将最新版本安装到 `~/.local/bin/`（打印 `skill-quality-cli vX.Y.Z 已就绪`) |
| 安装失败（无网络等） | 打印警告；**不会阻塞流程** |

> 如果 `skill-quality-cli` 已安装但不在 `PATH` 中：
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> 手动一次性安装回退：`bash scripts/install_cli.sh`。禁用遥测：`export SKILL_QUALITY_REPORT=0`。

### 步骤 0.5：检查 KooCLI 版本（非阻塞）

> **可选**：一个 KooCLI (`hcloud`) 可用性/版本检查，**永远不会阻塞流程**。稍后安装的技能可能依赖于 KooCLI；此步骤提前警告，然后**无论结果如何，始终继续到步骤 1**。

```bash
# 检查 KooCLI 可用性 & 版本（非阻塞）
python scripts/check-koocli.py
```

→ [scripts/check-koocli.py](scripts/check-koocli.py) (Python — 跨平台)

| 结果 | 行为 |
|------|------|
| `hcloud` 已安装且版本正常（≥ 3.0.0） | **静默通过** — 无输出 |
| `hcloud` 已安装但过旧 | 打印升级提醒 (`hcloud update -y`) |
| `hcloud` 未安装 | 打印安装提醒（官方 KooCLI 指南链接） |

> 脚本始终退出 `0` — 它仅提供信息，永远不会中断搜索或安装。

## 仓库信息

```
INDEX_REPO=developer-skill/skills-group-contribution
INDEX_BRANCH=test-for-index
SKILLS_REPO=huaweicloud/huaweicloud-skills
SKILLS_BRANCH=master
RAW_BASE=https://raw.githubusercontent.com/$SKILLS_REPO/$SKILLS_BRANCH
```

## 索引源

搜索脚本通过 HTTP GET 从 GitCode API v5 获取技能索引（自动 base64 解码）：

```
SKILLS_INDEX_URL=https://gitcode.com/api/v5/repos/developer-skill/skills-group-contribution/contents/skills-index/index.json?ref=test-for-index
SKILLS_CN_EN_MAP_URL=https://gitcode.com/api/v5/repos/developer-skill/skills-group-contribution/contents/skills-index/cn-en-map.json?ref=test-for-index
```

## 核心工作流和核心命令

### 步骤 1：搜索技能

> **必须**：代理必须执行搜索脚本以搜索技能索引。**不要直接读取 JSON 文件**——始终使用脚本。

给定 `keyword`（来自 AI 理解的用户意图）和可选的 `category`，运行搜索脚本：

```powershell
# PowerShell
python scripts/search-skills.py -k "<keyword>"
python scripts/search-skills.py -k "<keyword>" -c "<category>"
python scripts/search-skills.py -c "<category>"
```

```bash
# Bash
python scripts/search-skills.py -k "<keyword>"
python scripts/search-skills.py -k "<keyword>" -c "<category>"
python scripts/search-skills.py -c "<category>"
```

> **⚠️ 安全（命令注入防护）**：`keyword`/`category` 来自用户输入，严禁未转义直接拼接到 shell 命令字符串中。如果输入包含 `$()`, `$(...)`, 反引号 **` `**`, `;`, `|` 等 shell 元字符，在 Bash/PowerShell 双引号字符串中会触发命令注入。必须按以下方式调用，避免将外部输入拼入 shell 字符串：
> 1. **首选（推荐）**：使用 Python `subprocess` 参数数组方式调用，不经 shell：`subprocess.run([sys.executable, "scripts/search-skills.py", "-k", keyword, "-c", category])`；
> 2. 必须在 shell 中执行时，用**单引号**包裹用户输入（`'<keyword>'`），并先做转义（将输入中的 `'` 替换为 `'\''`）或使用 shell 转义工具（`shlex.quote`）；
> 3. 遇到包含 `$()`, 反引号, `;`, `|` 等元字符的输入时，优先改为参数数组方式，或在展示给用户前对输入做脱敏处理。

→ [scripts/search-skills.py](scripts/search-skills.py) (Python — 跨平台)

**脚本执行的操作**：
1. 通过 HTTP GET 从 GitCode API v5 获取 `index.json` 和 `cn-en-map.json`（自动 base64 解码内容）
2. 通过 `cn-en-map.json` 扩展关键字（双向 CN↔EN，例如 "ECS" → "ECS, 弹性云服务器, 云服务器")
3. 为每个技能评分：名称匹配 **+10**，触发器匹配 **+8**，描述匹配 **+5**，服务匹配 **+3**
4. 按分数降序排序，输出带匹配关键字的格式化结果
5. 将每个结果的技能名称报告给安装计数 API (`skills/<category>/<service>/<name>`) 作为曝光印象——即发即弃，不会阻塞或失败搜索

**回退迭代**（如果没有结果）：1) 切换 CN↔EN 关键字 2) 扩展关键字 3) 移除类别过滤器 4) 尝试同义词 5) 列出所有技能

该过程应持续进行，直到找到技能或确认其不存在。如果完全失败，通知用户尝试的具体步骤。

### 步骤 2：查看技能详情（可选）

从 GitHub 获取特定技能的完整 SKILL.md 内容以进行意图验证。如果步骤 1 的搜索结果足够信息，则跳过此步骤。

```bash
# URL 模式 — 使用索引中的类别、服务和名称
DETAIL_URL="https://raw.githubusercontent.com/huaweicloud/huaweicloud-skills/master/skills/${category}/${service}/${name}/SKILL.md"
```

代理可以使用 `curl` 或其网络获取工具获取此 URL，然后将技能的完整文档展示给用户。

### 步骤 3：安装技能

> **必须**：在安装之前，代理必须调用安装计数 API 以记录安装。然后使用以下安装命令之一。选项 A 是默认的；选项 C 是当选项 A 不可用时回退的方法。

#### 步骤 3.1：记录安装计数

在执行安装命令之前，调用安装计数 API。`skill_id` 是从步骤 1 的搜索结果构建的：`skills/<category>/<service>/<skill-name>`。

> **重要**：`category` 和 `service` 值必须直接从步骤 1 的搜索输出中获取（格式：`name (category/service)`）。**不要猜测或硬编码它们**。

```bash
curl -s -X POST "https://devdata2.huaweicloud.com/rest/developer/fwdo/rest/developer/servlet/hdskillservice/v1/obs/findcounts/increment" -H "Accept: application/json, text/plain, */*" -H "Content-Type: application/json" -H "Origin: https://skills.huaweicloud.com" -H "Referer: https://skills.huaweicloud.com/" -d "{\"skill_id\":\"skills/<category>/<service>/<skill-name>\"}"
```

> 这是一个即发即弃请求。**不要**因成功或失败而阻塞安装流程。

#### 步骤 3.2：执行安装命令

```bash
# 选项 A：从 GitCode 使用 npx skills add（默认）
npx skills add https://gitcode.com/huaweicloud/huaweicloud-skills.git#master --skill <skill-name> -y

# 选项 B：使用 npx clawhub install（OpenClaw 生态系统）
npx clawhub install <skill-name> -y

# 选项 C（回退）：从 GitHub 使用 npx skills add
npx skills add huaweicloud/huaweicloud-skills --skill <skill-name> -y
```

如果所有安装尝试都失败，将错误消息报告给用户。**不要**尝试上述命令之外的任何方法。

## 参数确认

| 参数 | 必须或可选 | 描述 | 默认值 |
|------|------------|------|--------|
| `Keyword` | 可选 | 搜索关键字（匹配名称、描述、触发器、服务） | 无 |
| `Category` | 可选 | 过滤的类别代码（例如，"computing"、"storage"、"network"） | 无 |
| `skill-name` | 步骤 3 必须的 | 安装的精确技能名称 | 无 |

## 参考

| 文档 | 描述 |
|------|------|
| GitCode API v5 `index.json` | 通过 HTTP GET 获取的技能索引（base64 解码） |
| GitCode API v5 `cn-en-map.json` | 通过 HTTP GET 获取的中文-英文关键字映射（base64 解码） |
| [scripts/search-skills.py](scripts/search-skills.py) | 搜索脚本（Python）—— 从 GitCode API v5 获取，扩展关键字，评分，排序，报告搜索结果曝光 |
| [scripts/check-koocli.py](scripts/check-koocli.py) | 步骤 0.5 非阻塞 KooCLI (`hcloud`) 可用性/版本检查 |
| [scripts/ensure_cli.sh](scripts/ensure_cli.sh) | **必须（步骤 0.1）** 的幂等性 `skill-quality-cli` 安装器（仅在缺失时安装，没有自动升级） |
| [scripts/install_cli.sh](scripts/install_cli.sh) | `skill-quality-cli` 的手动一次性安装器（仅用户触发） |
| [references/iam-policies.md](references/iam-policies.md) | IAM 权限说明 — 此技能仅访问公开接口，无需任何 IAM 凭证/策略 |
| [references/verification-method.md](references/verification-method.md) | 验证方法 — 各场景的验证步骤与预期结果 |
| [references/acceptance-criteria.md](references/acceptance-criteria.md) | 验收标准 — 功能/数据/安全/文件规范验收项 |
| [references/cli-installation-guide.md](references/cli-installation-guide.md) | CLI 安装/升级/遥测关闭说明 |

## 搜索启发式

> 关键字到类别提示的可选参考。代理可以从 `index.json` 推断类别，而无需这些。

- 云基础设施关键字（ecs, bms, vpc, obs, rds, ...）→ 可能是 `computing`、`network`、`storage` 等
- 工具关键字（cli, terraform, koo）→ 可能是 `devtools`
- 管理关键字（monitoring, alarm, log）→ 可能是 `monitoring`

## 故障排除

### 问题：`python` 不可识别为命令

**原因**：Python 3 未安装或不在 `PATH` 中
**解决方案**：安装 Python 3.6+ 并确保其添加到 `PATH`。在 Windows 上，重新运行安装程序并勾选 "添加 Python 到 PATH"。或者，如果可用，使用 `python3`

### 问题：`skill-quality-cli: command not found`（退出码 127）

**原因**：`skill-quality-cli` 安装在 `~/.local/bin/`，通常不在默认 `PATH` 中
**解决方案**：在当前 shell 中运行 `export PATH="$HOME/.local/bin:$PATH"`。如果 CLI 完全缺失，运行一次 `bash scripts/ensure_cli.sh`——它会幂等性安装 CLI（如果已存在则跳过），并且永远不会阻塞业务流程。

### 问题：脚本因 `SyntaxError: invalid syntax` 失败

**原因**：系统 `python` 指向 Python 2.x（脚本需要 Python 3.6+）
**解决方案**：显式使用 `python3` 运行：`python3 scripts/search-skills.py -k "<keyword>"`

### 问题：脚本因 "Failed to fetch index.json" 失败

**原因**：GitCode API v5 URL 不可达
**解决方案**：验证对 `gitcode.com` 的网络连接

### 问题：GitCode API v5 返回 404

**原因**：文件路径错误或分支不是 `test-for-index`
**解决方案**：验证搜索结果中的技能 `category`、`service` 和 `name`

### 问题：搜索无结果

**原因**：关键字与任何技能不匹配
**解决方案**：
1. 尝试更广泛的关键字
2. 切换中文和英文关键字（例如，"对象存储" → "obs"）
3. 列出所有技能：`python scripts/search-skills.py -c "computing"`

## 注意事项

- 此技能是 **只读** 的，不会创建任何云资源
- **不需要缓存管理**——索引每次运行都从 GitCode API v5 获取新鲜数据
- **需要网络**——索引数据托管在 GitCode，通过 HTTP GET（base64 解码）获取
- **必须使用脚本搜索**——不要直接读取 index.json
- 索引仓库：`https://gitcode.com/developer-skill/skills-group-contribution`（分支：`test-for-index`）
- 技能仓库：`https://github.com/huaweicloud/huaweicloud-skills`（分支：`master`）
- **KooCLI**：搜索/安装流程本身是纯 Python + HTTP（没有服务级别的 hcloud 命令，没有 `--cli-region`）。步骤 0.5 仅执行一个非阻塞 KooCLI 可用性/版本检查（通过 `scripts/check-koocli.py` 执行的 `hcloud version`）来警告在安装依赖它的技能之前 KooCLI 是否缺失或过时。
