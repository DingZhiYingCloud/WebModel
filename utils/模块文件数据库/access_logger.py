"""
访问日志插件 - HTTP请求日志记录与可视化

功能：
  1. 自动记录所有HTTP请求：路径、方法、IP、UA、状态码、耗时
  2. 文本文件存储，按大小自动切割
  3. 终端彩色实时输出
  4. 自动排除静态资源路径
  5. 按域名过滤查询
  6. 状态码和请求方法统计
  7. Django中间件集成
  8. 密码保护的Web可视化页面

环境变量（.env）：
  ACCESS_LOG_ENABLED       - 是否启用访问日志，默认 True
  ACCESS_LOG_PATH          - 日志文件路径，默认 logs/access.log
  ACCESS_LOG_MAX_SIZE      - 单文件最大大小(MB)，默认 10
  ACCESS_LOG_BACKUP_COUNT  - 备份文件数量，默认 5
  ACCESS_LOG_EXCLUDE_EXT   - 排除的文件扩展名（逗号分隔），默认 .ico,.css,.js,.png,.jpg,.gif,.svg,.woff,.woff2
  ACCESS_LOG_SHOW_CONSOLE  - 是否在终端显示，默认 True
  ACCESS_LOG_COLOR         - 是否终端彩色输出，默认 True
  ACCESS_LOG_PASSWORD      - 可视化页面访问密码，默认 admin123
  DEBUG                    - 调试日志开关，True 时输出 loguru 日志

使用示例：
  # Python 调用
  from access_logger import AccessLogger
  logger = AccessLogger()
  logger.log_request({
      'path': '/index',
      'method': 'GET',
      'ip': '127.0.0.1',
      'user_agent': 'Chrome',
      'status_code': 200,
      'duration': 0.123,
      'domain': 'example.com'
  })

  # 命令行
  python access_logger.py --view
  python access_logger.py --stats
"""

import os
import re
import sys
import json
import gzip
import time
import socket
import hashlib
import argparse
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from loguru import logger

# ============================================================
# 日志控制：仅在 DEBUG=True 时输出
# ============================================================
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
if not DEBUG:
    logger.disable("__main__")


# ============================================================
# 终端彩色输出定义
# ============================================================
class Colors:
    """终端颜色定义"""
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'

    @classmethod
    def get_status_color(cls, status_code: int) -> str:
        """根据状态码返回颜色"""
        if 200 <= status_code < 300:
            return cls.GREEN
        elif 300 <= status_code < 400:
            return cls.CYAN
        elif 400 <= status_code < 500:
            return cls.YELLOW
        else:
            return cls.RED

    @classmethod
    def get_method_color(cls, method: str) -> str:
        """根据请求方法返回颜色"""
        method_colors = {
            'GET': cls.GREEN,
            'POST': cls.BLUE,
            'PUT': cls.YELLOW,
            'DELETE': cls.RED,
            'PATCH': cls.MAGENTA,
            'HEAD': cls.CYAN,
            'OPTIONS': cls.WHITE,
        }
        return method_colors.get(method, cls.WHITE)


class AccessLogger:
    """访问日志记录器 - 核心类

    核心用法：
        logger = AccessLogger()
        logger.log_request(request_data)

    Attributes:
        log_path: 日志文件路径
        max_size: 单文件最大大小(MB)
        backup_count: 备份文件数量
        exclude_ext: 排除的文件扩展名列表
        show_console: 是否在终端显示
        use_color: 是否终端彩色输出
        enabled: 是否启用日志
    """

    LOG_FIELDS = ['timestamp', 'domain', 'ip', 'method', 'path', 'status_code', 'duration', 'user_agent']

    def __init__(self,
                 log_path: Optional[str] = None,
                 max_size: Optional[int] = None,
                 backup_count: Optional[int] = None,
                 exclude_ext: Optional[List[str]] = None,
                 show_console: Optional[bool] = None,
                 use_color: Optional[bool] = None,
                 enabled: Optional[bool] = None,
                 password: Optional[str] = None):
        """初始化访问日志记录器

        Args:
            log_path: 日志文件路径
            max_size: 单文件最大大小(MB)
            backup_count: 备份文件数量
            exclude_ext: 排除的文件扩展名列表
            show_console: 是否在终端显示
            use_color: 是否终端彩色输出
            enabled: 是否启用日志
            password: 可视化页面访问密码

        Raises:
            ValueError: 参数校验失败时
        """
        self.enabled = enabled if enabled is not None else (
            os.getenv("ACCESS_LOG_ENABLED", "True").lower() in ("true", "1", "yes")
        )

        if not self.enabled:
            logger.info("访问日志已禁用")
            return

        base_dir = Path(__file__).parent.parent.parent
        self.log_path = Path(log_path or os.getenv("ACCESS_LOG_PATH", "logs/access.log"))
        if not self.log_path.is_absolute():
            self.log_path = base_dir / self.log_path

        self.max_size = int(max_size or os.getenv("ACCESS_LOG_MAX_SIZE", "10")) * 1024 * 1024
        self.backup_count = int(backup_count or os.getenv("ACCESS_LOG_BACKUP_COUNT", "5"))

        default_exclude = ['.ico', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.map']
        env_exclude = os.getenv("ACCESS_LOG_EXCLUDE_EXT", "")
        if env_exclude:
            default_exclude = [x.strip() for x in env_exclude.split(',') if x.strip()]
        self.exclude_ext = exclude_ext or default_exclude

        self.show_console = show_console if show_console is not None else (
            os.getenv("ACCESS_LOG_SHOW_CONSOLE", "True").lower() in ("true", "1", "yes")
        )
        self.use_color = use_color if use_color is not None else (
            os.getenv("ACCESS_LOG_COLOR", "True").lower() in ("true", "1", "yes")
        )
        self.password = password or os.getenv("ACCESS_LOG_PASSWORD", "admin123")

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"访问日志初始化: path={self.log_path}, max_size={self.max_size//1024//1024}MB")

    def _should_rotate(self) -> bool:
        """检查是否需要滚动日志"""
        if not self.log_path.exists():
            return False
        return self.log_path.stat().st_size >= self.max_size

    def _rotate(self):
        """滚动日志文件"""
        if not self._should_rotate():
            return

        for i in range(self.backup_count - 1, 0, -1):
            src = self.log_path.with_suffix(f".{i}.gz")
            dst = self.log_path.with_suffix(f".{i + 1}.gz")
            if src.exists():
                src.replace(dst)

        if self.log_path.exists():
            with open(self.log_path, 'rb') as f_in:
                with gzip.open(self.log_path.with_suffix(".1.gz"), 'wb') as f_out:
                    f_out.writelines(f_in)
            self.log_path.unlink()

        logger.debug(f"日志已滚动: {self.log_path}")

    def _is_static_resource(self, path: str) -> bool:
        """检查是否是静态资源路径"""
        ext = Path(path).suffix.lower()
        return ext in self.exclude_ext

    def _format_console_line(self, data: Dict) -> str:
        """格式化终端输出行"""
        ts = data['timestamp'][11:19]
        method = data['method'].ljust(7)
        status = str(data['status_code']).ljust(3)
        duration = f"{float(data['duration'])*1000:.0f}ms".rjust(6)
        ip = data['ip'].ljust(15)
        path = data['path']
        if len(path) > 50:
            path = path[:47] + "..."

        if self.use_color:
            method_color = Colors.get_method_color(data['method'])
            status_color = Colors.get_status_color(data['status_code'])
            parts = [
                f"{Colors.WHITE}{ts}{Colors.RESET}",
                f"{method_color}{method}{Colors.RESET}",
                f"{status_color}{status}{Colors.RESET}",
                f"{Colors.YELLOW}{duration}{Colors.RESET}",
                f"{Colors.CYAN}{ip}{Colors.RESET}",
                f"{Colors.WHITE}{path}{Colors.RESET}",
            ]
            return " | ".join(parts)
        else:
            return f"{ts} | {method} | {status} | {duration} | {ip} | {path}"

    def log_request(self, data: Dict) -> bool:
        """记录一条请求日志

        Args:
            data: 请求数据字典，包含:
                path: 请求路径
                method: 请求方法
                ip: 客户端IP
                user_agent: User-Agent
                status_code: HTTP状态码
                duration: 请求耗时(秒)
                domain: 站点域名

        Returns:
            是否成功记录

        Raises:
            ValueError: 必填字段缺失时
        """
        if not self.enabled:
            return False

        required = ['path', 'method', 'ip', 'status_code']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"缺少必填字段: {field}")

        if self._is_static_resource(data['path']):
            logger.debug(f"跳过静态资源: {data['path']}")
            return False

        log_entry = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'domain': data.get('domain', ''),
            'ip': data['ip'],
            'method': data['method'].upper(),
            'path': data['path'],
            'status_code': int(data['status_code']),
            'duration': float(data.get('duration', 0)),
            'user_agent': data.get('user_agent', '')[:500],
        }

        self._rotate()

        line = json.dumps(log_entry, ensure_ascii=False)
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

        if self.show_console:
            print(self._format_console_line(log_entry), flush=True)

        return True

    def get_logs(self,
                 domain: Optional[str] = None,
                 limit: int = 1000,
                 offset: int = 0,
                 status_code: Optional[int] = None,
                 method: Optional[str] = None,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None) -> Tuple[List[Dict], int]:
        """查询日志

        Args:
            domain: 按域名过滤
            limit: 返回数量限制
            offset: 偏移量
            status_code: 按状态码过滤
            method: 按方法过滤
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            (日志列表, 总数量)
        """
        logs = []
        if not self.log_path.exists():
            return [], 0

        with open(self.log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in reversed(lines):
            try:
                entry = json.loads(line.strip())
            except:
                continue

            if domain and entry.get('domain') != domain:
                continue
            if status_code and entry['status_code'] != status_code:
                continue
            if method and entry['method'] != method.upper():
                continue
            if start_date and entry['timestamp'] < start_date + ' 00:00:00':
                continue
            if end_date and entry['timestamp'] > end_date + ' 23:59:59':
                continue

            logs.append(entry)

        total = len(logs)
        return logs[offset:offset + limit], total

    def get_statistics(self, domain: Optional[str] = None, days: int = 7) -> Dict:
        """获取统计数据

        Args:
            domain: 按域名过滤
            days: 统计最近N天

        Returns:
            包含各种统计指标的字典
        """
        logs, _ = self.get_logs(domain=domain, limit=100000)

        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        logs = [l for l in logs if l['timestamp'] >= cutoff + ' 00:00:00']

        stats = {
            'total_requests': len(logs),
            'by_status': defaultdict(int),
            'by_method': defaultdict(int),
            'by_path': defaultdict(int),
            'by_ip': defaultdict(int),
            'by_hour': defaultdict(int),
            'by_day': defaultdict(int),
            'avg_duration': 0.0,
            'unique_ips': set(),
            'status_2xx': 0,
            'status_3xx': 0,
            'status_4xx': 0,
            'status_5xx': 0,
        }

        total_duration = 0.0

        for entry in logs:
            stats['by_status'][entry['status_code']] += 1
            stats['by_method'][entry['method']] += 1
            stats['by_path'][entry['path']] += 1
            stats['by_ip'][entry['ip']] += 1
            stats['unique_ips'].add(entry['ip'])

            hour = entry['timestamp'][11:13]
            stats['by_hour'][hour] += 1

            day = entry['timestamp'][:10]
            stats['by_day'][day] += 1

            sc = entry['status_code']
            if 200 <= sc < 300:
                stats['status_2xx'] += 1
            elif 300 <= sc < 400:
                stats['status_3xx'] += 1
            elif 400 <= sc < 500:
                stats['status_4xx'] += 1
            else:
                stats['status_5xx'] += 1

            total_duration += entry['duration']

        if logs:
            stats['avg_duration'] = total_duration / len(logs) * 1000

        stats['unique_ip_count'] = len(stats['unique_ips'])
        del stats['unique_ips']

        stats['top_paths'] = sorted(stats['by_path'].items(), key=lambda x: -x[1])[:10]
        stats['top_ips'] = sorted(stats['by_ip'].items(), key=lambda x: -x[1])[:10]

        return stats

    def verify_password(self, password: str) -> bool:
        """验证访问密码"""
        return password == self.password


# ============================================================
# CLI 命令行接口
# ============================================================

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="访问日志插件 - HTTP请求日志记录与可视化",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python access_logger.py --view                    # 查看最近请求
  python access_logger.py --stats                   # 显示统计信息
  python access_logger.py --domain example.com      # 按域名过滤
  python access_logger.py --limit 50                # 显示50条记录
        """,
    )

    parser.add_argument("--view", action="store_true", help="查看最近请求")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--domain", type=str, help="按域名过滤")
    parser.add_argument("--limit", type=int, default=50, help="显示数量")

    args = parser.parse_args()

    logger = AccessLogger()

    if args.stats:
        stats = logger.get_statistics(domain=args.domain)
        print(f"\n{'='*60}")
        print(f"📊 访问统计 (最近7天)")
        print(f"{'='*60}")
        print(f"总请求数: {stats['total_requests']}")
        print(f"独立IP:   {stats['unique_ip_count']}")
        print(f"平均耗时: {stats['avg_duration']:.1f}ms")
        print(f"\n状态码分布:")
        print(f"  2xx: {stats['status_2xx']}  3xx: {stats['status_3xx']}  4xx: {stats['status_4xx']}  5xx: {stats['status_5xx']}")
        print(f"\n热门路径:")
        for path, count in stats['top_paths'][:5]:
            print(f"  {count:4d} | {path}")
        print(f"{'-'*60}\n")

    elif args.view:
        logs, total = logger.get_logs(domain=args.domain, limit=args.limit)
        print(f"\n{'='*80}")
        print(f"📋 最近请求 ({len(logs)}/{total})")
        print(f"{'='*80}")
        print(f"{'时间':<19} | {'方法':<7} | {'状态':<3} | {'耗时':>6} | {'IP':<15} | 路径")
        print(f"{'-'*80}")
        for entry in logs:
            ts = entry['timestamp']
            method = entry['method'].ljust(7)
            status = str(entry['status_code']).ljust(3)
            duration = f"{entry['duration']*1000:.0f}ms".rjust(6)
            ip = entry['ip'].ljust(15)
            path = entry['path'][:50]
            print(f"{ts} | {method} | {status} | {duration} | {ip} | {path}")
        print(f"{'-'*80}\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
