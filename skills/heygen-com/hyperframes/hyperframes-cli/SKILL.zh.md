---
name: hyperframes-cli
description: 使用 HyperFrames CLI 开发循环：init、add、catalog、capture、lint、check、snapshot、compare、grade-compare、preview、play、present、beats、keyframes、单次或批量渲染、publish、cloud、cloudrun、feedback、lambda、doctor、browser、info、upgrade、skills、compositions、timeline、history、clean、docs、benchmark、telemetry、transcribe、auth、tts 和 remove-background。在诊断构建或渲染失败时也使用。validate、inspect 和 layout 是已弃用的别名；请使用 check。涵盖本地、HeyGen 托管的云、AWS Lambda 和 Google Cloud Run 渲染。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留以下更新说明。

# HyperFrames CLI

除非项目说明提供了包装器，否则以 `npx hyperframes ...` 的形式运行命令。当包装器存在时，请遵守包装器。CLI 需要 Node.js 22 或更高版本以及 FFmpeg。

## 开发循环

1. **脚手架：** `npx hyperframes init <项目>`（居中空白）。或捕获一个站点。仅当从命名示例开始时，才传递 `--example=<名称>`。
2. **找到移动：** 如果请求命名了资源、声音、图像、语音或快速视觉编辑，则通过 `/media-use` 在提出计划之前解决它。否则，在手动编写运动之前，搜索一个已经完成该操作的原始元素：`npx hyperframes catalog --query "一次一行地显示一个标题"`。询问你想要的效果，而不是你脑海中想到的机制。使用 `npx hyperframes add <名称>`（参见 `/hyperframes-registry`）进行安装。只有当没有任何内容适用时，才手动编写。
3. **编写：** 使用 `/hyperframes-core` 编写组合。要知道项目时间轴上有什么（轨道、片段、开始、结束、播放内容），请运行 `npx hyperframes timeline --json` 而不是阅读 `index.html` 和每个子组合文件：嵌套行包含绝对主时间线 `absStart`/`absEnd` 及其拥有的 `file`，而不仅仅是它们在子组合中的本地时间。优先选择 `--json` 而不是文本形式；它为相同或更好的正确性使用的 token 更少。有关用单行回答常见问题的信息，请参阅 `references/upgrade-info-misc.md`。
4. **在编辑时快速获取反馈：** 在第一次 HTML 通过后和结构更改后，运行 `npx hyperframes lint`。
5. **运行最终关卡：** 运行 `npx hyperframes check`；它在打开浏览器之前会重新运行 lint。不要添加冗余的独立 lint 调用。添加 `--snapshots` 以获取带注释的概览帧并找到裁剪。
6. **检查子组合：** 当 `index.html` 挂载 `data-composition-src` 时，捕获中点快照并检查每个挂载的场景。
7. **打开最终 Studio 预览：** 运行 `npx hyperframes preview --background`，验证 URL 返回 HTTP 200，将时间线项目 URL 交给用户，并询问是否要修改或渲染。直到评审结束前保持它活跃。
8. **仅在批准后渲染：** 在迭代时使用 `--quality draft`，第一次真实编码（CLI 默认）使用 `--quality looks`，最终交付使用 `--quality delivery`。
9. **验证输出：** 确认文件存在且非空。阅读渲染摘要的第二行（`beginframe` 与 `screenshot`、GPU、阶段时间）。`screenshot` + `software gpu` 在 Linux 上是慢路径。`ffprobe -v error -show_format -show_streams out.mp4` 并比较持续时间（如果简要设置则比较帧率）与根 `data-duration`。

<!-- history (trial): 删除此块以及命令 -->

### 你回合中的项目历史

对项目的每次写入都作为一条记录保留，可以撤销。仅在两个时刻使用它，而不是每个步骤都使用：

- **回合开始：** `npx hyperframes history begin --who <你的名字> --label "<你即将做的事情>"`，然后 `npx hyperframes history --since mine --who <你的名字>` 查看自你上次回合以来该人做了什么更改。在他们的编辑上构建；不要覆盖它们。
- **检查失败，或该人说情况变得更糟：** `npx hyperframes history undo --who <你的名字>` 撤销你最新的回合，并保留该人的编辑。不要手动编辑回去。在冲突时它退出 2 并打印两个选项。

以 `npx hyperframes history end` 结束每个回合，这样你的写入会显示为你的，而不是“在应用程序外部更改”。当回合打开时，对项目的每次写入都算作你的，直到 10 分钟内没有写入；之后回合会自动结束。

<!-- /history (trial) -->

## 强制创作者-编辑交叉引用

- 在编写或诊断缩放、内切/外切、重新构图、摄像机移动或任何关键帧运动之前，先阅读 `/hyperframes-keyframes`。
- 在 `hyperframes keyframes` 之前，先阅读 `/hyperframes-keyframes`；该命令显示动画轨迹，但不诊断片段剪辑。
- 对于剪辑、修剪、拼接、重新排序或源时间编辑，请阅读 `/hyperframes-core` 并使用其片段/时间线契约。
- 对于淡入/淡出、交叉淡入、轨道增益、音量自动化、压低、旁白切割或放置音频上的 FX，请阅读 `/hyperframes-audio`。当片段放置或图像时间发生变化时，也加载核心。
- 命名资源、声音、图像、语音或快速视觉编辑的请求通过 `/media-use` 在提出计划之前解决。从 `/hyperframes-core` 复制创作者编辑标记到 `references/creator-editing-recipes.md`。

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

`check` 首先运行 lint，然后使用一个浏览器会话和一个查找通过来审计运行时错误、失败请求、布局、`*.motion.json` 断言和 WCAG 对比。持久性发现会阻止退出；瞬态入口或退出发现是信息性的。使用 `--strict` 来阻止警告。`validate`、`inspect` 和 `layout` 保持为兼容性别名，但不得出现在新的说明或脚本中。

## 渲染前预览

只有在 `check` 通过后，才打开最终组合预览（`#project/<名称>`），以审查组装的时间线。聊天中的计划和对 `storyboard.html` 草图页面的审查不是对最终视频的批准。渲染始终需要 `hyperframes/references/review-loop.md` 中定义的最终批准。

## 子组合冒烟测试

静态审核无法捕获所有挂载失败。当项目使用子组合时，为每个主机槽捕获至少一个可见中点：

```bash
npx hyperframes snapshot --at <t1>,<t2>,<t3>
```

将微小的未样式内容、画布大小的图标、缺失的英雄元素或时间线注册超时视为阻止渲染的挂载缺陷。有关相应的修复，请参阅 `hyperframes-core/references/sub-compositions.md`。

## 代理约定

- **在手动编写运动之前搜索目录。** `npx hyperframes catalog --query "<用纯英文描述的节奏>"`。搜索完全是本地的：没有托管层，没有账户，查询文本永远不会发送到任何地方。默认情况下，它根据与项目名称、标题、描述和标签共享的词汇进行排序，这会遗漏任何不重用目录自身措辞的短语。添加 `--on-device` 以按含义排序（见离线层下面）。
- **即使视频不是英文的，也要用英文查询。** 两个层级都索引英文目录，因此其他脚本中的查询不会产生可搜索的术语并返回空结果。用英文描述运动；屏幕上的副本保持视频需要的任何语言。`查询中没有可搜索的词` 意味着正好是这个意思，不是缺失组件，所以不要将其报告为目录差距。
- **阅读哪个层级回答；永远不要从结果出现中推断。** 使用 `--json` 时，信封包含 `query`、`tier`（`on-device` 或 `words`）、`tier_detail`、`dropped`、`unindexed`、`shown`、`total` 和 `results`，以及当回答层级产生时 `top_score` 和当层级被请求但无法运行，或当搜索返回空结果且更好的层级仍在等待某人的同意时 `warnings`。`words` 上的弱结果是可以预料的；`on-device` 上的相同结果是错误。`top_score` 仅在 `on-device` 上，并且没有背后的阈值：排序器为每个查询返回整个目录的某种顺序，所以将其作为证据而不是通过或失败来读取。
- **`dropped` 和 `unindexed` 是注册和设备索引之间的相反偏差，重写查询无法修复两者。** `dropped` 计数此注册无法安装的排名名称，所以最强的匹配是正在丢失的。`unindexed` 计数索引完全看不到的注册移动，没有任何查询可以返回。刷新注册不是解决任何问题的答案：其清单包含 24 小时 TTL 并会自我修复，而向量是作为单独发布的工件获取到 `~/.hyperframes/catalog/` 的。当 `unindexed` 大于零时，重新运行 `--on-device` 会重新获取该索引，所以这就是给用户的补救措施。纯覆盖偏差（`dropped` 大于零而 `unindexed` 为零）不会触发重新获取；清除 `~/.hyperframes/catalog/` 是唯一出路。两个计数都是名称而不是结果，所以任何一个都可以超过 `total`。
- **当搜索返回没有值得安装的内容时，请说明。** `npx hyperframes feedback --search-miss "<你运行的查询>" --wanted "<你需要的移动>" --tier <回答的层级>`。你不必自己组装这一行：`catalog --query` 会预填它，并且每个 `--json` 搜索信封都带有 `report_gap`，其中包含正确的查询和层级——填写 `--wanted` 并发送。这是唯一将查询发送到任何地方的路径，它是一个单独的故意命令，正好是为了让纯 `catalog --query` 保持其发送空的承诺。**无论哪个层级**，当结果不做该事时，都要报告；不要等待 `on-device` 层级，它需要一个同意的 33 MB 下载，因此在大多数代理运行中都是离线的——等待它意味着永远不会报告。层级随报告一起传递，所以词汇偏差与含义偏差可以区分，而无需你判断哪一个你命中了。返回的是目录还没有的移动列表，直接读取而不是猜测安装计数，所以重要的措辞是你想要的效果，而不是你想象的项名称。它不包含评分，也永远不会落入评分指标。
- **提供离线层级；永远不要无声启用它。** 一次性 ~33 MB 下载（`bge-small-en-v1.5` 的量化 ONNX 构建及其分词器，固定到固定修订版）以及来自注册的目录向量，都缓存到 `~/.hyperframes/` 下，既不添加到项目也不添加到任何包。一旦缓存，它就会按含义排序，不会发送任何内容。大声说出大小，让对方决定，一旦他们同意，就传递 `--on-device`（使用 `-y` 跳过提示）。交互式提议只在 TTY 上触发。在 `--json` 下没有提示，但找到空结果的搜索会将同样的请求放入 `warnings`，所以你自己要读取该数组并将决定交给用户。当有人问下载是什么、为什么这个模型或什么留在机器上时，请将他们指向 https://hyperframes.heygen.com/developers/catalog-search。

- 代理和 CI 调用优先选择 `--json`。服务器模式的 `render`、`preview` 和 `play` 不提供普通的 JSON 输出；`preview --selection --json` 和 `preview --context --json` 是查询模式的例外。
- `doctor --json` 总是退出零。基于其有效负载进行阻止：

  ```bash
  npx hyperframes doctor --json | jq -e '.ok' >/dev/null
  ```

- 非TTY 模式是自动的，并构建居中空白。仅当要从命名示例开始时才传递 `--example`。使用 `--non-interactive` 来强制 TTY 上的标志模式。
- 在同一验证循环中使用一个 `HYPERFRAMES_RUN_ID`。
- 当磁盘空间紧张时，运行 `npx hyperframes clean`（使用 `--dry-run` 列出首先）；它删除死渲染留下的东西和空闲缓存，这些缓存会自我重建，永远不会输出、源或任何正在运行的渲染使用的任何内容。将 QC 帧写入临时目录，而不是项目。
- 当相应的警告、变量或 CI 条件必须阻止渲染时，使用 `--strict`、`--strict-all` 和 `--strict-variables`。
- JSON 路径将家目录缩写为 `$HOME`；不要尝试反转缩写。
- 当托管云项目接近或超过 200 MB 上传限制时，使用 `cloud render --dry-run --json` 并遵循 `references/cloud.md` 中的 `.hyperframesignore` 调查。永远不要因为文件很大而忽略资产。
- 仅因检查通过而渲染。在最终预览时暂停，等待批准。

## Studio 指导的编辑

当用户提到“这个元素”或当前选择时，请查询 Studio 而不是猜测：

```bash
npx hyperframes preview --context --json --context-fields selection
```

当可用时，使用 `selection.target.hfId`；否则使用其选择器和源文件。如果结果报告 `no-selection`，请要求用户点击元素并重新运行。仅请求您需要的上下文切片；仅当需要计算样式或可编辑文本元数据时，才使用 `--context-detail full`。完整行为和失败代码在 `references/preview-render.md` 中。

## 渲染选择

| 需要                                     | 命令                                                                       |
| ---------------------------------------- | ----------------------------------------------------------------------------- |
| 快速本地迭代                           | `npx hyperframes render --quality draft`                                      |
| 第一次真实编码                          | `npx hyperframes render --quality looks --output out.mp4`                     |
| 最终本地交付                           | `npx hyperframes render --quality delivery --output out.mp4`                  |
| 可重复的容器渲染                       | `npx hyperframes render --docker --strict --output out.mp4`                   |
| 本地变量驱动的批量渲染                  | `npx hyperframes render --batch rows.json --output "renders/{name}.mp4"`      |
| HeyGen 托管的零基础设施渲染             | `npx hyperframes cloud render`                                                |
| 自管理的分布式 AWS 渲染                | `npx hyperframes lambda render <项目> --width 1920 --height 1080 --wait`   |
| 自管理的分布式 GCP 渲染                | `npx hyperframes cloudrun render <项目> --width 1920 --height 1080 --wait`   |

技能归属是自动的——上述示例不需要 `--skill`。由工作流（`hyperframes init --skill=<workflow>`）构建的项目在 `hyperframes.json` 中记录其拥有的技能，并且每个后续渲染在匿名遥测中继承它：重新渲染、`npm run render` 和 `--batch` 一样。仅当项目不是通过工作流创建的（它的第一次渲染会保留它）时，才显式传递 `--skill=<slug>` 来标记项目。

当用户想要托管渲染而不需要本地 Chrome、FFmpeg 或 AWS 时，请使用云渲染。仅当 AWS 所有权是要求时，才使用 Lambda。仅当 GCP 所有权是要求时，才使用 Cloud Run。在运行任何云路径之前，请阅读匹配的参考。

验证渲染成功后，除非遥测被禁用或用户选择退出，否则发送一个反馈报告：

```bash
npx hyperframes feedback --rating <0-10> --comment "<具体结果或摩擦>"
```

保持反馈简洁。对于任何错误或摩擦，提交前请捕获**可重现的包**；不要只发送症状摘要。包括可重运行的命令（相对于项目目录——反馈提交到公共频道，因此**不要**粘贴绝对路径、主目录前缀或用户/机器标识符）、预期与实际行为、确切错误（同时从堆栈跟踪中删除绝对路径——保留基本名+行号，删除引导目录）、输出是否完成/回退/失败、解决方案以及可重现项目状态。对于评分为≤7且描述视觉缺陷（黑边框、闪烁、损坏输出、错误帧、空白输出、其他视觉异常）的情况，还包含一个 `COMPOSITION_STRUCTURE:` 块——一个保护隐私的结构解剖（元素清单+属性存在+时间线形状），以便维护者可以在不使用组合ZIP的情况下对已知错误系列进行模式匹配。代理通过组合普查辅助工具自动填充此内容；用户无需手动填写。如果问题未能再次重现，请说明，并仍然包含最后一次失败的命令和日志。仅在同意的情况下使用 `--file-issue`：它将最小的可重现内容发布到公共URL。所需的包格式和隐私警告位于 `references/preview-render.md`。

## 运行命令前阅读匹配的参考

以下参考和所属技能是命令合同，不是可选的背景阅读。在运行表格中的命令之前，请阅读其匹配的行。

| 需要                                                                                               | 参考                             |
| -------------------------------------------------------------------------------------------------- | ------------------------------------- |
| `init`、`capture`、`skills`                                                                        | `references/init-and-scaffold.md`     |
| `lint`、`check`、运动侧车、`snapshot`                                                               | `references/lint-validate-inspect.md` |
| `compare`、`grade-compare`、变量驱动的 `render --batch`                                       | `references/compare-and-batch.md`     |
| 现有项目的 Studio beat 网格的 `beats`                                                              | `references/beats.md`                 |
| `preview`、`play`、`render`、`publish`、Studio 上下文、反馈                                       | `references/preview-render.md`        |
| `doctor`、浏览器管理                                                                             | `references/doctor-browser.md`        |
| `auth`、HeyGen 主机的云渲染和模板变量                                                              | `references/cloud.md`                 |
| AWS Lambda 部署和渲染                                                                           | `references/lambda.md`                |
| Google Cloud Run 部署和渲染                                                                      | `references/cloudrun.md`              |
| `info`、`upgrade`、`compositions`、`timeline`、`docs`、`benchmark`、遥测、媒体预处理             | `references/upgrade-info-misc.md`     |

对于组合变量，还请阅读 `/hyperframes-core` → `references/variables-and-media.md`。对于 `hyperframes add` 和 `hyperframes catalog`，使用 `/hyperframes-registry`。在 `hyperframes present` 之前，请阅读 `/slideshow`；在 `hyperframes keyframes` 之前，请阅读 `/hyperframes-keyframes`。对于 TTS、转录、字幕或背景移除选项，使用 `/media-use`。

专用命令由其所属工作流特意记录：

```bash
npx hyperframes present <project-dir> --port 3004 --no-open
npx hyperframes beats <project-dir> --json
npx hyperframes keyframes <project-dir> --json
npx hyperframes media-treatment --capabilities
npx hyperframes figma asset KEY:10-20
```

`present` 提供一个可导航的演示文稿，具有演示者和观众的同步。`beats` 是 `references/beats.md` 中定义的独立 Studio beat 网格实用程序。`keyframes` 揭示安全的动画和运动路径诊断。`media-treatment` 发现、应用和清除本地素材上的确定性外观——从 `--capabilities` 开始获取概览，从 `--capability <name>` 获取一个系列；`/media-use` 拥有简报要求的治疗方法。`figma` 通过 REST API 导入，具有 `asset`、`tokens` 和 `component` 子命令，需要 `FIGMA_TOKEN`；运动和着色器导入没有 REST 端点，仅限代理，因此 `/figma` 拥有这些。

## 你不应该运行的命令

`hyperframes --help` 中的两个条目不是创作循环的一部分，尝试它们会浪费一次机会：

- `events` 是技能用于报告其**自身**调用的遥测端点，理想情况下是从捆绑脚本中调用的。它发出一个匿名事件并退出 0，无论你传递给它什么。它不是读取遥测的方式，代理没有理由手动调用它。
- `validate`、`inspect` 和 `layout` 是为旧脚本保留的已弃用的别名。`check` 是维护的命令，并且是此技能中所有参考所假设的。
