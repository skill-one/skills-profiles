## 前置条件

首先，必须将音效添加到 `[remotion.media](./packages/remotion-media)` 包中。  
然后，可以使用 `bun run build` 进行部署。如果我们处于 worktree 中，可能会缺少 `.env` 文件，但在主非 worktree 分支上它应该存在。

事实来源是该仓库中的 `generate.ts`。在将其添加到 `@remotion/sfx` 之前，音效必须存在于那里。

音效必须满足以下要求：

- WAV 格式
- CC0（知识共享零）许可
- 归一化，峰值在 -3dB

## 步骤

### 1. 添加到 `remotion.media` 仓库（必须首先完成）

在 `remotion-dev/remotion.media` 仓库中：

1. 将 WAV 文件添加到仓库的根目录
2. 在 `generate.ts` 中的 `soundEffects` 数组中添加一个条目：
   ```ts
   {
     fileName: "my-sound.wav",
     attribution:
       "作者描述 -- https://source-url -- 许可证：知识共享零",
   },
   ```
3. 运行 `bun generate.ts` 将其复制到 `files/` 并重新生成 `variants.json`
4. 部署

### 2. 将导出添加到 `packages/sfx/src/index.ts`

使用 camelCase 作为变量名。避免使用 JavaScript 保留字（例如，使用 `uiSwitch` 而不是 `switch`）。

```ts
export const mySound = 'https://remotion.media/my-sound.wav';
```

### 3. 在 `packages/docs/docs/sfx/<name>.mdx` 创建一个文档页面

遵循现有页面的模式（例如 `whip.mdx`）。包括：

- 带有 `image`、`title`（camelCase 导出名）、`crumb: '@remotion/sfx'` 的 frontmatter
- `<AvailableFrom>` 标签，带有下一个发布版本号
- `<PlayButton>` 的导入和使用
- 描述
- 使用 `@remotion/media` 的 `<Audio>` 组件的示例代码
- 值部分，使用围栏代码块显示 URL
- 时长部分（获取文件并在 macOS 上使用 `afinfo` 获取时长/格式）
- 归因部分，带有来源链接和许可证
- 转换部分，使用全链接句子：`[在 remotion.dev/convert 上打开此文件](https://remotion.dev/convert?url=<encoded-sfx-url>)`
- 参见部分，链接到相关的音效

### 4. 在侧边栏和目录中注册

- `packages/docs/sidebars.ts` — 将 `'sfx/<name>'` 添加到 `@remotion/sfx` 类别项中
- `packages/docs/docs/sfx/table-of-contents.tsx` — 添加一个 `<TOCItem>` 并使用 `<PlayButton size={32}>`

### 5. 重新生成 SFX 波形

在音效添加到 `packages/remotion-media` 并从 `packages/sfx/src/index.ts` 导出后，重新生成文档使用的波形样本：

```bash
bun packages/docs/generate-sfx-waveforms.ts
```

这使用 `ffmpeg` 将每个导出的音效采样为约 2000 个波形样本，并更新 `packages/docs/components/sfx-demos/sfx-waveforms.ts`。

### 6. 更新技能规则文件

将新 URL 添加到 `packages/skills/skills/remotion-markup/sfx.md` 中的列表。

### 7. 构建

```bash
cd packages/sfx && bun run make
```

## 命名规范

| 文件名       | 导出名                |
| --------------- | -------------------------- |
| `my-sound.wav`  | `mySound`                  |
| `switch.wav`    | `uiSwitch` (保留字)     |
| `page-turn.wav` | `pageTurn`                 |

## 版本

使用 `packages/core/src/version.ts` 中的当前版本。  
对于文档 `<AvailableFrom>`，将补丁版本加 1。
