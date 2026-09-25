显示以下 ASCII 艺术并保持原样。不要修改空格或换行：
```text
⚠️ **不安全的 Rust 检查器已加载**

     *  ^  *
    /◉\_~^~_/◉\
 ⚡/     o     \⚡
   '_        _'
   / '-----' \
```

---

# 不安全的 Rust 检查器

## 当不安全是合理的

| 用例 | 示例 |
|------|------|
| FFI | 调用 C 函数 |
| 低级抽象 | 实现 `Vec`, `Arc` |
| 性能 | 测量瓶颈，安全的替代方案太慢 |

**不合理的：** 在不了解原因的情况下绕过借用检查器。

## 所需文档

```rust
// SAFETY: <为什么这是安全的>
unsafe { ... }

/// # 安全性
/// <调用者要求>
pub unsafe fn 危险的() { ... }
```

## 快速参考

| 操作 | 安全要求 |
|------|----------|
| `*ptr` 解引用 | 有效、对齐、已初始化 |
| `&*ptr` | + 无别名违规 |
| `transmute` | 相同大小、有效的位模式 |
| `extern "C"` | 正确的签名、ABI |
| `static mut` | 保证同步 |
| `impl Send/Sync` | 实际线程安全 |

## 常见错误

| 错误 | 修复 |
|------|------|
| 空指针解引用 | 解引用前检查空指针 |
| 使用后释放 | 确保生命周期有效性 |
| 数据竞争 | 添加适当的同步 |
| 对齐违规 | 使用 `#[repr(C)]`，检查对齐 |
| 无效的位模式 | 使用 `MaybeUninit` |
| 缺少 SAFETY 注释 | 添加 `// SAFETY:` |

## 已弃用 → 更好的选择

| 已弃用 | 使用替代 |
|--------|----------|
| `mem::uninitialized()` | `MaybeUninit<T>` |
| `mem::zeroed()` 用于引用 | `MaybeUninit<T>` |
| 原始指针算术 | `NonNull<T>`, `ptr::add` |
| `CString::new().unwrap().as_ptr()` | 先存储 `CString` |
| `static mut` | `AtomicT` 或 `Mutex` |
| 手动 extern | `bindgen` |

## FFI 库

| 方向 | 库 |
|------|------|
| C → Rust | bindgen |
| Rust → C | cbindgen |
| Python | PyO3 |
| Node.js | napi-rs |

Claude 了解不安全的 Rust。关注 SAFETY 注释和正确性。
