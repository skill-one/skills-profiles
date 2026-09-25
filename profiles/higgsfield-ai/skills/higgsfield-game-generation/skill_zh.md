# Higgsfield 游戏生成

创建一个连贯、可玩的网页游戏并交付URL，或仅生成所需的游戏资源。Higgsfield CLI负责生成、3D动作发现、部署和可选的市场发布。

## 初始化

开始工作前：

1. 如果`higgsfield`不可用，请安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果`higgsfield account status`报告会话过期或缺失，请要求用户运行`higgsfield auth login`，然后在确认后继续。
3. 对于完整游戏，在生成资源前确认`higgsfield game deploy --help`可用。这是交付能力检查。
4. 定位此安装的技能目录并显式设置它：
   ```bash
   export GAME_SKILL="/绝对路径/to/higgsfield-game-generation"
   test -f "$GAME_SKILL/scripts/pipeline.py"
   python3 "$GAME_SKILL/scripts/pipeline.py" --help
   ```
   不要从内存中重新创建捆绑脚本。

## 路由请求

- **完整可玩游戏** — 按照以下完整工作流程操作。
- **仅资源** — 阅读`references/stylization.md`，然后阅读匹配的资源参考。不要部署游戏。
- **仅设计** — 阅读`references/game-design-system.md`；返回请求的设计工件和资源清单。
- **现有游戏迭代** — 检查提供的源代码，保留其架构和未更改的资源，修改清单，重新构建，验证，并使用其现有的游戏ID重新部署。
- **预告片或宣传视频** — 使用`higgsfield-generate`，而不是此技能。
- **原生移动/桌面/主机运行时** — 解释此技能仅提供浏览器游戏；除非用户提供其他工具链，否则提供网页构建版本。

## 完整游戏工作流程

### 1. 规划

首先完整阅读`references/game-design-system.md`。确定游戏配置文件、交付上下文、核心循环、胜负/重启行为、性能预算、输入方法和语言处理。

创建`design/assets.csv`，每行对应一个视觉或音频资源：

```csv
id,角色,类型,描述,大小/比例,风格参考,来源
```

当玩家不是单人时，请随时阅读`references/multiplayer.md`。本地同屏多人游戏保持客户端侧；在线多人游戏需要平台服务器模块。

在生成任何视觉内容（包括程序化画布艺术）前，请先阅读`references/stylization.md`。导出一个风格公式，并将其逐字节插入到每个视觉提示中。如果简报已固定风格，请声明公式并继续。如果有多个实质性不同的风格适用，请展示简洁选项并等待选择。

在清单和风格公式之前，不应存在任何游戏代码或生成的视觉内容。

### 2. 生成资源并构建

同时启动独立的生成任务，然后在这些任务运行时编写游戏。在首次使用前检查每个模型合同：

```bash
higgsfield model list --json
higgsfield model get <任务类型>
higgsfield generate create <任务类型> ... --wait --json
```

媒体标志接受本地路径或先前的上传/任务ID。在链式操作时将任务JSON保存在项目文件中；不要将ID输入用户界面回复。

读取与清单行匹配的参考：

| 资源 | 必需参考 |
|---|---|
| 静态精灵、背景、UI | `references/stylization.md` |
| 精灵表 / 2D动画 | `references/2d-animation.md` |
| 重复地面、墙壁、瓦片、PBR贴图 | `references/textures.md` |
| 任何3D模型或动画 | `references/3d-animation.md` |
| 音乐、SFX、语音 | `references/audio.md` |

对于3D动画选择：

```bash
higgsfield preset list animation-action --query walk --json
higgsfield preset list animation-action --group Fighting --category Punching --json
```

当多个动作适用时，展示它们的预览URL并让用户选择。仅在检查目标模型模式后，将选择的整数作为`--animation_action_id`传递。

最后阅读`references/build-game.md`，但在编写游戏代码前。使用`index.html`和恰好一个根代码模块（`logic.js`或`server.js`）组装源ZIP。使用相对资源路径，并将`design/assets.csv`保存在交付的项目中。

生成失败最多重试两次。之后，使用最佳有效结果并在代码中补偿，或诚实修改清单。

### 3. 验证和交付

通过HTTP运行本地游戏，而不是`file://`：

```bash
python3 -m http.server 8000
```

验证完整循环、重启、缺失资源、控制台错误、响应式画布、非拉丁键盘布局通过`event.code`、移动设备范围内的仅触摸播放、声明的游戏手柄控制、固定步长行为，以及在适用情况下两个会话的多玩家。

从包含所需根文件的目录打包：

```bash
zip -r /绝对路径/to/game.zip . -x '*.DS_Store' 'node_modules/*' '.git/*'
higgsfield game deploy /绝对路径/to/game.zip \
  --title "<公开标题>" \
  --description "<面向玩家的描述>" \
  --thumbnail "<可选的 https 16:9 图片URL>" \
  --favicon "<可选的 https 1:1 图片URL>" \
  --json
```

对于更新，添加`--game-id <现有游戏ID>`；更新失败后永远不要省略它，因为那样会创建不同的游戏。

部署创建可玩URL。公开发布到公共市场是一个独立的外部操作，需要明确的用户意图：

```bash
higgsfield game publish <游戏ID> \
  --name "<可选的列表名称>" \
  --description "<可选的列表描述>" \
  --cover-url "<可选的 https 16:9 URL>" \
  --logo-url "<可选的 https 1:1 URL>" \
  --json
```

重新打开返回的可玩URL并重复关键冒烟路径。交付CLI返回的URL；永远不要手动构建它。

## 参考顺序

对于完整游戏：

1. `references/game-design-system.md`
2. `references/multiplayer.md` 当玩家不是单人时
3. `references/stylization.md`
4. 条件性资源参考
5. `references/build-game.md`

完整阅读每个选定的参考。不要加载无关参考。

仅在所属路由需要时才打开的支持性参考：

- `references/client-reference.md` — 在线客户端协议。
- `references/kernel-reference.md` — 平台房间-内核合同。
- `references/logic-reference.md` — 轮换/事件驱动规则模块。
- `references/meshy-api.md` — 仅原始Meshy回退。
- `references/meshy-input-rules.md` — 在任何图像到3D提交前强制执行。
- `references/procedural-animation.md` — 非类人的程序化构架。

## 用户体验规则

- 反映用户的语言；保持生成提示为英文。
- 用户更新简短，描述游戏，而不是内部门禁、阶段编号、任务ID或工具机制。
- 仅在答案实质性改变游戏时提问。不要批量无关问题。
- 在生成的和程序化的资源之间保留一个视觉系统。
- 不要在聊天中请求机密信息。原始Meshy回退仅在原生Higgsfield 3D模型不可用时才使用用户配置的环境密钥。
- 除非用户请求市场发布，否则不要公开发布。

## 输出

- 仅设计：请求的设计工件加上`design/assets.csv`。
- 仅资源：可用文件/结果URL及其清单角色。
- 完整游戏：验证的可玩URL、一行游戏玩法摘要，仅在明确发布时提供市场URL。
