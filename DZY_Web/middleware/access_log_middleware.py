"""
访问日志中间件 - 自动记录所有HTTP请求

在 settings.py 的 MIDDLEWARE 中添加：
    'DZY_Web.middleware.access_log_middleware.AccessLogMiddleware',
"""

import os
import sys
import time
import json
from django.conf import settings

sys.path.insert(0, os.path.join(settings.BASE_DIR, 'utils', '模块文件数据库'))
from access_logger import AccessLogger


class AccessLogMiddleware:
    """访问日志中间件

    自动记录每一个HTTP请求的详细信息：
    - 请求路径
    - 请求方法
    - 客户端IP
    - User-Agent
    - 状态码
    - 请求耗时
    - 站点域名
    - GET参数
    - POST数据
    - 文件上传信息
    - Referer
    - Content-Type
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = AccessLogger()

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        if not self.logger.enabled:
            return response

        try:
            duration = time.time() - start_time

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '')

            request_data = {
                'path': request.path,
                'method': request.method,
                'ip': ip,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'status_code': response.status_code,
                'duration': duration,
                'domain': request.META.get('HTTP_HOST', ''),
                'referer': request.META.get('HTTP_REFERER', ''),
                'content_type': request.META.get('CONTENT_TYPE', ''),
            }

            get_params = dict(request.GET.lists())
            if get_params:
                request_data['get_params'] = self._simplify_params(get_params)

            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.META.get('CONTENT_TYPE', '')

                if request.FILES:
                    files_info = []
                    for name, file_list in request.FILES.lists():
                        for f in file_list:
                            files_info.append({
                                'field': name,
                                'name': f.name,
                                'size': f.size,
                                'content_type': f.content_type
                            })
                    request_data['files'] = files_info

                if 'application/json' in content_type:
                    try:
                        if hasattr(request, 'body') and request.body:
                            body_data = json.loads(request.body.decode('utf-8'))
                            if isinstance(body_data, dict):
                                request_data['post_data'] = self._truncate_dict(body_data)
                            else:
                                request_data['post_data'] = str(body_data)[:500]
                    except Exception:
                        request_data['post_data'] = '[JSON Parse Error]'

                elif 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
                    post_params = dict(request.POST.lists())
                    if post_params:
                        request_data['post_data'] = self._simplify_params(post_params)

            self.logger.log_request(request_data)

        except Exception:
            pass

        return response

    def _simplify_params(self, params):
        result = {}
        for k, v in params.items():
            if isinstance(v, list) and len(v) == 1:
                result[k] = str(v[0])[:200]
            else:
                result[k] = [str(x)[:200] for x in v] if isinstance(v, list) else str(v)[:200]
        return result

    def _truncate_dict(self, data, max_len=200):
        result = {}
        for k, v in data.items():
            if isinstance(v, str):
                result[k] = v[:max_len] + ('...' if len(v) > max_len else '')
            elif isinstance(v, (int, float, bool)) or v is None:
                result[k] = v
            else:
                result[k] = str(v)[:max_len]
        return result
