"""
辅助工具函数模块
=================

提供URL验证、编码解码、参数解析、请求间隔控制等工具函数，
同时包含供其他模块调用的内部辅助函数。
"""

import re
import time
from urllib.parse import quote, unquote, urlparse, parse_qs, urlencode


# ====================================================================
#  内部辅助函数（供其他模块调用，不注册为MCP工具）
# ====================================================================

def is_valid_url(url: str) -> bool:
    """验证URL格式是否合法。"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_default_headers() -> dict:
    """返回默认的HTTP请求头，模拟浏览器访问。"""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def format_markdown_table(headers: list, rows: list) -> str:
    """将数据格式化为Markdown表格字符串。"""
    if not headers:
        return ""
    lines = []
    lines.append("| " + " | ".join(str(h) for h in headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        cells = [str(c).replace("|", "\\|").replace("\n", " ") for c in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def truncate_text(text: str, max_length: int = 50000) -> str:
    """截断过长的文本，附加截断提示。"""
    if len(text) > max_length:
        return (
            text[:max_length]
            + f"\n\n... (已截断，共 {len(text)} 字符，仅显示前 {max_length} 字符)"
        )
    return text


def safe_get_text(element) -> str:
    """安全获取BeautifulSoup元素的文本内容。"""
    try:
        if element is None:
            return ""
        return element.get_text(strip=True)
    except Exception:
        return ""


def get_attr(element, attr: str, default: str = "") -> str:
    """安全获取BeautifulSoup元素的属性值。"""
    try:
        if element is None:
            return default
        val = element.get(attr)
        return val if val else default
    except Exception:
        return default


# ====================================================================
#  MCP工具注册
# ====================================================================

def register(mcp):
    """向FastMCP服务器注册辅助工具函数。

    参数:
        mcp: FastMCP服务器实例
    """

    @mcp.tool()
    def validate_url(url: str) -> str:
        """
        验证URL格式是否合法，返回验证结果和URL各部分解析信息。

        解析URL的协议(scheme)、域名(netloc)、路径(path)、查询参数(query)和片段(fragment)，
        判断URL是否为合法格式（包含协议和域名）。

        参数:
            url: 待验证的URL字符串

        返回:
            Markdown格式的验证结果，包含合法性判断和URL各组成部分。
        """
        try:
            parsed = urlparse(url)
            valid = all([parsed.scheme, parsed.netloc])

            result = "## URL验证结果\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| URL | `{url}` |\n"
            result += f"| 是否合法 | {'是' if valid else '否'} |\n"
            result += f"| 协议(scheme) | `{parsed.scheme or '无'}` |\n"
            result += f"| 域名(netloc) | `{parsed.netloc or '无'}` |\n"
            result += f"| 路径(path) | `{parsed.path or '无'}` |\n"
            result += f"| 查询参数(query) | `{parsed.query or '无'}` |\n"
            result += f"| 片段(fragment) | `{parsed.fragment or '无'}` |\n"

            if not valid:
                result += "\n> URL不合法，缺少协议(scheme)或域名(netloc)。\n"

            return result
        except Exception as e:
            return f"## URL验证失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def encode_decode_url(url: str, action: str = "encode") -> str:
        """
        对URL或字符串进行编码或解码操作。

        编码操作将URL中的特殊字符转换为百分号编码格式（如空格变为%20），
        解码操作将百分号编码还原为原始字符。

        参数:
            url: 待处理的URL或字符串
            action: 操作类型，"encode"为编码，"decode"为解码，默认为"encode"

        返回:
            Markdown格式的处理结果，包含原始值和处理后的值。
        """
        try:
            if action == "encode":
                encoded = quote(url, safe="")
                decoded_back = unquote(encoded)
                result = "## URL编码结果\n\n"
                result += "| 属性 | 值 |\n| --- | --- |\n"
                result += f"| 原始字符串 | `{url}` |\n"
                result += f"| 编码后 | `{encoded}` |\n"
                result += f"| 解码回来 | `{decoded_back}` |\n"
                result += f"| 是否一致 | {'是' if decoded_back == url else '否'} |\n"
            elif action == "decode":
                decoded = unquote(url)
                result = "## URL解码结果\n\n"
                result += "| 属性 | 值 |\n| --- | --- |\n"
                result += f"| 原始字符串 | `{url}` |\n"
                result += f"| 解码后 | `{decoded}` |\n"
            else:
                result = (
                    f"## 参数错误\n\n"
                    f"> action参数必须为 'encode' 或 'decode'，当前为 '{action}'\n"
                )
            return result
        except Exception as e:
            return f"## 操作失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def parse_query_params(url: str) -> str:
        """
        解析URL中的查询参数，以表格形式展示所有参数及其值。

        支持解析形如 ?key1=value1&key2=value2 的查询字符串，
        自动处理多值参数（同一参数名对应多个值的情况）。

        参数:
            url: 包含查询参数的URL

        返回:
            Markdown格式的查询参数列表，包含参数名、参数值和值数量。
        """
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            if not params:
                return f"## 查询参数解析\n\n> URL中未找到查询参数。\n\nURL: `{url}`\n"

            result = "## 查询参数解析\n\n"
            result += f"**URL**: `{url}`\n\n"
            result += "| 参数名 | 参数值 | 值数量 |\n| --- | --- | --- |\n"
            for key, values in params.items():
                for val in values:
                    result += f"| `{key}` | `{val}` | {len(values)} |\n"

            result += f"\n**共 {len(params)} 个参数**\n"
            return result
        except Exception as e:
            return f"## 解析失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def rate_limit_wait(seconds: float = 1.0) -> str:
        """
        请求间隔控制工具，在连续请求之间等待指定时间以避免触发反爬机制。

        当需要频繁请求同一网站时，在请求之间调用此工具进行等待，
        可以有效避免因请求过快被目标网站封禁或限制访问。

        参数:
            seconds: 等待的秒数，默认1.0秒

        返回:
            Markdown格式的等待结果，包含设定等待时间和实际等待时间。
        """
        try:
            start = time.time()
            time.sleep(seconds)
            actual = time.time() - start

            result = "## 请求间隔控制\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| 设定等待 | {seconds} 秒 |\n"
            result += f"| 实际等待 | {actual:.3f} 秒 |\n"
            result += "| 状态 | 完成 |\n"
            return result
        except Exception as e:
            return f"## 等待失败\n\n> 错误: `{str(e)}`\n"
