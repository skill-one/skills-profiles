---
name: sdf
description: SDFormat/SDF模型和世界创建、验证以及仿真器交接。用于`.sdf`文件、SDFormat XML、模型、世界、链接、关节、姿态、框架、惯性、视觉/碰撞几何、网格URI、传感器、灯光、物理、插件、包含、Gazebo、静态SDF审查或特定仿真器的元数据。不应用于有符号距离场几何。
---

# SDF

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 中。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源追溯和发布审核。

在交付成果是 SDFormat 文档时使用此技能。SDFormat 描述了模拟器和世界的行为：模型、世界、框架、姿态、链接、关节、惯性、视觉、碰撞、传感器、灯光、物理、插件、包含以及模拟器元数据。

此技能用于 **SDFormat**，而不是有符号距离场几何。

`.sdf` 文件是真实来源：直接编写和编辑 XML。没有 `gen_sdf()` 合约。

## 设置

此技能的命令是 `cadgen` 发行版的薄入口点，它包含 Python 构建运行时和它执行的 JavaScript。安装一次：

```bash
python -m pip install -r requirements.txt
```

渲染还需要一个浏览器，而 pip 无法提供：

```bash
python -m playwright install chromium
```

## 核心规则

1. 直接编写 `.sdf` XML，并在报告完成之前使用 `cadgen sdf validate` 验证每个创建或修改的文件。
2. 编辑前确定目标消费者：Gazebo/libsdformat 版本、其他模拟器、仅可视化工具、模型包或世界交接。
3. 确定文档类型：模型级 SDF、世界级 SDF 或模型级世界。对于可重用的机器人/对象导出，优先使用模型级 SDF。
4. 除非目标明确要求否则使用 SI 单位：米、千克、秒、弧度。
5. 新输出优先使用 `version="1.12"`，除非目标消费者限制了版本。
6. 在编写姿态、框架、关节轴、网格比例、惯性、传感器或插件之前建立设计账本，并将其作为 `.sdf` 顶部的注释块保留。使用 `references/design-ledger.md` 和 `references/llm-guardrails.md`。
7. 在每个非平凡的姿态和轴上明确编写 `relative_to` / `expressed_in`。隐式框架默认值是 SDF 的主要失败模式。参见 `references/frame-semantics.md`。
8. 不要仅凭视觉印象推断空间变换。从上游源数据、绘图、模拟器文档、测量值或明确假设中导出姿态、轴、比例、质量、惯性和框架名称。不要手绘计算数字——使用公式或一次性辅助脚本（惯性张量、单位转换）。
9. 如果机器人已经有一个 URDF，则从它派生 SDF 而不是重新编写几何；参见 `references/interoperability.md`。
10. 在编辑引用它们的 SDF 之前，使用它们各自的工作流重新生成上游几何、网格、机器人描述、渲染、拓扑或包资产。
11. 编写完成后，运行可用检查：捆绑验证（它会在 `gz` 在 PATH 上时运行 `gz sdf --check` 本身）、模拟器加载、关节运动以及插件/传感器启动。
12. 报告假设、跳过的检查、未解决的资源路径和目标特定的兼容性风险。

## 范围

用于 SDFormat 输出。不要用于有符号距离场建模、原始几何生成、规划语义或掩盖不正确的上游机器人/源数据，除非任务是仅模拟器。

## CAD 查看器交接

在完成创建或修改 `.sdf` 的 SDF 工作后，你必须始终将显式文件路径传递给 `$cad-viewer`（如果该技能已安装）。`$cad-viewer` 必须在它未运行时启动 CAD 查看器并返回相关创建或更新文件的链接；如果 `$cad-viewer` 不可用或启动失败，则报告该问题而不是静默地省略交接。

## 工作流

1. 定位目标 `.sdf` 及其消费者。
2. 读取或创建设计账本注释块。
3. 编辑任何 `<pose>`、`<frame>`、关节轴、`relative_to`、`expressed_in`、嵌套范围、传感器框架或插件框架之前，阅读 `references/frame-semantics.md`。
4. 直接编写 XML，并遵循 `references/examples.md` 中的示例。
5. 使用 `cadgen sdf validate` 验证显式目标；将捆绑验证视为护栏，而不是模拟器证明。
6. 当可用时运行目标消费者冒烟测试（`references/smoke-tests.md`）。
7. 将文件交给 `$cad-viewer`。静态渲染不会执行 SDF 插件或读取文件编写的运动元数据。
8. 报告运行的检查、跳过的检查和假设。

## 命令

从此技能的 `requirements.txt` 安装的 Python 环境中运行 `cadgen`（`python -m cadgen.cli <verb>` 使用该解释器是 PATH 无关的等效方式）。`cadgen doctor <skill-dir>` 验证安装的 cadgen 是否与此技能的固定版本匹配——在版本不匹配的安装中，文档会静默地漂移。验证本身不需要超出 Python 标准库；只有快照需要浏览器。使用 `cadgen <verb> --help` 获取完整的当前界面。

```bash
cadgen sdf validate path/to/model.sdf
cadgen sdf validate path/to/model.sdf --strict
cadgen sdf validate path/to/model.sdf --json
cadgen sdf snapshot path/to/model.sdf review.png
```

验证器检查文档形状、名称作用域、姿态/框架图、关节、几何、网格 URI、惯性、传感器和插件，并打印其发现以及摘要。一次运行验证一个文件：`--strict` 将警告视为失败，`--json` 打印一行 `{"ok", "path", "issues": [{"severity", "code", "message", "element", "hint"}], "summary"}`，其中 `element` 是 XML 路径。如果目标失败，它将退出非零。

默认情况下，外部检查是开启的：

```bash
cadgen sdf validate path/to/model.sdf --gz-check required
cadgen sdf validate path/to/model.sdf --gz-check never
```

`gz sdf --check` 是目标消费者验证。`--gz-check auto` 是默认值：当 `gz` 在 PATH 上时运行，报告 `gz_check_passed` 或工具的输出作为错误 `gz_check_failed`，否则注明 `info: gz_check_unavailable` 并继续。缺失的可选工具不会对文件产生影响，因此它永远不会使干净的文档失败，`--strict` 也不会改变这一点。`--gz-check required` 使该工具成为必需的——然后缺失的 `gz` 是一个错误——而 `--gz-check never` 直接跳过它。

## 必须报告的形状

完成 SDF 任务时，包括紧凑的报告：

```text
Validated: path/to/model.sdf
Checks run:
- bundled SDF validation: passed
- gz sdf --check: skipped, gz not installed
- simulator load: skipped, target simulator unavailable
- viewer handoff: `$cad-viewer` link returned
Assumptions:
- Assumed mesh units are meters.
- Assumed lidar frame is coincident with lidar_link.
Risks:
- Camera plugin filename was not verified in the target simulator environment.
```

## 快照工具

`cadgen sdf snapshot` 将机器人渲染为 PNG 静态图像，使用每个渲染技能使用的相同共享 CLI 和无头浏览器运行时——因此快照与 CAD 查看器显示的内容匹配。

```bash
cadgen sdf snapshot path/to/robot.sdf review.png
```

它只接受 `.sdf`（格式门，与 `TARGET [OUT]` 语法相同）。使用 `--joint-values` 设置机器人姿态——`{joint: degrees}` JSON，未命名的关节保持其默认值，其中 CAD 查看器打开机器人（`"jointValues"` 任务字段与数据包中的相同）。快照使用查看器自己的场景绘制机器人，因此它显示查看器显示的内容，并且无法加载的链接网格会失败而不是省略链接。机器人以米为单位编写，并自动在机器人场景比例上框架化。

正常快照使用 Solid 预设和 Light 外观；省略的组继承预设默认值。
传递 `--display render` 以使用共享的摄影场景。内联显示 JSON 和 JSON 文件使用分组设置，如 `lighting`、`background` 和 `floor`；`appearance` 是 `light`（默认）或 `dark`。投影和焦距属于 `display.camera`。顶级 `--camera` 和 `--joint-values` 在每种显示模式下都保持激活状态。显示模式是 `solid` 和 `render`：`edges`、`clip`、`exploded`、`xray`、`hidden-line` 和 `wireframe` 模式以及 `hidden`/`off` 表面样式描述 STEP 模型的 CAD 边缘、部件和实体，并且在此处按名称拒绝。

链接网格相对于描述解析，因此它们必须存在：未解压的 Git LFS 指针会失败为 "No link mesh loaded for robot"。首先运行 `git lfs checkout <mesh dir>`。

语法是 `cadgen sdf snapshot TARGET [OUT] [flags]`，每个格式门都使用相同的语法。使用 `cadgen sdf snapshot --help` 获取完整的当前界面——机器人无法操作的标志不会包含在其中，而不是被拒绝。

## 参考文献

- SDF 工作流：`references/sdf-workflow.md`
- 示例（黄金骨架）：`references/examples.md`
- LLM 护栏：`references/llm-guardrails.md`
- 设计账本：`references/design-ledger.md`
- 框架语义：`references/frame-semantics.md`
- 验证范围：`references/validation.md`
- 冒烟测试：`references/smoke-tests.md`
- 互操作性笔记（从 URDF 派生的 SDF、网格、Gazebo）：`references/interoperability.md`
