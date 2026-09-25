# TestRail 集成

Playwright 测试与 TestRail 测试管理之间的双向同步。

## 前置条件

必须设置环境变量：
- `TESTRAIL_URL` — 例如，`https://your-instance.testrail.io`
- `TESTRAIL_USER` — 您的邮箱
- `TESTRAIL_API_KEY` — 来自 TestRail 的 API 密钥

如果未设置，请告知用户如何配置并停止。

> **TestRail MCP 服务器不会自动注册（问题 #978）。** `pw-testrail`
> 已从插件的 `.mcp.json` 中移除，因为它无法为每个用户连接（插件不包含 `node_modules`）。
> 以下使用的 `testrail_*` MCP 工具以及 `/pw:testrail` 命令，在手动启用之前会报“工具未找到”错误 — 请参考插件的 `CLAUDE.md` 文件的 **集成** 部分（`cd integrations/testrail-mcp && npm install`，然后在您自己的用户/项目 MCP 配置中注册服务器）。仅设置环境变量是不够的。

## 功能

### 1. 导入测试用例 → 生成 Playwright 测试

```
/pw:testrail import --project <id> --suite <id>
```

步骤：
1. 调用 `testrail_get_cases` MCP 工具获取测试用例
2. 对于每个测试用例：
   - 读取标题、前置条件、步骤、预期结果
   - 使用适当的模板映射到 Playwright 测试
   - 将 TestRail 用例 ID 作为测试注解：`test.info().annotations.push({ type: 'testrail', description: 'C12345' })`
3. 按章节分组生成测试文件
4. 报告：导入 X 个用例，生成 Y 个测试

### 2. 推送测试结果 → TestRail

```
/pw:testrail push --run <id>
```

步骤：
1. 使用 JSON 报告器运行 Playwright 测试：
   ```bash
   npx playwright test --reporter=json > test-results.json
   ```
2. 解析结果：将每个测试映射到其 TestRail 用例 ID（来自注解）
3. 调用 `testrail_add_result` MCP 工具为每个测试：
   - 通过 → 状态 ID：1
   - 失败 → 状态 ID：5，包含错误信息
   - 跳过 → 状态 ID：2
4. 报告：推送 X 个结果，通过 Y 个，失败 Z 个

### 3. 创建测试运行

```
/pw:testrail run --project <id> --name "Sprint 42 Regression"
```

步骤：
1. 调用 `testrail_add_run` MCP 工具
2. 包含 Playwright 测试注解中找到的所有测试用例 ID
3. 返回用于结果推送的运行 ID

### 4. 同步状态

```
/pw:testrail status --project <id>
```

步骤：
1. 从 TestRail 获取测试用例
2. 扫描本地 Playwright 测试以查找 TestRail 注解
3. 报告覆盖率：
   ```
   TestRail 用例：150
   带有 TestRail ID 的 Playwright 测试：120
   未关联的 TestRail 用例：30
   没有 TestRail ID 的 Playwright 测试：15
   ```

### 5. 更新 TestRail 中的测试用例

```
/pw:testrail update --case <id>
```

步骤：
1. 读取此用例 ID 的 Playwright 测试
2. 从测试代码中提取步骤和预期结果
3. 调用 `testrail_update_case` MCP 工具更新步骤

## 使用的 MCP 工具

| 工具 | 使用时机 |
|---|---|
| `testrail_get_projects` | 列出可用项目 |
| `testrail_get_suites` | 列出项目中的套件 |
| `testrail_get_cases` | 读取测试用例 |
| `testrail_add_case` | 创建新的测试用例 |
| `testrail_update_case` | 更新现有用例 |
| `testrail_add_run` | 创建测试运行 |
| `testrail_add_result` | 推送单个结果 |
| `testrail_get_results` | 读取历史结果 |

## 测试注解格式

所有与 TestRail 关联的 Playwright 测试都包含：

```typescript
test('should login successfully', async ({ page }) => {
  test.info().annotations.push({
    type: 'testrail',
    description: 'C12345',
  });
  // ... 测试代码
});
```

此注解是 Playwright 和 TestRail 之间的桥梁。

## 输出

- 带计数的操作摘要
- 任何错误或未匹配的用例
- 链接到 TestRail 运行/结果
