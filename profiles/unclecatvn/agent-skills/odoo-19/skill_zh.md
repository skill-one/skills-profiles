# Odoo 19 技能 - 主索引

所有 Odoo 19 开发指南的主索引。根据您的任务，从 `references/` 中阅读相应的指南。

## 快速参考

| 主题          | 文件                                      | 使用场景                                             |
| -------------- | ----------------------------------------- | ------------------------------------------------------- |
| 操作          | `references/odoo-19-actions-guide.md`     | 创建操作、菜单、计划任务、服务器操作                 |
| API 装饰器    | `references/odoo-19-decorator-guide.md`   | 使用 @api 装饰器、计算字段、验证                   |
| 控制器        | `references/odoo-19-controller-guide.md`  | 编写 HTTP 端点、路由、Web 控制器                   |
| 数据文件      | `references/odoo-19-data-guide.md`        | XML/CSV 数据文件、记录、快捷方式                  |
| 开发          | `references/odoo-19-development-guide.md` | 创建模块、清单、报告、安全、向导                  |
| 字段类型      | `references/odoo-19-field-guide.md`       | 定义模型字段、选择字段类型                         |
| 清单          | `references/odoo-19-manifest-guide.md`    | **manifest**.py 配置、依赖项、钩子              |
| 迁移          | `references/odoo-19-migration-guide.md`   | 升级模块、数据迁移、版本变更                      |
| 混合器        | `references/odoo-19-mixins-guide.md`      | mail.thread、活动、邮件别名、跟踪                  |
| 模型方法      | `references/odoo-19-model-guide.md`       | 编写 ORM 查询、CRUD 操作、域过滤器                |
| OWL 组件      | `references/odoo-19-owl-guide.md`         | 构建 OWL UI 组件、钩子、服务                      |
| 性能          | `references/odoo-19-performance-guide.md` | 优化查询、修复慢代码、防止 N+1                    |
| 报告          | `references/odoo-19-reports-guide.md`     | QWeb 报告、PDF/HTML、模板、纸张格式                |
| 安全          | `references/odoo-19-security-guide.md`    | 访问权限、记录规则、字段权限                      |
| 测试          | `references/odoo-19-testing-guide.md`     | 编写测试、模拟、断言、浏览器测试                  |
| 事务          | `references/odoo-19-transaction-guide.md` | 处理数据库错误、保存点、UniqueViolation            |
| 翻译          | `references/odoo-19-translation-guide.md` | 添加翻译、本地化、i18n                            |
| 视图 & XML    | `references/odoo-19-view-guide.md`        | 编写 XML 视图、操作、菜单、QWeb 模板              |

## 编码规范

在编写代码之前，如果已安装 `odoo-workflow` 技能（跟踪真实源代码、`file:line` 的上下文简报、完成定义），请运行它；与这个包一起安装它。

应用您打开的指南中的规范部分。Odoo 19 运行时行为，然后现有的稳定插件风格，优先级更高；保持差异集中。

- 模块命名、资源、JavaScript、CSS 和 SCSS：开发指南。
- XML 格式化和 ID：数据、操作、报告、安全、视图指南。
- Python、记录集、事务和翻译：模型、字段、装饰器、性能、事务和翻译指南。

## 文件结构

```
skills/odoo-19.0/
├── SKILL.md                          # 此文件 - 主索引
└── references/                       # 开发指南
    ├── odoo-19-actions-guide.md
    ├── odoo-19-controller-guide.md
    ├── odoo-19-data-guide.md
    ├── odoo-19-decorator-guide.md
    ├── odoo-19-development-guide.md
    ├── odoo-19-field-guide.md
    ├── odoo-19-manifest-guide.md
    ├── odoo-19-migration-guide.md
    ├── odoo-19-mixins-guide.md
    ├── odoo-19-model-guide.md
    ├── odoo-19-owl-guide.md
    ├── odoo-19-performance-guide.md
    ├── odoo-19-reports-guide.md
    ├── odoo-19-security-guide.md
    ├── odoo-19-testing-guide.md
    ├── odoo-19-transaction-guide.md
    ├── odoo-19-translation-guide.md
    └── odoo-19-view-guide.md
```

## 基础代码参考 (Odoo 19)

所有指南都基于对 Odoo 19 源代码的分析：

- `odoo/orm/models.py` - ORM 实现
- `odoo/orm/fields.py` - 字段类型
- `odoo/orm/decorators.py` - 装饰器
- `odoo/http.py` - HTTP 层
- `odoo/exceptions.py` - 异常类型
- `odoo/tools/translate.py` - 翻译系统
- `odoo/addons/base/models/res_lang.py` - 语言模型
- `addons/web/static/src/core/l10n/translation.js` - JS 翻译

## 外部文档

- [Odoo 19 官方文档](https://github.com/odoo/documentation/tree/19.0)
- [Odoo 19 开发者参考](https://github.com/odoo/documentation/blob/19.0/developer/reference/orm.rst)
- [Odoo 编码指南](https://raw.githubusercontent.com/odoo/documentation/17.0/content/contributing/development/coding_guidelines.rst)
