# MCP网页抓取服务器

一个基于FastMCP框架的功能全面的网页抓取MCP服务器，提供26个工具，覆盖网页获取、HTML解析、数据提取和辅助工具四大模块。所有工具返回Markdown格式字符串，可直接用于MCP客户端集成。

## 特性

- **26个MCP工具** - 覆盖网页抓取全流程，从获取到解析到提取
- **Markdown输出** - 所有工具返回格式化的Markdown字符串，便于阅读和使用
- **模块化设计** - 按功能拆分为4个独立模块，结构清晰易于维护
- **FastMCP框架** - 基于官方MCP Python SDK的FastMCP，开箱即用
- **错误处理** - 每个工具内置完善的异常捕获和错误提示
- **自动重定向** - 网页获取工具自动跟随HTTP重定向
- **默认浏览器头** - 自带模拟浏览器的请求头，减少被反爬拦截
- **流式下载** - 文件下载使用流式写入，支持大文件
- **HTML转Markdown** - 内置完整的HTML到Markdown转换器
- **智能内容提取** - 新闻文章和商品信息提取使用多种策略自动识别

## 安装

### 前置要求

- Python 3.10+
- pip 包管理器

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/yourname/mcp-web-scraper.git
cd mcp-web-scraper

# 安装依赖
pip install -r requirements.txt
```

### 依赖列表

| 依赖 | 版本要求 | 用途 |
| --- | --- | --- |
| mcp | >=1.0.0 | MCP协议服务器框架 |
| requests | - | HTTP请求库 |
| beautifulsoup4 | - | HTML解析库 |
| lxml | - | XML/HTML解析（XPath支持） |
| urllib3 | - | URL处理工具 |

## 使用方法

### 直接运行

```bash
python server.py
```

服务器将以stdio传输模式启动，等待MCP客户端连接。

### 配置MCP客户端

在MCP客户端配置文件中添加：

```json
{
  "mcpServers": {
    "web-scraper": {
      "command": "python",
      "args": ["/path/to/mcp-web-scraper/server.py"]
    }
  }
}
```

### 使用示例

#### 获取网页内容

```python
# 工具: fetch_webpage
# 参数: url="https://example.com", timeout=30
# 返回: Markdown格式的HTML内容和响应信息
```

#### 解析HTML表格

```python
# 工具: parse_html_tables
# 参数: html="<table><tr><th>名称</th><th>价格</th></tr>..."
# 返回: Markdown表格格式的数据
```

#### CSS选择器提取

```python
# 工具: extract_by_css_selector
# 参数: html="...", selector="div.product h2.title"
# 返回: 匹配元素的内容和属性
```

#### 新闻文章提取

```python
# 工具: extract_news_article
# 参数: html="..."
# 返回: 标题、作者、发布时间、正文等
```

#### HTML转Markdown

```python
# 工具: html_to_markdown
# 参数: html="<h1>标题</h1><p>段落</p>..."
# 返回: Markdown格式文本
```

## 工具列表

### 网页获取模块（6个工具）

| 工具名 | 说明 |
| --- | --- |
| `fetch_webpage` | 获取网页HTML内容，返回状态码、编码、响应头和HTML正文 |
| `fetch_json_api` | 获取JSON API数据，支持查询参数，自动解析JSON响应 |
| `fetch_with_headers` | 使用自定义请求头获取网页，支持Cookie和认证头 |
| `download_file` | 下载文件到本地，支持流式下载大文件 |
| `check_website_status` | 检查网站状态码和响应信息，适用于可用性监控 |
| `fetch_with_pagination` | 分页获取数据，自动构建分页URL并依次获取 |

### HTML解析模块（8个工具）

| 工具名 | 说明 |
| --- | --- |
| `parse_html_tables` | 解析HTML中的所有表格，转换为Markdown表格 |
| `extract_links` | 提取所有`<a>`标签的链接文本、URL、title和rel |
| `extract_images` | 提取所有`<img>`标签的src、alt、宽高等信息 |
| `extract_text` | 提取纯文本内容，自动去除脚本和样式 |
| `extract_meta_tags` | 提取所有meta标签，包括charset、viewport、OG等 |
| `parse_html_structure` | 分析HTML的DOM结构，统计标签数量，展示层级树 |
| `clean_html` | 清洗HTML，移除脚本、样式、注释等非内容元素 |
| `html_to_markdown` | 将HTML转换为Markdown格式，支持标题、列表、表格等 |

### 数据提取模块（8个工具）

| 工具名 | 说明 |
| --- | --- |
| `extract_by_css_selector` | 使用CSS选择器提取元素，支持属性获取 |
| `extract_by_xpath` | 使用XPath表达式提取元素或属性值 |
| `extract_table_data` | 将指定表格数据提取为CSV格式 |
| `extract_list_data` | 提取HTML列表（ul/ol）的数据 |
| `extract_form_data` | 提取表单结构，包括input、textarea、select等字段 |
| `extract_news_article` | 智能提取新闻文章的标题、正文、作者、时间 |
| `extract_product_info` | 提取商品名称、价格、描述、图片、规格等信息 |
| `extract_social_metadata` | 提取Open Graph、Twitter Card、JSON-LD等社交元数据 |

### 辅助工具模块（4个工具）

| 工具名 | 说明 |
| --- | --- |
| `validate_url` | 验证URL格式是否合法，解析URL各组成部分 |
| `encode_decode_url` | 对URL进行百分号编码或解码 |
| `parse_query_params` | 解析URL中的查询参数，以表格展示 |
| `rate_limit_wait` | 请求间隔控制，避免触发反爬机制 |

## 技术栈

| 技术 | 说明 |
| --- | --- |
| **FastMCP** | MCP官方Python SDK提供的高层API，简化MCP服务器开发 |
| **Requests** | Python最流行的HTTP库，用于网页获取和文件下载 |
| **BeautifulSoup4** | 强大的HTML/XML解析库，用于DOM操作和内容提取 |
| **lxml** | 高性能的XML/HTML解析库，提供XPath支持 |
| **urllib3** | URL处理工具库，提供URL编码解码支持 |

## 项目结构

```
mcp-web-scraper/
├── server.py          # 主入口，创建FastMCP实例并注册所有工具
├── fetch_tools.py     # 网页获取工具模块（6个工具）
├── parse_tools.py     # HTML解析工具模块（8个工具）
├── extract_tools.py   # 数据提取工具模块（8个工具）
├── utils.py           # 辅助工具模块（4个工具 + 内部函数）
├── requirements.txt   # Python依赖列表
├── README.md          # 项目文档
└── SKILL.md           # SkillHub技能描述
```

## 许可证

MIT License
