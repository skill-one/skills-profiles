# PowerShell Windows 模式

> Windows PowerShell 的关键模式和常见陷阱。

---

## 1. 操作符语法规则

### 关键：必须使用括号

| ❌ 错误 | ✅ 正确 |
|----------|-----------|
| `if (Test-Path "a" -or Test-Path "b")` | `if ((Test-Path "a") -or (Test-Path "b"))` |
| `if (Get-Item $x -and $y -eq 5)` | `if ((Get-Item $x) -and ($y -eq 5))` |

**规则：** 使用逻辑运算符时，每个 cmdlet 调用都必须使用括号括起来。

---

## 2. Unicode/Emoji 限制

### 关键：脚本中禁止使用 Unicode

| 目的 | ❌ 不要使用 | ✅ 使用 |
|---------|-------------|--------|
| 成功 | ✅ ✓ | [OK] [+] |
| 错误 | ❌ ✗ 🔴 | [!] [X] |
| 警告 | ⚠️ 🟡 | [*] [WARN] |
| 信息 | ℹ️ 🔵 | [i] [INFO] |
| 进度 | ⏳ | [...] |

**规则：** PowerShell 脚本中只能使用 ASCII 字符。

---

## 3. 空值检查模式

### 访问前始终检查

| ❌ 错误 | ✅ 正确 |
|----------|-----------|
| `$array.Count -gt 0` | `$array -and $array.Count -gt 0` |
| `$text.Length` | `if ($text) { $text.Length }` |

---

## 4. 字符串插值

### 复杂表达式

| ❌ 错误 | ✅ 正确 |
|----------|-----------|
| `"Value: $($obj.prop.sub)"` | 首先存储在变量中 |

**模式：**
```
$value = $obj.prop.sub
Write-Output "Value: $value"
```

---

## 5. 错误处理

### ErrorActionPreference

| 值 | 使用 |
|-------|-----|
| Stop | 开发环境（快速失败） |
| Continue | 生产脚本 |
| SilentlyContinue | 预期出现错误时 |

### Try/Catch 模式

- try 块内不要返回
- 使用 finally 进行清理
- try/catch 后返回

---

## 6. 文件路径

### Windows 路径规则

| 模式 | 使用 |
|---------|-----|
| 字面路径 | `C:\Users\User\file.txt` |
| 变量路径 | `Join-Path $env:USERPROFILE "file.txt"` |
| 相对路径 | `Join-Path $ScriptDir "data"` |

**规则：** 使用 Join-Path 以确保跨平台安全性。

---

## 7. 数组操作

### 正确模式

| 操作 | 语法 |
|-----------|--------|
| 空数组 | `$array = @()` |
| 添加项 | `$array += $item` |
| ArrayList 添加 | `$list.Add($item) | Out-Null` |

---

## 8. JSON 操作

### 关键：深度参数

| ❌ 错误 | ✅ 正确 |
|----------|-----------|
| `ConvertTo-Json` | `ConvertTo-Json -Depth 10` |

**规则：** 对于嵌套对象，始终指定 `-Depth`。

### 文件操作

| 操作 | 模式 |
|-----------|---------|
| 读取 | `Get-Content "file.json" -Raw | ConvertFrom-Json` |
| 写入 | `$data | ConvertTo-Json -Depth 10 | Out-File "file.json" -Encoding UTF8` |

---

## 9. 常见错误

| 错误信息 | 原因 | 修复 |
|---------------|-------|-----|
| "parameter 'or'" | 缺少括号 | 将 cmdlet 用 () 括起来 |
| "Unexpected token" | Unicode 字符 | 仅使用 ASCII 字符 |
| "Cannot find property" | 空对象 | 首先检查空值 |
| "Cannot convert" | 类型不匹配 | 使用 .ToString() |

---

## 10. 脚本模板

```powershell
# 严格模式
Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# 路径
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 主逻辑
try {
    # 逻辑代码
    Write-Output "[OK] 完成"
    exit 0
}
catch {
    Write-Warning "错误: $_"
    exit 1
}
```

---

> **记住：** PowerShell 有独特的语法规则。括号、仅使用 ASCII 字符和空值检查是不可协商的。

## 使用场景
此技能适用于执行概述中描述的工作流或操作。

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
