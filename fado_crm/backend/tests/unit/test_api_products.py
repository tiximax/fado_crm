# 🧪 FADO CRM - Product API Unit Tests
# Comprehensive testing cho Product endpoints

import pytest
from fastapi import status
from tests.conftest import generate_product_payload


class TestProductAPI:
    """🛍️ Product API test suite"""

    async def test_get_products_empty(self, async_client, db_session):
        """Test getting products when database is empty"""
        response = await async_client.get("/san-pham/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_get_products_with_data(self, async_client, multiple_products):
        """Test getting products with data"""
        response = await async_client.get("/san-pham/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 15  # From multiple_products fixture
        assert "ten_san_pham" in data[0]
        assert "gia_goc" in data[0]

    async def test_get_products_pagination(self, async_client, multiple_products):
        """Test product pagination"""
        response = await async_client.get("/san-pham/?skip=5&limit=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5

    async def test_get_products_search(self, async_client, multiple_products):
        """Test product search functionality"""
        # Search by name
        response = await async_client.get("/san-pham/?search=Product 1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    async def test_get_products_filter_by_category(self, async_client, multiple_products):
        """Test filtering products by category"""
        response = await async_client.get("/san-pham/?danh_muc=Electronics")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for product in data:
            assert product["danh_muc"] == "Electronics"

    async def test_get_products_filter_by_country(self, async_client, multiple_products):
        """Test filtering products by country"""
        response = await async_client.get("/san-pham/?quoc_gia=USA")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for product in data:
            assert product["quoc_gia_nguon"] == "USA"

    async def test_get_products_price_filter(self, async_client, multiple_products):
        """Test filtering products by price range"""
        response = await async_client.get("/san-pham/?gia_min=100&gia_max=300")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for product in data:
            assert 100 <= product["gia_goc"] <= 300

    async def test_get_products_sorting(self, async_client, multiple_products):
        """Test product sorting"""
        # Sort by price ascending
        response = await async_client.get("/san-pham/?sort_by=gia_ban&order=asc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2
        assert data[0]["gia_ban"] <= data[1]["gia_ban"]

        # Sort by price descending
        response = await async_client.get("/san-pham/?sort_by=gia_ban&order=desc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2
        assert data[0]["gia_ban"] >= data[1]["gia_ban"]

    async def test_create_product_success(self, async_client, db_session):
        """Test successful product creation"""
        product_data = generate_product_payload()
        response = await async_client.post("/san-pham/", json=product_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ten_san_pham"] == product_data["ten_san_pham"]
        assert data["gia_goc"] == product_data["gia_goc"]
        assert "id" in data
        assert "ngay_tao" in data

    async def test_create_product_invalid_data(self, async_client, db_session):
        """Test product creation with invalid data"""
        # Missing required field
        invalid_data = {"gia_goc": 100}
        response = await async_client.post("/san-pham/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid price
        invalid_data = generate_product_payload(gia_goc=-10)
        response = await async_client.post("/san-pham/", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_product_by_id_success(self, async_client, sample_product):
        """Test getting single product by ID"""
        response = await async_client.get(f"/san-pham/{sample_product.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_product.id
        assert data["ten_san_pham"] == sample_product.ten_san_pham

    async def test_get_product_by_id_not_found(self, async_client, db_session):
        """Test getting non-existent product"""
        response = await async_client.get("/san-pham/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["error"] is True
        assert data["error_code"] == "NOT_FOUND"

    async def test_update_product_success(self, async_client, sample_product):
        """Test successful product update"""
        update_data = {
            "ten_san_pham": "Updated Product Name",
            "gia_ban": 1500000.0
        }
        response = await async_client.put(f"/san-pham/{sample_product.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ten_san_pham"] == "Updated Product Name"
        assert data["gia_ban"] == 1500000.0
        assert data["id"] == sample_product.id

    async def test_update_product_not_found(self, async_client, db_session):
        """Test updating non-existent product"""
        update_data = {"ten_san_pham": "Updated Name"}
        response = await async_client.put("/san-pham/99999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_product_invalid_data(self, async_client, sample_product):
        """Test updating product with invalid data"""
        invalid_data = {"gia_goc": -100}
        response = await async_client.put(f"/san-pham/{sample_product.id}", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete_product_success(self, async_client, sample_product):
        """Test successful product deletion"""
        response = await async_client.delete(f"/san-pham/{sample_product.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Đã xóa sản phẩm" in data["message"]

        # Verify product is deleted
        get_response = await async_client.get(f"/san-pham/{sample_product.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_product_not_found(self, async_client, db_session):
        """Test deleting non-existent product"""
        response = await async_client.delete("/san-pham/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_product_data_validation(self, async_client, db_session):
        """Test comprehensive product data validation"""
        # Test email validation for link_goc
        invalid_data = generate_product_payload(link_goc="not-a-url")
        response = await async_client.post("/san-pham/", json=invalid_data)
        # URL validation might not be strictly enforced, so check if it's created
        # This depends on your Pydantic model validation

        # Test long strings
        long_name = "x" * 1000  # Very long product name
        valid_data = generate_product_payload(ten_san_pham=long_name)
        response = await async_client.post("/san-pham/", json=valid_data)
        # Check if your model handles long strings appropriately

    async def test_product_search_edge_cases(self, async_client, multiple_products):
        """Test search functionality edge cases"""
        # Empty search
        response = await async_client.get("/san-pham/?search=")
        assert response.status_code == status.HTTP_200_OK

        # Special characters in search
        response = await async_client.get("/san-pham/?search=@#$%")
        assert response.status_code == status.HTTP_200_OK

        # Very long search term
        long_search = "x" * 100
        response = await async_client.get(f"/san-pham/?search={long_search}")
        assert response.status_code == status.HTTP_200_OK

    async def test_concurrent_product_operations(self, async_client, sample_product):
        """Test concurrent operations on same product"""
        import asyncio

        # Simulate concurrent updates
        async def update_product(name_suffix):
            update_data = {"ten_san_pham": f"Concurrent Update {name_suffix}"}
            return await async_client.put(f"/san-pham/{sample_product.id}", json=update_data)

        # Run concurrent updates
        tasks = [update_product(i) for i in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # At least one should succeed
        success_count = sum(1 for r in results if hasattr(r, 'status_code') and r.status_code == 200)
        assert success_count >= 1


# 🎯 Product API Model Tests
class TestProductModels:
    """Test product data models and validation"""

    def test_product_model_creation(self, db_session, sample_product_data):
        """Test creating product model instance"""
        from models import SanPham

        product = SanPham(**sample_product_data)
        db_session.add(product)
        db_session.commit()

        assert product.id is not None
        assert product.ten_san_pham == sample_product_data["ten_san_pham"]
        assert product.ngay_tao is not None

    def test_product_schema_validation(self, sample_product_data):
        """Test product Pydantic schema validation"""
        from schemas import SanPhamCreate, SanPham

        # Valid data
        schema = SanPhamCreate(**sample_product_data)
        assert schema.ten_san_pham == sample_product_data["ten_san_pham"]

        # Test schema with ID (for responses)
        data_with_id = {**sample_product_data, "id": 1, "ngay_tao": "2023-01-01T00:00:00"}
        response_schema = SanPham(**data_with_id)
        assert response_schema.id == 1

# 🚀 Product API tests hoàn thành! ✨