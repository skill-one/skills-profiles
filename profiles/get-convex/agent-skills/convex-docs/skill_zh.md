<!-- GENERATED from convex-agents content/capabilities/convex-docs.json — do not edit by hand. -->

# 拉取 version-current Convex 文档

convex-expert 包含预置的、插件版本化的知识——非常适合稳定的惯用法，但它会在最关键的地方过时：一个获得了新导出的组件、一个改变了的 CLI 标志、一个版本间重命名的 API。这个能力是叠加在顶部的鲜活性规范：将版本固定到项目的实际版本，以极低的成本获取实时页面作为 markdown，并且当当前源是只需一次获取即可时，永远不要从记忆中编写不熟悉的 API。

## 工作流程

1. 固定版本：读取安装的 `convex` 版本 (`node -p "require('./node_modules/convex/package.json').version"` 或 `package.json`)，以及正在使用的任何 `@convex-dev/*` 组件的版本。你信任的文档必须匹配这些版本——版本偏差是导致 Convex 代码错误的最单一来源。
2. 鲜活性层级（从最经济正确的开始，Supabase 教授的顺序）：
   (a) 如果有可用的服务文档工具 / MCP `search_convex_docs`，则使用它（它返回版本范围的、重新排序的、适合上下文窗口大小的答案）；
   (b) 否则获取特定的文档页面作为 MARKDOWN——请求 `docs.convex.dev/<path>` 并在网站提供时优先选择 `.md`/markdown 格式（比 HTML 少得多令牌），或固定版本的组件的 README；
   (c) 只有到那时才回退到一般网络搜索，并将其版本视为未验证的。
   当当前性存疑时，不要跳转到从记忆中编写 API。
3. 在重要时刻与已安装的包进行验证：对于不确定是否存在的一个组件导出，检查 `node_modules/@convex-dev/<x>/`（它的 `package.json` `exports`，它的 `.d.ts`）——已安装的类型是这个版本的绝对真理，比任何文档更有权威性。
4. 狭义地使用获取的事实：应用当前的签名/标志，引用其来源（页面 + 版本），并将实际代码交还给 convex-expert 以惯用法编写。convex-docs 提供新鲜的事实；convex-expert 提供惯用法。
5. 在版本不匹配的构建错误时（一个“应该存在”但不存在导出/标志）：将其视为当前性问题——固定版本，获取当前 API，并修正——而不是猜测不同的拼写。

## 规则

- 当当前性存疑时，永远不要从模型记忆中编写不熟悉的或可能重命名的 Convex/组件 API——首先固定版本并获取当前源。
- 已安装包自带的 `exports`/`.d.ts` 在 `node_modules` 中是这个版本的绝对真理——比任何文档页面更有权威性。
- 遵循鲜活性层级：服务文档工具 → 页面作为 markdown / 固定的 README → 一般网络（未验证）——最经济正确的优先，最少的令牌。
- 优先选择 markdown 而不是 HTML 文档页面——相同内容所需的令牌远少。
- 提供新鲜的事实；将惯用法代码交还给 convex-expert。这是一个鲜活性层，而不是预置知识的替代品。
- 版本不匹配的构建错误是一个当前性问题，而不是拼写猜测——重新固定并重新获取。
