### 测试结构
- 使用 `.test.ts` 或 `.test.js` 后缀命名测试文件
- 将测试文件放在被测试代码旁边或专门的 `__tests__` 目录中
- 使用描述性的测试名称来解释预期行为
- 使用嵌套的 `describe` 块来组织相关的测试
- 遵循以下模式：`describe('Component/Function/Class', () => { it('should do something', () => {}) })`

### 高效的模拟
- 模拟外部依赖（API、数据库等）以隔离测试
- 使用 `jest.mock()` 进行模块级别的模拟
- 使用 `jest.spyOn()` 进行特定函数的模拟
- 使用 `mockImplementation()` 或 `mockReturnValue()` 定义模拟行为
- 在 `afterEach` 中使用 `jest.resetAllMocks()` 在测试之间重置模拟

### 测试异步代码
- 在测试中始终返回 Promise 或使用 async/await 语法
- 使用 `resolves`/`rejects` 匹配器进行 Promise 测试
- 使用 `jest.setTimeout()` 为慢速测试设置适当的超时

### 快照测试
- 对不经常变化的 UI 组件或复杂对象使用快照测试
- 保持快照简洁和专注
- 在提交前仔细审查快照变更

### 测试 React 组件
- 使用 React Testing Library 而不是 Enzyme 测试组件
- 测试用户行为和组件的可访问性
- 通过可访问性角色、标签或文本内容查询元素
- 使用 `userEvent` 而不是 `fireEvent` 进行更真实的用户交互

## 常见的 Jest 匹配器
- 基本：`expect(value).toBe(expected)`，`expect(value).toEqual(expected)`
- 布尔值：`expect(value).toBeTruthy()`，`expect(value).toBeFalsy()`
- 数字：`expect(value).toBeGreaterThan(3)`，`expect(value).toBeLessThanOrEqual(3)`
- 字符串：`expect(value).toMatch(/pattern/)`，`expect(value).toContain('substring')`
- 数组：`expect(array).toContain(item)`，`expect(array).toHaveLength(3)`
- 对象：`expect(object).toHaveProperty('key', value)`
- 异常：`expect(fn).toThrow()`，`expect(fn).toThrow(Error)`
- 模拟函数：`expect(mockFn).toHaveBeenCalled()`，`expect(mockFn).toHaveBeenCalledWith(arg1, arg2)`
