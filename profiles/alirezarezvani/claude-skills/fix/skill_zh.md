# 修复失败或不可靠的测试

使用系统化的分类法诊断和修复 Playwright 测试中出现的失败或间歇性通过的情况。

## 输入

`$ARGUMENTS` 包含：
- 测试文件路径：`e2e/login.spec.ts`
- 测试名称：`"登录后重定向"`
- 描述：`"CI中结账测试失败，但本地通过"`

## 步骤

### 1. 复现失败

运行测试以捕获错误：

```bash
npx playwright test <file> --reporter=list
```

如果测试通过，则可能是不可靠的。运行 burn-in：

```bash
npx playwright test <file> --repeat-each=10 --reporter=list
```

如果仍然通过，尝试使用并行工作进程：

```bash
npx playwright test --fully-parallel --workers=4 --repeat-each=5
```

### 2. 捕获跟踪信息

使用完整跟踪运行：

```bash
npx playwright test <file> --trace=on --retries=0
```

阅读跟踪输出。如果可用，使用 `/debug` 分析跟踪文件。

### 3. 对失败进行分类

从本技能目录加载 `flaky-taxonomy.md`。

每个失败的测试都属于以下四个类别之一：

| 类别 | 症状 | 诊断 |
|---|---|---|
| **时间/异步** | 每处都间歇性失败 | `--repeat-each=20` 本地可复现 |
| **测试隔离** | 测试套件中失败，单独通过 | `--workers=1 --grep "test name"` 通过 |
| **环境** | CI中失败，本地通过 | 对比CI与本地的截图/跟踪信息 |
| **基础设施** | 随机，无规律 | 错误引用浏览器内部实现 |

### 4. 应用针对性修复

**时间/异步：**
- 将 `waitForTimeout()` 替换为 web-first 断言
- 为缺失的 Playwright 调用添加 `await`
- 在断言前等待特定的网络响应
- 在与元素交互前使用 `toBeVisible()`

**测试隔离：**
- 移除测试间共享的可变状态
- 通过API或 fixtures 为每个测试创建测试数据
- 为测试数据使用唯一标识符（时间戳、随机字符串）
- 检查数据库状态泄漏

**环境：**
- 在本地和CI中匹配视口大小
- 考虑截图中的字体渲染差异
- 本地使用 `docker` 以匹配CI环境
- 检查时区相关的断言

**基础设施：**
- 为慢速CI运行器增加超时
- 在CI配置中添加重试（`retries: 2`）
- 检查浏览器 OOM（减少并行工作进程）
- 确保安装了浏览器依赖项

### 5. 验证修复

运行测试10次以确认稳定性：

```bash
npx playwright test <file> --repeat-each=10 --reporter=list
```

必须全部通过10次。如果有任何失败，返回步骤3。

### 6. 防止再次发生

建议：
- 如果尚未添加，使用 `retries: 2` 添加到CI
- 在配置中启用 `trace: 'on-first-retry'`
- 将修复模式添加到项目的测试规范文档

## 输出

- 根本原因类别和具体问题
- 应用的修复（附带diff）
- 验证结果（10/10通过）
- 预防建议
