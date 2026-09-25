# DeepWiki
DeepWiki MCP 服务器提供对 DeepWiki 公共仓库文档和搜索功能的程序化访问（Ask Devin）。

**MCP 服务器 URL**: https://mcp.deepwiki.com/mcp


## 提问（推荐）
> 工具的结果由 AI 生成，需要至少 1 分钟或更长的超时时间。
- `npx -y mcporter call "${MCP_URL}.ask_question" repoName:owner/repo question:"用户的问题"`

## 读取 wiki 结构
- `npx -y mcporter call "${MCP_URL}.read_wiki_structure" repoName:owner/repo`

## 读取 wiki 内容
- `npx -y mcporter call "${MCP_URL}.read_wiki_contents" repoName:owner/repo`

## Schema
```shell
/**
 * 获取 GitHub 仓库的文档主题列表。
 * Args:
 * repoName: GitHub 仓库在 owner/repo 格式（例如 "facebook/react"）
 */
function read_wiki_structure(repoName: string): object;
    {
      "type": "object",
      "properties": {
        "repoName": {
          "type": "string"
        }
      },
      "required": [
        "repoName"
      ]
    }

/**
 * 查看关于 GitHub 仓库的文档。
 * Args:
 * repoName: GitHub 仓库在 owner/repo 格式（例如 "facebook/react"）
 */
function read_wiki_contents(repoName: string): object;
    {
      "type": "object",
      "properties": {
        "repoName": {
          "type": "string"
        }
      },
      "required": [
        "repoName"
      ]
    }

/**
 * 提问关于 GitHub 仓库并获得基于上下文的 AI 驱动的回答。
 * Args:
 * repoName: GitHub 仓库或仓库列表（最多 10 个）在 owner/repo 格式
 * question: 关于仓库的问题
 */
function ask_question(repoName: unknown, question: string): object;
    {
      "type": "object",
      "properties": {
        "repoName": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            }
          ]
        },
        "question": {
          "type": "string"
        }
      },
      "required": [
        "repoName",
        "question"
      ]
    }
```
