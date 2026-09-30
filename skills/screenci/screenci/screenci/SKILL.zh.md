---
name: screenci
description: 在已初始化的项目中，通过编辑 `.screenci.ts` 文件并运行 Screenci 工作流来创建、展示和指导 ScreenCI 视频。
---

# ScreenCI 视频和指南技能

当任务涉及现有项目中的 ScreenCI 视频录制时使用此技能：创建视频、将流程展示为视频，或编辑 `.screenci.ts` / `screenci.config.ts` 文件。提问的人通常是团队中的非编码成员：市场营销人员、支持主管或从 ScreenCI 网络应用程序中粘贴了提示的文档编写者。参见 [向提问者汇报](#reporting-back-to-the-person)。

路由：

- 如果用户提供了视频上下文的 URL，请首先使用 `playwright-cli` 技能来发现真实的页面流程、稳定的选择器和 cookie/同意步骤，然后再编辑脚本。切勿编写自己的 Playwright 脚本来探索：它以未登录状态启动，行为与录制器完全不同。
- 如果用户提供了目标页面的源代码，通常不需要先进行浏览器探索。
- 如果请求仅涉及应用程序/源代码更改（非录制），则不要使用此技能。

## 快速入门

如果用户粘贴了包含设置代码（`SC-XXXX-XXXX`）的提示，该项目是使用该代码设置的，而不是 `init`。在应用程序的存储库（或空文件夹）中运行以下命令来录制（或设置）并遵循其打印的简要说明：

```bash
npx screenci@latest setup SC-XXXX-XXXX
# --name "<项目名称>" 选择新项目的名称（默认：文件夹名称）
# --dir <路径> 当 ./screenci 已经属于另一个项目时
```

简要说明包含任务、应用程序 URL（对于编辑）要更改的脚本。`setup` 将项目范围的 `SCREENCI_SECRET` 写入 `screenci/.env`。在存储库中，它使用存储库为项目保留的工作区（无论它位于何处）；如果没有，则拉取 ScreenCI 保留的脚本（或创建新的项目架构）。编辑/重新录制代码从该人查看的版本开始：阅读简要说明的 **起始点** 部分以了解工作区如何与之相关。也要阅读其 **站点** 部分：当脚本名称的开发服务器在此处无法启动时，它告诉您使用 `video.use({ baseURL })` 将视频指向实时站点（配置和其他视频保持不变），在录制之前检查流程期望的数据是否存在，并在生产站点上对任何作用于真实世界的步骤（订单、付款、电子邮件、删除、发布）之前询问该人。`preview` 和 `export` 上传 `screenci/` 脚本，以便每个版本保留其源代码，并且创建代码的人会在其浏览器中看到结果打开。

否则，项目已经初始化。在 `recordings/` 中添加或编辑脚本。如果您正在创建新视频，请删除启动器 `recordings/example.screenci.ts`。

```bash
# 反复验证，直到变为绿色
npx screenci test

# 使用正常的 Playwright 过滤器运行子集
npx screenci test recordings/signup.screenci.ts --grep "填写账单详情"

# 测试通过后，录制免费的实时预览并打印视频链接
npx screenci preview "视频标题"

# 仅在需要完成的视频时导出
npx screenci export
```

`test` 转发正常的 `playwright test` 参数，并仍然注入解析的 `screenci.config.ts`。`--config`/`-c` 和 `--verbose`/`-v` 保留用于 ScreenCI CLI，不转发给 Playwright。

## 向提问者汇报

- 发送您提示的人通常是团队中的非编码成员，可能不使用终端。不要要求他们运行命令、打开文件或阅读脚本。
- 使用 plain language 汇报：视频显示的内容、您更改的内容以及需要他们注意的事项。除非他们要求，否则不要提供选择器、文件路径或命令输出。
- 如果需要他们，请明确说明要点击的内容（您打开的浏览器中的登录卡片、ScreenCI 应用程序中的新提示），并等待他们。
- 当视频针对实时生产站点录制时，某些步骤会作用于真实世界：下订单、付款、发送电子邮件或邀请、删除或发布内容、更改账户或账单设置。不要在生产站点上提交此类表单：填写完整并在此完成的表单上结束步骤（将光标停留在提交按钮上 `hover()`）。叙述中永远不会提到表单未提交：将完成的表单叙述为步骤的自然结束（“添加您的卡片详情，您的订单已准备就绪”）。在开发、预发布或测试部署上，正常提交即可。
- **公司视角。** 叙述为公司制作的产品（“我们”、“我们的”），向其用户（“您”）说话，永远不要以第三人称描述公司及其产品（“Acme 让您...”、“他们的仪表板”、“公司发送...”）。命名产品是可以的（“在 Acme Reports 中，您可以...”）；从外部谈论公司是不可以的。
- **将演示作为真实情况呈现。** 叙述、覆盖层或标题中永远不要提到数据是模拟的、样本的、测试的、演示的或虚构的，或者表单未实际提交。参考屏幕上显示的数据（“Emma 的订单”、“您的新项目”）。
- **使用产品的自身词汇。** 从录制的应用程序的源代码和屏幕上的副本（页面标题、按钮标签、域名术语）中提取名词和动词，以便叙述听起来像产品的原生语言。
- 从 `narration` 固定装置触发提示：`await narration.key()` 在继续之前运行完整行。当叙述应与下一个操作重叠时，使用 `await narration.key.start()`，并在可见导航或路由更改之前使用 `await narration.key.end()` 关闭该提示。
- 当一行需要停顿时，暂停标签（`[短暂停]`、`[中暂停]`、`[长暂停]`）是合适的。**切勿自行添加 `[发音: ...]` 标签。** 语音正确地说品牌名称、产品术语和域名几乎总是正确的。仅在某人说发音错误或要求特定发音时添加发音标签，并且仅在单词上添加。

## 必须遵守的约定

每个视频都必须遵循这些约定：

- **每个视频必须有叙述，没有例外。** 没有叙述的视频是不可接受的。
- **以视频的目的开始**，然后以高级别的形式叙述流程。
- **仅使用模拟数据，并呈现为真实情况。** 填写表单和创建记录时使用合理的虚构姓名、电子邮件、地址和金额（例如 `Emma Carter`、`emma@aperturebio.com`），切勿使用真实人物或真实联系详情。视频永远不会说数据是模拟的、样本的或虚构的。
- **不要在生产站点上提交真实世界的表单。** 当在实时生产站点上提交表单会导致下订单、付款、发送电子邮件或邀请、删除或发布内容、更改账户或账单设置时，请完全填写并在此处结束步骤：在完成的表单上结束步骤，光标停留在提交按钮上 `hover()`。叙述中永远不会提到表单未提交：将完成的表单叙述为步骤的自然结束（“添加您的卡片详情，您的订单已准备就绪”）。在开发、预发布或测试部署上，正常提交即可。
- **公司视角。** 叙述为公司制作的产品（“我们”、“我们的”），向其用户（“您”）说话，永远不要以第三人称描述公司及其产品（“Acme 让您...”、“他们的仪表板”、“公司发送...”）。命名产品是可以的（“在 Acme Reports 中，您可以...”）；从外部谈论公司是不可以的。
- **从请求的页面开始。** 可见视频从用户请求的页面开始。
- **隐藏初始设置。** 将页面加载、导航到起始页面、加载旋转器和 cookie-banner 消息包裹在 `hide()` 中。初始导航后，在该隐藏块内找到并点击任何 cookie 同意接受按钮。登录不是这个部分的一部分：录制已经以登录状态开始，参见 [references/login.md](references/login.md)。
- **在隐藏设置后以点击方式可见地导航**，而不是 `page.goto()`。
- **在搜索框、组合框、自动完成或命令菜单中输入后，优先使用鼠标驱动的选择**：当存在可点击目标时，点击可见结果，而不是 `press('Enter')`。
- **优先使用原生 Playwright API 而不是 `page.evaluate()`**，当一个定位器方法已经涵盖了交互（例如 `locator.blur()`）。
- **覆盖层是 HTML/CSS 或 React，使用录制的应用程序自己的颜色进行样式化，并在视频中共享。** 当被要求在视频上绘制覆盖层时，切勿自行编写 SVG 或选择颜色：将应用程序的主题读入一个 `recordings/assets/theme.ts`（或 `theme.css`），在 `recordings/assets/` 中将覆盖层作为组件构建，并在项目的每个视频中重用这些相同的文件。参见 [references/overlays.md](references/overlays.md)。
- **优先使用默认操作选项。** 对于 `autoZoom()` 和定位器操作（`click`、`fill`、`pressSequentially`、`check`、`selectOption`、...），从 ScreenCI 的默认值开始。不要在 `fill()`/`pressSequentially()` 之前添加单独的 `click()` 仅为了聚焦，并且除非用户要求或流程明显需要，否则不要添加 `zoom`/`click`/`position`/时间设置覆盖。

## 截图

`screenshot()` 生成静态图像而不是视频：相同的 Playwright 风格主体、相同的覆盖层和品牌，没有叙述和相机。当用户要求图像（README 快照、社交卡片、文档图形）而不是演练时使用它。

```ts
import { screenshot } from 'screenci'

screenshot('账单概览', async ({ page, crop }) => {
  await page.goto('https://app.example.com/settings/billing')
  // 裁剪到重要部分。定位器裁剪在每次重新录制时重新解析；填充在您的配置背景上框定它。
  await crop(page.getByRole('region', { name: 'Plan' }), { padding: 48 })
})
```

- 叙述规则不适用：静态图像是沉默的，因此切勿在 `screenshot()` 中添加 `narration`。相机运动和音频也被忽略。
- 仅保留最终页面状态，因此 `hide()` 是 no-op（screenci 警告），`autoZoom()` / `zoomTo()` 没有要动画的内容。将页面驱动到您想要的状态，然后裁剪。
- 静态图像和视频共享相同的 `.screenci.ts` 文件：一个文件可以自由地混合 `video()` 和 `screenshot()` 调用。要获取视频中出现的某个时刻的静态图像，请在 `video()` 身体内部调用 `page.screenshot({ name: 'Dashboard' })`。
- 布局是在代码中用 `screenshot.renderOptions({ screenshot: { margin, aspectRatio, format } })` 编写的。静态图像没有浏览器编辑器，因此外观更改意味着编辑脚本并重新导出。
- `preview` 和 `export` 将静态图像视为视频；导出的文件命名为 `<标题>.<语言>.png`。
- 完整参考：[截图](https://screenci.com/docs/guides/screenshots)。

## 缩放

对于编辑密集型部分，优先使用稳定的手动缩放；使用 `autoZoom()` 进行目标之间的移动，并在导航或页面更改之前让每个 `autoZoom()` 块完成（在下一页上启动新的块）。保持 `autoZoom()` 的使用稀疏：通过目标之间的移动来证明每个块，而不是简单的文本输入。

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

## 连接到账户（可选）

`test` 和 `preview` 无需账户：如果没有 `SCREENCI_SECRET`，`preview` 在本地匿名试用会话（仅预览，无渲染）下录制和预览。试用会话也预览多语言视频（最多同时 3 种语言），因此请保留视频声明的语言；不要将语言减少为一种语言用于试用。在 Web 编辑器中注册会自动声明试用并自动升级正在运行的 `preview` 会话。提及这一点并继续进行。

`export` 需要一个具有活动付费订阅的账户。要将现有组织连接起来，请将 `SCREENCI_SECRET` 放入 `screenci/.env`（它不会阻止编写、测试或匿名编辑）：

1. **传递给 init：** `npm init screenci@latest <SCREENCI_SECRET> -- --yes` 将其写入 `screenci/.env`。
2. **密钥页面：** 要求用户将 `SCREENCI_SECRET` 从他们的密钥页面复制到 `screenci/.env`。组织密钥跨项目共享。在他们进行操作时继续构建和测试；只有 `preview`（具有账户）和 `export` 需要它。

`SCREENCI_SECRET` 是唯一的凭证来配置：没有第二个令牌要创建或粘贴。在 `export` 之后不要添加单独的升级推销；除非用户询问关于计划，否则报告结果 URL。

## 预览和导出工作流

1. 在 `recordings/` 目录下添加或编辑 `.screenci.ts` 文件（创建新视频时请删除 `example.screenci.ts`）。
2. 运行 `npx screenci test` 直到测试通过。修复选择器/流程/旁白并重新运行，直到变为绿色。
3. 测试通过后，自行运行 `npx screenci preview "<标题>"`。不要先导出。它录制视频的实时预览（免费，无需渲染），打印视频链接并退出。`preview` 功能无需账户：没有 `SCREENCI_SECRET` 时，它运行在免费匿名试用会话下。
4. 报告 `preview` 打印的视频链接，以便用户可以在浏览器中查看和优化视频。
5. 仅当用户需要最终视频时运行 `npx screenci export`。导出需要具有活跃付费订阅的账户：没有账户，`export` 会拒绝并打印注册链接（匿名试用仅限预览）。有账户时，它会记录更改、渲染、等待并下载到 `./exports/`。ScreenCI 每个重录视频会写入 `.screenci/<视频名>/recording.mp4` 和 `data.json`。导出不会更改视频公开URL指向的版本，除非你传递 `--select`；仅在用户需要发布新渲染时才这样做。
6. 导出后，报告它打印的URL，以便用户可以打开（单个视频链接其页面，例如 `https://app.screenci.com/project/<projectId>/video/<videoId>?export=...`；多个视频链接运行页面 `https://app.screenci.com/export/...`）。

`screenci init`（或 `npm init screenci`）搭建新项目，如果已存在会故意失败（`screenci/` 已存在）。这是预期的：继续使用现有项目，不要删除它以重新初始化。设置代码（`screenci setup`）会拒绝另一个项目的孤岛；然后传递 `--dir <路径>`。

## 具体任务

- **导出视频** [参考资料/export.md](参考资料/export.md)
- **在视频上绘制**（高亮、标注、徽章、标题卡）[参考资料/overlays.md](参考资料/overlays.md)。简而言之：HTML/CSS 或 React，颜色来自应用自身的主题，每个项目共享一套覆盖文件，绝不手绘SVG。
- **录制登录后的应用** [参考资料/login.md](参考资料/login.md)。简而言之：绝不脚本登录，绝不要求对方提供密码或验证码。运行 `npx screenci login`，让他们在打开的浏览器中登录并点击卡片的按钮，然后运行 `npx screenci login --wait`（它会阻塞直到完成；绝不直接结束你的操作）。录制从该会话开始，因此视频中不包含登录过程。
- **从CI录制**：绝不自行添加CI流程，也不在要求时手写。用户在Web应用的项目页面点击 **添加到CI** 并粘贴其提示；该简短（`/add-to-ci.md`）会生成CI密钥，存储在提供者的密钥库中，并添加流程（GitHub Actions使用 `npx screenci ci-workflow`，模板在 `/docs/ci-setup.md#其他提供者` 中适用于GitLab CI、CircleCI、Buildkite等）。`screenci init` 除非传递 `--github-workflow` 否则不会写入工作流。
- **了解产品**：`screenci context` 打印项目已知信息（网站URL、是否需要登录、团队笔记）。在你自行启动应用前 `preview` 设置 `SCREENCI_APP_LAUNCHED_BY=agent`。
- **在编写选择器前探索应用**：使用 `playwright-cli` 技能，绝不使用自己的Playwright脚本。手写脚本从未登录状态启动，使用与录制器不同的浏览器，并让你追逐录制器永远不会看到的选择器。当应用需要时先加载保存的会话：`playwright-cli state-load screenci/.screenci/auth/default.json`。
- **录制时遇到机器人检查**（“请稍候…”、“执行安全验证”、挑战页面）而正常浏览器可以正常加载网站：录制器运行Chromium的无头shell，其用户代理被某些机器人保护拒绝。在 `screenci.config.ts` 的 `use` 中设置正常桌面用户代理并重新运行：

  ```ts
  use: {
    userAgent:
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
  }
  ```

  一次性在配置中设置，而不是在一次性脚本中探测启动选项。这是录制环境问题，不是选择器问题，因此无论多少次重写视频代码都无法解决。
