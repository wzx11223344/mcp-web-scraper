"""
数据提取工具模块
==================

提供CSS选择器提取、XPath提取、表格数据CSV提取、列表数据提取、
表单数据提取、新闻文章提取、商品信息提取和社交媒体元数据提取等功能。
"""

import csv
import io

from bs4 import BeautifulSoup

from utils import (
    truncate_text,
    safe_get_text,
    get_attr,
    format_markdown_table,
)


def register(mcp):
    """向FastMCP服务器注册数据提取工具函数。

    参数:
        mcp: FastMCP服务器实例
    """

    @mcp.tool()
    def extract_by_css_selector(html: str, selector: str) -> str:
        """
        使用CSS选择器从HTML中提取元素。

        支持所有标准CSS选择器语法，如标签名、类名(.class)、ID(#id)、
        属性选择器([attr=val])、后代选择器(div p)等。

        参数:
            html: HTML源码字符串
            selector: CSS选择器表达式，例如 "div.content p.title"

        返回:
            Markdown格式的提取结果，包含匹配数量和每个匹配元素的内容。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            elements = soup.select(selector)

            if not elements:
                return (
                    f"## CSS选择器提取\n\n"
                    f"> 未找到匹配元素。\n\n"
                    f"**选择器**: `{selector}`\n"
                )

            result = (
                f"## CSS选择器提取\n\n"
                f"**选择器**: `{selector}`\n"
                f"**匹配数量**: {len(elements)}\n\n"
            )

            for idx, elem in enumerate(elements, 1):
                tag_name = elem.name
                text = safe_get_text(elem)
                if not text:
                    text = "(无文本内容)"
                if len(text) > 500:
                    text = text[:500] + "..."

                result += f"### 匹配 {idx}\n\n"
                result += f"| 属性 | 值 |\n| --- | --- |\n"
                result += f"| 标签 | `<{tag_name}>` |\n"
                result += f"| 文本 | {text} |\n"

                # 显示元素属性
                attrs = elem.attrs
                if attrs:
                    result += "\n**元素属性**:\n"
                    for k, v in attrs.items():
                        if isinstance(v, list):
                            v = " ".join(v)
                        result += f"- `{k}`: `{v}`\n"

                # 显示外部HTML（截断）
                outer_html = str(elem)
                if len(outer_html) > 300:
                    outer_html = outer_html[:300] + "..."
                result += f"\n**HTML**:\n```html\n{outer_html}\n```\n"

                if idx >= 50:
                    result += f"\n*仅显示前50个匹配元素，共 {len(elements)} 个*\n"
                    break

            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_by_xpath(html: str, xpath_expr: str) -> str:
        """
        使用XPath表达式从HTML中提取元素或属性。

        支持所有标准XPath语法，包括节点选择、属性提取、
        条件过滤、轴导航等。使用lxml解析器。

        参数:
            html: HTML源码字符串
            xpath_expr: XPath表达式，例如 "//div[@class='title']/text()"

        返回:
            Markdown格式的提取结果，包含匹配数量和每个匹配结果的值。
        """
        try:
            from lxml import html as lxml_html

            tree = lxml_html.fromstring(html)
            results = tree.xpath(xpath_expr)

            if not results:
                return (
                    f"## XPath提取\n\n"
                    f"> 未找到匹配结果。\n\n"
                    f"**XPath**: `{xpath_expr}`\n"
                )

            result = (
                f"## XPath提取\n\n"
                f"**XPath表达式**: `{xpath_expr}`\n"
                f"**匹配数量**: {len(results)}\n\n"
            )

            for idx, item in enumerate(results, 1):
                if hasattr(item, "tag"):
                    # lxml元素
                    text = item.text_content().strip() if hasattr(item, "text_content") else ""
                    tag = item.tag
                    result += f"### 匹配 {idx}\n\n"
                    result += f"| 属性 | 值 |\n| --- | --- |\n"
                    result += f"| 类型 | 元素 |\n"
                    result += f"| 标签 | `<{tag}>` |\n"
                    result += f"| 文本 | {truncate_text(text, 500)} |\n"
                    attrs = dict(item.attrib) if hasattr(item, "attrib") else {}
                    if attrs:
                        result += "\n**属性**:\n"
                        for k, v in attrs.items():
                            result += f"- `{k}`: `{v}`\n"
                else:
                    # 字符串或属性值
                    result += f"### 匹配 {idx}\n\n"
                    result += f"| 属性 | 值 |\n| --- | --- |\n"
                    result += f"| 类型 | 文本/属性值 |\n"
                    result += f"| 值 | `{str(item)}` |\n"

                if idx >= 50:
                    result += f"\n*仅显示前50个匹配结果，共 {len(results)} 个*\n"
                    break

            return result
        except ImportError:
            return (
                "## 提取失败\n\n"
                "> 缺少lxml库，请安装: `pip install lxml`\n"
            )
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_table_data(html: str, table_index: int = 0) -> str:
        """
        将HTML表格数据提取为CSV格式。

        指定表格索引，提取该表格的所有行和列数据，输出为CSV格式文本，
        可直接复制保存为.csv文件。

        参数:
            html: HTML源码字符串
            table_index: 表格索引（从0开始），默认为0（第一个表格）

        返回:
            Markdown格式的提取结果，包含CSV数据和表格预览。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            tables = soup.find_all("table")

            if not tables:
                return "## 表格数据提取\n\n> 未找到表格元素。\n"

            if table_index >= len(tables) or table_index < 0:
                return (
                    f"## 表格数据提取\n\n"
                    f"> 表格索引超出范围，共有 {len(tables)} 个表格"
                    f"（索引0-{len(tables) - 1}）。\n"
                )

            table = tables[table_index]
            rows = table.find_all("tr")

            csv_data = []
            for row in rows:
                cells = row.find_all(["td", "th"])
                row_data = [safe_get_text(cell) for cell in cells]
                csv_data.append(row_data)

            # 生成CSV
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
            for row in csv_data:
                writer.writerow(row)
            csv_text = output.getvalue().strip()

            result = f"## 表格数据提取\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| 表格索引 | {table_index} |\n"
            result += f"| 表格总数 | {len(tables)} |\n"
            result += f"| 行数 | {len(csv_data)} |\n"
            if csv_data:
                result += f"| 列数 | {len(csv_data[0])} |\n"

            # 表格预览
            if csv_data:
                result += "\n### 表格预览\n\n"
                headers = csv_data[0] if csv_data else []
                data_rows = csv_data[1:] if len(csv_data) > 1 else []
                if headers:
                    result += format_markdown_table(headers, [])
                    for row in data_rows:
                        if len(row) < len(headers):
                            row.extend([""] * (len(headers) - len(row)))
                        result += format_markdown_table([], [row])

            result += f"\n### CSV数据\n\n```csv\n{truncate_text(csv_text)}\n```\n"
            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_list_data(html: str, list_selector: str = "ul, ol") -> str:
        """
        从HTML中提取列表数据。

        解析HTML中的<ul>和<ol>列表元素，提取列表项内容，
        支持通过CSS选择器指定特定的列表。

        参数:
            html: HTML源码字符串
            list_selector: 列表的CSS选择器，默认为"ul, ol"（所有列表）

        返回:
            Markdown格式的列表数据，包含列表数量和每个列表的项目。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            lists = soup.select(list_selector)

            if not lists:
                return (
                    f"## 列表数据提取\n\n"
                    f"> 未找到匹配的列表元素。\n\n"
                    f"**选择器**: `{list_selector}`\n"
                )

            result = (
                f"## 列表数据提取\n\n"
                f"**选择器**: `{list_selector}`\n"
                f"**列表数量**: {len(lists)}\n"
            )

            for idx, lst in enumerate(lists, 1):
                list_type = lst.name
                items = lst.find_all("li", recursive=False)
                if not items:
                    items = lst.find_all("li")

                result += f"\n### 列表 {idx}（<{list_type}>）\n\n"

                if not items:
                    result += "> (无列表项)\n"
                    continue

                result += "| 序号 | 内容 |\n| --- | --- |\n"
                for i, item in enumerate(items, 1):
                    text = safe_get_text(item)
                    if len(text) > 100:
                        text = text[:100] + "..."
                    result += f"| {i} | {text} |\n"

                if idx >= 20:
                    result += f"\n*仅显示前20个列表，共 {len(lists)} 个*\n"
                    break

            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_form_data(html: str, form_index: int = 0) -> str:
        """
        从HTML中提取表单数据结构。

        解析指定表单的所有输入元素，包括input、textarea、select等，
        提取字段名称、类型、默认值、选项等信息。

        参数:
            html: HTML源码字符串
            form_index: 表单索引（从0开始），默认为0（第一个表单）

        返回:
            Markdown格式的表单结构信息，包含所有字段的详细信息。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            forms = soup.find_all("form")

            if not forms:
                return "## 表单数据提取\n\n> 未找到表单元素。\n"

            if form_index >= len(forms) or form_index < 0:
                return (
                    f"## 表单数据提取\n\n"
                    f"> 表单索引超出范围，共有 {len(forms)} 个表单"
                    f"（索引0-{len(forms) - 1}）。\n"
                )

            form = forms[form_index]
            action = get_attr(form, "action")
            method = get_attr(form, "method", "GET").upper()
            enctype = get_attr(form, "enctype", "application/x-www-form-urlencoded")

            result = "## 表单数据提取\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| 表单索引 | {form_index} |\n"
            result += f"| 表单总数 | {len(forms)} |\n"
            result += f"| action | `{action}` |\n"
            result += f"| method | `{method}` |\n"
            result += f"| enctype | `{enctype}` |\n"

            # 提取所有输入字段
            inputs = form.find_all("input")
            textareas = form.find_all("textarea")
            selects = form.find_all("select")
            buttons = form.find_all("button")

            result += f"| input数量 | {len(inputs)} |\n"
            result += f"| textarea数量 | {len(textareas)} |\n"
            result += f"| select数量 | {len(selects)} |\n"
            result += f"| button数量 | {len(buttons)} |\n"

            # input字段
            if inputs:
                result += "\n### Input字段\n\n"
                result += "| 名称 | 类型 | 值 | placeholder | 必填 |\n| --- | --- | --- | --- | --- |\n"
                for inp in inputs:
                    name = get_attr(inp, "name")
                    type_ = get_attr(inp, "type", "text")
                    value = get_attr(inp, "value")
                    placeholder = get_attr(inp, "placeholder")
                    required = "是" if inp.has_attr("required") else ""
                    result += f"| `{name}` | {type_} | `{value}` | {placeholder} | {required} |\n"

            # textarea字段
            if textareas:
                result += "\n### Textarea字段\n\n"
                result += "| 名称 | 默认值 | placeholder | 行数 | 列数 |\n| --- | --- | --- | --- | --- |\n"
                for ta in textareas:
                    name = get_attr(ta, "name")
                    value = safe_get_text(ta)
                    placeholder = get_attr(ta, "placeholder")
                    rows = get_attr(ta, "rows")
                    cols = get_attr(ta, "cols")
                    result += f"| `{name}` | {value[:50]} | {placeholder} | {rows} | {cols} |\n"

            # select字段
            if selects:
                result += "\n### Select字段\n\n"
                for sel in selects:
                    name = get_attr(sel, "name")
                    options = sel.find_all("option")
                    result += f"\n**字段名**: `{name}`\n\n"
                    result += "| 选项值 | 选项文本 | 是否选中 |\n| --- | --- | --- |\n"
                    for opt in options:
                        val = get_attr(opt, "value")
                        text = safe_get_text(opt)
                        selected = "是" if opt.has_attr("selected") else ""
                        result += f"| `{val}` | {text} | {selected} |\n"

            # button字段
            if buttons:
                result += "\n### Button字段\n\n"
                result += "| 类型 | 名称 | 文本 |\n| --- | --- | --- |\n"
                for btn in buttons:
                    type_ = get_attr(btn, "type", "submit")
                    name = get_attr(btn, "name")
                    text = safe_get_text(btn)
                    result += f"| {type_} | `{name}` | {text} |\n"

            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_news_article(html: str) -> str:
        """
        从HTML中提取新闻文章内容。

        自动识别并提取新闻文章的标题、正文内容、发布时间、作者、
        来源和摘要等信息，支持多种常见的新闻页面结构。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的新闻文章信息，包含标题、作者、时间、正文等。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # 提取标题
            title = ""
            title_tag = soup.find("h1")
            if title_tag:
                title = safe_get_text(title_tag)
            if not title:
                title = get_attr(soup.find("meta", {"property": "og:title"}), "content")
            if not title:
                t = soup.find("title")
                title = safe_get_text(t) if t else ""

            # 提取作者
            author = ""
            author_meta = soup.find("meta", {"name": "author"})
            if author_meta:
                author = get_attr(author_meta, "content")
            if not author:
                author_tag = soup.find(attrs={"class": "author"})
                if author_tag:
                    author = safe_get_text(author_tag)
            if not author:
                author_tag = soup.find(attrs={"itemprop": "author"})
                if author_tag:
                    author = safe_get_text(author_tag)

            # 提取发布时间
            publish_time = ""
            time_tag = soup.find("time")
            if time_tag:
                publish_time = get_attr(time_tag, "datetime") or safe_get_text(time_tag)
            if not publish_time:
                time_meta = soup.find("meta", {"property": "article:published_time"})
                if time_meta:
                    publish_time = get_attr(time_meta, "content")
            if not publish_time:
                for meta in soup.find_all("meta"):
                    name = get_attr(meta, "name") + get_attr(meta, "property")
                    if "date" in name.lower() or "time" in name.lower():
                        publish_time = get_attr(meta, "content")
                        break

            # 提取摘要
            summary = ""
            desc_meta = soup.find("meta", {"name": "description"})
            if desc_meta:
                summary = get_attr(desc_meta, "content")
            if not summary:
                desc_meta = soup.find("meta", {"property": "og:description"})
                if desc_meta:
                    summary = get_attr(desc_meta, "content")

            # 提取正文
            article = soup.find("article")
            if not article:
                article = soup.find(attrs={"class": ["article", "content", "post-content",
                                                       "article-body", "entry-content"]})
            if not article:
                article = soup.find(attrs={"id": ["article", "content", "article-body"]})

            if article:
                # 清除非内容元素
                for tag in article(["script", "style", "nav", "aside", "footer"]):
                    tag.decompose()
                body_text = article.get_text(separator="\n", strip=True)
            else:
                # 回退：从body中提取
                body = soup.body or soup
                for tag in body(["script", "style", "nav", "aside", "footer",
                                 "header", "form", "iframe"]):
                    tag.decompose()
                body_text = body.get_text(separator="\n", strip=True)

            # 清理多余空行
            lines = [line.strip() for line in body_text.split("\n") if line.strip()]
            clean_body = "\n".join(lines)

            # 提取来源
            source = ""
            source_meta = soup.find("meta", {"property": "og:site_name"})
            if source_meta:
                source = get_attr(source_meta, "content")

            result = "## 新闻文章提取\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| 标题 | {title} |\n"
            result += f"| 作者 | {author or '未检测到'} |\n"
            result += f"| 发布时间 | {publish_time or '未检测到'} |\n"
            result += f"| 来源 | {source or '未检测到'} |\n"
            result += f"| 摘要 | {summary or '未检测到'} |\n"
            result += f"| 正文字数 | {len(clean_body)} 字符 |\n"
            result += f"| 正文行数 | {len(lines)} 行 |\n"
            result += f"\n### 正文内容\n\n{truncate_text(clean_body)}\n"
            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_product_info(html: str) -> str:
        """
        从HTML中提取商品信息。

        自动识别并提取商品名称、价格、描述、图片、规格参数、
        评价信息等电商页面常见数据。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的商品信息，包含名称、价格、描述、图片等。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # 商品名称
            name = ""
            og_title = soup.find("meta", {"property": "og:title"})
            if og_title:
                name = get_attr(og_title, "content")
            if not name:
                h1 = soup.find("h1")
                if h1:
                    name = safe_get_text(h1)
            if not name:
                title_tag = soup.find("title")
                if title_tag:
                    name = safe_get_text(title_tag)

            # 商品价格
            price = ""
            price_patterns = [
                r'["\']price["\']\s*:\s*["\']?([\d.]+)',
                r'["\']price["\']\s*:\s*(\d+\.?\d*)',
            ]
            import re
            for pattern in price_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    price = match.group(1)
                    break
            if not price:
                price_meta = soup.find("meta", {"property": "product:price:amount"})
                if price_meta:
                    price = get_attr(price_meta, "content")
            if not price:
                price_elem = soup.find(attrs={"class": ["price", "product-price",
                                                         "sale-price", "current-price"]})
                if price_elem:
                    price_text = safe_get_text(price_elem)
                    price_match = re.search(r'[\d,]+\.?\d*', price_text)
                    if price_match:
                        price = price_match.group(0)

            # 货币
            currency = ""
            currency_meta = soup.find("meta", {"property": "product:price:currency"})
            if currency_meta:
                currency = get_attr(currency_meta, "content")

            # 商品描述
            description = ""
            desc_meta = soup.find("meta", {"name": "description"})
            if desc_meta:
                description = get_attr(desc_meta, "content")
            if not description:
                desc_meta = soup.find("meta", {"property": "og:description"})
                if desc_meta:
                    description = get_attr(desc_meta, "content")

            # 商品图片
            images = []
            og_image = soup.find("meta", {"property": "og:image"})
            if og_image:
                images.append(get_attr(og_image, "content"))
            img_tags = soup.find_all("img")
            for img in img_tags:
                src = get_attr(img, "src")
                alt = get_attr(img, "alt")
                if src and ("product" in src.lower() or alt):
                    if src not in images:
                        images.append(src)

            # 商品可用性
            availability = ""
            avail_meta = soup.find("meta", {"property": "product:availability"})
            if avail_meta:
                availability = get_attr(avail_meta, "content")

            # 商品URL
            url = ""
            url_meta = soup.find("meta", {"property": "og:url"})
            if url_meta:
                url = get_attr(url_meta, "content")

            # 品牌信息
            brand = ""
            brand_meta = soup.find("meta", {"property": "product:brand"})
            if brand_meta:
                brand = get_attr(brand_meta, "content")

            # SKU
            sku = ""
            sku_meta = soup.find("meta", {"property": "product:retailer_item_id"})
            if sku_meta:
                sku = get_attr(sku_meta, "content")

            result = "## 商品信息提取\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| 商品名称 | {name or '未检测到'} |\n"
            result += f"| 价格 | {price or '未检测到'} {currency} |\n"
            result += f"| 货币 | {currency or '未检测到'} |\n"
            result += f"| 品牌 | {brand or '未检测到'} |\n"
            result += f"| SKU | {sku or '未检测到'} |\n"
            result += f"| 可用性 | {availability or '未检测到'} |\n"
            result += f"| 商品URL | `{url or '未检测到'}` |\n"
            result += f"| 描述 | {truncate_text(description or '未检测到', 500)} |\n"

            if images:
                result += f"\n### 商品图片（共 {len(images)} 张）\n\n"
                for i, img_url in enumerate(images[:10], 1):
                    result += f"{i}. `{img_url}`\n"

            # 尝试提取规格参数表
            spec_tables = soup.find_all("table")
            if spec_tables:
                result += "\n### 规格参数\n\n"
                for table in spec_tables[:3]:
                    rows = table.find_all("tr")
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        if len(cells) >= 2:
                            key = safe_get_text(cells[0])
                            val = safe_get_text(cells[1])
                            if key and val:
                                result += f"- **{key}**: {val}\n"

            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_social_metadata(html: str) -> str:
        """
        从HTML中提取社交媒体元数据。

        提取Open Graph标签、Twitter Card标签、结构化数据(JSON-LD)、
        社交分享信息等社交媒体相关的元数据。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的社交媒体元数据，包含OG标签、Twitter Card和JSON-LD数据。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            result = "## 社交媒体元数据提取\n\n"

            # Open Graph标签
            og_tags = soup.find_all("meta", {"property": lambda x: x and x.startswith("og:")})
            if og_tags:
                result += "### Open Graph 标签\n\n"
                result += "| 属性 | 值 |\n| --- | --- |\n"
                for tag in og_tags:
                    prop = get_attr(tag, "property")
                    content = get_attr(tag, "content")
                    if len(content) > 100:
                        content = content[:100] + "..."
                    result += f"| `{prop}` | {content} |\n"
            else:
                result += "### Open Graph 标签\n\n> 未找到Open Graph标签。\n"

            # Twitter Card标签
            twitter_tags = soup.find_all(
                "meta", {"name": lambda x: x and x.startswith("twitter:")}
            )
            if twitter_tags:
                result += "\n### Twitter Card 标签\n\n"
                result += "| 属性 | 值 |\n| --- | --- |\n"
                for tag in twitter_tags:
                    name = get_attr(tag, "name")
                    content = get_attr(tag, "content")
                    if len(content) > 100:
                        content = content[:100] + "..."
                    result += f"| `{name}` | {content} |\n"
            else:
                result += "\n### Twitter Card 标签\n\n> 未找到Twitter Card标签。\n"

            # JSON-LD结构化数据
            json_ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
            if json_ld_scripts:
                result += f"\n### JSON-LD 结构化数据（共 {len(json_ld_scripts)} 个）\n"
                import json
                for idx, script in enumerate(json_ld_scripts, 1):
                    try:
                        data = json.loads(script.string)
                        formatted = json.dumps(data, ensure_ascii=False, indent=2)
                        result += f"\n#### JSON-LD {idx}\n\n```json\n"
                        result += truncate_text(formatted, 2000)
                        result += "\n```\n"
                    except (json.JSONDecodeError, TypeError):
                        result += f"\n#### JSON-LD {idx}\n\n> 解析失败\n"
            else:
                result += "\n### JSON-LD 结构化数据\n\n> 未找到JSON-LD数据。\n"

            # 其他社交相关meta标签
            result += "\n### 其他社交相关标签\n\n"
            social_metas = soup.find_all("meta", {
                "name": lambda x: x and any(
                    kw in x.lower() for kw in [
                        "author", "publisher", "share", "social",
                        "canonical", "referrer"
                    ]
                )
            })
            if social_metas:
                result += "| 属性 | 值 |\n| --- | --- |\n"
                for tag in social_metas:
                    name = get_attr(tag, "name")
                    content = get_attr(tag, "content")
                    if len(content) > 100:
                        content = content[:100] + "..."
                    result += f"| `{name}` | {content} |\n"
            else:
                result += "> 未找到其他社交相关标签。\n"

            # canonical链接
            canonical = soup.find("link", {"rel": "canonical"})
            if canonical:
                result += f"\n**Canonical URL**: `{get_attr(canonical, 'href')}`\n"

            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"
