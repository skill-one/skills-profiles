# OpenTUI 平台技能

用于构建终端用户界面的 OpenTUI 统一技能。使用下方的决策树找到合适的框架和组件，然后加载详细参考。

## 关键规则

在所有 OpenTUI 代码中必须遵循以下规则：

1. **使用 `create-tui` 创建新项目。** 参考框架 `REFERENCE.md` 快速入门。
2. **`create-tui` 选项必须位于参数之前。** `bunx create-tui -t react my-app` 有效，`bunx create-tui my-app -t react` 无效。
3. **直接调用 `process.exit()`。** 使用 `renderer.destroy()`（参见 `core/gotchas.md`）。
4. **React/Solid 中文本样式需要嵌套标签。** 使用修饰元素，而不是属性（参见 `components/text-display.md`）。

## 如何使用此技能

### 参考文件结构

框架参考遵循 5 文件模式。跨领域概念是单文件指南。

`./references/<framework>/` 中的每个框架包含：

| 文件 | 目的 | 何时阅读 |
|------|---------|--------------|
| `REFERENCE.md` | 概述、何时使用、快速入门 | **始终首先阅读** |
| `api.md` | 运行时 API、组件、钩子 | 编写代码 |
| `configuration.md` | 设置、tsconfig、打包 | 配置项目 |
| `patterns.md` | 常见模式、最佳实践 | 实现指导 |
| `gotchas.md` | 陷阱、限制、调试 | 排错 |

`./references/<concept>/` 中的跨领域概念以 `REFERENCE.md` 作为入口点。

### 阅读顺序

1. 从所选框架的 `REFERENCE.md` 开始
2. 然后阅读与您的任务相关的附加文件：
   - 构建组件 -> `api.md` + `components/<category>.md`
   - 设置项目 -> `configuration.md`
   - 布局/定位 -> `layout/REFERENCE.md`
   - 键盘/输入处理 -> `keyboard/REFERENCE.md`
   - 分层键绑定/命令 -> `keymap/REFERENCE.md`
   - 动画 -> `animation/REFERENCE.md`
   - 排错 -> `gotchas.md` + `testing/REFERENCE.md`

### 示例路径

```
./references/react/REFERENCE.md           # 从这里开始用于 React
./references/react/api.md              # React 组件和钩子
./references/solid/configuration.md    # Solid 项目设置
./references/components/inputs.md      # Input, Textarea, Select 文档
./references/core/gotchas.md           # 核心调试技巧
```

### 运行时注意事项

OpenTUI 基于 Bun 运行，并使用 Zig 进行原生构建。阅读 `./references/core/gotchas.md` 获取运行时要求和构建指导。

## 快速决策树

### "我应该使用哪个框架？"

```
选择框架？
├─ 我想完全控制、最大性能、无框架开销
│  └─ core/ (命令式 API)
├─ 我熟悉 React，想使用熟悉的组件模式
│  └─ react/ (React 调和器)
├─ 我需要细粒度响应性、最佳重绘
│  └─ solid/ (Solid 调和器)
└─ 我正在构建基于 OpenTUI 的库/框架
   └─ core/ (命令式 API)
```

### "我需要显示内容"

```
显示内容？
├─ 普通或样式化文本 -> components/text-display.md
├─ 带边框/背景的容器 -> components/containers.md
├─ 可滚动的内容区域 -> components/containers.md (scrollbox)
├─ 独立滚动条 -> components/containers.md (scrollbar)
├─ ASCII 艺术横幅/标题 -> components/text-display.md (ascii-font)
├─ PNG/JPEG/WebP/GIF 图像 -> components/text-display.md (image)
├─ 首次绘制诊断 -> components/text-display.md (time-to-first-draw)
├─ QR 码 -> components/text-display.md (qr-code, @opentui/qrcode)
├─ 嵌入式子终端/VT 输出 -> components/containers.md (Core 仅限)
├─ 带边框/换行的数据表 -> components/code-diff.md (TextTable)
├─ 带语法高亮的代码 -> components/code-diff.md
├─ 差异查看器（统一/分割、块导航） -> components/code-diff.md
├─ 带诊断的行号 -> components/code-diff.md
└─ Markdown 内容（流式） -> components/code-diff.md (markdown)
```

### "我需要用户输入"

```
用户输入？
├─ 单行文本字段 -> components/inputs.md (input)
├─ 多行文本编辑器 -> components/inputs.md (textarea)
├─ 从列表中选择（垂直） -> components/inputs.md (select)
├─ 标签式选择（水平） -> components/inputs.md (tab-select)
├─ 值滑块 -> components/inputs.md (slider)
├─ 声明式/分层键绑定 -> keymap/REFERENCE.md (@opentui/keymap)
└─ 自定义键盘快捷键 -> keyboard/REFERENCE.md
```

### "我需要布局/定位"

```
布局？
├─ Flexbox 风格布局（行、列、换行） -> layout/REFERENCE.md
├─ 绝对定位 -> layout/patterns.md
├─ 响应终端大小 -> layout/patterns.md
├─ 内容居中 -> layout/patterns.md
└─ 复杂嵌套布局 -> layout/patterns.md
```

### "我需要动画"

```
动画？
├─ 基于时间线的动画 -> animation/REFERENCE.md
├─ 缓动函数 -> animation/REFERENCE.md
├─ 属性过渡 -> animation/REFERENCE.md
└─ 循环动画 -> animation/REFERENCE.md
```

### "我需要处理输入"

```
输入处理？
├─ 键盘事件（按键、释放） -> keyboard/REFERENCE.md
├─ 分层绑定、命令、领导者键 -> keymap/REFERENCE.md
├─ 聚焦管理 -> keyboard/REFERENCE.md
├─ 粘贴事件 -> keyboard/REFERENCE.md
├─ 鼠标事件 -> components/containers.md
├─ 文本选择 & 选择时复制 -> keyboard/REFERENCE.md (selection)
└─ 主机/终端剪贴板服务或 OSC 52 -> keyboard/REFERENCE.md (clipboard)
```

### "我需要测试我的 TUI"

```
测试？
├─ 快照测试 -> testing/REFERENCE.md
├─ 交互测试 -> testing/REFERENCE.md
├─ 测试渲染器设置 -> testing/REFERENCE.md
└─ 调试测试 -> testing/REFERENCE.md
```

### "我需要平台功能（音频、图像、剪贴板、通知、SSH）"

```
平台功能？
├─ 播放加载的音频或 MP3/FLAC 流 -> core/api.md (Audio)
├─ 捕获麦克风 PCM / 录制 WAV -> core/api.md (Audio)
├─ 解码、转换或显示图像 -> components/text-display.md (image)
├─ 读取/写入主机或终端剪贴板 -> keyboard/REFERENCE.md (clipboard)
├─ 桌面通知（OSC 9/777/99） -> core/api.md (triggerNotification)
├─ 自定义 stdin/stdout (PTY, xterm.js) -> core/api.md (createCliRenderer)
└─ 通过 SSH 提供 TUI -> core/REFERENCE.md (@opentui/ssh)
```

### "我需要调试/排错"

```
排错？
├─ 运行时错误、崩溃 -> <framework>/gotchas.md
├─ 布局问题 -> layout/REFERENCE.md + layout/patterns.md
├─ 输入/聚焦问题 -> keyboard/REFERENCE.md
└─ 复现 + 回归测试 -> testing/REFERENCE.md
```

### 排错索引

- 终端清理、崩溃 -> `core/gotchas.md`
- 文本样式未应用 -> `components/text-display.md`
- 输入聚焦/快捷键 -> `keyboard/REFERENCE.md`
- 布局错位 -> `layout/REFERENCE.md`
- 不稳定的快照 -> `testing/REFERENCE.md`

组件命名差异和文本修饰请参见 `components/REFERENCE.md`。

## 产品索引

### 框架
| 框架 | 入口文件 | 描述 |
|-----------|------------|-------------|
| Core | `./references/core/REFERENCE.md` | 命令式 API，所有原语 |
| React | `./references/react/REFERENCE.md` | React 调和器用于声明式 TUI |
| Solid | `./references/solid/REFERENCE.md` | SolidJS 调和器用于声明式 TUI |

### 跨领域概念
| 概念 | 入口文件 | 描述 |
|---------|------------|-------------|
| Layout | `./references/layout/REFERENCE.md` | Yoga/Flexbox 布局系统 |
| Components | `./references/components/REFERENCE.md` | 按类别划分的组件参考 |
| Keyboard | `./references/keyboard/REFERENCE.md` | 低级键盘输入处理 |
| Keymap | `./references/keymap/REFERENCE.md` | 声明式分层键绑定 (`@opentui/keymap`) |
| Animation | `./references/animation/REFERENCE.md` | 基于时间线的动画 |
| Testing | `./references/testing/REFERENCE.md` | 测试渲染器和快照 |

### 组件类别
| 类别 | 入口文件 | 组件 |
|----------|------------|------------|
| Text & Display | `./references/components/text-display.md` | text, ascii-font, image, time-to-first-draw, styled text, qr-code |
| Containers | `./references/components/containers.md` | box, scrollbox, scrollbar, embedded-terminal, borders |
| Inputs | `./references/components/inputs.md` | input, textarea, select, tab-select, slider |
| Code & Diff | `./references/components/code-diff.md` | code, line-number, diff, markdown, text-table |

### 附加包
| 包 | 描述 | 文档 |
|---------|-------------|------|
| `@opentui/keymap` | 分层键绑定/命令引擎（Bun 或 Node，无 FFI） | `./references/keymap/REFERENCE.md` |
| `@opentui/qrcode` | QR 码组件 | `./references/components/text-display.md` |
| `@opentui/ssh` | 通过 SSH 提供 TUI | `./references/core/REFERENCE.md` |
| `@opentui/three` | Three.js WebGPU 渲染器（原 `core/src/3d`） | upstream `packages/three` |
| `@opentui/examples` | 可运行的示例（原 `core/src/examples`） | upstream `packages/examples` |

Core 还包含加载/流式传输/捕获的 **Audio**、原生 **图像**、主机和终端 **剪贴板** 服务以及 OSC 桌面 **通知**。

## 资源

**仓库**: https://github.com/anomalyco/opentui
**核心文档**: https://github.com/anomalyco/opentui/tree/main/packages/core/docs
**示例**: https://github.com/anomalyco/opentui/tree/main/packages/examples/src
**Awesome List**: https://github.com/msmps/awesome-opentui
