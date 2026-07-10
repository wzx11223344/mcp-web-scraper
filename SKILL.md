---
name: mcp-web-scraper-zx
displayName: 网页抓取MCP服务器
version: 1.0.1
summary: 26个MCP工具：网页获取/JSON API/文件下载/HTML表格解析/链接提取/CSS选择器/XPath/HTML转Markdown/新闻文章提取/商品信息提取
tags: [mcp, web-scraper, html-parser, beautifulsoup]
license: MIT
---

# 网页抓取MCP服务器

一个功能全面的MCP网页抓取服务器，提供26个工具，覆盖网页获取、HTML解析、数据提取和辅助功能。

## 功能概览

| 模块 | 工具数量 | 说明 |
| --- | --- | --- |
| 网页获取 | 6 | 获取HTML、JSON API、自定义请求、文件下载、状态检查、分页获取 |
| HTML解析 | 8 | 表格解析、链接提取、图片提取、文本提取、meta标签、结构分析、HTML清洗、转Markdown |
| 数据提取 | 8 | CSS选择器、XPath、表格CSV、列表数据、表单数据、新闻文章、商品信息、社交元数据 |
| 辅助工具 | 4 | URL验证、编码解码、查询参数解析、请求间隔控制 |

## 工具列表

### 网页获取（6个）
- `fetch_webpage` - 获取网页HTML内容
- `fetch_json_api` - 获取JSON API数据
- `fetch_with_headers` - 自定义请求头获取
- `download_file` - 下载文件到本地
- `check_website_status` - 检查网站状态码
- `fetch_with_pagination` - 分页获取数据

### HTML解析（8个）
- `parse_html_tables` - 解析HTML表格
- `extract_links` - 提取所有链接
- `extract_images` - 提取所有图片
- `extract_text` - 提取纯文本内容
- `extract_meta_tags` - 提取meta标签
- `parse_html_structure` - 解析HTML结构
- `clean_html` - 清洗HTML（去脚本/样式）
- `html_to_markdown` - HTML转Markdown

### 数据提取（8个）
- `extract_by_css_selector` - CSS选择器提取
- `extract_by_xpath` - XPath提取
- `extract_table_data` - 表格数据提取为CSV
- `extract_list_data` - 列表数据提取
- `extract_form_data` - 表单数据提取
- `extract_news_article` - 新闻文章提取
- `extract_product_info` - 商品信息提取
- `extract_social_metadata` - 社交媒体元数据提取

### 辅助工具（4个）
- `validate_url` - URL验证
- `encode_decode_url` - URL编码/解码
- `parse_query_params` - 查询参数解析
- `rate_limit_wait` - 请求间隔控制

## 使用方式

```json
{
  "mcpServers": {
    "web-scraper": {
      "command": "python",
      "args": ["path/to/server.py"]
    }
  }
}
```
