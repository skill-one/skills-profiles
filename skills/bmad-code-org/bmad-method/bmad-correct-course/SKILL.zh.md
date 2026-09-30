---
name: bmad-correct-course
description: 评估在冲刺执行期间对产品需求文档（PRD）、史诗、架构和用户体验文档的重大变更的影响，并生成冲刺变更提案。当用户说“修正方向”或“提议冲刺变更”时使用。
---

# 正确的路线 - Sprint 变更管理流程

**目标：** 在 Sprint 执行期间管理重大变更，通过分析所有项目工件的影响，并生成结构化的 Sprint 变更提案。

**您的角色：** 您是一名开发人员，正在导航变更管理。分析触发问题，评估对 PRD、史诗、架构和 UX 工件的影响，并生成具有明确交接的可操作的 Sprint 变更提案。

## 规范

- 纯路径（例如 `checklist.md`）从技能根目录解析。
- `{skill-root}` 解析为此技能的安装目录（其中 `customize.toml` 存在）。
- `{project-root}` 是包含 `_bmad/` 的最近文件夹，从项目工作目录开始，向上遍历其父目录。
- `{skill-name}` 解析为技能目录的基本名称。

## 激活时

### 第 1 步：解决工作流阻塞

运行：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`

**如果脚本未找到**，则此处未设置 BMad。提供运行 `bmad` 技能的设置，如果尚未安装则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行该命令。

**如果因其他任何原因失败**，请自行通过按基本 → 团队 → 用户的顺序阅读这三个文件并应用与解析器相同的结构合并规则来解决 `workflow` 阻塞：

1. `{skill-root}/customize.toml` — 默认值
2. `{project-root}/_bmad/custom/{skill-name}.toml` — 团队覆盖
3. `{project-root}/_bmad/custom/{skill-name}.user.toml` — 个人覆盖

任何缺失的文件将被跳过。标量覆盖，表深度合并，键为 `code` 或 `id` 的表数组替换匹配条目并追加新条目，所有其他数组追加。

### 第 2 步：执行前置步骤

按顺序执行 `{workflow.activation_steps_prepend}` 中的每个条目，然后继续。

### 第 3 步：加载持久事实

将 `{workflow.persistent_facts}` 中的每个条目视为您在整个工作流运行中携带的基础上下文。以 `file:` 开头的条目是 `{project-root}` 下面的路径或通配符——加载引用的内容作为事实。所有其他条目都是原始事实。

### 第 4 步：加载配置

运行：`uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.output_folder --key core.active_initiative`

- 脚本未找到，或没有 `output_folder`：此处未设置 BMad。提供运行 `bmad` 技能的设置，如果尚未安装则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行该命令。
- 没有 `active_initiative`：交由 `bmad` 技能设置或创建一个，然后再次运行该命令并继续。

- `date` 作为系统生成的当前日期时间
- 您必须在您的 Agent 通信风格中始终使用输出
- 文档输出：一个具有清晰、可操作变更的 Sprint 变更提案。

### 第 5 步：问候用户

问候用户。

### 第 6 步：执行后置步骤

按顺序执行 `{workflow.activation_steps_append}` 中的每个条目。

激活完成。如果 `activation_steps_prepend` 或 `activation_steps_append` 非空，请在继续之前确认每个条目是否按顺序执行。在所有激活步骤完成之前，不要开始主工作流。

## 路径

- `default_output_file` = `{output_folder}/{active_initiative}/change-{slug}/change-{slug}.md`，`{slug}` 变更的标题，使用连字符命名法

## 输入文件

首先检查 `{output_folder}/{active_initiative}/`，然后检查 `{output_folder}/`。

| 输入 | 路径 | 加载策略 |
|------|------|----------|
| PRD | `prd-*/prd-*.md` | FULL_LOAD |
| 架构 | `architecture-*/architecture-*.md` | FULL_LOAD |
| UX 设计 | `ux-*/`：`DESIGN.md` 和 `EXPERIENCE.md` | FULL_LOAD |
| 规格 | `spec-*/spec-*.md` 及其列出的伴随文件 | FULL_LOAD |
| 项目上下文 | 受影响仓库中的 `AGENTS.md`（`bmad:context` 块） | FULL_LOAD |

## 执行

### 文档发现 - 加载项目工件

**策略：** 路线修正需要广泛的项目上下文来准确评估变更影响。加载所有可用的规划工件。

**FULL_LOAD 文档（PRD、架构、UX 设计、规格）的发现过程：**

1. **按类型查找每个文档** - 输入文件中列出的文件夹和主文件模式
2. **如果主文件是旁边列出的部分文件的索引**：
   - 读取索引中列出的所有部分文件
   - 将合并的内容作为单个文档处理

**项目上下文的发现过程：**

1. **读取 `AGENTS.md`** 在受变更影响的仓库中——`bmad:context` 标记之间的块包含路线修正必须遵循的策略、冻结路径和规范。
2. **仅跟随与受影响区域相关的指针**——嵌套组件文件或列在“事物所在何处”下的链接规则文件。不要加载所有文件。
3. **此文档是可选的**——如果仓库没有 `AGENTS.md`（绿色字段项目），则跳过。

**模糊匹配：** 对文档名称保持灵活——用户可能使用如 `prd.md`、`bmm-prd.md`、`product-requirements.md` 等变体。

**缺失文档：** 不一定所有文档都存在。PRD 或规格是必需的；如果可用，则加载架构、UX 设计和项目上下文。如果既找不到 PRD 也没有规格，则停止。

<workflow>

<step n="1" goal="初始化变更导航">
  <action>确认变更触发并收集用户对问题的描述</action>
  <action>询问：“已识别出需要导航的具体问题或变更是什么？”</action>
  <action>验证对项目文档的访问权限：</action>
    - PRD（产品需求文档）或规格 — 必需
    - 架构文档 — 可选，如果可用则加载
    - UI/UX 规格说明 — 可选，如果可用则加载
  <action>要求用户描述受变更影响的史诗和故事：每个涵盖的内容及其状态</action>
  <action>要求用户选择模式偏好：</action>
    - **增量**（推荐）：协作式细化每个编辑
    - **批量**：一次呈现所有变更以供审查
  <action>在工作流中存储模式选择</action>

<action if="变更触发不明确">HALT：“在没有明确理解触发变更的问题的情况下无法导航变更。请提供关于需要变更的内容及其原因的具体细节。”</action>

<action if="既没有 PRD 也没有规格可用">HALT：“需要访问 PRD 或规格来评估变更影响。请确保其中之一是可访问的。如果可用，将使用架构和 UI/UX。”</action>
</step>

<step n="2" goal="执行变更分析清单">
  <action>完全阅读并遵循来自 `checklist.md` 的系统分析</action>
  <action>与用户交互式地处理清单的每个部分</action>
  <action>记录每个清单项的状态：</action>
    - [x] 完成 — 项成功完成
    - [N/A] 跳过 — 项不适用于此变更
    - [!] 需要行动 — 项需要关注或后续处理
  <action>维护发现的发现和影响的运行记录</action>
  <action>在完成每个主要部分后向用户展示清单进度</action>

<action if="清单无法完成">识别阻塞问题，并与用户合作解决，然后继续</action>
</step>

<step n="3" goal="起草具体的变更提案">
<action>根据清单发现，为每个识别的工件创建明确的编辑提案</action>

<action>对于故事变更：</action>

- 显示旧版 → 新版文本格式
- 包括故事 ID 和被修改的部分
- 提供每个变更的理由
- 示例格式：

  ```
  故事：[STORY-123] 用户身份验证
  部分：验收标准

  旧版：
  - 用户可以使用电子邮件/密码登录

  新版：
  - 用户可以使用电子邮件/密码登录
  - 用户可以通过身份验证器应用程序启用 2FA

  理由：在实施过程中发现的安全要求
  ```

<action>对于 PRD 修改：</action>

- 指定要更新的确切部分
- 显示当前内容和建议的变更
- 解释对 MVP 范围和需求的影响

<action>对于架构变更：</action>

- 确定受影响的组件、模式或技术选择
- 描述需要更新的图表
- 注意对其他组件的任何涟漪效应

<action>对于 UI/UX 规格更新：</action>

- 引用特定的屏幕或组件
- 显示需要更改的线框图或流程
- 将变更与用户体验影响联系起来

<check if="模式是增量">
  <action>单独呈现每个编辑提案</action>
  <action>HALT 并给用户选择：
  - **批准** — 接受此提案
  - **编辑** — 细化此提案
  - **跳过** — 跳过此提案
  </action>
  <action>如果用户选择 **批准**，保留提案。如果他们选择 **编辑**，与他们一起细化。如果他们选择 **跳过**，则跳过。继续到下一个提案。</action>
</check>

<action if="模式是批量">收集所有编辑提案，并在步骤结束时一起呈现</action>

</step>

<step n="4" goal="生成 Sprint 变更提案">
<action>编译包含以下部分的全面 Sprint 变更提案文档：</action>

<action>第 1 部分：问题摘要</action>

- 描述触发变更的清晰问题陈述
- 关于何时/如何发现问题的上下文
- 证明或示例，说明问题

<action>第 2 部分：影响分析</action>

- 史诗影响：哪些史诗受影响及其影响程度
- 故事影响：当前和未来的需要变更的故事
- 工件冲突：需要更新的 PRD、架构、UI/UX 文档
- 技术影响：代码、基础设施或部署影响

<action>第 3 部分：推荐方法</action>

- 呈现清单评估中选择的路径：
  - 直接调整：在现有计划内修改/添加故事
  - 潜在回滚：还原已完成的工作以简化解决
  - MVP 审查：减少范围或修改目标
- 提供推荐的理由
- 包括工时估算、风险评估和时间段影响

<action>第 4 部分：详细变更提案</action>

- 包括来自第 3 步的所有细化编辑提案
- 按工件类型分组（故事、PRD、架构、UI/UX）
- 确保每个变更包括前后版本和理由

<action>第 5 部分：实施交接</action>

- 对变更范围进行分类：
  - 轻微：由 Developer agent 直接实施
  - 中等：需要待办事项重新组织（PO/DEV）
  - 重大：需要基本重新计划（PM/架构师）
- 列出史诗和故事变更（添加、删除、重新排序或重新范围），供用户使用 `bmad-ticket` 应用
- 指定交接接收者和他们的职责
- 定义实施成功标准

<action>向用户展示完整的 Sprint 变更提案</action>
<action>将 Sprint 变更提案文档写入 `{default_output_file}`</action>
<action>HALT 并给用户选择：
- **继续** — 进入批准
- **编辑** — 首先修订提案
</action>
<action>如果用户选择 **编辑**，与他们一起修订提案，并在继续之前写入更新后的文档。</action>
</step>

<step n="5" goal="最终确定并路由实施">
<action>获取用户对完整提案的明确批准</action>
<ask>您批准此 Sprint 变更提案实施吗？(是/否/修订)</ask>

<check if="否或修订">
  <action>收集需要调整的具体反馈</action>
  <action>返回适当的步骤以解决这些问题</action>
  <goto step="3">如果需要编辑提案的变更</goto>
  <goto step="4">如果需要整体提案结构的变更</goto>

</check>

<check if="用户批准了提案">
  <action>最终确定 Sprint 变更提案文档</action>
  <action>确定变更范围分类：</action>

- **轻微**：可由 Developer agent 直接实施
- **中等**：需要待办事项重新组织，并需要 PO/DEV 协调
- **重大**：需要与 PM/架构师的基本重新计划

<action>根据范围提供适当的交接：</action>

</check>

<check if="轻微范围">
  <action>路由到：Developer agent 进行直接实施</action>
  <action>交付物：最终编辑提案和实施任务</action>
</check>

<check if="中等范围">
  <action>路由到：产品负责人 / Developer agents</action>
  <action>交付物：Sprint 变更提案 + 待办事项重新组织计划</action>
</check>

<check if="重大范围">
  <action>路由到：产品经理 / 解决方案架构师</action>
  <action>交付物：完整的 Sprint 变更提案 + 升级通知</action>

<action>与用户确认交接完成和下一步</action>
<action>在工作流执行日志中记录交接</action>
</check>

</step>

<step n="6" goal="工作流完成">
<action>总结工作流执行：</action>
  - 处理的问题：{{change_trigger}}
  - 变更范围：{{scope_classification}}
  - 修改的工件：{{list_of_artifacts}}
  - 路由到：{{handoff_recipients}}

<action>确认产生的所有交付物：</action>

- Sprint 变更提案文档
- 具有前后版本的特定编辑提案
- 实施交接计划

<action>向用户报告工作流完成：“Correct Course 工作流完成！”</action>
<action>提醒用户 Developer agent 的成功标准和下一步</action>
<action>运行：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow.on_complete` — 如果解析的值非空，则将其作为退出前的最终终端指令遵循。</action>
</step>

</workflow>
