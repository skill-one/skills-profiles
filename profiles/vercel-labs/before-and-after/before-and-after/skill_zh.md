# 为 PR 添加视觉媒体

使用 `agent-browser` 创建截图或录制视频。这项技能仅拥有 GitHub PR 附件工作流。

## 捕获

1. 使用 `agent-browser skills get core --full` 加载与版本匹配的核心指令，并遵循它们进行会话、导航、页面状态、截图和录制。
2. 如果 Vercel URL 受保护，加载 `agent-browser skills get protected-vercel-deployments --full`。不要在此处重现其认证工作流。
3. 将媒体保存在仓库下，路径中不包含空格，例如：

   ```text
   captures/desktop-before.png
   captures/desktop-after.png
   captures/mobile-before.png
   captures/mobile-after.png
   ```

格式化器支持 PNG、JPEG、GIF、WebP、MP4、MOV 和 WebM 文件。使用没有匹配 `--before` 文件的 `--after` 文件创建全新的预览。

### 屏幕录制

`agent-browser record start` 创建一个新的浏览器上下文。它会保留 cookies 和本地存储，但用于打开受保护的 Vercel 预览的源作用域头可能不会传递到该新上下文中。在录制受保护的预览之前：

1. 加载 `agent-browser skills get protected-vercel-deployments --full`。
2. 在空白页面上开始录制上下文。
3. 在录制上下文中应用该技能中的认证方法。
4. 认证激活后导航到预览，如有必要，则修剪导航前的部分。

不要假设在 `record start` 之前可以正常工作的页面在之后仍然保持认证状态。

Agent-browser `0.35.2` 和 `0.36.0` 以硬编码的 10 fps 捕获，没有 CLI 或环境覆盖选项。检查安装的版本及其录制参考，而不是假设这在后续版本中仍然保持不变。在转码时保留源节奏：将容器改为 30 或 60 fps 仅重复帧，并不会使运动更平滑。对于需要更高实际帧率的动画证据，使用真正更高节奏的捕获路径，而不是对 agent-browser 输出进行上采样。

### 等高图像对

GitHub 会将较短的图像在 Markdown 表格单元格中垂直居中。对于全页面的 before/after 截图，使两个文件具有相同的像素高度，以便它们的顶部边缘对齐：

1. 在相同的视口和状态下打开两个页面。
2. 在两个会话中读取 `document.documentElement.scrollHeight`。
3. 向较短的页面追加底部空间，直到两个滚动高度匹配，然后获取两个 `--full` 截图。

填充可以是透明的，也可以使用捕获工具的默认画布。切勿在页面上方添加空间。对于组件或部分比较，捕获相同的范围区域，而不是填充无关的页面内容。

使用原始 `agent-browser eval` 进行此 DOM 仅调整；不要为此技能添加图像处理依赖项。在发布之前，确认生成的文件具有相等的像素尺寸。

## 格式

为每个比较传递一对 `--before` 和 `--after`。重复 `--label` 以识别多个对：

```bash
node skill/scripts/format.mjs \
  --before captures/desktop-before.png \
  --after captures/desktop-after.png \
  --before captures/mobile-before.png \
  --after captures/mobile-after.png \
  --label Desktop \
  --label Mobile \
  > /tmp/before-and-after.md
```

对于仅 after 的预览：

```bash
node skill/scripts/format.mjs \
  --after captures/new-page.png \
  > /tmp/before-and-after.md
```

添加 `--attribution "<name>"` 以在 PR 应该归功于谁提供了证据时，在块前添加 `> Before/after by <name>` 行。

图像在表格中渲染。本地视频最初在其自己的行上渲染，以便 `gh --attach` 可以上传它们并暴露它们的最终附件 URL。Before/after 视频表格使用以下两步工作流程，因为 `gh --attach` 不会重写 `<video src>` 属性中的本地引用。

## 放置证据

在插入新的标记块之前，阅读现有的 PR 描述。将视觉证据放在顶部附近，在简短的开启上下文和现有的预览或部署链接部分（如果存在）之后，但在 Details、Changes、Testing 或 Notes 等实施密集部分之前。

在视觉证据中使用此阅读顺序：

1. 首先放置证明 PR 的真实 before/after 或预览证据。
2. 在主要证据之后放置补充格式、替代状态或演示。
3. 将演示技能而不是 PR 本身的任何内容标记为 demo，并在旁边说明材料限制。例如，当运动平滑度很重要时，注意已安装的 agent-browser 录制器当前的 10 fps 限制。

标题是语义提示，不是必需的名称。切勿仅仅为了创建锚点而编造或重写文本，也切勿拆分段落、列表、表格、代码块或其他 Markdown 结构。如果没有安全的锚点，则追加块而不是冒险损坏。如果标记块已存在，则仅移动或替换整个块；保留所有无关的文本。

发布后，打开渲染的 PR 并确认主要证据出现在补充演示之前，以及实施细节之前。

## 发布

保留现有的 PR 描述，仅替换此技能的标记块：

```bash
PR=123
gh pr view "$PR" --json body --jq .body > /tmp/pr-body.md

node skill/scripts/format.mjs \
  --body-file /tmp/pr-body.md \
  --before captures/desktop-before.png \
  --after captures/desktop-after.png \
  > /tmp/pr-body-next.md

ATTACH_ARGS=()
while IFS= read -r file; do
  ATTACH_ARGS+=(--attach "$file")
done < <(
  node skill/scripts/format.mjs \
    --attach-list \
    --before captures/desktop-before.png \
    --after captures/desktop-after.png
)

gh pr edit "$PR" --body-file /tmp/pr-body-next.md "${ATTACH_ARGS[@]}"
```

从同一目录运行格式化器和 `gh`。`gh --attach` 将本地文件上传到 GitHub 并重写 PR 正文中的匹配本地引用。

发布后，获取或打开 PR 描述，确认没有 `./captures/...` 引用在标记块中，并且证据按预期阅读顺序显示。

### 发布视频表格

视频比较是一流的两步发布操作：

1. 使用正常的 own-line 输出和 `gh pr comment --attach` 在临时 PR 评论中上传本地视频。
2. 通过 `gh api` 获取该评论并收集 before/after 顺序的稳定 `https://github.com/user-attachments/assets/...` URL。
3. 从这些 URL 生成最终的 HTML 表格，并替换 PR 标记块：

   ```bash
   node skill/scripts/format.mjs \
     --body-file /tmp/pr-body.md \
     --before-video-url https://github.com/user-attachments/assets/BEFORE_ID \
     --after-video-url https://github.com/user-attachments/assets/AFTER_ID \
     --label "Desktop hero" \
     > /tmp/pr-body-next.md

   gh pr edit "$PR" --body-file /tmp/pr-body-next.md
   ```

4. 在删除临时评论之前获取编辑后的 PR 正文。确认两个最终 URL 都存在且没有本地视频路径，然后删除评论。
5. 打开渲染的 PR 并确认两个 `<video>` 元素都在比较表格内，达到可播放的准备好状态，并显示控件。

如果 URL 提取、格式化或 PR 验证失败，保留临时评论，以便其上传的附件保持可恢复状态，并从最后一个成功阶段重试。使用 own-line 视频作为简单的备用方案。

不要发布包含 Vercel OIDC 令牌、绕过秘密、认证查询参数或浏览器状态文件的捕获。

## 脚本契约

`scripts/format.mjs` 是有意作为唯一捆绑脚本。它：

- 格式化现有的本地媒体；
- 将最终 GitHub 视频附件 URL 格式化为 HTML 比较表格；
- 将仅 after 的媒体标记为 `Preview`；
- 发出确切的附件路径列表；
- 插入或替换 `<!-- before-and-after:start/end -->` 而不改变其他 PR 文本。

其参数与这项技能相关，而不是公共库 API。
