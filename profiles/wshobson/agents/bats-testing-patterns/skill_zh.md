# Bats 测试模式

使用 Bats（Bash 自动化测试系统）编写全面单元测试的全面指南，包括测试模式、测试环境（fixtures）和生产级 shell 测试的最佳实践。

## 何时使用此技能

- 编写 shell 脚本的单元测试
- 为脚本实施测试驱动开发（TDD）
- 在 CI/CD 管道中设置自动化测试
- 测试边界情况和错误条件
- 验证不同 shell 环境下的行为
- 为脚本构建可维护的测试套件
- 为复杂测试场景创建测试环境（fixtures）
- 测试多种 shell 语法（bash、sh、dash）

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 测试错误条件

```bash
#!/usr/bin/env bats

@test "函数因缺少文件而失败" {
    run my_function "/nonexistent/file.txt"
    [ "$status" -ne 0 ]
    [[ "$output" == *"not found"* ]]
}

@test "函数因无效输入而失败" {
    run my_function ""
    [ "$status" -ne 0 ]
}

@test "函数因权限被拒绝而失败" {
    touch "$TMPDIR/readonly.txt"
    chmod 000 "$TMPDIR/readonly.txt"
    run my_function "$TMPDIR/readonly.txt"
    [ "$status" -ne 0 ]
    chmod 644 "$TMPDIR/readonly.txt"  # 清理
}

@test "函数提供有用的错误信息" {
    run my_function --invalid-option
    [ "$status" -ne 0 ]
    [[ "$output" == *"Usage:"* ]]
}
```

### 带依赖项的测试

```bash
#!/usr/bin/env bats

setup() {
    # 检查必需工具
    if ! command -v jq &>/dev/null; then
        skip "jq 未安装"
    fi

    export SCRIPT="${BATS_TEST_DIRNAME}/../bin/script.sh"
}

@test "JSON 解析正常" {
    skip_if ! command -v jq &>/dev/null
    run my_json_parser '{"key": "value"}'
    [ "$status" -eq 0 ]
}
```

### 测试 Shell 兼容性

```bash
#!/usr/bin/env bats

@test "在 bash 中脚本正常工作" {
    bash "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
}

@test "在 sh (POSIX) 中脚本正常工作" {
    sh "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
}

@test "在 dash 中脚本正常工作" {
    if command -v dash &>/dev/null; then
        dash "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
    else
        skip "dash 未安装"
    fi
}
```

### 并行执行

```bash
#!/usr/bin/env bats

@test "多个独立操作" {
    run bash -c 'for i in {1..10}; do
        my_operation "$i" &
    done
    wait'
    [ "$status" -eq 0 ]
}

@test "并发文件操作" {
    for i in {1..5}; do
        my_function "$TMPDIR/file$i" &
    done
    wait
    [ -f "$TMPDIR/file1" ]
    [ -f "$TMPDIR/file5" ]
}
```

## 测试辅助模式

### test_helper.sh

```bash
#!/usr/bin/env bash

# 源测试脚本
export SCRIPT_DIR="${BATS_TEST_DIRNAME%/*}/bin"

# 常用测试工具
assert_file_exists() {
    if [ ! -f "$1" ]; then
        echo "预期文件存在: $1"
        return 1
    fi
}

assert_file_equals() {
    local file="$1"
    local expected="$2"

    if [ ! -f "$file" ]; then
        echo "文件不存在: $file"
        return 1
    fi

    local actual=$(cat "$file")
    if [ "$actual" != "$expected" ]; then
        echo "文件内容不匹配"
        echo "预期: $expected"
        echo "实际: $actual"
        return 1
    fi
}

# 创建临时测试目录
setup_test_dir() {
    export TEST_DIR=$(mktemp -d)
}

cleanup_test_dir() {
    rm -rf "$TEST_DIR"
}
```

## 与 CI/CD 集成

### GitHub Actions 工作流

```yaml
name: 测试

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: 安装 Bats
        run: |
          npm install --global bats

      - name: 运行测试
        run: |
          bats tests/*.bats

      - name: 使用 Tap 报告器运行测试
        run: |
          bats tests/*.bats --tap | tee test_output.tap
```

### Makefile 集成

```makefile
.PHONY: test test-verbose test-tap

test:
	bats tests/*.bats

test-verbose:
	bats tests/*.bats --verbose

test-tap:
	bats tests/*.bats --tap

test-parallel:
	bats tests/*.bats --parallel 4

coverage: test
	# 可选: 生成覆盖率报告
```

## 最佳实践

1. **每个测试测试一件事** - 单一职责原则
2. **使用描述性测试名称** - 清晰说明测试内容
3. **测试后清理** - 总是在 teardown 中删除临时文件
4. **测试成功和失败路径** - 不要只测试成功路径
5. **模拟外部依赖** - 隔离被测试单元
6. **使用测试环境（fixtures）处理复杂数据** - 使测试更易读
7. **在 CI/CD 中运行测试** - 尽早捕获回归问题
8. **跨 Shell 语法测试** - 确保可移植性
9. **保持测试快速** - 尽可能并行运行
10. **记录复杂测试设置** - 解释不寻常的模式
