# Azure 架构构建器

一个使用自然语言设计 Azure 基础设施，或分析现有资源以可视化架构并继续进行修改和部署的流程。

图表示例引擎**嵌入在技能中**（`scripts/` 文件夹）。
无需 `pip install` — 它直接使用捆绑的 Python 脚本
生成具有 605+ 个官方 Azure 图标的交互式 HTML 图表。
无需网络访问或包安装即可立即使用。

## 自动用户语言检测

**🚨 检测用户第一条消息的语言，并在后续所有响应中使用该语言。这是最高优先级的准则。**

- 如果用户使用韩语编写 → 使用韩语回复
- 如果用户使用英语编写 → **使用英语回复**（ask_user、进度更新、报告、Bicep 注释 — 所有内容均使用英语）
- 本文档中的说明和示例使用英语编写，**所有面向用户的输出必须与用户的语言匹配**

**⚠️ 不要逐字复制本文档中的示例给用户。**
仅参考结构，并根据用户的语言调整文本。

## 工具使用指南（GHCP 环境）

| 功能 | 工具名称 | 备注 |
|------|----------|------|
| 获取 URL 内容 | `web_fetch` | 用于 MS Docs 查找等 |
| 网络搜索 | `web_search` | URL 发现 |
| 询问用户 | `ask_user` | `choices` 必须是字符串数组 |
| 子代理 | `task` | explore/task/general-purpose |
| Shell 命令执行 | `powershell` | Windows PowerShell |

> 所有子代理（explore/task/general-purpose）不能使用 `web_fetch` 或 `web_search`。
> 需要使用 MS Docs 查找进行事实核查的操作必须由**主代理直接执行**。

## 外部工具路径发现

`az`、`python`、`bicep` 等通常不在 PATH 中。
**在开始阶段前发现一次并缓存结果。不要每次都重新发现。**

> **⚠️ 不要使用 `Get-Command python`** — 风险是 Windows Store 别名。
> 直接文件系统发现（`$env:LOCALAPPDATA\Programs\Python`）优先。

az CLI 路径：
```powershell
$azCmd = $null
if (Get-Command az -ErrorAction SilentlyContinue) { $azCmd = 'az' }
if (-not $azCmd) {
  $azExe = Get-ChildItem -Path "$env:ProgramFiles\Microsoft SDKs\Azure\CLI2\wbin", "$env:LOCALAPPDATA\Programs\Azure CLI\wbin" -Filter "az.cmd" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
  if ($azExe) { $azCmd = $azExe }
}
```

Python 路径 + 嵌入式图表示例引擎：参考 `references/phase1-advisor.md` 中的图表示例生成部分。

## 进度更新要求

使用 blockquote + emoji + 粗体格式：
```markdown
> **⏳ [操作]** — [原因]
> **✅ [完成]** — [结果]
> **⚠️ [警告]** — [详情]
> **❌ [失败]** — [原因]
```

## 并行预加载原则

在等待用户通过 `ask_user` 输入时，并行预加载下一步所需的信息。

| ask_user 问题 | 同时预加载 |
|------|----------|
| 项目名称 / 扫描范围 | 参考文件、MS Docs、Python 路径发现、**图表示例模块路径验证** |
| 模型/SKU 选择 | 用于下一个问题的 MS Docs |
| 架构确认 | `az account show/list`、`az group list` |
| 订阅选择 | `az group list` |

---

## 路径分支 — 由用户请求自动确定

### 路径 A：新设计（新建）

**触发**： "创建"、"设置"、"部署"、"构建" 等。
```
阶段 1（references/phase1-advisor.md） — 交互式架构设计 + 图表示例
    ↓
阶段 2（references/bicep-generator.md） — Bicep 代码生成
    ↓
阶段 3（references/bicep-reviewer.md） — 代码审查 + 编译验证
    ↓
阶段 4（references/phase4-deployer.md） — 验证 → what-if → 部署
```

### 路径 B：现有分析 + 修改（分析 & 修改）

**触发**： "分析"、"当前资源"、"扫描"、"绘制图表示例"、"显示我的基础设施" 等。
```
阶段 0（references/phase0-scanner.md） — 现有资源扫描 + 图表示例
    ↓
修改对话 — "您想在这里修改什么？"（自然语言修改请求 → 随后问题）
    ↓
阶段 1（references/phase1-advisor.md） — 确认修改 + 更新图表示例
    ↓
阶段 2~4 — 与上述相同
```

### 当路径确定不明确时

直接询问用户：
```
ask_user({
  question: "您想做什么？",
  choices: [
    "设计新的 Azure 架构（推荐）",
    "分析 + 修改现有的 Azure 资源"
  ]
})
```

---

## 阶段转换规则

- 每个阶段读取并遵循其对应的 `references/*.md` 文件中的说明
- 在阶段之间转换时，始终告知用户下一步操作
- 不要跳过阶段（尤其是阶段 3 → 阶段 4 之间的 what-if）
- **🚨 阶段 1 → 阶段 2 转换的必要条件**：`01_arch_diagram_draft.html` 必须使用嵌入式图表示例引擎生成并展示给用户。**没有图表示例不要进行 Bicep 生成。** 完成规范收集本身并不意味着阶段 1 完成 — 阶段 1 包括图表示例生成 + 用户确认。
- 部署后的修改请求 → 返回阶段 1，而不是阶段 0（增量确认规则）

## 服务覆盖 & 回退

### 优化服务
Microsoft Foundry、Azure OpenAI、AI 搜索、ADLS Gen2、Key Vault、Microsoft Fabric、Azure Data Factory、VNet/私有端点、AML/AI Hub

### 其他 Azure 服务
所有支持 — 自动咨询 MS Docs 以生成相同质量标准的内容。
**不要发送导致用户焦虑的消息，例如 "超出范围" 或 "尽力而为"。**

### 稳定 vs 动态信息处理

| 类别 | 处理方法 | 示例 |
|------|----------|------|
| **稳定** | 首先参考文件 | `isHnsEnabled: true`、PE 三重集 |
| **动态** | **始终获取 MS Docs** | API 版本、模型可用性、SKU、区域 |

## 快速参考

| 文件 | 角色 |
|------|------|
| `references/phase0-scanner.md` | 现有资源扫描 + 关系推理 + 图表示例 |
| `references/phase1-advisor.md` | 交互式架构设计 + 事实核查 |
| `references/bicep-generator.md` | Bicep 代码生成规则 |
| `references/bicep-reviewer.md` | 代码审查清单 |
| `references/phase4-deployer.md` | 验证 → what-if → 部署 |
| `references/service-gotchas.md` | 必要属性、PE 映射 |
| `references/azure-dynamic-sources.md` | MS Docs URL 注册表 |
| `references/azure-common-patterns.md` | PE/安全/命名模式 |
| `references/ai-data.md` | AI/数据服务指南 |
| `assets/06-architecture-diagram.png` | 示例生成的架构图表示例 |
| `assets/07-azure-portal-resources.png` | 示例 Azure 门户资源视图 |
| `assets/08-deployment-succeeded.png` | 示例成功部署结果 |
