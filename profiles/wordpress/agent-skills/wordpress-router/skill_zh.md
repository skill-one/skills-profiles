# WordPress 路由器

## 使用场景

在大多数 WordPress 任务开始时使用此技能，以：

- 识别这是什么类型的 WordPress 代码库（插件 vs 主题 vs 块主题 vs WP 核心代码库 vs 完整网站），
- 选择正确的流程和约束条件，
- 分配到最相关的领域技能。

## 所需输入

- 仓库根目录（当前工作目录）。
- 用户的意图（他们想要更改的内容）以及任何约束条件（WP 版本目标、WP.com 特定要求、发布要求）。

## 流程

1. 运行项目筛选脚本：
   - `node skills/wp-project-triage/scripts/detect_wp_project.mjs`
2. 读取筛选输出并分类：
   - 主要项目类型，
   - 可用的工具（PHP/Composer、Node、@wordpress/scripts），
   - 存在的测试（PHPUnit、Playwright、wp-env），
   - 任何版本提示。
3. 根据用户意图 + 仓库类型路由到领域工作流：
   - 对于决策树，请阅读：`skills/wordpress-router/references/decision-tree.md`。
4. 在进行更改前应用约束条件：
   - 如果不明确，请确认任何版本约束条件。
   - 优先使用仓库现有的构建/测试工具和约定。

## 验证

- 如果创建或重构了重要文件，请重新运行筛选脚本。
- 运行筛选输出推荐的仓库的 lint/测试/构建命令（如果可用）。

## 失败模式 / 调试

- 如果筛选报告 `kind: unknown`，请检查：
  - 根目录的 `composer.json`、`package.json`、`style.css`、`block.json`、`theme.json`、`wp-content/`。
- 如果仓库非常大，请考虑缩小扫描范围或向筛选脚本添加忽略规则。

## 升级处理

- 如果路由不明确，请提出一个问题：
  - “这是打算作为 WordPress 插件、主题（经典/块）还是完整网站仓库吗？”
