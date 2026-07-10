"""
HTML解析工具模块
==================

提供HTML表格解析、链接提取、图片提取、文本提取、
meta标签提取、HTML结构分析、HTML清洗和HTML转Markdown等功能。
"""

from bs4 import BeautifulSoup, Comment

from utils import truncate_text, safe_get_text, get_attr, format_markdown_table


def register(mcp):
    """向FastMCP服务器注册HTML解析工具函数。

    参数:
        mcp: FastMCP服务器实例
    """

    @mcp.tool()
    def parse_html_tables(html: str) -> str:
        """
        解析HTML中的所有表格，以Markdown表格格式输出。

        自动识别HTML中的<table>元素，提取表头和表格数据，
        将每个表格转换为Markdown表格格式。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的表格列表，每个表格包含标题、表头和数据行。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            tables = soup.find_all("table")

            if not tables:
                return "## HTML表格解析\n\n> 未找到表格元素。\n"

            result = f"## HTML表格解析\n\n**共找到 {len(tables)} 个表格**\n"

            for idx, table in enumerate(tables, 1):
                result += f"\n### 表格 {idx}\n\n"
                rows = table.find_all("tr")

                if not rows:
                    result += "> 表格无数据行。\n"
                    continue

                # 提取表头
                header_cells = rows[0].find_all(["th", "td"])
                headers = [safe_get_text(cell) for cell in header_cells]

                if headers:
                    result += format_markdown_table(headers, [])
                else:
                    result += "| (无表头) |\n| --- |\n"

                # 提取数据行
                data_rows = []
                for row in rows[1:]:
                    cells = row.find_all(["td", "th"])
                    data_rows.append([safe_get_text(cell) for cell in cells])

                if data_rows:
                    for row in data_rows:
                        if len(row) < len(headers):
                            row.extend([""] * (len(headers) - len(row)))
                        elif len(row) > len(headers) and headers:
                            row = row[:len(headers)]
                        result += format_markdown_table([], [row])

                result += f"\n*共 {len(data_rows)} 行数据*\n"

            return result
        except Exception as e:
            return f"## 解析失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_links(html: str) -> str:
        """
        提取HTML中的所有超链接。

        扫描所有<a>标签，提取链接文本、URL地址、title属性和rel属性。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的链接列表，包含链接文本、URL、title和rel属性。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a")

            if not links:
                return "## 链接提取\n\n> 未找到链接元素。\n"

            result = f"## 链接提取\n\n**共找到 {len(links)} 个链接**\n\n"
            result += "| 序号 | 链接文本 | URL | title | rel |\n| --- | --- | --- | --- | --- |\n"

            for idx, link in enumerate(links, 1):
                text = safe_get_text(link)
                href = get_attr(link, "href")
                title = get_attr(link, "title")
                rel = get_attr(link, "rel")
                if len(text) > 50:
                    text = text[:50] + "..."
                result += f"| {idx} | {text} | `{href}` | {title} | {rel} |\n"

            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_images(html: str) -> str:
        """
        提取HTML中的所有图片信息。

        扫描所有<img>标签，提取图片URL、alt文本、宽高和title属性。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的图片列表，包含src、alt、width、height等信息。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            images = soup.find_all("img")

            if not images:
                return "## 图片提取\n\n> 未找到图片元素。\n"

            result = f"## 图片提取\n\n**共找到 {len(images)} 张图片**\n\n"
            result += "| 序号 | src | alt | width | height | title |\n| --- | --- | --- | --- | --- | --- |\n"

            for idx, img in enumerate(images, 1):
                src = get_attr(img, "src")
                alt = get_attr(img, "alt")
                width = get_attr(img, "width")
                height = get_attr(img, "height")
                title = get_attr(img, "title")
                result += f"| {idx} | `{src}` | {alt} | {width} | {height} | {title} |\n"

            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_text(html: str) -> str:
        """
        提取HTML中的纯文本内容。

        去除所有HTML标签，提取页面中的纯文本内容，
        自动去除<script>和<style>标签内的内容，保留文本的换行结构。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的纯文本内容。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # 移除script和style
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            # 获取文本，保留换行
            text = soup.get_text(separator="\n", strip=True)

            # 去除多余空行
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            clean_text = "\n".join(lines)

            result = "## 纯文本提取\n\n"
            result += f"| 属性 | 值 |\n| --- | --- |\n"
            result += f"| 原始HTML长度 | {len(html)} 字符 |\n"
            result += f"| 提取文本长度 | {len(clean_text)} 字符 |\n"
            result += f"| 文本行数 | {len(lines)} 行 |\n"
            result += f"\n### 文本内容\n\n```\n{truncate_text(clean_text)}\n```\n"
            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def extract_meta_tags(html: str) -> str:
        """
        提取HTML中的meta标签信息。

        解析所有<meta>标签，包括charset声明、viewport设置、
        description、keywords、Open Graph标签和Twitter Card标签等。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的meta标签列表，包含属性名、属性值和内容。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            metas = soup.find_all("meta")

            if not metas:
                return "## Meta标签提取\n\n> 未找到meta标签。\n"

            result = f"## Meta标签提取\n\n**共找到 {len(metas)} 个meta标签**\n\n"
            result += "| 序号 | name/property | content | http-equiv | charset |\n"
            result += "| --- | --- | --- | --- | --- |\n"

            for idx, meta in enumerate(metas, 1):
                name = get_attr(meta, "name")
                prop = get_attr(meta, "property")
                content = get_attr(meta, "content")
                http_equiv = get_attr(meta, "http-equiv")
                charset = get_attr(meta, "charset")

                label = name or prop or ""
                if len(content) > 80:
                    content = content[:80] + "..."
                result += (
                    f"| {idx} | `{label}` | {content} | "
                    f"{http_equiv} | {charset} |\n"
                )

            return result
        except Exception as e:
            return f"## 提取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def parse_html_structure(html: str) -> str:
        """
        分析HTML文档的结构层次。

        解析HTML的DOM树结构，展示各标签的嵌套层级关系，
        统计各类标签的数量，帮助理解页面整体结构。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的HTML结构分析，包含标签统计和层级树。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # 标签统计
            all_tags = soup.find_all(True)
            tag_counts = {}
            for tag in all_tags:
                name = tag.name
                tag_counts[name] = tag_counts.get(name, 0) + 1

            # 按数量排序
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

            result = "## HTML结构分析\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| HTML总长度 | {len(html)} 字符 |\n"
            result += f"| 标签总数 | {len(all_tags)} |\n"
            result += f"| 标签种类 | {len(tag_counts)} 种 |\n"

            result += "\n### 标签统计\n\n"
            result += "| 标签名 | 数量 |\n| --- | --- |\n"
            for name, count in sorted_tags:
                result += f"| `<{name}>` | {count} |\n"

            # 结构树（只展示前几层）
            result += "\n### 结构树（前3层）\n\n```\n"

            def build_tree(element, depth=0, max_depth=3):
                if depth > max_depth:
                    return
                name = element.name
                if not name or name in (
                    "script", "style", "noscript", "meta", "link", "br"
                ):
                    return
                indent = "  " * depth
                attrs_str = ""
                if element.get("id"):
                    attrs_str += f" #{element.get('id')}"
                if element.get("class"):
                    cls = " ".join(element.get("class"))
                    attrs_str += f" .{cls}"
                result_lines.append(f"{indent}<{name}{attrs_str}>")
                for child in element.children:
                    if hasattr(child, "name") and child.name:
                        build_tree(child, depth + 1, max_depth)

            result_lines = []
            if soup.body:
                build_tree(soup.body)
            else:
                build_tree(soup)

            tree_text = "\n".join(result_lines[:200])
            if len(result_lines) > 200:
                tree_text += f"\n... (共 {len(result_lines)} 行，仅显示前200行)"
            result += tree_text + "\n```\n"

            return result
        except Exception as e:
            return f"## 解析失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def clean_html(html: str) -> str:
        """
        清洗HTML，移除脚本、样式、注释等非内容元素。

        去除<script>、<style>、<noscript>、<iframe>、HTML注释等元素，
        保留页面的核心内容结构，输出清洗后的干净HTML。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的清洗结果，包含清洗前后的对比和清洗后的HTML。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            original_length = len(html)

            # 移除不需要的标签
            removed_tags = []
            tags_to_remove = ["script", "style", "noscript", "iframe", "svg"]
            for tag_name in tags_to_remove:
                found = soup.find_all(tag_name)
                removed_tags.append((tag_name, len(found)))
                for tag in found:
                    tag.decompose()

            # 移除HTML注释
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()

            # 移除空标签（连续清理）
            for tag in soup.find_all(True):
                if not tag.get_text(strip=True) and not tag.find_all():
                    tag.decompose()

            clean_html_str = str(soup)
            clean_length = len(clean_html_str)

            result = "## HTML清洗结果\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| 清洗前长度 | {original_length} 字符 |\n"
            result += f"| 清洗后长度 | {clean_length} 字符 |\n"
            reduction = (
                f"{(1 - clean_length / original_length) * 100:.1f}%"
                if original_length > 0
                else "0%"
            )
            result += f"| 缩减比例 | {reduction} |\n"

            result += "\n### 移除的元素统计\n\n"
            result += "| 标签 | 移除数量 |\n| --- | --- |\n"
            for name, count in removed_tags:
                result += f"| `<{name}>` | {count} |\n"
            result += f"| HTML注释 | {len(comments)} |\n"

            result += f"\n### 清洗后的HTML\n\n```html\n{truncate_text(clean_html_str)}\n```\n"
            return result
        except Exception as e:
            return f"## 清洗失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def html_to_markdown(html: str) -> str:
        """
        将HTML转换为Markdown格式。

        将HTML中的标题、段落、链接、图片、列表、表格、引用、代码等元素
        转换为对应的Markdown语法，输出格式化的Markdown文本。

        参数:
            html: HTML源码字符串

        返回:
            Markdown格式的转换结果，包含转换统计和Markdown正文。
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # 移除script和style
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            md_lines = []
            stats = {"headings": 0, "paragraphs": 0, "links": 0,
                     "images": 0, "lists": 0, "tables": 0, "quotes": 0,
                     "code_blocks": 0}

            def convert_element(element):
                """递归转换单个元素为Markdown。"""
                if element is None:
                    return ""

                # 处理字符串节点
                if isinstance(element, str):
                    return str(element).strip()

                if not hasattr(element, "name") or element.name is None:
                    text = element.get_text(strip=True) if hasattr(element, "get_text") else ""
                    return text

                tag = element.name

                if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    level = int(tag[1])
                    stats["headings"] += 1
                    text = element.get_text(strip=True)
                    return "\n" + "#" * level + " " + text + "\n"

                if tag == "p":
                    stats["paragraphs"] += 1
                    text = convert_children(element)
                    return "\n" + text + "\n"

                if tag == "a":
                    href = get_attr(element, "href")
                    text = element.get_text(strip=True)
                    stats["links"] += 1
                    return f"[{text}]({href})"

                if tag == "img":
                    src = get_attr(element, "src")
                    alt = get_attr(element, "alt")
                    stats["images"] += 1
                    return f"![{alt}]({src})"

                if tag in ("strong", "b"):
                    text = element.get_text(strip=True)
                    return f"**{text}**"

                if tag in ("em", "i"):
                    text = element.get_text(strip=True)
                    return f"*{text}*"

                if tag == "code":
                    text = element.get_text()
                    return f"`{text}`"

                if tag == "pre":
                    stats["code_blocks"] += 1
                    text = element.get_text()
                    return f"\n```\n{text}\n```\n"

                if tag == "blockquote":
                    stats["quotes"] += 1
                    text = element.get_text(strip=True)
                    lines = text.split("\n")
                    quoted = "\n".join("> " + line for line in lines)
                    return "\n" + quoted + "\n"

                if tag == "hr":
                    return "\n---\n"

                if tag == "br":
                    return "\n"

                if tag in ("ul", "ol"):
                    stats["lists"] += 1
                    items = element.find_all("li", recursive=False)
                    md_items = []
                    for i, item in enumerate(items):
                        text = item.get_text(strip=True)
                        if tag == "ol":
                            md_items.append(f"{i + 1}. {text}")
                        else:
                            md_items.append(f"- {text}")
                    return "\n" + "\n".join(md_items) + "\n"

                if tag == "table":
                    stats["tables"] += 1
                    rows = element.find_all("tr")
                    if not rows:
                        return ""
                    md_table_lines = []
                    for i, row in enumerate(rows):
                        cells = row.find_all(["th", "td"])
                        cell_texts = [safe_get_text(c) for c in cells]
                        md_table_lines.append(
                            "| " + " | ".join(cell_texts) + " |"
                        )
                        if i == 0:
                            md_table_lines.append(
                                "| " + " | ".join("---" for _ in cells) + " |"
                            )
                    return "\n" + "\n".join(md_table_lines) + "\n"

                # 默认：递归处理子元素
                return convert_children(element)

            def convert_children(element):
                """递归转换所有子元素。"""
                parts = []
                for child in element.children:
                    converted = convert_element(child)
                    if converted:
                        parts.append(converted)
                return "".join(parts)

            # 处理body或整个文档
            target = soup.body if soup.body else soup
            for child in target.children:
                converted = convert_element(child)
                if converted:
                    md_lines.append(converted)

            markdown_text = "\n".join(md_lines)
            # 清理多余空行
            while "\n\n\n" in markdown_text:
                markdown_text = markdown_text.replace("\n\n\n", "\n\n")

            result = "## HTML转Markdown\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| HTML长度 | {len(html)} 字符 |\n"
            result += f"| Markdown长度 | {len(markdown_text)} 字符 |\n"
            result += f"| 标题数 | {stats['headings']} |\n"
            result += f"| 段落数 | {stats['paragraphs']} |\n"
            result += f"| 链接数 | {stats['links']} |\n"
            result += f"| 图片数 | {stats['images']} |\n"
            result += f"| 列表数 | {stats['lists']} |\n"
            result += f"| 表格数 | {stats['tables']} |\n"
            result += f"| 引用块数 | {stats['quotes']} |\n"
            result += f"| 代码块数 | {stats['code_blocks']} |\n"
            result += f"\n### Markdown内容\n\n{truncate_text(markdown_text)}\n"
            return result
        except Exception as e:
            return f"## 转换失败\n\n> 错误: `{str(e)}`\n"
