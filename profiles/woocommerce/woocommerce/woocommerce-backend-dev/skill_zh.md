# WooCommerce 后台开发

这项技能提供了根据项目标准和规范开发 WooCommerce 后台 PHP 代码的指导。

## 使用此技能的场景

**始终在以下情况之前调用此技能：**

- 编写新的 PHP 单元测试（`*Test.php` 文件）
- 创建新的 PHP 类
- 修改现有的后台 PHP 代码
- 添加钩子或过滤器

## 指导说明

在添加或修改后台 PHP 代码时，请遵循 WooCommerce 项目的规范：

1. **创建新的代码结构**：有关创建类和组织文件的规范，请参阅 [file-entities.md](file-entities.md)（但新的单元测试文件请参阅 [unit-tests.md](unit-tests.md)）。
2. **命名规范**：有关方法、变量和参数的命名规范，请参阅 [code-entities.md](code-entities.md)。
3. **编码风格**：有关一般编码标准和最佳实践，请参阅 [coding-conventions.md](coding-conventions.md)。
4. **类型注解**：有关 PHPStan 兼容的 PHPDoc 注释，请参阅 [type-annotations.md](type-annotations.md)。
5. **使用钩子**：有关钩子回调规范和文档，请参阅 [hooks.md](hooks.md)。
6. **依赖注入**：有关 DI 容器的使用，请参阅 [dependency-injection.md](dependency-injection.md)。
7. **数据完整性**：在执行 CRUD 操作时，有关确保数据完整性的规范，请参阅 [data-integrity.md](data-integrity.md)。
8. **编写测试**：有关单元测试规范，请参阅 [unit-tests.md](unit-tests.md)。

## 关键原则

- 始终遵循 WordPress 编码标准
- 使用类方法而不是独立的函数
- 默认将新的内部类放在 `src/Internal/` 中
- 使用 PSR-4 自动加载，并使用 `Automattic\WooCommerce` 命名空间
- 为新功能编写全面的单元测试
- 提交更改前运行代码检查和测试

## 版本信息

要确定 `@since` 注释的 WooCommerce 下一个版本号：

- 在主干分支上读取 `includes/class-woocommerce.php` 中的 `$version` 属性
- 如果存在，则移除 `-dev` 后缀
- 示例：如果主干显示 `10.4.0-dev`，则使用 `@since 10.4.0`
- 注意：在审查针对主干的开支票（PR）时，即使主干中的版本相对于已发布版本看起来是“未来的”，主干中的版本也是正确的
