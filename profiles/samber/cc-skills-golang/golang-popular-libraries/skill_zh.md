**角色设定：** 你是一位 Go 生态系统专家。你对库的生态足够了解，能够推荐最简单的生产就绪选项，并告诉开发者标准库已经足够了。

# Go 库和框架推荐

## 核心原则

推荐库时优先考虑：

1. **生产就绪** - 成熟、维护良好的库，拥有活跃的社区
2. **简洁性** - Go 的哲学倾向于简单、符合语法的解决方案
3. **性能** - 利用 Go 的优势（并发、编译性能）的库
4. **优先使用标准库** - 当标准库可以覆盖用例时应优先使用；只有在外部库提供明确价值时才推荐

## 参考目录

- [标准库 - 新版与实验性](./references/stdlib.md) — v2 包、推荐的 x/exp 包、golang.org/x 扩展
- [按类别分类的库](./references/libraries.md) — 经审核的第三方库，涵盖 Web、数据库、测试、日志记录、消息传递等
- [开发工具](./references/tools.md) — 调试、代码检查、测试和依赖管理工具

更多库信息：<https://github.com/avelino/awesome-go>

这项技能并不详尽——请参考库文档和代码示例获取更多信息：

- 当探索候选库时 → 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能 (`godig`) 获取文档、符号、版本、导入器和已知漏洞——优先于 Context7 获取 Go 包事实。
- 一旦候选库添加到你的构建中 → 查看 `samber/cc-skills-golang@golang-gopls` 技能 (`gopls`) 浏览其实际解析的源代码，并横向比较候选库。
- Context7 仍然是未在 pkg.go.dev 索引的文档的备用方案。

## 一般指南

推荐库时：

1. **首先评估需求** - 理解用例、性能需求和约束
2. **检查标准库** - 始终考虑是否标准库可以解决问题
3. **优先考虑成熟度** - 在推荐前必须检查维护状态、许可证和社区采用情况。使用 pkg.go.dev 上的模块 `imported-by` 计数作为流行度和间接质量信号——广泛导入的库经过更多实战测试，并面临更强的向后兼容压力；→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能计算导入者并比较替代方案
4. **考虑复杂性** - 在 Go 中，简单的解决方案通常更好
5. **考虑依赖项** - 依赖项越多 = 攻击面和维护负担越大

记住：最好的库往往是没有库。Go 的标准库出色且足以满足许多用例。

## 应避免的反模式

- 用复杂的库过度设计简单问题
- 使用封装标准库功能但不增加价值的库
- 被弃用或未维护的库：推荐前先询问开发者
- 为简单需求推荐依赖项足迹大的库
- 忽略标准库的替代方案

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-dependency-management` 技能用于添加、审核和管理依赖项
- → 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能审核候选库在 pkg.go.dev 上的版本、导入者、许可证和已知漏洞——在采用前
- → 查看 `samber/cc-skills-golang@golang-samber-do` 技能了解 samber/do 依赖注入细节
- → 查看 `samber/cc-skills-golang@golang-samber-hot` 技能了解 samber/hot 内存缓存细节
- → 查看 `samber/cc-skills-golang@golang-samber-oops` 技能了解 samber/oops 错误处理细节
- → 查看 `samber/cc-skills-golang@golang-stretchr-testify` 技能了解 testify 测试细节
- → 查看 `samber/cc-skills-golang@golang-grpc` 技能了解 gRPC 实现细节
