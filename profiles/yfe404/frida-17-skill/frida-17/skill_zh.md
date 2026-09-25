# Frida 17 脚本编写指南

本指南帮助您编写和修复与 Frida 17.0.0（2025 年 5 月发布）兼容的 Frida 脚本。

## Frida 17 中的重大变更

### 1. 静态模块方法 - 已移除

```javascript
// 旧版本 - 在 Frida 17 中不再工作
Module.findBaseAddress('libriver.so')
Module.getBaseAddress('libriver.so')
Module.findExportByName(null, 'open')
Module.findExportByName('libc.so', 'open')
Module.getExportByName(null, 'open')
Module.ensureInitialized('libc.so')
Module.enumerateExports('libc.so')
Module.enumerateSymbols('libc.so')

// 新版本 - 使用进程和实例方法替代
var lib = Process.findModuleByName('libriver.so');  // 返回 Module 或 null
var lib = Process.getModuleByName('libriver.so');   // 未找到时抛出异常
lib.base                                             // 模块基址
lib.findExportByName('open')                        // 返回地址或 null
lib.getExportByName('open')                         // 未找到时抛出异常
lib.enumerateExports()                              // 返回数组
lib.enumerateSymbols()                              // 返回数组
```

### 2. 静态内存方法 - 已移除

```javascript
// 旧版本 - 不再工作
Memory.readU32(ptr)
Memory.writeU32(ptr, value)

// 新版本 - 使用 NativePointer 实例方法
ptr.readU32()
ptr.writeU32(value)
```

### 3. 遗留枚举 API - 已移除

```javascript
// 旧版本 - 移除了回调风格
Process.enumerateModules({ onMatch: fn, onComplete: fn })
Process.enumerateModulesSync()

// 新版本 - 直接返回数组
Process.enumerateModules()
```

### 4. 保留函数名 - 请勿重写

以下为内置的 Frida 函数。使用这些名称定义自定义函数会导致：
`TypeError: cannot define variable 'hexdump'`

**保留名称：**
- `hexdump` - 自定义十六进制转储函数请使用 `dumpHex` 代替
- `ptr` - 指针构造器简写
- `NULL` - 空指针常量

```javascript
// 错误用法 - 与内置函数冲突
function hexdump(ptr, len) { ... }

// 正确用法 - 使用不同名称
function dumpHex(ptr, len) { ... }
```

## NativePointer 方法（Frida 17 中有效）

**转换：**
- `toInt32()` - 转换为有符号 32 位整数
- `toNumber()` - 转换为 JavaScript 数字
- `toString([radix])` - 转换为字符串

**不可用：**
- `toUInt32()` - 不存在，小于 2^31 的尺寸请使用 `toInt32()`

**内存读取：**
- `readU8()`, `readS8()`, `readU16()`, `readS16()`
- `readU32()`, `readS32()`, `readU64()`, `readS64()`
- `readByteArray(length)` - 返回 ArrayBuffer
- `readPointer()`, `readCString()`, `readUtf8String()`

**内存写入：**
- `writeU8(value)`, `writeS8(value)`, 等
- `writeByteArray(bytes)` - bytes 必须为 ArrayBuffer 或 JS 数组
- `writePointer(ptr)`, `writeUtf8String(str)`

**指针算术：**
- `add(rhs)`, `sub(rhs)`, `and(rhs)`, `or(rhs)`, `xor(rhs)`
- `shr(n)`, `shl(n)`, `not()`
- `isNull()`, `equals(rhs)`, `compare(rhs)`

## Java Bridge API（Frida 17 中未变更）

```javascript
Java.perform(function() {
    var MyClass = Java.use('com.example.MyClass');

    // 带重载的 Hook
    MyClass.myMethod.overload('int', 'java.lang.String').implementation = function(a, b) {
        console.log('Called with: ' + a + ', ' + b);
        // 调用原始函数
        return this.myMethod.overload('int', 'java.lang.String').call(this, a, b);
    };

    // Hook 所有重载
    MyClass.myMethod.overloads.forEach(function(overload) {
        overload.implementation = function() {
            return overload.apply(this, arguments);
        };
    });
});
```

**Java byte[] 处理：**
Java byte 数组不能直接传递给 `Memory.alloc().writeByteArray()`。
手动转换：

```javascript
// 错误用法 - 抛出 "expected a buffer-like object"
var hex = dumpHex(Memory.alloc(javaByteArray.length).writeByteArray(javaByteArray), len);

// 正确用法 - 迭代转换
var hex = "";
for (var i = 0; i < javaByteArray.length; i++) {
    hex += ("0" + (javaByteArray[i] & 0xff).toString(16)).slice(-2);
}
```

## Frida 17 常用模式

### 等待库加载

```javascript
function waitForLibrary(libName, callback) {
    var lib = Process.findModuleByName(libName);
    if (lib) {
        callback(lib.base);
        return;
    }
    var pollInterval = setInterval(function() {
        var lib = Process.findModuleByName(libName);
        if (lib) {
            clearInterval(pollInterval);
            callback(lib.base);
        }
    }, 500);
}
```

### Hook libc 函数

```javascript
var libc = Process.findModuleByName('libc.so');
var open = libc ? libc.findExportByName('open') : null;
if (open) {
    Interceptor.attach(open, {
        onEnter: function(args) {
            console.log('open(' + args[0].readCString() + ')');
        }
    });
}
```

### 自定义十六进制转储函数

```javascript
function dumpHex(ptr, len) {
    if (!ptr || ptr.isNull()) return 'null';
    try {
        var bytes = ptr.readByteArray(len);
        if (!bytes) return 'null';
        var arr = new Uint8Array(bytes);
        var hex = '';
        for (var i = 0; i < arr.length; i++) {
            hex += ('0' + arr[i].toString(16)).slice(-2);
        }
        return hex;
    } catch (e) {
        return 'error: ' + e;
    }
}
```

## Frida 17 兼容性检查清单

在审查 Frida 脚本时，请检查：

1. [ ] `Module.findBaseAddress()` -> `Process.findModuleByName().base`
2. [ ] `Module.getBaseAddress()` -> `Process.getModuleByName().base`
3. [ ] `Module.findExportByName(null, name)` -> `Process.findModuleByName('libc.so').findExportByName(name)`
4. [ ] `Module.findExportByName(lib, name)` -> `Process.findModuleByName(lib).findExportByName(name)`
5. [ ] `Module.enumerateExports(lib)` -> `Process.getModuleByName(lib).enumerateExports()`
6. [ ] `Module.enumerateSymbols(lib)` -> `Process.getModuleByName(lib).enumerateSymbols()`
7. [ ] `Memory.readU32(ptr)` -> `ptr.readU32()`
8. [ ] `toUInt32()` -> `toInt32()` (toUInt32 从未存在)
9. [ ] `function hexdump()` -> `function dumpHex()` (名称冲突)
10. [ ] Java byte[] 与 `writeByteArray()` -> 手动十六进制转换

## 参考

- [Frida 17.0.0 发布说明](https://frida.re/news/2025/05/17/frida-17-0-0-released/)
- [Frida JavaScript API](https://frida.re/docs/javascript-api/)
- [Frida Android 示例](https://frida.re/docs/examples/android/)
