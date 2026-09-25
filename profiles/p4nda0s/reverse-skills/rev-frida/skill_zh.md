# rev-frida - Frida 脚本生成器

为动态分析、钩子拦截和运行时检查生成 Frida 仪器化脚本。

## 概述

使用 Frida 进行：
- 本地导出钩子
- Java 或 ObjC 方法钩子
- 运行时跟踪
- 参数或返回值捕获
- 内存转储
- 加载器感知的本地仪器化

## 重要提示：现代 Frida CLI

现代 Frida CLI 不使用 `--no-pause`。启动的进程在脚本加载后继续执行。

```bash
# 启动并钩子
frida -U -f com.example.app -l hook.js

# 附加到正在运行的进程
frida -U com.example.app -l hook.js

# 通过 PID 附加
frida -U -p 1234 -l hook.js
```

## 现代 API 参考

### 模块和符号查找

```javascript
const mod = Process.getModuleByName("libssl.so");

mod.name;
mod.base;
mod.size;
mod.path;

const ptr = mod.getExportByName("SSL_read");

Process.enumerateModules();
mod.enumerateExports();
mod.enumerateImports();

const addr = Module.getExportByName(null, "open");
```

### 拦截器

```javascript
Interceptor.attach(ptr, {
    onEnter(args) {
        console.log("arg0:", args[0].toInt32());
        console.log("arg1 str:", args[1].readUtf8String());
    },
    onLeave(retval) {
        console.log("ret:", retval.toInt32());
    }
});

Interceptor.replace(ptr, new NativeCallback(function (a0, a1) {
    console.log("replaced");
    return 0;
}, "int", ["pointer", "int"]));
```

### NativeFunction & NativeCallback

```javascript
const open = new NativeFunction(
    Module.getExportByName(null, "open"),
    "int",
    ["pointer", "int"]
);

const fd = open(Memory.allocUtf8String("/etc/hosts"), 0);

const cb = new NativeCallback(function (arg) {
    console.log("called with:", arg);
    return 0;
}, "int", ["int"]);
```

### 内存操作

```javascript
ptr(addr).readByteArray(size);
ptr(addr).readUtf8String();
ptr(addr).readU32();
ptr(addr).readPointer();

ptr(addr).writeByteArray(bytes);
ptr(addr).writeUtf8String("hello");
ptr(addr).writeU32(0x41414141);

const buf = Memory.alloc(256);
const str = Memory.allocUtf8String("hello");

Memory.scan(mod.base, mod.size, "48 89 5C 24 ?? 48 89 6C", {
    onMatch(address, size) {
        console.log("found at:", address);
    },
    onComplete() {}
});
```

### ObjC

```javascript
if (ObjC.available) {
    const hook = ObjC.classes.ClassName["- methodName:"];
    Interceptor.attach(hook.implementation, {
        onEnter(args) {
            const selfObj = new ObjC.Object(args[0]);
            const param = new ObjC.Object(args[2]);
            console.log(selfObj.toString());
            console.log(param.toString());
        }
    });
}
```

### Java

```javascript
if (Java.available) {
    Java.perform(function () {
        const Activity = Java.use("android.app.Activity");
        Activity.onCreate.implementation = function (bundle) {
            console.log("onCreate called");
            return this.onCreate(bundle);
        };
    });
}
```

## 脚本生成指南

生成 Frida 脚本时：

1. 始终使用现代 API，如 `Process.getModuleByName()` 和 `mod.getExportByName()`。
2. 不要使用 `--no-pause`。
3. 优先使用加载事件驱动的本地钩子，而不是轮询。
4. 以可读形式打印指针和缓冲区。
5. 将有风险的钩子包装在 `try/catch` 中。
6. 使用 `hexdump()` 进行二进制检查。

### 处理本地模块加载时机

不要假设目标 `.so` 文件已经加载。

首选顺序：
1. 钩子 `android_dlopen_ext` 或 `dlopen`，并在目标库加载时安装钩子。
2. 使用立即的 `Process.findModuleByName()` 检查已加载的模块。
3. 仅作为后备方案使用轮询。

默认使用此辅助函数：

```javascript
function hookModuleLoad(moduleName, callback) {
    const dlopen = Module.findGlobalExportByName("android_dlopen_ext")
        || Module.findGlobalExportByName("dlopen");

    if (!dlopen) {
        throw new Error("dlopen/android_dlopen_ext not found");
    }

    const hooked = new Set();

    Interceptor.attach(dlopen, {
        onEnter(args) {
            this.path = args[0].isNull() ? null : args[0].readCString();
            this.shouldHook = this.path && this.path.indexOf(moduleName) !== -1;
        },
        onLeave(retval) {
            if (!this.shouldHook || retval.isNull()) {
                return;
            }

            const mod = Process.findModuleByName(moduleName);
            if (!mod) {
                return;
            }

            const key = mod.base.toString();
            if (hooked.has(key)) {
                return;
            }
            hooked.add(key);

            callback(mod);
        }
    });
}
```

使用方法：

```javascript
hookModuleLoad("libtarget.so", function (mod) {
    const target = mod.getExportByName("target_export");
    Interceptor.attach(target, {
        onEnter(args) {
            console.log("target_export called");
        }
    });
});
```

如果目标可能已经加载，将立即检查与加载钩子结合：

```javascript
function hookNowOrOnLoad(moduleName, callback) {
    const mod = Process.findModuleByName(moduleName);
    if (mod) {
        callback(mod);
        return;
    }
    hookModuleLoad(moduleName, callback);
}
```

仅作为后备方案使用轮询：

```javascript
function hookWhenReady(moduleName, exportName, callbacks) {
    const mod = Process.findModuleByName(moduleName);
    if (mod) {
        Interceptor.attach(mod.getExportByName(exportName), callbacks);
        return;
    }

    const timer = setInterval(function () {
        const loaded = Process.findModuleByName(moduleName);
        if (!loaded) {
            return;
        }
        clearInterval(timer);
        Interceptor.attach(loaded.getExportByName(exportName), callbacks);
    }, 100);
}
```

注意：
- 在 Android 上，优先使用 `android_dlopen_ext` 而不是 `dlopen`。
- 通过模块基址去重，而不仅仅是通过路径。
- `dlopen/android_dlopen_ext` 的 `onLeave` 通常是构造函数运行后安装钩子的正确时间。
- 如果 Java 驱动本地加载，也考虑 `System.loadLibrary`、`Runtime.loadLibrary0`、`dlsym` 或 `RegisterNatives`。

### 不要盲目钩子 init 系列函数

不要盲目告诉用户钩子 `.init`、`.init_array`、构造函数或 `JNI_OnLoad`。

这些是脆弱点：
- 许多库在那里进行一次性设置
- 坏的钩子可以在真实目标逻辑运行之前崩溃进程
- 早期的钩子可以改变时间并隐藏用户想要研究的行為
- 构造函数代码通常分散到许多不相关的辅助函数中

在建议 init 阶段钩子之前：
1. 确定为什么需要早期钩子
2. 确定确切的模块和确切的初始化例程
3. 确认目标符号或行为是否只在正常导出之前存在
4. 如果可能，优先使用较晚的稳定钩子以获得相同的可见性

首选顺序：
1. 模块加载后钩子一个稳定的导出函数
2. 钩子 `RegisterNatives`、`dlsym` 或第一个真正的业务函数
3. 仅在本地注册或反调试设置在那里时钩子 `JNI_OnLoad`
4. 仅在确凿证据表明关键逻辑在那里时钩子构造函数或 `.init_array`

如果建议早期 init 钩子，说明：
- 为什么正常导出钩子不足
- 应该钩子的确切函数或地址
- 预期失败模式
- 如何验证钩子没有破坏初始化

坏建议：

```javascript
// 不要没有理由就建议这个
Interceptor.attach(Module.findBaseAddress("libtarget.so").add(0x1234), ...);
```

更好的建议：
- 等待模块加载
- 通过符号、xrefs、字符串或跟踪证据确认构造函数目标
- 仅在识别出确切的初始化函数后附加
- 在使用 init 阶段钩子之前向用户解释风险

### 优先构造函数调度器而不是盲目 init 钩子

如果构造函数链中怀疑有反调试逻辑，优先观察或钩子调度器而不是盲目附加到原始 `.init_array` 条目。

有用的较高层次目标包括：
- `call_constructors`
- `call_array`
- 链接器侧构造函数遍历器
- 应用侧遍历构造函数表的包装函数

为什么这是更安全的：
- 一个钩子可以揭示完整的构造函数序列
- 你可以看到哪个构造函数在终止或反调试设置之前立即运行
- 减少盲目修补不相关的初始化代码
- 允许你首先记录构造函数目标，然后仅修补冒犯性的一个

推荐工作流程：
1. 钩子模块加载
2. 确定进程是否在构造函数执行期间终止
3. 如果是，当可用时钩子 `call_constructors` 或 `call_array`
4. 记录每个构造函数目标在调度时
5. 确定执行反调试检查的确切构造函数
6. 钩子或修补该构造函数，或修补其内部的特定反调试分支

仅当：
- 目标平台或链接器构建暴露了这些函数
- 符号、跟踪或反汇编表明它们实际上在使用
- 用户需要可见性到构造时的反调试行为时，建议 `call_constructors` 或 `call_array`

警告这些约束：
- 这些函数是加载器或链接器内部函数，名称可能因 Android 版本、供应商构建或平台而异
- 它们可能不会被导出，可能需要符号恢复或基于偏移量的附加
- 过早钩子会影响每个库加载，因此要小心范围日志记录
- 首先用于发现，而不是作为默认的永久绕过

好的指导：
- “进程在本地库初始化期间死亡。首先钩子构造函数调度器，如 `call_constructors` 或 `call_array`（如果存在），记录构造函数目标，然后移动到确切的冒犯性构造函数。”

坏建议：
- “钩子每个 `.init_array` 条目并修补，直到它停止崩溃。”

### 指针和缓冲区日志记录

```javascript
console.log(args[0]);
console.log(args[0].toString());
console.log(hexdump(args[0], {
    offset: 0,
    length: 64,
    header: true,
    ansi: false
}));
```
