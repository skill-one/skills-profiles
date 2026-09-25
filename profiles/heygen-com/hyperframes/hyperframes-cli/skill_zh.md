# HyperFrames CLI

除非项目说明提供了包装器，否则使用 `npx hyperframes ...` 运行命令。如果存在包装器，则遵循包装器。CLI 需要 Node.js 22 或更高版本以及 FFmpeg。

## 开发循环

1. **搭建框架：** `npx hyperframes init <项目>`（居中空白）。或者捕获一个网站。仅当从命名示例开始时，才传递 `--example=<名称>`。
2. **寻找移动：** 在手动编写运动之前，搜索已经完成该运动的原始操作：`npx hyperframes catalog --query "逐行显示一个标题"`。询问你想要的效果，而不是你脑海中想到的机制。使用 `npx hyperframes add <名称>`（参见 `/hyperframes-registry`）进行安装。只有在没有任何匹配的情况下，才手动编写。
3. **编写：** 使用 `/hyperframes-core` 编写组合。要知道项目时间轴上的内容（轨道、片段、开始、结束、播放内容），请运行 `npx hyperframes timeline --json` 而不是阅读 `index.html` 和每个子组合文件：嵌套行包含绝对主时间轴 `absStart`/`absEnd` 和它们所属的 `file`，而不仅仅是它们在子组合中的本地时间。优先选择 `--json` 而不是文本形式；它为相同或更好的正确性使用的 token 更少。有关用单行回答常见问题的参考，请参阅 `references/upgrade-info-misc.md`。
4. **在编辑时快速获取反馈：** 在第一次 HTML 通过后和结构更改后运行 `npx hyperframes lint`。
5. **运行最终关卡：** 运行 `npx hyperframes check`；它在打开浏览器之前会重新运行 lint。不要添加冗余的独立 lint 调用。添加 `--snapshots` 以获取带注释的概览帧并找到裁剪。
6. **检查子组合：** 当 `index.html` 加载 `data-composition-src` 时，捕获中点快照并检查每个挂载的场景。
7. **打开最终 Studio 预览：** 运行 `npx hyperframes preview --background`，验证 URL 返回 HTTP 200，将时间轴项目 URL 交给用户，并询问是否要修改或渲染。直到评审结束前保持它处于活动状态。
8. **仅在批准后渲染：** 在迭代时使用 `--quality draft`，第一次真实编码（CLI 默认）使用 `--quality looks`，最终交付使用 `--quality delivery`。
9. **验证输出：** 确认文件存在且非空。阅读渲染摘要的第二行（`beginframe` 与 `screenshot`，GPU，阶段时间）。Linux 上的 `screenshot` + `software gpu` 是慢路径。`ffprobe -v error -show_format -show_streams` 并比较持续时间（如果简要设置，则比较帧率）与根 `data-duration`。

## 强制创作者编辑交叉引用

- 在编写或诊断缩放、切入/切出、重新构图、摄像机移动或任何关键帧运动之前，请先阅读 `/hyperframes-keyframes`。
- 在 `hyperframes keyframes` 之前，请阅读 `/hyperframes-keyframes`；该命令显示动画轨迹，但不诊断片段剪切。
- 对于剪切、修剪、拼接、重新排序或源时间编辑，请阅读 `/hyperframes-core` 并使用其片段/时间轴合同。
- 对于淡入/淡出、交叉淡入、轨道增益、音量自动化、压低、旁白切割或放置音频上的 FX，请阅读 `/hyperframes-audio`。当片段放置或图片时间发生变化时，请与其核心一起加载。
- 仅用于源/生成媒体或预处理派生资产。从 `/hyperframes-core` 复制创作者编辑标记到 `references/creator-editing-recipes.md`。

```bash
# 快速迭代检查；在编写时按需重复。
npx hyperframes lint

# 必须的最终关卡；包括 lint。
npx hyperframes check
npx hyperframes preview --background
npx hyperframes render --quality looks --output out.mp4
test -s out.mp4
ffprobe -v error -show_format -show_streams out.mp4
```

`check` 首先运行 lint，然后使用一个浏览器会话和一个查找通过，以审计运行时错误、失败请求、布局、`*.motion.json` 断言和 WCAG 对比。持久性发现会阻止退出；瞬态入口或退出发现是信息性的。使用 `--strict` 以阻止警告。`validate`、`inspect` 和 `layout` 保持为兼容别名，但不得在新指令或脚本中出现。

## 渲染前预览

只有在 `check` 通过后，才打开最终组合预览（`#project/<名称>`），以审查组装的时间轴。聊天中的计划和平板电脑草图不是对最终视频的批准。渲染始终需要 `hyperframes/references/review-loop.md` 中定义的最终批准。

## 子组合冒烟测试

静态审核无法捕获所有挂载失败。当项目使用子组合时，为每个主机槽捕获至少一个可见中点：

```bash
npx hyperframes snapshot --at <t1>,<t2>,<t3>
```

将微小的未样式内容、画布大小的图标、缺失的英雄元素或时间轴注册超时视为阻止渲染的挂载缺陷。有关相应的修复，请参阅 `hyperframes-core/references/sub-compositions.md`。

## 代理约定

- **在手动编写运动之前搜索目录。** `npx hyperframes catalog --query "<用普通英语描述的节奏>"`。搜索完全是本地的：没有托管层，没有账户，查询文本永远不会发送到任何地方。默认情况下，它根据与项目名称、标题和描述共享的词汇进行排序，这会遗漏任何不重用目录自身措辞的措辞。添加 `--on-device` 以按含义排序（见离线层）。使用英语查询，即使视频不是英语。两个层都索引英语目录，因此其他脚本中的查询不会产生可搜索的术语并返回空结果。用英语描述运动；屏幕上的副本保持视频需要的任何语言。`查询中没有可搜索的词` 意思就是这，不是缺失的组件，所以不要将其报告为目录差距。
- **阅读哪个层回答了；永远不要从结果出现中推断。** 使用 `--json` 时，信封包含 `query`、`tier`（`on-device` 或 `words`）、`tier_detail`、`dropped`、`unindexed`、`shown`、`total` 和 `results`，以及当回答层产生时 `top_score` 和当层被请求但无法运行或当搜索返回空结果且更好的层仍在等待某人同意时 `warnings`。`words` 上的弱结果是可以预料的；`on-device` 上的相同结果是一个错误。`top_score` 仅在 `on-device` 上，并且没有背后的阈值：排序器为每个查询按某种顺序返回整个目录，所以将其作为证据而不是通过或失败来读取。
- **`dropped` 和 `unindexed` 是注册和设备索引之间的相反偏差，重写查询两者都无济于事。** `dropped` 计数此注册无法安装的排名名称，因此最强的匹配是正在丢失的匹配。`unindexed` 计数索引完全看不到的注册移动，没有任何查询可以返回。刷新注册不是解决这两个问题的答案：其清单包含 24 小时 TTL 并自行修复，而向量是单独发布的工件，被获取到 `~/.hyperframes/catalog/` 中。当 `unindexed` 大于零时，重新运行 `--on-device` 会重新获取该索引，因此这就是给用户的补救措施。纯过度覆盖偏差（`dropped` 大于零而 `unindexed` 为零）不会触发重新获取；清除 `~/.hyperframes/catalog/` 是唯一出路。两个计数都是名称而不是结果，因此都可以超过 `total`。
- **当搜索返回无安装价值时，请说明。** `npx hyperframes feedback --search-miss "<你运行的查询>" --wanted "<你需要的移动>" --tier <回答的层>`。你不必组装这一行：`catalog --query` 会预填它，并且每个 `--json` 搜索信封都作为 `report_gap` 包含查询和层，已经正确——填写 `--wanted` 并发送。这是唯一将查询发送到任何地方的路径，它是一个单独的故意命令，因此普通的 `catalog --query` 仍然保持其承诺不发送任何东西。**无论哪个层，只要结果不做事情，就报告。** 不要等待 `on-device` 层，它需要一个同意的 33 MB 下载，因此在大多数代理运行中都是离线的——等待它意味着永远不会报告。层随着报告一起出现，因此词汇偏差与含义偏差可以区分，而无需你判断哪个你命中了。返回的是目录还没有的移动列表，直接读取而不是猜测安装计数，因此重要的措辞是你想要的效果，而不是你想象的项名称。它不包含评级，也永远不会落入评级指标。
- **提供离线层；永远不要无声启用。** 一次性的 ~33 MB 下载（`bge-small-en-v1.5` 的量化 ONNX 构建及其分词器，固定到固定修订版）以及来自注册的目录向量，都缓存到 `~/.hyperframes/` 下，既不添加到项目也不添加到任何包。一旦缓存，它就会按含义排序，不会发送任何东西。大声说出大小，让对方决定，一旦他们同意，就传递 `--on-device`（使用 `-y` 跳过提示）。交互式提议仅在 TTY 上触发。在 `--json` 下没有提示，但找到空结果的搜索会将同样的请求放入 `warnings`，所以你自己要将其交给用户决定。

- 代理和 CI 调用优先选择 `--json`。服务器模式的 `render`、`preview` 和 `play` 不提供普通 JSON 输出；`preview --selection --json` 和 `preview --context --json` 是查询模式的例外。
- `doctor --json` 总是退出零。根据其有效负载进行阻止：

  ```bash
  npx hyperframes doctor --json | jq -e '.ok' >/dev/null
  ```

- 非TTY 模式是自动的，并搭建居中空白。仅当从命名示例开始时才传递 `--example`。使用 `--non-interactive` 强制在 TTY 上强制标志模式。
- 在同一验证循环中使用一个 `HYPERFRAMES_RUN_ID`。
- 当相应的警告、变量或 CI 条件必须阻止渲染时，使用 `--strict`、`--strict-all` 和 `--strict-variables`。
- JSON 路径将主目录作为 `$HOME` 进行编辑；不要尝试反向编辑。
- 当托管云项目接近或超过 200 MB 上传限制时，使用 `cloud render --dry-run --json` 并遵循 `references/cloud.md` 中的 `.hyperframesignore` 调查。永远不要因为文件很大而忽略资产。
- 仅因检查通过而渲染。在最终预览时暂停，等待批准。

## Studio 指导的编辑

当用户提到“这个元素”或当前选择时，请查询 Studio 而不是猜测：

```bash
npx hyperframes preview --context --json --context-fields selection
```

当可用时，使用 `selection.target.hfId`，否则使用其选择器和源文件。如果结果报告 `no-selection`，请要求用户点击元素并重新运行。仅请求您需要的上下文切片；仅当需要计算样式或可编辑文本元数据时，才使用 `--context-detail full`。完整行为和失败代码在 `references/preview-render.md` 中。

## 渲染选择

| 需要                                     | 命令                                                                       |
| ---------------------------------------- | ----------------------------------------------------------------------------- |
| 快速本地迭代                           | `npx hyperframes render --quality draft`                                      |
| 第一次真实编码                         | `npx hyperframes render --quality looks --output out.mp4`                     |
| 最终本地交付                           | `npx hyperframes render --quality delivery --output out.mp4`                  |
| 可重复的容器渲染                       | `npx hyperframes render --docker --strict --output out.mp4`                   |
| 本地变量驱动的批量渲染                 | `npx hyperframes render --batch rows.json --output "renders/{name}.mp4"`      |
| HeyGen 托管的零基础设施渲染             | `npx hyperframes cloud render`                                                |
| 自管理的分布式 AWS 渲染               | `npx hyperframes lambda render <项目> --width 1920 --height 1080 --wait`   |
| 自管理的分布式 GCP 渲染               | `npx hyperframes cloudrun render <项目> --width 1920 --height 1080 --wait` |

技能归属是自动的——上述示例不需要 `--skill`。由工作流（`hyperframes init --skill=<workflow>`）搭建的项目在 `hyperframes.json` 中记录其拥有的技能，并且每个后续渲染都会在匿名遥测中继承它：重新渲染、`npm run render` 和 `--batch` 一样。仅当项目不是通过工作流创建的时，才显式传递 `--skill=<slug>` 以标记该项目（然后它的第一次渲染会保留它）。

当用户想要托管渲染而不需要本地 Chrome、FFmpeg 或 AWS 时，请使用云渲染。仅当 AWS 所有权是要求时，才使用 Lambda。仅当 GCP 所有权是要求时，才使用 Cloud Run。在运行任何云路径之前，请阅读匹配的参考。

在验证成功渲染后，除非遥测被禁用或用户选择退出，否则发送一个反馈报告：

```bash
npx hyperframes feedback --rating <0-10> --comment "<具体结果或摩擦>"
```

保持干净运行的反馈简洁。对于任何错误或摩擦，在提交之前捕获**可重现数据包**；不要只发送症状摘要。包括可重运行的命令（相对于项目目录——反馈提交到公共频道，所以**不要**粘贴绝对路径、主目录前缀或用户/机器标识符）、预期与实际行为、确切错误（也从堆栈跟踪中删除绝对路径——保留 basename + 行号，删除开头的目录）、输出是否完成/回退/失败、解决方案以及可重现项目状态。对于评级 ≤ 7 且描述视觉缺陷（黑帧、闪烁、损坏输出、错误帧、空白输出、其他视觉异常）的情况，还包括 `COMPOSITION_STRUCTURE:` 块——一个隐私保护的结构解剖（元素计数 + 属性存在 + 时间轴形状），以便维护人员可以与已知错误家族进行模式匹配，而无需组合 ZIP。代理自动通过组合普查辅助程序填充此内容；人类用户不会手动填充。如果问题没有再次重现，请说明，但仍然包括最后一个失败的命令和日志。仅在与同意一起使用时使用 `--file-issue`：它将最小的可重现发布到公共 URL。所需的包格式和隐私警告在 `references/preview-render.md` 中。

## 在运行命令之前阅读匹配的参考

下表中的参考和拥有技能是必须的命令合同，而不是可选的背景阅读。在运行表格中的命令之前，请阅读其匹配的行。

| 需要                                                                                               | 参考                             |
| -------------------------------------------------------------------------------------------------- | ------------------------------------- |
| `init`、`capture`、`skills`                                                                        | `references/init-and-scaffold.md`     |
| `lint`、`check`、运动副件、`snapshot`                                                               | `references/lint-validate-inspect.md` |
| `compare`、`grade-compare`、变量驱动的 `render --batch`                                       | `references/compare-and-batch.md`     |
| `beats` 用于现有项目 Studio 节奏网格                                                             | `references/beats.md`                 |
| `preview`、`play`、`render`、`publish`、Studio 上下文、反馈                                   | `references/preview-render.md`        |
| `doctor`、浏览器管理                                                                       | `references/doctor-browser.md`        |
| `auth`、HeyGen 托管的云渲染、模板变量                                                              | `references/cloud.md`                 |
| AWS Lambda 部署和渲染                                                                | `references/lambda.md`                |
| Google Cloud Run 部署和渲染                                                          | `references/cloudrun.md`              |
| `info`、`upgrade`、`compositions`、`timeline`、`docs`、`benchmark`、遥测、媒体预处理 | `references/upgrade-info-misc.md`     |

对于组合变量，还请阅读 `/hyperframes-core` → `references/variables-and-media.md`。对于 `hyperframes add` 和 `hyperframes catalog`，请使用 `/hyperframes-registry`。在 `hyperframes present` 之前，请阅读 `/slideshow`；在 `hyperframes keyframes` 之前，请阅读 `/hyperframes-keyframes`。对于 TTS、转录、字幕或背景移除选择，请使用 `/media-use`。

专门命令由其拥有的工作流专门文档：

```bash
npx hyperframes present <项目目录> --port 3004 --no-open
npx hyperframes beats <项目目录> --json
npx hyperframes keyframes <项目目录> --json
npx hyperframes media-treatment --capabilities
npx hyperframes figma asset KEY:10-20
```

`present` 提供一个可导航的演示文稿，具有演示者和观众同步。`beats` 是 `references/beats.md` 中定义的独立 Studio 节奏网格实用程序。`keyframes` 显示安全的查找动画和运动路径诊断。`media-treatment` 发现、应用和清除本地素材上的确定性外观——从 `--capabilities` 开始获取概述，并使用 `--capability <名称>` 获取一个家族；`/media-use` 拥有简要要求的外观。`figma` 通过 REST API 导入，具有 `asset`、`tokens` 和 `component` 子命令，需要 `FIGMA_TOKEN`；运动和着色器导入没有 REST 端点，并且是代理专用的，因此 `/figma` 拥有这些。

## 你不应该运行的命令

`hyperframes --help` 中的两个条目不是作者循环的一部分，并且使用它们浪费了一个回合：

- `events` 是技能用于报告其**自身**调用的遥测端点。它发出匿名事件并退出 0，无论你传递给它什么。它不是读取遥测的方式，代理没有理由手动调用它。
- `validate`、`inspect` 和 `layout` 是为旧脚本保留的已弃用别名。`check` 是维护的，并且这是本技能中每个参考所假设的。
