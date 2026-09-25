# 贡献给 HyperFrames Registry

为新的 Registry 区块或组件，引导用户从创意到已合并的 PR。

## 工作流程

```
1. Clarify → 2. Scaffold → 3. Build → 4. Validate → 5. Preview → 6. Ship
```

### 步骤 1：明确需求

询问他们正在构建什么。Registry 有两种项目类型：

- **区块** (`registry/blocks/`, type `hyperframes:block`) — 带有固定尺寸和时长的完整独立组合。包含字幕样式、VFX 特效、标题卡片、下三分之一等。
- **组件** (`registry/components/`, type `hyperframes:component`) — 无需固定尺寸或时长的可复用片段。包含 CSS 特效、文本处理、可适应任何组合尺寸的叠加层等。

然后询问：

- 效果的一句话描述
- 视觉参考（URL、截图或描述）
- 谁会在何时使用它？

### 步骤 2：搭建

创建 Registry 结构：

**对于区块：**

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

### | 条目名称 | ID 前缀 | 示例 ID |
### | -------- | -------- | -------- |
### | `cap-hormozi` | `hz` | `hz-cg-0`, `hz-cw-3` |
### | `cap-typewriter` | `tw` | `tw-ch-0-5` |
### | `vfx-chrome` | `vc` | `vc-canvas` |

使用 2-3 个字母的前缀。所有元素 ID 必须使用此前缀，以避免子组合中发生冲突。

**区块的 registry-item.json：**

```json
{
  "$schema": "https://hyperframes.heygen.com/schema/registry-item.json",
  "name": "{block-name}",
  "type": "hyperframes:block",
  "title": "{Human Title}",
  "description": "{one sentence}",
  "dimensions": { "width": 1920, "height": 1080 }, // adjust: 1080x1920 for portrait/social
  "duration": 10, // adjust for your composition
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

**组件的 registry-item.json**（无 `dimensions` 或 `duration`）：

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

### 步骤 3：构建

根据类型应用正确的模板。参见 [templates.md](templates.md) 获取可复制的起始内容。

#### 字幕区块

**字幕不可妥协的规则：**

- 字体：比例字体的**最低 96px**。等宽字体的 **64-72px** 可接受（字符更宽，所需字号更小）。
- 可读性：`-webkit-text-stroke: 2-3px` 或使用多层 ` text-shadow`
- 溢出：在每个 group 上调用 `window.__hyperframes.fitTextFontSize()`
- 卡拉OK（Karaoke）：通过 `tl.to(wordEl, { color/scale }, WORDS[wi].start)` 高亮当前活跃的单词
- 硬性停止：在每个 `group` 的 `g.end` 处调用 `tl.set(groupEl, { opacity: 0, visibility: "hidden" }, g.end)`
- **绝不在 `tl.set(el, { opacity: 1 })` 所在位置同时使用 `tl.from(el, { opacity: 0 })`** — 前者会覆盖后者。请使用 `tl.to` 替代。

**逐字符动画**（打字机、乱码）：

- 将每个字符包裹在 ID 为 `{prefix}-ch-{group}-{char}` 的 `<span>` 中
- 通过从单词时间戳计算出的区间使用 `tl.set` 实现错开效果
- 光标/装饰元素：使用 `tl.set` 按间隔设置，不可使用 CSS 动画（无法预览/跳转）

**定位变体：**

- 居中：`display: flex; align-items: center; justify-content: center;`
- 下三分之一（lower-third）：`position: absolute; bottom: 100px; left: 0; width: 100%; text-align: center;`
- 左对齐：`position: absolute; bottom: 100px; left: 120px; text-align: left;`

#### VFX 区块（Three.js）

- 从 CDN 使用 `three@0.147.0`（全局脚本）
- `tl.eventCallback("onUpdate", renderScene); renderScene();` — 无需使用 `requestAnimationFrame`
- 状态代理模式：GSAP 动画普通 JS 对象，渲染函数读取该对象
- 使用 `mulberry32` 种子化 PRNG 实现随机性

#### 所有类型

- `data-composition-id` 必须与 `window.__timelines["id"]` 匹配
- 所有元素 ID 必须以前缀缩写命名
- `gsap.timeline({ paused: true })` — 始终处于暂停状态
- 禁止使用 `Math.random()`，禁止使用 `Date.now()`

### 步骤 4：验证

```bash
hyperframes lint                    # 0 errors required
hyperframes validate --no-contrast  # 0 console errors required
```

### 步骤 5：预览

```bash
# 渲染预览视频
hyperframes render -o preview.mp4

# 用于视觉 QA 的快照
hyperframes snapshot --at "1.0,3.0,5.0,7.0"

# 发布到 hyperframes.dev 供评审
npx hyperframes publish
```

**目录预览图片** — 目录卡片使用位于 `docs/images/catalog/{kind}/{name}.png` 的 PNG 图片（其中 `{kind}` 为 `blocks` 或 `components`）。从快照中生成它，然后：

- **HeyGen 内部贡献者：** 运行 `scripts/upload-docs-images.sh`（需要 AWS 配置文件 `engineering-767398024897`）
- **外部贡献者：** 将预览 MP4 附加到 PR 描述中。维护者将在合并前生成并上传目录图片。

### 步骤 6：发布

**所有步骤均不可或缺。缺少其中任何一步都会导致目录条目失效。**

`{kind}` 取决于步骤 1 中构建的是区块还是组件。

```bash
# 1. 创建分支
git checkout -b feat/registry-{name}

# 2. 格式化 HTML
npx oxfmt registry/{kind}/{name}/*.html

# 3. 更新 registry/registry.json — 向 "items" 数组添加条目：
#    { "name": "{name}", "type": "hyperframes:block" }  (或 "hyperframes:component")

# 4. 生成目录文档页面
npx tsx scripts/generate-catalog-pages.ts

# 5. 发布到 hyperframes.dev，以便评审者预览
npx hyperframes publish

# 6. 暂存所有内容
git add registry/{kind}/{name}/ registry/registry.json docs/catalog/

# 7. 提交
git commit -m "feat(registry): add {name} — {one sentence}"

# 8. 推送并开启包含 hyperframes.dev 链接的 PR
git push origin feat/registry-{name}
gh pr create --title "feat(registry): {name}" --body "preview: {hyperframes.dev-url}"
```

**如果没有 GitHub 账号：** 你需要一个账号来开启 PR。在 https://github.com/signup 注册，然后运行 `gh auth login`。

## 质量门禁

- [ ] `hyperframes lint` → 0 errors
- [ ] `hyperframes validate` → 0 console errors
- [ ] `npx oxfmt --check` 通过
- [ ] `registry/registry.json` 已更新并包含新条目
- [ ] 已运行 `scripts/generate-catalog-pages.ts`（已生成文档页面）
- [ ] 已运行 `npx hyperframes publish`（认领您的项目链接）
- [ ] 预览 MP4 已附加到 PR（外部贡献者）或目录 PNG 已上传（内部贡献者）
- [ ] 所有 ID 唯一且已添加前缀
