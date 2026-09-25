# 现代JavaScript模式

全面指南，用于掌握现代JavaScript（ES6+）特性、函数式编程模式以及编写干净、可维护和高效的代码的最佳实践。

## 何时使用这项技能

- 重构遗留JavaScript到现代语法
- 实现函数式编程模式
- 优化JavaScript性能
- 编写可维护和可读的代码
- 处理异步操作
- 构建现代Web应用
- 从回调迁移到Promises/async-await
- 实现数据转换管道

## 详细模式和实例

详细模式文档位于`references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **默认使用const**：仅在需要重新赋值时使用let
2. **优先使用箭头函数**：尤其是在回调中
3. **使用模板字面量**：替代字符串拼接
4. **解构对象和数组**：使代码更清晰
5. **使用async/await**：替代Promise链
6. **避免修改数据**：使用展开运算符和数组方法
7. **使用可选链**：防止"Cannot read property of undefined"
8. **使用空值合并运算符**：用于默认值
9. **优先使用数组方法**：替代传统循环
10. **使用模块**：改善代码组织
11. **编写纯函数**：更易于测试和理解
12. **使用有意义的变量名**：代码自文档化
13. **保持函数简短**：单一职责原则
14. **正确处理错误**：使用try/catch与async/await
15. **使用严格模式**：使用`'use strict'`以更好地捕获错误

关于常见陷阱（this绑定、Promise反模式、内存泄漏），请参阅[references/advanced-patterns.md](references/advanced-patterns.md)。
