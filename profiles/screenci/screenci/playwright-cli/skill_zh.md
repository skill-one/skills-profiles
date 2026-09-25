<!--  
  根据 Microsoft Playwright CLI 项目中的 "playwright-cli" 技能改编  
  (https://github.com/microsoft/playwright-cli)，版权所有 (c) Microsoft Corporation，  
  根据 Apache License, Version 2.0 授权，由 ScreenCI 修改。完整许可和归属：  
  请参阅 screenci 包中的 THIRD_PARTY_NOTICES.md 和 licenses/microsoft-playwright-cli-APACHE-2.0.txt。  
-->  

# 使用 playwright-cli 进行浏览器自动化  

使用 `playwright-cli` 检查实时页面，发现真实流程、稳定选择器和 cookie/同意步骤，  
在编写 ScreenCI `.screenci.ts` 脚本之前。它从 CLI 驱动真实浏览器：导航、截图、点击、输入。  

**请使用这些命令，而不是自己编写 Playwright 脚本。** 一次性脚本会以未登录状态启动，  
默认启动浏览器，并需要自己的清理操作；这些每一个差异都会导致你追逐录制中永远不会遇到的选择器。  

## 为 ScreenCI 检查页面  

- 如果应用程序需要登录，请加载 ScreenCI 已保存的会话，而不是在此处登录。否则，  
  在录制运行时，你将探索一个未登录的应用程序，而录制将作为已登录运行，  
  你找到的每个选择器都是错误的：  

  ```bash
  playwright-cli open
  playwright-cli state-load screenci/.screenci/auth/default.json
  playwright-cli goto https://app.example.com
  ```

  当该文件不存在时，运行 `npx screenci login`，让用户在打开的浏览器中登录，  
  然后运行 `npx screenci login --done`，再加载它。  
  不要将用户的凭证输入此浏览器，也不要将状态保存回该文件（`state-save` 会覆盖真实会话）。  

- 在第一次导航和截图后，检查是否出现了 cookie 同意或 cookie 政策横幅。  
- 确定视频脚本在其初始 `hide()` 块中应使用的确切接受操作，最好使用稳定定位器，例如  
  `getByRole('button', { name: /accept|accept all|allow all|agree|ok/i })`。  
- 如果存在多个同意操作，请优先选择明确的接受/允许操作，而不是仅关闭或设置操作。  
- 将 cookie 同意点击报告为隐藏的初始设置的一部分，而不是可见的演示步骤。  

## 快速入门  

```bash
# 打开新浏览器  
playwright-cli open  
# 导航到页面  
playwright-cli goto https://playwright.dev  
# 使用快照中的引用与页面交互  
playwright-cli click e15  
playwright-cli type "page.click"  
playwright-cli press Enter  
# 关闭浏览器  
playwright-cli close  
```

## 核心命令  

```bash
playwright-cli open  
# 立即打开并导航  
playwright-cli open https://example.com/  
playwright-cli goto https://playwright.dev  
playwright-cli type "search query"  
playwright-cli click e3  
playwright-cli dblclick e7  
# --submit 在填写元素后按 Enter  
playwright-cli fill e5 "user@example.com" --submit  
playwright-cli hover e4  
playwright-cli select e9 "option-value"  
playwright-cli check e12  
playwright-cli uncheck e12  
playwright-cli snapshot  
playwright-cli eval "document.title"  
playwright-cli eval "el => el.textContent" e5  
# 获取快照中不可见的属性  
playwright-cli eval "el => el.getAttribute('data-testid')" e5  
playwright-cli close  
```

### 导航  

```bash
playwright-cli go-back  
playwright-cli go-forward  
playwright-cli reload  
playwright-cli press Enter  
playwright-cli press ArrowDown  
```

## 快照  

每次命令后，playwright-cli 都会提供当前浏览器状态的快照。  

```bash
> playwright-cli goto https://example.com  
### 页面  
- 页面 URL: https://example.com/  
- 页面标题: Example Domain  
### 快照  
[快照](.playwright-cli/page-2026-02-14T19-22-42-679Z.yml)  
```

你也可以按需拍摄快照。选项可以组合使用。  

```bash
# 默认 - 保存为基于时间戳命名的文件  
playwright-cli snapshot  

# 快照元素而不是整个页面  
playwright-cli snapshot "#main"  

# 限制快照深度以提高效率  
playwright-cli snapshot --depth=4  
playwright-cli snapshot e34  
```

全局 `--raw` 选项会移除页面状态和生成代码，仅返回结果值。用于将输出管道到其他工具。  

```bash
playwright-cli --raw snapshot > before.yml  
playwright-cli click e5  
playwright-cli --raw snapshot > after.yml  
diff before.yml after.yml  
```

## 定位元素  

默认情况下，使用快照中的引用与页面元素交互。  

```bash
# 获取带引用的快照  
playwright-cli snapshot  

# 使用引用交互  
playwright-cli click e15  
```

你也可以使用 CSS 选择器或 Playwright 定位器。  

```bash
# CSS 选择器  
playwright-cli click "#main > button.submit"  

# role 定位器  
playwright-cli click "getByRole('button', { name: 'Submit' })"  

# 测试 ID  
playwright-cli click "getByTestId('submit-button')"  
```

## 浏览器会话  

```bash
# 创建命名浏览器会话  
playwright-cli -s=mysession open example.com  
playwright-cli -s=mysession click e6  
playwright-cli -s=mysession close  

playwright-cli list  
# 关闭所有浏览器  
playwright-cli close-all  
```

## 安装  

如果全局 `playwright-cli` 不可用，尝试本地版本：  

```bash
npx --no-install playwright-cli --version  
```

否则，全局安装：  

```bash
npm install -g @playwright/cli@latest  
```

## 示例：表单提交  

```bash
playwright-cli open https://example.com/form  
playwright-cli snapshot  
playwright-cli fill e1 "user@example.com"  
playwright-cli fill e2 "password123"  
playwright-cli click e3  
playwright-cli snapshot  
playwright-cli close  
```
