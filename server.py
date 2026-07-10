"""
MCP网页抓取服务器 - 主入口
============================

基于FastMCP框架实现的网页抓取服务器，提供26个MCP工具，
涵盖网页获取、HTML解析、数据提取和辅助工具四大模块。

启动方式:
    python server.py

或通过MCP客户端配置:
    command: python
    args: [server.py的完整路径]
"""

import sys
import os

# 将当前目录添加到Python路径，确保模块导入正常
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

import fetch_tools
import parse_tools
import extract_tools
import utils


def create_server() -> FastMCP:
    """创建FastMCP服务器实例并注册所有工具。

    返回:
        配置好的FastMCP服务器实例
    """
    mcp = FastMCP(
        name="mcp-web-scraper",
        instructions=(
            "MCP网页抓取服务器，提供26个工具：\n"
            "- 网页获取（6个）: fetch_webpage, fetch_json_api, "
            "fetch_with_headers, download_file, check_website_status, "
            "fetch_with_pagination\n"
            "- HTML解析（8个）: parse_html_tables, extract_links, "
            "extract_images, extract_text, extract_meta_tags, "
            "parse_html_structure, clean_html, html_to_markdown\n"
            "- 数据提取（8个）: extract_by_css_selector, extract_by_xpath, "
            "extract_table_data, extract_list_data, extract_form_data, "
            "extract_news_article, extract_product_info, "
            "extract_social_metadata\n"
            "- 辅助工具（4个）: validate_url, encode_decode_url, "
            "parse_query_params, rate_limit_wait\n"
            "所有工具返回Markdown格式字符串。"
        ),
    )

    # 注册各模块工具
    fetch_tools.register(mcp)
    parse_tools.register(mcp)
    extract_tools.register(mcp)
    utils.register(mcp)

    return mcp


# 创建全局服务器实例
mcp = create_server()


if __name__ == "__main__":
    mcp.run(transport="stdio")
