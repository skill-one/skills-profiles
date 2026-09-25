使用 Plugin Framework 框架搭建新的 Terraform 提供者：

1. 如果我已经处于一个 Terraform 提供者工作区中，请确认我想要创建一个新的工作区。如果我不想创建新的工作区，则跳过所有剩余步骤。
1. 创建一个新的工作区根目录。根目录名称应以 "terraform-provider-" 开头。在此新的工作区中执行所有后续步骤。
1. 初始化一个新的 Go 模块。
1. 运行 `go get -u github.com/hashicorp/terraform-plugin-framework@latest`。
1. 编写一个遵循 [示例](assets/main.go) 的 main.go 文件。
1. 编写一个遵循 [示例](assets/provider.go) 的 `internal/provider/provider.go` 文件。将 `demo` 提供者、`DEMO_*` 环境变量和认证属性重命名为与目标 API 匹配。
1. 从 `main.go` 和 `provider.go` 中删除 TODO 注释。
1. 运行 `go mod tidy`。
1. 运行 `go build -o /dev/null`。
1. 运行 `go test ./...`。

该脚手架将凭证解析为显式配置，并使用环境变量作为后备。要将其扩展为完整的凭证提供者链（共享凭证文件、配置文件、平台身份、配置时验证），请使用 `provider-configuration` 技能（如果可用）。要添加第一个资源或数据源，请使用 `provider-resources` 技能（如果可用）。
