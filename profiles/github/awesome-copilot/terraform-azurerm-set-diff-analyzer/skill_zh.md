# Terraform AzureRM Set 差异分析器

一个技能，用于识别由 AzureRM 提供者的 Set 类型属性引起的 Terraform 计划中的“误报差异”，并将它们与实际变更区分开来。

## 使用场景

- `terraform plan` 显示许多变更，但你只添加/删除了一个元素
- 应用网关、负载均衡器、网络安全组等显示“所有元素已变更”
- 你希望在 CI/CD 中自动过滤误报差异

## 背景

Terraform 的 Set 类型通过位置进行比较，而不是通过键，因此在添加或删除元素时，所有元素都会显示为“已变更”。这是一个通用的 Terraform 问题，但在使用 Set 类型属性较多的 AzureRM 资源（如应用网关、负载均衡器和网络安全组）中尤为明显。

这些“误报差异”实际上不会影响资源，但会使审查 terraform 计划输出变得困难。

## 前置条件

- Python 3.8+

如果 Python 不可用，请通过您的包管理器安装（例如，`apt install python3`，`brew install python3`）或从 [python.org](https://www.python.org/downloads/) 安装。

## 基本用法

```bash
# 1. 生成计划 JSON 输出
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json

# 2. 分析
python scripts/analyze_plan.py plan.json
```

## 故障排除

- **`python: command not found`**：使用 `python3`，或安装 Python
- **`ModuleNotFoundError`**：脚本仅使用标准库；确保 Python 3.8+

## 详细文档

- [scripts/README.md](scripts/README.md) - 所有选项、输出格式、退出代码、CI/CD 示例
- [references/azurerm_set_attributes.md](references/azurerm_set_attributes.md) - 支持的资源和属性
