# 异步 I/O 模型指南

Turso 使用协作式让步和显式状态机，而不是 Rust 的 async/await。

## 核心类型

```rust
pub enum IOCompletions {
    Single(Completion),
}

#[must_use]
pub enum IOResult<T> {
    Done(T),      // 操作完成，这是结果
    IO(IOCompletions),  // 需要 I/O，完成完成后再次调用我
}
```

返回 `IOResult` 的函数必须重复调用，直到 `Done`。

## 完成（Completion）和完成组（CompletionGroup）

`Completion` 追踪单个 I/O 操作：

```rust
pub struct Completion { /* ... */ }

impl Completion {
    pub fn finished(&self) -> bool;
    pub fn succeeded(&self) -> bool;
    pub fn get_error(&self) -> Option<CompletionError>;
}
```

要等待多个 I/O 操作，请使用 `CompletionGroup`：

```rust
let mut group = CompletionGroup::new(|_| {});

// 添加单个完成
group.add(&completion1);
group.add(&completion2);

// 构建为单个完成，当所有完成时结束
let combined = group.build();
io_yield_one!(combined);
```

`CompletionGroup` 的特性：
- 将多个完成聚合为一个
- 当所有完成时（或出现任何错误）调用回调
- 可以嵌套组（将一个组的完成添加到另一个组）
- 可通过 `group.cancel()` 取消

## 辅助宏

### `return_if_io!`
解包 `IOResult`，将 IO 变体向上传播到调用栈：
```rust
let result = return_if_io!(some_io_operation());
// 只有当操作返回 Done 时才会到达这里
```

### `io_yield_one!`
让步单个完成：
```rust
io_yield_one!(completion);  // 返回 Ok(IOResult::IO(Single(completion)))
```

## 状态机模式

可能让步的操作使用显式的状态枚举：

```rust
enum MyOperationState {
    Start,
    WaitingForRead { page: PageRef },
    Processing { data: Vec<u8> },
    Done,
}
```

函数循环，匹配状态并进行转换：

```rust
fn my_operation(&mut self) -> Result<IOResult<Output>> {
    loop {
        match &mut self.state {
            MyOperationState::Start => {
                let (page, completion) = start_read();
                self.state = MyOperationState::WaitingForRead { page };
                io_yield_one!(completion);
            }
            MyOperationState::WaitingForRead { page } => {
                let data = page.get_contents();
                self.state = MyOperationState::Processing { data: data.to_vec() };
                // 无需让步，继续循环
            }
            MyOperationState::Processing { data } => {
                let result = process(data);
                self.state = MyOperationState::Done;
                return Ok(IOResult::Done(result));
            }
            MyOperationState::Done => unreachable!(),
        }
    }
}
```

## 重新进入：关键陷阱

**在让步点之前的状态突变会导致重新进入时出现错误。**

### 错误示例
```rust
fn bad_example(&mut self) -> Result<IOResult<()>> {
    self.counter += 1;  // 状态突变
    return_if_io!(something_that_might_yield());  // 如果让步，重新进入将再次递增！
    Ok(IOResult::Done(()))
}
```

如果 `something_that_might_yield()` 返回 `IO`，调用者等待完成，然后再次调用 `bad_example()`。`counter` 会被递增两次（或更多）。

### 正确：让步后突变
```rust
fn good_example(&mut self) -> Result<IOResult<()>> {
    return_if_io!(something_that_might_yield());
    self.counter += 1;  // 只有在 I/O 完成后才会到达这里
    Ok(IOResult::Done(()))
}
```

### 正确：使用状态机
```rust
enum State { Start, AfterIO }

fn good_example(&mut self) -> Result<IOResult<()>> {
    loop {
        match self.state {
            State::Start => {
                // 在这里不要突变共享状态
                self.state = State::AfterIO;
                return_if_io!(something_that_might_yield());
            }
            State::AfterIO => {
                self.counter += 1;  // 安全：只进入一次
                return Ok(IOResult::Done(()));
            }
        }
    }
}
```

## 常见的重新进入错误

| 模式 | 问题 |
|---------|---------|
| `vec.push(x); return_if_io!(...)` | Vec 在每次重新进入时增长 |
| `idx += 1; return_if_io!(...)` | 索引多次前进 |
| `map.insert(k,v); return_if_io!(...)` | 重复插入或覆盖 |
| `flag = true; return_if_io!(...)` | 通常可以，但检查逻辑 |

## 状态枚举设计

在状态变体中编码进度：

```rust
// 好：索引是状态的一部分，跨让步保留
enum ProcessState {
    Start,
    ProcessingItem { idx: usize, items: Vec<Item> },
    Done,
}

// 循环仅在转换状态时才前进 idx
ProcessingItem { idx, items } => {
    return_if_io!(process_item(&items[idx]));
    if idx + 1 < items.len() {
        self.state = ProcessingItem { idx: idx + 1, items };
    } else {
        self.state = Done;
    }
}
```

## Turso 实现

关键文件：
- `core/types.rs` - `IOResult`, `IOCompletions`, `return_if_io!`, `return_and_restore_if_io!`
- `core/io/completions.rs` - `Completion`, `CompletionGroup`
- `core/util.rs` - `io_yield_one!` 宏
- `core/state_machine.rs` - 通用 `StateMachine` 包装器
- `core/storage/btree.rs` - 许多状态机示例
- `core/storage/pager.rs` - `CompletionGroup` 使用示例

## 测试异步代码

重新进入错误通常仅在特定 I/O 时间下才会显现。使用：
- 确定性模拟 (`testing/simulator/`)
- Whopper 并发 DST (`testing/concurrent-simulator/`)
- 故障注入以强制在不同点让步

## 参考文献

- `docs/manual.md` 中的 I/O 部分
