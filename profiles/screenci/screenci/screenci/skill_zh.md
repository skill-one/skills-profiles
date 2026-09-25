# ScreenCI 视频和指南技能

当任务涉及现有项目中的 ScreenCI 视频录制时（例如创建视频、将流程展示为视频或编辑 `.screenci.ts` / `screenci.config.ts` 文件），请使用此技能。提问者通常是团队中不编码的成员：市场营销人员、支持主管或从 ScreenCI 网络应用程序中粘贴了提示的文档编写人员。参见 [向提问者汇报](#reporting-back-to-the-person)。

路由：

- 如果用户提供了视频上下文的 URL，请首先使用 `playwright-cli` 技能来发现真实的页面流程、稳定的选择器和 cookie/同意步骤，然后再编辑脚本。切勿编写自己的 Playwright 脚本来探索：它以未登录状态启动，行为与录制器完全不同。
- 如果用户提供了目标页面的源代码，通常不需要先进行浏览器探索。
- 如果请求仅涉及应用程序/源代码更改（不涉及录制），请勿使用此技能。

## 快速入门

如果用户粘贴了包含设置代码（`SC-XXXX-XXXX`）的提示，该项目是使用该代码设置的，而不是 `init`。在应用程序的存储库（或空文件夹）中运行以下命令来录制（或设置），并遵循其打印的简要说明：

```bash
npx screenci@latest setup SC-XXXX-XXXX
# --name "<项目名称>" 选择新项目的名称（默认：文件夹名称）
# --dir <路径> 当 ./screenci 已经属于另一个项目时
```

简要说明包含任务、应用程序 URL，以及（对于编辑）要更改的脚本。`setup` 将项目范围的 `SCREENCI_SECRET` 写入 `screenci/.env`。在存储库中，它使用存储库为项目持有的工作区（无论它位于何处）；如果没有，则拉取 ScreenCI 持有的脚本（或搭建新项目）。编辑/重新录制代码从该人查看的版本开始：阅读简要说明的 **起始点** 部分了解工作区如何与之相关。也要阅读其 **站点** 部分：当脚本命名您无法在此启动的开发服务器时，它告诉您使用 `video.use({ baseURL })` 将视频指向实时站点（配置和其他视频保持不变），在录制之前检查流程期望的数据是否存在，并在对生产站点执行任何实际操作的步骤之前询问该人（订单、付款、电子邮件、删除）。`preview` 和 `export` 上传 `screenci/` 脚本，以便每个版本保留其源代码，并且创建代码的人会在他们的浏览器中看到结果。

否则项目已经初始化。在 `recordings/` 中添加或编辑脚本。如果您正在创建新视频，请删除启动器 `recordings/example.screenci.ts`。

```bash
# 反复验证直到变为绿色
npx screenci test

# 使用正常的 Playwright 过滤器运行子集
npx screenci test recordings/signup.screenci.ts --grep "填写付款详情"

# 测试通过后，录制免费的实时预览并打印视频链接
npx screenci preview "视频标题"

# 仅在想要完成的视频时才导出
npx screenci export
```

`test` 转发正常的 `playwright test` 参数，并仍然注入解析的 `screenci.config.ts`。`--config`/`-c` 和 `--verbose`/`-v` 保留用于 ScreenCI CLI，不转发给 Playwright。

## 向提问者汇报

- 向您发送提示的人通常是团队中不编码的成员，可能不使用终端。不要让他们运行命令、打开文件或阅读脚本。
- 使用 plain language 汇报：视频展示了什么，您更改了什么，以及需要他们注意什么。除非他们要求，否则不要提供选择器、文件路径或命令输出。
- 如果需要他们，请明确说明要点击什么（您在浏览器中打开的登录卡片、ScreenCI 应用程序中的新提示），并等待他们。
- 当视频针对实时生产站点录制时，某些步骤会对现实世界执行操作：下订单、付款、发送电子邮件或邀请、删除或发布内容、更改账户或付款设置。在运行此类步骤之前，请停止并使用 plain language 询问该人在生产站点上是否可以执行该操作，并等待答案。不要猜测，也不要重写流程以避免该步骤；如果他们说不，请报告需要测试帐户或安全环境。读取和导航可以无需询问，并且在开发、预发布或测试部署（`dev.`、`staging.`、`test.` 或预览地址）上的所有内容也是如此：在那里可以自由操作。
- 不要要求密码、一次性代码或 API 密钥；`screenci login` 是唯一的登录路径。
- 在您的最后一条消息中，以单独的最后一行打印 `preview` 打印的视频链接（或管道运行链接）。
- 按照由 `setup` 打印的简要说明的方式交付结果：您自己录制的实时预览、您触发的管道运行或您打开的拉取请求。不要因为存储库恰好有 CI 就切换到其他路径；只有要求管道运行的代码才会在一个上完成。

## ScreenCI 添加的内容

ScreenCI 使用 Playwright 风格的 `.screenci.ts` 文件加上录制辅助工具：

- `video()` 声明每个测试一个输出视频。
- `hide()` 从最终录制中剪切设置和加载部分。
- `autoZoom()` 跟随导航和点击驱动的流程，使用平滑的相机运动。用于目标之间的移动。
- `zoomTo()` / `resetZoom()` 对表单和稳定的编辑部分保持固定帧。
- `video.narration({ ... })` 在每个视频上都是强制性的（见下文）。
- `video.overlays({ ... })` 使用 HTML/CSS 或 React 文件（保存在 `recordings/assets/` 中）在视频上绘制（元素周围的环、标签、标题卡片）。参见 [参考资料/overlays.md](references/overlays.md)。
- `screenshot()` 声明每个测试一个静态图像，而不是视频（见 [屏幕截图](#screenshots)）。

```ts
import { video, voices } from 'screenci'

// Voice 是一个渲染选项（如何朗读旁白），不是旁白规范的一部分。
video.renderOptions({ narration: { voice: { name: voices.Ava } } }).narration({
  en: {
    intro:
      '此视频展示了如何更新您的付款详情并保存更改。',
    explainForm:
      '我们从付款页面开始，更新公司名称、电子邮件和税号。',
    saving: '现在我们保存更改并等待确认消息。',
    nextPage:
      '接下来，我们打开发票部分以确认新的付款详情正在使用。',
  },
})('更新付款详情', async ({ page, narration }) => {
  await narration.intro()
  await narration.explainForm()
  await narration.saving.start()
  await page.getByRole('button', { name: 'Save changes' }).click()
  await narration.saving.end()
  await narration.nextPage()
  await page.getByRole('link', { name: 'Invoices' }).click()
})
```

### 旁白

- 在每个视频上声明 `video.narration({ ... })` 并在整个演示中说话。传递一个扁平的 `cue -> text` 对象（跨语言共享）或一个按语言键入的对象（`en`、`es`、...）。
- 开头行必须说明视频的目的，然后继续进行演练。
- **旁白流程，而不是点击。** 每个提示描述用户正在实现的目标（“邀请您的团队成员并设置他们的角色”），而不是机制（“现在点击蓝色按钮”）。少数涵盖整个流程的广泛提示比每个动作一个提示更好。
- **使用产品的自己的词汇。** 从录制的应用程序的源代码和屏幕上的副本（页面标题、按钮标签、域名术语）中提取名词和动词，以便旁白听起来像产品的原生语言。
- 从 `narration` 固定装置触发提示：`await narration.key()` 在继续之前运行完整行。当旁白应与下一个动作重叠时，使用 `await narration.key.start()`，并且 `await narration.key.end()` 在稍后关闭该提示，尤其是在可见导航或路由更改之前。
- 当一行需要停顿时，暂停标签（`[短暂停]`、`[中等暂停]`、`[长暂停]`）是合适的。**不要自己添加 `[pronounce: ...]` 标签。** 语音正确地说品牌名称、产品术语和域名。只有在有人说一个词的发音不正确或要求特定发音时，才添加发音标签，并且只在那个词上添加。

## 必须遵循的约定

每个视频必须遵循这些：

- **每个视频必须有旁白，没有例外。** 没有旁白的视频是不可接受的。
- **以视频的目的开头**，然后以高级别旁白流程。
- **表单中仅使用示例数据。** 使用合理的虚构姓名、电子邮件和地址（例如 `Emma Carter`、`emma@aperturebio.com`），切勿使用真实人物或真实联系详情。
- **从请求的页面开始。** 可见视频从用户请求的页面开始。
- **隐藏初始设置。** 将页面加载、导航到起始页面、加载旋转器和 cookie-banner 取消操作包裹在 `hide()` 中。在初始导航后，在该隐藏块内找到并点击任何 cookie 同意接受按钮。登录不是其中一部分：录制已经以登录状态开始，参见 [参考资料/login.md](references/login.md)。
- **在隐藏设置后，通过点击可见地导航**，而不是 `page.goto()`。
- **在搜索框、组合框、自动完成或命令菜单中输入后，优先使用鼠标驱动的选择**：当存在可点击目标时，点击可见结果而不是 `press('Enter')`。
- **在定位方法已经涵盖交互的情况下，优先使用原生 Playwright API 覆盖 `page.evaluate()`**（例如 `locator.blur()`）。
- **覆盖是 HTML/CSS 或 React，使用录制的应用程序自己的颜色，并在视频中共享。** 当被要求在视频上绘制时，切勿自己编写 SVG 或选择颜色：将应用程序的主题读入一个 `recordings/assets/theme.ts`（或 `theme.css`），在 `recordings/assets/` 中将覆盖作为组件构建，并在项目的每个视频中重用相同的文件。参见 [参考资料/overlays.md](references/overlays.md)。
- **优先选择默认操作选项。** 对于 `autoZoom()` 和定位器动作（`click`、`fill`、`pressSequentially`、`check`、`selectOption`、...），从 ScreenCI 的默认值开始。不要在 `fill()`/`pressSequentially()` 之前添加单独的 `click()` 只是为了聚焦，并且不要添加 `zoom`/`click`/`position`/时间设置覆盖，除非用户要求或流程明显需要它。

## 屏幕截图

`screenshot()` 生成一个静态图像，而不是视频：相同的 Playwright 风格的主体，相同的覆盖和品牌，没有旁白和相机。当用户要求图像（README 快照、社交卡片、文档图形）而不是演练时，使用它。

```ts
import { screenshot } from 'screenci'

screenshot('付款概览', async ({ page, crop }) => {
  await page.goto('https://app.example.com/settings/billing')
  // 裁剪到重要的部分。定位器裁剪会在每次重新录制时重新解析；填充会在您配置的背景上框定它。
  await crop(page.getByRole('region', { name: 'Plan' }), { padding: 48 })
})
```

- 旁白规则不适用：静态图像是沉默的，因此切勿在 `screenshot()` 中添加 `narration`。相机运动和音频被忽略。
- 仅保留最终页面状态，因此 `hide()` 是无操作（screenci 警告），`autoZoom()` / `zoomTo()` 没有要动画的。将页面驱动到您想要的状态，然后裁剪。
- 静态图像和视频共享相同的 `.screenci.ts` 文件：文件可以自由混合 `video()` 和 `screenshot()` 调用。要抓取视频中出现的某个时刻的静态图像，请在 `video()` 身体内部调用 `page.screenshot({ name: 'Dashboard' })`。
- 裁剪是在代码中用 `screenshot.renderOptions({ screenshot: { margin, aspectRatio, format } })` 编写的。静态图像没有浏览器编辑器，因此外观更改意味着编辑脚本并重新导出。
- `preview` 和 `export` 将静态图像视为视频；导出的文件命名为 `<标题>.<语言>.png`。
- 完整参考：[屏幕截图](https://screenci.com/docs/guides/screenshots)。

## 缩放

对于编辑密集型部分，优先使用稳定的手动缩放；使用 `autoZoom()` 进行目标之间的移动，并在导航或页面更改之前让每个 `autoZoom()` 块完成（在下一页上启动新的块）。保持 `autoZoom()` 使用稀疏：通过目标之间的移动而不是简单的文本输入来证明每个块。

```ts
// 表单和稳定的编辑：固定帧。
await zoomTo(page.getByRole('form', { name: /profile settings/i }))
await page.getByLabel('Name').fill('Emma Carter')
await page.getByRole('checkbox', { name: 'Email notifications' }).check()
await page.getByRole('button', { name: 'Save changes' }).click()
await resetZoom()

// 导航和点击驱动的流程：跟随移动。
await autoZoom(async () => {
  await page.getByRole('link', { name: 'Reports' }).click()
  await page.getByRole('button', { name: 'Open filters' }).click()
  await page.getByRole('option', { name: 'Last 30 days' }).click()
  await page.getByRole('button', { name: 'Apply' }).click()
})
```

## 连接到帐户（可选）

`test` 和 `preview` 无需帐户：如果没有 `SCREENCI_SECRET`，`preview` 在本地匿名试用会话（仅预览，无渲染）下录制和预览。试用预览多语言视频（一次最多 3 种语言），因此请保持视频声明的语言；不要将它减少为一种语言用于试用。在网页编辑器中注册会声明试用并自动升级正在运行的 `preview` 会话。提及这一点并继续进行。

`export` 需要一个具有活动付费订阅的帐户。要将现有组织连接起来，请将 `SCREENCI_SECRET` 复制到 `screenci/.env`（它不会阻止编写、测试或匿名编辑）：

1. **传递给 init:** `npm init screenci@latest <SCREENCI_SECRET> -- --yes` 将其写入 `screenci/.env`。
2. **秘密页面:** 请用户从他们的秘密页面将 `SCREENCI_SECRET` 复制到 `screenci/.env`。组织秘密在项目中共享。在他们这样做时继续构建和测试；只有 `preview`（具有帐户）和 `export` 需要它。

`SCREENCI_SECRET` 是唯一的配置凭证：没有第二个令牌需要创建或粘贴。在 `export` 之后不要添加单独的升级推销；除非用户询问计划，否则报告结果 URL。

## 预览和导出工作流

1. 在 `recordings/` 中添加或编辑 `.screenci.ts` 文件（如果创建新视频，请删除 `example.screenci.ts`）。
2. 运行 `npx screenci test` 直到它通过。修复选择器/流程/旁白并重新运行，直到变为绿色。
3. 一旦测试通过，请自己运行 `npx screenci preview "<标题>"`。不要先导出。它录制视频的实时预览（免费，无渲染），打印视频链接并退出。`preview` 无需帐户：如果没有 `SCREENCI_SECRET`，它在免费的匿名试用会话下运行。
4. 向用户报告 `preview` 打印的视频链接，以便他们可以在浏览器中查看和改进视频。
5. 仅当用户想要完成的视频时，运行 `npx screenci export`。导出需要具有活动付费订阅的帐户：没有它，`export` 会拒绝并打印注册链接（匿名试用仅预览）。有一个，它会记录更改、渲染、等待并下载到 `./exports/`。ScreenCI 为每个重新录制的视频写入 `.screenci/<视频名称>/recording.mp4` 和 `data.json`。导出不会更改视频的公共 URL 服务哪个版本，除非您传递 `--select`；只有在用户想要发布新渲染时才这样做。
6. 在 `export` 之后，报告它打印的 URL，以便用户可以打开它（单个视频链接其页面，例如 `https://app.screenci.com/project/<projectId>/video/<videoId>?export=...`；多个视频链接运行页面 `https://app.screenci.com/export/...`）。

`screenci init`（或 `npm init screenci`）搭建新项目，如果已存在则故意失败（`screenci/` 已经存在）。这是预期的：继续使用现有项目，不要删除它以重新初始化。设置代码（`screenci setup`）拒绝另一个项目的孤岛；然后传递 `--dir <路径>`。

## 具体任务

- **导出视频** [参考资料/export.md](references/export.md)
- **在视频上绘制**（高亮、标注、徽章、标题卡片）[参考资料/overlays.md](references/overlays.md)。简而言之：HTML/CSS 或 React，颜色来自应用程序自己的主题，每个项目一个共享的覆盖文件集，切勿手绘 SVG。
- **录制一个需要登录的应用程序** [参考资料/login.md](references/login.md)。简而言之：切勿编写登录脚本，并且切勿向该人要密码或代码。运行 `npx screenci login`，让他们在打开的浏览器中登录并点击卡片的按钮，然后运行 `npx screenci login --wait`（这会阻塞直到他们完成；切勿只是结束您的回合）。录制从该会话开始，因此视频本身不包含登录。
- **从 CI 录制**：切勿自行添加 CI 管道，并且在被要求时切勿手写。该人点击 **添加到 CI** 在网页应用程序中的项目页面，并将 CI 的提示粘贴给您；该简要（`/add-to-ci.md`）铸造 CI 密钥，将其存储在提供者的秘密存储中，并添加管道（对于 GitHub Actions，`npx screenci ci-workflow`，模板在 `/docs/ci-setup.md#其他提供者` 中为 GitLab CI、CircleCI、Buildkite 和其他）。`screenci init` 除非传递 `--github-workflow`，否则不会写入工作流。
- **了解产品**：`screenci context` 打印组织的 AI 上下文（存储库、站点 URL、您是否可以启动应用程序、团队的笔记）。在您自己启动应用程序之前设置 `SCREENCI_APP_LAUNCHED_BY=agent`。
- **在您编写选择器之前探索应用程序**：使用 `playwright-cli` 技能，切勿使用您自己的 Playwright 脚本。手写的脚本以未登录状态启动，启动与录制器不同的浏览器，并让您追逐录制永远不会看到的定位器。当应用程序需要保存会话时，首先加载保存的会话：`playwright-cli state-load screenci/.screenci/auth/default.json`。
- **录制在机器人检查上结束**（“请稍等…”、“执行安全验证”、挑战页面）而正常浏览器可以很好地加载网站：录制器运行 Chromium 的无头 shell，其用户代理是某些机器人保护拒绝的。在 `screenci.config.ts` 中的 `use` 中设置一个正常的桌面用户代理并重新运行：

  ```ts
  use: {
    userAgent:
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
  }
  ```

  只做一次，在配置中，而不是在弃用脚本中探测启动选项。这是一个录制环境问题，而不是选择器问题，因此无论您如何重写视频代码，都无法修复它。
