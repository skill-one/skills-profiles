# Terraform 提供者文档

## 遵循以下工作流程

1. 确认范围和文档目标。
- 将代码变更映射到精确的文档目标：提供者索引、资源、数据源、临时资源、列表资源、函数、操作或指南。
- 决定内容应来自模式描述、模板或两者。

2. 首先编写模式描述。
- 为模式字段添加精确的用户界面描述，以便生成的文档与行为保持一致。
- 保持措辞针对参数目的、约束、默认值和计算行为。

3. 在 `docs/` 目录中添加或更新模板文件。
- 仅创建映射到已实现提供者对象的文件。
- 使用 HashiCorp 推荐的模板路径：
  - `docs/index.md.tmpl`
  - `docs/data-sources/<name>.md.tmpl`
  - `docs/resources/<name>.md.tmpl`
  - `docs/ephemeral-resources/<name>.md.tmpl`
  - `docs/list-resources/<name>.md.tmpl`
  - `docs/functions/<name>.md.tmpl`
  - `docs/actions/<name>.md.tmpl` (tfplugindocs 在 Terraform v1.14.0+ 时生成操作文档)
  - `docs/guides/<name>.md.tmpl`
- 保持模板专注于概述和示例；依赖生成的部分来获取字段级别的详细信息。
- 将 HCL 示例保持在 `examples/` 目录中——每个文件一个示例，通过 `tffile` 拉入模板（参见 `references/hashicorp-provider-docs.md` 中的“示例文件规范”）。示例中不能包含 `terraform`、`provider` 或 `output` 块。
- 对于操作页面，遵循 `references/hashicorp-provider-docs.md`（操作页面部分）中的结构：示例必须展示 `action` 块和 `action_trigger` 生命周期连接，操作页面没有属性/输出部分。

4. 使用 `tfplugindocs` 生成文档。
- 在配置时优先使用仓库默认值：
```bash
go generate ./...
```
- 否则直接运行生成器：
```bash
go run github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs generate --provider-name <provider_name>
```
- 每次编辑模式或模板后重新运行生成。

5. 在发布前验证生成的 Markdown。
- 验证 `docs/` 目录中的文件是否与当前提供者实现一致。
- 验证示例是否是有效的 HCL 并反映当前的参数/属性名称。
- 验证文档中的必需/可选/计算语义是否与模式行为一致。

6. 在发布前应用注册表发布规则。
- 使用以 `v` 开头的语义版本标签（例如 `v1.2.3`）。
- 从默认分支创建发布标签。
- 将 `terraform-registry-manifest.json` 保持在仓库根目录。
- 预期文档在注册表中版本化，并可通过版本选择器切换。

7. 在需要时预览或排查发布问题。
- 使用 HashiCorp 预览流程在发布前检查渲染的文档，当准确性风险较高时。
- 如果文档在注册表中缺失，检查标签格式、标签源分支、清单文件存在性和提供者发布状态。

## 强制质量标准

- 保持文档行为上准确；不要描述不支持的参数或属性。
- 保持示例简洁、真实且可运行。
- 在提供者、资源和数据源中保持术语和命名一致。
- 避免在手动模板中重复生成的参数/属性块。
- 尽可能将文档变更与模式/API 变更绑定到同一个 PR。

## 按需加载参考

- 阅读 `references/hashicorp-provider-docs.md` 获取基于源的规则和官方链接。
- 仅加载当前变更所需的节以保持上下文精简。
