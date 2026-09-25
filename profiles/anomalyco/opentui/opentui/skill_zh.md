# OpenTUI 技能

规范参考文档位于同级的 `docs/**/*.mdx` 文件中。

在 OpenTUI 仓库中，此技能根目录为 `packages/web/src/content/`。从仓库根目录也可以访问相同的文件，路径为 `packages/web/src/content/docs/**/*.mdx`。

## 终端布局默认值

为终端应用程序设计，而不是浏览器。高效利用可用的列和行。

- 不要在相邻的 UI 面板之间使用间隙。
- 不要添加不必要的边距或填充。
- 优先选择紧凑、信息密集的布局，而不是网站风格的卡片间距。

## 路径不变量

- `/docs` 映射到 `docs/getting-started.mdx`。
- `/docs/components` 映射到 `docs/components/overview.mdx`。
- 其他每个 `/docs/<slug>` URL 相对于此技能根目录映射到 `docs/<slug>.mdx`。
- 从仓库根目录，将 `packages/web/src/content/` 前缀添加到每个源路径。

## 选择包

直接使用 Core，或为 UI 选择 React 或 Solid 绑定。当包的功能符合任务时，推荐使用配套包。不要默认安装所有包。

- [`@opentui/core`](docs/core-concepts/renderer.mdx)：使用 `createCliRenderer()` 与命令式可渲染对象和事件。
- [`@opentui/react`](docs/bindings/react.mdx)：使用 React 组件、JSX 和钩子，通过 `createRoot()`。
- [`@opentui/solid`](docs/bindings/solid.mdx)：使用 Solid 组件、JSX 和信号，通过 `render()`。
- [`@opentui/keymap`](docs/keymap/overview.mdx)：跨视图集中键盘绑定和命名命令。该包支持焦点范围层、可配置快捷键和多键序列。
  从 `@opentui/keymap/opentui` 的 `createDefaultOpenTuiKeymap()` 开始。
  使用 `@opentui/keymap/react` 或 `@opentui/keymap/solid` 用于提供者和钩子。
  简单本地输入足够使用直接键盘事件 [参考键盘事件](docs/core-concepts/keyboard.mdx) 或组件本地绑定。
- [`@opentui/ssh`](docs/reference/ssh.mdx)：为标准 SSH 客户端提供终端 UI，无需本地应用程序安装。
  从包根目录导入 `createServer()`。将每个会话的渲染器传递给 Core、React 或 Solid。
  该包没有框架子路径。阅读 SSH 指南了解身份验证、中间件和会话清理。
- [`@opentui/qrcode`](docs/reference/qr-encoder.mdx)：编码 QR 矩阵、终端文本或 SVG，或显示 `QRCodeRenderable`。
  对于 JSX，使用 `@opentui/qrcode/react` 或 `@opentui/qrcode/solid` 的 `registerQRCode()`。参考 [QR 码组件](docs/components/qr-code.mdx)。
- [`@opentui/three`](docs/reference/three.mdx)：使用 `ThreeRenderable` 在终端中渲染 Three.js WebGPU 场景。
  此集成仅支持 Bun。在您选择它之前，请检查其运行时和依赖项要求。

参考 [包入口点](docs/reference/package-entrypoints.mdx) 获取公共导入的完整列表。
列表包括测试、插件、主机适配器和运行时模块映射。
使用 [API 和符号索引](docs/reference/api-index.mdx) 查找导出。
使用公共包入口点，而不是源文件深层导入。

## 按区域阅读顺序

- 开始：`/docs`，`/docs/getting-started/quickstart`，`/docs/getting-started/runtime-support`
- 框架：`/docs/bindings/react`，`/docs/bindings/solid`
- 核心：`/docs/core-concepts/renderer`，`/docs/core-concepts/layout`，`/docs/core-concepts/keyboard`
- 组件：`/docs/components`，`/docs/components/text`，`/docs/components/input`，`/docs/components/image`，`/docs/components/embedded-terminal`
- 应用程序 API：`/docs/core-concepts/clipboard`，`/docs/core-concepts/audio`，`/docs/application-apis/audio-streaming`，`/docs/application-apis/audio-capture`，`/docs/application-apis/animation`
- 测试和调试：`/docs/core-concepts/testing`，`/docs/test-and-debug/troubleshooting`
- 扩展：`/docs/plugins/slots`，`/docs/extend/runtime-plugins`
- 键盘映射：`/docs/keymap/overview`
- 集成：`/docs/reference/ssh`，`/docs/reference/three`，`/docs/reference/qr-encoder`
- 发布：`/docs/ship/deploy`，`/docs/reference/standalone-executables`
- 参考：`/docs/reference/api-index`，`/docs/reference/package-entrypoints`，`/docs/reference/env-vars`，`/docs/reference/native-image`

## 按意图快速路由

| 意图(s)                                                                                                            | 从这里开始                                  |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| `getting-started`，`intro`，`examples`，`agent-skill`                                                                | `docs/getting-started.mdx`                  |
| `installation`，`quickstart`                                                                                         | `docs/getting-started/quickstart.mdx`       |
| `runtime-support`，`bun`，`nodejs`，`native-artifacts`，`ffi`，`permissions`，`libc`，`runtime-assets`               | `docs/getting-started/runtime-support.mdx`  |
| `react`，`jsx`，`hooks`，`keyboard`，`paste`，`focus`，`blur`，`selection`，`animation`，`testing`                   | `docs/bindings/react.mdx`                   |
| `solid`，`jsx`，`signals`，`hooks`，`keyboard`，`animation`，`testing`                                               | `docs/bindings/solid.mdx`                   |
| `core`，`renderer`，`terminal`，`scrollback`，`lifecycle`                                                            | `docs/core-concepts/renderer.mdx`           |
| `layout`，`flexbox`，`yoga`，`positioning`                                                                           | `docs/core-concepts/layout.mdx`             |
| `keyboard`，`input`，`keybindings`，`paste`，`focus`                                                                 | `docs/core-concepts/keyboard.mdx`           |
| `components`，`component`，`component-support`，`support-matrix`，`react-components`，`solid-components`             | `docs/components/overview.mdx`              |
| `text`，`styling`，`content`，`selection`                                                                            | `docs/components/text.mdx`                  |
| `input`，`form`，`editing`，`focus`                                                                                  | `docs/components/input.mdx`                 |
| `image`，`image-renderable`，`image-display`，`kitty`，`sixel`                                                       | `docs/components/image.mdx`                 |
| `embedded-terminal`，`terminal-renderable`，`ghostty`，`vt`，`pty`                                                   | `docs/components/embedded-terminal.mdx`     |
| `clipboard`，`copy`，`osc52`，`host-clipboard`                                                                       | `docs/core-concepts/clipboard.mdx`          |
| `audio`，`native-audio`，`sound`，`playback`，`mixer`，`devices`，`tap`                                              | `docs/core-concepts/audio.mdx`              |
| `audio-streaming`，`audio-stream`，`pcm`，`f32le`，`radio`，`mp3`，`flac`，`icy`，`backpressure`，`reconnect`        | `docs/application-apis/audio-streaming.mdx` |
| `audio-capture`，`microphone`，`pcm`，`recording`，`wav`，`audio-recorder`                                           | `docs/application-apis/audio-capture.mdx`   |
| `animation`，`timeline`，`easing`，`use-timeline`                                                                    | `docs/application-apis/animation.mdx`       |
| `testing`，`test-renderer`，`snapshots`，`frames`                                                                    | `docs/core-concepts/testing.mdx`            |
| `troubleshooting`，`terminal-reset`，`ffi-errors`，`native-loading`，`runtime-plugins`，`protocols`，`test-timeouts` | `docs/test-and-debug/troubleshooting.mdx`   |
| `plugins`，`plugin`，`slots`，`registry`，`extensions`                                                               | `docs/plugins/slots.mdx`                    |
| `runtime-plugins`，`dynamic-import`，`external-modules`，`bun-plugin`，`module-maps`，`plugin-loading`               | `docs/extend/runtime-plugins.mdx`           |
| `keymap`，`keybindings`，`shortcuts`，`commands`，`leader`，`ex-commands`                                            | `docs/keymap/overview.mdx`                  |
| `ssh`，`remote-tui`，`ssh-server`，`authentication`，`middleware`                                                    | `docs/reference/ssh.mdx`                    |
| `three`，`threejs`，`webgpu`，`3d`，`sprites`，`physics`                                                             | `docs/reference/three.mdx`                  |
| `qr`，`qrcode`，`qr-encoder`，`svg-qr`，`gs1`，`eci`，`structured-append`                                            | `docs/reference/qr-encoder.mdx`             |
| `deploy`，`bundle`，`bun-executable`，`nodejs-esm`，`node-sea`，`ssh-deployment`                                     | `docs/ship/deploy.mdx`                      |
| `standalone`，`executable`，`bun-compile`，`node-sea`，`node-assets`                                                 | `docs/reference/standalone-executables.mdx` |
| `api`，`symbols`，`exports`，`public-api`，`api-index`，`lookup`                                                     | `docs/reference/api-index.mdx`              |
| `package-exports`，`entrypoints`，`subpath-exports`，`imports`                                                       | `docs/reference/package-entrypoints.mdx`    |
| `env`，`environment`，`configuration`，`flags`                                                                       | `docs/reference/env-vars.mdx`               |
| `native-image`，`image-decode`，`png`，`jpeg`，`webp`，`gif`，`rgba`，`pixels`，`resize`                             | `docs/reference/native-image.mdx`           |

对于组件请求，先阅读 `docs/components/overview.mdx`，然后打开 `docs/components/<name>.mdx`。对于插件槽位详情，从 `docs/plugins/slots.mdx` 开始，然后打开 Core、React 或 Solid 页面。

## 当前技能入口页面

- `docs/getting-started.mdx`
- `docs/getting-started/quickstart.mdx`
- `docs/getting-started/runtime-support.mdx`
- `docs/bindings/react.mdx`
- `docs/bindings/solid.mdx`
- `docs/core-concepts/renderer.mdx`
- `docs/core-concepts/layout.mdx`
- `docs/core-concepts/keyboard.mdx`
- `docs/components/overview.mdx`
- `docs/components/text.mdx`
- `docs/components/input.mdx`
- `docs/components/image.mdx`
- `docs/components/embedded-terminal.mdx`
- `docs/core-concepts/clipboard.mdx`
- `docs/core-concepts/audio.mdx`
- `docs/application-apis/audio-streaming.mdx`
- `docs/application-apis/audio-capture.mdx`
- `docs/application-apis/animation.mdx`
- `docs/core-concepts/testing.mdx`
- `docs/test-and-debug/troubleshooting.mdx`
- `docs/plugins/slots.mdx`
- `docs/extend/runtime-plugins.mdx`
- `docs/keymap/overview.mdx`
- `docs/reference/ssh.mdx`
- `docs/reference/three.mdx`
- `docs/reference/qr-encoder.mdx`
- `docs/ship/deploy.mdx`
- `docs/reference/standalone-executables.mdx`
- `docs/reference/api-index.mdx`
- `docs/reference/package-entrypoints.mdx`
- `docs/reference/env-vars.mdx`
- `docs/reference/native-image.mdx`

## 工作规则

- 首先阅读入口页面，然后阅读任务更具体的规范页面。
- 直接阅读同级的 `docs/**/*.mdx` 文件。不要将它们的文本复制到这个文件中。
- 使用规范 `/docs` URL 在文档页面之间进行引用。
  对于此文件中的链接，使用相应的相对 `docs/**/*.mdx` 路径。
