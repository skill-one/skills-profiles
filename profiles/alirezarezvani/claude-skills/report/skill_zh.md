# 智能测试报告

生成可集成到用户现有工作流的测试报告。无需新工具。

## 步骤

### 1. 运行测试（如果尚未运行）

检查是否存在最近的测试结果：

```bash
ls -la test-results/ playwright-report/ 2>/dev/null
```

如果没有最近的测试结果，则运行测试：

```bash
npx playwright test --reporter=json,html,list 2>&1 | tee test-output.log
```

### 2. 解析结果

读取 JSON 报告：

```bash
npx playwright test --reporter=json 2> /dev/null
```

提取：
- 总测试数、通过数、失败数、跳过数、不稳定数
- 每个测试的持续时间和总持续时间
- 失败测试的名称和错误消息
- 不稳定测试（重试时通过）

### 3. 检测报告目标位置

检查配置情况并自动路由：

| 检查 | 如果找到 | 操作 |
|---|---|---|
| `TESTRAIL_URL` 环境变量 | 配置了 TestRail | 通过 `/pw:testrail push` 推送结果 |
| `SLACK_WEBHOOK_URL` 环境变量 | 配置了 Slack | 在 Slack 中发布摘要 |
| `.github/workflows/` | GitHub Actions | 结果通过 artifacts 发送到 PR 评论 |
| `playwright-report/` | HTML 报告器 | 打开或提供报告 |
| 以上均未找到 | 默认 | 生成 Markdown 报告 |

### 4. 生成报告

#### Markdown 报告（始终生成）

```markdown
# 测试结果 — {{date}}

## 摘要
- ✅ 通过：{{passed}}
- ❌ 失败：{{failed}}
- ⏭️ 跳过：{{skipped}}
- 🔄 不稳定：{{flaky}}
- ⏱️ 持续时间：{{duration}}

## 失败测试
| 测试 | 错误 | 文件 |
|---|---|---|
| {{name}} | {{error}} | {{file}}:{{line}} |

## 不稳定测试
| 测试 | 重试次数 | 文件 |
|---|---|---|
| {{name}} | {{retries}} | {{file}} |

## 按项目
| 浏览器 | 通过 | 失败 | 持续时间 |
|---|---|---|---|
| Chromium | X | Y | Zs |
| Firefox | X | Y | Zs |
| WebKit | X | Y | Zs |
```

保存到 `test-reports/{{date}}-report.md`。

#### Slack 摘要（如果配置了 Webhook）

```bash
curl -X POST "$SLACK_WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🧪 测试结果：✅ {{passed}} | ❌ {{failed}} | ⏱️ {{duration}}\n{{failed_details}}"
  }'
```

#### TestRail 推送（如果配置了）

使用 JSON 结果调用 `/pw:testrail push`。

#### HTML 报告

```bash
npx playwright show-report
```

或者在 CI 中：

```bash
echo "HTML 报告位于：playwright-report/index.html"
```

### 5. 趋势分析（如果存在历史数据）

如果 `test-reports/` 中存在之前的报告：
- 比较随时间的通过率
- 识别最近变得不稳定的测试
- 突出新失败与重复失败

## 输出

- 通过/失败/跳过/不稳定数的摘要
- 带有错误消息的失败测试详情
- 报告目标位置确认
- 趋势比较（如果存在历史数据）
- 下一步操作建议（修复失败或庆祝绿色）
