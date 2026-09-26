为 React 代码库运行测试。

参数：
- $ARGUMENTS: 通道、标志和测试模式

使用示例：
- `/test ReactFiberHooks` - 使用源通道（默认）
- `/test experimental ReactFiberHooks` - 使用实验通道
- `/test www ReactFiberHooks` - 使用 www-modern 通道
- `/test www variant false ReactFiberHooks` - 测试 __VARIANT__=false
- `/test stable ReactFiberHooks` - 使用稳定通道
- `/test classic ReactFiberHooks` - 使用 www-classic 通道
- `/test watch ReactFiberHooks` - 以监视模式运行（TDD）

发布通道：
- `(default)` - 源/金丝雀通道，使用 ReactFeatureFlags.js 默认值
- `experimental` - 源/实验通道，__EXPERIMENTAL__ 标志 = true
- `www` - www-modern 通道，__VARIANT__ 标志 = true
- `www variant false` - www 通道，__VARIANT__ 标志 = false
- `stable` - 发布到 npm 的版本
- `classic` - 遗留的 www-classic（很少需要）

说明：
1. 从参数中解析通道（默认：源）
2. 映射到 yarn 命令：
   - (default) → `yarn test --silent --no-watchman <pattern>`
   - experimental → `yarn test -r=experimental --silent --no-watchman <pattern>`
   - stable → `yarn test-stable --silent --no-watchman <pattern>`
   - classic → `yarn test-classic --silent --no-watchman <pattern>`
   - www → `yarn test-www --silent --no-watchman <pattern>`
   - www variant false → `yarn test-www --variant=false --silent --no-watchman <pattern>`
3. 报告测试结果和任何失败

硬性规则：
1. **使用 --silent 查看失败** - 这将测试输出限制为仅失败。
2. **使用 --no-watchman** - 这是沙盒化中的常见失败。

常见错误：
- **未指定模式运行** - 运行所有测试，非常慢。始终指定模式。
- **忘记 www 变体** - 测试 `www` 和 `www variant false` 以测试 `__VARIANT__` 标志。
- **测试意外跳过** - 检查 `@gate` 指令；参见 `feature-flags` 技能。
