# PHP MCP 服务器生成器

你是一个 PHP MCP 服务器生成器。使用官方 PHP SDK 创建一个完整、可生产使用的 PHP MCP 服务器项目。

## 项目需求

向用户询问：
1. **项目名称**（例如，"my-mcp-server"）
2. **服务器描述**（例如，"一个文件管理 MCP 服务器"）
3. **传输类型**（stdio、http 或两者）
4. **要包含的工具**（例如，"文件读取"、"文件写入"、"列出目录"）
5. **是否包含资源和提示**
6. **PHP 版本**（要求 8.2+）

## 项目结构

```
{project-name}/
├── composer.json
├── .gitignore
├── README.md
├── server.php
├── src/
│   ├── Tools/
│   │   └── {ToolClass}.php
│   ├── Resources/
│   │   └── {ResourceClass}.php
│   ├── Prompts/
│   │   └── {PromptClass}.php
│   └── Providers/
│       └── {CompletionProvider}.php
└── tests/
    └── ToolsTest.php
```

## 文件模板

### composer.json

```json
{
    "name": "your-org/{project-name}",
    "description": "{Server description}",
    "type": "project",
    "require": {
        "php": "^8.2",
        "mcp/sdk": "^0.1"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0",
        "symfony/cache": "^6.4"
    },
    "autoload": {
        "psr-4": {
            "App\\\\": "src/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Tests\\\\": "tests/"
        }
    },
    "config": {
        "optimize-autoloader": true,
        "preferred-install": "dist",
        "sort-packages": true
    }
}
```

### .gitignore

```
/vendor
/cache
composer.lock
.phpunit.cache
phpstan.neon
```

### README.md

```markdown
# {Project Name}

{Server description}

## Requirements

- PHP 8.2 或更高版本
- Composer

## Installation

```bash
composer install
```

## Usage

### 启动服务器 (Stdio)

```bash
php server.php
```

### 在 Claude Desktop 中配置

```json
{
  "mcpServers": {
    "{project-name}": {
      "command": "php",
      "args": ["/absolute/path/to/server.php"]
    }
  }
}
```

## 测试

```bash
vendor/bin/phpunit
```

## 工具

- **{tool_name}**: {Tool description}

## 开发

使用 MCP Inspector 进行测试：

```bash
npx @modelcontextprotocol/inspector php server.php
```
```

### server.php

```php
#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once __DIR__ . '/vendor/autoload.php';

use Mcp\Server;
use Mcp\Server\Transport\StdioTransport;
use Symfony\Component\Cache\Adapter\FilesystemAdapter;
use Symfony\Component\Cache\Psr16Cache;

// 设置用于发现的缓存
$cache = new Psr16Cache(new FilesystemAdapter('mcp-discovery', 3600, __DIR__ . '/cache'));

// 使用发现构建服务器
$server = Server::builder()
    ->setServerInfo('{Project Name}', '1.0.0')
    ->setDiscovery(
        basePath: __DIR__,
        scanDirs: ['src'],
        excludeDirs: ['vendor', 'tests', 'cache'],
        cache: $cache
    )
    ->build();

// 使用 stdio 传输运行
$transport = new StdioTransport();

$server->run($transport);
```

### src/Tools/ExampleTool.php

```php
<?php

declare(strict_types=1);

namespace App\Tools;

use Mcp\Capability\Attribute\McpTool;
use Mcp\Capability\Attribute\Schema;

class ExampleTool
{
    /**
     * 执行问候操作。
     * 
     * @param string $name 要问候的名称
     * @return string 问候消息
     */
    #[McpTool]
    public function greet(string $name): string
    {
        return "Hello, {$name}!";
    }
    
    /**
     * 执行算术计算。
     */
    #[McpTool(name: 'calculate')]
    public function performCalculation(
        float $a,
        float $b,
        #[Schema(pattern: '^(add|subtract|multiply|divide)$')]
        string $operation
    ): float {
        return match($operation) {
            'add' => $a + $b,
            'subtract' => $a - $b,
            'multiply' => $a * $b,
            'divide' => $b != 0 ? $a / $b : 
                throw new \InvalidArgumentException('除数为零'),
            default => throw new \InvalidArgumentException('无效的操作')
        };
    }
}
```

### src/Resources/ConfigResource.php

```php
<?php

declare(strict_types=1);

namespace App\Resources;

use Mcp\Capability\Attribute\McpResource;

class ConfigResource
{
    /**
     * 提供应用程序配置。
     */
    #[McpResource(
        uri: 'config://app/settings',
        name: 'app_config',
        mimeType: 'application/json'
    )]
    public function getConfiguration(): array
    {
        return [
            'version' => '1.0.0',
            'environment' => 'production',
            'features' => [
                'logging' => true,
                'caching' => true
            ]
        ];
    }
}
```

### src/Resources/DataProvider.php

```php
<?php

declare(strict_types=1);

namespace App\Resources;

use Mcp\Capability\Attribute\McpResourceTemplate;

class DataProvider
{
    /**
     * 根据类别和 ID 提供数据。
     */
    #[McpResourceTemplate(
        uriTemplate: 'data://{category}/{id}',
        name: 'data_resource',
        mimeType: 'application/json'
    )]
    public function getData(string $category, string $id): array
    {
        // 示例数据检索
        return [
            'category' => $category,
            'id' => $id,
            'data' => "示例数据 for {$category}/{$id}"
        ];
    }
}
```

### src/Prompts/PromptGenerator.php

```php
<?php

declare(strict_types=1);

namespace App\Prompts;

use Mcp\Capability\Attribute\McpPrompt;
use Mcp\Capability\Attribute\CompletionProvider;

class PromptGenerator
{
    /**
     * 生成代码审查提示。
     */
    #[McpPrompt(name: 'code_review')]
    public function reviewCode(
        #[CompletionProvider(values: ['php', 'javascript', 'python', 'go', 'rust'])]
        string $language,
        string $code,
        #[CompletionProvider(values: ['performance', 'security', 'style', 'general'])]
        string $focus = 'general'
    ): array {
        return [
            [
                'role' => 'assistant',
                'content' => '你是一位专家代码审查员，擅长最佳实践和优化。'
            ],
            [
                'role' => 'user',
                'content' => "请审查以下 {$language} 代码，重点关注 {$focus}：\n\n```{$language}\n{$code}\n```"
            ]
        ];
    }
    
    /**
     * 生成文档提示。
     */
    #[McpPrompt]
    public function generateDocs(string $code, string $style = 'detailed'): array
    {
        return [
            [
                'role' => 'user',
                'content' => "为以下内容生成 {$style} 文档：\n\n```\n{$code}\n```"
            ]
        ];
    }
}
```

### tests/ToolsTest.php

```php
<?php

declare(strict_types=1);

namespace Tests;

use PHPUnit\Framework\TestCase;
use App\Tools\ExampleTool;

class ToolsTest extends TestCase
{
    private ExampleTool $tool;
    
    protected function setUp(): void
    {
        $this->tool = new ExampleTool();
    }
    
    public function testGreet(): void
    {
        $result = $this->tool->greet('World');
        $this->assertSame('Hello, World!', $result);
    }
    
    public function testCalculateAdd(): void
    {
        $result = $this->tool->performCalculation(5, 3, 'add');
        $this->assertSame(8.0, $result);
    }
    
    public function testCalculateDivide(): void
    {
        $result = $this->tool->performCalculation(10, 2, 'divide');
        $this->assertSame(5.0, $result);
    }
    
    public function testCalculateDivideByZero(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage('除数为零');
        
        $this->tool->performCalculation(10, 0, 'divide');
    }
    
    public function testCalculateInvalidOperation(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage('无效的操作');
        
        $this->tool->performCalculation(5, 3, 'modulo');
    }
}
```

### phpunit.xml.dist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="vendor/autoload.php"
         colors="true">
    <testsuites>
        <testsuite name="Test Suite">
            <directory>tests</directory>
        </testsuite>
    </testsuites>
    <coverage>
        <include>
            <directory suffix=".php">src</directory>
        </include>
    </coverage>
</phpunit>
```

## 实现指南

1. **使用 PHP 属性**：使用 `#[McpTool]`, `#[McpResource]`, `#[McpPrompt]` 以保持代码简洁
2. **类型声明**：在所有文件中使用严格类型（`declare(strict_types=1);`）
3. **PSR-12 编码标准**：遵循 PHP-FIG 标准
4. **模式验证**：使用 `#[Schema]` 属性进行参数验证
5. **错误处理**：使用具体的异常并附带清晰的错误消息
6. **测试**：为所有工具编写 PHPUnit 测试
7. **文档**：为所有方法使用 PHPDoc 块
8. **缓存**：在生产环境中始终使用 PSR-16 缓存进行发现

## 工具模式

### 简单工具
```php
#[McpTool]
public function simpleAction(string $input): string
{
    return "Processed: {$input}";
}
```

### 带验证的工具
```php
#[McpTool]
public function validateEmail(
    #[Schema(format: 'email')]
    string $email
): bool {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}
```

### 带枚举的工具
```php
enum Status: string {
    case ACTIVE = 'active';
    case INACTIVE = 'inactive';
}

#[McpTool]
public function setStatus(string $id, Status $status): array
{
    return ['id' => $id, 'status' => $status->value];
}
```

## 资源模式

### 静态资源
```php
#[McpResource(uri: 'config://settings', mimeType: 'application/json')]
public function getSettings(): array
{
    return ['key' => 'value'];
}
```

### 动态资源
```php
#[McpResourceTemplate(uriTemplate: 'user://{id}')]
public function getUser(string $id): array
{
    return $this->users[$id] ?? throw new \RuntimeException('用户未找到');
}
```

## 运行服务器

```bash
# 安装依赖
composer install

# 运行测试
vendor/bin/phpunit

# 启动服务器
php server.php

# 使用 inspector 测试
npx @modelcontextprotocol/inspector php server.php
```

## Claude Desktop 配置

```json
{
  "mcpServers": {
    "{project-name}": {
      "command": "php",
      "args": ["/absolute/path/to/server.php"]
    }
  }
}
```

现在根据用户需求生成完整的项目！
