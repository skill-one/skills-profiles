# rev-idapython - IDAPython / IDALib 脚本参考

用于 IDA 交互式使用的 IDAPython 脚本片段和用于 IDALib 无头分析的 IDAPython 脚本。在生成 IDAPython 代码时，将其用作参考。

- **IDAPython**：在 IDA GUI 内运行的脚本（脚本命令、插件或 IDC 控制台）
- **IDALib**：在 IDA 9.0 中引入的无头模式——无需打开 IDA GUI 即可运行分析脚本

---

## 常见 API

### 注册操作

```python
idc.get_reg_value('rax')
idaapi.set_reg_val("rax", 1234)
```

### 调试内存操作

```python
idc.read_dbg_byte(addr)
idc.read_dbg_memory(addr, size)
idc.read_dbg_dword(addr)
idc.read_dbg_qword(addr)
idc.patch_dbg_byte(addr, val)
idc.add_bpt(0x409437)          # 添加断点
idaapi.get_imagebase()         # 获取图像基地址
```

### 本地内存操作（修改 IDB 数据库）

```python
idc.get_qword(addr)
idc.patch_qword(addr, val)
idc.patch_dword(addr, val)
idc.patch_word(addr, val)
idc.patch_byte(addr, val)
idc.get_db_byte(addr)
idc.get_bytes(addr, size)
idaapi.get_dword(addr)
idc.get_strlit_contents          # 读取字符串字面量
```

### 反汇编

```python
GetDisasm(addr)                  # 获取反汇编文本
idc.next_head(ea)                # 获取下一条指令地址
idc.create_insn(addr)            # c, 生成代码
ida_bytes.create_strlit          # 创建字符串，与 'A' 键相同
ida_funcs.add_func(addr)         # p, 创建函数
idc.del_items(addr)              # U, 取消定义
```

### 地址转换

```python
idc.get_name_ea(0, '_sub_6051')  # 通过函数名获取地址
```

### 函数操作

```python
ida_funcs.get_func(ea)           # 获取函数描述符

# 枚举所有函数
for func in idautils.Functions():
    print("0x%x, %s" % (func, idc.get_func_name(func)))
```

---

## 代码片段

### 字节模式搜索

```python
import ida_bytes
import ida_idaapi
import ida_funcs
import idc

# find_bytes_list("90 90 90 90 90")
# find_bytes_list("55 ??")
# 返回匹配地址列表
def find_bytes_list(bytes_pattern):
    ea = -1
    result = []
    while True:
        ea = idc.find_bytes(bytes_pattern, ea + 1)
        if ea == ida_idaapi.BADADDR:
            break
        result.append(ea)
    return result
```

### Appcall - 调用调试目标函数

```python
# 测试 check_passwd(char *passwd) -> int
passwd = ida_idd.Appcall.byref("MyFirstGuess")
res = ida_idd.Appcall.check_passwd(passwd)
if res.value == 0:
  print("Good passwd !")
else:
  print("Bad passwd...")
```

```python
# 显式创建作为 byref 对象的缓冲区
s_in = Appcall.byref("SomeEncryptedBuffer")
# 缓冲区始终作为 byref 返回
s_out = Appcall.buffer(" ", SizeOfBuffer)
# 调用调试目标
Appcall.decrypt_buffer(s_in, s_out, SizeOfBuffer)
# 打印结果
print "decrypted=", s_out.value
```

```python
loadlib = Appcall.proto("kernel32_LoadLibraryA", "int __stdcall loadlib(const char *fn);")
hmod = loadlib("dll_to_inject.dll")

getlasterror = Appcall.proto("kernel32_GetLastError", "DWORD __stdcall GetLastError();")
print "lasterror=", getlasterror()

getcmdline = Appcall.proto("kernel32_GetCommandLineA", "const char *__stdcall getcmdline();")
print "command line:", getcmdline()
```

### 跨引用

```python
for ref in idautils.XrefsTo(ea):
    print(hex(ref.frm))

# 简写
[ref.frm for ref in idautils.XrefsTo(start_ea)]
```

### 基本块遍历

```python
fn = 0x4800
f_blocks = idaapi.FlowChart(idaapi.get_func(fn), flags=idaapi.FC_PREDS)
for block in f_blocks:
    print(hex(block.start_ea))
```

```python
# 后继块
for succ in block.succs():
    print hex(succ.start_ea)

# 前驱块
for pred in block.preds():
    print hex(pred.start_ea)
```

### 调试内存读写

```python
def patch_dbg_mem(addr, data):
    for i in range(len(data)):
        idc.patch_dbg_byte(addr + i, data[i])

def read_dbg_mem(addr, size):
    dd = []
    for i in range(size):
        dd.append(idc.read_dbg_byte(addr + i))
    return bytes(dd)
```

### 读取 std::string (64 位)

```python
def dbg_read_cppstr_64(objectAddr):
    strPtr = idc.read_dbg_qword(objectAddr)
    result = ''
    i = 0
    while True:
        onebyte = idc.read_dbg_byte(strPtr + i)
        if onebyte == 0:
            break
        else:
            result += chr(onebyte)
            i += 1
    return result
```

### 读取 C 字符串 (64 位)

```python
def dbg_read_cstr_64(objectAddr):
    strPtr = objectAddr
    result = ''
    i = 0
    while True:
        onebyte = idc.read_dbg_byte(strPtr + i)
        if onebyte == 0:
            break
        else:
            result += chr(onebyte)
            i += 1
    return result
```

### 解析 GNU C++ std::map

```python
import idautils
import idaapi
import idc

def parse_gnu_map_header(address):
    root = idc.read_dbg_qword(address + 0x10)
    return root

def parse_gnu_map_node(address):
    left  = idc.read_dbg_qword(address + 0x10)
    right = idc.read_dbg_qword(address + 0x18)
    data  = address + 0x20
    return left, right, data

def parse_gnu_map_travel(address):
    # address <- std::map 结构地址
    result = []
    worklist = [parse_gnu_map_header(address)]
    while len(worklist) > 0:
        addr = worklist.pop()
        (left, right, data) = parse_gnu_map_node(addr)
        if left > 0: worklist.append(left)
        if right > 0: worklist.append(right);
        result.append(data)
    return result

# 示例
elements = parse_gnu_map_travel(0x0000557518073EB0)
for elem in elements:
    print(hex(elem))
```

### 读取 XMM 寄存器 (调试)

```python
def read_xmm_reg(name):
    rv = idaapi.regval_t()
    idaapi.get_reg_val(name, rv)
    return (struct.unpack('Q', rv.bytes())[0])
```

### 单步执行并等待调试事件

```python
while ida_dbg.step_over():
    wait_for_next_event(WFNE_ANY, -1)
    rip = idc.get_reg_value("rip")
    # .....
```

### 遍历函数中的指令

```python
for ins in idautils.FuncItems(0x401000):
    print(hex(ins))
```

### 获取函数被调用者 (基于指令)

```python
def ida_get_callees(func_addr: int) -> list:
    callees = []
    for head in idautils.Heads(func_addr, idaapi.get_func(func_addr).end_ea):
        if idaapi.is_call_insn(head):
            callee_ea = idc.get_operand_value(head, 0)
            callees.append(callee_ea)
    return callees
```

### 双精度/复数内存操作

```python
def float_to_double_bytearray(value):
    double_value = ctypes.c_double(value)
    byte_array = bytearray(ctypes.string_at(ctypes.byref(double_value), ctypes.sizeof(double_value)))
    return byte_array

def set_pos(x, y): # complex<double, double>
    rbp = idc.get_reg_value("rbp")
    complex_base = rbp - 0x260

    patch_dbg_mem(complex_base, float_to_double_bytearray(x))
    patch_dbg_mem(complex_base + 8, float_to_double_bytearray(y))

set_pos(5.0, 6.0)
```

---

## 导入表

### 枚举导入表

```python
import ida_nalt

nimps = ida_nalt.get_import_module_qty()

print("Found %d import(s)..." % nimps)

for i in range(nimps):
    name = ida_nalt.get_import_module_name(i)
    if not name:
        print("Failed to get import module name for #%d" % i)
        name = "<unnamed>"

    print("Walking imports for module %s" % name)
    def imp_cb(ea, name, ordinal):
        if not name:
            print("%08x: ordinal #%d" % (ea, ordinal))
        else:
            print("%08x: %s (ordinal #%d)" % (ea, name, ordinal))
        return True
    ida_nalt.enum_import_names(i, imp_cb)

print("All done...")
```

### 检查地址是否为导入函数

```python
def ida_is_import_function(addr: int) -> bool:
    is_find = False

    nimps = ida_nalt.get_import_module_qty()

    for i in range(nimps):
        def imp_cb(ea, name, ordinal):
            nonlocal is_find
            if ea == addr:
                is_find = True
                return False
            return True
        ida_nalt.enum_import_names(i, imp_cb)

    return is_find
```

### 枚举导入地址

```python
def ida_enum_import_addr() -> List[int]:
    import_addrs = []
    nimps = ida_nalt.get_import_module_qty()
    for i in range(nimps):
        def imp_cb(ea, name, ordinal):
            nonlocal import_addrs
            import_addrs.append(ea)
            return True
        ida_nalt.enum_import_names(i, imp_cb)
    return import_addrs
```

---

## 类型信息

### 结构成员遍历

```python
def extract_struct_members(type_name):
    fields = []
    tif = ida_typeinf.tinfo_t()
    if tif.get_named_type(None, type_name):
        offset = 0
        for iter in tif.iter_struct(): # udm
            fsize = iter.type.get_size()
            fields.append({
                "offset": iter.offset // 8, # 位偏移
                "size": fsize,
                "type": iter.type._print()
            })
            offset += fsize
    else:
        print(f"Unable to get {type_name} type info.")
    return fields

extract_struct_members("sqlite3_vfs")
```

### 枚举所有类型

```python
til = ida_typeinf.get_idati()
for type_name in til.get_type_names():
    print(type_name)
```

### 列出所有结构类型

```python
def list_struct_types():
    types = []
    til = ida_typeinf.get_idati()
    for type_name in til.get_type_names():
        tif = ida_typeinf.tinfo_t()
        if tif.get_named_type(None, type_name):
            if tif.is_struct():
                types.append(type_name)
    return types
```

---

## Hex-Rays 反编译器 API

### 反编译函数

```python
# verified: IDA 9.0
dec = ida_hexrays.decompile(func_addr)
# dec 是一个对象，str(dec) 转换为文本
print(str(dec))
```

### 在不同成熟级别打印微代码

```python
def print_microcode(func_ea):
    maturity = ida_hexrays.MMAT_GLBOPT3
    #   maturity:
    #   MMAT_ZERO,         ///< 微代码不存在
    #   MMAT_GENERATED,    ///< 生成的微代码
    #   MMAT_PREOPTIMIZED, ///< 预优化阶段完成
    #   MMAT_LOCOPT,       ///< 每个基本块的局部优化完成。
    #                      ///< 控制流图也已准备好。
    #   MMAT_CALLS,        ///< 检测到调用参数
    #   MMAT_GLBOPT1,      ///< 执行了全局优化的第一遍
    #   MMAT_GLBOPT2,      ///< 大部分全局优化阶段完成
    #   MMAT_GLBOPT3,      ///< 完成所有全局优化。微代码现在已固定。
    #   MMAT_LVARS,        ///< 分配了局部变量
    hf = ida_hexrays.hexrays_failure_t()
    pfn = idaapi.get_func(func_ea)
    rng = ida_hexrays.mba_ranges_t(pfn)
    mba = ida_hexrays.gen_microcode(rng, hf, None,
                ida_hexrays.DECOMP_WARNINGS, maturity)
    vp = ida_hexrays.vd_printer_t()
    mba._print(vp)
print_microcode(0x1229)
```

### 自定义指令到用户定义调用

```python
class udc_exit_t(ida_hexrays.udc_filter_t):
    def __init__(self, code, name):
        ida_hexrays.udc_filter_t.__init__(self)
        if not self.init("int __usercall %s@<R0>(int status@<R1>);" % name):
            raise Exception("Couldn't initialize udc_exit_t instance")
        self.code = code
        self.installed = False

    def match(self, cdg):
        return cdg.insn.itype == ida_allins.ARM_svc and cdg.insn.Op1.value == self.code

    def install(self):
        ida_hexrays.install_microcode_filter(self, True);
        self.installed = True

    def uninstall(self):
        ida_hexrays.install_microcode_filter(self, False);
        self.installed = False

    def toggle_install(self):
        if self.installed:
            self.uninstall()
        else:
            self.install()

udc_exit = udc_exit_t(0x900001, "svc_exit")
udc_exit.toggle_install()
```

### Hexrays_Hooks

```python
class MicrocodeCallback(ida_hexrays.Hexrays_Hooks):
    def __init__(self, *args):
        super().__init__(*args)
    def microcode(self, mba: ida_hexrays.mba_t) -> "int":
        print("microcode generated.")
        return 0
r = MicrocodeCallback()
r.hook()
```

---

## 混淆辅助工具

### OLLVM - 在真实块上设置断点

在所有真实块入口地址上设置断点。真实块通过查找 OLLVM 分发器合并点的前驱来识别。

注意：通过跨引用识别真实块是一种启发式方法，可能不完全准确。使用 IDA 断点组进行批量管理。

```python
fn = 0x401F60
ollvm_tail = 0x405D4B # OLLVM 真实块合并点
f_blocks = idaapi.FlowChart(idaapi.get_func(fn), flags=idaapi.FC_PREDS)
for block in f_blocks:
    for succ in block.succs():
        if succ.start_ea == ollvm_tail:
            print(hex(block.start_ea))
            idc.add_bpt(block.start_ea)
```

### 批量添加断点

```python
def brkall(l):
    for addr in l:
        idc.add_bpt(addr)
```

---

## 固件辅助工具

### 搜索 x86 函数序言并创建函数

```python
# verified: IDA 9.0
def make_x86_func():
    func_headers = find_bytes_list("55 8B")
    for h in func_headers:
        idc.del_items(h)
        idc.create_insn(h)
        ida_funcs.add_func(h)
```

---

## 基本块工具

### 获取基本块大小

```python
# verified: IDA 9.0
def get_bb_size(bbaddr):
    fn = bbaddr
    f_blocks = idaapi.FlowChart(idaapi.get_func(fn), flags=idaapi.FC_PREDS)
    for block in f_blocks:
        if block.start_ea == bbaddr:
            return block.end_ea - block.start_ea
    raise Exception("Not found")
```

### 通过地址获取基本块

```python
def ida_get_bb(ea):
    f_blocks = idaapi.FlowChart(idaapi.get_func(ea), flags=idaapi.FC_PREDS)
    for block in f_blocks:
        if block.start_ea <= ea and ea < block.end_ea:
            return block
    return None
```

---

## 指令工具

### 通过关键字搜索下一条指令

```python
# verified: IDA 9.0
def search_next_insn(addr, insnkey, max_search=0x100):
    cnt = 0
    while cnt < max_search:
        addr = idc.next_head(addr)
        dis = GetDisasm(addr)
        if insnkey in dis:
            return addr
        cnt += 1
    return None

# 示例
# search_next_insn(addr, 'movdqa')
```

### 取消定义一个范围 (U 键等效)

```python
# verified: IDA 9.0
def undefine_range(start, end):
    for i in range(start, end):
        idc.del_items(i)
# 示例
# undefine_range(func_start, func_end)
```

### 搜索反汇编文本

```python
# verified: IDA 9.0
def search_text_all(text):
    import idaapi, idc
    start_ea = 0
    result = []
    while True:
        start_ea = idaapi.find_text(ustr=text, x=0, y=0,
            sflag=idaapi.SEARCH_DOWN, start_ea=start_ea)
        if start_ea == idc.BADADDR:
            break
        result.append(start_ea)
        start_ea = idc.next_head(start_ea)
    return result
# 示例
for x in search_text_all('movdqa'):
    print(GetDisasm(x))
```

---

## NOP 函数

```python
import idaapi
import idautils
import idc

def nop_func(addr_func, arch='arm'):
    func = ida_funcs.get_func(addr_func)
    if not func:
        print("Function not found!")
        return

    start = func.start_ea
    end = func.end_ea

    print(f"Nopping function at: 0x{start:x} - 0x{end:x}")

    if arch == 'x86':
        nop_bytes = [0x90]  # x86 NOP
    elif arch == 'arm':
        nop_bytes = [0x1F, 0x20, 0x03, 0xD5]  # ARM NOP
    else:
        print(f"Unsupported architecture: {arch}")
        return

    ea = start
    while ea < end:
        insn = ida_ua.insn_t()
        length = ida_ua.decode_insn(insn, ea)
        if length == 0:
            print(f"Failed to decode instruction at: 0x{ea:x}")
            break

        nop_len = len(nop_bytes)
        for i in range(0, length, nop_len):
            for j in range(nop_len):
                if i + j < length:
                    idc.patch_byte(ea + i + j, nop_bytes[j])

    print("Nopping complete.")

# 示例
nop_func(0x401000, 'arm')
```

---

## IDALib (无头 IDA, IDA 9.0+)

IDALib 允许在不打开 IDA GUI 的情况下运行 IDAPython 分析脚本。

### 安装

```bash
cd idalib/python
pip install .
python py-activate-idalib.py
```

### 基本用法

```python
import idapro # 必须是第一个导入
import idautils
import idc

# 打开 idb/binary 文件
ida.open_database("samples/patch.so", True)

# 枚举函数
for func in idautils.Functions():
    func_name = idc.get_func_name(func)
    print("Function Name: {}, Address: {}".format(func_name, hex(func)))

# 关闭并保存 idb
ida.close_database(save=True)
```

### 批量反编译为 JSON

```bash
Usage: decompile.py <input_file_elf> <output_file_json>
```

decompile.py:

```python
import idapro

import ida_hexrays
import idautils
import idc

import os
import sys
import json

def _decompile_internal():
    result = []
    for func in idautils.Functions():
        func_name = idc.get_func_name(func)
        print("Function Name: {}, Address: {}".format(func_name, hex(func)))
        dec_obj = ida_hexrays.decompile(func)
        if dec_obj is None:
            continue
        dec_str = str(dec_obj)
        result.append({
            'name': func_name,
            'address': hex(func),
            'decompiled': dec_str
        })
    return result

def decomple_export(file, out_file):
    ida.open_database(file, True)
    r = _decompile_internal()
    ida.close_database(save=False)
    open(out_file, "w").write(json.dumps(r, indent=4))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <input_file_elf> <output_file_json>".format(sys.argv[0]))
        sys.exit(1)
    decomple_export(sys.argv[1], sys.argv[2])
```

### 多进程批量反编译

```python
import os
import time
from multiprocessing import Pool

args = {
    "NUM_WORKERS": 8,
    "INPUT_DIR": "/Users/ctf/idek2024/baby2/baby",
    "OUTPUT_DIR": "/Users/ctf/idek2024/baby2/decompiled",
    "NUM_MAX_RETRY": 3
}

def decomple_one(file, out_file):
    retry = 0
    while True:
        os.system("python3 decompile.py {} {}".format(file, out_file))
        if os.path.exists(out_file):
            break
        retry += 1
        if retry >= args["NUM_MAX_RETRY"]:
            return "Failed to decompile {}".format(file)
        time.sleep(1)
    return None

if __name__ == "__main__":
    if not os.path.exists(args["OUTPUT_DIR"]):
        os.makedirs(args["OUTPUT_DIR"])
    files = os.listdir(args["INPUT_DIR"])

    files = [os.path.join(args["INPUT_DIR"], f) for f in files]
    out_files = [os.path.join(args["OUTPUT_DIR"], os.path.basename(f) + ".json" ) for f in files]
    with Pool(args["NUM_WORKERS"]) as p:
        r = p.starmap(decomple_one, zip(files, out_files))
        for i in r:
            if i is not None:
                print(i)
```
