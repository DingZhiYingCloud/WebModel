"""文章模块业务逻辑层 - 纯数据处理与业务逻辑，不引用 Django request/response"""

import os
import re
from loguru import logger
from django.conf import settings
from DZY_API.models import Article
from .status_codes import (
    ARTICLE_NOT_FOUND,
    ARTICLE_SLUG_EXISTS,
    ARTICLE_CREATE_FAILED,
    ARTICLE_UPDATE_FAILED,
    ARTICLE_DELETE_FAILED,
    ARTICLE_FILE_SAVE_FAILED,
    ARTICLE_FILE_READ_FAILED,
    ARTICLE_FILE_DELETE_FAILED,
)

# 文章 HTML 文件存储目录（相对于 MEDIA_ROOT）
ARTICLE_DIR = "articles"


# ========== 日志辅助 ==========

def _log(message):
    """调试日志，仅在 DEBUG=True 时输出"""
    if getattr(settings, 'DEBUG', False):
        logger.debug(f"[article] {message}")


# ========== 文件操作（内部函数） ==========

def _get_article_relative_path(slug):
    """获取文章 HTML 文件的相对路径（相对于 MEDIA_ROOT）

    例：articles/my-article.html
    """
    return os.path.join(ARTICLE_DIR, f"{slug}.html")


def _get_article_full_path(relative_path):
    """获取文章 HTML 文件的绝对路径"""
    return os.path.join(settings.MEDIA_ROOT, relative_path)


def _save_html_file(slug, html_content):
    """保存 HTML 内容到磁盘文件

    Returns:
        dict: {"code": 0, "relative_path": "..."} 成功
              {"code": ARTICLE_FILE_SAVE_FAILED, "message": "..."} 失败
    """
    try:
        article_dir = os.path.join(settings.MEDIA_ROOT, ARTICLE_DIR)
        os.makedirs(article_dir, exist_ok=True)

        relative_path = _get_article_relative_path(slug)
        full_path = _get_article_full_path(relative_path)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        _log(f"HTML 文件已保存: {full_path}")
        return {"code": 0, "relative_path": relative_path}
    except Exception as e:
        _log(f"HTML 文件保存失败: {e}")
        return {"code": ARTICLE_FILE_SAVE_FAILED, "message": f"文件保存失败：{str(e)}"}


def _read_html_file(relative_path):
    """从磁盘读取 HTML 内容

    Returns:
        dict: {"code": 0, "content": "..."} 成功
              {"code": ARTICLE_FILE_READ_FAILED, "message": "..."} 失败
    """
    try:
        full_path = _get_article_full_path(relative_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        _log(f"HTML 文件已读取: {full_path}")
        return {"code": 0, "content": content}
    except Exception as e:
        _log(f"HTML 文件读取失败: {e}")
        return {"code": ARTICLE_FILE_READ_FAILED, "message": f"文件读取失败：{str(e)}"}


def _delete_html_file(relative_path):
    """删除磁盘上的 HTML 文件

    Returns:
        dict: {"code": 0} 成功
              {"code": ARTICLE_FILE_DELETE_FAILED, "message": "..."} 失败
    """
    try:
        full_path = _get_article_full_path(relative_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            _log(f"HTML 文件已删除: {full_path}")
        return {"code": 0}
    except Exception as e:
        _log(f"HTML 文件删除失败: {e}")
        return {"code": ARTICLE_FILE_DELETE_FAILED, "message": f"文件删除失败：{str(e)}"}


# ========== 字数 & 阅读时长计算 ==========

def _calculate_word_count(html_content):
    """从 HTML 内容计算字数

    剥离 HTML 标签后统计纯文本字符数（去除空白字符）
    """
    text = re.sub(r'<[^>]+>', '', html_content)
    count = len(text.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", ""))
    return count


def _calculate_reading_time(word_count):
    """根据字数计算阅读时长（分钟），按 400 字/分钟估算"""
    if word_count <= 0:
        return 0
    return max(1, word_count // 400)


# ========== 序列化辅助 ==========

def _serialize_article(article):
    """将 Article 对象序列化为字典（不含 HTML 内容）"""
    return {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "cover_image": article.cover_image,
        "word_count": article.word_count,
        "reading_time": article.reading_time,
        "created_at": article.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": article.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _get_article_or_error(article_id):
    """根据 ID 获取文章对象，不存在时返回错误字典

    Returns:
        (Article, None) 成功
        (None, error_dict) 失败
    """
    try:
        article_id = int(article_id)
    except (ValueError, TypeError):
        return None, {"code": 1002, "message": "文章ID不合法"}

    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return None, {"code": ARTICLE_NOT_FOUND, "message": "文章不存在"}

    return article, None


# ========== 业务接口 ==========

def create_article(title, slug, html_content, cover_image=""):
    """创建文章

    Args:
        title: 文章标题
        slug: 路径名称（唯一标识，同时作为磁盘文件名）
        html_content: HTML 内容
        cover_image: 封面图 URL（可选）

    Returns:
        dict: {"code": 0, "data": {...}} 或 {"code": xxx, "message": "..."}
    """
    _log(f"创建文章: title={title}, slug={slug}")

    # 检查 slug 是否已存在
    if Article.objects.filter(slug=slug).exists():
        return {"code": ARTICLE_SLUG_EXISTS, "message": "路径名称已存在"}

    # 保存 HTML 文件到磁盘
    file_result = _save_html_file(slug, html_content)
    if file_result["code"] != 0:
        return file_result

    # 计算字数和阅读时长
    word_count = _calculate_word_count(html_content)
    reading_time = _calculate_reading_time(word_count)

    # 创建数据库记录
    try:
        article = Article.objects.create(
            title=title,
            slug=slug,
            cover_image=cover_image,
            content_path=file_result["relative_path"],
            word_count=word_count,
            reading_time=reading_time,
        )
        _log(f"文章创建成功: id={article.id}")
        return {"code": 0, "data": _serialize_article(article)}
    except Exception as e:
        # 数据库创建失败时，清理已保存的文件
        _delete_html_file(file_result["relative_path"])
        _log(f"文章创建失败，已回滚文件: {e}")
        return {"code": ARTICLE_CREATE_FAILED, "message": f"文章创建失败：{str(e)}"}


def get_article_detail(article_id):
    """获取文章详情

    Args:
        article_id: 文章 ID

    Returns:
        dict: {"code": 0, "data": {...含content...}} 或 {"code": xxx, "message": "..."}
    """
    _log(f"获取文章详情: id={article_id}")

    article, err = _get_article_or_error(article_id)
    if err:
        return err

    # 从磁盘读取 HTML 内容
    file_result = _read_html_file(article.content_path)
    if file_result["code"] != 0:
        return file_result

    data = _serialize_article(article)
    data["content"] = file_result["content"]

    return {"code": 0, "data": data}


def update_article(article_id, **kwargs):
    """更新文章

    Args:
        article_id: 文章 ID
        **kwargs: 可更新字段（title, slug, html_content, cover_image）

    Returns:
        dict: {"code": 0, "data": {...}} 或 {"code": xxx, "message": "..."}
    """
    _log(f"更新文章: id={article_id}, fields={list(kwargs.keys())}")

    article, err = _get_article_or_error(article_id)
    if err:
        return err

    # 如果更新 slug，检查新 slug 是否已被占用
    new_slug = kwargs.get("slug")
    if new_slug and new_slug != article.slug:
        if Article.objects.filter(slug=new_slug).exists():
            return {"code": ARTICLE_SLUG_EXISTS, "message": "路径名称已存在"}

    # 如果更新 HTML 内容，重新保存文件并计算字数
    html_content = kwargs.get("html_content")
    if html_content is not None:
        target_slug = new_slug if new_slug else article.slug

        # 如果 slug 变了，删除旧文件
        if new_slug and new_slug != article.slug:
            _delete_html_file(article.content_path)

        # 保存新文件
        file_result = _save_html_file(target_slug, html_content)
        if file_result["code"] != 0:
            return file_result

        article.content_path = file_result["relative_path"]
        article.word_count = _calculate_word_count(html_content)
        article.reading_time = _calculate_reading_time(article.word_count)

    elif new_slug and new_slug != article.slug:
        # 只改了 slug 没改内容：重命名文件
        old_full_path = _get_article_full_path(article.content_path)
        new_relative_path = _get_article_relative_path(new_slug)
        new_full_path = _get_article_full_path(new_relative_path)

        try:
            os.rename(old_full_path, new_full_path)
            article.content_path = new_relative_path
            _log(f"文件已重命名: {old_full_path} -> {new_full_path}")
        except Exception as e:
            _log(f"文件重命名失败: {e}")
            return {"code": ARTICLE_FILE_SAVE_FAILED, "message": f"文件重命名失败：{str(e)}"}

    # 更新简单字段
    if kwargs.get("title"):
        article.title = kwargs["title"]
    if new_slug:
        article.slug = new_slug
    if "cover_image" in kwargs:
        article.cover_image = kwargs["cover_image"]

    try:
        article.save()
        _log(f"文章更新成功: id={article.id}")
    except Exception as e:
        _log(f"文章更新失败: {e}")
        return {"code": ARTICLE_UPDATE_FAILED, "message": f"文章更新失败：{str(e)}"}

    return {"code": 0, "data": _serialize_article(article)}


def delete_article(article_id):
    """删除文章（物理删除：删除磁盘文件 + 数据库记录）

    Args:
        article_id: 文章 ID

    Returns:
        dict: {"code": 0, "data": {}} 或 {"code": xxx, "message": "..."}
    """
    _log(f"删除文章: id={article_id}")

    article, err = _get_article_or_error(article_id)
    if err:
        return err

    # 先删除磁盘文件
    file_result = _delete_html_file(article.content_path)
    if file_result["code"] != 0:
        return file_result

    # 再删除数据库记录
    try:
        article.delete()
        _log(f"文章删除成功: id={article_id}")
    except Exception as e:
        _log(f"文章删除失败: {e}")
        return {"code": ARTICLE_DELETE_FAILED, "message": f"文章删除失败：{str(e)}"}

    return {"code": 0, "data": {}}


def get_article_list(page=1, page_size=10):
    """获取文章列表（分页）

    Args:
        page: 页码（从 1 开始）
        page_size: 每页数量

    Returns:
        dict: {"code": 0, "data": {"total", "page", "page_size", "articles"}}
    """
    _log(f"获取文章列表: page={page}, page_size={page_size}")

    # 参数校验
    try:
        page = int(page)
        page_size = int(page_size)
    except (ValueError, TypeError):
        return {"code": 1002, "message": "分页参数不合法"}

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 50:
        page_size = 50

    total = Article.objects.count()
    offset = (page - 1) * page_size
    articles = Article.objects.all()[offset:offset + page_size]

    article_list = [_serialize_article(a) for a in articles]

    return {
        "code": 0,
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "articles": article_list,
        }
    }
