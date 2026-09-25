# Go 代码审查清单

> 兼容性：`references/WEB-SERVER.md` 使用 `log/slog` 示例，需要 Go 1.21+。

## 资源路由

- `assets/review-template.md` - 用于使用 Must Fix、Should Fix 和 Nits 部分格式化审查输出。
- `scripts/pre-review.sh` - 在手动审查前运行，收集 gofmt、go vet 和 golangci-lint 结果。
- `references/WEB-SERVER.md` - 在审查结合了并发、上下文、日志记录、错误处理和关闭行为的 HTTP 服务器时阅读。

## 审查流程

> 使用 `assets/review-template.md` 格式化代码审查输出，确保与 Must Fix / Should Fix / Nits 严重性分组一致的结构的结构。

1. 运行 `gofmt -d .` 和 `go vet ./...` 以首先捕获机械问题
2. 逐文件阅读差异；对于每个文件，按以下顺序检查类别
3. 使用特定行引用和规则名称标记问题
4. 审查所有文件后，重新阅读标记的项目以验证它们是真实的问题
5. 按严重性（必须修复、应该修复、小问题）分组总结发现

> **验证**：完成审查后，再次阅读差异以验证每个标记的问题都是真实的。删除您无法使用特定行引用证明的任何发现。

---

## 格式化

- [ ] **gofmt**：代码使用 `gofmt` 或 `goimports` 格式化 → [go-linting](../go-linting/SKILL.md)

---

## 文档

- [ ] **注释句子**：注释是完整的句子，以被描述的名称开头，以句号结尾 → [go-documentation](../go-documentation/SKILL.md)
- [ ] **文档注释**：所有导出的名称都有文档注释；非平凡的未导出声明也是如此 → [go-documentation](../go-documentation/SKILL.md)
- [ ] **包注释**：包注释紧邻包声明，没有空行 → [go-documentation](../go-documentation/SKILL.md)
- [ ] **命名结果参数**：仅在它们澄清含义时使用（例如，多个相同类型的返回），而不仅仅是为了启用裸返回 → [go-documentation](../go-documentation/SKILL.md)

---

## 错误处理

- [ ] **处理错误**：不使用 `_` 丢弃错误；处理、返回或（例外情况）恐慌 → [go-error-handling](../go-error-handling/SKILL.md)
- [ ] **错误字符串**：小写，没有标点符号（除非以专有名词/缩写开头）→ [go-error-handling](../go-error-handling/SKILL.md)
- [ ] **带内错误**：不使用魔法值（-1、""、nil）；使用带错误或 ok bool 的多个返回 → [go-error-handling](../go-error-handling/SKILL.md)
- [ ] **错误流程缩进**：首先处理错误并返回；保持正常路径的最小缩进 → [go-error-handling](../go-error-handling/SKILL.md)

---

## 命名

- [ ] **MixedCaps**：使用 `MixedCaps` 或 `mixedCaps`，从不使用下划线；未导出的是 `maxLength` 而不是 `MAX_LENGTH` → [go-naming](../go-naming/SKILL.md)
- [ ] **首字母缩写词**：保持一致的案例：`URL`/`url`、`ID`/`id`、`HTTP`/`http`（例如，`ServeHTTP`、`xmlHTTPRequest`）→ [go-naming](../go-naming/SKILL.md)
- [ ] **变量名**：短名用于有限范围（`i`、`r`、`c`）；较长名用于更广范围 → [go-naming](../go-naming/SKILL.md)
- [ ] **接收者名**：类型的一到两个字母缩写（`c` 用于 `Client`）；不使用 `this`、`self`、`me`；跨方法一致 → [go-naming](../go-naming/SKILL.md)
- [ ] **包名**：不使用重复（使用 `chubby.File` 而不是 `chubby.ChubbyFile`）；避免 `util`、`common`、`misc` → [go-packages](../go-packages/SKILL.md)
- [ ] **避免内置名**：不要遮蔽 `error`、`string`、`len`、`cap`、`append`、`copy`、`new`、`make` → [go-declarations](../go-declarations/SKILL.md)

---

## 并发

- [ ] **Goroutine 生命周期**：明确 goroutines 何时/是否退出；如果不明显，请记录 → [go-concurrency](../go-concurrency/SKILL.md)
- [ ] **同步函数**：优先使用同步而不是异步；如果需要，让调用者添加并发 → [go-concurrency](../go-concurrency/SKILL.md)
- [ ] **上下文**：第一个参数；不在结构中；不使用自定义上下文类型；即使认为不需要也要传递 → [go-context](../go-context/SKILL.md)

---

## 接口

- [ ] **接口位置**：在消费者包中定义，而不是实现者；从生产者返回具体类型 → [go-interfaces](../go-interfaces/SKILL.md)
- [ ] **过早接口**：在未使用前不要定义；在实现者侧不要定义“用于模拟” → [go-interfaces](../go-interfaces/SKILL.md)
- [ ] **接收者类型**：如果可变、有同步字段或很大，则使用指针；对于小的不变类型使用值；不要混合 → [go-interfaces](../go-interfaces/SKILL.md)

---

## 数据结构

- [ ] **空切片**：优先使用 `var t []string`（nil）而不是 `t := []string{}`（非 nil 零长度）→ [go-data-structures](../go-data-structures/SKILL.md)
- [ ] **复制**：小心复制具有指针/切片字段的 struct；不要按值复制 `*T` 方法的接收者 → [go-data-structures](../go-data-structures/SKILL.md)

---

## 安全

- [ ] **Crypto rand**：使用 `crypto/rand` 用于密钥，而不是 `math/rand` → [go-defensive](../go-defensive/SKILL.md)
- [ ] **不要恐慌**：使用错误返回进行正常错误处理；仅在真正异常的情况下恐慌 → [go-defensive](../go-defensive/SKILL.md)

---

## 声明和初始化

- [ ] **分组相似**：将相关的 `var`/`const`/`type` 分组在括号块中；分离不相关的 → [go-declarations](../go-declarations/SKILL.md)
- [ ] **var vs :=**：使用 `var` 用于有意为零的值；`:=` 用于显式赋值 → [go-declarations](../go-declarations/SKILL.md)
- [ ] **减少作用域**：将声明移近使用位置；使用 if-init 限制变量作用域 → [go-declarations](../go-declarations/SKILL.md)
- [ ] **结构初始化**：始终使用字段名；省略零字段；`var` 用于零结构 → [go-declarations](../go-declarations/SKILL.md)
- [ ] **使用 `any`**：在新代码中优先使用 `any` 而不是 `interface{}` → [go-declarations](../go-declarations/SKILL.md)

---

## 函数

- [ ] **文件排序**：类型 → 构造函数 → 导出方法 → 未导出 → 工具 → [go-functions](../go-functions/SKILL.md)
- [ ] **签名格式化**：所有参数单独一行，并在包装时带有尾随逗号 → [go-functions](../go-functions/SKILL.md)
- [ ] **裸参数**：为歧义的布尔/整型参数添加 `/* name */` 注释，或使用自定义类型 → [go-functions](../go-functions/SKILL.md)
- [ ] **Printf 命名**：接受格式字符串的函数以 `f` 结尾，以便 `go vet` → [go-functions](../go-functions/SKILL.md)

---

## 风格

- [ ] **行长度**：没有严格的限制，但避免不舒适的过长行；按语义而不是任意长度断行 → [go-style-core](../go-style-core/SKILL.md)
- [ ] **裸返回**：仅在短函数中使用；在中等/长函数中使用显式返回 → [go-style-core](../go-style-core/SKILL.md)
- [ ] **传递值**：不要仅为了节省字节而使用指针；对于小固定大小类型传递 `string` 而不是 `*string` → [go-performance](../go-performance/SKILL.md)
- [ ] **字符串连接**：`+` 用于简单；`fmt.Sprintf` 用于格式化；`strings.Builder` 用于循环 → [go-performance](../go-performance/SKILL.md)

---

## 日志记录

- [ ] **使用 slog**：新代码使用 `log/slog`，而不是 `log` 或 `fmt.Println` 用于操作日志 → [go-logging](../go-logging/SKILL.md)
- [ ] **结构化字段**：日志消息使用静态字符串和键值属性，而不是 `fmt.Sprintf` → [go-logging](../go-logging/SKILL.md)
- [ ] **适当级别**：Debug 用于开发者跟踪，Info 用于显著事件，Warn 用于可恢复问题，Error 用于失败 → [go-logging](../go-logging/SKILL.md)
- [ ] **日志中无秘密**：PII、凭证和令牌永远不会记录 → [go-logging](../go-logging/SKILL.md)

---

## 导入

- [ ] **导入组**：标准库首先，然后空行，然后外部包 → [go-packages](../go-packages/SKILL.md)
- [ ] **导入重命名**：除非冲突；在冲突时重命名本地/项目特定的导入 → [go-packages](../go-packages/SKILL.md)
- [ ] **导入空白**：`import _ "pkg"` 仅在主包或测试中 → [go-packages](../go-packages/SKILL.md)
- [ ] **导入点**：仅在测试中用于循环依赖的解决方案 → [go-packages](../go-packages/SKILL.md)

---

## 泛型

- [ ] **何时使用**：仅在多个类型共享相同逻辑且接口不足时使用 → [go-generics](../go-generics/SKILL.md)
- [ ] **类型别名**：使用定义用于新类型；别名仅用于包迁移 → [go-generics](../go-generics/SKILL.md)

---

## 测试

- [ ] **示例**：包含可运行的 `Example` 函数或测试以演示用法 → [go-documentation](../go-documentation/SKILL.md)
- [ ] **有用的测试失败**：消息包括什么不正确、输入、得到和期望；顺序是 `got != want` → [go-testing](../go-testing/SKILL.md)
- [ ] **TestMain**：仅在所有测试需要通用设置和清理时使用；优先使用作用域帮助程序 → [go-testing](../go-testing/SKILL.md)
- [ ] **真实传输**：优先使用 `httptest.NewServer` + 真实客户端而不是模拟 HTTP → [go-testing](../go-testing/SKILL.md)

---

## 自动检查

运行自动预审查检查：

```bash
bash scripts/pre-review.sh ./...         # 文本输出
bash scripts/pre-review.sh --json ./...  # 结构化 JSON 输出
```

或手动：`gofmt -l <path> && go vet ./... && golangci-lint run ./...`

在继续上述清单之前修复任何问题。有关 linter 设置和配置，请参阅 [go-linting](../go-linting/SKILL.md)。

---

## 相关技能

- **风格基础**：在解决格式化争议或应用清晰度 > 简洁性 > 精炼优先级时，请参阅 [go-style-core](../go-style-core/SKILL.md)
- **Linting 设置**：在配置 golangci-lint 或向 CI 添加自动检查时，请参阅 [go-linting](../go-linting/SKILL.md)
- **错误策略**：在审查错误包装、哨兵错误或处理一次模式时，请参阅 [go-error-handling](../go-error-handling/SKILL.md)
- **命名约定**：在评估标识符名称、接收者名称或包符号重复时，请参阅 [go-naming](../go-naming/SKILL.md)
- **测试模式**：在审查测试代码的表格驱动结构、失败消息或帮助程序使用时，请参阅 [go-testing](../go-testing/SKILL.md)
- **并发安全**：在审查 goroutine 生命周期、通道使用或互斥锁放置时，请参阅 [go-concurrency](../go-concurrency/SKILL.md)
- **日志实践**：在审查日志使用、结构化日志或 slog 配置时，请参阅 [go-logging](../go-logging/SKILL.md)
