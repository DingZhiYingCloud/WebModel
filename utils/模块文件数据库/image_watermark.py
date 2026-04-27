"""
图片水印工具模块 - 通用图片下载 + 动态水印处理

功能：
  1. 从 URL 下载图片并添加文字水印
  2. 支持批量处理（多张图片一次搞定）
  3. 水印文本和位置从 .env 读取，也可运行时覆盖
  4. 提供 CLI 命令行接口，可直接执行

环境变量（.env）：
  ARTICLE_IMAGE_WATERMARK_TEXT     - 水印文字，默认 "有道翻译"
  ARTICLE_IMAGE_WATERMARK_POSITION - 水印位置，默认 "右下角"
  DEBUG                           - 调试日志开关，True 时输出 loguru 日志

支持的水印位置：
  左上角、右上角、左下角、右下角、居中

使用示例：
  # Python 调用
  from image_watermark import WatermarkProcessor
  wp = WatermarkProcessor()
  result = wp.download_and_watermark("https://example.com/img.jpg", "./output", "photo.jpg")

  # 批量处理
  images = [
      {"url": "https://example.com/a.jpg", "filename": "a.jpg"},
      {"url": "https://example.com/b.png", "filename": "b.png"},
  ]
  results = wp.batch_process(images, "./output")

  # 命令行
  python image_watermark.py --url https://example.com/img.jpg --output-dir ./out --filename photo.jpg
  python image_watermark.py --images '[{"url":"https://example.com/a.jpg","filename":"a.jpg"}]' --output-dir ./out
"""

import os
import sys
import json
import argparse
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple

import requests
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

# ============================================================
# 日志控制：仅在 DEBUG=True 时输出
# ============================================================
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
if not DEBUG:
    logger.disable("__main__")


# ============================================================
# 水印位置映射
# ============================================================
POSITION_MAP = {
    "左上角": "top-left",
    "右上角": "top-right",
    "左下角": "bottom-left",
    "右下角": "bottom-right",
    "居中": "center",
    "top-left": "top-left",
    "top-right": "top-right",
    "bottom-left": "bottom-left",
    "bottom-right": "bottom-right",
    "center": "center",
}


@dataclass
class WatermarkConfig:
    """水印配置

    Attributes:
        text: 水印文字内容
        position: 水印位置（中文或英文皆可）
        font_size_ratio: 字体大小占图片短边的比例，默认 0.04
        opacity: 水印透明度 (0.0~1.0)，默认 0.6
        color: 水印颜色 (R, G, B)，默认白色
        stroke_width: 文字描边宽度，默认 1
        stroke_color: 描边颜色 (R, G, B)，默认半透明黑
        padding_ratio: 水印距边缘的间距占短边的比例，默认 0.03
    """
    text: str = ""
    position: str = "右下角"
    font_size_ratio: float = 0.04
    opacity: float = 0.6
    color: Tuple[int, int, int] = (255, 255, 255)
    stroke_width: int = 1
    stroke_color: Tuple[int, int, int] = (0, 0, 0)
    padding_ratio: float = 0.03


@dataclass
class WatermarkResult:
    """单张图片处理结果

    Attributes:
        success: 是否成功
        local_path: 本地保存路径（成功时）
        filename: 文件名
        original_url: 原始 URL
        error: 错误信息（失败时）
    """
    success: bool = False
    local_path: str = ""
    filename: str = ""
    original_url: str = ""
    error: str = ""


class WatermarkProcessor:
    """图片水印处理器

    核心用法：
        wp = WatermarkProcessor()                    # 自动从 .env 读取配置
        result = wp.download_and_watermark(url, dir, name)

    也可手动指定配置：
        wp = WatermarkProcessor(text="自定义水印", position="居中")
    """

    def __init__(
        self,
        text: Optional[str] = None,
        position: Optional[str] = None,
        config: Optional[WatermarkConfig] = None,
    ):
        """初始化水印处理器

        Args:
            text: 水印文字，为 None 时从 .env 读取 ARTICLE_IMAGE_WATERMARK_TEXT
            position: 水印位置，为 None 时从 .env 读取 ARTICLE_IMAGE_WATERMARK_POSITION
            config: 完整的 WatermarkConfig 对象，提供时忽略 text/position 参数
        """
        if config:
            self.config = config
        else:
            self.config = WatermarkConfig(
                text=text or os.getenv("ARTICLE_IMAGE_WATERMARK_TEXT", "有道翻译"),
                position=position or os.getenv("ARTICLE_IMAGE_WATERMARK_POSITION", "右下角"),
            )

        if not self.config.text:
            raise ValueError("水印文字不能为空，请设置 .env 中的 ARTICLE_IMAGE_WATERMARK_TEXT 或传入 text 参数")

        logger.info(f"水印处理器初始化: text='{self.config.text}', position='{self.config.position}'")

    # ----------------------------------------------------------
    # 核心方法
    # ----------------------------------------------------------

    def add_watermark(self, image_path: str, output_path: str) -> str:
        """为本地图片添加水印并保存

        Args:
            image_path: 原图本地路径
            output_path: 输出路径

        Returns:
            保存后的文件路径

        Raises:
            FileNotFoundError: 原图不存在
            ValueError: 不支持的水印位置
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片不存在: {image_path}")

        img = Image.open(image_path).convert("RGBA")
        watermarked = self._draw_watermark(img)
        watermarked.convert("RGB").save(output_path, quality=95)

        logger.debug(f"水印已添加: {output_path}")
        return output_path

    def download_and_watermark(
        self,
        image_url: str,
        output_dir: str,
        filename: str,
    ) -> WatermarkResult:
        """从 URL 下载图片，添加水印后保存

        Args:
            image_url: 图片 URL
            output_dir: 保存目录
            filename: 保存文件名

        Returns:
            WatermarkResult 处理结果
        """
        logger.debug(f"开始处理: {image_url}")

        # 1. 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 2. 下载图片
        temp_path = os.path.join(output_dir, f"_temp_{filename}")
        output_path = os.path.join(output_dir, filename)

        try:
            img = self._download_image(image_url)
        except Exception as e:
            error_msg = f"图片下载失败 [{image_url}]: {e}"
            logger.error(error_msg)
            return WatermarkResult(
                success=False, original_url=image_url,
                filename=filename, error=error_msg,
            )

        # 3. 添加水印
        try:
            img_rgba = img.convert("RGBA")
            watermarked = self._draw_watermark(img_rgba)
            watermarked.convert("RGB").save(output_path, quality=95)
            logger.debug(f"水印图片已保存: {output_path}")
        except Exception as e:
            error_msg = f"水印添加失败 [{image_url}]: {e}"
            logger.error(error_msg)
            # 保存原图作为降级
            img.convert("RGB").save(output_path, quality=95)
            logger.warning(f"已保存无水印原图: {output_path}")
            return WatermarkResult(
                success=False, local_path=output_path,
                original_url=image_url, filename=filename, error=error_msg,
            )
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return WatermarkResult(
            success=True, local_path=output_path,
            original_url=image_url, filename=filename,
        )

    def batch_process(
        self,
        images: List[Dict[str, str]],
        output_dir: str,
    ) -> List[WatermarkResult]:
        """批量下载图片并添加水印

        Args:
            images: 图片列表，每项 {"url": "...", "filename": "..."}
            output_dir: 保存目录

        Returns:
            处理结果列表

        Raises:
            ValueError: 任一图片下载失败时（严格模式）
        """
        results = []
        for img_info in images:
            url = img_info.get("url", "")
            filename = img_info.get("filename", "")

            if not url or not filename:
                results.append(WatermarkResult(
                    success=False, original_url=url,
                    filename=filename, error="url 或 filename 缺失",
                ))
                continue

            result = self.download_and_watermark(url, output_dir, filename)
            results.append(result)

            if not result.success:
                # 严格模式：任一失败立即报错中断
                raise ValueError(
                    f"图片处理失败，已中断: {result.error}\n"
                    f"已成功处理 {sum(1 for r in results if r.success)}/{len(images)} 张"
                )

        logger.info(f"批量处理完成: {len(results)} 张")
        return results

    # ----------------------------------------------------------
    # 内部方法
    # ----------------------------------------------------------

    def _download_image(self, url: str) -> Image.Image:
        """下载图片并返回 PIL Image 对象

        Args:
            url: 图片 URL

        Returns:
            PIL Image 对象

        Raises:
            requests.RequestException: 下载失败
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        from io import BytesIO
        return Image.open(BytesIO(response.content))

    def _draw_watermark(self, img: Image.Image) -> Image.Image:
        """在图片上绘制水印

        Args:
            img: RGBA 模式的 PIL Image

        Returns:
            添加水印后的 RGBA Image
        """
        # 创建透明叠加层
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # 计算字体大小
        short_side = min(img.size)
        font_size = max(12, int(short_side * self.config.font_size_ratio))

        # 加载字体（尝试多种中文字体，依次降级）
        font = self._load_font(font_size)

        # 计算水印位置
        bbox = draw.textbbox((0, 0), self.config.text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        padding = int(short_side * self.config.padding_ratio)

        x, y = self._calculate_position(
            img.size, text_width, text_height, padding
        )

        # 绘制水印文字（带描边）
        alpha = int(255 * self.config.opacity)
        text_color = (*self.config.color, alpha)
        stroke_color = (*self.config.stroke_color, alpha // 2)

        draw.text(
            (x, y), self.config.text, font=font, fill=text_color,
            stroke_width=self.config.stroke_width, stroke_fill=stroke_color,
        )

        # 合并叠加层
        return Image.alpha_composite(img, overlay)

    def _calculate_position(
        self,
        img_size: Tuple[int, int],
        text_width: int,
        text_height: int,
        padding: int,
    ) -> Tuple[int, int]:
        """根据配置计算水印坐标

        Args:
            img_size: 图片尺寸 (width, height)
            text_width: 水印文字宽度
            text_height: 水印文字高度
            padding: 边距

        Returns:
            (x, y) 坐标

        Raises:
            ValueError: 不支持的位置
        """
        pos_key = POSITION_MAP.get(self.config.position, "bottom-right")
        w, h = img_size

        positions = {
            "top-left": (padding, padding),
            "top-right": (w - text_width - padding, padding),
            "bottom-left": (padding, h - text_height - padding),
            "bottom-right": (w - text_width - padding, h - text_height - padding),
            "center": ((w - text_width) // 2, (h - text_height) // 2),
        }

        if pos_key not in positions:
            raise ValueError(
                f"不支持的水印位置: '{self.config.position}'，"
                f"可选: {list(POSITION_MAP.keys())}"
            )

        return positions[pos_key]

    def _load_font(self, font_size: int) -> ImageFont.FreeTypeFont:
        """加载中文字体，依次尝试多种路径

        Args:
            font_size: 字体大小

        Returns:
            字体对象（降级为默认字体）
        """
        # Windows 常见中文字体路径
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",     # 黑体
            "C:/Windows/Fonts/simsun.ttc",     # 宋体
            "C:/Windows/Fonts/simkai.ttf",     # 楷体
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",       # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
            "/System/Library/Fonts/PingFang.ttc",                  # macOS
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, font_size)
                except Exception:
                    continue

        logger.warning("未找到中文字体，使用默认字体（中文可能显示为方框）")
        return ImageFont.load_default()


# ============================================================
# CLI 命令行接口
# ============================================================

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="图片水印工具 - 下载图片并添加文字水印",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  # 单张图片
  python image_watermark.py --url https://example.com/img.jpg --output-dir ./out --filename photo.jpg

  # 批量处理
  python image_watermark.py --images '[{"url":"https://a.com/1.jpg","filename":"1.jpg"}]' --output-dir ./out

  # 指定水印文字和位置
  python image_watermark.py --url https://example.com/img.jpg --output-dir ./out --text "自定义水印" --position 居中
        """,
    )

    # 单图模式参数
    parser.add_argument("--url", help="图片 URL（单图模式）")
    parser.add_argument("--filename", help="保存文件名（单图模式）")

    # 批量模式参数
    parser.add_argument("--images", help='图片列表 JSON（批量模式），格式: [{"url":"...","filename":"..."}]')

    # 通用参数
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--text", help="水印文字（覆盖 .env 配置）")
    parser.add_argument("--position", help="水印位置（覆盖 .env 配置）")

    args = parser.parse_args()

    # 初始化处理器
    try:
        wp = WatermarkProcessor(text=args.text, position=args.position)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 执行处理
    try:
        if args.images:
            # 批量模式
            images = json.loads(args.images)
            results = wp.batch_process(images, args.output_dir)
            for r in results:
                status = "✓" if r.success else "✗"
                print(f"  {status} {r.filename}: {r.local_path or r.error}")
        elif args.url and args.filename:
            # 单图模式
            result = wp.download_and_watermark(args.url, args.output_dir, args.filename)
            if result.success:
                print(f"成功: {result.local_path}")
            else:
                print(f"失败: {result.error}", file=sys.stderr)
                sys.exit(1)
        else:
            parser.error("请提供 --url + --filename（单图模式）或 --images（批量模式）")
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
