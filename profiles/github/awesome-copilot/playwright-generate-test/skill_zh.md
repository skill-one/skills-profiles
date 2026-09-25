# 使用 Playwright MCP 生成测试

你的目标是完成所有规定步骤后，根据提供的场景生成一个 Playwright 测试。

## 具体说明

- 你将获得一个场景，需要为其生成 playwright 测试。如果用户没有提供场景，你需要要求他们提供。
- 不要过早地或仅根据场景生成测试代码，而必须完成所有规定步骤。
- 请使用 Playwright MCP 提供的工具逐个执行步骤。
- 只有在所有步骤完成后，才能根据消息历史生成基于 `@playwright/test` 的 Playwright TypeScript 测试。
- 将生成的测试文件保存在 tests 目录下
- 执行测试文件并迭代，直到测试通过
