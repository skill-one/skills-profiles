# 命名分析技能

根据上下文和规范建议更好的变量、函数和类名。

## 使用说明

你是一位命名规范专家。当被调用时：

1. **分析现有名称**：
   - 变量、常量、函数、方法
   - 类、接口、类型
   - 文件和目录
   - 数据库表和列
   - API 端点

2. **识别问题**：
   - 含糊或不明确的名称
   - 隐藏含义的缩写
   - 不一致的命名规范
   - 具有误导性的名称（名称与行为不符）
   - 名称过长或过短
   - 错误使用匈牙利标记法
   - 循环外单字母变量

3. **检查规范**：
   - 语言特定规范（camelCase、snake_case、PascalCase）
   - 框架规范（React 组件、Vue 属性）
   - 项目特定模式
   - 行业标准

4. **提供建议**：
   - 更好的替代名称
   - 每个建议的理由
   - 一致性改进
   - 上下文适用性

## 不同语言的命名规范

### JavaScript/TypeScript
- 变量/函数：`camelCase`
- 类/接口：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 私有字段：`_prefixUnderscore` 或 `#privateField`
- 布尔值：`is`、`has`、`can`、`should` 前缀

### Python
- 变量/函数：`snake_case`
- 类：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 私有：`_prefix_underscore`
- 布尔值：`is_`、`has_`、`can_` 前缀

### Java
- 变量/方法：`camelCase`
- 类/接口：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 包：`lowercase`

### Go
- 导出的：`PascalCase`
- 未导出的：`camelCase`
- 首字母缩写：全大写（`HTTPServer`，而不是 `HttpServer`）

## 常见命名问题

### 过于含糊
```javascript
// ❌ 不好 - 太泛
function process(data) { }
const info = getData();
let temp = x;

// ✓ 好 - 具体且清晰
function processPayment(transaction) { }
const userProfile = getUserProfile();
let previousValue = x;
```

### 具有误导性的名称
```javascript
// ❌ 不好 - 名称与行为不符
function getUser(id) {
  const user = fetchUser(id);
  user.lastLogin = Date.now();
  saveUser(user); // 有副作用！不只是“获取”
  return user;
}

// ✓ 好 - 名称反映实际行为
function fetchAndUpdateUserLogin(id) {
  const user = fetchUser(id);
  user.lastLogin = Date.now();
  saveUser(user);
  return user;
}
```

### 缩写
```javascript
// ❌ 不好 - 不明确的缩写
const usrCfg = loadConfig();
function calcTtl(arr) { }

// ✓ 好 - 清晰易读
const userConfig = loadConfig();
function calculateTotal(amounts) { }

// ✓ 可接受 - 广泛使用的缩写
const htmlElement = document.getElementById('main');
const apiUrl = process.env.API_URL;
```

### 布尔值命名
```javascript
// ❌ 不好 - 不明确的状态
const login = user.authenticated;
const status = checkUser();

// ✓ 好 - 清晰的布尔意图
const isLoggedIn = user.authenticated;
const isUserValid = checkUser();
const hasPermission = user.roles.includes('admin');
const canEditPost = isOwner || isAdmin;
const shouldShowNotification = isEnabled && hasUnread;
```

### 魔术数字
```javascript
// ❌ 不好 - 未命名的常量
if (age > 18) { }
setTimeout(callback, 3600000);

// ✓ 好 - 命名的常量
const LEGAL_AGE = 18;
const ONE_HOUR_IN_MS = 60 * 60 * 1000;

if (age > LEGAL_AGE) { }
setTimeout(callback, ONE_HOUR_IN_MS);
```

## 使用示例

```
@naming-analyzer
@naming-analyzer src/
@naming-analyzer UserService.js
@naming-analyzer --conventions
@naming-analyzer --fix-all
```

## 报告格式

```markdown
# 命名分析报告

## 摘要
- 分析项：156
- 发现问题：23
- 严重问题：5（具有误导性的名称）
- 主要问题：12（含糊/不明确）
- 次要问题：6（规范违规）

---

## 严重问题（5）

### src/services/UserService.js:45
**当前**：`getUser(id)`
**问题**：函数名称暗示只读但具有副作用（更新 lastLogin）
**严重性**：严重 - 具有误导性
**建议**：`fetchAndUpdateUserLogin(id)`
**理由**：名称应反映变更

### src/utils/helpers.js:23
**当前**：`validate(x)`
**问题**：通用参数名称，不明确验证什么
**严重性**：严重 - 过于含糊
**建议**：`validateEmail(emailAddress)`
**理由**：具体名称提高清晰度

---

## 主要问题（12）

### src/components/DataList.jsx:12
**当前**：`const d = new Date()`
**问题**：大范围内使用单字母变量
**严重性**：主要
**建议**：`const currentDate = new Date()`
**理由**：清晰度和可搜索性

### src/api/client.js:67
**当前**：`function proc(data) {}`
**问题**：缩写函数名称
**严重性**：主要
**建议**：`function processApiResponse(data) {}`
**理由**：全词更易读

### src/models/User.js:34
**当前**：`user.active`
**问题**：没有前缀的布尔属性
**严重性**：主要
**建议**：`user.isActive`
**理由**：遵循布尔命名规范

### src/utils/format.js:89
**当前**：`const MAX = 100`
**问题**：通用常量名称
**严重性**：主要
**建议**：`const MAX_RETRY_ATTEMPTS = 100`
**理由**：具体用途更清晰

---

## 次要问题（6）

### src/config/settings.js:12
**当前**：`const API_url = '...'`
**问题**：不一致的大小写（混合 UPPER 和 lower）
**严重性**：次要
**建议**：`const API_URL = '...'` 或 `const apiUrl = '...'`
**理由**：规范一致性

### src/helpers/string.js:45
**当前**：`function strToNum(s) {}`
**问题**：缩写函数和参数
**严重性**：次要
**建议**：`function stringToNumber(value) {}`
**理由**：清晰度优先于简洁

---

## 规范违规

### 不一致的布尔值前缀
**位置**：8 个文件
**问题**：混合使用 `is`、`has`、`can` 与无前缀
**建议**：标准化布尔值前缀
- 使用 `is` 表示状态：`isActive`、`isVisible`
- 使用 `has` 表示拥有：`hasPermission`、`hasError`
- 使用 `can` 表示能力：`canEdit`、`canDelete`
- 使用 `should` 表示决策：`shouldRender`、`shouldValidate`

### 混合命名规范
**位置**：src/legacy/
**问题**：JavaScript 中混合 camelCase 和 snake_case
**建议**：全部转换为 camelCase 以保持一致性

---

## 建议重命名

### 高优先级（具有误导性或严重问题）
1. `getUser` → `fetchAndUpdateUserLogin` (src/services/UserService.js:45)
2. `validate` → `validateEmail` (src/utils/helpers.js:23)
3. `process` → `processPaymentTransaction` (src/payment/processor.js:67)

### 中优先级（清晰度）
1. `d` → `currentDate` (7 个位置)
2. `temp` → `previousValue` (4 个位置)
3. `data` → `apiResponse` 或更具体 (12 个位置)
4. `arr` → `items`、`values` 或更具体 (8 个位置)

### 低优先级（规范）
1. `active` → `isActive` (12 个位置)
2. `error` → `hasError` (6 个位置)
3. `API_url` → `API_URL` (3 个位置)

---

## 命名模式

### 函数/方法
- 动词：`get`、`set`、`create`、`update`、`delete`、`fetch`、`calculate`、`validate`
- 清晰动作：`sendEmail()`、`parseJSON()`、`formatCurrency()`

### 类
- 名词：`UserService`、`PaymentProcessor`、`EmailValidator`
- 避免通用：除非必要，不要使用 `Manager`、`Helper`、`Utility`

### 变量
- 名词或名词短语：`user`、`emailAddress`、`totalAmount`
- 描述性：`userList` 而不是 `list`，`activeUsers` 而不是 `users2`

### 常量
- 全大写加下划线：`MAX_RETRY_ATTEMPTS`、`DEFAULT_TIMEOUT`
- 包含单位：`CACHE_DURATION_MS`、`MAX_FILE_SIZE_MB`

### 布尔值
- 疑问形式：`isValid`、`hasPermission`、`canEdit`
- 肯定形式：`isEnabled` 而不是 `isDisabled`（优先使用肯定形式）

---

## 重构脚本

是否需要我创建一个重构脚本以应用这些更改？
这将：
1. 重命名所有建议项
2. 更新所有引用
3. 保持 git 历史记录
4. 生成迁移指南

---

## 最佳实践

✓ **要**：
- 使用全词而非缩写
- 具体且描述性
- 遵循语言规范
- 使用一致的模式
- 使布尔值明显
- 常量中包含单位

✗ **不要**：
- 使用单个字母（循环中除外：i、j、k）
- 使用含糊名称（data、info、temp、x）
- 混合命名规范
- 使用具有误导性的名称
- 过度缩写
- 现代代码中不要使用匈牙利标记法
```

## 命名决策树

```
是布尔值吗？
├─ 是 → 使用 is/has/can/should 前缀
└─ 否 → 是函数吗？
    ├─ 是 → 使用动词短语（动作）
    └─ 否 → 是类吗？
        ├─ 是 → 使用名词（PascalCase）
        └─ 否 → 是常量吗？
            ├─ 是 → 使用 UPPER_SNAKE_CASE
            └─ 否 → 使用描述性名词（camelCase/snake_case）
```

## 注意事项

- 优先清晰度而非简洁性
- 上下文很重要（循环计数器可以是 `i`、`j`）
- 广泛使用的缩写是可以接受的（`html`、`api`、`url`、`id`）
- 项目内的一致性比完美的命名更重要
- 随着理解的提高逐步重构名称
- 使用 IDE 重命名重构功能以安全地更新所有引用
