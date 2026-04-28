"""
站点地图生成器 - 标准 XML sitemap 生成工具

功能：
  1. 根据文章列表生成符合 sitemaps.org 协议的 XML sitemap
  2. 支持自定义 <changefreq>、<priority> 等属性
  3. 纯 Python 实现，不依赖 Django（数据通过参数传入）
  4. 提供 CLI 命令行接口，可直接执行

协议参考：https://www.sitemaps.org/protocol.html

使用示例：
  # Python 调用
  from sitemap_generator import SitemapGenerator

  gen = SitemapGenerator(base_url="https://example.com")
  articles = [
      {"loc": "/web/youdaotools/news/1/", "lastmod": "2026-04-25"},
      {"loc": "/web/youdaotools/news/2/", "lastmod": "2026-04-26"},
  ]
  xml_string = gen.generate(articles)

  # 命令行
  python sitemap_generator.py --base-url https://example.com --articles '[{"loc":"/news/1/","lastmod":"2026-04-25"}]'
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Optional
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from loguru import logger

# ============================================================
# 日志控制：仅在 DEBUG=True 时输出
# ============================================================
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
if not DEBUG:
    logger.disable("__main__")


class SitemapGenerator:
    """站点地图生成器

    生成符合 sitemaps.org 协议的 XML sitemap。

    核心用法：
        gen = SitemapGenerator(base_url="https://example.com")
        xml_string = gen.generate(articles)

    Attributes:
        base_url: 站点根 URL（如 https://example.com），用于拼接完整 <loc>
        default_changefreq: 默认更新频率
        default_priority: 默认优先级 (0.0~1.0)
    """

    # XML 命名空间
    NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"

    def __init__(
        self,
        base_url: str,
        default_changefreq: str = "weekly",
        default_priority: float = 0.8,
    ):
        """初始化站点地图生成器

        Args:
            base_url: 站点根 URL，末尾不带斜杠（如 https://example.com）
            default_changefreq: 默认更新频率，可选值：
                always / hourly / daily / weekly / monthly / yearly / never
            default_priority: 默认优先级 (0.0~1.0)

        Raises:
            ValueError: base_url 为空
        """
        if not base_url:
            raise ValueError("base_url 不能为空")

        # 确保 base_url 不以 / 结尾，避免拼接时出现双斜杠
        self.base_url = base_url.rstrip("/")
        self.default_changefreq = default_changefreq
        self.default_priority = default_priority

        logger.info(f"站点地图生成器初始化: base_url={self.base_url}")

    def generate(self, articles: List[Dict[str, str]]) -> str:
        """根据文章列表生成 sitemap XML 字符串

        Args:
            articles: 文章列表，每项为一个字典，支持的字段：
                - loc (必填): 页面路径，如 /web/youdaotools/news/1/
                - lastmod (可选): 最后修改时间，格式 YYYY-MM-DD
                - changefreq (可选): 更新频率，覆盖默认值
                - priority (可选): 优先级字符串如 "0.8"，覆盖默认值

        Returns:
            格式化的 XML 字符串

        Raises:
            ValueError: articles 为空或某条记录缺少 loc
        """
        if not articles:
            raise ValueError("文章列表不能为空")

        logger.info(f"开始生成 sitemap: {len(articles)} 条记录")

        # 构建根元素
        urlset = Element("urlset")
        urlset.set("xmlns", self.NAMESPACE)

        for i, article in enumerate(articles):
            loc = article.get("loc", "").strip()
            if not loc:
                logger.warning(f"第 {i+1} 条记录缺少 loc，已跳过")
                continue

            url_elem = SubElement(urlset, "url")

            # <loc>: 完整 URL
            full_url = self._build_full_url(loc)
            SubElement(url_elem, "loc").text = full_url

            # <lastmod>: 最后修改时间
            lastmod = article.get("lastmod", "").strip()
            if lastmod:
                SubElement(url_elem, "lastmod").text = lastmod

            # <changefreq>: 更新频率
            changefreq = article.get("changefreq", "").strip() or self.default_changefreq
            SubElement(url_elem, "changefreq").text = changefreq

            # <priority>: 优先级
            priority = article.get("priority", "").strip() or str(self.default_priority)
            SubElement(url_elem, "priority").text = priority

            logger.debug(f"已添加: {full_url}")

        # 格式化输出（带缩进换行）
        raw_xml = tostring(urlset, encoding="unicode", xml_declaration=False)
        pretty_xml = minidom.parseString(raw_xml).toprettyxml(indent="  ")

        # minidom 会自动加 <?xml version="1.0" ?>，替换为带 encoding 的声明
        declaration = '<?xml version="1.0" encoding="UTF-8"?>'
        pretty_xml = pretty_xml.replace(
            '<?xml version="1.0" ?>', declaration
        )

        logger.info(f"sitemap 生成完成")
        return pretty_xml

    def _build_full_url(self, path: str) -> str:
        """拼接完整 URL

        Args:
            path: 页面路径，如 /web/youdaotools/news/1/

        Returns:
            完整 URL，如 https://example.com/web/youdaotools/news/1/
        """
        # 确保 path 以 / 开头，避免拼接时缺少分隔符
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"


# ============================================================
# CLI 命令行接口
# ============================================================

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="站点地图生成器 - 生成标准 XML sitemap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  # 基本用法
  python sitemap_generator.py --base-url https://example.com --articles '[{"loc":"/news/1/","lastmod":"2026-04-25"}]'

  # 输出到文件
  python sitemap_generator.py --base-url https://example.com --articles articles.json --output sitemap.xml

  # 自定义频率和优先级
  python sitemap_generator.py --base-url https://example.com --articles articles.json --changefreq daily --priority 0.9
        """,
    )

    parser.add_argument(
        "--base-url", required=True,
        help="站点根 URL（如 https://example.com），不包含末尾斜杠",
    )
    parser.add_argument(
        "--articles", required=True,
        help='文章列表，JSON 字符串或 JSON 文件路径。格式: [{"loc":"...","lastmod":"..."}]',
    )
    parser.add_argument(
        "--changefreq", default="weekly",
        help="默认更新频率（默认: weekly）",
    )
    parser.add_argument(
        "--priority", type=float, default=0.8,
        help="默认优先级 0.0~1.0（默认: 0.8）",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径（不指定则输出到 stdout）",
    )

    args = parser.parse_args()

    # 解析文章列表（支持 JSON 字符串或文件路径）
    try:
        if os.path.isfile(args.articles):
            with open(args.articles, "r", encoding="utf-8") as f:
                articles = json.load(f)
        else:
            articles = json.loads(args.articles)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"错误: 无法解析文章列表 - {e}", file=sys.stderr)
        sys.exit(1)

    # 生成 sitemap
    try:
        gen = SitemapGenerator(
            base_url=args.base_url,
            default_changefreq=args.changefreq,
            default_priority=args.priority,
        )
        xml_string = gen.generate(articles)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(xml_string)
        print(f"sitemap 已保存: {args.output}")
    else:
        print(xml_string)


if __name__ == "__main__":
    main()
