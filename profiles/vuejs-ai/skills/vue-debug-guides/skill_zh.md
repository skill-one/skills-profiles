Vue 3 运行时问题、警告、异步失败和 hydration 错误的调试和错误处理。
对于开发最佳实践和常见陷阱，请使用 `vue-best-practices`。

### 响应式系统
- 追踪意外的重新渲染和状态更新 → 查看 [reactivity-debugging-hooks](reference/reactivity-debugging-hooks.md)
- 由于缺少 .value 访问导致 Ref 值未更新 → 查看 [ref-value-access](reference/ref-value-access.md)
- 解构响应式对象后状态停止更新 → 查看 [reactive-destructuring](reference/reactive-destructuring.md)
- 数组、Map 或 Set 中的 Ref 未解包 → 查看 [refs-in-collections-need-value](reference/refs-in-collections-need-value.md)
- 模板中嵌套的 Ref 渲染为 [object Object] → 查看 [template-ref-unwrapping-top-level](reference/template-ref-unwrapping-top-level.md)
- 响应式代理身份比较始终返回 false → 查看 [reactivity-proxy-identity-hazard](reference/reactivity-proxy-identity-hazard.md)
- 代理时第三方实例失效 → 查看 [reactivity-markraw-for-non-reactive](reference/reactivity-markraw-for-non-reactive.md)
- 观察者意外地每帧只触发一次 → 查看 [reactivity-same-tick-batching](reference/reactivity-same-tick-batching.md)

### 计算属性
- 计算属性获取器意外触发变异或请求 → 查看 [computed-no-side-effects](reference/computed-no-side-effects.md)
- 修改计算属性值导致变化消失 → 查看 [computed-return-value-readonly](reference/computed-return-value-readonly.md)
- 条件逻辑后计算属性值从未更新 → 查看 [computed-conditional-dependencies](reference/computed-conditional-dependencies.md)
- 排序或反转数组破坏原始状态 → 查看 [computed-array-mutation](reference/computed-array-mutation.md)
- 向计算属性传递参数失败 → 查看 [computed-no-parameters](reference/computed-no-parameters.md)

### 观察者
- 异步操作使用过时的数据覆盖 → 查看 [watch-async-cleanup](reference/watch-async-cleanup.md)
- 在异步回调中创建观察者 → 查看 [watch-async-creation-memory-leak](reference/watch-async-creation-memory-leak.md)
- 观察者对响应式对象属性从未触发 → 查看 [watch-reactive-property-getter](reference/watch-reactive-property-getter.md)
- 异步 watchEffect 在 await 后错过依赖项 → 查看 [watcheffect-async-dependency-tracking](reference/watcheffect-async-dependency-tracking.md)
- 观察者回调中的 DOM 读取过时 → 查看 [watch-flush-timing](reference/watch-flush-timing.md)
- 深度观察者报告相同的旧/新值 → 查看 [watch-deep-same-object-reference](reference/watch-deep-same-object-reference.md)
- watchEffect 在模板 Ref 更新前运行 → 查看 [watcheffect-flush-post-for-refs](reference/watcheffect-flush-post-for-refs.md)

### 组件
- 子组件抛出 "组件未找到" 错误 → 查看 [local-components-not-in-descendants](reference/local-components-not-in-descendants.md)
- 自定义组件上的点击监听器未触发 → 查看 [click-events-on-components](reference/click-events-on-components.md)
- 父组件在脚本设置中无法访问子组件 Ref 数据 → 查看 [component-ref-requires-defineexpose](reference/component-ref-requires-defineexpose.md)
- HTML 模板解析破坏 Vue 组件语法 → 查看 [in-dom-template-parsing-caveats](reference/in-dom-template-parsing-caveats.md)
- 由于命名冲突导致渲染错误组件 → 查看 [component-naming-conflicts](reference/component-naming-conflicts.md)
- 父组件样式未应用于多根组件 → 查看 [multi-root-component-class-attrs](reference/multi-root-component-class-attrs.md)

### Props & Emits
- 在 defineProps 中引用变量导致错误 → 查看 [prop-defineprops-scope-limitation](reference/prop-defineprops-scope-limitation.md)
- 组件发出未声明的事件导致警告 → 查看 [declare-emits-for-documentation](reference/declare-emits-for-documentation.md)
- 在函数或条件语句中使用 defineEmits → 查看 [defineEmits-must-be-top-level](reference/defineEmits-must-be-top-level.md)
- defineEmits 同时具有类型和运行时参数 → 查看 [defineEmits-no-runtime-and-type-mixed](reference/defineEmits-no-runtime-and-type-mixed.md)
- 原生事件监听器未响应点击 → 查看 [native-event-collision-with-emits](reference/native-event-collision-with-emits.md)
- 点击时组件事件触发两次 → 查看 [undeclared-emits-double-firing](reference/undeclared-emits-double-firing.md)

### 模板
- 使用语句获取模板编译错误 → 查看 [template-expressions-restrictions](reference/template-expressions-restrictions.md)
- 运行时错误 "Cannot read property of undefined" → 查看 [v-if-null-check-order](reference/v-if-null-check-order.md)
- 动态指令参数未正常工作 → 查看 [dynamic-argument-constraints](reference/dynamic-argument-constraints.md)
- v-else 元素无条件始终渲染 → 查看 [v-else-must-follow-v-if](reference/v-else-must-follow-v-if.md)
- 混合 v-if 与 v-for 导致优先级问题和迁移破坏 → 查看 [no-v-if-with-v-for](reference/no-v-if-with-v-for.md)
- 模板函数调用变异状态导致不可预测的重新渲染错误 → 查看 [template-functions-no-side-effects](reference/template-functions-no-side-effects.md)
- 循环中的子组件显示未定义数据 → 查看 [v-for-component-props](reference/v-for-component-props.md)
- 排序或反转后数组顺序改变 → 查看 [v-for-computed-reverse-sort](reference/v-for-computed-reverse-sort.md)
- 列表项意外消失或交换状态 → 查看 [v-for-key-attribute](reference/v-for-key-attribute.md)
- 范围迭代时出现 off-by-one 错误 → 查看 [v-for-range-starts-at-one](reference/v-for-range-starts-at-one.md)
- v-show 或 v-else 在模板元素上未工作 → 查看 [v-show-template-limitation](reference/v-show-template-limitation.md)

### 模板 Refs
- 条件隐藏元素时 Ref 变为 null → 查看 [template-ref-null-with-v-if](reference/template-ref-null-with-v-if.md)
- 循环中 Ref 数组索引与数据数组不匹配 → 查看 [template-ref-v-for-order](reference/template-ref-v-for-order.md)
- 重构模板 Ref 名称导致代码中无声破坏 → 查看 [use-template-ref-vue35](reference/use-template-ref-vue35.md)

### 表单 & v-model
- 使用 v-model 时初始表单值未显示 → 查看 [v-model-ignores-html-attributes](reference/v-model-ignores-html-attributes.md)
- Textarea 内容变化未更新 Ref → 查看 [textarea-no-interpolation](reference/textarea-no-interpolation.md)
- iOS 用户无法选择下拉列表第一个选项 → 查看 [select-initial-value-ios-bug](reference/select-initial-value-ios-bug.md)
- 父组件和子组件值不同 → 查看 [define-model-default-value-sync](reference/define-model-default-value-sync.md)
- 对象属性变化未同步到父组件 → 查看 [definemodel-object-mutation-no-emit](reference/definemodel-object-mutation-no-emit.md)
- 中文/日文输入的实时搜索/验证失效 → 查看 [v-model-ime-composition](reference/v-model-ime-composition.md)
- 数字输入返回空字符串而不是零 → 查看 [v-model-number-modifier-behavior](reference/v-model-number-modifier-behavior.md)
- 自定义复选框值在表单中未提交 → 查看 [checkbox-true-false-value-form-submission](reference/checkbox-true-false-value-form-submission.md)

### 事件 & 修饰符
- 链接多个事件修饰符产生意外结果 → 查看 [event-modifier-order-matters](reference/event-modifier-order-matters.md)
- 系统修饰键不触发键盘快捷键 → 查看 [keyup-modifier-timing](reference/keyup-modifier-timing.md)
- 键盘快捷键意外触发修饰符组合 → 查看 [exact-modifier-for-precise-shortcuts](reference/exact-modifier-for-precise-shortcuts.md)
- 结合被动和 prevent 修饰符破坏事件行为 → 查看 [no-passive-with-prevent](reference/no-passive-with-prevent.md)

### 生命周期
- 未移除的事件监听器导致内存泄漏 → 查看 [cleanup-side-effects](reference/cleanup-side-effects.md)
- 组件挂载前 DOM 访问失败 → 查看 [lifecycle-dom-access-timing](reference/lifecycle-dom-access-timing.md)
- 状态变化后 DOM 读取返回过时值 → 查看 [dom-update-timing-nexttick](reference/dom-update-timing-nexttick.md)
- 服务器渲染与客户端 hydration 不同 → 查看 [lifecycle-ssr-awareness](reference/lifecycle-ssr-awareness.md)
- 异步注册的生命周期钩子从未运行 → 查看 [lifecycle-hooks-synchronous-registration](reference/lifecycle-hooks-synchronous-registration.md)

### 插槽
- 在插槽内容中访问子组件数据返回未定义值 → 查看 [slot-render-scope-parent-only](reference/slot-render-scope-parent-only.md)
- 混合命名和作用域插槽导致编译错误 → 查看 [slot-named-scoped-explicit-default](reference/slot-named-scoped-explicit-default.md)
- 在原生 HTML 元素上使用 v-slot 导致编译错误 → 查看 [slot-v-slot-on-components-or-templates-only](reference/slot-v-slot-on-components-or-templates-only.md)
- 隐式默认插槽行为导致意外内容放置 → 查看 [slot-implicit-default-content](reference/slot-implicit-default-content.md)
- 作用域插槽属性缺少预期名称 → 查看 [slot-name-reserved-prop](reference/slot-name-reserved-prop.md)
- 包装组件破坏子插槽功能 → 查看 [slot-forwarding-to-child-components](reference/slot-forwarding-to-child-components.md)

### Provide/Inject
- 异步操作后调用 provide 失败 → 查看 [provide-inject-synchronous-setup](reference/provide-inject-synchronous-setup.md)
- 追踪提供值来源 → 查看 [provide-inject-debugging-challenges](reference/provide-inject-debugging-challenges.md)
- 提供者变化时注入值未更新 → 查看 [provide-inject-reactivity-not-automatic](reference/provide-inject-reactivity-not-automatic.md)
- 多个组件共享相同默认对象 → 查看 [provide-inject-default-value-factory](reference/provide-inject-default-value-factory.md)

### Attrs
- 内部和穿透事件处理器同时执行 → 查看 [attrs-event-listener-merging](reference/attrs-event-listener-merging.md)
- 显式属性被穿透值覆盖 → 查看 [fallthrough-attrs-overwrite-vue3](reference/fallthrough-attrs-overwrite-vue3.md)
- 包装器中属性应用于错误元素 → 查看 [inheritattrs-false-for-wrapper-components](reference/inheritattrs-false-for-wrapper-components.md)

### Composables
- 在 setup 上下文外或异步调用可组合函数 → 查看 [composable-call-location-restrictions](reference/composable-call-location-restrictions.md)
- 可组合函数响应式依赖项在输入变化时未更新 → 查看 [composable-tovalue-inside-watcheffect](reference/composable-tovalue-inside-watcheffect.md)
- 可组合函数意外变异外部状态 → 查看 [composable-avoid-hidden-side-effects](reference/composable-avoid-hidden-side-effects.md)
- 解构可组合函数返回破坏响应性 → 查看 [composable-naming-return-pattern](reference/composable-naming-return-pattern.md)

### Composition API
- 异步操作后生命周期钩子无声失败 → 查看 [composition-api-script-setup-async-context](reference/composition-api-script-setup-async-context.md)
- 父组件 Ref 无法访问暴露属性 → 查看 [define-expose-before-await](reference/define-expose-before-await.md)
- 函数式编程模式破坏预期 Vue 响应性行为 → 查看 [composition-api-not-functional-programming](reference/composition-api-not-functional-programming.md)
- React 钩子思维模式导致 Composition API 使用错误 → 查看 [composition-api-vs-react-hooks-differences](reference/composition-api-vs-react-hooks-differences.md)

### 动画
- 动态 DOM 节点重用时动画失败 → 查看 [animation-key-for-rerender](reference/animation-key-for-rerender.md)
- TransitionGroup 列表更新在负载下感觉卡顿 → 查看 [animation-transitiongroup-performance](reference/animation-transitiongroup-performance.md)

### TypeScript
- 可变 prop 默认值在组件实例间泄漏状态 → 查看 [ts-withdefaults-mutable-factory-function](reference/ts-withdefaults-mutable-factory-function.md)
- reactive() 泛型类型导致 Ref 解包不匹配 → 查看 [ts-reactive-no-generic-argument](reference/ts-reactive-no-generic-argument.md)
- 模板 Ref 在挂载前或 v-if 卸载后抛出 null 访问错误 → 查看 [ts-template-ref-null-handling](reference/ts-template-ref-null-handling.md)
- 可选布尔 prop 行为为 false 而不是 undefined → 查看 [ts-defineprops-boolean-default-false](reference/ts-defineprops-boolean-default-false.md)
- 导入的 defineProps 类型因无法解析或复杂类型引用失败 → 查看 [ts-defineprops-imported-types-limitations](reference/ts-defineprops-imported-types-limitations.md)
- 在严格 TypeScript 设置下未定义的 DOM 事件处理器失败 → 查看 [ts-event-handler-explicit-typing](reference/ts-event-handler-explicit-typing.md)
- 动态组件 Ref 触发响应式组件警告 → 查看 [ts-shallowref-for-dynamic-components](reference/ts-shallowref-for-dynamic-components.md)
- 联合类型模板表达式未缩小时失败类型检查 → 查看 [ts-template-type-casting](reference/ts-template-type-casting.md)

### 异步组件
- 路由组件使用 defineAsyncComponent 懒加载配置错误 → 查看 [async-component-vue-router](reference/async-component-vue-router.md)
- 网络故障或超时加载组件 → 查看 [async-component-error-handling](reference/async-component-error-handling.md)
- 组件重新激活后模板 Ref 未定义 → 查看 [async-component-keepalive-ref-issue](reference/async-component-keepalive-ref-issue.md)

### 渲染函数
- 状态变化后渲染函数输出保持静态 → 查看 [rendering-render-function-return-from-setup](reference/rendering-render-function-return-from-setup.md)
- 重用的 vnode 实例渲染错误 → 查看 [render-function-vnodes-must-be-unique](reference/render-function-vnodes-must-be-unique.md)
- 字符串组件名渲染为 HTML 元素 → 查看 [rendering-resolve-component-for-string-names](reference/rendering-resolve-component-for-string-names.md)
- 访问 vnode 内部属性在 Vue 更新时破坏 → 查看 [render-function-avoid-internal-vnode-properties](reference/render-function-avoid-internal-vnode-properties.md)
- Vue 2 渲染函数模式在 Vue 3 中崩溃 → 查看 [rendering-render-function-h-import-vue3](reference/rendering-render-function-h-import-vue3.md)
- 从 h() 未渲染插槽内容 → 查看 [rendering-render-function-slots-as-functions](reference/rendering-render-function-slots-as-functions.md)

### KeepAlive
- 嵌套 Vue Router 路由时子组件挂载两次 → 查看 [keepalive-router-nested-double-mount](reference/keepalive-router-nested-double-mount.md)
- 结合 KeepAlive 与 Transition 动画时内存增长 → 查看 [keepalive-transition-memory-leak](reference/keepalive-transition-memory-leak.md)

### 过渡
- JavaScript 过渡钩子未挂载 done 回调 → 查看 [transition-js-hooks-done-callback](reference/transition-js-hooks-done-callback.md)
- 移动动画在行内列表元素上失败 → 查看 [transition-group-flip-inline-elements](reference/transition-group-flip-inline-elements.md)
- 列表项跳跃而不是平滑动画 → 查看 [transition-group-move-animation-position-absolute](reference/transition-group-move-animation-position-absolute.md)
- Vue 2 到 Vue 3 TransitionGroup 包装器更改破坏布局 → 查看 [transition-group-no-default-wrapper-vue3](reference/transition-group-no-default-wrapper-vue3.md)
- 嵌套过渡在完成前被截断 → 查看 [transition-nested-duration](reference/transition-nested-duration.md)
- 可重用过渡包装器中作用域样式失效 → 查看 [transition-reusable-scoped-style](reference/transition-reusable-scoped-style.md)
- RouterView 过渡在首次渲染时意外动画 → 查看 [transition-router-view-appear](reference/transition-router-view-appear.md)
- 混合 CSS 过渡和动画导致时间问题 → 查看 [transition-type-when-mixed](reference/transition-type-when-mixed.md)
- 快速过渡交换期间错过清理钩子 → 查看 [transition-unmount-hook-timing](reference/transition-unmount-hook-timing.md)

### Teleport
- Teleport 目标元素未在 DOM 中找到 → 查看 [teleport-target-must-exist](reference/teleport-target-must-exist.md)
- Teleport 内容破坏 SSR hydration → 查看 [teleport-ssr-hydration](reference/teleport-ssr-hydration.md)
- 作用域样式未应用于 Teleport 内容 → 查看 [teleport-scoped-styles-limitation](reference/teleport-scoped-styles-limitation.md)

### Suspense
- 需要处理 Suspense 组件的异步错误 → 查看 [suspense-no-builtin-error-handling](reference/suspense-no-builtin-error-handling.md)
- 使用 Suspense 与服务器端渲染 → 查看 [suspense-ssr-hydration-issues](reference/suspense-ssr-hydration-issues.md)
- 在 Suspense 下异步组件加载/错误 UI 被忽略 → 查看 [async-component-suspense-control](reference/async-component-suspense-control.md)

### SSR
- 服务器和客户端渲染的 HTML 不同 → 查看 [ssr-hydration-mismatch-causes](reference/ssr-hydration-mismatch-causes.md)
- 从共享单例存储跨请求泄漏用户状态 → 查看 [state-ssr-cross-request-pollution](reference/state-ssr-cross-request-pollution.md)
- 浏览器专用 API 在通用代码路径中崩溃服务器渲染 → 查看 [ssr-platform-specific-apis](reference/ssr-platform-specific-apis.md)

### 性能
- 由于父组件传递不稳定 prop 导致列表子组件不必要的重新渲染 → 查看 [perf-props-stability-update-optimization](reference/perf-props-stability-update-optimization.md)
- 计算对象尽管值等效仍重新触发效果 → 查看 [perf-computed-object-stability](reference/perf-computed-object-stability.md)

### SFC (单文件组件)
- 尝试从组件脚本块使用命名导出 → 查看 [sfc-named-exports-forbidden](reference/sfc-named-exports-forbidden.md)
- 脚本更改后模板中的变量未更新 → 查看 [sfc-script-setup-reactivity](reference/sfc-script-setup-reactivity.md)
- 作用域样式未应用于子组件元素 → 查看 [sfc-scoped-css-child-component-styling](reference/sfc-scoped-css-child-component-styling.md)
- 作用域样式未应用于动态 v-html 内容 → 查看 [sfc-scoped-css-dynamic-content](reference/sfc-scoped-css-dynamic-content.md)
- 作用域样式未应用于插槽内容 → 查看 [sfc-scoped-css-slot-content](reference/sfc-scoped-css-slot-content.md)
- 动态构建时 Tailwind 类缺失 → 查看 [tailwind-dynamic-class-generation](reference/tailwind-dynamic-class-generation.md)
- 由于名称冲突导致递归组件未渲染 → 查看 [self-referencing-component-name](reference/self-referencing-component-name.md)

### 插件
- 调试全局属性导致命名冲突的原因 → 查看 [plugin-global-properties-sparingly](reference/plugin-global-properties-sparingly.md)
- 插件未工作或 inject 返回 undefined → 查看 [plugin-install-before-mount](reference/plugin-install-before-mount.md)
- 插件全局属性在基于 setup 的组件中不可用 → 查看 [plugin-prefer-provide-inject-over-global-properties](reference/plugin-prefer-provide-inject-over-global-properties.md)
- 插件类型增强错误破坏 ComponentCustomProperties 类型 → 查看 [plugin-typescript-type-augmentation](reference/plugin-typescript-type-augmentation.md)

### App 配置
- 挂载调用后 App 配置方法未工作 → 查看 [configure-app-before-mount](reference/configure-app-before-mount.md)
- 在 mount() 上链式 App 配置失败因为 mount 返回组件实例 → 查看 [mount-return-value](reference/mount-return-value.md)
- require.context 基于的组件自动注册在 Vite 中失败 → 查看 [dynamic-component-registration-vite](reference/dynamic-component-registration-vite.md)
