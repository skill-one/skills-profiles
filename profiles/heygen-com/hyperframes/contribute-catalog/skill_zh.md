# 为 HyperFrames Registry 贡献

指导用户从想法到合并 PR，以添加新的 Registry 块或组件。

## 工作流程

```
1. 明确需求 → 2. 搭建结构 → 3. 构建 → 4. 验证 → 5. 预览 → 6. 发布
```

### 第 1 步：明确需求

询问他们正在构建什么。Registry 有两种项目类型：

- **块** (`registry/blocks/`, 类型 `hyperframes:block`) — 具有固定尺寸和持续时间的完整独立组合。标题样式、VFX 效果、标题卡、底部字幕。
- **组件** (`registry/components/`, 类型 `hyperframes:component`) — 无固定尺寸或持续时间的可重用片段。CSS 效果、文本处理、可适应任何组合尺寸的叠加层。

然后询问：

- 效果的简短描述
- 视觉参考（URL、截图或描述）
- 谁在何时使用这个？

### 第 2 步：搭建结构

创建 Registry 结构：

**对于块：**

```
registry/blocks/{block-name}/
  {block-name}.html
  registry-item.json
```

**对于组件：**

```
registry/components/{component-name}/
  {component-name}.html
  registry-item.json
```

**命名规范：**

| 项目名称        | ID 前缀 | 示例 ID            |
| -------------- | ------- | ------------------ |
| `cap-hormozi`  | `hz`    | `hz-cg-0`, `hz-cw-3` |
| `cap-typewriter` | `tw`    | `tw-cg-0`, `tw-ch-0-5` |
| `vfx-chrome`   | `vc`    | `vc-canvas`        |

使用 2-3 个字母的前缀。所有元素 ID 必须使用此前缀，以避免在子组合中发生冲突。

**块的 `registry-item.json`：**

```json
{
  "$schema": "https://hyperframes.heygen.com/schema/registry-item.json",
  "name": "{block-name}",
  "type": "hyperframes:block",
  "title": "{Human Title}",
  "description": "{one sentence}",
  "dimensions": { "width": 1920, "height": 1080 }, // 调整：1080x1920 用于竖屏/社交
  "duration": 10, // 根据你的组合调整
  "tags": ["{category}", "{subcategory}"],
  "files": [
    {
      "path": "{block-name}.html",
      "target": "compositions/{block-name}.html",
      "type": "hyperframes:composition"
    }
  ]
}
```

**组件的 `registry-item.json`**（无 `dimensions` 或 `duration`）：

```json
{
  "$schema": "https://hyperframes.heygen.com/schema/registry-item.json",
  "name": "{component-name}",
  "type": "hyperframes:component",
  "title": "{Human Title}",
  "description": "{one sentence}",
  "tags": ["{category}"],
  "files": [
    {
      "path": "{component-name}.html",
      "target": "compositions/components/{component-name}.html",
      "type": "hyperframes:snippet"
    }
  ]
}
```

### 第 3 步：构建

根据类型应用正确的模板。参考 [templates.md](templates.md) 获取复制粘贴的起点。

#### 标题块

**不可协商的标题规则：**

- 字体：**96px 最小**（比例字体）。**64-72px 可接受**（等宽字体，更宽的字符需要更小的尺寸）。
- 可读性：`-webkit-text-stroke: 2-3px` 或多层 `text-shadow`
- 溢出：在每组上调用 `window.__hyperframes.fitTextFontSize()`
- 卡路里：通过 `tl.to(wordEl, { color/scale }, WORDS[wi].start)` 高亮活动单词
- 硬删除：在每组上调用 `tl.set(groupEl, { opacity: 0, visibility: "hidden" }, g.end)`
- **绝对不要在相同位置使用 `tl.from(el, { opacity: 0 })` 和 `tl.set(el, { opacity: 1 })`** — `from` 会覆盖 `set`。使用 `tl.to` 代替。

**逐字符动画**（打字机、打乱）：

- 将每个字符包裹在 `<span>` 中，ID 为 `{prefix}-ch-{group}-{char}`
- 通过 `tl.set` 在计算间隔（从单词时间戳）处错开
- 光标/装饰元素：使用 `tl.set` 在间隔处设置 — **不要使用 CSS 动画**（不可搜索）

**定位变体：**

- 居中：`display: flex; align-items: center; justify-content: center;`
- 底部字幕：`position: absolute; bottom: 100px; left: 0; width: 100%; text-align: center;`
- 左对齐：`position: absolute; bottom: 100px; left: 120px; text-align: left;`

#### VFX 块（Three.js）

- 使用 CDN 中的 `three@0.147.0`（全局脚本）
- `tl.eventCallback("onUpdate", renderScene); renderScene();` — **不要使用 requestAnimationFrame**
- 状态代理模式：GSAP 动画化普通 JS 对象，渲染函数读取它
- 使用 `mulberry32` 作为种子 PRNG（伪随机数生成器）进行随机性

#### 所有类型

- `data-composition-id` 必须 与 `window.__timelines["id"]` 匹配
- 所有元素 ID 必须使用块缩写前缀
- `gsap.timeline({ paused: true })` — 始终暂停
- **不要使用 `Math.random()`，不要使用 `Date.now()`**

### 第 4 步：验证

```bash
hyperframes lint                    # 需要 0 个错误
hyperframes validate --no-contrast  # 需要 0 个控制台错误
```

### 第 5 步：预览

```bash
# 渲染预览视频
hyperframes render -o preview.mp4

# 快照用于视觉 QA
hyperframes snapshot --at "1.0,3.0,5.0,7.0"

# 发布到 hyperframes.dev 进行审核
npx hyperframes publish
```

**目录预览图像** — 目录卡片使用 `docs/images/catalog/{kind}/{name}.png`（其中 `{kind}` 是 `blocks` 或 `components`）处的 PNG。从快照生成它，然后：

- **HeyGen 内部贡献者：** 运行 `scripts/upload-docs-images.sh`（需要 AWS 账户 `engineering-767398024897`）
- **外部贡献者：** 将预览 MP4 附加到你的 PR 描述中。维护者将在合并前生成并上传目录图像。

### 第 6 步：发布

**所有步骤都是必需的。缺少任何一步都会导致目录条目损坏。**

`{kind}` 是 `blocks` 或 `components`，取决于你在第 1 步构建的内容。

```bash
# 1. 创建分支
git checkout -b feat/registry-{name}

# 2. 格式化 HTML
npx oxfmt registry/{kind}/{name}/*.html

# 3. 更新 registry/registry.json — 将条目添加到 "items" 数组：
#    { "name": "{name}", "type": "hyperframes:block" }  (或 "hyperframes:component")

# 4. 生成目录文档页面
npx tsx scripts/generate-catalog-pages.ts

# 5. 发布到 hyperframes.dev 以供审核者预览
npx hyperframes publish

# 6. 添加所有内容
git add registry/{kind}/{name}/ registry/registry.json docs/catalog/

# 7. 提交
git commit -m "feat(registry): add {name} — {one sentence}"

# 8. 推送并打开带 hyperframes.dev 链接的 PR
git push origin feat/registry-{name}
gh pr create --title "feat(registry): {name}" --body "preview: {hyperframes.dev-url}"
```

**如果你没有 GitHub 账户：** 你需要一个账户来打开 PR。在 https://github.com/signup 上注册，然后运行 `gh auth login`。

## 质量门禁

- [ ] `hyperframes lint` → 0 个错误
- [ ] `hyperframes validate` → 0 个控制台错误
- [ ] `npx oxfmt --check` 通过
- [ ] `registry/registry.json` 更新了新条目
- [ ] 运行了 `scripts/generate-catalog-pages.ts`（生成了文档页面）
- [ ] 运行了 `npx hyperframes publish`（获取你的项目 URL）
- [ ] PR 中附加了预览 MP4（外部）或上传了目录 PNG（内部）
- [ ] 所有 ID 唯一且带前缀
