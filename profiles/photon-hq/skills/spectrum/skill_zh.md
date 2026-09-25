# Spectrum

Spectrum 是 Photon 的统一消息 SDK。针对一个 `app.messages` 流编写处理逻辑，并通过 iMessage、WhatsApp Business、Terminal 或自定义提供程序进行消息传递。此技能针对 **[`spectrum-ts`](https://github.com/photon-hq/spectrum-ts)** 12.2.0 版本；其代码示例使用 TypeScript。

## 合约门

在编写特定提供程序的代码之前，需要识别提供程序并加载其主题文件。只有当每个导入、方法、内容形状、平台 ID、回退和抛出的错误都属于 `spectrum-ts` 12.2.0 和所选提供程序的合同时，示例才被认为是完整的。存在通用方法并不能证明每个提供程序都实现了它；每当支持影响正确性时，请阅读 [`capability-semantics.md`](./capability-semantics.md)。

## 此技能的组织结构

每个主题都位于此目录的独立文件中。根据用户的问题阅读相关的文件。

| 文件 | 咨询时机 |
|---|---|
| [`getting-started.md`](./getting-started.md) | 安装、`Spectrum()` 应用实例、多平台设置、四个核心原语。 |
| [`messages.md`](./messages.md) | 接收消息、`Message` 形状、基于 `content.type` 进行缩小、过滤自己的消息。 |
| [`content.md`](./content.md) | 外发消息的内容构建器：`text`、`markdown`、`attachment`、`voice`、`contact`、`richlink`、`app`、`poll`、`group`、`custom`。 |
| [`spaces-and-users.md`](./spaces-and-users.md) | `Space` 接口、输入指示器、`responding`、创建 DM 和群组。 |
| [`reactions-and-replies.md`](./reactions-and-replies.md) | `message.react(...)`、线程化的 `message.reply(...)`、何时使用哪个。 |
| [`capability-semantics.md`](./capability-semantics.md) | 原生支持与回退、警告并跳过、接受的 no-op 和抛出的错误。 |
| [`platform-narrowing.md`](./platform-narrowing.md) | 从通用 Spectrum 原语中恢复特定平台的类型。 |
| [`providers/imessage.md`](./providers/imessage.md) | iMessage — 分离的云端/本地提供程序、共享/专用云端线路模型、按手机路由、消息效果、点击响应。 |
| [`providers/terminal.md`](./providers/terminal.md) | Terminal TUI 提供程序 — 聊天侧边栏、响应、回复、附件、斜杠命令。 |
| [`providers/whatsapp-business.md`](./providers/whatsapp-business.md) | WhatsApp Business 云端 API。**仅限 1:1**。 |
| [`custom-events-and-lifecycle.md`](./custom-events-and-lifecycle.md) | 每个提供程序的事件流 (`app.typing` 等)、`app.stop()`、信号处理。 |
| [`custom-platforms.md`](./custom-platforms.md) | 使用 `definePlatform` 编写自己的提供程序 — 完整字段参考。 |
| [`best-practices.md`](./best-practices.md) | Photon 内部使用的生产架构模式 — 节流管道、飞行中取消、传递、幂等重试、按资源内存、作业失败审计日志。 |

## 参见

- [Spectrum 文档](https://photon.codes/docs/spectrum-ts/getting-started)
- [`spectrum-ts` on GitHub](https://github.com/photon-hq/spectrum-ts)
