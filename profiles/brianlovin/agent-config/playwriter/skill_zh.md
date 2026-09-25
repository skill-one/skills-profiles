# Playwriter

使用此技能通过 Playwriter 驱动用户的 Chrome 活动标签页。

完整文档请参阅：https://playwriter.dev/

## 快速入门

1. 确保目标标签页上的 Playwriter 扩展已启用（绿色）。
2. 确保 CLI 可用：

```bash
playwriter --version || npx -y playwriter --version
```

3. 创建/附加会话：

```bash
playwriter session new
```

4. 针对该会话运行命令：

```bash
playwriter -s 1 -e "console.log(await page.url())"
```

## 核心工作流

1. 确认连接并选择正确的标签页：

```bash
playwriter -s <会话> -e "console.log(await page.url()); console.log(await page.title());"
```

2. 在需要时收集页面结构：

```bash
playwriter -s <会话> -e "console.log(await accessibilitySnapshot({ page }))"
```

3. 执行目标操作（点击/输入/悬停/获取/评估）。
4. 通过 `page.evaluate` 拉取日志和结构化状态。
5. 使用精确的 ID、时间戳和观察到的状态转换来总结发现。

## 有用命令

从当前应用 UI 获取列表行/选项：

```bash
playwriter -s <会话> -e "const rows = await page.getByRole('option').all(); console.log(rows.length);"
```

读取弹窗/悬停内容：

```bash
playwriter -s <会话> -e "const row = page.getByRole('option').nth(0); await row.hover(); await page.waitForTimeout(700); console.log(await page.locator('[data-side]').first().innerText());"
```

运行页面内任意调试代码：

```bash
playwriter -s <会话> -e "const out = await page.evaluate(() => ({ href: location.href })); console.log(out);"
```

## 故障排除

- 如果会话附加到了错误的标签页，请在目标标签页点击扩展图标并重新运行 `playwriter session new`。
- 如果 `playwriter` 命令缺失，请使用 `npx -y playwriter ...` 或全局安装。
- 如果执行错误提示连接已过期，请创建一个新的会话。

## 安全规范

- 除非任务需要修改，否则优先进行只读检查。
- 在执行破坏性 UI 操作前进行公告。
- 在捕获日志时，在总结中遮蔽敏感令牌/用户数据。
