"""
网页获取工具模块
=================

提供网页内容获取、JSON API调用、自定义请求头获取、
文件下载、网站状态检查和分页获取等功能。
"""

import os
import json
import time
import requests

from utils import is_valid_url, get_default_headers, truncate_text


def register(mcp):
    """向FastMCP服务器注册网页获取工具函数。

    参数:
        mcp: FastMCP服务器实例
    """

    @mcp.tool()
    def fetch_webpage(url: str, timeout: int = 30) -> str:
        """
        获取网页HTML内容。

        发送HTTP GET请求获取网页的完整HTML源码，使用默认浏览器请求头，
        自动跟随重定向，返回HTML内容和响应信息。

        参数:
            url: 目标网页URL
            timeout: 请求超时时间（秒），默认30秒

        返回:
            Markdown格式的网页获取结果，包含HTTP状态码、编码、内容长度、
            最终URL、响应头和HTML正文。
        """
        if not is_valid_url(url):
            return f"## 获取失败\n\n> URL不合法: `{url}`\n"

        try:
            headers = get_default_headers()
            response = requests.get(
                url, headers=headers, timeout=timeout, allow_redirects=True
            )

            result = "## 网页获取结果\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| URL | `{url}` |\n"
            result += f"| 状态码 | {response.status_code} |\n"
            result += f"| 编码 | `{response.encoding}` |\n"
            result += f"| 内容长度 | {len(response.text)} 字符 |\n"
            result += f"| 最终URL | `{response.url}` |\n"
            result += "\n### 响应头\n\n"
            for k, v in response.headers.items():
                result += f"- **{k}**: `{v}`\n"
            result += f"\n### HTML内容\n\n```html\n{truncate_text(response.text)}\n```\n"
            return result
        except requests.exceptions.Timeout:
            return f"## 获取失败\n\n> 请求超时（{timeout}秒）: `{url}`\n"
        except requests.exceptions.ConnectionError as e:
            return f"## 获取失败\n\n> 连接错误: `{str(e)}`\n"
        except Exception as e:
            return f"## 获取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def fetch_json_api(url: str, params: str = "", timeout: int = 30) -> str:
        """
        获取JSON API数据。

        向指定的API端点发送GET请求，解析返回的JSON数据。
        支持通过查询参数进行过滤和筛选。

        参数:
            url: API端点URL
            params: 查询参数字符串，格式为 key1=val1&key2=val2，可选
            timeout: 请求超时时间（秒），默认30秒

        返回:
            Markdown格式的API调用结果，包含状态码、数据类型和格式化的JSON内容。
        """
        if not is_valid_url(url):
            return f"## 获取失败\n\n> URL不合法: `{url}`\n"

        try:
            headers = get_default_headers()
            headers["Accept"] = "application/json"

            query_params = {}
            if params:
                for pair in params.split("&"):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        query_params[k.strip()] = v.strip()

            response = requests.get(
                url, headers=headers, params=query_params,
                timeout=timeout, allow_redirects=True
            )

            result = "## JSON API获取结果\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| URL | `{url}` |\n"
            result += f"| 状态码 | {response.status_code} |\n"
            result += f"| 内容类型 | `{response.headers.get('Content-Type', '未知')}` |\n"

            if query_params:
                result += "| 查询参数 | "
                result += ", ".join(f"`{k}={v}`" for k, v in query_params.items())
                result += " |\n"
            else:
                result += "| 查询参数 | 无 |\n"

            try:
                json_data = response.json()
                formatted = json.dumps(json_data, ensure_ascii=False, indent=2)
                result += f"\n### JSON数据\n\n```json\n{truncate_text(formatted)}\n```\n"
            except (json.JSONDecodeError, ValueError):
                result += f"\n### 响应内容（非JSON）\n\n```\n{truncate_text(response.text)}\n```\n"

            return result
        except requests.exceptions.Timeout:
            return f"## 获取失败\n\n> 请求超时（{timeout}秒）: `{url}`\n"
        except requests.exceptions.ConnectionError as e:
            return f"## 获取失败\n\n> 连接错误: `{str(e)}`\n"
        except Exception as e:
            return f"## 获取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def fetch_with_headers(
        url: str, headers_json: str, timeout: int = 30
    ) -> str:
        """
        使用自定义请求头获取网页内容。

        允许指定任意HTTP请求头（如Cookie、Authorization、自定义User-Agent等），
        适用于需要认证或特殊请求头的场景。

        参数:
            url: 目标URL
            headers_json: JSON格式的请求头字符串，例如
                '{"User-Agent": "MyBot/1.0", "Cookie": "session=abc123"}'
            timeout: 请求超时时间（秒），默认30秒

        返回:
            Markdown格式的获取结果，包含使用的请求头、状态码和响应内容。
        """
        if not is_valid_url(url):
            return f"## 获取失败\n\n> URL不合法: `{url}`\n"

        try:
            custom_headers = json.loads(headers_json)
        except json.JSONDecodeError as e:
            return f"## 参数错误\n\n> headers_json不是有效的JSON: `{str(e)}`\n"

        try:
            response = requests.get(
                url, headers=custom_headers, timeout=timeout, allow_redirects=True
            )

            result = "## 自定义请求头获取结果\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| URL | `{url}` |\n"
            result += f"| 状态码 | {response.status_code} |\n"
            result += f"| 内容长度 | {len(response.text)} 字符 |\n"

            result += "\n### 使用的请求头\n\n"
            for k, v in custom_headers.items():
                display_val = v if k.lower() != "cookie" else v[:20] + "..."
                result += f"- **{k}**: `{display_val}`\n"

            result += f"\n### 响应内容\n\n```html\n{truncate_text(response.text)}\n```\n"
            return result
        except requests.exceptions.Timeout:
            return f"## 获取失败\n\n> 请求超时（{timeout}秒）: `{url}`\n"
        except requests.exceptions.ConnectionError as e:
            return f"## 获取失败\n\n> 连接错误: `{str(e)}`\n"
        except Exception as e:
            return f"## 获取失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def download_file(url: str, save_path: str = "") -> str:
        """
        下载文件到本地。

        支持下载任意类型的文件（图片、PDF、压缩包等），自动从URL中提取文件名，
        使用流式下载以支持大文件。

        参数:
            url: 文件的下载URL
            save_path: 本地保存路径，如果为空则保存到当前目录

        返回:
            Markdown格式的下载结果，包含文件名、大小、保存路径和下载耗时。
        """
        if not is_valid_url(url):
            return f"## 下载失败\n\n> URL不合法: `{url}`\n"

        try:
            headers = get_default_headers()
            start_time = time.time()

            with requests.get(
                url, headers=headers, stream=True, timeout=60, allow_redirects=True
            ) as response:
                response.raise_for_status()

                # 从URL或响应头中提取文件名
                filename = ""
                content_disp = response.headers.get("Content-Disposition", "")
                if "filename=" in content_disp:
                    filename = content_disp.split("filename=")[-1].strip('"\'')
                if not filename:
                    filename = url.split("/")[-1].split("?")[0]
                if not filename:
                    filename = "downloaded_file"

                if save_path:
                    if os.path.isdir(save_path):
                        filepath = os.path.join(save_path, filename)
                    else:
                        filepath = save_path
                else:
                    filepath = filename

                total_size = 0
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)

                elapsed = time.time() - start_time

                # 格式化文件大小
                if total_size < 1024:
                    size_str = f"{total_size} B"
                elif total_size < 1024 * 1024:
                    size_str = f"{total_size / 1024:.2f} KB"
                else:
                    size_str = f"{total_size / (1024 * 1024):.2f} MB"

                result = "## 文件下载结果\n\n"
                result += "| 属性 | 值 |\n| --- | --- |\n"
                result += f"| URL | `{url}` |\n"
                result += f"| 状态码 | {response.status_code} |\n"
                result += f"| 文件名 | `{filename}` |\n"
                result += f"| 保存路径 | `{os.path.abspath(filepath)}` |\n"
                result += f"| 文件大小 | {size_str} |\n"
                result += f"| 下载耗时 | {elapsed:.2f} 秒 |\n"
                result += "| 状态 | 下载成功 |\n"
                return result
        except requests.exceptions.Timeout:
            return f"## 下载失败\n\n> 请求超时: `{url}`\n"
        except requests.exceptions.ConnectionError as e:
            return f"## 下载失败\n\n> 连接错误: `{str(e)}`\n"
        except Exception as e:
            return f"## 下载失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def check_website_status(url: str) -> str:
        """
        检查网站状态码和响应信息。

        发送HEAD请求检查目标网站的状态，返回HTTP状态码、响应时间和服务器信息，
        适用于网站可用性监控和健康检查。

        参数:
            url: 目标网站URL

        返回:
            Markdown格式的状态检查结果，包含状态码、响应时间、服务器类型等。
        """
        if not is_valid_url(url):
            return f"## 检查失败\n\n> URL不合法: `{url}`\n"

        try:
            headers = get_default_headers()
            start_time = time.time()

            response = requests.head(
                url, headers=headers, timeout=15, allow_redirects=True
            )

            elapsed = time.time() - start_time

            # 状态码含义
            status_codes = {
                200: "OK - 请求成功",
                301: "Moved Permanently - 永久重定向",
                302: "Found - 临时重定向",
                304: "Not Modified - 资源未修改",
                400: "Bad Request - 请求错误",
                401: "Unauthorized - 未授权",
                403: "Forbidden - 禁止访问",
                404: "Not Found - 资源不存在",
                500: "Internal Server Error - 服务器内部错误",
                502: "Bad Gateway - 网关错误",
                503: "Service Unavailable - 服务不可用",
                504: "Gateway Timeout - 网关超时",
            }
            status_meaning = status_codes.get(
                response.status_code, "未知状态码"
            )

            result = "## 网站状态检查\n\n"
            result += "| 属性 | 值 |\n| --- | --- |\n"
            result += f"| URL | `{url}` |\n"
            result += f"| 状态码 | {response.status_code} |\n"
            result += f"| 状态含义 | {status_meaning} |\n"
            result += f"| 响应时间 | {elapsed:.3f} 秒 |\n"
            result += f"| 服务器 | `{response.headers.get('Server', '未知')}` |\n"
            result += f"| 内容类型 | `{response.headers.get('Content-Type', '未知')}` |\n"
            result += f"| 最终URL | `{response.url}` |\n"

            if response.history:
                result += f"| 重定向次数 | {len(response.history)} |\n"
                redirect_chain = " -> ".join(
                    str(r.status_code) for r in response.history
                )
                result += f"| 重定向链 | {redirect_chain} -> {response.status_code} |\n"
            else:
                result += "| 重定向次数 | 0 |\n"

            return result
        except requests.exceptions.Timeout:
            return f"## 检查失败\n\n> 请求超时: `{url}`\n"
        except requests.exceptions.ConnectionError as e:
            return f"## 检查失败\n\n> 连接错误: `{str(e)}`\n"
        except Exception as e:
            return f"## 检查失败\n\n> 错误: `{str(e)}`\n"

    @mcp.tool()
    def fetch_with_pagination(
        base_url: str, pages: int = 5, param_name: str = "page"
    ) -> str:
        """
        分页获取数据。

        自动构建分页URL并依次获取每一页的数据，支持自定义分页参数名。
        每页之间有1秒间隔以避免触发反爬机制。

        参数:
            base_url: 基础URL，分页参数将附加到此URL
            pages: 要获取的页数，默认5页
            param_name: 分页参数名，默认为"page"

        返回:
            Markdown格式的分页获取结果，包含每页的URL、状态码和内容摘要。
        """
        if not is_valid_url(base_url):
            return f"## 获取失败\n\n> URL不合法: `{base_url}`\n"

        if pages < 1 or pages > 50:
            return f"## 参数错误\n\n> pages参数应在1-50之间，当前为{pages}\n"

        try:
            headers = get_default_headers()
            results_summary = []

            for page_num in range(1, pages + 1):
                separator = "&" if "?" in base_url else "?"
                page_url = f"{base_url}{separator}{param_name}={page_num}"

                try:
                    response = requests.get(
                        page_url, headers=headers, timeout=30, allow_redirects=True
                    )
                    content_length = len(response.text)
                    results_summary.append(
                        (page_num, page_url, response.status_code, content_length)
                    )
                except Exception as e:
                    results_summary.append(
                        (page_num, page_url, "错误", str(e)[:100])
                    )

                if page_num < pages:
                    time.sleep(1)

            result = f"## 分页获取结果\n\n"
            result += f"**基础URL**: `{base_url}`\n"
            result += f"**分页参数**: `{param_name}`\n"
            result += f"**获取页数**: {pages}\n\n"
            result += "| 页码 | URL | 状态码 | 内容长度 |\n| --- | --- | --- | --- |\n"
            for item in results_summary:
                page_num, url, status, length = item
                result += f"| {page_num} | `{url}` | {status} | {length} |\n"

            successful = sum(
                1 for r in results_summary if r[2] == 200
            )
            result += f"\n**成功**: {successful}/{pages} 页\n"
            return result
        except Exception as e:
            return f"## 获取失败\n\n> 错误: `{str(e)}`\n"
