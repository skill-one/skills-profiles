---
name: srdf
description: MoveIt2 SRDF 的创建、验证和规划语义工作流程。在创建、编辑、检查或验证 `.srdf` 文件、MoveIt 规划组、虚拟关节、被动关节、末端执行器、组状态、禁用碰撞、URDF 配对的规划语义或用于实时预览的 SRDF 交接时使用。使用 URDF 技能处理机器人结构，使用 SDF 技能处理模拟器描述，使用 cad-viewer 技能进行渲染和实时预览链接。
---

# SRDF

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad)。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源和发布审查。

使用此技能在现有的有效 URDF 之上创建 MoveIt 语义机器人描述。SRDF 定义规划语义；它不定义物理机器人结构。`.srdf` 文件是真实来源：直接编写和编辑 XML。没有 `gen_srdf()` 合约。

SRDF 正确性是一个 **规划语义** 问题。常见错误不是无效的 XML；它是一个合理的 SRDF，但向 MoveIt 提供了错误的规划组、错误的工具链接、错误的默认状态、不安全的禁用碰撞矩阵或错误的关节单位。由于语言模型在空间和运动学推理方面较弱，从 URDF 拓扑、MoveIt Setup Assistant 输出、采样碰撞分析或显式用户数据中推导出规划组、末端执行器、组状态和禁用碰撞。不要仅从视觉主题中推断它们——并且不要从记忆中输入任何链接或关节名称：首先提取 URDF 的链接/关节表，然后从表中复制名称。

## 设置

此技能的命令是 `cadgen` 发行版的薄入口点，它包含 Python 构建运行时和它执行的 JavaScript。安装一次：

```bash
python -m pip install -r requirements.txt
```

渲染还需要一个浏览器，而 pip 无法提供：

```bash
python -m playwright install chromium
```

## 格式边界

- **URDF** 拥有物理机器人结构：链接、关节、几何形状、惯性、限制、模拟关节、传输和机器人状态发布。
- **SRDF** 拥有 MoveIt 语义：虚拟关节、被动关节、规划组、组状态、末端执行器和禁用碰撞对。
- **SDF** 拥有模拟器/世界语义：物理、传感器、灯光、插件、世界和特定于模拟的元数据。

不要在 SRDF 中放置几何形状、惯性、关节原点、链接姿态、网格引用、物理关节限制、传输或 `ros2_control` 接口。

## CAD 查看器交接

完成创建或修改 `.srdf` 的 SRDF 工作后，当该技能安装时，你必须始终将显式文件路径传递给 `$cad-viewer`。如果 `$cad-viewer` 没有运行，它必须启动 CAD 查看器并返回相关创建或更新文件的链接。如果 `$cad-viewer` 不可用或启动失败，请报告该问题，而不是静默地省略交接。

## 必需的工作流程

1. **从有效的 URDF 开始。** 首先使用 `$urdf` 编写或修复 URDF，并验证它。SRDF 通过位置和机器人名称与该 URDF 配对，SRDF 中的每个名称都必须存在于其中。
2. **提取 URDF 表。** 在编写任何 SRDF XML 之前，列出 URDF 的机器人名称、链接、关节（类型、父级、子级、限制、模拟标志）。仅从此表中复制名称；不要从记忆中输入它们。参见 `references/srdf-workflow.md`。
3. **识别规划任务。** 记录目标是否为手臂 IK、夹爪控制、移动底座规划、双臂规划、工具使用或本地烟雾测试。
4. **创建或更新规划账本。** 在编写 XML 之前使用 `references/planning-ledger.md`；将紧凑的副本作为注释块保存在 `.srdf` 中。
5. **通过位置配对 URDF。** 将 `.srdf` 保存在与其 `.urdf` 相同的文件夹中，并使用相同的 `<robot name>`——这是唯一的配对机制。验证器和查看器都通过扫描文件夹来解析配对（查找机器人名称匹配的 `.urdf`）；每个机器人名称在每个文件夹中最多一个。没有元数据元素链接文件。参见 `references/authoring-contract.md`。
6. **有意定义虚拟和被动关节。** 当机器人模型需要时使用它们。
7. **从 URDF 拓扑定义规划组。** 对于串联机械臂，当基座/尖端在 URDF 树中形成真实的父子路径时（验证器会验证这一点），优先使用链组。仅在它们是故意的时才使用关节/链接/子组定义。
8. **在组成员资格确定后定义末端执行器。** 避免末端执行器组与其父组重叠。记录实际目标/TCP 链接。
9. **使用 URDF 本地单位定义组状态。** 旋转和连续值为弧度；平移值为米。不要在 SRDF 中存储度数。值必须在 URDF 限制范围内，并且不能设置固定或模拟关节。
10. **从证据生成禁用碰撞。** 使用从 URDF 关节表中派生的邻接性、MoveIt Setup Assistant 采样或用户提供的碰撞矩阵。不要编造广泛的禁用列表。参见 `references/disabled-collisions.md`。
11. **使用 `cadgen srdf validate` 验证每个创建或修改的 `.srdf`**；它将所有名称、链、状态和配对与配对的 URDF 进行交叉验证。修复发现的问题并重新验证，直到干净。
12. **在可用时运行 MoveIt 烟雾测试。** 使用 MoveIt Setup Assistant 或直接使用项目 MoveIt 启动。
13. **报告假设和跳过的检查。** 包括不完整的验证、缺少 MoveIt 环境、手动推理的碰撞禁用和推断的目标链接。

## 命令

从此技能的 `requirements.txt` 安装的 Python 环境运行 `cadgen`（`python -m cadgen.cli <verb>` 使用该解释器是路径无关的等效方式）。`cadgen doctor <skill-dir>` 验证安装的 cadgen 是否与此技能的固定版本匹配——在安装不匹配的情况下，文档会静默地漂移。验证本身不需要超出 Python 标准库；只有快照需要浏览器。使用 `cadgen <verb> --help` 获取完整的当前界面。

验证器形状是：

```bash
cadgen srdf validate path/to/robot.srdf
cadgen srdf validate path/to/robot.srdf --strict
cadgen srdf validate path/to/robot.srdf --json
```

验证器解析 SRDF，解析配对的 URDF（与 `.urdf` 相同的文件夹，其机器人名称匹配；无、多个或无效的之一是错误），并进行交叉验证：组/关节/链接/子组名称存在性、链路径可解析性、子组循环、虚拟/被动关节、末端执行器拓扑、组状态成员资格/限制/完整性、禁用碰撞对（包括 Adjacent-reason 真实性）和拼写错误元素。每个阶段在一次遍历中收集其所有发现（严重性、代码、XML 路径），但结构错误会停止交叉文件阶段——在每次修复后重新运行。一次运行验证一个文件：`--strict` 将警告视为失败，`--json` 打印一行 `{"ok", "path", "issues": [{"severity", "code", "message", "element", "hint"}], "summary"}`，其中 `element` 是 XML 路径。如果目标失败，它将退出非零。相对目标从当前工作目录解析。

## 硬规则

- SRDF 与其 URDF 位于同一文件夹中，并共享其 `<robot name>`；这个位置加名称匹配是唯一的配对机制，文件夹中每个机器人名称最多只能存在一个 URDF。
- 每个链接、关节、组和子组名称必须来自 URDF 表或在同一文件中定义的组。
- 组状态使用 URDF 本地单位：旋转/连续值为弧度，平移值为米。
- 禁用碰撞对需要真实的理由和来源。
- 末端执行器组不应与其父规划组共享链接。
- 视觉渲染审查有用，但不能证明规划正确性。

## 快照工具

`cadgen snapshot` 将机器人渲染为 PNG 静态图像，使用每个渲染技能使用的相同共享 CLI 和无头浏览器运行时——因此快照与 CAD 查看器显示的内容匹配。

```bash
cadgen snapshot path/to/robot.srdf review.png
```

传递 `.srdf`；它通过后缀路由并渲染配对 URDF 的几何形状——与 `<robot name>` 匹配的相同文件夹的 `.urdf`，与 `cadgen srdf validate` 配对它们的方式完全相同。没有匹配项，或多个匹配项，在渲染之前会被拒绝，并命名它查找的机器人名称和找到的 `.urdf` 文件。使用 `--joint-values` 设置机器人姿态——`{joint: degrees}` JSON，未命名的关节保持在 CAD 查看器打开机器人时的位置：每个关节在其默认位置，然后如果此 SRDF 声明了一个 `home` 组状态（`"jointValues"` 任务字段与数据包中的相同），则使用该组状态。快照使用查看器自己的场景绘制机器人，因此它显示查看器显示的内容，并且无法加载的链接网格会失败，而不是省略链接。机器人以米为单位编写，并自动在机器人场景比例框架中。

正常快照使用 Solid 预设和 Light 外观；省略的组继承预设默认值。
传递 `--display render` 以使用共享的摄影场景。内联显示 JSON 和 JSON 文件使用分组设置，如 `lighting`、`background` 和 `floor`；`appearance` 是 `light`（默认）或 `dark`。投影和焦距属于 `display.camera`。顶层 `--camera` 和 `--joint-values` 在每种显示模式下都保持激活状态。显示模式是 `solid` 和 `render`：`edges`、`clip`、`exploded`、`xray`、`hidden-line` 和 `wireframe` 模式以及 `hidden`/`off` 表面样式描述 STEP 模型的 CAD 边缘、部件和实体，并且在此处通过名称拒绝。

链接网格相对于描述解析，因此它们必须存在：未解压的 Git LFS 指针会失败为 "No link mesh loaded for robot"。首先运行 `git lfs checkout <mesh dir>`。

SRDF 的几何形状来自其配对的 URDF，因此它没有自己的快照门；多态的 `cadgen snapshot` 通过后缀路由。语法是 `cadgen snapshot TARGET [OUT] [flags]`，每个格式门都使用相同的语法。使用 `cadgen snapshot --help` 获取完整的当前界面。

## 参考

- 作者合约（结构、URDF 配对、黄金骨架）：`references/authoring-contract.md`
- SRDF 工作流（URDF 表提取、编辑循环）：`references/srdf-workflow.md`
- 规划账本：`references/planning-ledger.md`
- 验证和确认配方：`references/validation.md`
- 末端执行器：`references/end-effectors.md`
- 禁用碰撞：`references/disabled-collisions.md`
