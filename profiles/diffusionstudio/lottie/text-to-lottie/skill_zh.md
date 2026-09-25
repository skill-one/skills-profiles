# 文本转Lottie

为官方本地Skia Skottie播放器生成生产就绪的Lottie JSON。
交付成果是播放器中的可渲染场景，而不是独立的JSON。

## 运作模式

- 使用官方播放器项目并在Skia Skottie中验证。不要手动创建自定义查看器或切换渲染器进行验证。
- 保持技能在Agent Skills客户端中的可移植性。在技能说明中避免使用特定于主机的命令、命令模式或编排约定。
- 优先考虑更少的问题和更强的默认值。仅在决策实质性改变输出时提问，例如透明背景与全帧背景、品牌约束、目标格式或提供的源资产。
- 优先考虑干净、有意为之、专业的动画，而不是仅仅满足字面提示。

## 参考加载

此`SKILL.md`是薄控制平面。仅加载与任务匹配的一级参考。不要打开整个参考库。

在创建、编辑、修复或验证场景之前，始终阅读`references/player-contract.md`。如果路由参考不可用，请继续使用此文件中的内联规则。

| 用户意图 | 当存在时读取的参考 |
| --- | --- |
| 任何新的/编辑/修复Lottie场景 | `references/player-contract.md` |
| JSON结构、关键帧、插槽、形状、资产 | `references/lottie-spec-map.md` |
| Logo动画 | `references/recipe-logo.md`、`references/motion-taste.md`、`references/design-taste.md` |
| 字体、标题、引用、文本显示 | `references/recipe-typography.md`、`references/design-taste.md`、`references/motion-taste.md` |
| 下标、姓名标签、标题栏、覆盖层 | `references/recipe-lower-thirds.md`、`references/design-taste.md`、`references/motion-taste.md` |
| 加载器、图标、旋转器、徽章动画 | `references/recipe-loaders-icons.md`、`references/motion-taste.md` |
| 成功、错误、警告、完成、空状态 | `references/recipe-loaders-icons.md`、`references/design-taste.md`、`references/motion-taste.md` |
| UI微交互 | `references/recipe-ui-microinteractions.md`、`references/design-taste.md`、`references/motion-taste.md` |
| 通用的“动画这个SVG”或SVG到Lottie | `references/recipe-svg-animation.md`、`references/svg-compatibility.md`、`references/motion-taste.md` |
| 摄像机跟随、平移、缩放、视差、场景动画 | `references/recipe-camera-scene-motion.md`、`references/design-taste.md`、`references/motion-taste.md` |
| 图表、技术线动画、标注、流程跟踪 | `references/recipe-diagram-technical.md`、`references/design-taste.md`、`references/motion-taste.md` |
| 数据、统计数据、KPI、图表、指标、仪表板图形 | `references/recipe-data-stats.md`、`references/design-taste.md`、`references/motion-taste.md` |
| 产品发布、功能公告、社交推广 | `references/recipe-product-promo.md`、`references/design-taste.md`、`references/motion-taste.md` |
| 长文本、多个想法、列表/功能/步骤、时间线、前后、问题/解决方案、引用+证明、回顾/故事、产品演示、多语言变体、章节、多节序列、集数、跳转/硬切、过渡语法 | `references/chapterization-transition-grammar.md`、`references/motion-taste.md` |
| 发光、玻璃、金属、渐变、填充、气泡/爆炸效果 | `references/recipe-visual-effects.md`、`references/design-taste.md`、`references/motion-taste.md` |
| Logo/图标/UI/下标工作中的SVG输入 | 任务配方加上`references/svg-compatibility.md` |
| 启动简报或可重用项目方向 | `references/recipe-starter-projects.md`、`references/design-taste.md`、`references/motion-taste.md` |
| 任何“高级”、“干净”、“极简”、“现代”、“流畅”或“精致”限定符 | `references/design-taste.md`（约束默认值），加上路由配方 |

对于混合提示，从主要交付成果中选择一个主要配方，然后添加用于源格式或视觉处理的次要参考。示例：带发光的SVG标志使用标志作为主要参考加上SVG兼容性和视觉效果；带平移/缩放的产品发布使用产品推广加上摄像机场景动画；技术SVG图表跟踪使用图表/技术加上SVG兼容性；带玻璃扫掠的动态标题使用字体加上视觉效果。

## 工作流程

1. 使用上表路由任务。仅读取存在的相关参考。
2. 定位官方播放器项目并使用以下目标优先级解析目标场景。在编辑之前，验证解析的路径是`public/projects/<project>/<scene-N>/lottie.json`；在覆盖之前立即重新读取当前文件，因为UI可以将插槽编辑写回源。
3. 在创作之前决定背景策略。
4. 编写或更新`public/projects/<project>/<scene-N>/lottie.json`，并在有用时编写`controls.json`。
5. 验证JSON，运行或重用开发服务器，使用`?frame=N`检查确切帧，并在完成之前修复渲染/设计/动画问题。

## 内联规则

### 设计默认值（始终适用）

这些少数默认值是不可协商的，并适用于每个设计的场景。加载`references/design-taste.md`以了解完整原因，特别是对于任何“高级”、“干净”、“极简”、“现代”或“卡片”提示。

- 高级意味着减法，而不是加法。当提示说高级、干净、极简、现代、流畅或精致时，默认值为克制：在添加之前移除铬。高级由比例、重量、亮度、间距和时机承载，永远不会由卡片、边框、分隔符、阴影、发光或堆叠色调承载。
- 铬/容器预算默认为`0`。除非空白和排列无法完成工作，否则不要添加框架卡片、容器、边框或分隔符。首先用负空间和排列分隔网格和列，其次用单根头发线，最后用填充或带边框的卡片，并且仅在明确说明的情况下使用。
- 一个表面色调。使用一个背景色调。不要堆叠两个近黑色或两个近白色的色调来假装一个“表面”；它看起来模糊。如果卡片表面必须与背景不同，使其有一个明确的步骤和明确的目的。
- 一个分隔符处理，一个颜色。如果确实需要分隔符，对所有分隔符使用一个重量和一个颜色，包括标题规则和列规则。永远不要为每个分隔符使用稍微不同的颜色或重量。

### 场景规则

- 场景文件位于`public/projects/<project>/<scene-N>/lottie.json`。
- 通过权威解析目标场景：显式的文件路径获胜；浏览器URL路由如`/<project>/<scene>`其次获胜；对于任务的已知项目/场景再次获胜；否则创建一个新的安全场景。仅用于发现、验证或播放状态使用`/__context`，除非任务明确说明要编辑当前屏幕上的内容且没有更具体的目标。不要让`/__context.live`覆盖已知的文件路径、URL或项目/场景。仅在`main-project/scene-1`仍然是未触摸的占位符时才覆盖它；否则创建一个新场景。
- 全帧独立组合应包括一个带有`bgColor`插槽和`controls.json`条目的可见背景层。
- 默认透明的输出包括标志、图标、加载器、覆盖层、下标和SVG派生资产，除非用户要求背景。
- 包括顶层`v`、`fr`、`ip`、`op`、`w`、`h`、`nm`、`assets`和`layers`。将`op`视为排他性。
- 使用有目的的缓动和舞台。避免默认为线性运动。从`motion-taste.md`中的基于行为锚点（由运动行为、焦点元素最强）导出缓动；不要对所有层都回退到一个统一的缓动。
- 使用插槽用于重要的可编辑值，并在它们改进属性面板时添加`controls.json`标签/范围。
- 对于SVG输入，保留viewBox，规范化样式，注意填充规则和交集，并在Skottie中验证结果。
- 原生Lottie文本/文本插槽（`ty:5`）在场景将其字体发送时在此播放器中渲染：将`.ttf`/`.otf`/`.ttc`放在`lottie.json`旁边，在`fonts.list`中声明它，`fFamily`与字体的嵌入家族名称匹配，并从文本文档中引用它。加载器将每个场景字体传递给Skottie。优先使用原生文本；仅用于故意路径效果（描边上、字形变形、手写）时才使用矢量/形状文本。查看播放器合同中的“原生文本”参考。

## 验证

在完成之前：

1. 确认预期的目标文件路径是`public/projects/<project>/<scene-N>/lottie.json`。
2. 验证JSON：

   ```bash
   node -e "JSON.parse(require('fs').readFileSync('public/projects/<project>/<scene-N>/lottie.json','utf8'))"
   ```

3. 确认官方播放器正在运行，并且场景出现在`GET /__context`中。
4. 在浏览器中检查固定帧。对于新场景，检查帧`0`、中点和`op - 1`。
5. 确认背景策略与用例匹配。
6. 检查空白画布、缺失资产、未样式化的形状、错误的层顺序、不良缓动、尴尬的时机、裁剪内容、文本溢出和可见的SVG伪影。
7. 仅在动画干净且感觉有意为之时才完成。

## 维护评估

在正常动画工作时不要读取评估文件。仅在测试或更改此技能时使用它们：

- `evals/trigger-prompts.json`
- `evals/routing-prompts.json`
- `evals/reference-loading-prompts.json`
- `evals/output-rubric.md`
