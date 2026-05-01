"""
访问日志中间件 - 自动记录所有HTTP请求

在 settings.py 的 MIDDLEWARE 中添加：
    'DZY_Web.middleware.access_log_middleware.AccessLogMiddleware',
"""

import os
import sys
import time
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
            }

            self.logger.log_request(request_data)

        except Exception:
            pass

        return response
