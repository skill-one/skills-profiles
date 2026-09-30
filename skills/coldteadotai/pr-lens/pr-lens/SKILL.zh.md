---
name: pr-lens
description: 什么事：将代码变更或代码库的一部分绘制为动画化的架构图或数据流图，可以独立绘制或在拉取请求中绘制。何时使用：当需要绘制图表、可视化或解释变更或系统时，或者在拉取请求中需要附带图表时。关键词：PR Lens、图表、架构、数据流、可视化、拉取请求
---

# PR Lens

PR Lens 将代码以视觉丰富的动画图表形式呈现。它可以表示差异、架构、数据流等。

差异或代码被表示为一个 JSON 文档（轨道、节点、边、有序流），并将其渲染为动画 SVG。

## 操作手册

在编写之前，确定图表的放置位置：画布，或 SVG 和拉取请求评论。只有画布绘制 `payload`，即流程步骤上的示例请求和响应。晚决定会导致重新经过步骤 2 和 3。

1. **阅读差异。** 当要求表示代码更改时：`git diff --find-renames <base>...<head>`。基准是合并基准，而不是基准分支的尖端。

   如果不是表示代码差异，则阅读要视觉表示的代码

2. **编写文档** 到 `.pr-lens/graph.json`，遵循 `references/graph-document.md`。`references/example.graph.json` 是一个有效的参考，包含三个轨道、所有四个 delta 状态、一个英雄边、一个七步流程、一个嵌套的向下钻取树和六步演练。在编写第一个之前阅读它。它比阅读参考更快。如果它将发送到画布，则在编写时为每个移动数据的流程步骤（`messages`）提供 `payload`。下面的“流程步骤上的示例流量”说明了放入的内容。只有流程步骤包含一个。流程需要 `data-flow` 透镜，因此架构视图不绘制任何内容。

3. **验证，并修复**

   ```bash
   npx @coldtea/pr-lens-cli@latest validate .pr-lens/graph.json
   ```

   修复每个失败并再次运行它。不要渲染无效文档；不要通过删除它命名的元素来“绕过”失败。

4. **渲染。**

   ```bash
   npx @coldtea/pr-lens-cli@latest render .pr-lens/graph.json --theme light
   ```

   默认情况下渲染为浅色，除非用户请求另一个主题。SVG、清单和 `drawn.graph.json` 将位于 `.pr-lens/` 下自己的目录中，并以文档的标题命名。渲染会打印该路径，因此从那里读取。CLI 将 `.pr-lens/` 添加到存储库的 .gitignore 中。不要提交任何内容。这些文件将根据差异在任何人再次需要它们时从 diff 重新构建。每个 SVG 都以其视图、主题和内容哈希命名；`manifest.json` 按透镜和视图列出它们，因此从那里或从目录读取名称。

   如果用户要求图表、解释或架构的图片，更多，将其放在画布上并返回链接：

   ```bash
   npx @coldtea/pr-lens-cli@latest canvas push .pr-lens/<drawing>/drawn.graph.json
   ```

   传递渲染打印的路径。一个空的 `canvas push` 在签出只包含一个时找到绘图；多于一个时，它列出了它们并询问哪个，因此始终传递路径。

   它打印三个链接。给用户视图链接 `https://prlens.dev/c/{id}`：那是图表，全屏，每个视图在一页上，并且无需登录即可打开。编辑链接，以 `#w=…` 结尾，允许其持有者将画布推送到，因此除非他们要求，否则不要将其包含在回复中，并且永远不要将链接粘贴到任何公共地方。嵌入链接将顶部视图作为 SVG 用于 README。

   再次推送相同文档会更新相同的画布，因此后续操作，如“重命名该节点”或“添加队列”，是：编辑文档、验证、渲染、推送。虽然标题保持不变，但它渲染到相同的目录并推送到相同的画布，因此链接不会改变。如果推送失败，请告知他们在哪里可以找到 SVG，以及哪个是顶部视图。

   不同的图表只需要不同的标题。它渲染到自己的目录并推送到自己的画布，而第一个保持不变。`canvas list` 显示它们全部。

5. **附加，当有要附加的拉取请求时。** 这意味着用户要求你打开一个 PR，要求在现有的 PR 上提供一个图表，或者你作为所做的更改的一部分打开一个 PR。否则跳过此步骤。

图表如何到达取决于熔炉。在编写可能熔炉没有的标志周围的正文之前，运行 `git remote get-url origin` 查看主机。

   **GitHub。** GitHub CLI 将图表与拉取请求一起上传。使用指向本地文件的 Markdown 图像编写正文，然后将相同的路径传递给 `--attach`。`gh` 重新编写参考以指向上传的资产并保留您编写的替代文本：

   ```markdown
   将批量发送从每个接收者的触发器移至批量端点。

   ![此更改后的架构：队列路由、新的批量发送者和已停用的每个接收者路径](.pr-lens/overview-light-4f9bd6c1.svg)
   ```

   ```bash
   gh pr create --title "批量广播发送" --body-file .pr-lens/body.md \
     --attach .pr-lens/overview-light-4f9bd6c1.svg
   ```

   在已存在的拉取请求上，使用相同的两个标志 `gh pr edit <number>` 将图表放入描述中，并使用 `gh pr comment <number>` 将其放入评论中。对于正文引用的每个图表，重复 `--attach`。

   gh 有三个规则：
   - 参考必须是 Markdown 图像，`![alt](path)`。HTML `<img>` 或 `<picture>` 被保留原样，文件被附加到正文底部。
   - 替代文本是对于没有图像的读者来说的标题。用一句话说明图表显示的内容。
   - `--attach` 已在 GitHub CLI 2.99 中到达。在编写围绕它的正文之前，请使用 `gh --version` 进行检查。

   将审阅者需要的视图附加到画布上，并将其余部分保留在 `.pr-lens/` 中：首先是顶部的架构视图，如果更改有一个值得遵循的序列，则接着是一个数据流。带有四个图表的正文比带有两个图表的正文更差，除非四个图表确实需要理解更改，例如在复杂功能或重构的情况下。

   **GitLab。** 没有东西为您上传描述中的文件，因此请首先将每个 SVG 上传到项目。响应包括要粘贴到描述中的 Markdown：

   ```bash
   curl -sf --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
     --form "file=@.pr-lens/overview-light-4f9bd6c1.svg" \
     "https://gitlab.com/api/v4/projects/<url-encoded-path>/uploads"
   # → {"markdown":"![overview-light-4f9bd6c1](/uploads/…/overview-light-4f9bd6c1.svg)", …}

   glab mr create --title "批量广播发送" --description "$(cat .pr-lens/body.md)"
   ```

   上传的图像为每个合并请求的读者加载。在私有项目上的原始文件 URL 不会。问题是附件 URL 是权限：它是无法猜测的，但任何人拥有它都可以看到图表，无论成员与否。如果项目是私有的，请告知用户此信息。GitLab 删除 `<picture>`，因此使用 `--theme neutral` 渲染，并引用单个 SVG。中性渲染有自己的背景，并在浅色和深色模式下阅读。浅色/深色对的任一半部分在其中一个模式下看起来都错误。

   **Bitbucket。** 评论和描述是纯 Markdown，没有 HTML，因此这里也没有可折叠部分或主题对。同样使用 `--theme neutral` 渲染。将 SVG 发布到某个持久位置，例如存储库的下载或画布，并作为普通 Markdown 图像引用它们。

   在任何不允许 `--attach` 的熔炉上，将 SVG 发布到某个持久位置，并让 CLI 组合评论：

   ```bash
   npx @coldtea/pr-lens-cli@latest comment \
     --graph .pr-lens/<drawing>/drawn.graph.json \
     --manifest .pr-lens/<drawing>/manifest.json \
     --asset-base-url https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<dir>
   ```

   `--graph` 接收绘图自己的 `drawn.graph.json`，而不是您编写的文档，因为更正会改变图表显示的内容，CLI 拒绝其清单未描述的文档。`--asset-base-url` 是您发布 SVG 的位置；省略它，Markdown 指向读者无法获取的本地路径。Markdown 被输出到 stdout，每个图表都是一个 `<picture>` 对。发布它是您的业务。

   当评论不是为 GitHub 时，添加 `--target gitlab` 或 `--target bitbucket`，以便组合器编写熔炉可以渲染的标记。GitHub 获得 `<picture>` 主题对和可折叠的向下钻取。GitLab 获得相同的 HTML，带有单个中性渲染。Bitbucket 获得 plain Markdown，并将视图扁平化。使用错误的靶标，评论将其标签显示为原始文本。

如果您宁愿不自己编写文档，`npx @coldtea/pr-lens-cli@latest analyze --base <ref>` 会通过询问提供者——Gemini、OpenAI 或任何说话 `/chat/completions` 的端点——使用您自己的密钥执行步骤 1 和 2。这是这里唯一需要一个的路径。

## 在打开的画布旁边回答

一旦画布被推送，您就可以在画布本身上回答关于它的问题。读者保持页面打开，在终端中询问您，而您的答案在那里播放：相机逐步移动，您命名的部分亮起，每个名称都是一个链接。

运行一次，当用户想要谈论他们打开的画布或即将打开的画布。命名您推送的绘图，与推送相同的路径：

```bash
npx @coldtea/pr-lens-cli@latest canvas open .pr-lens/<drawing>/drawn.graph.json
```

它打开一个跟随您的浏览器标签页。只有那个标签页移动。任何其他人阅读相同链接都会看到画布的原始状态。下面的每个命令都与该标签页通信，并使用与 `--drawing` 相同的路径。始终传递它：签出可以包含多个画布，路径指明您指的是哪一个。

**当用户给您一个您没有推送的画布链接**，例如 `https://prlens.dev/c/<id>`，使用链接打开它。这适用于任何文件夹，只要画布不是私有的：

```bash
npx @coldtea/pr-lens-cli@latest canvas open --canvas https://prlens.dev/c/<id>
```

CLI 将绘图副本保存到 `.pr-lens/canvases/<id>.graph.json`。从该文件中获取您答案的 ID。在下面的命令中，使用 `--canvas <id>` 替换 `--drawing`。私有的画布仅在其所有者运行 `npx @coldtea/pr-lens-cli@latest auth login` 后打开。

**当用户说“这个”、“这里”或“我选择的”**，首先查看。他们点击了组件，拖动了一个框或选择了一个绘图的一部分，而您看不到它：

```bash
npx @coldtea/pr-lens-cli@latest canvas look --drawing .pr-lens/<drawing>/drawn.graph.json
```

它打印 JSON：他们所在的图表（`diagram.stage`，准备好粘贴到步骤中）、屏幕上显示的内容（`inFrame`）、他们选择的（`scope`）、他们打开的答案，以及画布下悬挂的绘图（`fork`），如果有。当 `scope` 设置时，回答它。`following: false` 意味着他们离开了代理模式：告诉他们答案正在等待，而不是说您移动了他们的画布。

**回答** 使用 JSON 文件，或 `-` 以管道方式传递它：

```bash
npx @coldtea/pr-lens-cli@latest canvas answer .pr-lens/answer.json --drawing .pr-lens/<drawing>/drawn.graph.json
```

```json
{
  "question": "推送首先检查什么？",
  "steps": [
    {
      "heading": "推送首先检查令牌",
      "stage": { "kind": "view", "view": "overview" },
      "focus": { "kind": "selection", "nodes": ["canvas-api"] },
      "paragraphs": [
        {
          "parts": [
            { "text": "The " },
            { "text": "canvas API", "ref": { "kind": "component", "id": "canvas-api" } },
            { "text": " 拒绝没有写入令牌的推送，在绘制任何内容之前。" }
          ]
        }
      ]
    }
  ]
}
```

- 一到四步。通常是两步。每一步停在一张图表上，按读者应该遵循的顺序。
- `heading` 是最多六个字的句子：谁或什么，一个动词，发生了什么。第一步的标题是答案。对于一个 yes 或 no 的问题，它说 yes 或 no。
- `stage` 和 `focus` 与演练中完全一样。省略 `stage` 用于打开的图表。点亮一个或两个东西，而不是半个图表。
- 一个段落是一个或两个句子，最多 30 个字。第二个段落是第一个段落没有命名的失败或风险。
- 您命名的每个地方都有一个 `ref`：`component` 是一个节点 ID，`message` 是 `flowId/messageId`，`diagram` 是一个视图或流程 ID。从文档中精确复制 ID。永远不要编造一个。CLI 在发送之前检查每个 ID 是否与绘图匹配，应用程序再次检查；一个错误的 ID 会与存在的 ID 一起返回。
- 当画布无法回答问题的部分时，在 `cannotTell` 中说明缺失的内容，而不是猜测。

**“带我去 X”** 是一个相机移动，而不是一个答案：

```bash
npx @coldtea/pr-lens-cli@latest canvas show --drawing .pr-lens/<drawing>/drawn.graph.json \
  --diagram send-pipeline --focus send-pipeline/enqueue --open send-pipeline/enqueue
```

`--focus` 接收节点 ID 或 `flow/message` 并重复。`--open` 打开该消息的样本有效负载。

**“X 里面有什么”、“X 的详细说明”或“分解 X”** 是一个绘图。编写一个小的图表文档 X 的内部（最多十个节点），并将其挂到 X 下：

```bash
npx @coldtea/pr-lens-cli@latest canvas fork .pr-lens/inside-x.json --from x --drawing .pr-lens/<drawing>/drawn.graph.json
```

草图可以省略 `schemaVersion`、`kind` 和 `provenance`；它们来自画布。

**当问题需要更改图表本身**（缺少组件、错误的箭头），像往常一样编辑文档、验证、渲染和 `canvas push`。打开的标签页会自动重新加载到新的修订版上。

在 `answer`、`show` 和 `fork` 之后，CLI 告知读者在哪里。如果它说他们退出了，告诉用户答案正在他们的“问题”列表中等待，`/` 打开它。

## 当有拉取请求正文时

审阅者应该在阅读差异之前理解更改，因此图表应该放在他们首先查看的位置：描述，而不是尾随评论。用一句话说明更改的原因，然后是架构图表，然后是证明更改工作的任何内容，例如结果的屏幕截图或交互的录制。每个想法使用一个视觉。需要一段解释的图表有一个文档问题；回到步骤 2。

## 使文档值得阅读

- **包含未更改的内容。** 仅更改节点的图表什么也说不上爆破半径。更改影响的未更改邻居是上下文；将它们标记为 `delta: "unchanged"`。
- **轨道是读者的心理模型**（运行时、层、边界），而不是文件夹树。
- **一个英雄边**，外面两个：更改真正关心的连接。
- **只有当有一个值得动画的序列时才添加流程**。一个好的流程比三个薄的流程更好。
- **附加文件引用**：它们将成为审阅者点击的永久链接。
- **没有 findings 透镜。** PR Lens 是理解层，不是另一个审查机器人。没有用于错误、风险或安全笔记的字段，并且发明一个文档会被拒绝而不是修剪。

## 选择架构视图

将架构视图视为一个受 C4 启发的决策树，而不是一个清单。一个小更改只需要一个有用的视图。当更改影响用户、外部系统或系统边界时，从系统上下文开始。使用容器视图用于受影响的应用程序、服务、作业、数据存储和运行时。只有当受影响的容器的内部很重要时，才添加组件子视图。默认情况下不要添加代码级视图。

每个子视图向下移动一个级别，并覆盖更窄的范围。跳过空的、重复的或推测性的级别，并且不要仅凭文件夹名称推断架构。两个视图不应包含实质上相同的节点和边。保留解释爆破半径的直接邻居。

将数据流视图作为单独的根而不是将它们嵌套在架构树中。在最高有用的架构视图上设置 `defaultOpen: true`。较低级别的视图应保持默认值 `false`。

## 编写演练

一个流程图是一个简短的引导式浏览。它包含两到十二个步骤。每个步骤展示一个流程图，指向其中的一个部分，并简要说明它。流程图播放它，读者通过滚动浏览它。

合同将流程图设为可选的。无论如何，为任何非平凡的内容编写一个：超过一个流程图，一个包含多个更改部分的流程图，或任何流程。仅在文档只有一个小流程图，其单个步骤只是重复标题时才跳过它。

目标是三到七个步骤。

流程图是对拉取请求最快的阅读方式。每个步骤是一个更改：添加、更改、删除或移动，按审查者需要的顺序。一个步骤永远不会是流程图的描述。

什么算作一个步骤：行为更改、API更改、架构更改、数据流更改或添加。未更改的部分仅在需要时出现以使其有意义。标题更改是第一步。如果有的话，所有受影响内容的概述是最后一步。

```json
"流程图": {
  "步骤": [
    {
      "id": "四批处理调用",
      "标题": "Postmark 现在每调用获取 500 封邮件",
      "正文": "每个批次一个调用，Postmark 为每封邮件返回结果。",
      "阶段": { "kind": "流程", "流程": "发送管道" },
      "焦点": { "kind": "选择", "消息": ["批处理发送", "批处理结果"] }
    },
    {
      "id": "爆炸半径",
      "标题": "3 个部分添加，2 个删除，跨越 3 个通道",
      "正文": "一个 2000 人的广播以前会向 Postmark 发起 2000 个调用。现在只发起 4 个。",
      "阶段": { "kind": "视图", "视图": "概述" }
    }
  ]
}
```

每个步骤包含：

- `标题`：事物及其发生的变化，最多 48 个字符，使用句子大小写。从更改词构建：添加、删除、替换、现在、移动、拆分。如果一个标题在拉取请求之前可能就是真实的，它就不是更改标题。
- `正文`：标题下的一行，最多 140 个字符，说明更改对行为的影响：现在发生而之前没有发生的事情，或停止发生的事情，以及相关的数字。不是标题的重复陈述，也不是代码的描述。没有正文的标题读作未完成，因此正文是必需的。
- `阶段`：显示哪个流程图。文档可以有多个流程图：其视图（下钻流程图）和其流程（序列流程图）。`{ "kind": "视图", "视图": "概述" }` 显示名为 `概述` 的视图。`{ "kind": "流程", "流程": "发送管道" }` 显示名为 `发送管道` 的流程。省略 `阶段`，步骤使用读者当前所在的流程图。在未指定焦点的情况下打开最宽的视图，以便读者在缩小之前看到整个内容。
- `焦点`：在流程图中要放大什么。`{ "kind": "全部" }`，默认值，表示整个流程图。选择表示“仅这些内容”：通过 ID 命名任何通道、节点、边或流程步骤（消息），相机将放大它们，而其他内容变暗。聚焦步骤更改影响的元素，以便幕布照亮更改。指向两个或三个元素。一个步骤照亮半个流程图就没有说什么。

为聪明的十二岁孩子写每个字：短常用词，每行一个想法，主动语态，按流程图名称命名事物，数字用数字表示。如果一行需要第二遍阅读，就重写它。像“利用”、“协调”、“异步管道”和“扇出”这样的词永远不会出现在步骤中。这在文档是用什么语言编写的都不重要。

同样三个步骤，写得好的和写得不好的。标题首先，然后斜杠后的正文：

| 写这个 | 不要这样写 |
| -------- | -------- |
| Route 现在排队作业而不是发送 / API 调用立即完成。一个工作线程稍后发送邮件。 | Broadcast 扇出移到队列后面 / API 路由现在将广播作业排队进行异步批量处理，而不是内联发送邮件。 |
| Postmark 现在每调用获取 500 封邮件 / 每个批次一个调用而不是每人一个调用。 | 批量发送替换单个发送 / 工作线程利用共享库通过 Postmark 的批量端点以 500 个为一组发送邮件。 |
| processBroadcast 和 sendSingleEmail 删除 / sendBroadcastBulk 为整个批次完成工作。 | 单个发送函数已退役 / sendBroadcastBulk 替代 processBroadcast 和 sendSingleEmail 处理批量发送。 |

将连续的步骤保持在同一阶段上。每个阶段的更改都会让相机飞过画布，因此一个在两个流程图之间交替的游览会花费时间在旅行上。

验证器检查：

- 你命名的每个 ID 都存在于文档中。你命名的流程步骤必须属于阶段显示的流程，因为流程步骤 ID 仅在其自己的流程内部是唯一的。
- `messages` 需要一个显示流程的阶段。当阶段是架构视图时省略它。
- 步骤 ID 在流程图中是唯一的。至少两个步骤，最多十二个。
- 存储的映射永远不会包含流程图。映射描述系统；流程图讲述一个更改的故事。

该字段随合同 0.1.1 到来。一个早于 0.4.0 的 CLI 不知道它，并拒绝整个文档作为虚构的字段，因此使用当前的版本进行验证。

## 流程步骤上的流量样本

流程步骤可以携带 `payload`：它在上面传输的内容。只有画布绘制它，在读者点击步骤时打开的轨道中。SVG 或拉取请求评论中的任何内容都不会改变。当文档将要发送到画布（步骤 4，`canvas push`）时编写它，否则省略它。参考文档上的六个有效载荷增加了其长度的一半，因此这不是一个默认填充的字段。

在画布文档中，将其添加到移动数据的步骤：请求正文、作业记录、查询、结果。将其从仅发出信号（如没有附加内容的触发器）的步骤中省略。

```json
{
  "id": "batch-post",
  "from": "send-broadcast-bulk",
  "to": "postmark",
  "label": "POST /email/batch",
  "kind": "同步",
  "delta": "添加",
  "repeat": 4,
  "payload": {
    "请求": {
      "类型": "EmailBatch[500]",
      "形状": "Email[]  // 最大 500\nEmail = { From: string; To: string; Subject: string; HtmlBody: string; MessageStream: \"broadcast\"; Metadata: { campaignId: string; batchId: string } }",
      "样本": [
        {
          "From": "news@example.com",
          "To": "ada@example.com",
          "Subject": "批量问题已修复",
          "HtmlBody": "<!doctype html><html><body>…",
          "MessageStream": "broadcast",
          "Metadata": { "campaignId": "cmp_0001", "batchId": "b_0001" }
        }
      ],
      "之前": [
        {
          "From": "news@example.com",
          "To": "ada@example.com",
          "Subject": "批量问题已修复",
          "HtmlBody": "<!doctype html><html><body>…",
          "Metadata": { "campaignId": "cmp_0001" }
        }
      ],
      "来源": { "路径": "tests/fixtures/postmark-batch.json" }
    },
    "响应": {
      "类型": "BatchResult[500]",
      "形状": "SendResult[]  // 每个Email一个，顺序相同",
      "样本": [{ "ErrorCode": 0, "Message": "OK", "To": "ada@example.com", "MessageID": "b7fa5c1e-…" }]
    }
  }
}
```

有效载荷有一个 `请求` 端，一个 `响应` 端，或两个端。每个端包含：

- `类型`：代码读者会识别的名称。当步骤携带集合时，将其中的数量包含在内：`EmailBatch[500]`，而不是 `EmailBatch`。对于不携带任何内容的端，如“火并忘记”调用的答案，编写 `{ "类型": "void" }`。
- `形状`：文本类型签名，从代码自己的类型获取。最多 2048 字节。
- `样本`：更改后的一个示例实例，以内联 JSON 编写。它是一个 JSON 值，而不是 JSON 字符串：`"样本": [{ "To": "ada@example.com" }]`，永远不会是 `"样本": "[{\"To\": ...}]"`。这里不能是字符串。每个键一次，任何数组中的一个元素，长字符串用省略号截断。最多 8 层深，序列化后最多 4096 字节。解析器拒绝超过任一限制的样本，而不是修剪它。
- `之前`：更改前的相同示例，当它不同时。与 `样本` 相同的规则，并且它需要一个 `样本` 才能与它不同。
- `来源`：形状和样本来自的 fixture 或类型，作为文件引用。它成为永久链接。

使用占位符值：`ada@example.com`，`cmp_0001`。永远不会从 fixture 中复制可能属于真实人物或解锁内容的值，即使在测试数据中也是如此。

不要编写 `changedPaths`。`before` 和 `sample` 之间的不同路径在文档存储时确定。你编写的列表被丢弃。

该字段随合同 0.2.0 到来。在它之前构建的 CLI 拒绝整个文档作为虚构的字段，因此使用当前的版本进行验证。

## 验证器会捕获什么

在编写之前阅读 `references/graph-document.md`。几乎一切都归因于四个失败：

| 代码                         | 你做了什么                                                         |
| ---------------------------- | -------------------------------------------------------------------- |
| `BROKEN_REFERENCE`           | 边缘、流程步骤、视图或流程图步骤命名了你从未声明的 ID             |
| `INVALID_DOCUMENT`           | 虚构的字段；模式是严格的，未知的键会被拒绝                         |
| `DUPLICATE_ID`               | 两个节点、边缘或视图共享一个 ID                                  |
| `UNSUPPORTED_SCHEMA_VERSION` | `schemaVersion` 不是安装的合同版本                              |

七个规则无法用 JSON 模式表达，并且只能由解析器检查，因此结构化输出本身并不能使文档有效：引用完整性、行范围在它开始之前结束、一个 `self` 消息的端点不一致、一个补丁的两个提交相同、比渲染清单能描述的更多视图、流程图步骤聚焦其阶段上不绘制的流程步骤，以及超出深度或字节限制的样本流量。始终验证。

## 修复映射而不是编写

当有人说不正确的流程图（节点命名错误、文件夹不应在它上面、某物放在了错误的通道中）时，不要编辑生成的文档。它在每次运行时都会重新生成。将更正写入 `.github/pr-lens.yml`，这是一个每次应用时都会覆盖新鲜推理的叠加层：

```yaml
schemaVersion: 0.2.0
map:
  重命名:
    - match: functions/src/broadcast/sendBroadcastBulk.ts
      to: Broadcast 发送者
  排除:
    - "**/*.test.ts"
  通道:
    - match: packages/broadcast-lib/**
      通道: functions
```

`references/config.md` 包含完整格式和配方。使用相同的方式验证它：`npx @coldtea/pr-lens-cli@latest validate .github/pr-lens.yml`。

一个以 `id:` 开头的 `match` 精确地指向一个节点；任何其他内容都是匹配节点文件路径的模式。优先使用模式，因为它在下次运行命名节点时仍然保持有效。一个通道固定可能命名文档从未声明的通道：创建该乐队，并获取其标签的 ID，因此给它一个读者会想要看到的 ID。

`pr-lens render` 在更正未匹配任何内容时说明，这就是一个配置因为命名的文件已移动或已删除而漂移，而不是安静地什么也不做而变得可见的方式。

## 随此技能一起提供的内容

你需要的所有内容都在这一页旁边。这里没有要求你先安装任何包。

|                                 |                                                                                    |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `references/graph-document.md`  | 文档，字段逐字段：枚举、限制，以及文档实际出错的地方                         |
| `references/config.md`          | `.github/pr-lens.yml`，更正叠加层，完整格式                                     |
| `references/example.graph.json` | 一个完整的、有效的文档，供阅读和复制形状 |

相同的文档作为 `postmark-refactor.graph.json` 随 `@coldtea/pr-lens-schema` 提供，验证器强制的 JSON 模式发布在 `https://unpkg.com/@coldtea/pr-lens-schema/json-schema/graph-doc.schema.json`。两者都不是你需要获取以编写文档的内容。
