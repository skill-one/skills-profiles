# PR Lens

PR Lens 将代码绘制为视觉丰富的动画图表。它可以表示差异、架构、数据流等。

差异或代码表示为一个 JSON 文档（轨道、节点、边、有序流），并将其渲染为动画 SVG。

## 操作手册

在编写之前，确定图表的放置位置：画布或 SVG 和拉取请求评论。只有画布绘制 `payload`，即在流程步骤上的示例请求和响应。迟来的决定需要再次通过步骤 2 和 3。

1. **阅读差异。** 当要求表示代码更改时：`git diff --find-renames <base>...<head>`。基准是合并基准，而不是基准分支的尖端。

   如果不是表示代码差异，则阅读要视觉表示的代码

2. **编写文档** 到 `.pr-lens/graph.json`，遵循 `references/graph-document.md`。`references/example.graph.json` 是一个有效的参考，包含三个轨道、所有四个 delta 状态、一个英雄边、一个七步流程、一个嵌套的向下钻取树和六步演练。在编写第一个之前阅读它。它比阅读参考更快。如果它将发送到画布，则在编写时为每个流程步骤（`messages`）移动数据赋予 `payload`。下面的“流程步骤上的示例流量”说明了放入的内容。只有流程步骤携带一个。流程需要 `data-flow` 透镜，因此架构视图不绘制任何内容。

3. **验证并修复**

   ```bash
   npx @coldtea/pr-lens-cli@latest validate .pr-lens/graph.json
   ```

   修复每个失败并再次运行。不要渲染无效文档；不要通过删除它命名的元素来“绕过”失败。

4. **渲染。**

   ```bash
   npx @coldtea/pr-lens-cli@latest render .pr-lens/graph.json --theme light
   ```

   默认情况下渲染浅色，除非用户请求另一个主题。SVG、清单和 `drawn.graph.json` 位于 `.pr-lens/` 中，CLI 会将其添加到仓库的 .gitignore 中。不要提交任何内容。这些文件将根据差异重新构建，以便任何人再次需要它们。每个 SVG 都以其视图、主题和内容哈希命名；`manifest.json` 按透镜和视图列出它们，因此从那里或从目录中读取名称。

   如果用户要求图表、解释或架构的图片，则将其放在画布上并返回链接：

   ```bash
   npx @coldtea/pr-lens-cli@latest canvas push
   ```

   这会推送 `.pr-lens/drawn.graph.json` 并打印三个链接。给用户视图链接，`https://prlens.dev/c/{id}`：那是图表，全屏，所有视图在一个页面上，并且无需登录即可打开。编辑链接，以 `#w=…` 结尾，允许其持有者推送画布，因此除非他们要求，否则不要将其包含在回复中，并且永远不要将其粘贴到任何公共位置。嵌入链接将顶层视图作为 SVG 用于 README。

   再次推送相同文件会更新相同的画布，因此后续操作，如“重命名该节点”或“添加队列”，是：编辑文档、验证、渲染、推送。链接保持不变。如果推送失败，请告知他们 SVG 的位置以及哪个是顶层视图。

5. **附加，当有要附加的拉取请求时。** 这意味着用户要求你打开一个 PR，要求在现有的 PR 上提供一个图表，或者你作为所做的更改的一部分打开一个 PR。否则跳过此步骤。

   GitHub CLI 将图表与拉取请求一起上传。使用 Markdown 图像指向本地文件编写正文，然后将相同的路径传递给 `--attach`。`gh` 重新编写参考以指向上传的资产并保留您编写的替代文本：

   ```markdown
   将批量发送从每个接收者的触发器移至批量端点。

   ![此更改后的架构：队列路由、新的批量发送者和已退役的每个接收者路径](.pr-lens/overview-light-4f9bd6c1.svg)
   ```

   ```bash
   gh pr create --title "批量广播发送" --body-file .pr-lens/body.md \
     --attach .pr-lens/overview-light-4f9bd6c1.svg
   ```

   在已存在的拉取请求中，使用相同的两个标志 `gh pr edit <number>` 将图表放入描述中，`gh pr comment <number>` 将其放入评论中。重复 `--attach` 以附加正文引用的每个图表。

   gh 有三个规则：
   - 参考必须是 Markdown 图像，`![alt](path)`。HTML `<img>` 或 `<picture>` 保持原样，文件附加在正文底部。
   - 替代文本是图像无法显示的读者的标题。用一句话说明图表显示的内容。
   - `--attach` 在 GitHub CLI 2.99 中到达。在编写正文之前使用 `gh --version` 进行检查。

   附加审阅者需要的视图，并将其余视图保留在 `.pr-lens/` 中：首先添加顶层的架构视图，如果更改影响用户、外部系统或系统边界，则使用容器视图。仅当受影响的容器的内部重要时才添加组件子视图。默认情况下不要添加代码级视图。

   每个子视图向下移动一个级别，并覆盖更窄的范围。跳过空的、重复的或推测性的级别，并且不要仅凭文件夹名称推断架构。两个视图不应包含基本相同的节点和边。保留说明影响范围的未更改的直接邻居。

   将数据流视图保留为单独的根，而不是在架构树中嵌套它们。在最高有用的架构视图上设置 `defaultOpen: true`。较低级别的视图通常应保持默认值 `false`。

## 编写演练

演练是图表的简短引导式游览。它有 2 到 12 步。每一步显示一个图表，指向其中的一个部分，并对此说几句话。画布播放它，读者滚动浏览它。

合同将演练设为可选的。无论如何为非平凡内容编写演练：多个图表、具有多个更改部分的图表或任何流程。仅在文档是一个小图表，其单个步骤将重复标题时才跳过它。

目标是 3 到 7 步。

演练是拉取请求的最快阅读方式。每一步都是一个更改：添加、更改、删除或移动，按审阅者需要的顺序。步骤永远不会是图表的描述。

什么算作一个步骤：行为更改、API 更改、架构更改、数据流更改或添加。未更改的部分仅在需要使步骤有意义时出现。标题更改是第一步。如果有一个涵盖所有受影响内容的概述，则它是最后一步。

```json
"walkthrough": {
  "steps": [
    {
      "id": "four-batch-calls",
      "heading": "Postmark 现在每调用获取 500 封邮件",
      "body": "每个批量一个调用，Postmark 对每封消息返回一个结果。",
      "stage": { "kind": "flow", "flow": "send-pipeline" },
      "focus": { "kind": "selection", "messages": ["batch-post", "batch-results"] }
    },
    {
      "id": "blast-radius",
      "heading": "3 个轨道中添加了 4 个部分，删除了 2 个部分",
      "body": "以前的 2,000 人广播会向 Postmark 发出 2,000 个调用。现在它会发出 4 个。",
      "stage": { "kind": "view", "view": "overview" }
    }
  ]
}
```

每一步都有：

- `heading`：事物及其发生的变化，最多 48 个字符，使用句子大小写。使用更改词：添加、删除、替换、现在、移动、拆分。如果标题在拉取请求之前可能就是真实的，则它不是更改标题。
- `body`：标题下的一行，最多 140 个字符，说明更改对行为的影响：现在发生而之前没有发生的事情，或停止发生的事情，并在需要时提供数字。不是标题的重新陈述，也不是代码的描述。没有身体的标题读起来不完整，因此需要身体。
- `stage`：要显示的图表。文档可以有几个图表：其视图（向下钻取图表）和其流程（序列图表）。`{ "kind": "view", "view": "overview" }` 显示名为 `overview` 的视图。`{ "kind": "flow", "flow": "send-pipeline" }` 显示名为 `send-pipeline` 的流程。省略 `stage`，步骤将使用读者当前的图表。在最宽的视图上打开，不保留焦点，以便读者先看到整体内容。
- `focus`：在图表中要放大什么。`{ "kind": "all" }`，默认值，表示整个图表。选择表示“仅这些事物”：通过 id 命名任何轨道、节点、边或流程步骤（`messages`），相机将缩放到它们，而其他所有内容都会变暗。聚焦步骤更改影响的元素，以便灯光照亮更改。指向两到三个元素。一个步骤照亮半个图表就没有说什么。

为聪明的小学生编写每个词：短常用词，每行一个想法，主动语态，像图表命名它们一样命名事物，数字用数字表示。如果一行需要第二次阅读，请重写它。像 leverages、orchestrates、asynchronous pipeline 和 fan-out 这样的词永远不会出现在步骤中。这在文档用任何语言编写时都适用。

三个相同的步骤，写得好的和写得不好的。标题首先，然后斜杠后的正文：

| 写这个 | 不要这样写 |
| -------- | -------- |
| 路由现在将作业排队而不是发送 / API 调用立即完成。工作线程稍后发送邮件。 | 广播 fan-out 移到队列后面 / API 路由现在将广播作业入队以进行异步批量处理，而不是内联发送电子邮件。 |
| Postmark 现在每调用获取 500 封邮件 / 每个批量一个调用，而不是每个个人一个调用。 | 批量发送取代了单独发送 / 工作线程利用共享库通过 Postmark 的批量端点发送 500 个电子邮件。 |
| processBroadcast 和 sendSingleEmail 删除 / sendBroadcastBulk 为整个批量执行他们的工作。 | 单独发送函数已退役 / sendBroadcastBulk 取代 processBroadcast 和 sendSingleEmail 以处理批量发送。 |

将连续的步骤放在同一阶段上。每次更改阶段都会让相机飞过画布，因此交替在两个图表之间切换的游览会花费时间在旅行上。

验证器检查：

- 您命名的每个 id 都存在于文档中。您命名的流程步骤必须属于阶段显示的流程，因为流程步骤 id 仅在其自己的流程内部唯一。
- `messages` 需要一个显示流程的阶段。当阶段是架构视图时，请省略它。
- 步骤 id 在演练中是唯一的。至少两个步骤，最多十二个步骤。
- 存储的映射永远不会携带演练。映射描述系统；演练讲述一个更改的故事。

该字段在合同 0.1.1 中到达。比 0.4.0 更旧的 CLI 不认识它，并将整个文档作为虚构的字段拒绝，因此使用当前的验证器进行验证。

## 流程步骤上的示例流量

流程步骤可以携带一个 `payload`：它在上面传输的内容。只有画布绘制它，在读者点击步骤时打开的轨道中绘制。SVG 或拉取请求评论中的任何内容都不会改变。当文档发送到画布（步骤 4，`canvas push`）时编写它，否则省略它。参考文档上的六个有效负载增加了其长度的一半，因此这不是一个默认填充的字段。

在画布文档中，将有效负载添加到移动数据的步骤：请求正文、作业记录、查询、结果。省略仅发出信号（如没有附加的触发器）的步骤。

```json
{
  "id": "batch-post",
  "from": "send-broadcast-bulk",
  "to": "postmark",
  "label": "POST /email/batch",
  "kind": "sync",
  "delta": "added",
  "repeat": 4,
  "payload": {
    "request": {
      "type": "EmailBatch[500]",
      "shape": "Email[]  // max 500\nEmail = { From: string; To: string; Subject: string; HtmlBody: string; MessageStream: \"broadcast\"; Metadata: { campaignId: string; batchId: string } }",
      "sample": [
        {
          "From": "news@example.com",
          "To": "ada@example.com",
          "Subject": "此更改后的架构：队列路由、新的批量发送者和已退役的每个接收者路径",
          "HtmlBody": "<!doctype html><html><body>…",
          "MessageStream": "broadcast",
          "Metadata": { "campaignId": "cmp_0001", "batchId": "b_0001" }
        }
      ],
      "before": [
        {
          "From": "news@example.com",
          "To": "ada@example.com",
          "Subject": "此更改后的架构：队列路由、新的批量发送者和已退役的每个接收者路径",
          "HtmlBody": "<!doctype html><html><body>…",
          "Metadata": { "campaignId": "cmp_0001" }
        }
      ],
      "source": { "path": "tests/fixtures/postmark-batch.json" }
    },
    "response": {
      "type": "BatchResult[500]",
      "shape": "SendResult[]  // one per Email, same order",
      "sample": [{ "ErrorCode": 0, "Message": "OK", "To": "ada@example.com", "MessageID": "b7fa5c1e-…" }]
    }
  }
}
```

有效负载有一个 `request` 端，一个 `response` 端，或两个端。每个端都有：

- `type`：代码读者会识别的名称。当步骤携带集合时，将其数量放在其中：`EmailBatch[500]`，而不是 `EmailBatch`。为不携带任何内容的端编写 `{ "type": "void" }`，例如对火并忘记调用的回答。
- `shape`：文本类型签名，从代码自己的类型获取。最多 2048 字节。
- `sample`：更改后的一个示例实例，内联作为 JSON 编写。它是一个 JSON 值，而不是 JSON 字符串：`"sample": [{ "To": "ada@example.com" }]`，永远不要 `"sample": "[{\"To\": ...}]"`。这里字符串会被拒绝。每个键一次，任何数组中的一个元素，长字符串用省略号切割。最多 8 层深和 4096 字节一次序列化。解析器拒绝超过任何限制的样本，而不是修剪它。
- `before`：与更改前相同的示例，当它不同时。与 `sample` 相同的规则，并且它需要一个 `sample` 才能与它不同。
- `source`：形状和样本来自的 fixture 或类型，作为文件引用。它成为永久链接。

使用占位符值：`ada@example.com`，`cmp_0001`。永远不会从 fixture 中复制值，即使它可能属于真人或解锁内容，即使在测试数据中也是如此。

不要编写 `changedPaths`。`before` 和 `sample` 之间的差异路径在存储文档时确定。您编写的列表被丢弃。

该字段在合同 0.2.0 中到达。在它之前构建的 CLI 会将整个文档作为虚构的字段拒绝，因此使用当前的验证器进行验证。

## 验证器会捕获什么

在编写之前阅读 `references/graph-document.md`。几乎一切都归因于四个失败：

| 代码                         | 您做了什么                                                         |
| ---------------------------- | -------------------------------------------------------------------- |
| `BROKEN_REFERENCE`           | 边缘、流程步骤、视图或演练步骤命名了您从未声明的 id              |
| `INVALID_DOCUMENT`           | 虚构的字段；模式是严格的，未知的键会被拒绝                         |
| `DUPLICATE_ID`               | 两个节点、边缘或视图共享一个 id                                  |
| `UNSUPPORTED_SCHEMA_VERSION` | `schemaVersion` 不是安装的合同版本                                |

七个规则无法用 JSON 模式表达，并且仅由解析器检查，因此仅靠结构化输出并不能使文档有效：引用完整性、行范围在它开始之前结束、`self` 消息的端点不一致、补丁的两个提交相同、比渲染清单描述的视图更多、演练步骤聚焦其阶段上不绘制的流程步骤，以及超出深度或字节限制的样本流量。始终验证。

## 修复映射而不是编写

当有人说我绘制的图表是错误的（节点命名错误、文件夹不应在它上面、某物位于错误的轨道中）时，不要编辑生成的文档。它在每次运行时都会重新生成。将更正写入 `.github/pr-lens.yml`，这是一个每次运行时应用于新鲜推理的覆盖层：

```yaml
schemaVersion: 0.2.0
map:
  rename:
    - match: functions/src/broadcast/sendBroadcastBulk.ts
      to: Broadcast sender
  exclude:
    - "**/*.test.ts"
  lane:
    - match: packages/broadcast-lib/**
      lane: functions
```

`references/config.md` 包含完整格式和配方。以相同的方式验证它：`npx @coldtea/pr-lens-cli@latest validate .github/pr-lens.yml`。

`match` 以 `id:` 开头精确地针对一个节点；否则是针对节点文件路径的路径通配符。优先使用通配符，因为它在下次运行时命名节点时仍然有效。一个车道固定可能命名文档从未声明的车道：创建乐队，并获取其标签 id，因此给它一个读者想要看到的 id。

`pr-lens render` 在匹配不到任何内容时说明，这是由于文件已漂移，因为它命名的文件已移动或已删除，而不是默默不做任何事情。

## 随附此技能的物品

您需要的一切都在此页旁边。这里没有要求您先安装任何软件包。

|                                 |                                                                                    |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `references/graph-document.md`  | 文档，按字段：枚举、限制和文档实际出错的地方                               |
| `references/config.md`          | `.github/pr-lens.yml`，更正覆盖层，完整格式                                     |
| `references/example.graph.json` | 一个完整的文档，可以验证、阅读和复制其形状                                 |

相同的文档作为 `postmark-refactor.graph.json` 随附在 `@coldtea/pr-lens-schema` 中，验证器强制执行的 JSON 模式发布在 `https://unpkg.com/@coldtea/pr-lens-schema/json-schema/graph-doc.schema.json`。您不需要获取任何内容来编写文档。
