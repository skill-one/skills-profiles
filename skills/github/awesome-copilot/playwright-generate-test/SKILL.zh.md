---
name: playwright-generate-test
description: 基于Playwright MCP生成一个场景的Playwright测试
---

# 使用 Playwright MCP 生成测试用例

你的目标是完成所有规定步骤后，根据提供的场景生成一个 Playwright 测试用例。

## 具体说明

- 你将获得一个场景，需要为其生成 Playwright 测试用例。如果用户没有提供场景，你需要要求他们提供。
- 切勿过早生成测试代码，或仅基于场景而未完成所有规定步骤就生成。
- 必须使用 Playwright MCP 提供的工具逐个执行步骤。
- 只有在所有步骤完成后，才能根据消息历史生成基于 `@playwright/test` 的 Playwright TypeScript 测试用例。
- 将生成的测试文件保存在测试目录中
- 执行测试文件，并迭代直至测试通过
