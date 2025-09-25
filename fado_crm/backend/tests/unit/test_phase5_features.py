# -*- coding: utf-8 -*-
"""
Unit tests for Phase 5 features
Testing Advanced Analytics, AI Recommendations, Export functionality, and Performance Monitoring
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Import the modules to test
from main import app
from analytics import AdvancedAnalytics, get_analytics_service
from ai_recommendations import AIRecommendationEngine, get_ai_recommendation_engine
from advanced_export import AdvancedExportService, get_advanced_export_service
from performance_monitor import PerformanceMonitor, get_performance_monitor

# Test client
client = TestClient(app)


class TestAdvancedAnalytics:
    """Test suite cho Advanced Analytics module"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = Mock(spec=Session)
        return session

    @pytest.fixture
    def analytics_service(self, mock_db_session):
        """Create analytics service instance"""
        return AdvancedAnalytics(mock_db_session)

    def test_customer_segmentation_analysis(self, analytics_service, mock_db_session):
        """Test RFM customer segmentation analysis"""
        # Mock database results
        mock_result = Mock()
        mock_result._mapping = {
            'customer_type': 'VIP',
            'customer_count': 10,
            'avg_recency_days': 15.0,
            'avg_frequency': 5.0,
            'avg_monetary_value': 1000000.0,
            'avg_order_value': 200000.0,
            'min_spending': 50000.0,
            'max_spending': 2000000.0
        }

        mock_db_session.execute.return_value.fetchall.return_value = [mock_result]

        # Run the analysis
        result = analytics_service.customer_segmentation_analysis()

        # Assertions
        assert 'rfm_analysis' in result
        assert 'lifecycle_analysis' in result
        assert 'generated_at' in result
        assert len(result['rfm_analysis']) > 0

    def test_sales_performance_analysis(self, analytics_service, mock_db_session):
        """Test sales performance analysis"""
        # Mock database results for different queries
        mock_daily_sales = Mock()
        mock_daily_sales._mapping = {
            'sale_date': '2024-01-01',
            'order_count': 5,
            'daily_revenue': 500000.0,
            'avg_order_value': 100000.0,
            'unique_customers': 3
        }

        mock_category_performance = Mock()
        mock_category_performance._mapping = {
            'category': 'Electronics',
            'orders_count': 10,
            'category_revenue': 1000000.0,
            'avg_order_value': 100000.0,
            'unique_customers': 5
        }

        mock_status_funnel = Mock()
        mock_status_funnel._mapping = {
            'order_status': 'Hoàn thành',
            'order_count': 8,
            'revenue': 800000.0,
            'percentage': 80.0
        }

        # Configure mock to return different results for different queries
        mock_db_session.execute.return_value.fetchall.side_effect = [
            [mock_daily_sales],
            [mock_category_performance],
            [mock_status_funnel]
        ]

        # Run analysis
        result = analytics_service.sales_performance_analysis(30)

        # Assertions
        assert 'daily_sales_trend' in result
        assert 'category_performance' in result
        assert 'order_status_funnel' in result
        assert 'analysis_period' in result
        assert result['analysis_period']['days'] == 30

    def test_generate_executive_summary(self, analytics_service, mock_db_session):
        """Test executive summary generation"""
        # Mock business metrics
        mock_metrics = Mock()
        mock_metrics._mapping = {
            'total_customers': 100,
            'total_products': 50,
            'total_orders': 200,
            'total_revenue': 10000000.0,
            'avg_order_value': 50000.0,
            'completed_orders': 180,
            'completion_rate': 90.0
        }

        mock_growth = Mock()
        mock_growth._mapping = {
            'month': '2024-01',
            'monthly_orders': 50,
            'monthly_revenue': 2500000.0,
            'active_customers': 30
        }

        mock_current = Mock()
        mock_current._mapping = {
            'current_month_orders': 25,
            'current_month_revenue': 1250000.0,
            'current_month_customers': 15
        }

        # Configure mock returns
        mock_db_session.execute.return_value.fetchone.side_effect = [
            mock_metrics, mock_current
        ]
        mock_db_session.execute.return_value.fetchall.return_value = [mock_growth]

        # Run summary
        result = analytics_service.generate_executive_summary()

        # Assertions
        assert 'business_metrics' in result
        assert 'growth_trends' in result
        assert 'current_month_performance' in result
        assert result['report_type'] == 'Executive Summary'


class TestAIRecommendations:
    """Test suite cho AI Recommendations Engine"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = Mock(spec=Session)
        return session

    @pytest.fixture
    def ai_engine(self, mock_db_session):
        """Create AI recommendation engine instance"""
        return AIRecommendationEngine(mock_db_session)

    def test_recommend_products_for_customer(self, ai_engine, mock_db_session):
        """Test product recommendations for customer"""
        # Mock customer query
        mock_customer = Mock()
        mock_customer.full_name = "Test Customer"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_customer

        # Mock customer orders history
        mock_order = Mock()
        mock_order.category = "Electronics"
        mock_order.origin_country = "USA"
        mock_order.frequency = 3
        mock_order.avg_spent = 500000.0
        mock_order.last_order = datetime.now()

        mock_db_session.execute.return_value.fetchall.return_value = [mock_order]

        # Run recommendations
        result = ai_engine.recommend_products_for_customer(1, 5)

        # Assertions
        assert 'customer_id' in result
        assert 'customer_name' in result
        assert 'recommendation_strategy' in result
        assert 'generated_at' in result

    def test_generate_business_insights(self, ai_engine, mock_db_session):
        """Test business insights generation"""
        # Mock various database queries for insights
        mock_category = Mock()
        mock_category.category = "Electronics"
        mock_category.recent_orders = 20
        mock_category.avg_order_value = 100000.0
        mock_category.unique_customers = 15

        mock_churn = Mock()
        mock_churn._mapping = {
            'customer_id': 1,
            'full_name': 'John Doe',
            'customer_type': 'VIP',
            'days_inactive': 70,
            'total_orders': 5,
            'lifetime_value': 1000000.0
        }

        # Configure different mock returns
        mock_db_session.execute.return_value.fetchall.side_effect = [
            [mock_category],  # category trends
            [mock_churn],     # churn risk
            [],               # upselling opportunities
            []                # slow products
        ]

        # Run insights generation
        result = ai_engine.generate_business_insights()

        # Assertions
        assert 'insights' in result
        assert 'total_insights' in result
        assert 'generated_at' in result
        assert isinstance(result['insights'], list)

    def test_cosine_similarity(self, ai_engine):
        """Test cosine similarity calculation"""
        vec1 = {'electronics_usa': 3, 'clothing_china': 1}
        vec2 = {'electronics_usa': 2, 'clothing_china': 2, 'books_uk': 1}

        similarity = ai_engine._cosine_similarity(vec1, vec2)

        # Assertions
        assert 0 <= similarity <= 1
        assert isinstance(similarity, float)


class TestAdvancedExport:
    """Test suite cho Advanced Export Service"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = Mock(spec=Session)
        return session

    @pytest.fixture
    def export_service(self, mock_db_session):
        """Create export service instance"""
        return AdvancedExportService(mock_db_session)

    @patch('advanced_export.PANDAS_AVAILABLE', False)
    def test_export_customers_excel_no_pandas(self, export_service):
        """Test Excel export when pandas not available"""
        result = export_service.export_customers_excel()

        assert 'error' in result
        assert 'Pandas library không khả dụng' in result['error']

    @patch('advanced_export.REPORTLAB_AVAILABLE', False)
    def test_generate_pdf_report_no_reportlab(self, export_service):
        """Test PDF generation when ReportLab not available"""
        result = export_service.generate_analytics_pdf_report()

        assert 'error' in result
        assert 'ReportLab library không khả dụng' in result['error']

    @patch('advanced_export.PANDAS_AVAILABLE', True)
    @patch('advanced_export.pd')
    def test_export_customers_excel_success(self, mock_pd, export_service, mock_db_session):
        """Test successful Excel export"""
        # Mock database results
        mock_result = Mock()
        mock_result._mapping = {
            'customer_id': 1,
            'full_name': 'Test Customer',
            'phone': '0123456789',
            'email': 'test@example.com',
            'address': 'Test Address',
            'customer_type': 'VIP',
            'created_at': datetime.now(),
            'total_orders': 5,
            'lifetime_value': 1000000,
            'last_order_date': datetime.now(),
            'total_contacts': 3
        }

        mock_db_session.execute.return_value.fetchall.return_value = [mock_result]

        # Mock pandas DataFrame
        mock_df = Mock()
        mock_df.empty = False
        mock_df.__len__ = Mock(return_value=1)
        mock_pd.DataFrame.return_value = mock_df

        # Mock Excel writer
        mock_writer = Mock()
        mock_writer.__enter__ = Mock(return_value=mock_writer)
        mock_writer.__exit__ = Mock(return_value=None)
        mock_pd.ExcelWriter.return_value = mock_writer

        with patch('io.BytesIO') as mock_bytesio, \
             patch('base64.b64encode') as mock_b64encode:

            mock_bytesio.return_value.read.return_value = b'fake_excel_data'
            mock_b64encode.return_value.decode.return_value = 'fake_base64_data'

            result = export_service.export_customers_excel()

            # Assertions
            assert 'success' in result
            assert result['success'] is True
            assert 'filename' in result
            assert 'data' in result


class TestPerformanceMonitor:
    """Test suite cho Performance Monitor"""

    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor instance"""
        return PerformanceMonitor()

    def test_start_request_monitoring(self, performance_monitor):
        """Test request monitoring start"""
        context = performance_monitor.start_request_monitoring("GET", "/test")

        assert 'start_time' in context
        assert context['method'] == "GET"
        assert context['endpoint'] == "/test"
        assert performance_monitor.active_requests == 1

    def test_end_request_monitoring(self, performance_monitor):
        """Test request monitoring end"""
        # Start a request first
        context = performance_monitor.start_request_monitoring("GET", "/test")
        initial_requests = performance_monitor.total_requests

        # End the request
        performance_monitor.end_request_monitoring(context, 200)

        assert performance_monitor.active_requests == 0
        assert performance_monitor.total_requests == initial_requests
        assert len(performance_monitor.request_times) > 0

    def test_check_alert_conditions(self, performance_monitor):
        """Test alert condition checking"""
        # Create metrics that should trigger alerts
        metrics = {
            'system': {
                'cpu_usage': 85.0,  # Above threshold (80%)
                'memory_usage': 90.0,  # Above threshold (85%)
            },
            'application': {
                'error_rate': 7.0,  # Above threshold (5%)
                'avg_response_time': 3.0  # Above threshold (2.0s)
            }
        }

        alerts = performance_monitor.check_alert_conditions(metrics)

        # Should have multiple alerts
        assert len(alerts) > 0
        alert_types = [alert['type'] for alert in alerts]
        assert 'cpu_high' in alert_types
        assert 'memory_high' in alert_types
        assert 'error_rate_high' in alert_types

    def test_calculate_health_score(self, performance_monitor):
        """Test health score calculation"""
        good_metrics = {
            'system': {
                'cpu_usage': 20.0,
                'memory_usage': 30.0
            },
            'application': {
                'error_rate': 1.0
            }
        }

        score = performance_monitor._calculate_health_score(good_metrics, [])

        # Should be high score for good metrics
        assert 80 <= score <= 100

        # Test with bad metrics
        bad_metrics = {
            'system': {
                'cpu_usage': 90.0,
                'memory_usage': 95.0
            },
            'application': {
                'error_rate': 10.0
            }
        }

        bad_score = performance_monitor._calculate_health_score(bad_metrics, [])

        # Should be lower score
        assert bad_score < score

    def test_health_status_mapping(self, performance_monitor):
        """Test health status mapping from score"""
        assert performance_monitor._get_health_status(95) == "excellent"
        assert performance_monitor._get_health_status(80) == "good"
        assert performance_monitor._get_health_status(60) == "fair"
        assert performance_monitor._get_health_status(30) == "poor"
        assert performance_monitor._get_health_status(10) == "critical"


class TestPhase5Integration:
    """Integration tests cho Phase 5 features"""

    def test_analytics_endpoints_require_auth(self):
        """Test that analytics endpoints require authentication"""
        # Test without auth
        response = client.get("/analytics/customer-segmentation")
        assert response.status_code == 401

        response = client.get("/analytics/executive-summary")
        assert response.status_code == 401

    def test_ai_endpoints_require_auth(self):
        """Test that AI endpoints require authentication"""
        response = client.get("/ai/recommend-products/1")
        assert response.status_code == 401

        response = client.get("/ai/business-insights")
        assert response.status_code == 401

    def test_export_endpoints_require_auth(self):
        """Test that export endpoints require authentication"""
        response = client.get("/export/customers-excel")
        assert response.status_code == 401

        response = client.get("/export/business-intelligence")
        assert response.status_code == 401

    def test_monitoring_endpoints_require_admin(self):
        """Test that monitoring endpoints require admin access"""
        response = client.get("/monitor/health")
        assert response.status_code == 401

        response = client.get("/monitor/metrics")
        assert response.status_code == 401

        response = client.get("/monitor/prometheus")
        assert response.status_code == 401

    def test_health_endpoint_exists(self):
        """Test that health endpoint is properly defined"""
        # This should return 401 (unauthorized) rather than 404 (not found)
        response = client.get("/monitor/health")
        assert response.status_code == 401
        # If endpoint didn't exist, would be 404

    @patch('advanced_export.PANDAS_AVAILABLE', True)
    @patch('advanced_export.REPORTLAB_AVAILABLE', True)
    def test_export_dependencies_check(self):
        """Test that export service properly checks dependencies"""
        from advanced_export import AdvancedExportService

        # Should not raise exception when dependencies available
        service = AdvancedExportService(Mock())
        assert service is not None


# Performance test helpers
class TestPerformanceHelpers:
    """Helper tests for performance measurement"""

    def test_timing_context_manager(self):
        """Test timing functionality works"""
        import time

        start_time = time.time()
        time.sleep(0.1)  # Sleep 100ms
        end_time = time.time()

        duration = end_time - start_time
        assert 0.09 <= duration <= 0.15  # Allow for timing variance

    def test_memory_measurement(self):
        """Test memory measurement functionality"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            assert hasattr(memory, 'percent')
            assert hasattr(memory, 'available')
            assert hasattr(memory, 'total')
            assert 0 <= memory.percent <= 100
        except ImportError:
            pytest.skip("psutil not available")


# Mock fixtures for database
@pytest.fixture
def mock_customer_data():
    """Mock customer data for testing"""
    return {
        'customer_id': 1,
        'full_name': 'Test Customer',
        'phone': '0123456789',
        'email': 'test@example.com',
        'customer_type': 'VIP'
    }

@pytest.fixture
def mock_product_data():
    """Mock product data for testing"""
    return {
        'product_id': 1,
        'product_name': 'Test Product',
        'category': 'Electronics',
        'origin_country': 'USA',
        'selling_price': 100000.0
    }

@pytest.fixture
def mock_order_data():
    """Mock order data for testing"""
    return {
        'order_id': 1,
        'customer_id': 1,
        'product_id': 1,
        'total_amount': 150000.0,
        'order_status': 'Hoàn thành',
        'order_date': datetime.now()
    }


# Utility functions for testing
def create_test_metrics():
    """Create sample metrics for testing"""
    return {
        'system': {
            'cpu_usage': 45.0,
            'memory_usage': 60.0,
            'disk_usage': 70.0
        },
        'application': {
            'active_requests': 5,
            'total_requests': 1000,
            'error_count': 10,
            'error_rate': 1.0,
            'avg_response_time': 0.5
        }
    }

def create_test_alerts():
    """Create sample alerts for testing"""
    return [
        {
            'type': 'cpu_high',
            'severity': 'warning',
            'message': 'CPU usage cao: 85.0%',
            'current_value': 85.0,
            'threshold': 80.0,
            'timestamp': datetime.now().isoformat()
        }
    ]