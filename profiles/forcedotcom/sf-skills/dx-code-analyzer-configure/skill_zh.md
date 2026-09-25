# 配置代码分析器技能

## 概述

> **生态系统：** 此技能是 3 技能代码分析器套件的一部分 — `dx-code-analyzer-run`（扫描 & 结果）· `dx-code-analyzer-configure`（设置、配置、CI/CD）· `dx-code-analyzer-custom-rule-create`（自定义规则编写）。

此技能管理 `code-analyzer.yml` 配置文件 — 项目中代码分析器行为的单一事实来源。所有自定义（引擎、规则、忽略、抑制）都是通过创建或编辑此文件完成的。如果文件不存在，此技能会在当前工作目录中创建它。

---

## 范围

**在范围内：**
- 检查先决条件（sf CLI、Java、Node.js、Python、组织授权）
- 安装/更新代码分析器插件
- 如果不存在，则创建 `code-analyzer.yml`
- 编辑 `code-analyzer.yml` 以进行所有配置更改
- 引擎设置、规则覆盖、忽略模式、抑制
- CI/CD 管道设置（GitHub Actions、Jenkins 等）
- 环境验证和故障排除

**超出范围：**
- 运行扫描 → 使用 `dx-code-analyzer-run` 技能
- 修复违规、解释规则、抑制管理 → 使用 `dx-code-analyzer-run` 技能
- 创建自定义规则 → 使用 `dx-code-analyzer-custom-rule-create` 技能

---

## 工具使用规则

**允许：** Bash (sf, java, node, python3, npm), Read, Write, Edit
**禁止：** MCP 工具、Agent 工具、Web 工具、其他技能、`which`, `find`, `locate`, 搜索二进制文件

---

## 核心原则：仅自定义时使用 YAML

代码分析器无需配置文件即可开箱即用 — 所有默认值都内置在工具中。`code-analyzer.yml` 文件仅在用户明确要求自定义时才创建。

**规则：**
- **不要主动创建 `code-analyzer.yml`** — 仅在用户要求更改时创建
- **不要重复内置默认值** — 仅编写有意覆盖行为的条目
- **始终放置在项目根目录** — `sfdx-project.json` 或 `sf-project.json` 所在的位置
- **CLI 自动发现它** — 从项目根目录运行 `sf code-analyzer run` 会自动选择该目录中的 `code-analyzer.yml`。不需要 `--config-file` 标志。
- 用户说“配置代码分析器”但没有具体说明？ → **询问他们想要自定义什么**。不要创建空或样板文件。

**工作流程：**
1. 用户请求自定义（例如，“禁用 PMD”、“忽略测试文件”、“增加 SFGE 内存”）
2. 检查项目根目录是否存在 `code-analyzer.yml`
3. 如果没有 → 在项目根目录创建它，仅包含请求的覆盖
4. 如果有 → 读取它，然后编辑请求的更改
5. 使用 `sf code-analyzer config` 进行验证

---

## 第 1 步：理解意图并映射到配置部分

用户可以用自然语言请求任何配置更改的组合。你的工作是：

1. **解析他们想要什么** — 可能是一个或多个事情的组合
2. **将每个请求映射到 `code-analyzer.yml` 的正确部分**
3. **如果文件不存在，则创建文件，然后应用所有更改**

### `code-analyzer.yml` 结构（可以写入/编辑的内容）

```yaml
config_root: .                    # 相对路径解析的根目录
log_folder: <path>                # 日志写入位置
log_level: <1-5>                  # 1=错误, 2=警告, 3=信息, 4=调试, 5=精细

ignores:                          # 从扫描中排除的文件/文件夹
  files: [<glob patterns>]

engines:                          # 每个引擎的设置
  <engine_name>:
    disable_engine: <bool>
    <engine_specific_keys>: ...

rules:                            # 每个规则的覆盖
  <engine_name>:
    <rule_name>:
      severity: <1-5>
      tags: [<strings>]
      disabled: <bool>

suppressions:                     # 批量抑制配置
  disable_suppressions: <bool>
  "<file_or_folder_path>":
    - rule_selector: "<selector>"
      max_suppressed_violations: <number|null>
      reason: "<why>"
```

### 映射原则

任何用户请求都映射到上述一个或多个部分。解析意图并编辑正确的部分：

| 意图类别 | 映射到 | 用户可能说的示例 |
|---------|-------|-----------------|
| 设置 / 安装 | 第 2 步（先决条件 + 安装） | "设置", "安装", "开始使用", "新笔记本电脑", "从零开始" |
| **诊断 / 修复** | **第 2A 步（系统化调试）** | **"不工作", "损坏", "修复我的设置", "扫描失败", "出现错误"** |
| 引擎控制 | `engines.<name>.disable_engine` | "禁用 X", "关闭 Y", "仅使用 Z", "启用所有" |
| 引擎调优 | `engines.<name>.<property>` | "增加内存", "更改堆", "使用我的 eslint 配置", "将令牌设置为 50" |
| 文件排除 | `ignores.files` | "排除", "忽略", "跳过", "不扫描 X" |
| 规则严重性 | `rules.<engine>.<rule>.severity` | "将 X 设置为关键", "提升", "降低", "更改严重性" |
| 规则禁用 | `rules.<engine>.<rule>.disabled` | "禁用规则 X", "关闭 Y 规则", "移除 Z" |
| 规则标签 | `rules.<engine>.<rule>.tags` | "将 X 标记为安全", "添加推荐标签" |
| 抑制 | `suppressions` 部分 | "在文件夹 Y 中抑制 X", "允许 N 个违规" |
| CI/CD | 生成管道文件（与配置分开） | "github actions", "CI", "质量门" |
| 查看/检查 | 读取文件 + `sf code-analyzer config` | "显示配置", "已配置什么", "当前设置" |

### 文件存在性决策

**在编辑任何内容之前**，检查项目根目录是否存在 `code-analyzer.yml`：

```bash
ls code-analyzer.yml code-analyzer.yaml 2>/dev/null
```

- **文件不存在** → 在项目根目录创建它，仅包含用户的请求覆盖
- **文件存在** → 读取它，然后编辑以添加/修改请求的部分

CLI 会自动发现当前目录中的 `code-analyzer.yml`。由于扫描从项目根目录运行，文件必须存放在那里。

### 规则名称解析 — 始终在写入 YAML 之前

当用户通过部分、描述性或近似名称引用规则（例如，“文档规则”、“CRUD 违规”、“控制台规则”、“硬编码值”）时，你必须使用 **第 6.1 步** 中的查找来解析到确切的规则名称，然后再写入任何 YAML。`code-analyzer.yml` 文件会静默忽略与确切名称不匹配的规则名称 — 没有错误，覆盖将不会应用。

**需要模糊→确切解析的示例：**
- "禁用 ApexDoc 规则" → 查找确认 `ApexDoc`（引擎：`pmd`）
- "将 no-console 降级为低" → 查找确认 `no-console`（引擎：`eslint`）
- "将 CRUD 违规设置为关键" → 查找确认 `ApexCRUDViolation`（引擎：`pmd`）
- "关闭硬编码值检查" → 查找发现 `@salesforce-ux/slds/no-hardcoded-values-slds2`（引擎：`eslint`）
- "禁用注入规则" → 多个匹配可能 → 询问用户是哪一个

**仅在用户提供一个无歧义、确切、众所周知的名称时才跳过查找**（例如，“ApexDoc”、“no-console”、“no-unused-vars”）。

### 处理组合/复杂请求

用户通常会在一个请求中组合多个更改。在单个编辑中处理所有更改：

- "禁用 PMD 的 ApexDoc 规则并将 CRUD 违规设置为关键" → 在 `rules.pmd` 下编辑两个条目
- "排除测试文件和供应商代码，并增加 SFGE 内存" → 编辑 `ignores.files` + `engines.sfge.java_max_heap_size`
- "使用 ESLint 和 PMD 仅设置代码分析器，忽略 node_modules" → 创建文件，包含 `engines`（禁用其他）+ `ignores`
- "将所有安全规则严重性设置为 1" → 通过 `sf code-analyzer rules --rule-selector Security` 查找规则，然后覆盖每个规则
- "配置代码分析器"（没有具体说明）→ 在创建任何文件之前询问用户他们想要自定义什么

### 快速参考：常见请求→配置输出

| 用户说 | 结果ing YAML |
|-------|---------------|
| "configure code analyzer" | 询问用户要自定义什么 — 在有实际覆盖之前不要创建文件 |
| "disable the ApexDoc rule" | `rules: pmd: ApexDoc: disabled: true` |
| "仅扫描 Apex，不扫描 JavaScript" | `engines: eslint: disable_engine: true` + `engines: retire-js: disable_engine: true` |
| "忽略所有测试文件" | `ignores: files: ["**/test/**", "**/__tests__/**", "**/*.test.js"]` |
| "将安全规则严重性设置为关键" | 查找规则，然后 `rules: <engine>: <rule>: severity: 1` 为每个规则 |
| "将 SFGE 内存增加到 8g" | `engines: sfge: java_max_heap_size: "8g"` |
| "使用我项目的 ESLint 配置" | `engines: eslint: auto_discover_eslint_config: true` |
| "在旧版文件夹中抑制 CRUD 违规" | `suppressions: "force-app/legacy/": [{rule_selector: "pmd:ApexCRUDViolation", reason: "..."}]` |

**AI 必须理解 YAML 模式，并为任何请求编写有效的配置，而不仅仅是上面的示例。**

---

## 第 2 步：检查先决条件并安装

运行 `bash "<skill_dir>/scripts/check-prerequisites.sh"` 或手动检查：

```bash
sf --version 2>&1                                    # sf CLI
sf plugins --core 2>&1 | grep -i "code-analyzer"    # 插件
java -version 2>&1                                   # Java 11+ (PMD, CPD, SFGE)
node --version 2>&1                                  # Node 18+ (ESLint, RetireJS)
python3 --version 2>&1                               # Python 3 (Flow 引擎)
```

如果任何内容缺失，请安装它（**始终先询问用户**）：

```bash
npm install -g @salesforce/cli                       # sf CLI
sf plugins install @salesforce/plugin-code-analyzer  # 代码分析器插件
```

对于 Java/Node/Python 安装，请阅读 `<skill_dir>/references/engine-prerequisites.md`。
如果安装失败，请阅读 `<skill_dir>/references/troubleshooting.md`。

---

## 第 2A 步：诊断和修复损坏的设置

**触发条件：** 用户说“不工作”、“损坏”、“出现错误”、“扫描失败”、“帮助我修复”等。

**读取 `<skill_dir>/references/diagnostic-flow.md`** 以获取完整的多层诊断程序、修复表和反模式。

**关键原则（始终应用）：**
- 从不搜索二进制文件（`which`, `find`, `ls /opt/homebrew/bin/`）
- 从不使用 `sfdx` 作为解决方法 — 仅使用 `sf`
- 按层修复：CLI → 插件 → 引擎依赖 → 验证扫描
- 一次给用户一个命令，等待确认后再继续
- 修复成功后，自动继续运行完整扫描

---

## 第 3 步：创建或编辑 `code-analyzer.yml`

**仅在用户请求自定义时触发。** 从不主动创建。

### 创建（文件不存在）

选择以下两种方法之一 — 不要同时运行：

**选项 A — 根据项目类型自动生成（首次设置推荐）：**

运行 `bash "<skill_dir>/scripts/generate-config.sh"`。此脚本检测 Apex、LWC 和 Flow 标记，并生成适合项目的最小 `code-analyzer.yml`。跳转到“任何创建/编辑后验证”部分。

> 注意：如果 `code-analyzer.yml` 已存在，脚本会以错误退出。如果您需要重新生成，请先删除现有文件。

**选项 B — 手动编写（当用户有特定的自定义想法时）：**

作为结构参考，读取适当的示例配置：
- 对于仅 Apex 项目，读取 `<skill_dir>/examples/apex-project-config.yml`
- 对于仅 LWC 项目，读取 `<skill_dir>/examples/lwc-project-config.yml`
- 对于全栈（Apex + LWC + Flows），读取 `<skill_dir>/examples/fullstack-project-config.yml`

使用 Write 工具在项目根目录编写文件。仅包含用户的请求更改：

```bash
# 示例：用户说“忽略测试文件并增加 SFGE 内存”
# → 写入项目根目录（`sfdx-project.json` 所在位置）：
```

```yaml
ignores:
  files:
    - "**/test/**"
    - "**/__tests__/**"

engines:
  sfge:
    java_max_heap_size: "4g"
```

不要添加 `config_root`、`log_folder` 或任何用户没有请求的字段。

### 编辑（文件已存在）

读取文件，然后使用 Edit 工具添加/修改相关部分。保留所有其他内容。

### 任何创建/编辑后验证：

运行 `bash "<skill_dir>/scripts/validate-config.sh"` 以验证 YAML 语法和模式正确性，或直接使用 CLI：

```bash
sf code-analyzer config
```

(不需要 `--config-file` 标志 — CLI 会自动发现当前目录中的 `code-analyzer.yml`。)

### 如果用户说“配置代码分析器”但没有具体说明

询问：“您想要自定义什么？例如：忽略某些文件、更改规则严重性、调整引擎设置或禁用不需要的引擎。”

---

## 第 4 步：启用/禁用引擎

编辑 `code-analyzer.yml` 中的 `engines` 部分：

```yaml
engines:
  pmd:
    disable_engine: true       # 禁用 PMD
  eslint:
    disable_engine: false      # 启用 ESLint（默认）
```

有效引擎名称：`pmd`, `cpd`, `eslint`, `regex`, `retire-js`, `flow`, `sfge`, `apexguru`

**编辑后始终验证：**
```bash
sf code-analyzer config --config-file code-analyzer.yml
```

---

## 第 5 步：忽略模式

编辑 `code-analyzer.yml` 中的 `ignores` 部分：

```yaml
ignores:
  files:
    - "**/node_modules/**"
    - "**/.sfdx/**"
    - "**/.sf/**"
    - "**/vendor/**"
    - "**/*.min.js"
```

常见模式：

| 模式 | 排除 |
|-------|------|
| `**/node_modules/**` | npm 依赖 |
| `**/.sfdx/**`, `**/.sf/**` | SF CLI 内部 |
| `**/test/**`, `**/__tests__/**` | 测试目录 |
| `**/*.test.js`, `**/*.spec.js` | 测试文件 |
| `**/jest-mocks/**` | Jest 模拟 |
| `**/vendor/**`, `**/*.min.js` | 第三方/压缩 |
| `**/staticresources/**` | 静态资源 |

---

## 第 6 步：规则覆盖

编辑 `code-analyzer.yml` 中的 `rules` 部分。每个规则可以有 `severity`、`tags` 和 `disabled` 覆盖：

```yaml
rules:
  pmd:
    ApexCRUDViolation:
      severity: 1              # 提升为关键
    AvoidGlobalModifier:
      disabled: true           # 完全关闭
    ApexDoc:
      severity: 5              # 降低为信息
      tags: ["Documentation"]
  eslint:
    no-console:
      severity: 4              # 降低为低
    no-unused-vars:
      severity: 2              # 提升为高
```

**严重性值：** `1`/关键, `2`/高, `3`/中等, `4`/低, `5`/信息

### 6.1 规则名称解析（模糊匹配）

**关键：** `code-analyzer.yml` 中的拼写错误或部分规则名称会被静默忽略 — 没有错误，覆盖将不会应用。

当用户通过近似名称引用规则时（例如，“文档规则”、“CRUD 违规”、“硬编码值”），在写入 YAML 之前解析到确切名称：

```bash
sf code-analyzer rules --rule-selector all 2>&1 | grep -i "<USER_KEYWORD>"
```

- **1 个匹配** → 使用确切的名称 + 其引擎作为 YAML 路径
- **多个匹配** → 询问用户他们指的是哪一个
- **0 个匹配** → 尝试更广泛的关键字或通知用户

**仅当名称无歧义且确切时才跳过查找**（例如，“ApexDoc”、“no-console”、“no-unused-vars”）。

**有关详细匹配策略、常见模糊→确切映射和引擎识别**：阅读 `<skill_dir>/references/rule-name-resolution.md`。

---

## 第 7 步：引擎特定设置

编辑 `engines` 部分。最常见的覆盖：

```yaml
engines:
  sfge:
    java_max_heap_size: "4g"      # <200 类→"2g", 200-500→"4g", 500+→"6g"/"8g"
    java_thread_count: 4
    java_thread_timeout: 900000
  eslint:
    auto_discover_eslint_config: true    # 使用项目的 ESLint 配置
    eslint_config_file: "./eslint.config.mjs"
  pmd:
    custom_rulesets: ["./config/custom-pmd-rules.xml"]
    java_classpath_entries: ["./lib/custom-rules.jar"]
  cpd:
    minimum_tokens: { apex: 100, javascript: 100 }
  apexguru:
    target_org: "my-org-alias"
  flow:
    python_command: "python3"
  # regex.custom_rules — 使用 `dx-code-analyzer-custom-rule-create` 技能创建这些。
  # 从不手动将 regex 模式写入 `code-analyzer.yml`：YAML 中的引号/反斜杠会导致解析失败。`create-regex-rule.js` 脚本正确处理序列化，并且必须始终用于 regex 规则创建。
```

每个引擎的完整属性列表请阅读 `<skill_dir>/references/config-schema.md`。

---

## 第 8 步：CI/CD 管道设置

从工作区检测 CI 系统（`.github/workflows/` → GitHub Actions, `Jenkinsfile` → Jenkins 等）。阅读 `<skill_dir>/references/ci-cd-templates.md` 获取模板。使用 `<skill_dir>/examples/ci-github-actions.yml` 作为 GitHub Actions 基线。关键标志：`--severity-threshold 2`（门禁），`--output-file results.sarif`（GitHub 扫描），`--config-file code-analyzer.yml`。

---

## 第 9 步：查看当前配置

```bash
sf code-analyzer config                               # 显示有效配置
sf code-analyzer config --rule-selector pmd:Security  # 具体规则
sf code-analyzer config --include-unmodified-rules    # 所有默认值
```

---

## 跨技能集成

此技能与 `dx-code-analyzer-run` 协同工作。AI 代理应在它们之间无缝切换：

### 当 `dx-code-analyzer-run` 将执行委托到此：

如果用户说“扫描我的代码” / “运行代码分析器”但失败（CLI 缺失、插件未安装或扫描错误输出），`dx-code-analyzer-run` 将委托到此技能。在这种情况下：

1. 运行 **诊断和修复** 流程（第 2A 步）— 找出什么损坏，修复它
2. 一切正常后，**自动继续运行扫描** — 不要停止并询问。用户的原始意图是扫描。
3. 将执行交还给 `dx-code-analyzer-run` 行为（构建命令、执行、解析结果）。

### 当此技能将执行委托给 `dx-code-analyzer-run`：

在成功的配置操作后，建议运行扫描（例如，“设置完成！要我运行扫描吗？”，“配置已更新 — 要扫描并验证吗？”）。如果用户说“是”，则继续执行 `dx-code-analyzer-run` 行为。

### 当此技能将执行委托给 `dx-code-analyzer-custom-rule-create`：

如果用户在处理配置时要求创建自定义规则（例如，“也添加一个禁止 System.debug 的规则”，“设置 PMD XPath 规则”），则委托给 `dx-code-analyzer-custom-rule-create`。当该技能完成时，`code-analyzer.yml` 中的 `custom_rulesets` 或 `eslint_config_file` 指针可能需要设置 — 该编辑属于此技能。

### 当用户意图跨越两个技能：

端到端处理：**“不工作”** → 诊断 → 修复 → 扫描。**“设置并扫描”** → 安装 → 扫描。**“禁用 ESLint 并扫描 Apex”** → 编辑配置 → 使用 `--rule-selector pmd` 运行。**“配置自定义规则并扫描”** → `dx-code-analyzer-custom-rule-create` → 连接配置 → `dx-code-analyzer-run`。始终遵循到用户的最终意图。

---

## 规则 / 约束

| 约束 | 理由 |
|-------|-----------|
| 仅在用户请求自定义时创建 YAML | 默认值无需任何文件即可工作 — 不要创建样板文件 |
| 仅将 YAML 放在项目根目录 | CLI 从当前目录自动发现 `code-analyzer.yml` |
| 仅写入覆盖，从不重复默认值 | 保持文件最小且有意 |
| 使用 Write 工具创建，Edit 工具修改 | 保留现有设置 |
| 每次更改后验证 | `sf code-analyzer config` 捕获 YAML 错误 |
| 安装先决条件前询问 | 从不未经同意自动安装 |
| 从不未经询问删除现有配置 | 用户可能有自定义设置 |
| 设置后，建议扫描 | 闭环 — 没有扫描的配置是不完整的 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|----------|
| 配置未拾取 | 必须是当前目录中的 `code-analyzer.yml` 或使用 `--config-file` |
| YAML 验证失败 | 仅空格（不要制表符），检查冒号间距 |
| SFGE 内存不足 | 增加 `java_max_heap_size` 在 engines 部分 |
| ESLint 规则缺失 | 设置 `auto_discover_eslint_config: true` |

有关完整故障排除，请阅读 `<skill_dir>/references/troubleshooting.md`。

---

## 参考文件索引

`<skill_dir>` 是包含此 `SKILL.md` 文件的目录的绝对路径。

| 文件 | 目的 |
|------|---------|
| `<skill_dir>/scripts/check-prerequisites.sh` | 环境检查 |
| `<skill_dir>/scripts/generate-config.sh` | 自动检测项目类型并生成配置 |
| `<skill_dir>/scripts/validate-config.sh` | 更改后的 YAML 验证 |
| `<skill_dir>/references/config-schema.md` | 完整 YAML 模式文档 |
| `<skill_dir>/references/diagnostic-flow.md` | 第 2A 步：分层诊断程序和修复表 |
| `<skill_dir>/references/rule-name-resolution.md` | 第 6.1 步：模糊规则名称查找策略和映射 |
| `<skill_dir>/references/engine-prerequisites.md` | 每个引擎的安装说明 |
| `<skill_dir>/references/ci-cd-templates.md` | CI/CD 管道模板 |
| `<skill_dir>/references/troubleshooting.md` | 常见设置问题和修复 |
| `<skill_dir>/examples/apex-project-config.yml` | 仅 Apex 项目的配置 |
| `<skill_dir>/examples/lwc-project-config.yml` | 仅 LWC 项目的配置 |
| `<skill_dir>/examples/fullstack-project-config.yml` | Apex + LWC + Flows 的配置 |
| `<skill_dir>/examples/ci-github-actions.yml` | GitHub Actions 工作流 |
