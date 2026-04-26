"""文章模块工具层 - 统一响应封装、参数获取辅助"""

from django.http import JsonResponse


# ========== 统一响应函数 ==========

def success_response(data=None, message="成功"):
    """成功响应

    Args:
        data: 实际数据，无数据时传 {} 或 None
        message: 提示信息
    """
    return JsonResponse({
        "code": 0,
        "message": message,
        "data": data if data is not None else {}
    })


def error_response(code, message, data=None):
    """错误响应

    Args:
        code: 错误状态码
        message: 错误描述
        data: 错误时统一传 None
    """
    return JsonResponse({
        "code": code,
        "message": message,
        "data": data
    })


def method_not_allowed_response():
    """405 请求方式不允许"""
    return JsonResponse({
        "code": 405,
        "message": "请求方式不允许",
        "data": None
    })


# ========== 参数获取函数 ==========

def get_param(request, key, required=True, default=None):
    """获取 POST 参数

    Args:
        request: Django request 对象
        key: 参数名
        required: 是否必填
        default: 非必填时的默认值

    Returns:
        (value, error_response) 元组：
        - 成功获取：value 为参数值，error_response 为 None
        - 必填参数缺失：value 为 None，error_response 为错误响应
    """
    value = request.POST.get(key)
    if value is None or value == "":
        if required:
            return None, _param_missing_response(key)
        return default, None
    return value, None


# ========== 内部辅助函数 ==========

def _param_missing_response(param_name):
    """1001 必填参数缺失"""
    return JsonResponse({
        "code": 1001,
        "message": f"参数 {param_name} 缺失",
        "data": None
    })
