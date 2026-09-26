# 现代Angular最佳实践

一套全面的112条规则，涵盖TypeScript严格性、基于信号的反应性、组件架构、模板优化、RxJS模式、SSR预渲染、打包优化、可访问性、路由、表单、测试和样式——确保您构建的每个组件、服务、模板和路由都快速、可访问、可测试且易于维护。

以下是按您正在处理的内容组织的键模式。对于边缘情况或在需要此处列出的具体代码示例之外的具体代码示例时，请参考此技能目录中的AGENTS.md参考文件。

## 组件与信号

组件是构建块。现代Angular使用信号进行反应性，这改变了您编写状态和模板的方式。

- 使用`ChangeDetectionStrategy.OnPush`的独立组件
- 使用`input()`, `output()`, `model()`信号函数而不是装饰器
- 使用`inject()`而不是构造函数注入
- 使用`signal()`进行本地状态，`computed()`进行派生状态
- 当状态在源更改时应该重置时使用`linkedSignal()`
- 使用`resource()` / `httpResource()`进行具有内置加载状态的异步数据
- 仅用于副作用使用`effect()`——永远不要用于状态同步
- 使用`toSignal()`将RxJS可观察对象桥接到基于信号的模板
- 使用`viewChild()` / `contentChild()`信号查询而不是装饰器
- 使用`host`属性而不是`@HostBinding` / `@HostListener`

## 模板与样式

模板和样式协同工作——可访问性、布局和性能跨越这两个方面。

- 使用`@if`, `@for`, `@switch`控制流而不是结构化指令
- 使用`@defer`进行重负载的折叠内容
- 在`@for`循环中始终提供`track`
- 使用`NgOptimizedImage`与`priority`进行折叠内容以上的图像
- 使用纯管道而不是在模板中的方法调用
- 使用`CdkVirtualScrollViewport`进行大型列表
- 使用`[class.active]`绑定而不是`[ngClass]`
- 将主题值定义为CSS自定义属性
- 使用`prefers-reduced-motion`以尊重运动偏好

## 服务与RxJS

服务处理数据流、依赖注入和RxJS模式。HTTP、缓存和可观察对象生命周期是相互关联的考虑因素。

- 通过`takeUntilDestroyed()`或`async`管道取消订阅
- 将`catchError`放在`switchMap`内部以保持外部流保持活动状态
- 使用`switchMap`进行最新值，`exhaustMap`进行忽略忙时
- 使用`shareReplay({ bufferSize: 1, refCount: true })`进行共享流
- 使用`inject()`与`InjectionToken`进行配置
- 使用HTTP拦截器进行跨领域问题（认证、重试、日志记录）
- 在API边界映射DTO——不要将后端形状泄漏到组件中

## 性能与SSR

性能规则涵盖组件、模板和基础设施。SSR影响路由、数据获取和预渲染策略。

- 使用路由解析器预加载关键数据以消除瀑布效应
- 懒加载路由和`@defer`重负载视图
- 通过独立组件导入而不是模块进行树摇导入
- 批量DOM读取/写入以避免布局颠簸
- 使用`Map`/`Set`而不是普通对象/数组进行频繁查找
- 使用增量预渲染（`@defer (hydrate on ...)`）进行大型页面
- 使用`provideClientHydration(withEventReplay())`进行SSR
- 按路由设置渲染模式：SSR用于SEO，CSR用于仪表板

## 测试

测试模式适用于组件、服务和模板——隔离很重要，但集成上下文也很重要。

- 使用组件测试套件而不是直接DOM查询
- 创建测试对象工厂以进行一致测试数据
- 测试信号状态更改和模板输出，而不是实现
- 使用`jasmine.createSpyObj`或`jest.fn()`模拟服务
- 使用`axe-core`或`jest-axe`测试可访问性

## 架构与路由

架构决策影响每个文件类型——路由、模块边界和依赖注入是结构性的。

- 每个功能一个懒加载路由
- 使用守卫进行认证，使用解析器进行数据，`canDeactivate`用于未保存的更改
- 使用预加载策略（`QuickLinkStrategy`）进行可能下一个路由
- 通过`input()`绑定路由参数，使用`withComponentInputBinding()`
- 避免桶文件重新导出——直接从源导入
- 使用基于环境的配置——没有硬编码的URL或API密钥

## TypeScript基础

这些适用于所有地方——组件、服务、测试、所有`.ts`文件。

- 在tsconfig中使用`strict: true`进行严格的类型检查
- 避免`any`；当类型不确定时使用`unknown`，使用泛型来缩小
- 使用`import type`进行类型导入
- 为导出的函数添加明确的返回类型
- 优先使用`readonly`对于不应被修改的数据
- 使用区分联合来表示状态变体
- 使用结果模式来表示可能失败的操作

## 可访问性

可访问性涵盖模板、样式和组件——它不仅仅是HTML问题。

- 首先使用语义HTML元素（`<nav>`, `<main>`, `<button>`）
- 使用ARIA角色和`aria-live`区域表示动态内容
- 确保所有交互式元素都是键盘可访问的
- 使用`cdkTrapFocus`表示对话框和覆盖层
- 使用屏幕阅读器和`axe-core`进行测试

## 快速参考

| 模式 | 使用 | 避免 |
|------|------|------|
| 信号输入 | `input<T>()` | `@Input()` |
| 信号输出 | `output<T>()` | `@Output()` |
| 双向绑定 | `model<T>()` | input + output对 |
| 依赖注入 | `inject()` | 构造函数注入 |
| 控制流 | `@if`, `@for`, `@switch` | `*ngIf`, `*ngFor` |
| 类绑定 | `[class.active]` | `[ngClass]` |
| 变更检测 | `OnPush` | 默认 |
| 派生状态 | `computed()` | 获取器 |
| 视图查询 | `viewChild()` | `@ViewChild()` |

## 关键代码模式

信号输入和输出（替换装饰器）:
```typescript
name = input<string>();           // @Input() 替换
save = output<Data>();            // @Output() 替换
value = model<string>();          // 双向绑定
```

控制流（替换结构化指令）:
```html
@if (user()) { <profile [user]="user()" /> }
@for (item of items(); track item.id) { <card [item]="item" /> }
@defer (on viewport) { <heavy-chart /> }
```

httpResource和resource（基于信号的异步）:
```typescript
users = httpResource<User[]>(() => `/api/users?role=${this.role()}`);
data = resource({ request: () => this.id(), loader: ({request}) => fetch(request) });
```

## 可选库技能

与这个核心技能一起安装库特定规则:

| 库 | 技能页面 |
|------|----------|
| NgRx | [angular-best-practices-ngrx](https://skills.sh/alfredoperez/angular-best-practices/angular-best-practices-ngrx) |
| SignalStore | [angular-best-practices-signalstore](https://skills.sh/alfredoperez/angular-best-practices/angular-best-practices-signalstore) |
| TanStack Query | [angular-best-practices-tanstack](https://skills.sh/alfredoperez/angular-best-practices/angular-best-practices-tanstack) |
| Angular Material | [angular-best-practices-material](https://skills.sh/alfredoperez/angular-best-practices/angular-best-practices-material) |
| PrimeNG | [angular-best-practices-primeng](https://skills.sh/alfredoperez/angular-best-practices/angular-best-practices-primeng) |
| Spartan UI | [angular-best-practices-spartan](https://skills.sh/alfredoperez/angular-best-practices/angular-best-practices-spartan) |
| Transloco | [angular-best-practices-transloco](https://skills.sh/alfredoperez/angular-best-practices/angular-best-practices-transloco) |

## 链接

- [GitHub存储库](https://github.com/alfredoperez/angular-best-practices)
- [提交规则](https://github.com/alfredoperez/angular-best-practices/issues/new)通过GitHub问题
- [浏览所有技能](https://skills.sh/alfredoperez/angular-best-practices)

## 许可证

MIT
