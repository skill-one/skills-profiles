# 安装或更新 anti-slop

Anti-slop 是一个第三方代码：目标仓库拥有其规则、诊断、测试和配置。在引入上游变更时，请保留这些选择。

## 选择路径

阅读仓库的代理说明并执行 `git status`。确定其包管理器、Oxlint/Vite+ 配置以及任何现有的 anti-slop 入口点，包括由 `jsPlugins` 引用的重命名或重新定位的副本。

- **现有安装 — 更新、升级、迁移或重新配置：** 阅读 [更新一个第三方安装](references/update.md) 并按照该程序，而不是下面的全新安装步骤。
- **无安装 — 全新安装：** 按照下面的步骤进行。如果用户请求更新但找不到安装，请在安装前确认目标。

当操作和目标路径确定，并识别现有工作后，即可完成。

## 全新安装

1. 从此技能中复制捆绑的插件。从目标仓库运行：

   ```bash
   node <skill-directory>/scripts/install.mjs
   ```

   这会创建 `tools/oxlint/anti-slop/`。当仓库有既定的工具布局时，将另一个相对目标作为第一个参数传递。脚本拒绝替换现有目标；通过更新程序而不是 `--force` 路由现有副本。

   保留嵌套的 `vendor/eslint-stylistic/LICENSE` 和 `UPSTREAM.md`；它们随复制的规则一起移动。可读性强制执行是自包含的，并且不需要 Stylistic 插件依赖。

   当文件（包括第三方许可证和来源）在商定的目标位置存在且未替换现有副本时，即可完成。

2. 安装当前兼容的依赖项，而不是信任代理记住的版本：
   - 如果仓库已经依赖于 `oxlint`，从包管理器或锁文件中读取其安装版本，并安装 `@oxlint/plugins` 在完全相同的版本。精确地固定它，而不是通过范围，以便未来的升级将两个包一起移动。
   - 只有当仓库没有 `oxlint` 依赖项时，查询 `npm view oxlint version` 和 `npm view @oxlint/plugins version`，然后安装两个包的相同当前版本。
   - `oxlint` 是一个开发依赖项。复制的源代码导入 `@oxlint/plugins`，因此将其作为本地插件的开发依赖项安装。
   - 不要替换包管理器或重写无关的依赖项范围。

   当匹配的兼容版本安装且无关的依赖项范围被保留时，即可完成。

3. 注册通用插件，配置忽略，并启用所有通用规则。对于 `oxlint.config.ts` 或 `.oxlintrc.json`，将这些字段与现有配置合并：

   ```ts
   ignorePatterns: [
     ".agent/**",
     ".agents/**",
     ".claude/**",
     ".codex/**",
     ".continue/**",
     ".cursor/**",
     ".gemini/**",
     ".opencode/**",
     ".pi/**",
     ".roo/**",
     ".windsurf/**",
     "tools/oxlint/anti-slop/**",
   ],
   jsPlugins: [
     { name: "anti-slop", specifier: "./tools/oxlint/anti-slop/index.ts" },
   ],
   ```

   保留所有现有忽略。当插件被复制到其他地方时，调整最终模式。检查仓库中其他项目本地代理工具目录，并添加它们，而不是将已安装的技能、钩子或生成的代理配置作为应用程序源进行代码检查。不要广泛忽略所有点目录，因为某些仓库将拥有的源或检查保存在其中。

   对于 Vite+，将这些字段添加到 `lint.ignorePatterns` 和 `lint.jsPlugins`。还将相同的模式合并到 `fmt.ignorePatterns`，以便 `vp check` 不会重新格式化已安装的代理资产或第三方插件。合并现有条目而不是替换它们。

   在 `"error"` 级别启用这些规则，包括原生 Oxlint 伴生规则：

   ```json
   {
     "oxc/no-accumulating-spread": "error",
     "anti-slop/no-array-filter-map": "error",
     "anti-slop/no-reduce-accumulator-copy": "error",
     "anti-slop/no-chained-type-assertions": "error",
     "anti-slop/no-conditional-empty-object-spread": "error",
     "anti-slop/no-known-value-widening": "error",
     "anti-slop/no-module-mocking": "error",
     "anti-slop/no-object-parameters": "error",
     "anti-slop/no-reflect-apply": "error",
     "anti-slop/no-reflect-get": "error",
     "anti-slop/no-runtime-typeof": "error",
     "anti-slop/no-shape-in-symbol-names": "error",
     "anti-slop/no-unknown-parameters": "error",
     "anti-slop/no-unknown-returns": "error",
     "anti-slop/no-unknown-type-aliases": "error",
     "anti-slop/no-unsafe-dictionary-type": "error",
     "anti-slop/no-widen-then-assert": "error",
     "anti-slop/require-readable-spacing": "error",
     "anti-slop/require-safety-comment-for-type-assertion": "error"
   }
   ```

   对于 `no-array-filter-map`，只有当目标运行时支持迭代器助手时，才优先使用懒惰的 `.values().filter(...).map(...).toArray()` 管道；否则使用适当的单个 `flatMap` 或本地修改的 reducer。审查回调顺序、索引、稀疏数组、`thisArg` 和过滤语义，而不是机械地重写链。此 AST/作用域规则故意不推断未知接收器类型。

   将 `no-reduce-accumulator-copy` 与原生的 `oxc/no-accumulating-spread` 配对：自定义规则捕获支持的非展开副本，例如 `Object.assign({}, acc, item)`、`Array.from(acc)` 和数组累加器 `concat`/`slice` 调用。允许修改新的本地累加器；也允许复制单个输入项。未完全分析命名回调、间接辅助程序和嵌套累加器属性，因此不要声称所有二次方 reducer 都被排除在外。

   如果仓库在包清单中声明 `effect`，或者用户明确请求 Effect 规则，则还注册可选的 Effect 插件：

   ```ts
   jsPlugins: [
     {
       name: "anti-slop-effect",
       specifier: "./tools/oxlint/anti-slop/effect/index.ts",
     },
   ],
   rules: {
     "anti-slop-effect/no-manual-effect-error-tag": "error",
     "anti-slop-effect/no-manual-tag-comparison": "error",
     "anti-slop-effect/no-manual-tagged-construction": "error",
     "anti-slop-effect/no-service-constructor-imports": "error",
     "anti-slop-effect/prefer-effect-match": "error",
   },
   ```

   将这些条目与通用插件配置合并而不是替换它。不要仅仅因为 Effect 出现在锁文件中就启用 Effect 插件；需要直接的包清单依赖项或明确的用户请求。规则涵盖相对项目导入。将包别名导入报告为当前限制，而不是假装它们被强制执行。

   当通用规则和符合条件的 Effect 规则注册并保留现有配置时，即可完成。

4. 运行仓库的代码检查和类型检查。对于 Vite+，在添加 both lint 和 format 忽略后，运行仓库的完整 `vp check` 命令。如果发现出现在拥有的项目源中，只有在用户要求迁移/清理时才报告它们并修复它们。不要抑制规则、减弱规则严重性、添加不安全的类型转换或机械地清洗类型以使代码检查通过。

   当授权清理时，使用代码检查自动修复应用 `require-readable-spacing`，然后运行仓库的格式化程序和代码检查。确认第二次修复/格式化传递后文件保持不变。保留空白修复与语义编辑分开，保留文档附件和重载组，并且不要启用整个竞争的格式化预设。

   当检查运行、授权清理的修复/格式化稳定性得到验证，并且每个失败都被解决或报告其诊断时，即可完成。

5. 在捆绑的入口点旁边记录来源 `UPSTREAM.md`：源仓库、确切的源提交或可恢复的原始快照（如果可用）、安装的插件路径和有意偏差。验证修订版标识实际复制的资产；仅包版本或当前上游 HEAD 是不足够的。如果无法建立来源，则记录为未知而不是猜测。

   审查最终差异并报告安装路径、源身份、依赖项/配置更改和检查结果。当记录和报告描述实际安装的文件和任何剩余发现时，即可完成。
