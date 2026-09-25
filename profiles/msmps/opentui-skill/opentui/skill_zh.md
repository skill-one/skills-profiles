# OpenTUI 平台技能

用于使用 OpenTUI 构建终端用户界面的综合技能。请使用下方的决策树找到合适的框架和组件，然后加载详细参考文档。

## 关键规则

**在所有的 OpenTUI 代码中，请遵循以下规则：**

1. **使用 `create-tui` 创建新项目。** 参见框架 `REFERENCE.md` 快速启动说明。
2. **`create-tui` 选项必须位于参数之前。** `bunx create-tui -t react my-app` 有效，而 `bunx create-tui my-app -t react` 无效。
3. **切勿直接调用 `process.exit()`。** 请使用 `renderer.destroy()`（参见 `core/gotchas.md`）。
4. **React/Solid 中的文本样式需要嵌套标签。** 请使用修饰符元素，而非属性（参见 `components/text-display.md`）。

## 如何使用此技能

### 参考文件结构

框架参考文件遵循 5 文件模式。跨切面概念以单文件指南形式提供。

每个框架在 `./references/<framework>/` 中包含：

| 文件 | 用途 | 何时阅读 |
|------|------|----------|
| `REFERENCE.md` | 概述、何时使用、快速启动 | **始终首先阅读** |
| `api.md` | 运行时 API、组件、hooks | 编写代码时 |
| `configuration.md` | 设置、tsconfig、打包 | 配置项目时 |
| `patterns.md` | 常见模式、最佳实践 | 实现指导 |
| `gotchas.md` | 常见问题、限制、调试 | 故障排查时 |

跨切面概念在 `./references/<concept>/` 中，以 `REFERENCE.md` 为入口点。

### 阅读顺序

1. 从所选框架的 `REFERENCE.md` 开始
2. 然后阅读与您的任务相关的其他文件：
   - 构建组件 -> `api.md` + `components/<类别>.md`
   - 设置项目 -> `configuration.md`
   - 布局/定位 -> `layout/REFERENCE.md`
   - 键盘/输入处理 -> `keyboard/REFERENCE.md`
   - 分层键绑定/命令 -> `keymap/REFERENCE.md`
   - 动画 -> `animation/REFERENCE.md`
   - 故障排查 -> `gotchas.md` + `testing/REFERENCE.md`

### 示例路径

```
./references/react/REFERENCE.md           # 从这里开始阅读 React 相关内容
./references/react/api.md              # React 组件和 hooks
./references/solid/configuration.md    # Solid 项目设置
./references/components/inputs.md      # 输入、Textarea、Select 文档
./references/core/gotchas.md           # 核心调试技巧
```

### 运行时说明

OpenTUI 在 Bun 上运行，使用 Zig 进行原生构建。请阅读 `./references/core/gotchas.md` 以了解运行时需求和构建指导。

## 快速决策树

### "我应该使用哪个框架？"

```
使用哪个框架？
├─ 我想要完全控制、最高性能、无框架开销
│  └─ core/（命令式 API）
├─ 我熟悉 React，想要熟悉的组件模式
│  └─ react/（React 协调器）
├─ 我想要精细响应式、最优重新渲染
│  └─ solid/（Solid 协调器）
└─ 我正在基于 OpenTUI 构建库/框架
   └─ core/（命令式 API）
```

### "我需要显示内容"

```
需要显示内容？
├─ 普通文本或带样式文本 -> components/text-display.md
├─ 带边框/背景的容器 -> components/containers.md
├─ 可滚动内容区域 -> components/containers.md（scrollbox）
├─ 独立滚动条 -> components/containers.md（scrollbar）
├─ ASCII 艺术横幅/标题 -> components/text-display.md（ascii-font）
├─ PNG/JPEG/WebP/GIF 图片 -> components/text-display.md（image）
├─ 首次绘制诊断 -> components/text-display.md（time-to-first-draw）
├─ 二维码 -> components/text-display.md（qr-code, @opentui/qrcode）
├─ 嵌入式子终端/VT 输出 -> components/containers.md（仅 Core）
├─ 带边框/换行的数据表格 -> components/code-diff.md（TextTable）
├─ 带语法高亮的代码 -> components/code-diff.md
├─ 差异查看器（统一/分离，片段导航）-> components/code-diff.md
├─ 带行号的诊断信息 -> components/code-diff.md
└─ Markdown 内容（流式传输）-> components/code-diff.md（markdown）
```

### "我需要用户输入"

```
需要用户输入？
├─ 单行文本字段 -> components/inputs.md（input）
├─ 多行文本编辑器 -> components/inputs.md（textarea）
├─ 从列表中选择（垂直）-> components/inputs.md（select）
├─ 基于标签的选择（水平）-> components/inputs.md（tab-select）
├─ 数值滑块 -> components/inputs.md（slider）
├─ 声明式/分层键绑定 -> keymap/REFERENCE.md（@opentui/keymap）
└─ 自定义键盘快捷键 -> keyboard/REFERENCE.md
```

### "我需要布局/定位"

```
需要布局？
├─ Flexbox 式布局（行、列、换行）-> layout/REFERENCE.md
├─ 绝对定位 -> layout/patterns.md
├─ 响应式适配终端尺寸 -> layout/patterns.md
├─ 居中内容 -> layout/patterns.md
└─ 复杂嵌套布局 -> layout/patterns.md
```

### "我需要动画"

```
需要动画？
├─ 基于时间线的动画 -> animation/REFERENCE.md
├─ 缓动函数 -> animation/REFERENCE.md
├─ 属性过渡 -> animation/REFERENCE.md
└─ 循环动画 -> animation/REFERENCE.md
```

### "我需要处理输入"

```
需要处理输入？
├─ 键盘事件（keypress, release）-> keyboard/REFERENCE.md
├─ 分层绑定、命令、领键 -> keymap/REFERENCE.md
├─ 焦点管理 -> keyboard/REFERENCE.md
├─ 粘贴事件 -> keyboard/REFERENCE.md
├─ 鼠标事件 -> components/containers.md
├─ 文本选择与选择后复制 -> keyboard/REFERENCE.md（selection）
└─ 主机/终端剪贴板服务或 OSC 52 -> keyboard/REFERENCE.md（clipboard）
```

### "我需要测试我的 TUI"

```
需要测试 TUI？
├─ 快照测试 -> testing/REFERENCE.md
├─ 交互测试 -> testing/REFERENCE.md
├─ 测试渲染器设置 -> testing/REFERENCE.md
└─ 调试测试 -> testing/REFERENCE.md
```

### "我需要平台能力（音频、图片、剪贴板、通知、SSH）"

```
需要平台能力？
├─ 播放已加载声音或 MP3/FLAC 流 -> core/api.md（Audio）
├─ 捕获麦克风 PCM / 录制 WAV -> core/api.md（Audio）
├─ 解码、转换或显示图片 -> components/text-display.md（image）
├─ 读取/写入主机或终端剪贴板 -> keyboard/REFERENCE.md（clipboard）
├─ 桌面通知（OSC 9/777/99）-> core/api.md（triggerNotification）
├─ 自定义 stdin/stdout（PTY, xterm.js）-> core/api.md（createCliRenderer）
└─ 通过 SSH 提供 TUI 服务 -> core/REFERENCE.md（@opentui/ssh）
```

### "我需要调试/故障排查"

```
需要调试/故障排查？
├─ 运行时错误、崩溃 -> <框架>/gotchas.md
├─ 布局问题 -> layout/REFERENCE.md + layout/patterns.md
├─ 输入/焦点问题 -> keyboard/REFERENCE.md
└─ 复现与回归测试 -> testing/REFERENCE.md
```

### 故障排查索引

- 终端清理、崩溃 -> `core/gotchas.md`
- 文本样式未生效 -> `components/text-display.md`
- 输入焦点/快捷键 -> `keyboard/REFERENCE.md`
- 布局错位 -> `layout/REFERENCE.md`
- 不稳定快照 -> `testing/REFERENCE.md`

有关组件命名差异和文本修饰符，请参见 `components/REFERENCE.md`。

## 产品索引

### 框架
| 框架 | 入口文件 | 说明 |
|-----------|------------|-------------|
| Core | `./references/core/REFERENCE.md` | 命令式 API，所有基础组件 |
| React | `./references/react/REFERENCE.md` | React 协调器，用于声明式 TUI |
| Solid | `./references/solid/REFERENCE.md` | SolidJS 协调器，用于声明式 TUI |

### 跨切面概念
| 概念 | 入口文件 | 说明 |
|---------|------------|-------------|
| 布局 | `./references/layout/REFERENCE.md` | Yoga/Flexbox 布局系统 |
| 组件 | `./references/components/REFERENCE.md` | 按类别划分的组件参考 |
| 键盘 | `./references/keyboard/REFERENCE.md` | 底层键盘输入处理 |
| 键映射 | `./references/keymap/REFERENCE.md` | 声明式分层键绑定（`@opentui/keymap`） |
| 动画 | `./references/animation/REFERENCE.md` | 基于时间线的动画 |
| 测试 | `./references/testing/REFERENCE.md` | 测试渲染器与快照 |

### 组件类别
| 类别 | 入口文件 | 组件 |
|----------|------------|------------|
| 文本与显示 | `./references/components/text-display.md` | text, ascii-font, image, time-to-first-draw, styled text, qr-code |
| 容器 | `./references/components/containers.md` | box, scrollbox, scrollbar, embedded-terminal, borders |
| 输入 | `./references/components/inputs.md` | input, textarea, select, tab-select, slider |
| 代码与差异 | `./references/components/code-diff.md` | code, line-number, diff, markdown, text-table |

### 附加包
| 包 | 说明 | 文档 |
|--------|-------------|------|
| `@opentui/keymap` | 分层键绑定/命令引擎（Bun 或 Node，无 FFI） | `./references/keymap/REFERENCE.md` |
| `@opentui/qrcode` | 二维码组件 | `./references/components/text-display.md` |
| `@opentui/ssh` | 通过 SSH 提供 TUI 服务 | `./references/core/REFERENCE.md` |
| `@opentui/three` | Three.js WebGPU 渲染器（原 `core/src/3d`） | 上游 `packages/three` |
| `@opentui/examples` | 可运行示例（原 `core/src/examples`） | 上游 `packages/examples` |

Core 还提供加载/流式/捕获的 **Audio**、原生 **images**、主机和终端 **clipboard** 服务，以及 OSC 桌面 **notifications**。

## 资源

**仓库**：https://github.com/anomalyco/opentui
**Core 文档**：https://github.com/anomalyco/opentui/tree/main/packages/core/docs
**示例**：https://github.com/anomalyco/opentui/tree/main/packages/examples/src
**Awesome List**：https://github.com/msmps/awesome-opentui
