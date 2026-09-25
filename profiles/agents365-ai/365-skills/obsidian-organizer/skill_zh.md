# Obsidian Organizer

通过（1）将新笔记归档到最合适的文件夹中，以及（2）审核/重组现有结构，随着时间的推移保持 Obsidian 库的整洁。这两种模式都依赖于一个共享的理念：一个存储在**库内部**的纯 Markdown 地图，显示“什么东西放在哪里”，这样它就不会与现实脱节。

这项技能驱动着 `obsidian` CLI（来自独立的 `obsidian-cli` 技能），它将与**正在运行的 Obsidian 桌面应用程序**进行通信。应用程序必须处于打开状态。如果命令因连接/库错误而失败，请提示用户打开 Obsidian，而不是猜测。

## 地图为何存储在库中（首先阅读此部分）

通过重新列出约 650 个文件夹来为新笔记决定文件夹是昂贵的，并且猜测会逐渐偏离。将文件夹分类结构复制到 Claude 的私有内存中会创建一个更严重的问题：一个过时的副本，它默默地与真实库不一致。

解决方法是一个文件，`00_Index/Folder_Map.md`，将其提交到库本身。它是归档决策的唯一真实来源。在归档或重组之前，使用一次廉价的调用来读取它——**不要**重新运行完整的 `obsidian folders` 遍历，除非地图丢失或用户要求您重建它。

```bash
obsidian read path="00_Index/Folder_Map.md"
```

它被故意设计为纯 Markdown（标题 + 项目符号，没有必需的前置内容），以便您和人类可以手动追加新类别。当您创建一个新的文件夹/类别时，向此文件添加一行，以便下次归档决策时记住它。

如果地图不存在（已删除或全新的库），请**从实时库**中重建它，而不是从此技能中存储的副本中重建——捆绑的副本会与现实脱节，这正是此文件存在要防止的整个失败。使用 `obsidian vault="MyVault" folders`（以及 `folders folder=...` 用于深度）列出真实结构，草拟一个按顶级 PARA 文件夹分组的纯 Markdown 地图，每个文件夹附带一个简短的“这里放什么”注释以及一个归档规则，然后与用户确认分组，然后创建它：
`obsidian vault="MyVault" create path="00_Index/Folder_Map.md" content="..."`。

## 库目标

上面的 `MyVault` 是一个占位符——在所有地方替换为用户的实际库名称。如果用户有多个库，请在每个命令中明确指定目标库，以防止“最近关注的库”默认值误归档笔记：

```bash
obsidian vault="MyVault" read path="00_Index/Folder_Map.md"
```

`vault=` 必须是**第一个**参数。这是此技能中唯一的库特定值——其他所有内容都来自库自身的 `Folder_Map.md`。

## 一个严格的安全规则：永远不要使用原始 Shell 触摸库文件

当您移动或重命名文件时，**始终**使用 CLI 的 `move` / `rename` 命令。这些通过 Obsidian 的 API 进行操作，因此 Obsidian 的内置“自动更新内部链接”行为会重写库中每个 wikilink 和反向链接，以跟随移动的文件。在库路径内部对原始 `mv`、`rm`、`rmdir` 或 `find -delete` 会跳过此修复，并默默地留下指向旧位置的断开链接。

因此，对于库目录下的任何内容：

- 移动/重命名 → `obsidian move ...` 或 `obsidian rename ...`
- 删除 → `obsidian delete ...`（除非 `permanent`，否则会发送到回收站）
- **永远**不要在库内部路径上使用 Bash `mv` / `rm` / `rmdir` / `find -delete`。

使用非修改工具读取文件的字节是安全的；修改库文件仅限于 CLI。

---

## 模式 1 — 归档笔记

目标：给定一个笔记（一个现有路径，或一个您即将编写的标题 + 内容），将其放入最合适的单个文件夹中。

1. **读取地图一次**：`obsidian vault="MyVault" read path="00_Index/Folder_Map.md"`。
2. **匹配**笔记的主题到使用地图归档规则的目的地。优先考虑现有的特定子文件夹而不是通用文件夹（例如，一个 Seurat 教程应该放在 `03_Research_Knowledge/Bioinformatics/seurat/`，而不是一个通用的桶）。
3. **对最佳匹配采取行动**：
   - *存在一个明确的匹配文件夹* → 放置在那里。
     - 新笔记：`obsidian vault="MyVault" create path="03_Research_Knowledge/Bioinformatics/seurat/My Note.md" content="..." silent`
     - 现有笔记重新定位：`obsidian vault="MyVault" move path="00_Inbox/My Note.md" to="03_Research_Knowledge/Bioinformatics/seurat"`（`to` 可以是文件夹或完整路径）。
   - *存在一个大致但不完美的匹配*（例如，一个没有专用子文件夹的工具）→ 使用地图的通用约定（例如 `Bioinformatics/misc/`），并告诉用户它被放置在哪里。
   - *没有类别很好地匹配* → **在发明文件夹之前停止并询问**用户。建议一个名称和位置；不要默默地创建新的分类法。
4. **记住新类别**。当用户批准一个新文件夹时，在 `00_Index/Folder_Map.md` 的正确部分追加一行描述它（`obsidian append path="00_Index/Folder_Map.md" content="..."`），以便未来的归档决策知道它。
5. 简要报告最终路径。

关于 CLI 的注释：`create` 会按需创建中间文件夹；添加 `silent` 以免它通过打开笔记来窃取焦点。`move` 的 `to` 接受目标文件夹或完整路径；使用 `rename name="New Title"` 在原地更改标题。

---

## 模式 2 — 审核 / 重组

目标：给定一个范围（一个文件夹路径、最近的收件箱笔记，或一个明确的请求，如“清理细胞聊天笔记”），找到问题，**提出计划，获取明确确认，然后执行**。永远不要在沉默中批量移动、合并或删除。

### 第 1 步 — 为范围收集信号

首先读取地图以获取上下文，然后使用结构命令。在命令支持的情况下，将每个列表的范围限制到相关的文件夹。

- `obsidian vault="MyVault" files folder="<scope>"` — 清单 + 发现近似重复的标题（例如 "CellChat analysis" vs "CellChat Analysis v2"）。
- `obsidian vault="MyVault" orphans` — 没有入站链接的笔记（没有任何东西链接到它们；候选归档/合并/存档）。
- `obsidian vault="MyVault" deadends` — 没有出站链接的笔记（通常是草稿或从未开发的捕获）。
- `obsidian vault="MyVault" search:context query="<topic>" path="<scope>"` — 在提出合并之前，比较疑似近似重复的内容。
- `obsidian vault="MyVault" backlinks path="<file>"` — 在合并或删除笔记之前，查看它链接到什么，以免断开引用。

没有专门的“重复”命令；通过比较 `files` 的标题并使用 `search:context` / `read` 进行确认来检测重复。

### 第 2 步 — 提出计划（并等待）

提出一个具体的、分项的计划并停止等待确认。按操作分组：

```
Bioinformatics/cellchat/（7 个笔记）的提议重组：

合并
- "CellChat analysis.md" + "CellChat analysis (1).md" → 保留 "CellChat analysis.md"，合并来自重复的唯一内容，然后删除重复项。

移动
- "Spatial CellChat.md" → Single_Cell/Spatial_Omics/（主题是空间，而不是工具）

重命名
- "untitled cellchat.md" → "CellChat LR 数据库笔记.md"

无变化：3 个笔记看起来很好。

继续？我不会在您确认之前移动/合并/删除任何东西。
```

保持计划对不确定性诚实——标记猜测，以便用户可以否决它们。

### 第 3 步 — 在“是”之后才执行

在确认后，通过 CLI 按保持链接完整的顺序运行移动/重命名/删除（通常：首先合并内容，然后删除空白的重复项；如果两者都适用，则移动在重命名之前）。使用 `move`、`rename`、`delete`、`append`/`read` 进行合并——永远不要使用原始 Shell。报告发生了什么变化，并将您创建的任何新文件夹/类别追加到 `00_Index/Folder_Map.md`。

### 已知的持续重组候选者

如果库的 `Folder_Map.md` 指出了已知的问题区域（遗留文件夹与较新的文件夹重叠、一个积累了近似重复标题的子文件夹等），在它们处于范围内时显示它们——但仍然在触摸任何东西之前提出并确认。

---

## 命令快速参考

| 需要 | 命令 |
| --- | --- |
| 读取地图 | `obsidian vault="MyVault" read path="00_Index/Folder_Map.md"` |
| 创建/归档一个新笔记 | `obsidian vault="MyVault" create path="Folder/Note.md" content="..." silent` |
| 移动/重新定位一个笔记 | `obsidian vault="MyVault" move path="Old/Note.md" to="New/Folder"` |
| 原地重命名 | `obsidian vault="MyVault" rename path="Folder/Note.md" name="New Title"` |
| 删除（发送到回收站） | `obsidian vault="MyVault" delete path="Folder/Note.md"` |
| 列出文件夹中的文件 | `obsidian vault="MyVault" files folder="<scope>"` |
| 或有 / 死端 | `obsidian vault="MyVault" orphans` · `... deadends` |
| 带上下文的搜索 | `obsidian vault="MyVault" search:context query="..." path="<scope>"` |
| 笔记的回链接 | `obsidian vault="MyVault" backlinks path="Folder/Note.md"` |
| 追加到地图 | `obsidian vault="MyVault" append path="00_Index/Folder_Map.md" content="- ..."` |

运行 `obsidian help <command>` 以确认确切参数——CLI 是真实依据。
