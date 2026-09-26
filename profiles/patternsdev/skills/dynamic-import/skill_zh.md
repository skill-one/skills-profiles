# 动态导入

在一个聊天应用中，我们有四个关键组件：`UserInfo`、`ChatList`、`ChatInput`和`EmojiPicker`。然而，在初始页面加载时，只有其中的三个组件会被立即使用：`UserInfo`、`ChatList`和`ChatInput`。`EmojiPicker`不会直接可见，如果用户甚至不会点击`Emoji`来切换`EmojiPicker`，它甚至可能根本不会被渲染。这意味着我们无谓地将`EmojiPicker`模块添加到了初始包中，这可能会增加加载时间！

为了解决这个问题，我们可以动态导入`EmojiPicker`组件。与其静态导入，我们只在需要显示`EmojiPicker`时才导入它。在React中动态导入组件的一种简单方法是使用**React Suspense**。`React.Suspense`组件接收应该动态加载的组件，这使得`App`组件能够通过挂起`EmojiPicker`模块的导入来更快地渲染其内容！

## 使用场景

- 当某些模块仅基于用户交互或条件时才需要使用
- 当你希望减少初始包的大小以加快页面加载速度时，这很有帮助
- 当模态框、选择器或重型库在初始渲染时不需要使用时，使用此方法

## 操作步骤

- 在React中使用`React.lazy`与`Suspense`进行动态组件导入
- 在动态导入模块时加载期间提供有意义的备用UI
- 考虑在React Suspense不受支持的SSR应用程序中使用`loadable-components`
- 仅动态导入对初始渲染不关键的模块

## 详细说明

与其无谓地将`EmojiPicker`添加到初始包中，我们可以将其拆分为自己的包，从而减少初始包的大小！

初始包越小，初始加载就越快：用户不必长时间盯着空白加载屏幕。`fallback`组件让用户知道我们的应用程序没有冻结：他们只需稍等片刻，等待模块被处理和执行。

```
资源                             大小         包件            包件名称
emoji-picker.bundle.js           1.48 KiB      1    [emitted]    emoji-picker
main.bundle.js                   1.33 MiB      main [emitted]    main
vendors~emoji-picker.bundle.js   171 KiB       2    [emitted]    vendors~emoji-picker
```

而之前初始包的大小是`1.5MiB`，通过挂起`EmojiPicker`的导入，我们已经将其减少到`1.33 MiB`！

通过动态导入`EmojiPicker`组件，我们将初始包的大小从`1.5MiB`减少到`1.33 MiB`！尽管用户可能仍需等待一段时间直到`EmojiPicker`完全加载完毕，但我们通过确保应用程序在用户等待组件加载时能够渲染和交互，从而改善了用户体验。

### 可加载组件

服务器端渲染不支持React Suspense（目前）。React Suspense的一个良好替代方案是`loadable-components`库，它可以在SSR应用程序中使用。

类似于React Suspense，我们可以将惰性导入的模块传递给`loadable`，它将仅在请求`EmojiPicker`模块时导入该模块！在模块加载期间，我们可以渲染一个`fallback`组件。

虽然可加载组件是SSR应用程序中React Suspense的绝佳替代方案，但它们在CSR应用程序中用于挂起模块导入也非常有用。

## 来源

- [patterns.dev/vanilla/dynamic-import](https://patterns.dev/vanilla/dynamic-import)
