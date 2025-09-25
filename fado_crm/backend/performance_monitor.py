# -*- coding: utf-8 -*-
"""
Performance Monitoring and APM (Application Performance Monitoring)
Giám sát hiệu suất hệ thống real-time cho FADO CRM
"""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import threading
from collections import defaultdict, deque
import statistics

# Optional monitoring dependencies
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from database import get_db
from logging_config import app_logger


class PerformanceMonitor:
    """Class giám sát hiệu suất hệ thống"""

    def __init__(self):
        self.start_time = time.time()
        self.metrics_history = defaultdict(lambda: deque(maxlen=100))
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'api_response_time': 2.0,
            'error_rate': 5.0,
            'active_connections': 1000
        }
        self.active_requests = 0
        self.request_times = deque(maxlen=1000)
        self.error_count = 0
        self.total_requests = 0

        # Prometheus metrics (nếu có)
        if PROMETHEUS_AVAILABLE:
            self._init_prometheus_metrics()

        app_logger.info("🔍 Performance Monitor initialized")

    def _init_prometheus_metrics(self):
        """Khởi tạo Prometheus metrics"""
        self.request_count = Counter(
            'fado_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )

        self.request_duration = Histogram(
            'fado_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )

        self.active_connections_gauge = Gauge(
            'fado_active_connections',
            'Currently active connections'
        )

        self.system_cpu_usage = Gauge(
            'fado_system_cpu_usage_percent',
            'System CPU usage percentage'
        )

        self.system_memory_usage = Gauge(
            'fado_system_memory_usage_percent',
            'System memory usage percentage'
        )

        self.database_connections = Gauge(
            'fado_database_connections',
            'Active database connections'
        )

    def start_request_monitoring(self, method: str, endpoint: str):
        """🚀 Bắt đầu monitor request"""
        self.active_requests += 1
        self.total_requests += 1

        if PROMETHEUS_AVAILABLE:
            self.active_connections_gauge.set(self.active_requests)

        return {
            'start_time': time.time(),
            'method': method,
            'endpoint': endpoint
        }

    def end_request_monitoring(self, request_context: Dict, status_code: int):
        """⏹️ Kết thúc monitor request"""
        self.active_requests = max(0, self.active_requests - 1)
        duration = time.time() - request_context['start_time']
        self.request_times.append(duration)

        if status_code >= 400:
            self.error_count += 1

        # Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.request_count.labels(
                method=request_context['method'],
                endpoint=request_context['endpoint'],
                status_code=str(status_code)
            ).inc()

            self.request_duration.labels(
                method=request_context['method'],
                endpoint=request_context['endpoint']
            ).observe(duration)

            self.active_connections_gauge.set(self.active_requests)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """📊 Thu thập metrics hệ thống"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100

            # Network stats
            network = psutil.net_io_counters()

            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory_percent,
                    'memory_available': memory.available,
                    'memory_total': memory.total,
                    'disk_usage': disk_percent,
                    'disk_free': disk.free,
                    'disk_total': disk.total
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': {
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads()
                },
                'application': {
                    'active_requests': self.active_requests,
                    'total_requests': self.total_requests,
                    'error_count': self.error_count,
                    'error_rate': (self.error_count / max(1, self.total_requests)) * 100,
                    'avg_response_time': statistics.mean(self.request_times) if self.request_times else 0,
                    'uptime_seconds': time.time() - self.start_time
                }
            }

            # Store in history
            self.metrics_history['cpu_usage'].append(cpu_percent)
            self.metrics_history['memory_usage'].append(memory_percent)
            self.metrics_history['disk_usage'].append(disk_percent)
            self.metrics_history['error_rate'].append(metrics['application']['error_rate'])

            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                self.system_cpu_usage.set(cpu_percent)
                self.system_memory_usage.set(memory_percent)

            return metrics

        except Exception as e:
            app_logger.error(f"❌ Error collecting system metrics: {str(e)}")
            return {"error": f"Lỗi khi thu thập metrics: {str(e)}"}

    def check_alert_conditions(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """⚠️ Kiểm tra điều kiện cảnh báo"""
        alerts = []

        try:
            system = metrics.get('system', {})
            app = metrics.get('application', {})

            # CPU alert
            if system.get('cpu_usage', 0) > self.alert_thresholds['cpu_usage']:
                alerts.append({
                    'type': 'cpu_high',
                    'severity': 'warning',
                    'message': f"CPU usage cao: {system['cpu_usage']:.1f}%",
                    'current_value': system['cpu_usage'],
                    'threshold': self.alert_thresholds['cpu_usage'],
                    'timestamp': datetime.now().isoformat()
                })

            # Memory alert
            if system.get('memory_usage', 0) > self.alert_thresholds['memory_usage']:
                alerts.append({
                    'type': 'memory_high',
                    'severity': 'warning',
                    'message': f"Memory usage cao: {system['memory_usage']:.1f}%",
                    'current_value': system['memory_usage'],
                    'threshold': self.alert_thresholds['memory_usage'],
                    'timestamp': datetime.now().isoformat()
                })

            # Error rate alert
            if app.get('error_rate', 0) > self.alert_thresholds['error_rate']:
                alerts.append({
                    'type': 'error_rate_high',
                    'severity': 'critical',
                    'message': f"Tỷ lệ lỗi cao: {app['error_rate']:.1f}%",
                    'current_value': app['error_rate'],
                    'threshold': self.alert_thresholds['error_rate'],
                    'timestamp': datetime.now().isoformat()
                })

            # Response time alert
            if app.get('avg_response_time', 0) > self.alert_thresholds['api_response_time']:
                alerts.append({
                    'type': 'response_time_high',
                    'severity': 'warning',
                    'message': f"Thời gian phản hồi chậm: {app['avg_response_time']:.2f}s",
                    'current_value': app['avg_response_time'],
                    'threshold': self.alert_thresholds['api_response_time'],
                    'timestamp': datetime.now().isoformat()
                })

        except Exception as e:
            app_logger.error(f"❌ Error checking alert conditions: {str(e)}")

        return alerts

    def get_database_metrics(self, db: Session) -> Dict[str, Any]:
        """🗄️ Thu thập metrics database"""
        try:
            # Query performance metrics
            slow_queries = db.execute(text("""
                SELECT
                    'customers' as table_name,
                    COUNT(*) as row_count
                FROM customers
                UNION ALL
                SELECT 'products', COUNT(*) FROM products
                UNION ALL
                SELECT 'orders', COUNT(*) FROM orders
                UNION ALL
                SELECT 'contact_history', COUNT(*) FROM contact_history
            """)).fetchall()

            table_stats = {row.table_name: row.row_count for row in slow_queries}

            # Recent activity
            recent_orders = db.execute(text("""
                SELECT COUNT(*) as recent_orders
                FROM orders
                WHERE order_date >= DATE('now', '-1 hour')
            """)).scalar()

            recent_customers = db.execute(text("""
                SELECT COUNT(*) as recent_customers
                FROM customers
                WHERE created_at >= DATE('now', '-1 hour')
            """)).scalar()

            return {
                'table_statistics': table_stats,
                'recent_activity': {
                    'orders_last_hour': recent_orders or 0,
                    'customers_last_hour': recent_customers or 0
                },
                'connection_info': {
                    'pool_size': 'SQLite (No pool)',
                    'active_connections': 1
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            app_logger.error(f"❌ Error collecting database metrics: {str(e)}")
            return {"error": f"Lỗi khi thu thập database metrics: {str(e)}"}

    def generate_health_report(self, db: Session) -> Dict[str, Any]:
        """🏥 Tạo báo cáo sức khỏe tổng thể"""
        system_metrics = self.collect_system_metrics()
        db_metrics = self.get_database_metrics(db)
        alerts = self.check_alert_conditions(system_metrics)

        # Tính health score
        health_score = self._calculate_health_score(system_metrics, alerts)

        return {
            'overall_health': {
                'status': self._get_health_status(health_score),
                'score': health_score,
                'timestamp': datetime.now().isoformat()
            },
            'system_metrics': system_metrics,
            'database_metrics': db_metrics,
            'active_alerts': alerts,
            'performance_trends': {
                'cpu_trend': list(self.metrics_history['cpu_usage'])[-10:],
                'memory_trend': list(self.metrics_history['memory_usage'])[-10:],
                'error_rate_trend': list(self.metrics_history['error_rate'])[-10:]
            },
            'uptime': time.time() - self.start_time
        }

    def _calculate_health_score(self, metrics: Dict[str, Any], alerts: List[Dict]) -> float:
        """Tính điểm sức khỏe hệ thống (0-100)"""
        score = 100.0

        try:
            system = metrics.get('system', {})
            app = metrics.get('application', {})

            # Deduct points based on system metrics
            score -= min(30, system.get('cpu_usage', 0) / 3)  # Max -30 points
            score -= min(25, system.get('memory_usage', 0) / 4)  # Max -25 points
            score -= min(20, app.get('error_rate', 0) * 2)  # Max -20 points

            # Deduct points for critical alerts
            critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
            score -= len(critical_alerts) * 10

            # Deduct points for warning alerts
            warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
            score -= len(warning_alerts) * 5

            return max(0, min(100, score))

        except Exception:
            return 50  # Default moderate score if calculation fails

    def _get_health_status(self, score: float) -> str:
        """Chuyển đổi điểm thành trạng thái"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "fair"
        elif score >= 25:
            return "poor"
        else:
            return "critical"

    def get_prometheus_metrics(self) -> str:
        """📈 Trả về Prometheus metrics format"""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus not available\n"

        return generate_latest()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware:
    """Middleware để monitor performance của các requests"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Start monitoring
            method = scope["method"]
            path = scope["path"]
            request_context = performance_monitor.start_request_monitoring(method, path)

            # Wrap send to capture status code
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    performance_monitor.end_request_monitoring(request_context, status_code)
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


def get_performance_monitor() -> PerformanceMonitor:
    """Factory function để lấy performance monitor instance"""
    return performance_monitor


# Async background task để monitor liên tục
async def continuous_monitoring():
    """🔄 Task chạy nền để monitor liên tục"""
    while True:
        try:
            # Thu thập metrics
            db = next(get_db())
            metrics = performance_monitor.collect_system_metrics()
            alerts = performance_monitor.check_alert_conditions(metrics)

            # Gửi alerts nếu có
            if alerts:
                from websocket_service import notify_performance_alert
                for alert in alerts:
                    await notify_performance_alert(
                        "system",
                        alert['type'],
                        alert['current_value'],
                        alert['threshold'],
                        alert['severity']
                    )

            await asyncio.sleep(60)  # Check every minute

        except Exception as e:
            app_logger.error(f"❌ Error in continuous monitoring: {str(e)}")
            await asyncio.sleep(60)