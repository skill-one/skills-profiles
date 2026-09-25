# MSW 包 — 官方预构建目录

[`MSW-Git/MSWPackages`](https://github.com/MSW-Git/MSWPackages) 是 MSW 官方的一级仓库，包含预构建的功能包。在从零开始编写任何标准游戏功能之前，**请先查看此目录** — 如果存在匹配的包，建议集成而不是零基础实现。

这个技能是一个薄索引。每个包的详细信息（README、源代码、集成步骤）会**按需从 GitHub 获取**，而不是在此处镜像，因此目录会自动保持最新。

---

## 决策流程

```
用户请求功能 X
        │
        ▼
将 X 与下方功能→包表进行匹配
        │
   ┌────┴─────┐
   │ 匹配    │ 未匹配
   ▼          ▼
范围优先检查      继续正常 MSW 编写
(见下文部分):   (msw-scripting,
系统 vs UI 仅?     msw-search 等)
        │
   ┌────┴───────────┐
   │ 系统         │ UI 仅
   ▼                ▼
获取包    路由到 msw-ui-system
README           (+ references/templates/, 跳过此技能的其余部分)
        │
        ▼
向用户总结
"找到 <包>. README 说明: <摘要>.
 集成此包，或从零构建?"
        │
   ┌────┴─────┐
   │          │
   ▼          ▼
集成    从零构建
        │
        ▼
运行集成工作流 (下方)
```

**默认立场**: 集成前询问用户。未经确认不要自动安装 — 包可能与应用程序中现有的 UUID、sprite RUID 或命名约定冲突。

---

## 功能→包映射

当用户请求中提到以下功能（韩语或英语）时，查找匹配的包并首先获取其 README。

| 功能域 | 包 | GitHub 路径 |
|---|---|---|
| Toast / 通知 / 横幅 | `maplestory-toast-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/maplestory-toast-package) |
| 排名 / 排行榜 / 计分板 (基本) | `ranking-basic-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/ranking-basic-package) |
| 排名 / 排行榜 (高级 — 多计分板、赛季) | `ranking-advanced-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/ranking-advanced-package) |
| 背包 / 物品包 / 装备 | `inventory-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/inventory-package) |
| 商店 / 购物点 / 购买 | `shop-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/shop-package) |
| 世界商店 / 高级商店 | `worldshop-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/worldshop-package) |
| 邮件 / 邮箱 | `mail-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/mail-package) |
| 任务 / 成就 / 使命 | `quest-achievement-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/quest-achievement-package) |
| 对话 / NPC 对话 (打字机风格) | `dialog-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/dialog-package) |
| 键绑定 / 虚拟按钮 | `key-binding-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/key-binding-package) |
| 游戏事件广播 / 发布订阅 | `game-event-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/game-event-package) |
| 玩家数据 / 保存 / 个人资料 | `player-data-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/player-data-package) |
| 收藏 / 画廊 / 图鉴 | `collections-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/collections-package) |
| 命令 / 聊天命令 | `command-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/command-package) |
| 虚拟滚动列表 / 大列表 | `recyclescrollview-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/recyclescrollview-package) |
| 掉落表 / 掉落概率 | `droptable-resolver-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/droptable-resolver-package) |
| 全局配置 / 共享设置 | `global-config-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/global-config-package) |
| GM / 系统公告 | `gm-message-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/gm-message-package) |
| 游戏资源 (货币、能量、可补充) | `resource-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/resource-package) |
| UI 组件和预制模型 | `ui-component-package` | [链接](https://github.com/MSW-Git/MSWPackages/tree/main/ui-component-package) |

如果多个包可能匹配（例如 "排名" → 基本 vs 高级），获取两个 README 并让用户根据比较结果选择。

---

## 范围优先路由 (UI vs 系统)

当请求匹配目录关键字但不确定用户是否需要**完整系统**（数据 + 逻辑 + UI）或**仅 UI 屏幕**时，在获取包文件之前问一个简短的问题。使用下方表格中的匹配行。

| 请求关键字 | 要询问的问题 |
|---|---|
| 排名 / 排行榜 | "您是否需要分数保存和排名计算，还是只需要排行榜屏幕？" |
| 背包 / 包 | "您是否需要添加/移除物品逻辑，还是只需要槽位屏幕？" |
| 商店 / 购物点 | "您是否需要货币扣减和购买处理，还是只需要商店屏幕？" |
| 邮件 / 邮箱 | "您是否需要发送/接收逻辑，还是只需要邮箱屏幕？" |
| 任务 / 成就 | "您是否需要进度跟踪和奖励，还是只需要任务列表屏幕？" |
| Toast / 通知 | "您是否需要队列/计时系统，还是只需要消息弹窗？" |
| 对话 / NPC 对话 | "您是否需要分支对话和状态，还是只需要对话窗口？" |
| 收藏 / 图鉴 | "您是否需要收藏状态和进度跟踪，还是只需要图鉴屏幕？" |
| 玩家数据 / 保存 | "您是否需要持久化和加载/保存流程，还是只需要个人资料屏幕？" |
| 其他 / 不明确 | "您需要完整功能，还是只需要 UI 屏幕？" |

### 路由规则

将用户的回答映射到目的地：

| 用户说... | 路由到 |
|---|---|
| "功能", "系统", "逻辑", "保存", "计算", "处理" | **保持在此 (`msw-packages`)** — 继续到 Fetch 协议下方 |
| "屏幕", "UI", "查看", "视觉", "仅布局", "仅显示" | **`msw-ui-system` 技能** (+ `references/templates/`) — 选择一个样式模板，然后通过 UI 构建器构建 |
| 低级问题 (锚点、组件属性、枚举) | **`msw-ui-system` 技能** — 直接通过 [`references/component-api.md`](../msw-ui-system/references/component-api.md) (包括 §Enums) / [`ui-fundamentals.md`](../msw-ui-system/references/ui-fundamentals.md) 回答，无需获取 |

### 跳过问题的情况

当用户的请求已经明确时，跳过范围优先问题并直接路由：

- "从零开始" / "仅 UI" / "仅屏幕" → `msw-ui-system` 技能 (+ `references/templates/`)
- "完整系统" / "带后端" / "带数据" / "保存分数" → 保持 `msw-packages`
- 纯低级 UI 问题（例如 "如何设置锚点？"）→ `msw-ui-system` 技能

仅在关键字匹配目录包且范围确实模糊时才提问。

---

## Fetch 协议

当识别出候选包时：

### 1. 首先获取 README (始终)

```
https://raw.githubusercontent.com/MSW-Git/MSWPackages/main/<package-name>/README.md
```

使用 `WebFetch` 拉取此内容。在进一步操作前，向用户总结公共 API 和用例。

### 2. 文件树 (当集成可能时)

使用 GitHub 树 API 并 grep 包路径：

```
https://api.github.com/repos/MSW-Git/MSWPackages/git/trees/main?recursive=1
```

响应较大可能被截断。grep 响应中的 `<package-name>/` 以提取文件列表。如果截断，则回退到每个目录树调用：

```
https://api.github.com/repos/MSW-Git/MSWPackages/contents/<package-name>/MyDesk
```

标准包布局：
- `<package-name>/README.md`
- `<package-name>/<PackageName>.modpackage` — 安装器清单（视为不透明）
- `<package-name>/MyDesk/<PackageName>/Core/` — 核心脚本/UI 要复制
- `<package-name>/MyDesk/<PackageName>/Sample/` — 示例用法（除非用户明确要求，否则不要复制）
- `<package-name>/MyDesk/Util/` — 共享工具（部分包）

### 3. 原始文件获取 (按需逐文件)

```
https://raw.githubusercontent.com/MSW-Git/MSWPackages/main/<path>
```

将 `github.com/.../blob/main/...` 替换为 `raw.githubusercontent.com/.../main/...` 以用于任何浏览 URL。

---

## 集成工作流

用户确认集成后：

1. **将文件映射到项目布局**:
   - `MyDesk/<PackageName>/Core/*.mlua` → `RootDesk/MyDesk/<PackageName>/`
   - `MyDesk/<PackageName>/Core/*.ui` → `ui/`
   - `MyDesk/<PackageName>/Core/*.model` → `RootDesk/MyDesk/Models/<分类>/`
   - `MyDesk/Util/*` → `RootDesk/MyDesk/Util/` (如果已存在则重用)

2. **检查 UUID 冲突**: 接收的 `.ui`/`.model` 文件中的每个实体 `id` 和 `EntryKey` 都不能在用户的项目中已存在。在写入前使用 `grep` 工作区查找冲突。使用新的十六进制 UUID 重新生成任何冲突的 UUID。

3. **检查 sprite RUID 依赖**: 扫描包文件以查找硬编码的 RUID。它们引用 MSW 社区资源 — 通常可以，但如果任何看起来可疑或需要替代，请使用 `msw-search` 验证。

4. **解决跨包依赖**: 一些包依赖其他包（例如排名可能依赖于玩家数据）。阅读包的 README 和源代码头部 — 先安装传递依赖的包，然后安装此包。

5. **使用标准 MSW 工作流应用**: `stop` → `refresh_workspace` → `play`。在构建日志和运行时日志中验证。

6. **集成到用户代码**: 大多数包暴露一个 `_<PackageName>` 逻辑单例。从用户现有脚本调用其 API（例如 `_MaplestoryToast:Show(...)`）。

---

## 陷阱

- **`.modpackage` 文件在此工作流中不是自动安装脚本** — 它是 Maker-编辑器元数据。实际集成包需要手动文件复制。
- **示例中的硬编码 sprite RUID**: 包示例通常引用特定的 RUID 用于装饰精灵。这些可以工作，但用户可能想替换。总结时注意此点。
- **UI 文件使用 UIGroup 根实体** — 复制时通过 `msw-ui-system` (`UIBuilder.read/load` 检查, builder API 修改；设计规则 — UIGroup 根配置、锚点模式陷阱 — 同一技能中）。不要手动编辑原始 `.ui` JSON。
- **`Sample/` 内容仅为说明，非生产** — 除非用户明确要求，否则不要复制 `Sample/` 文件。示例脚本通常绑定到键盘快捷键，可能与用户的控制冲突。
- **包不替代对 mlua 的理解** — 包提供预构建功能，但用户仍需 `msw-scripting` 知识扩展它们。
- **不要推测性批量安装多个包** — 每次集成都会添加文件和表面区域。一次安装一个功能，验证后继续。

---

## 用户已选择 "从零构建"

完全跳过集成。继续正常 MSW 创作 (`msw-scripting`, `msw-search` 等)。不要默默继续向用户推荐包。

---

## 当 `MSW-Git/MSWPackages` 无法访问

- WebFetch 返回错误或 404 → 确认 URL 未更改。
- 沙盒网络可能阻止直接 `curl` 到 `api.github.com` — 优先使用 `WebFetch` 获取原始和 HTML URL。
- 如果所有尝试都失败，回退到从零构建，并告知用户包当前无法访问。

---

## 参考链接

- `msw-general` — 工作区、文件路径、MCP 工具、坐标系。
- `msw-scripting` — `.mlua` 语法用于将包 API 钩入游戏逻辑。
- `msw-search` — 当替换包捆绑资源时查找 sprite/动画/声音 RUID。
