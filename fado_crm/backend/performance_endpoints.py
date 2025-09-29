# -*- coding: utf-8 -*-
"""
FADO CRM - Database Performance Monitoring Endpoints
Real-time database performance monitoring and optimization
"""

import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

# psutil có thể không có trong môi trường test
try:
    import psutil  # type: ignore

    PSUTIL_AVAILABLE = True
except Exception:
    PSUTIL_AVAILABLE = False
import os

from backend.database_pool import (
    get_dashboard_stats_optimized,
    performance_monitor,
    pool_manager,
    query_cache,
)

# Import phụ thuộc có thể không sẵn ở môi trường test → fallback an toàn
try:
    from backend.database import get_db
except Exception:  # pragma: no cover - fallback cho môi trường test tối thiểu
    get_db = None  # type: ignore

try:
    from backend.auth import get_admin_user
except Exception:  # pragma: no cover
    from fastapi import HTTPException

    def get_admin_user():  # type: ignore
        raise HTTPException(status_code=401, detail="Admin auth not available")


try:
    from backend.models import NguoiDung
except Exception:  # pragma: no cover

    class NguoiDung:  # type: ignore
        pass


router = APIRouter(prefix="/performance", tags=["Performance Monitoring"])


@router.get("/database/stats")
async def get_database_performance_stats(
    current_user: NguoiDung = Depends(get_admin_user),
) -> Dict[str, Any]:
    """Get comprehensive database performance statistics"""

    try:
        # Get query performance stats
        query_stats = performance_monitor.get_performance_stats()

        # Get connection pool stats
        engine = pool_manager.engine
        pool_info = {
            "pool_size": getattr(engine.pool, "size", lambda: 0)(),
            "checked_in": getattr(engine.pool, "checkedin", lambda: 0)(),
            "checked_out": getattr(engine.pool, "checkedout", lambda: 0)(),
            "overflow": getattr(engine.pool, "overflow", lambda: 0)(),
        }

        # Get cache stats
        cache_stats = {}
        if query_cache.enabled:
            try:
                redis_info = query_cache.redis_client.info()
                cache_stats = {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory_human", "0B"),
                    "keyspace_hits": redis_info.get("keyspace_hits", 0),
                    "keyspace_misses": redis_info.get("keyspace_misses", 0),
                    "cache_hit_ratio": (
                        redis_info.get("keyspace_hits", 0)
                        / max(
                            redis_info.get("keyspace_hits", 0)
                            + redis_info.get("keyspace_misses", 0),
                            1,
                        )
                    )
                    * 100,
                }
            except Exception as e:
                cache_stats = {"error": str(e)}

        # System performance (nếu psutil không sẵn có, trả về thông tin tối thiểu)
        if PSUTIL_AVAILABLE:
            system_stats = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
            }
        else:
            system_stats = {
                "cpu_percent": None,
                "memory_percent": None,
                "disk_usage": None,
                "note": "psutil not available",
            }

        return {
            "query_performance": query_stats,
            "connection_pool": pool_info,
            "cache_stats": cache_stats,
            "system_performance": system_stats,
            "timestamp": time.time(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance stats error: {str(e)}")


@router.get("/database/slow-queries")
async def get_slow_queries(
    current_user: NguoiDung = Depends(get_admin_user), db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get slow query analysis"""

    try:
        # For SQLite, we'll simulate slow query detection
        # In production PostgreSQL, you'd query pg_stat_statements

        slow_queries = []

        # Test some common queries and measure performance
        test_queries = [
            {
                "name": "Dashboard Statistics",
                "query": "SELECT COUNT(*) FROM khach_hang",
                "type": "dashboard",
            },
            {
                "name": "Recent Orders",
                "query": "SELECT COUNT(*) FROM don_hang WHERE ngay_tao >= date('now', '-7 days')",
                "type": "orders",
            },
            {
                "name": "Active Products",
                "query": "SELECT COUNT(*) FROM san_pham WHERE is_active = 1",
                "type": "products",
            },
            {
                "name": "Customer Search",
                "query": "SELECT COUNT(*) FROM khach_hang WHERE ho_ten LIKE '%nguyen%'",
                "type": "search",
            },
        ]

        for test in test_queries:
            start_time = time.time()
            try:
                result = db.execute(text(test["query"]))
                result.fetchone()
                execution_time = time.time() - start_time

                slow_queries.append(
                    {
                        "query_name": test["name"],
                        "query_type": test["type"],
                        "execution_time_ms": round(execution_time * 1000, 2),
                        "is_slow": execution_time > 0.1,  # >100ms is considered slow
                        "query_text": (
                            test["query"][:100] + "..."
                            if len(test["query"]) > 100
                            else test["query"]
                        ),
                    }
                )
            except Exception as e:
                slow_queries.append(
                    {
                        "query_name": test["name"],
                        "query_type": test["type"],
                        "execution_time_ms": -1,
                        "is_slow": True,
                        "error": str(e),
                    }
                )

        return sorted(slow_queries, key=lambda x: x.get("execution_time_ms", 0), reverse=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slow query analysis error: {str(e)}")


@router.get("/database/indexes")
async def get_database_indexes(
    current_user: NguoiDung = Depends(get_admin_user), db: Session = Depends(get_db)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get database index information"""

    try:
        # Get all indexes grouped by table
        indexes_by_table = {}

        # Get all tables
        tables_result = db.execute(
            text(
                """
            SELECT name FROM sqlite_master WHERE type='table' ORDER BY name
        """
            )
        )
        tables = [row[0] for row in tables_result.fetchall()]

        for table in tables:
            # Get indexes for this table
            indexes_result = db.execute(text(f"PRAGMA index_list({table})"))
            indexes = []

            for idx_row in indexes_result.fetchall():
                idx_name = idx_row[1]
                is_unique = idx_row[2]

                # Get index columns
                columns_result = db.execute(text(f"PRAGMA index_info({idx_name})"))
                columns = [col[2] for col in columns_result.fetchall()]

                indexes.append(
                    {
                        "name": idx_name,
                        "columns": columns,
                        "is_unique": bool(is_unique),
                        "is_auto": idx_name.startswith("sqlite_autoindex_"),
                    }
                )

            indexes_by_table[table] = indexes

        return indexes_by_table

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index analysis error: {str(e)}")


@router.post("/cache/clear")
async def clear_query_cache(
    pattern: str = None, current_user: NguoiDung = Depends(get_admin_user)
) -> Dict[str, Any]:
    """Clear query cache (all or by pattern)"""

    try:
        if not query_cache.enabled:
            return {"message": "Cache not enabled", "cleared": 0}

        if pattern:
            # Clear specific pattern
            query_cache.invalidate_pattern(pattern)
            return {"message": f"Cache cleared for pattern: {pattern}", "pattern": pattern}
        else:
            # Clear all cache
            cache_keys = query_cache.redis_client.keys("query_cache:*")
            if cache_keys:
                query_cache.redis_client.delete(*cache_keys)
                cleared_count = len(cache_keys)
            else:
                cleared_count = 0

            return {"message": "All cache cleared", "cleared": cleared_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear error: {str(e)}")


@router.get("/database/optimize")
async def optimize_database(
    current_user: NguoiDung = Depends(get_admin_user), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Run database optimization tasks"""

    try:
        optimization_results = {}

        # 1. Update SQLite statistics
        start_time = time.time()
        db.execute(text("ANALYZE"))
        db.commit()
        optimization_results["analyze_time"] = time.time() - start_time

        # 2. Vacuum database (SQLite specific)
        try:
            start_time = time.time()
            db.execute(text("VACUUM"))
            optimization_results["vacuum_time"] = time.time() - start_time
        except Exception as e:
            optimization_results["vacuum_error"] = str(e)

        # 3. Check database integrity
        start_time = time.time()
        integrity_result = db.execute(text("PRAGMA integrity_check")).fetchone()
        optimization_results["integrity_check"] = {
            "status": integrity_result[0],
            "check_time": time.time() - start_time,
        }

        # 4. Get database size
        try:
            db_path = None
            engine = pool_manager.engine
            if str(engine.url).startswith("sqlite"):
                # Resolve actual SQLite file path from engine URL
                # engine.url.database returns the filesystem path for file-based SQLite
                db_path = engine.url.database

            if db_path and os.path.exists(db_path):
                db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
                optimization_results["database_size_mb"] = round(db_size_mb, 2)
        except Exception as e:
            optimization_results["size_error"] = str(e)

        return {
            "optimization_completed": True,
            "timestamp": time.time(),
            "results": optimization_results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database optimization error: {str(e)}")


@router.get("/health")
async def performance_health_check() -> Dict[str, Any]:
    """Quick performance health check (no auth required)"""

    try:
        health_status = {}

        # Database connection test
        try:
            engine = pool_manager.engine
            with engine.connect() as conn:
                start_time = time.time()
                conn.execute(text("SELECT 1"))
                db_response_time = time.time() - start_time
                health_status["database"] = {
                    "status": "healthy",
                    "response_time_ms": round(db_response_time * 1000, 2),
                }
        except Exception as e:
            health_status["database"] = {"status": "unhealthy", "error": str(e)}

        # Cache connection test
        if query_cache.enabled:
            try:
                start_time = time.time()
                query_cache.redis_client.ping()
                cache_response_time = time.time() - start_time
                health_status["cache"] = {
                    "status": "healthy",
                    "response_time_ms": round(cache_response_time * 1000, 2),
                }
            except Exception as e:
                health_status["cache"] = {"status": "unhealthy", "error": str(e)}
        else:
            health_status["cache"] = {"status": "disabled"}

        # Overall status
        overall_healthy = all(
            service.get("status") in ["healthy", "disabled"] for service in health_status.values()
        )

        return {
            "overall_status": "healthy" if overall_healthy else "degraded",
            "services": health_status,
            "timestamp": time.time(),
        }

    except Exception as e:
        return {"overall_status": "unhealthy", "error": str(e), "timestamp": time.time()}


@router.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    """Expose Prometheus metrics if available. Always returns text/plain."""
    try:
        from backend.performance_monitor import (
            performance_monitor as sys_performance_monitor,  # type: ignore
        )

        metrics_text = sys_performance_monitor.get_prometheus_metrics()
        return Response(content=metrics_text, media_type="text/plain; version=0.0.4")
    except Exception as e:
        # Graceful fallback if module or prometheus not available
        return Response(
            content=f"# metrics unavailable: {e}\n", media_type="text/plain; version=0.0.4"
        )
