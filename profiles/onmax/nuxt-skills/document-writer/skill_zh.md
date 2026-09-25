# Nuxt 生态系统文档编写者

遵循官方 Nuxt 网站模式的博客文章和文档编写指南。

## 使用场景

- 为 Nuxt 生态系统项目撰写博客文章
- 创建或编辑文档页面
- 确保内容风格一致

## 写作标准

**覆盖**: 在编写文档时，请保持正确的语法和完整的句子。 "为简洁而牺牲语法" 的规则在此处**不适用**。

文档必须：

- 语法正确
- 清晰且无歧义
- 标点符号使用正确
- 使用完整句子（非片段）

简洁性仍然受到重视，但绝不能以牺牲清晰度或正确性为代价。

## 相关技能

对于组件和语法细节，使用以下技能：

| 技能            | 用于                                         |
| ---------------- | ----------------------------------------------- |
| **nuxt-content** | MDC 语法、散文组件、代码高亮                 |
| **nuxt-ui**      | 组件属性、主题、UI 模式                     |

## 可用参考

| 参考                                                            | 目的                                         |
| -------------------------------------------------------------------- | ----------------------------------------------- |
| **[references/writing-style.md](references/writing-style.md)**       | 语气、语调、句子结构                         |
| **[references/content-patterns.md](references/content-patterns.md)** | 博客 frontmatter、结构、组件模式             |

## 文件加载

**根据您的任务考虑加载以下参考文件**：

- [ ] [references/writing-style.md](references/writing-style.md) - 如果正在撰写散文、改进语气/语调或构建句子结构
- [ ] [references/content-patterns.md](references/content-patterns.md) - 如果正在创建博客文章、设置 frontmatter 或使用 MDC 组件

**不要一次性加载所有文件**。 仅加载与当前任务相关的文件。

## 快速参考

### 写作模式

| 模式       | 示例                                            |
| ------------- | -------------------------------------------------- |
| 主语优先     | "The `useFetch` composable handles data fetching." |
| 命令式      | "Add the following to `nuxt.config.ts`."           |
| 上下文式    | "When using authentication, configure..."          |

### 情态动词

| 动词     | 含义     |
| -------- | ----------- |
| `can`    | 可选    |
| `should` | 推荐    |
| `must`   | 必须要    |

### 组件模式（何时使用）

| 需求              | 组件                         |
| ----------------- | --------------------------------- |
| 信息侧边栏        | `::note`                          |
| 建议        | `::tip`                           |
| 警告           | `::warning`                       |
| 必要          | `::important`                     |
| CTA               | `:u-button{to="..." label="..."}` |
| 多源代码        | `::code-group`                    |

> 对于组件属性：参见 **nuxt-ui** 技能

## 标题

- **H1 (`#`)**: 不要使用反引号——它们无法正确渲染
- **H2-H4**: 反引号完全可以正常使用

## 工作流程

1. 加载相关的参考文件（[writing-style.md](references/writing-style.md) 用于散文，[content-patterns.md](references/content-patterns.md) 用于结构）
2. 使用主动语态和现在时态起草内容
3. 应用以下清单来验证质量——如果任何项目未通过，请修改并重新检查
4. 验证标注类型是否与意图一致（注意/提示/警告/重要）

## 示例

```md
# 认证入门

Nuxt Better Auth 提供了一种简单的方法来为您的应用程序添加认证。
在您的 `nuxt.config.ts` 中配置该模块即可开始使用。

::note
认证需要数据库连接。有关详细信息，请参阅 [数据库设置](/docs/database) 指南。
::

## 安装

将模块添加到您的项目中：

~~~bash [终端]
pnpm add @nuxtjs/better-auth
~~~

该模块自动导入 `useUserSession` composable。从任何组件中访问当前用户会话。
```

## 清单

- [ ] 主动语态（85%+）
- [ ] 现在时态
- [ ] 每段 2-4 个句子
- [ ] 代码之前有解释
- [ ] 代码块上的文件路径标签
- [ ] 适当的标注类型
- [ ] H1 标题中不要使用反引号
