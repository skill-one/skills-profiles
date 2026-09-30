---
name: ccf-skill-forger
description: 维护和审计 Codex/CCFA 技能、触发器、参考、脚本、文档/SVG 图表、安装依赖项和发布验证。用于技能维护、GPT 模型适配和家庭路由清理。不要进行研究写作或评审。
---

# CCF技能伪造器

## 家族文件合同

在编写前，确定每个任务/成果的规范输出和一个稳定的作业目录。重用显式或已建立的任务路径；否则使用项目根目录 `ccfa-workfiles/<用途>/<成果ID>/`，仅在需要时使用 `source/`、`assets/`、`cache/` 和 `build/`。就地更新当前文件；不要分散中间文件或创建迭代副本。保留输入和所需证据；仅清理此任务创建的已验证可丢弃文件。使用UTF-8文本I/O，并在保存或渲染后检查中文文本。对于文件工作，应用 [artifact-contracts.md](../ccf-common/references/artifact-contracts.md) 并在技能转换期间重用相同的路径。

## 协作合同

在专家执行前，先阅读并应用 [ccf-humanization](../ccf-humanization/SKILL.md)，然后应用 [ccf-common](../ccf-common/SKILL.md)。在每次交接时，重用适用的活跃规则或刷新缺失/更改的规则。即使没有文本，这两个预检也是必需的；详细的编辑、实验和维护模式仅在相关时运行。

保留一个集成的负责人，并积极使用其他技能来解决缺失的先决条件或检查材料发现。重用适用的证据；不要为了节省token而跳过必要的准备工作。在最终确定前，集成贡献并验证受影响的成果。遵循条件性 [合作路线](../ccf-common/references/routing.md)；避免无关的阶段和重复报告。

## 调用控制

**CCFA交接模式：部分（推荐）。** 在维护CCFA技能家族时，遵循 `metadata.ccf_skill_controls.handoff_question_mode` 和 `../ccf-common/references/handoff-modes.md`。

在维护CCFA技能家族时，在每个 `SKILL.md` 中保留 `metadata.ccf_skill_controls`。在检查 `../ccf-common/references/routing.md`、`../ccf-common/references/task-modes.md`、`../ccf-common/references/handoff-modes.md` 和尊重拒绝列表的回退之前，不要添加兄弟技能转换。

如果用户禁用技能或要求仅写入行为，请直接在编辑的技能指令中编码该边界。除非用户明确要求政策变更，否则不要在写入技能中削弱思想范围保护。

在添加源时，更新 `../ccf-common/references/source-registry.yaml` 而不是在兄弟技能中复制URL列表。在添加浏览或证据规则时，保持它们与 `../ccf-common/references/privacy-and-evidence.md` 一致。

永远不要将特定于机器的绝对路径、用户名、展开的home目录或私有本地目录名称提交到技能、README文件、源注册表、图表、示例、脚本或命令片段中。使用 `$CODEX_HOME`、`$HOME`、仓库相对路径或不识别用户或机器的占位符。

## 核心规则

将技能构建为另一个Codex会话的紧凑操作指南。保持 `SKILL.md` 聚焦于触发相关的流程、决策和资源导航。将详细的示例、清单、模式、政策文本或长指令放在 `references/` 中，并且仅在需要时加载它们。此技能还拥有CCFA文档SVG图表；不要为仓库架构或流程图创建单独的运行时绘图技能。

## 工作流

1. 使用具体示例澄清目标。如果用户的意图明确，则按合理的假设进行。仅询问改变技能范围、位置或所需资产的信息缺失。
2. 选择技能名称和目标位置。仅使用小写字母、数字和连字符；保持名称在64个字符以内；检查目标技能目录中的冲突。默认为 `$CODEX_HOME/skills`；如果未设置，则使用 `~/.codex/skills`。
3. 确定资源形状：
   - 仅使用 `SKILL.md` 进行简短、稳定的程序性指导。
   - 添加 `references/` 用于Codex应选择性地读取的详细文档。
   - 仅在重复的确定性操作或易碎的命令序列时添加 `scripts/`。
   - 仅在最终输出中使用模板、图像、样板或其他文件时添加 `assets/`。
4. 从空白创建时初始化技能。如果可用，请优先使用本地 `skill-creator` 初始化器：

```powershell
python '<skill-creator-dir>/scripts/init_skill.py' <skill-name> --path '<skills-dir>' --resources references,scripts
```

5. 在填充可选资源之前编写 `SKILL.md`。将所有“何时使用”的触发词放在YAML `description` 中；正文仅在触发选择后才加载。在共享任务模式下应用功能命名规则到方法介绍和报告标题，同时保留源记录和叙述内容。使用祈使指令，避免面向用户的教程文本。
6. 添加直接支持技能的资源。删除占位符文件和未使用的目录。通过在小型代表性示例上运行它来测试任何脚本。
7. 使用现有的家族检查验证更改的行为和结构。比较 SKILL.md、代理提示、注册表、共享规则和文档以查找冲突。检查实际的YAML元数据、现有脚本的语法、资源依赖关系和代表性任务边界；区分静态检查和实际模型评估。保留公共路径和命令兼容性。在用户将工作限制为现有表面时，不要添加新文件、依赖关系或评估。
8. 在完成CCFA家族维护之前运行 `ccf-common/scripts/check_path_privacy.py`。将任何提交的本地绝对路径或用户名替换为 `$CODEX_HOME`、`$HOME`、仓库相对路径或非识别占位符。
9. 对于CCFA文档图表，在CCFA仓库检出中工作，更新其 `tools/build_ccfa_diagrams.py`，重新生成所有语言变体，并截图检查渲染的SVG输出。使用 `references/svg-style-guide.md`；除非将相同的更改回退到生成器，否则不要手动编辑生成的SVG。

对于模型适配，使用当前的官方指南并将其来源存储在现有的源注册表中。在添加新指令之前删除冲突或冗余指令。将模型设置和仅API功能保留在主机中；不要在每个技能中硬编码模型，或在没有代表性比较的情况下声称收益。

## 参考文件

仅在任务要求时加载这些文件：

- `references/design-checklist.md`：在规划新技能、审查结构或决定内容是否属于 `SKILL.md`、`references/`、`scripts/` 或 `assets/` 时使用。
- `references/patterns.md`：在起草具体的 `SKILL.md` 形状、frontmatter描述或示例驱动流程时使用。
- `references/local-commands.md`：在构建或验证此机器上的技能时使用，特别是在PowerShell或Windows路径中。
- `references/svg-style-guide.md`：在维护CCFA架构、流程、路由、安装、成果、目录或演示SVG图表时使用。

## 输出风格

使用已批准的方案，无需再次确认。对于显式的仅计划请求，在可审查的提案后停止；对于授权维护，在请求的现有文件中实现它。创建后，报告技能名称、位置、关键文件和验证结果。如果由于本地依赖缺失而无法运行验证，请明确说明失败的内容并执行 `references/design-checklist.md` 中的手动检查。
