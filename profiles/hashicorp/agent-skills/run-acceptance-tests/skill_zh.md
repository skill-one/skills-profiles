验收测试是一个以 `TestAcc` 为前缀的 Go 测试函数。

运行前：验收测试会针对提供者的实时 API 创建**真实的基础设施**，这可能会产生费用。在进行之前，请确认配置的凭证指向了一个测试账户。

要运行名为 `TestAccFeatureHappyPath` 的聚焦验收测试：

1. 使用以下环境变量运行 `go test -run=TestAccFeatureHappyPath -timeout 60m`：
   - `TF_ACC=1`

   默认为非详细测试输出。始终传递明确的 `-timeout`：`go test` 默认会在 10 分钟后终止任何测试运行，而验收测试通常超过这个时间。
1. 验收测试可能需要针对特定提供者的额外环境变量。要发现哪些变量：
   - 读取测试的 `PreCheck` / `testAccPreCheck` 函数，并在测试文件中搜索：`grep -rn "os.Getenv" --include="*_test.go"`。
   - 检查仓库的 README、CONTRIBUTING 或 `.env.example` 以获取文档化的测试设置。
   - 提供者的 `Configure` 方法显示了凭证如何解析；使用 `provider-configuration` 技能（如果可用）来理解凭证提供者链。

   为单个测试调用设置变量（`EXAMPLE_API_KEY=... TF_ACC=1 go test ...`），而不是将它们导出到 shell 配置文件中，并且永远不要将秘密值写入仓库中的文件。

要诊断失败的验收测试，请按顺序使用这些选项。这些选项是累积的：每个选项都包含它上面的所有选项。

1. 重新运行测试。使用 `-count=1` 选项确保 `go test` 不会使用缓存的结果。
1. 提供 `go test` 的详细输出。使用 `-v` 选项。
1. 提供调试级别的日志记录。使用环境变量 `TF_LOG=debug` 启用调试级别日志记录。
1. 提供持久化验收测试的 Terraform 工作区。使用环境变量 `TF_ACC_WORKING_DIR_PERSIST=1` 启用持久化。

一个通过的验收测试可能是假阴性。要“翻转”一个名为 `TestAccFeatureHappyPath` 的通过验收测试：

1. 编辑其中一个测试用例中测试步骤中的一个 TestCheckFunc 的值。
1. 运行验收测试。预期测试会失败。
1. 如果测试失败，则撤销编辑并报告成功的翻转。否则，保留编辑并报告不成功的翻转。

如果测试运行被中断，可能会留下真实资源；如果提供者注册了清理程序（参考 `provider-test-patterns` 技能的清理程序参考，如果可用），请运行提供者的清理程序。对于编写或重构测试，请使用 `provider-test-patterns` 技能。
