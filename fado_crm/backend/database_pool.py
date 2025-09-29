# -*- coding: utf-8 -*-
"""
FADO CRM - Database Connection Pooling and Caching
Enhanced database performance with connection pooling and query caching
"""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

# Redis có thể không sẵn trong môi trường test
try:
    import redis  # type: ignore

    REDIS_AVAILABLE = True
except Exception:
    redis = None  # type: ignore
    REDIS_AVAILABLE = False
import hashlib
import json
import logging
import time
from functools import wraps
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DatabasePoolManager:
    """Enhanced database manager with connection pooling"""

    def __init__(self):
        # Align default with backend/database.py to avoid using two different SQLite files
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./fado_crm.db")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.enable_cache = os.getenv("ENABLE_QUERY_CACHE", "true").lower() == "true"

        # Connection pool settings
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))

        self._engine = None
        self._session_local = None
        self._redis_client = None

    @property
    def engine(self):
        """Get database engine with connection pooling"""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    @property
    def SessionLocal(self):
        """Get session factory"""
        if self._session_local is None:
            self._session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return self._session_local

    @property
    def redis_client(self):
        """Get Redis client for caching"""
        if self._redis_client is None and self.enable_cache and REDIS_AVAILABLE:
            try:
                self._redis_client = redis.from_url(self.redis_url, decode_responses=True)  # type: ignore
                # Test connection
                self._redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, caching disabled")
                self.enable_cache = False
                self._redis_client = None
        elif not REDIS_AVAILABLE:
            # Nếu redis library không có, tắt cache
            if self.enable_cache:
                logger.info("Redis library not available; disabling query cache")
            self.enable_cache = False
            self._redis_client = None
        return self._redis_client

    def _create_engine(self):
        """Create database engine with optimized settings"""
        if self.database_url.startswith("sqlite"):
            # SQLite optimizations
            engine = create_engine(
                self.database_url,
                poolclass=StaticPool,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=os.getenv("SQL_ECHO", "false").lower() == "true",
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20,
                    # SQLite performance settings
                    "isolation_level": None,  # autocommit mode
                },
            )
        else:
            # PostgreSQL optimizations
            engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            )

        # Add performance monitoring
        self._setup_engine_events(engine)
        return engine

    def _setup_engine_events(self, engine):
        """Setup engine events for performance monitoring"""

        @event.listens_for(engine, "before_cursor_execute")
        def receive_before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            context._query_start_time = time.time()

        @event.listens_for(engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - context._query_start_time
            if total > 0.1:  # Log slow queries (>100ms)
                logger.warning(f"Slow query ({total:.3f}s): {statement[:100]}...")

    def get_db_session(self):
        """Get database session with proper cleanup"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Global pool manager instance
pool_manager = DatabasePoolManager()


# Enhanced database dependency
def get_db():
    """Database dependency with connection pooling"""
    return next(pool_manager.get_db_session())


class QueryCache:
    """Query result caching system"""

    def __init__(self, redis_client=None, default_ttl=300):
        self.redis_client = redis_client or pool_manager.redis_client
        self.default_ttl = default_ttl
        self.enabled = self.redis_client is not None

    def _generate_cache_key(self, query: str, params: dict = None) -> str:
        """Generate cache key from query and parameters"""
        cache_data = {"query": query, "params": params or {}}
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"query_cache:{hashlib.md5(cache_str.encode()).hexdigest()}"

    def get(self, query: str, params: dict = None) -> Optional[Any]:
        """Get cached query result"""
        if not self.enabled:
            return None

        try:
            cache_key = self._generate_cache_key(query, params)
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")

        return None

    def set(self, query: str, result: Any, params: dict = None, ttl: int = None):
        """Cache query result"""
        if not self.enabled:
            return

        try:
            cache_key = self._generate_cache_key(query, params)
            ttl = ttl or self.default_ttl

            # Serialize result
            serialized_result = json.dumps(result, default=str)
            self.redis_client.setex(cache_key, ttl, serialized_result)

        except Exception as e:
            logger.warning(f"Cache set error: {e}")

    def invalidate_pattern(self, pattern: str):
        """Invalidate cache keys by pattern"""
        if not self.enabled:
            return

        try:
            keys = self.redis_client.keys(f"query_cache:*{pattern}*")
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for pattern: {pattern}")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")


# Global cache instance
query_cache = QueryCache()


def cached_query(ttl: int = 300, cache_key_params: list = None):
    """Decorator for caching query results"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and specified parameters
            cache_params = {}
            if cache_key_params:
                for param in cache_key_params:
                    if param in kwargs:
                        cache_params[param] = kwargs[param]

            query_signature = f"{func.__name__}:{json.dumps(cache_params, sort_keys=True)}"

            # Try to get from cache
            cached_result = query_cache.get(query_signature)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            query_cache.set(query_signature, result, cache_params, ttl)
            logger.debug(f"Cached result for {func.__name__}")

            return result

        return wrapper

    return decorator


class DatabasePerformanceMonitor:
    """Monitor database performance metrics"""

    def __init__(self):
        self.redis_client = pool_manager.redis_client
        self.metrics_key = "db_performance_metrics"

    def record_query_time(self, query_type: str, execution_time: float):
        """Record query execution time"""
        if not self.redis_client:
            return

        try:
            metric_key = f"{self.metrics_key}:{query_type}"

            # Store in Redis sorted set with timestamp as score
            timestamp = time.time()
            self.redis_client.zadd(metric_key, {execution_time: timestamp})

            # Keep only last 1000 entries
            self.redis_client.zremrangebyrank(metric_key, 0, -1001)

        except Exception as e:
            logger.warning(f"Performance monitoring error: {e}")

    def get_performance_stats(self, query_type: str = None) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.redis_client:
            return {}

        try:
            if query_type:
                metric_keys = [f"{self.metrics_key}:{query_type}"]
            else:
                # Get all query types
                pattern = f"{self.metrics_key}:*"
                metric_keys = self.redis_client.keys(pattern)

            stats = {}
            for key in metric_keys:
                query_type = key.split(":")[-1] if ":" in key else "unknown"
                execution_times = [float(x) for x in self.redis_client.zrange(key, 0, -1)]

                if execution_times:
                    stats[query_type] = {
                        "count": len(execution_times),
                        "avg_time": sum(execution_times) / len(execution_times),
                        "min_time": min(execution_times),
                        "max_time": max(execution_times),
                        "total_time": sum(execution_times),
                    }

            return stats

        except Exception as e:
            logger.warning(f"Performance stats error: {e}")
            return {}


# Global performance monitor
performance_monitor = DatabasePerformanceMonitor()


# Optimized query functions
def get_dashboard_stats_optimized(db):
    """Optimized dashboard statistics query"""

    @cached_query(ttl=60, cache_key_params=[])  # Cache for 1 minute
    def _get_stats():
        from sqlalchemy import text

        # Single optimized query using indexes
        query = text(
            """
            SELECT
                (SELECT COUNT(*) FROM khach_hang) as total_customers,
                (SELECT COUNT(*) FROM don_hang) as total_orders,
                (SELECT COUNT(*) FROM khach_hang WHERE ngay_tao >= date('now', '-30 days')) as new_customers_month,
                (SELECT COUNT(*) FROM don_hang WHERE trang_thai = 'cho_xac_nhan') as pending_orders,
                (SELECT COALESCE(SUM(tong_tien), 0) FROM don_hang
                 WHERE trang_thai != 'huy' AND strftime('%Y-%m', ngay_tao) = strftime('%Y-%m', 'now')) as revenue_month
        """
        )

        start_time = time.time()
        result = db.execute(query).fetchone()
        execution_time = time.time() - start_time

        performance_monitor.record_query_time("dashboard_stats", execution_time)

        return {
            "tong_khach_hang": result[0],
            "tong_don_hang": result[1],
            "khach_moi_thang": result[2],
            "don_cho_xu_ly": result[3],
            "doanh_thu_thang": result[4],
        }

    return _get_stats()


def get_customers_optimized(
    db, skip: int = 0, limit: int = 100, search: str = None, loai_khach: str = None
):
    """Optimized customer listing with search and filtering"""
    from sqlalchemy import text

    # Build dynamic query with proper indexing
    conditions = ["1=1"]
    params = {"skip": skip, "limit": limit}

    if search:
        conditions.append("(ho_ten LIKE :search OR email LIKE :search)")
        params["search"] = f"%{search}%"

    if loai_khach:
        conditions.append("loai_khach = :loai_khach")
        params["loai_khach"] = loai_khach

    where_clause = " AND ".join(conditions)

    query = text(
        f"""
        SELECT * FROM khach_hang
        WHERE {where_clause}
        ORDER BY ngay_tao DESC
        LIMIT :limit OFFSET :skip
    """
    )

    start_time = time.time()
    result = db.execute(query, params).fetchall()
    execution_time = time.time() - start_time

    performance_monitor.record_query_time("get_customers", execution_time)

    return result


# Export optimized database components
__all__ = [
    "pool_manager",
    "get_db",
    "query_cache",
    "cached_query",
    "performance_monitor",
    "get_dashboard_stats_optimized",
    "get_customers_optimized",
]
