> [!IMPORTANT]
> **当用户想要搜索、发现或安装华为云（Huawei Cloud）代理技能时：**
> 1. **搜索** — 使用此技能 (`huawei-cloud-find-skills`) 来查找相关技能。
> 2. **安装** — 安装匹配的技能（参见[步骤 3](#步骤-3-安装技能)）。
> 3. **执行** — 按照已安装技能的说明来完成任务。
>
> 此技能仅处理**技能发现和安装** — 它本身不执行华为云资源管理/查询任务；这些任务由它安装的技能处理。

## 概述

此技能使用户能够高效地搜索、发现和安装华为云技能。

**依赖项**：Python 3.6+ 和访问 `gitcode.com`（技能索引的 API v5）以及 `github.com` / `raw.githubusercontent.com`（技能详细信息）的网络访问。通过 `scripts/ensure_cli.sh` 安装的 `skill-quality-cli`（如果不存在）自动收集质量遥测数据 — 无需其他 CLI 或凭证。

## 隐私与遥测

> **透明披露**: 本技能在搜索与安装过程中会产生以下对外遥测上报。均为**匿名聚合数据**(技能名/类目/服务等元信息), **不包含**用户输入内容、凭证、云资源数据或个人身份信息。**质量上报默认开启**(opt-out): 如需关闭, 设置环境变量 `export SKILL_QUALITY_REPORT=0` 即可整体关闭。

| 上报内容 | 触发点 | 目的地 | 是否含敏感数据 |
|----------|--------|--------|----------------|
| 搜索 top-3 曝光计数 | `scripts/search-skills.py`（每次搜索） | `devdata2.huaweicloud.com` install-count API | 否（仅技能名/类目/服务） |
| 安装计数 | Step 3.1 `curl`（每次安装前） | `devdata2.huaweicloud.com` install-count API | 否（仅 `skill_id`，即 `skills/<category>/<service>/<name>`） |
| 质量上报 | `skill-quality-cli run` 包装执行 | quality 上报 APIG（测试环境） | 否（执行状态/耗时/技能名） |

- **默认开启 / 关闭方式**: 以上三类上报**默认开启**(未设置该环境变量即会上报)；如需关闭, 执行 `export SKILL_QUALITY_REPORT=0`（`skill-quality-cli` 与 `search-skills.py` 均遵循该开关）。
- 上报均为 **fire-and-forget**，永不阻塞搜索/安装主流程。

## 场景描述

此技能使用户能够：

- **搜索技能**：通过关键词、类目或两者（匹配名称、描述和触发器）
- **浏览类目**：探索可用的技能类目
- **查看技能详情**：从 GitHub 获取特定技能的完整 SKILL.md 内容
- **安装技能**：通过 `npx skills add`（GitCode 默认）、`npx skills add https://clawhub.ai/huaweicloudskill/skills/<skill-name>`（ClawHub）或回退 GitHub 方法指导用户完成技能安装

**架构**：GitCode API v5 (`index.json` + `cn-en-map.json`) → HTTP GET (base64 解码) → 内存搜索 → GitHub raw 获取详情 → 安装

### 用例

- "找一个用于管理 ECS 实例的技能"
- "OBS 可用的华为云技能有哪些？"
- "华为云有哪些 VPC 相关的技能?"
- "浏览所有可用的华为云技能"
- "安装一个用于 RDS 管理的技能"
- "帮我找一个华为云网络相关的skill"

## 前置条件

- **必须安装 Python 3.6+** 并在 `PATH` 中可用为 `python`（或 `python3`）
- **必须访问网络** 到 `gitcode.com`（索引的 API v5）和 `github.com` / `raw.githubusercontent.com`（技能详细信息）
- **`skill-quality-cli`** — **必须 (步骤 0.1)**: 由 `bash scripts/ensure_cli.sh` 确保
  (幂等性: 如果已存在则跳过)。**必须**在每次执行此技能前运行任何搜索/安装命令前触发。

  - 升级: 手动运行 `skill-quality-cli upgrade`（无自动升级）
  - **质量上报**: 每次搜索(步骤 1)与安装(步骤 3)命令都必须用 `skill-quality-cli run --skill-name huawei-cloud-find-skills -- ` 包装执行, 保证每次执行都触发质量上报

### 步骤 0: 检查 Python 环境

> **必须**: 在运行任何脚本命令前，验证 Python 是否可用。

> **⚠️ 必须的**: 此技能中的每个 `hcloud` 命令都必须用 `skill-quality-cli run --skill-name huawei-cloud-find-skills -- ` 包装 — 禁止裸调 `hcloud` 命令。

```bash
# 检查 Python 可用性
python --version   # 或: python3 --version
```

如果命令失败或返回 Python 2.x:

1. **安装 Python 3**: 从 [python.org](https://www.python.org/downloads/) 下载或使用包管理器:
   ```bash
   # macOS
   brew install python3
   # Ubuntu/Debian
   sudo apt-get install python3
   # Windows — 下载安装程序从 python.org, 勾选 "Add Python to PATH"
   ```
2. **安装后验证**: 再次运行 `python --version` 确认 Python 3.6+ 可用
3. **如果 `python` 指向 Python 2**: 在所有以下命令中使用 `python3` 而不是 `python`

### 步骤 0.1: 确保 `skill-quality-cli` (必须)

> **必须**: 在运行任何搜索/安装命令前，确保 `skill-quality-cli` 已安装且可用。**此步骤必须**在每次执行此技能时触发，立即在步骤 0 之后。它与 **步骤 0: 检查 Python 环境** 具有相同的必须级别 — 即使您认为 CLI 已存在 (`ensure_cli.sh` 幂等性: 当一切就绪时静默退出)。
>
> **披露**: 该 CLI 仅用于本技能的**匿名质量遥测上报**(执行状态/耗时, 见
> [隐私与遥测](#隐私--遥测)); 安装位置 `~/.local/bin`, 不修改系统服务或全局配置; 关闭方式见 [隐私与遥测](#隐私--遥测)。

```bash
# 确保 ~/.local/bin 在 PATH 中 (skill-quality-cli 安装位置)
export PATH="$HOME/.local/bin:$PATH"

# 确保 skill-quality-cli 已就绪 (幂等性: 仅当缺失时安装; 也自动将 CLI 链接到可写的 PATH 目录, 以使裸命令可用)
bash scripts/ensure_cli.sh

# 验证可用性
command -v skill-quality-cli && skill-quality-cli version
```

| 结果 | 行为 |
|---------|----------|
| CLI 已安装且可用 | **静默通过** — 脚本立即退出 |
| CLI 缺失 | 在 `~/.local/bin/` 中安装最新版本 (打印 `skill-quality-cli vX.Y.Z 已就绪`) |
| 安装失败 (无网络等) | 打印警告; **永不阻塞流程** |

> `ensure_cli.sh` 会自动把 `skill-quality-cli` 软链到 `PATH` 中第一个可写目录
> (如 `/usr/local/bin`)，因此 `skill-quality-cli` 通常可直接调用。若仍不可用
> (没有任何可写的 PATH 目录)，请在当前 shell 执行：
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> 手动一次性安装回退: `bash scripts/install_cli.sh`.

### 步骤 0.5: 检查 KooCLI 版本 (非阻塞)

> **可选**: 一个 KooCLI (`hcloud`) 可用性/版本检查，**永不阻塞流程**。
> 后续安装的技能可能依赖 KooCLI; 此步骤提前警告，然后**无论结果如何始终继续到步骤 1**。

```bash
# 检查 KooCLI 可用性 & 版本 (非阻塞)
python scripts/check-koocli.py
```

→ [scripts/check-koocli.py](scripts/check-koocli.py) (Python — 跨平台)

| 结果 | 行为 |
|---------|----------|
| `hcloud` 安装且版本 OK (≥ 3.0.0) | **静默通过** — 无输出 |
| `hcloud` 安装但过旧 | 打印升级提醒 (`hcloud update -y`) |
| `hcloud` 未安装 | 打印安装提醒 (官方 KooCLI 指南链接) |

> 脚本始终退出 `0` — 它仅用于信息，永不中断搜索或安装。

## 仓库信息

```
INDEX_REPO=developer-skill/skills-group-contribution
INDEX_BRANCH=test-for-index
SKILLS_REPO=huaweicloud/huaweicloud-skills
SKILLS_BRANCH=master
RAW_BASE=https://raw.githubusercontent.com/$SKILLS_REPO/$SKILLS_BRANCH
```

## 索引源

搜索脚本通过 HTTP GET 从 GitCode API v5 获取技能索引（自动 base64 解码）:

```
SKILLS_INDEX_URL=https://gitcode.com/api/v5/repos/developer-skill/skills-group-contribution/contents/skills-index/index.json?ref=test-for-index
SKILLS_CN_EN_MAP_URL=https://gitcode.com/api/v5/repos/developer-skill/skills-group-contribution/contents/skills-index/cn-en-map.json?ref=test-for-index
```

## 核心工作流和核心命令

### 步骤 1: 搜索技能

> **必须**: 代理必须执行搜索脚本以搜索技能索引。**绝对不要**直接读取 JSON 文件 — 始终使用脚本。

给定 `keyword`（来自 AI 理解的用户意图）和可选的 `category`，运行搜索脚本:

> **必须 (质量上报)**: 搜索命令必须用 `skill-quality-cli run --skill-name huawei-cloud-find-skills -- ` 包装, 保证每次搜索都触发质量上报。严禁裸调 `python scripts/search-skills.py`。

```powershell
# PowerShell
skill-quality-cli run --skill-name huawei-cloud-find-skills -- python scripts/search-skills.py -k "<keyword>"
skill-quality-cli run --skill-name huawei-cloud-find-skills -- python scripts/search-skills.py -k "<keyword>" -c "<category>"
skill-quality-cli run --skill-name huawei-cloud-find-skills -- python scripts/search-skills.py -c "<category>"
```

```bash
# Bash
skill-quality-cli run --skill-name huawei-cloud-find-skills -- python scripts/search-skills.py -k "<keyword>"
skill-quality-cli run --skill-name huawei-cloud-find-skills -- python scripts/search-skills.py -k "<keyword>" -c "<category>"
skill-quality-cli run --skill-name huawei-cloud-find-skills -- python scripts/search-skills.py -c "<category>"
```

> **安全（命令注入防护）**: `keyword`/`category` 来自用户输入，严禁未转义直接拼接到 shell 命令字符串中。若输入包含 `$()`, `$(...)`, 反引号 **` `**`, `;`, `|` 等 shell 元字符，在 Bash/PowerShell 双引号字符串中会触发命令注入。必须按以下方式调用，避免将外部输入拼入 shell 字符串：
> 1. **首选（推荐）**: 用 Python `subprocess` 参数数组方式调用，不经 shell：`subprocess.run([sys.executable, "scripts/search-skills.py", "-k", keyword, "-c", category])`；
> 2. 必须在 shell 中执行时，用**单引号**包裹用户输入（`'<keyword>'`），并先做转义（将输入中的 `'` 替换为 `'\''`）或使用 shell 转义工具（`shlex.quote`）；
> 3. 遇到包含 `$()`, 反引号, `;`, `|` 等元字符的输入时，优先改为参数数组方式，或在展示给用户前对输入做脱敏处理。

→ [scripts/search-skills.py](scripts/search-skills.py) (Python — 跨平台)

**脚本执行的内容**:
1. 通过 HTTP GET 从 GitCode API v5 获取 `index.json` 和 `cn-en-map.json`（自动 base64 解码）
2. 通过 `cn-en-map.json` 扩展关键词（中英双向, 例如 "ECS" → "ECS, 弹性云服务器, 云服务器")
3. 为每个技能评分: 名称匹配 **+10**, 触发器匹配 **+8**, 描述匹配 **+5**, 服务匹配 **+3**
4. 按分数降序排序，输出格式化结果并高亮匹配的关键词
5. 仅向 install-count API 报告 top-3 结果的技能名作为曝光印象 — fire-and-forget, 永不阻塞或失败搜索

**回退迭代** (若无结果): 1) 切换中英关键词 2) 扩展关键词 3) 移除类目过滤器 4) 尝试同义词 5) 列出所有技能

过程应持续进行，直到找到技能或确认其不存在。在完全失败的情况下，通知用户尝试的具体步骤。

### 步骤 2: 查看技能详情 (可选)

从 GitHub 获取完整 SKILL.md 内容以进行意图验证。如果步骤 1 的搜索结果足够信息，则跳过此步骤。

```bash
# URL 模板 — 使用索引中的类目、服务和名称
DETAIL_URL="https://raw.githubusercontent.com/huaweicloud/huaweicloud-skills/master/skills/${category}/${service}/${name}/SKILL.md"
```

代理可以使用 `curl` 或其网络获取工具获取此 URL，然后将技能的完整文档展示给用户。

### 步骤 3: 安装技能

> **必须**: 在安装前，代理必须调用 install-count API 来记录安装。然后使用以下安装命令之一。选项 A 是默认的；选项 C 是当选项 A 不可用时回退的方法。

#### 步骤 3.1: 记录安装计数

在执行安装命令前，调用 install-count API。`skill_id` 是从步骤 1 的搜索结果构建的: `skills/<category>/<service>/<skill-name>`。

> **重要**: `category` 和 `service` 值必须直接从步骤 1 的搜索输出获取（格式: `name (category/service)`）。**绝对不要**猜测或硬编码它们。

> **必须 (质量上报)**: 安装计数请求同样用 `run` 包装, 保证安装流程触发质量上报。

```bash
skill-quality-cli run --skill-name huawei-cloud-find-skills -- curl -s -X POST "https://devdata2.huaweicloud.com/rest/developer/fwdo/rest/developer/servlet/hdskillservice/v1/obs/findcounts/increment" -H "Accept: application/json, text/plain, */*" -H "Content-Type: application/json" -H "Origin: https://skills.huaweicloud.com" -H "Referer: https://skills.huaweicloud.com/" -d "{\"skill_id\":\"skills/<category>/<service>/<skill-name>\"}"
```

> 这是一个 fire-and-forget 请求。**绝对不要**因请求成功或失败而阻塞安装流程。

#### 步骤 3.2: 执行安装命令

> **必须 (质量上报)**: 安装命令必须用 `skill-quality-cli run --skill-name huawei-cloud-find-skills -- sh -c '...'` 包装, 保证每次安装都触发质量上报。`sh -c` 内的 `printf "\n"` 用于自动确认 `npx skills add` 的 scope 交互提示。

```bash
# 选项 A: 从 GitCode 使用 npx skills add (默认)
skill-quality-cli run --skill-name huawei-cloud-find-skills -- sh -c 'printf "\n" | npx skills add https://gitcode.com/huaweicloud/huaweicloud-skills.git#master --skill <skill-name> -y'

# 选项 B: 从 ClawHub 使用 npx skills add
skill-quality-cli run --skill-name huawei-cloud-find-skills -- sh -c 'printf "\n" | npx skills add https://clawhub.ai/huaweicloudskill/skills/<skill-name> -y'

# 选项 C (回退): 从 GitHub 使用 npx skills add
skill-quality-cli run --skill-name huawei-cloud-find-skills -- sh -c 'printf "\n" | npx skills add huaweicloud/huaweicloud-skills --skill <skill-name> -y'
```

> **安全**: `<skill-name>` 必须来自步骤 1 搜索结果的规范技能名（`name` 字段），禁止拼接未经校验的用户输入到 `sh -c '...'` 内；若技能名含 `'` 等 shell 元字符，须先转义（`'` → `'\''`）或改用 `npx skills add ... -y` 裸调用（此时质量上报改为安装完成后手动 `skill-quality-cli report --skill-name huawei-cloud-find-skills`）。

如果所有安装尝试都失败，将错误信息报告给用户。**绝对不要**尝试上述命令之外的任何方法。

## 参数确认

| 参数 | 必须可选 | 描述 | 默认 |
|-----------|-------------------|-------------|---------|
| `Keyword` | 可选 | 搜索关键词 (匹配名称、描述、触发器、服务) | 无 |
| `Category` | 可选 | 过滤用的类目代码 (例如, "computing", "storage", "network") | 无 |
| `skill-name` | 步骤 3 必须的 | 安装的精确技能名 | 无 |

## 参考

| 文档 | 描述 |
|----------|-------------|
| GitCode API v5 `index.json` | 通过 HTTP GET 获取的技能索引 (base64 解码) |
| GitCode API v5 `cn-en-map.json` | 通过 HTTP GET 获取的中英关键词映射 (base64 解码) |
| [scripts/search-skills.py](scripts/search-skills.py) | 搜索脚本 (Python) — 从 GitCode API v5 获取, 扩展关键词, 评分, 排序, 报告 top-3 搜索结果曝光 |
| [scripts/check-koocli.py](scripts/check-koocli.py) | 步骤 0.5 非阻塞 KooCLI (`hcloud`) 可用性/版本检查 |
| [scripts/ensure_cli.sh](scripts/ensure_cli.sh) | **必须 (步骤 0.1)** 幂等性安装器 for `skill-quality-cli` (仅当缺失时安装, 无自动升级) |
| [scripts/install_cli.sh](scripts/install_cli.sh) | 手动一次性安装器 for `skill-quality-cli` (仅用户触发) |
| [references/iam-policies.md](references/iam-policies.md) | IAM 权限说明 — 本技能仅访问公开接口, 无需任何 IAM 凭证/策略 |
| [references/verification-method.md](references/verification-method.md) | 验证方法 — 各场景的验证步骤与预期结果 |
| [references/acceptance-criteria.md](references/acceptance-criteria.md) | 验收标准 — 功能/数据/安全/文件规范验收项 |
| [references/cli-installation-guide.md](references/cli-installation-guide.md) | CLI 安装/升级/遥测关闭说明 |

## 搜索启发式

> 可选参考: 关键词到类目的提示。代理可以从 `index.json` 推断类目，无需这些。

- 云基础设施关键词 (ecs, bms, vpc, obs, rds, ...) → 可能 `computing`, `network`, `storage`, 等
- 工具关键词 (cli, terraform, koo) → 可能 `devtools`
- 管理关键词 (monitoring, alarm, log) → 可能 `monitoring`

## 故障排除

### 问题: `python` 不可识别为命令

**原因**: Python 3 未安装或不在 `PATH`
**解决**: 安装 Python 3.6+ 并确保其添加到 `PATH`。在 Windows 中，重新运行安装程序并勾选 "Add Python to PATH"。或者，如果可用，使用 `python3`。

### 问题: `skill-quality-cli: command not found` (退出码 127)

**原因**: `skill-quality-cli` 安装在 `~/.local/bin/`，这通常
**不在默认 `PATH`**。
**解决**: 重新运行 `bash scripts/ensure_cli.sh` — 它现在自动将 CLI 链接到 `PATH` 上第一个可写的目录（例如 `/usr/local/bin`），因此裸命令可用。
作为手动回退，在当前 shell 中运行 `export PATH="$HOME/.local/bin:$PATH"`。
如果完全缺失 CLI, `ensure_cli.sh` 幂等性安装它（如果已存在则跳过）并且永不阻塞业务流程。

### 问题: 脚本因 `SyntaxError: invalid syntax` 失败

**原因**: 系统 `python` 指向 Python 2.x（脚本需要 Python 3.6+）
**解决**: 明确使用 `python3` 运行: `python3 scripts/search-skills.py -k "<keyword>"`

### 问题: 脚本因 "Failed to fetch index.json" 失败

**原因**: GitCode API v5 URL 不可达
**解决**: 验证对 `gitcode.com` 的网络连接

### 问题: GitCode API v5 返回 404

**原因**: 文件路径错误或分支不是 `test-for-index`
**解决**: 验证搜索结果中的技能的 `category`, `service`, 和 `name`

### 问题: 搜索无结果

**原因**: 关键词不匹配任何技能
**解决**:
1. 尝试更广泛的关键词
2. 切换中英关键词 (例如, "对象存储" → "obs")
3. 列出所有技能: `python scripts/search-skills.py -c "computing"`

## 注意事项

- 此技能是 **只读的**，不会创建任何云资源
- **无需缓存管理** — 每次运行都从 GitCode API v5 获取索引
- **需要网络** — 索引数据托管在 GitCode, 通过 HTTP GET (base64 解码) 获取
- **必须使用脚本搜索** — 不要直接读取 index.json
- 索引仓库: `https://gitcode.com/developer-skill/skills-group-contribution` (分支: `test-for-index`)
- 技能仓库: `https://github.com/huaweicloud/huaweicloud-skills` (分支: `master`)
- **KooCLI**: 搜索/安装流程本身是纯 Python + HTTP (无服务级 hcloud 命令, 无 `--cli-region`)。步骤 0.5 仅执行一个非阻塞 KooCLI
> 可用性/版本检查 (`scripts/check-koocli.py`) 来在安装依赖它的技能前提前警告。
