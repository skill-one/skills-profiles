# 烟花技术图

一个便携式代理技能，适用于 Codex 和 Claude 代码。SVG 是规范化的工件；PNG、离线 HTML 和支持的 GIF 动画是输出路径。保留请求的标签、拓扑和含义；成功的命令不是视觉质量评判。

## 定位和选择

将包含此文件的目录解析为 `SKILL_ROOT`。在 Claude 代码中使用 `${CLAUDE_SKILL_DIR}`，或在 Codex 加载的技能元数据中使用绝对目录。不要假设当前工作目录或先前 shell 变量仍然存在。

使用适用于任务的安装版本。运行 `version` 以回答源/版本问题，并在诊断缺少渲染器、字体或依赖项时运行 `doctor`；不要将安装、更新或完整的测试套件作为每个图表的先决条件。

```bash
SKILL_ROOT="${CLAUDE_SKILL_DIR:-/absolute/path/from-codex-skill-metadata}"
python3 "$SKILL_ROOT/scripts/fireworks.py" version
```

- 尊重用户的图表类型、内容和风格；从摘要中选择合理的可逆细节。仅请求缺失的工程事实或用户明确保留的选择。绘图请求包括本地渲染。
- 风格 1–7 和 9–12 具有 JSON 生成器。风格 8（暗黑奢华）仍然是 AI 编写的 SVG：使用其风格参考，然后使用相同的验证/导出门。
- 默认使用风格 1 平面图标，当没有用户/工作区偏好时。从 [风格矩阵](references/style-diagram-matrix.md) 加载实际匹配的文件。仅当请求比较时才读取其他风格。
- 风格 9–12 默认使用 C4、云、事件和可观察性语义契约。在布局之前验证事实；不要编造职责、协议或指标。
- 在适当的情况下直接适应现有的有效 SVG。并非每次编辑都需要 JSON 生成。仅使用 [图表/布局指南](references/diagram-layout-reference.md) 和 [图标](references/icons.md) 以适用于相关类型或符号。

## 生成和检查

重用用户的当前摘要和工件；额外的规划文档是可选的。对于 JSON 工作，当所有标签必须完全可见时，选择 `text_policy: "strict"`。兼容的 `report` 默认保留 SVG 元数据中的完整标签并报告任何可见截断。在声称完整精确文本之前解决该警告。对于精细工作，应用 [组合契约](references/composition-quality-contract.md)。

```bash
SKILL_ROOT="${CLAUDE_SKILL_DIR:-/absolute/path/from-codex-skill-metadata}"
python3 "$SKILL_ROOT/scripts/fireworks.py" validate architecture input.json
python3 "$SKILL_ROOT/scripts/fireworks.py" render architecture input.json diagram.svg --report layout.json
python3 "$SKILL_ROOT/scripts/fireworks.py" check diagram.svg
python3 "$SKILL_ROOT/scripts/fireworks.py" export-png diagram.svg diagram.png --width 1920
```

`check` 验证 SVG 身份、标记引用、通用冲突、语义几何和组合。检查报告的字体和调色板范围；启发式文本宽度不能替代检查实际渲染的字体。使用 [视觉质量指南](references/visual-quality.md) 以提高可读性和特定风格的改进。每个业务边缘保留一个语义连接器。

## 额外输出

- **PNG：** 优先使用 `export-png`，它读取根画布尺寸、限制输出大小、原子写入并读取 PNG 尺寸。备用渲染器细节在 [PNG 导出](references/png-export.md) 中。
- **HTML：** `fireworks.py export-html diagram.svg diagram.html`。一个经过清理的离线文件提供平移/缩放、源复制和静态图像下载。
- **GIF：** “生成 GIF”、“动画化这个图表”、“生成 GIF”、“制作 GIF” 和 “让这张图动起来” 选择现有语义 SVG 的动画路径。文档化的场景契约启用了风格 1–12；不保证任意同风格拓扑。加载 [动画效果](references/motion-effects.md) 并运行 `fireworks.py animate diagram.svg diagram.gif`。默认为 960px、20fps、5.75s，使用 `+2s-settled-flow` 预设和 `.motion.json` 报告。历史 `user-approved` 字段描述维护人员审查的预设，而不是当前用户发布、花费或发送数据的授权。

## 验证请求的结果

在图像查看可用时，检查最终 PNG 在预期阅读尺寸下的文本完整性、对比度、字体替换、层次结构、间距、裁剪、箭头方向、交叉和标签。在修复缺陷的同时保留风格调色板和材料。重用未更改的已审查渲染；在验收通过后不要继续添加测试或精细。如果查看不可用，明确标记视觉检查跳过，不要声称视觉正确。

在检查失败后，使用其元素 ID 和几何形状进行集中修复；在两次未更改的失败后更改方法。拓宽/分割过满的图表，而不是隐藏必需的副本或无限缩小字体。不要在获得通过的情况下无声地削弱语义或组合约束。

完成所有请求的本地输出及其适用检查，然后报告文件路径、尺寸、视觉审查和剩余限制。第一个 SVG 并不完成请求的 PNG/GIF/HTML 包。发布或远程交付需要其自己的范围匹配授权；不会再次请求现有授权。
