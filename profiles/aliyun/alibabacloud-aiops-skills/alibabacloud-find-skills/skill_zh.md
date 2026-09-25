> [!IMPORTANT]
> **对于任何阿里云查询或管理任务：**
> 1. **搜索** — 使用此技能 (`alibabacloud-find-skills`) 查找相关技能。
> 2. **安装** — 仅在用户要求安装或使用它们完成任务时才安装所选技能。
> 3. **执行** — 按照已安装技能的说明来完成任务。

# 阿里云代理技能搜索与发现

此技能帮助用户从代理浏览器目录中搜索、发现和安装阿里云官方代理技能。

## 场景描述

此技能使用户能够：

1. **搜索技能** — 通过意图短语、关键词、分类列表或组合语义搜索查找阿里云代理技能
2. **浏览分类** — 探索可用技能分类和子分类
3. **查看技能详情** — 获取特定技能的详细信息
4. **安装技能** — 在要求安装时指导用户完成技能安装

**架构**: `curl` + 代理浏览器 HTTP API → 技能仓库

发现通过 `curl` 直接使用代理浏览器 HTTP API；不要使用 Aliyun CLI 或安装/更新 `agentexplorer` CLI 插件进行搜索、浏览或详情工作流。

### 用例

- "查找管理 ECS 实例的技能"
- "阿里云有哪些数据库相关的技能？"
- "阿里云有哪些 OSS 相关的技能？"
- "浏览所有可用的 alicloud 技能"
- "安装用于 RDS 管理的技能"

## 代理浏览器 HTTP API

**基本 URL**: `https://agentexplorer.aliyuncs.com`

每个代理浏览器 HTTP 请求必须包含这些头部。

```bash
# Bash 兼容的头部片段，适用于 macOS、Linux、WSL 和 Git Bash。
# 在 Windows 上，请使用 PowerShell 命令格式。
-H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
-H 'x-acs-version: 2026-03-17'
```

每个代理浏览器 HTTP `curl` / `curl.exe` 请求必须包含 `--connect-timeout 10 --max-time 30`。

### Shell 兼容的 curl 使用

在运行代理浏览器命令之前，选择适用于当前 Shell/OS 的命令格式。如果环境是 Windows，请使用 [API 格式](#api-shapes) 中的 Windows PowerShell 格式；有关 Shell 特定细节，请参阅 [references/curl-shell-compatibility.md](references/curl-shell-compatibility.md)。

### API 格式

#### Bash 兼容示例

```bash
# Bash 兼容的示例，适用于 macOS、Linux、WSL 和 Git Bash。
# 在 Windows 上，请使用上面 PowerShell 命令格式，并替换端点/查询参数。

# 搜索技能
curl -sS -G --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills' \
  --data-urlencode 'keyword=<user-intent-or-keyword>' \
  --data-urlencode 'searchMode=semantic' \
  --data-urlencode 'maxResults=20' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'

# 列出分类
curl -sS --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/categories' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'

# 获取技能内容
curl -sS --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills/<skillName>' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'
```

#### Windows PowerShell 搜索示例

在 Windows 上使用此命令格式，并根据需要仅替换查询参数：

```powershell
powershell -NoProfile -Command "curl.exe -sS -G --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills' --data-urlencode 'keyword=<user-intent-or-keyword>' --data-urlencode 'searchMode=semantic' --data-urlencode 'maxResults=20' -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' -H 'x-acs-version: 2026-03-17'"
```

## 核心工作流

### 第 1 步：了解他们的需求

在搜索之前，识别：

1. **领域** — 相关区域或阿里云产品系列，例如 ECS、RDS、OSS、SLS、PAI、测试、部署、数据分析。
2. **具体任务** — 用户想要做什么，例如诊断 ECS 问题、将文件同步到 OSS、构建数据分析项目、审查权限。
3. **技能可能性** — 这是否是一个常见到足以存在现有技能的任务。
4. **分类匹配** — 领域是否明显映射到已知分类。当用户要求浏览分类或必须确认 `categoryCode` 时，调用 `/openapi/for-agent/categories`；否则避免在初始理解阶段调用分类。

使用这种理解首先选择请求格式，然后仅在使用关键词或语义请求时才形成搜索文本。`keyword` 支持短关键词和完整意图短语。因为 `searchMode=semantic` 匹配技能描述，当可用时，优先使用用户的意图，例如 `建一个数据分析项目`，而不是将每个请求简化为单个产品词。

在搜索之前，使用 [搜索的意图分析](#1-intent-analysis-for-search) 将此分析转换为可搜索的意图单元。对于复合请求，每个有意义的请求或支持需求都必须成为其自己的可搜索意图单元，并独立搜索。

`搜索短语` 必须面向能力。它不应简单地复制用户的表面措辞，除非表面措辞已经清楚地命名了能力、产品或服务。

如果搜索短语主要是特定领域的标签、文档标题、组织特定术语、策略名称或私有/内部术语，请在搜索之前将其改写为底层能力。

### 第 2 步：搜索技能

根据请求和可用分类上下文从以下命令格式中选择。对于广泛的产品系列发现，在关键词搜索之前确认分类上下文，然后使用分类列表或分类范围搜索。对于没有有用分类上下文的任务匹配请求，默认使用语义意图搜索。

- **意图搜索（默认用于任务匹配）**：将用户的任务或完整意图短语作为 `keyword`，并使用 `searchMode=semantic`。
- **关键词搜索**：当意图广泛、嘈杂或已经命名产品/能力时，使用 `searchMode=semantic` 和简洁的产品/任务关键词。
- **浏览分类**：当用户要求可用分类或必须确认分类代码时，调用 `/openapi/for-agent/categories`。
- **列出分类中的技能**：仅使用 `categoryCode`。不要传递 `keyword` 或 `searchMode=semantic`；此模式支持分页。
- **组合语义搜索**：在分类选择后，仅在用户要求在该分类内查找最佳匹配时，使用 `keyword` 和 `categoryCode` 以及 `searchMode=semantic`。

根据用户请求选择一个请求格式：

```bash
# Bash 兼容的示例，适用于 macOS、Linux、WSL 和 Git Bash。
# 在 Windows 上，请使用上面 PowerShell 命令格式，并替换端点/查询参数。

# 意图或关键词搜索
curl -sS -G --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills' \
  --data-urlencode 'keyword=<user-intent-or-keyword>' \
  --data-urlencode 'searchMode=semantic' \
  --data-urlencode 'maxResults=20' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'

# 在列出分类中的技能之前获取所有分类
curl -sS --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/categories' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'

# 列出分类中的技能
curl -sS -G --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills' \
  --data-urlencode 'categoryCode=<category-code>' \
  --data-urlencode 'maxResults=20' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'

# 如果返回 nextToken，则获取下一个分类页
curl -sS -G --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills' \
  --data-urlencode 'categoryCode=<category-code>' \
  --data-urlencode 'maxResults=20' \
  --data-urlencode 'nextToken=<next-token-from-previous-response>' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'

# 分类选择后的组合语义搜索
curl -sS -G --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills' \
  --data-urlencode 'keyword=<user-intent-or-keyword>' \
  --data-urlencode 'categoryCode=<category-code>' \
  --data-urlencode 'searchMode=semantic' \
  --data-urlencode 'maxResults=20' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'
```

### 第 3 步：迭代直到找到

如果一个可搜索的意图单元没有明确的覆盖技能，或者结果很弱、过于通用或仅匹配表面/领域特定措辞，请在声明差距之前自动重写搜索短语并重试：

1. 当可用时，从用户的完整意图短语开始
2. 从请求中提取直接的产品/任务关键词
3. 在中文和英文术语之间切换（例如，“云服务器”→“ECS”，“对象存储”→“OSS”）
4. 广泛或简化关键词（删除限定词：“RDS 备份自动化”→“RDS”）
5. 使用 `/openapi/for-agent/categories`，选择最佳分类，然后使用组合搜索重试
6. 尝试同义词或相关术语（例如，“实例”→“ECS”，“存储桶”→“OSS”）

在尝试至少一个面向能力的搜索短语用于该意图单元之前，不要得出“不存在专用技能”的结论。

重复直到每个可搜索的意图单元都有一个明确的覆盖技能，或者被互补选择的技能覆盖，或者被确认为已知差距。如果一个意图单元的所有尝试都失败，请告知用户尝试了什么。

### 第 4 步：查看技能详情（可选）

可选地检索技能内容，以在安装之前验证它是否匹配用户意图。如果搜索结果已经提供足够的信息，可以跳过此步骤。

```bash
# Bash 兼容的示例，适用于 macOS、Linux、WSL 和 Git Bash。
# 在 Windows 上，请使用上面 PowerShell 命令格式，并替换端点/查询参数。

curl -sS --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills/<skillName>' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'
```

### 第 5 步：安装所选技能

当用户仅要求列出、浏览、比较或检查技能而不安装时，跳过此步骤。当要求安装时，为每个所选技能执行安装命令。

```bash
# 选项 A：使用 npx skills add
# 默认此命令是交互式的（等待用户输入）。
# 推荐：使用非交互模式以避免阻塞。
#   --agent <client>   要安装的代理客户端（请参阅 references/npx-skills-agents.md）
#   -g                 全局安装（家目录）；省略则为项目本地安装
#   -y                 跳过确认（需要 --agent 和 -g/-local 设置）
npx skills add aliyun/alibabacloud-aiops-skills \
  --skill <skill-name> \
  --full-depth \
  --agent qwen-code \
  -g -y

# 选项 B：使用 npx clawhub install（OpenClaw 生态系统）
npx clawhub install <selected-skill-name>
```

验证每个所选技能在安装后出现在可用技能列表中。

## API 参考

有关完整的 HTTP 参数细节和搜索参数规则，请参阅 [references/agentexplorer-api.md](references/agentexplorer-api.md)。

## 成功验证

每次操作后，通过检查以下内容来验证成功：

1. **列出分类**：响应包含 `data`，其中包含分类 `code` 和 `name` 字段
2. **搜索技能**：响应包含 `data`，其中包含有效的技能对象
3. **获取技能内容**：响应包含完整的技能 markdown `content`
4. **安装所选技能**：每个所选技能出现在可用技能列表中

有关详细的验证步骤，请参阅 [references/verification-method.md](references/verification-method.md)。

## 搜索策略

### 1. 搜索的意图分析

在选择搜索文本之前，将用户的请求分析为可搜索的意图单元。可搜索的意图单元应描述技能必须提供的能力，而不仅仅是用户的表面措辞。

对于每个有意义的请求，识别：

- **操作**：需要什么操作，例如查询、生成、诊断、部署、安装、验证、转换
- **对象**：操作适用于什么，例如文档、知识库、视频、脚本、数据库、CLI 环境
- **上下文/来源**：信息或资源来自哪里，例如内部文档、云服务、本地文件、OSS、数据库、运行时环境
- **预期输出**：用户期望返回什么，例如带引用的答案、生成的脚本、报告、命令指导、安装的依赖项
- **支持需求**：请求是否还需要插件、运行时依赖项、环境检查或故障排除

将显式的支持、阻止和回退子句视为可搜索的意图，即使它们是条件性的。这包括关于设置、依赖项、运行时环境、插件、连接性、验证、故障排除、修复或处理执行期间可能发生的错误的要求。不要因为这些子句不是主要业务目标而丢弃它们；如果它们可能需要单独的技能，请独立搜索它们。

然后使用以下格式形成一个或多个可搜索的意图短语：

`<操作> + <对象/能力> + <上下文/来源> + <预期输出>`

对于复合请求，为每个有意义的请求创建一个可搜索的意图单元，并独立搜索每个单元。不要假设一个技能覆盖整个请求，除非搜索结果明确说明它这样做。

一个可搜索的意图单元可能仍然需要多个互补的技能。当一个技能覆盖主要操作，但需要另一个技能来支持插件、运行时设置、数据访问或验证等需求时，选择两者并分别解释它们的作用。

### 2. 搜索文本选择

- **首先使用意图短语**：优先使用用户的自然语言任务或要求，例如 "建一个数据分析项目"、"把本地文件同步到 OSS"
- **当意图广泛或嘈杂时使用产品/任务关键词**：提取简洁的产品和操作术语，例如 "ECS 诊断"、"OSS 同步"
- **使用产品代码作为回退或细化**：`ecs`、`rds`、`oss`、`slb`、`vpc`
- **使用中文和英文变体**：例如 "云服务器" / "ECS"、"对象存储" / "OSS"
- **仅在特定意图搜索失败后使用更广泛的关键词**：例如 "compute"、"storage"、"network"

### 3. 分类过滤

- **需要时浏览**：当用户询问分类或领域应缩小搜索范围时，使用 `/openapi/for-agent/categories`
- **选择最佳分类**：将领域映射到最接近的 `categoryCode`，然后将其作为 `categoryCode` 传递
- **与意图结合**：对于在明确领域中清晰的任务，使用任务短语作为 `keyword`，并使用选择的分类作为 `categoryCode`

### 4. 结果优化

- **从意图开始**：从用户的任务描述开始，仅在领域明确或初始结果过于广泛时才添加分类过滤
- **将互补技能放在一起**：如果一个技能处理主要任务，另一个技能处理所需的设置、访问、验证或故障排除，请包含两者，而不是仅选择排名靠前的主技能
- **检查安装次数**：热门技能通常具有更高的安装次数
- **阅读描述**：将技能描述与您的具体用例匹配

### 5. 当未找到结果时

```bash
# Bash 兼容的示例，适用于 macOS、Linux、WSL 和 Git Bash。
# 在 Windows 上，请使用上面 PowerShell 命令格式，并替换端点/查询参数。

# 策略 1：尝试用户的完整意图
# 与仅 "OSS" 相比，尝试 "把本地文件同步到 OSS"

# 策略 2：提取产品/任务关键词
# 与 "云服务器故障排查" 相比，尝试 "ECS 诊断"

# 策略 3：尝试中文和英文变体
# 与 "云服务器" 相比，尝试 "ECS" 或 "instance"

# 策略 4：使用更广泛的关键词
# 与 "RDS 备份自动化" 相比，仅尝试 "RDS" 或 "database"

# 策略 5：浏览或按分类过滤
curl -sS --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/categories' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'

curl -sS -G --connect-timeout 10 --max-time 30 'https://agentexplorer.aliyuncs.com/openapi/for-agent/skills' \
  --data-urlencode 'keyword=ECS 实例管理' \
  --data-urlencode 'categoryCode=<selected-category-code>' \
  --data-urlencode 'searchMode=semantic' \
  --data-urlencode 'maxResults=20' \
  -H 'User-Agent: AlibabaCloud-Agent-Skills/alibabacloud-find-skills' \
  -H 'x-acs-version: 2026-03-17'
```

### 6. 向用户显示结果

当向用户显示搜索结果时，格式化为表格：

```
找到 N 个技能：

| 技能名称 | 显示名称 | 描述 | 分类 | 安装次数 |
|------------|--------------|-------------|----------|---------------|
| alibabacloud-ecs-batch | ECS 批量操作 | 批量管理 ECS 实例 | 计算 > ECS | 245 |
| ... | ... | ... | ... | ... |
```

包括：

- **skillName**：用于安装和详细查询
- **displayName**：用户友好名称
- **description**：简要概述
- **categoryName** + **subCategoryName**：分类
- **installCount**：流行度指标

## 清理

此技能不会创建任何资源。不需要清理。

## 最佳实践

1. **选择正确的搜索模式** — 用于任务匹配的语义意图或关键词搜索；当用户要求列出某个分类中的所有技能时，使用不带 `searchMode=semantic` 的分类列表
2. **按意图单元搜索** — 将复合请求拆分为有意义的能
