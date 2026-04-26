"""文章模块视图层 - HTTP 请求处理入口，零业务逻辑"""

from django.views.decorators.csrf import csrf_exempt
from .utils import success_response, error_response, method_not_allowed_response, get_param
from .service import create_article, get_article_detail, update_article, delete_article, get_article_list


@csrf_exempt
def create(request):
    """创建文章

    必填：title, slug, html_content
    可选：cover_image
    """
    if request.method != "POST":
        return method_not_allowed_response()

    title, err = get_param(request, "title", required=True)
    if err:
        return err

    slug, err = get_param(request, "slug", required=True)
    if err:
        return err

    html_content, err = get_param(request, "html_content", required=True)
    if err:
        return err

    cover_image, _ = get_param(request, "cover_image", required=False, default="")

    res = create_article(title, slug, html_content, cover_image)

    if res["code"] != 0:
        return error_response(res["code"], res["message"])
    return success_response(res["data"], "文章创建成功")


@csrf_exempt
def detail(request):
    """获取文章详情

    必填：id
    """
    if request.method != "POST":
        return method_not_allowed_response()

    article_id, err = get_param(request, "id", required=True)
    if err:
        return err

    res = get_article_detail(article_id)

    if res["code"] != 0:
        return error_response(res["code"], res["message"])
    return success_response(res["data"], "获取文章详情成功")


@csrf_exempt
def update(request):
    """更新文章

    必填：id
    可选（至少提供一个）：title, slug, html_content, cover_image
    """
    if request.method != "POST":
        return method_not_allowed_response()

    article_id, err = get_param(request, "id", required=True)
    if err:
        return err

    # 获取可选参数
    title, _ = get_param(request, "title", required=False)
    slug, _ = get_param(request, "slug", required=False)
    html_content, _ = get_param(request, "html_content", required=False)
    cover_image, _ = get_param(request, "cover_image", required=False)

    # 构建更新字段字典（只包含实际提供的字段）
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    if slug is not None:
        kwargs["slug"] = slug
    if html_content is not None:
        kwargs["html_content"] = html_content
    if cover_image is not None:
        kwargs["cover_image"] = cover_image

    if not kwargs:
        return error_response(1002, "至少需要提供一个更新字段")

    res = update_article(article_id, **kwargs)

    if res["code"] != 0:
        return error_response(res["code"], res["message"])
    return success_response(res["data"], "文章更新成功")


@csrf_exempt
def delete(request):
    """删除文章（物理删除）

    必填：id
    """
    if request.method != "POST":
        return method_not_allowed_response()

    article_id, err = get_param(request, "id", required=True)
    if err:
        return err

    res = delete_article(article_id)

    if res["code"] != 0:
        return error_response(res["code"], res["message"])
    return success_response(res["data"], "文章删除成功")


@csrf_exempt
def article_list(request):
    """获取文章列表（分页）

    可选：page（默认1）, page_size（默认10，最大50）
    """
    if request.method != "POST":
        return method_not_allowed_response()

    page, _ = get_param(request, "page", required=False, default="1")
    page_size, _ = get_param(request, "page_size", required=False, default="10")

    res = get_article_list(page, page_size)

    if res["code"] != 0:
        return error_response(res["code"], res["message"])
    return success_response(res["data"], "获取文章列表成功")
