# App Store & Google Play Screenshots Generator

## 概述

搭建一个预构建的 Next.js + ShadCN 编辑器，让用户设计和导出 App Store **和** Google Play 截图作为 **广告**（而不是 UI 展示）。编辑器处理所有繁重的工作：

- 在画布的真实分辨率下连接实时预览（缩放以适应）
- 拖动重新排序列表，内联文本编辑，每个屏幕的布局切换器
- 跨屏幕模型：手机/设备框架、标题和分层元素可以移动到相邻屏幕，然后导出为剪辑的裁剪
- 拖放目标截图选择器（文件 → 保存到 `public/screenshots/uploaded/<hash>.png`）
- 自动保存到 **`app-store-screenshots.json`** 在项目根目录（git 可跟踪）+ `localStorage` 镜像
- 易于切换 iOS ↔ Android 平台——分离的幻灯片演示并排显示
- 通过 `html-to-image` 在每个 Apple/Google 要求的分辨率进行一键批量 PNG 导出
- 每个幻灯片切换明/暗变体，主题预设，区域选择
- 为由此技能创建的旧项目提供就地引导迁移；被动和显式迁移保持传统幻灯片隔离，直到用户有意选择连接画布

开箱即用的支持设备：

- **iPhone** (竖屏) — Apple App Store
- **iPad** (竖屏) — Apple App Store
- **Android 手机** (竖屏) — Google Play
- **Android 平板电脑 7"** (竖屏 + 横屏) — Google Play
- **Android 平板电脑 10"** (竖屏 + 横屏) — Google Play
- **功能图形** (1024×500 旗帜) — Google Play 商店列表页眉

## 核心原则

**截图是广告，不是文档。** 每个截图销售一个想法。如果你展示 UI，你就做错了——你是在销售一种感觉、一个结果或消灭一个痛点。使用此技能的交互式编辑器快速迭代副本和布局；不要从头开始手工制作页面。

## 此技能的作用

1. **复制一个预构建的模板** 从 `template/`（与此 `SKILL.md` 同位于）到用户的 working directory。
2. 使用用户的包管理器安装依赖项。
3. 将用户的截图放入 `public/screenshots/...` 并将他们的应用图标放入 `public/`。
4. （可选）用用户的 App 名称、起始副本、截图和连接画布偏好预先填充 `app-store-screenshots.json`，以便第一个预览是有意义的。
5. 启动开发服务器并告诉用户在浏览器中打开编辑器。

你不应该手工编写 `page.tsx`、设备框架或导出逻辑。它们位于模板中。

## 步骤 0：探测现有截图项目

在步骤 1 中询问新项目问题之前，始终检查当前工作目录是否存在现有的 App Store 截图实现。

运行轻量级探测：

```bash
test -f package.json && sed -n '1,220p' package.json
test -f app-store-screenshots.json && sed -n '1,120p' app-store-screenshots.json
rg -n "app-store-screenshots|html-to-image|toPng|ScreenshotEditor|DeckCanvas|connectedCanvas|EXPORT_SIZES|mockup.png|PHONE_SCREEN" package.json src app public 2>/dev/null
find public -maxdepth 4 \( -path "*/screenshots*" -o -name "mockup.png" -o -name "app-icon.png" \) -print 2>/dev/null
```

当任何这些为真时，将项目视为旧实现：

- `app-store-screenshots.json` 存在但没有 `schemaVersion`，`schemaVersion < 2` 或缺少 `connectedCanvas`。
- `src/components/editor/screenshot-editor.tsx` 存在但编辑器不引用 `DeckCanvas` 或 `connectedCanvas`。
- `src/app/page.tsx` 包含一个以前的全部生成器 (`html-to-image`, `toPng`, `EXPORT_SIZES`, `PHONE_SCREEN`, 硬编码幻灯片数组/主题)。
- 仓库包含旧截图资源布局 (`public/mockup.png`, `public/screenshots...`) 加上截图生成器包设置。

如果检测到旧实现，在执行任何其他操作之前，询问用户一个问题：

> 我在这里找到一个旧的 App Store 截图项目。您想让我将现有项目迁移到新的连接画布编辑器吗？
>
> 1. 是的 — 将现有项目迁移到新编辑器
> 2. 否的 — 以其他方式设置或修改项目

如果用户选择 **是的**，则**不要**询问步骤 1 问卷。使用仓库中已有的文件运行迁移路径。如果用户选择 **否**，请继续到步骤 1。

### 迁移路径（当用户说是的）

目标是就地 UI/模板升级，而不是重新设计。保留用户的现有应用名称、副本、截图路径、应用图标、上传的资产、区域和设备牌组，无论它们现在在哪里存在。用当前模板替换旧的 UI 实现。除非项目已经明确选择连接画布，否则保留传统牌组。

迁移规则：

1. **不再询问进一步的产品/设计问题。** 用户已经有一个项目。从现有文件中推断，并在末尾报告任何非阻塞差距。
2. **永远不要删除用户资产。** 保留 `public/screenshots/`, `public/app-icon.png`, 上传的截图和任何现有的 `app-store-screenshots.json`。
3. **保持可恢复性。** 如果工作区不干净，不要回滚无关的更改。在覆盖模板文件之前，将替换的项目状态/资产/代码快照复制到仓库外部的临时备份（例如 `/tmp/app-store-screenshots-migration-<timestamp>/`）并将在最终响应中提及该路径。
4. **优先选择结构化迁移。** 使用 JSON 工具读取和写入 `app-store-screenshots.json`。不要 regex 编辑 JSON。
5. **设置 `schemaVersion: 2` 并保留传统的 `connectedCanvas` 安全。** 如果现有项目已经有一个明确的布尔值 `connectedCanvas`，则保留它。如果项目是 pre-v2 或缺少标志，则写入 `"connectedCanvas": false` 以防止 offscreen/clipped 传统模型泄漏到相邻导出。新项目仍然默认为连接画布。
6. **保持截图指向现有文件。** 除非旧项目已经依赖于数字名称并且迁移需要它们，否则不要重命名截图文件。现有的静态路径是好的。
7. **无需询问即可处理自定义主题。** 如果旧项目引用了自定义的 `themeId`，则当找到匹配的主题对象时，将其合并到新的 `src/lib/constants.ts` 中。如果无法恢复，则将 `themeId` 留在项目 JSON 中；编辑器将回退到 `clean-light` 并在浏览器中警告，你应该在浏览器中记录需要手动恢复的自定义主题。
8. **在可能的情况下合并包元数据。** 模板的依赖项和脚本必须为截图编辑器获胜，但保留与它们直接冲突的无关现有的 `dependencies`, `devDependencies` 和有用的脚本。
9. **不要将模板样本牌组导入到真实的迁移中。** 如果旧项目已经具有牌组或截图，请仅使用模板进行 UI/代码。保留模板样本截图/牌组从迁移项目中排除，以便用户的 App 不会继承无关的示例内容。
10. **使用可丢弃的副本进行自用测试。** 如果用户要求测试或审查迁移而不是实际迁移他们的项目，请将应用复制到临时目录或工作区并在那里运行迁移。只有在用户明确要求实际迁移并回答 **是的** 时才触摸真实检出。

推荐的迁移顺序：

```bash
# 1. 在 repo 外部快照有用的旧文件。
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/tmp/app-store-screenshots-migration-$STAMP"
mkdir -p "$BACKUP_DIR"
cp -R app-store-screenshots.json public src package.json tailwind.config.ts next.config.mjs "$BACKUP_DIR/" 2>/dev/null || true

# 2. 保留必须存活的模板状态和资产。
PRESERVE_DIR="$BACKUP_DIR/preserve"
mkdir -p "$PRESERVE_DIR"
cp app-store-screenshots.json "$PRESERVE_DIR/" 2>/dev/null || true
cp -R public/screenshots "$PRESERVE_DIR/screenshots" 2>/dev/null || true
cp public/app-icon.png "$PRESERVE_DIR/app-icon.png" 2>/dev/null || true

# 3. 将当前模板覆盖旧的 UI 实现。
cp -R "<SKILL_DIR>/template/." "$PWD/"
cp app-store-screenshots.json "$BACKUP_DIR/template-app-store-screenshots.json" 2>/dev/null || true

# 4. 用保留的用户状态/资产覆盖模板样本。
cp "$PRESERVE_DIR/app-store-screenshots.json" app-store-screenshots.json 2>/dev/null || true
mkdir -p public
if [ -d "$PRESERVE_DIR/screenshots" ]; then
  mkdir -p "$BACKUP_DIR/template-samples/public"
  mv public/screenshots "$BACKUP_DIR/template-samples/public/screenshots" 2>/dev/null || true
  cp -R "$PRESERVE_DIR/screenshots" public/screenshots
else
  mkdir -p public/screenshots
fi
cp "$PRESERVE_DIR/app-icon.png" public/app-icon.png 2>/dev/null || true
```

复制后，升级或创建 `app-store-screenshots.json`。如果存在现有的项目文件，则强制就地进行。如果不存在项目文件，但旧幻灯片数据嵌入在 `src/lib/defaults.ts` 或 `src/app/page.tsx` 中，则尽最大努力将其提取到模板的项目 JSON 中，然后再回退到启动幻灯片。优先考虑旧数组或对象命名的 `slides`, `screens`, `features`, `defaultSlides`, `appName`, `tagline`, `theme` 和截图路径。如果旧实现仅包含图像文件，请按路径对 `public/screenshots/**` 进行排序，并从这些文件中尽最大努力生成幻灯片。

使用以下小的 JSON 脚本进行最终的 项目状态强制转换：

```bash
BACKUP_DIR="$BACKUP_DIR" node <<'NODE'
const fs = require("fs");
const path = require("path");

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

const templateState =
  readJson(path.join(process.env.BACKUP_DIR || "", "template-app-store-screenshots.json")) ||
  readJson(PROJECT_FILE) ||
  {};
const existingState = readJson(PROJECT_FILE) || {};
const hasExplicitConnectedCanvas = typeof existingState.connectedCanvas === "boolean";
const existingDecks =
  existingState.slidesByDevice && typeof existingState.slidesByDevice === "object"
    ? existingState.slidesByDevice
    : {};
const hasExistingDecks = Object.keys(existingDecks).length > 0;
const state = {
  ...templateState,
  ...existingState,
  slidesByDevice: hasExistingDecks ? existingDecks : templateState.slidesByDevice || {},
};

const legacySlides =
  Array.isArray(existingState.slides) ? existingState.slides :
  Array.isArray(existingState.screens) ? existingState.screens :
  Array.isArray(existingState.features) ? existingState.features :
  null;

if (legacySlides && !hasExistingDecks) {
  state.slidesByDevice = {
    iphone: legacySlides,
  };
}

function localized(value) {
  if (typeof value === "string") return { [DEFAULT_LOCALE]: value };
  if (value && typeof value === "object") return value;
  return {};
}

function cleanTransform(value) {
  if (!value || typeof value !== "object") return undefined;
  const { x, y, width, height, rotation, zIndex } = value;
  if (![x, y, width, height].every((n) => typeof n === "number" && Number.isFinite(n)) return undefined;
  return {
    x,
    y,
    width: Math.max(1, width),
    height: Math.max(1, height),
    ...(typeof rotation === "number" && Number.isFinite(rotation) ? { rotation } : {}),
    ...(typeof zIndex === "number" && Number.isFinite(zIndex) ? { zIndex } : {}),
  };
}

function firstString(...values) {
  return values.find((value) => typeof value === "string") || "";
}

function migrateSlide(slide) {
  if (!slide || typeof slide !== "object") return null;
  const transforms = {};
  const rawTransforms = slide.transforms && typeof slide.transforms === "object" ? slide.transforms : {};
  for (const [id, transform] of Object.entries(rawTransforms)) {
    const cleaned = cleanTransform(transform);
    if (cleaned) transforms[id] = cleaned;
  }
  const textElements = Array.isArray(slide.textElements)
    ? slide.textElements
        .map((element) => {
          const transform = cleanTransform(element.transform);
          if (!element || typeof element.id !== "string" || !transform) return null;
          return {
            ...element,
            text: localized(element.text),
            transform,
          };
        })
        .filter(Boolean)
    : undefined;

  return {
    ...slide,
    id: typeof slide.id === "string" ? slide.id : `migrated-${Math.random().toString(36).slice(2, 10)}`,
    layout: LAYOUTS.includes(slide.layout) ? slide.layout : "device-bottom",
    label: localized(slide.label),
    headline: localized(slide.headline || slide.title || slide.caption || slide.copy),
    screenshot: firstString(slide.screenshot, slide.image, slide.src, slide.path),
    ...(Object.keys(transforms).length ? { transforms } : { transforms: undefined }),
    ...(textElements && textElements.length ? { textElements } : { textElements: undefined }),
  };
}

state.schemaVersion = 2;
state.connectedCanvas = hasExplicitConnectedCanvas ? existingState.connectedCanvas : false;
state.locales = Array.isArray(state.locales) && state.locales.length ? state.locales : [DEFAULT_LOCALE];
state.locale = state.locales.includes(state.locale) ? state.locale : state.locales[0];
state.device = DEVICE_KEYS.includes(state.device) ? state.device : "iphone";

if (state.slidesByDevice && typeof state.slidesByDevice === "object") {
  for (const [device, slides] of Object.entries(state.slidesByDevice)) {
    if (!DEVICE_KEYS.includes(device)) continue;
    state.slidesByDevice[device] = Array.isArray(slides) ? slides.map(migrateSlide).filter(Boolean) : [];
  }
}

if (!state.slidesByDevice[state.device]) {
  const firstDeviceWithSlides = DEVICE_KEYS.find((device) => state.slidesByDevice[device]?.length);
  if (firstDeviceWithSlides) state.device = firstDeviceWithSlides;
}

fs.writeFileSync(PROJECT_FILE, JSON.stringify(state, null, 2) + "\n");
NODE
```

如果 `package.json` 在模板复制之前存在，则在项目状态强制转换后合并它，而不是留下盲目的覆盖。保留模板的 `dev`, `build` 和 `start` 脚本以及所有编辑器依赖项，然后添加从备份的 `package.json` 中备份的任何旧的非冲突脚本和依赖项。

```bash
BACKUP_DIR="$BACKUP_DIR" node <<'NODE'
const fs = require("fs");
const path = require("path");

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

const oldPkg = readJson(path.join(process.env.BACKUP_DIR || "", "package.json"));
const templatePkg = readJson("package.json");

if (oldPkg && templatePkg) {
  const merged = {
    ...oldPkg,
    ...templatePkg,
    scripts: {
      ...(oldPkg.scripts || {}),
      ...(templatePkg.scripts || {}),
    },
    dependencies: {
      ...(oldPkg.dependencies || {}),
      ...(templatePkg.dependencies || {}),
    },
    devDependencies: {
      ...(oldPkg.devDependencies || {}),
      ...(templatePkg.devDependencies || {}),
    },
  };

  fs.writeFileSync("package.json", JSON.stringify(merged, null, 2) + "\n");
}
NODE
```

然后安装/更新依赖项并验证：

```bash
bun install      # or pnpm install / yarn / npm install
set -o pipefail
bun run build 2>&1 | tee "$BACKUP_DIR/build.log"    # or the detected package-manager equivalent
```

启动开发服务器并在浏览器中验证：

- 工具栏显示 **隔离**，对于迁移的 pre-v2 牌组，除非项目文件已经明确具有 `"connectedCanvas": true`。
- 现有的屏幕、副本、截图路径和应用图标都存在。
- 每个配置区域都存在用于每个配置语言的参考截图文件，或者最终报告列出了缺失的路径。
- 从旧项目中保留的设备牌组不会默默变成模板占位符。如果保留的牌组有空的截图或缺少活动区域的副本，则将其报告为后续操作而不是删除它。
- 对于活动设备，成功进行捆绑导出。
- `app-store-screenshots.json` 包含 `"schemaVersion": 2` 和一个布尔值 `"connectedCanvas"` 值。

## 步骤 1：收集输入（搭建模板之前）

询问用户以下内容。在获得答案之前不要继续：

### 必要的

1. **App 截图** — "您是否已经有了设备的截图？"
   - 如果 **是**：询问 "您的 App 截图在哪里？(实际设备捕获的 PNG 文件)" 并继续。
   - 如果 **否** 并且应用是 **iOS + Swift**：提供伴随捕获技能——"想用 `ios-marketing-capture` 技能 (https://github.com/ParthJadhav/ios-marketing-capture) 自动捕获它们吗？" 如果他们说是，用以下命令安装它：
     ```bash
     npx skills add ParthJadhav/ios-marketing-capture
     ```
     然后让他们首先运行该技能以生成截图，然后再继续到这里。
   - 如果 **否** 并且应用不是 **iOS + Swift**（例如 Android、React Native、Flutter、Web）：捕获技能将不起作用——用户需要手动捕获截图（模拟器/设备截图）才能继续。
2. **App 图标** — "您的 App 图标 PNG 在哪里？"
3. **App 名称** — "您的 App 叫什么名字？"
4. **功能列表** — "列出您应用的功能，按优先级排序。您应用的最主要功能是什么？"
5. **风格方向** — "您想要什么样的风格？您可以 either (a) 选择一个命名的 deep-spec 风格，或 (b) 用您自己的话描述您自己的感觉（温暖/有机，黑暗/忧郁，简洁/极简，大胆/多彩，以及您喜欢的任何参考应用）我将构建一个自定义调色板。模板还附带 `clean-light`, `dark-bold`, `warm-editorial`, `ocean-fresh` 和 `bloom-roast` 调色板预设，您可以从此开始。命名的 deep specs 位于 `style-prompts/` — 请参阅 `style-prompts.md` 获取完整索引。目前可用的：Retro Rubberhose Mascot, Moody Curated Dating, Paper Sticker Skeuomorphic, Dreamy Pastel Couples, Hand-Drawn Editorial Tasks, Glossy 3D K-Beauty Creator。如果用户命名其中一个——或者描述的内容明显匹配其中一个——请首先阅读 `style-prompts/_QUALITY_BAR.md`，然后是匹配的 deep spec 文件，并应用其整个 spec（调色板、渐变、阴影、旋转、每张幻灯片的分解）。

如果用户描述了一个完全自定义的样式，请回退到以下通用视觉设计原则并选择最接近的 deep spec 作为起始参考。

### 可选的

6. **目标商店** — 仅 Apple App Store、仅 Google Play 或两者？这决定了要生成哪个平台的牌组。
7. **iPad / Android 平板电脑截图** — 如果是，什么尺寸和方向？
8. **功能图形** — 想要 1024×500 的 Play Store 旗帜吗？
9. **本地化截图** — 语言？(例如 en, de, es, pt, ja, ar, he)
10. **幻灯片数量** — Apple 允许最多 10 张，Google Play 允许最多 8 张。
11. **品牌颜色 / 字体** — 如果他们想要超出内置预设的自定义主题。
12. **其他说明** — 任何具体内容。

**重要提示**：如果用户在任何时候给出说明，请遵循它们。它们会覆盖技能默认值。

## 步骤 2：搭建模板

### 检测包管理器

优先级：**bun > pnpm > yarn > npm**。

```bash
which bun && echo bun || which pnpm && echo pnpm || which yarn && echo yarn || echo npm
```

### 复制模板

模板位于 `<this skill dir>/template/`——当技能安装时，整个文件夹已经存在于磁盘。复制其内容（不是文件夹本身），保留点文件如 `.gitignore`。

```bash
# Replace <SKILL_DIR> with the absolute path to this skill (the directory containing SKILL.md).
cp -R "<SKILL_DIR>/template/." "$PWD/"
```

如果目标目录已经有一个 `package.json`，在新的搭建过程中询问用户是否覆盖。如果步骤 0 检测到旧实现并且用户选择了 **是的**，则不要再次询问此问题；遵循迁移路径，使用备份目录保留可恢复性，并在模板复制后合并包元数据。

### 安装依赖项

```bash
bun install      # or pnpm install / yarn / npm install
```

### 放置用户的资产

将用户的截图移动到模板期望的布局中：

```
public/
├── app-icon.png                      # ← 用户提供的 App 图标
├── mockup.png                        # ← 已经由模板复制（iPhone 边框）（不要在没有重新测量 PHONE_SCREEN 的情况下替换）
│   └── screenshots/
    ├── apple/
    │   ├── iphone/{locale}/01.png … N.png
    │   └── ipad/{locale}/01.png   … N.png
    └── android/
        ├── phone/{locale}/01.png  … N.png
        ├── tablet-7/{portrait|landscape}/{locale}/...
        └── tablet-10/{portrait|landscape}/{locale}/...
```

模板的启动项目状态位于 `app-store-screenshots.json` 中，不是 `src/lib/defaults.ts`。如果用户命名他们的截图与预期文件名不匹配，则要么重命名，要么使用编辑器中的拖放目标。

否则，用户可以在运行时直接将文件拖放到编辑器中——上传的截图将写入 `public/screenshots/uploaded/<hash>.png` 当开发服务器运行时。

### （可选）预填充初始副本

如果用户提供了标题，请编辑 `app-store-screenshots.json` 以设置：

- `appName`
- `themeId`（内置预设之一，或添加匹配的条目到 `src/lib/constants.ts` 中的 `THEMES`)
- `connectedCanvas` (`true` 对于新的连接画布；迁移的旧牌组应保持 `false`，直到用户有意选择连接画布)
- 每个设备对应的启动幻灯片，包含用户的 `label` + `headline` + 截图路径

否则，保留默认值——用户可以在编辑器中重写副本。

### 启动开发服务器

```bash
bun dev    # → http://localhost:3000
```

告诉用户打开 URL 在浏览器中并开始编辑。编辑器自动保存到 **`app-store-screenshots.json`** 在项目根目录（git 可跟踪）+ `localStorage` 镜像。上传的截图位于 `public/screenshots/uploaded/<hash>.png`。两者都是 git 可跟踪的——将它们提交意味着另一台机器可以 `git clone` 并恢复确切的牌组。

## 步骤 3：指导用户复制

在编辑器中，用户将自行编写标题，但它们通常需要指导。在审查他们的副本或生成建议时应用这些规则。

### 铁律

1. **每行一个想法。** 永远不要用 "和" 连接两件事。
2. **短、常见的词。** 1-2 个音节。不要行话，除非它是特定领域的行话。
3. **每行 3-5 个词。** 必须在 App Store 中以缩略图大小可读。
4. **换行是故意的。** textarea 中的换行直接映射到可见的换行。

### 三种方法

| 类型 | 它做什么 | 示例 |
|------|-------------|---------|
| **描绘一个时刻** | 你想象自己正在使用它 | "检查你的咖啡而不打开应用。" |
| **声明结果** | 你的生活在你使用后是什么样子 | "每个咖啡都有一个家。" |
| **消灭痛点** | 命名一个问题和消灭它 | "永远不会浪费一个伟大的咖啡包。" |

### 从差到好

| 弱的 | 更好的 | 为什么 |
|------|--------|-----|
| 跟踪习惯并保持动力 | 保持你的连续性 | 每个想法，更容易解析 |
| 用 AI 摘要组织任务 | 将笔记转换为下一步 | 结果优先，减少行话 |
| 用标签和收藏夹保存食谱 | 快速找到晚餐 | 销售好处，而不是 UI |

### 叙事弧

用户幻灯片牌组应遵循大致的弧形（跳过不合适的槽位）：

| 槽位 | 用途 |
|------|---------|
| #1 | **英雄 / 主要好处** — 大多数人看到的唯一幻灯片 |
| #2 | **差异化** — 使应用独特的地方 |
| #3 | **生态系统** — 小部件、手表、扩展（如果适用） |
| #4+ | **核心功能** — 每张幻灯片一个，最重要的先 |
| 第二到最后 | **信任信号** — "为 [X] 的人制作..." |
| 最后 | **更多功能** — 列出额外的功能（如果功能不多） |

### 布局变化

跨幻灯片切换 `layout` 字段。编辑器暴露：

- `hero` — 居中标题 + 底部锚定的设备
- `device-bottom` — 相同的构图，较小的标题
- `device-top` — 翻转，设备在标题上方（良好的对比幻灯片）
- `two-devices` — 背面和正面手机层叠
- `no-device` — 独立的大标题（应谨慎使用）
- `split-landscape` — 标题在左侧 + 设备在右侧（仅平板电脑横屏）
- `feature-graphic` — Play Store 旗帜 (1024×500)

永远不要连续使用相同的布局。使用 1-2 个 `inverted`（暗色）幻灯片以获得视觉节奏。

### 跨屏幕 / 跨画布构图

使用连接画布作为设计工具，在步骤 3 中，在选择了叙事弧和布局节奏之后，但在最终导出之前。对于大多数 5 张幻灯片以上的牌组，默认计划一个雅致的跨屏幕时刻。对于 8-10 张幻灯片的牌组，最多使用两个。对于简短、正式或合规性重的牌组，零也是可以的。目标是“这些截图属于一起”，而不是“一个巨大的海报被切成几块”。

好的跨屏幕模式：

- 一个超大的手机、平板电脑或截图马赛克通过相邻屏幕的 10-30% 宽度连接，而每个导出的裁剪仍然可以作为一个完整的广告阅读。
- 一个背景地平线、照片、渐变、涂鸦路径、波形、星空、贴纸轨迹或地图路线继续穿过接缝。
- 一个角色、3D 对象、浮动芯片或通知从屏幕一个屏幕探出作为次要视觉效果，而不是整个信息。
- 相关想法形成一对：问题 → 解决方案，之前 → 之后，概述 → 细节，计划 → 结果。

坏的跨屏幕模式：

- 分割标题、应用名称、价格、法律文本、评分、CTA 或关键 UI 跨接缝。
- 在接缝上居中一个巨大的手机，以便每个裁剪只显示半个设备，没有明确的好处。
- 在每张幻灯片中使用跨屏幕移动；它成为一个噱头，使牌组更难浏览。
- 切割面孔、角色眼睛、关键图表数字、产品声明或 App Store 要求的信息。
- 让观众理解轮播是一个不间断的海报。每个导出的 PNG 必须仍然可以通过一秒钟的独立测试。
- 让阴影、贴纸或部分对象看起来像是偶然裁剪的。如果它跨越边界，请使用缩放、阴影、旋转或延续来故意制作出血。

放置规则：

- 仅使用相邻屏幕，除非故意制作 3 屏幕全景是整个概念。
- 保持所有文本完全在一个单独的导出屏幕内，带有安全的边距。
- 让非关键视觉的 10-30% 跨越接缝；仅当背景颜色不同时，用共享对象、匹配阴影方向或设计的过渡带桥接它们。
- 审查两个视图：缩放出的连接画布必须看起来连贯，每个单独导出的屏幕仍然可以销售一个想法。

## 视觉设计原则

这些规则是从研究野外最好的 App Store 截图（Superlist, Headspace, CRED, (Not Boring) Camera, Arc Search, Linktree, Gentler Streak 等）中得出的。无论用户选择哪个主题预设，这些规则都适用。特定于主题的标记（字体、调色板、强调）位于 `style-prompts.md` 中——请将用户指向那里。

### 1. 背景是一个设计过的表面——永远不要白色

纯白色是业余的迹象。每个伟大的牌组都使用一个故意的表面：饱和色块、温暖的奶油/浅白色 (`#F4F1EC` 似的), 深海军裤/近乎黑色，或渐变。背景可以每张幻灯片更改（Headspace, Linktree 这样做），但它必须看起来是故意的，而不是默认的。

### 2. 标题占主导地位

标题大约占据画布的 **顶部 30-40%**——比典型的网络英雄大得多。如果一个人在缩略图大小下无法阅读它，则需要重新设计。

### 3. 标题内部混合强调

几乎每个伟大的标题都有一个词与其他词的样式不同——对比色、斜体脚本、更重的权重或手绘下划线。示例：
- Superlist: "拥有 **你的整个一天**"（脚本 + 珊瑚）
- Headspace: "压力 **更少**"（`less` 橙色对黑色）
- Arc Search: "**最快** 的搜索方式。**最干净** 的浏览方式。"（紫色 / 蓝色）

单色标题看起来较弱。每张幻灯片选择一个强调词。

### 4. 装饰性强调是规则，不是例外

顶级牌组在大多数幻灯片中至少叠加以下之一：

- 手绘曲线、箭头、涂鸦 (Superlist)
- 闪烁/发光 (Gentler Streak, Arc)
- 标签徽章在视觉上（"超级原始", "电影感", "LUT"）
- 带有真实统计数据的浮动小部件芯片 ("赚取 $3,630", "11,175 步")——它们在不使用副本的情况下讲述故事
- 仅在英雄幻灯片中显示的奖项锁定（Apple Design Award, Webby, 星级）
