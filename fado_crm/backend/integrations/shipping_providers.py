# 🚚 Shipping Providers Integration (Stub)
# Define interfaces for multiple providers (e.g., DHL, UPS, local VN providers)

import os
from typing import Dict, Any

class ShippingProvider:
    def create_label(self, order: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def track(self, tracking_number: str) -> Dict[str, Any]:
        raise NotImplementedError

class DummyShipping(ShippingProvider):
    def create_label(self, order: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "created",
            "provider": "dummy",
            "tracking_number": "DUMMY123456",
        }

    def track(self, tracking_number: str) -> Dict[str, Any]:
        return {
            "tracking_number": tracking_number,
            "status": "in_transit"
        }

PROVIDER = os.getenv("SHIPPING_PROVIDER", "dummy").lower()

def get_provider() -> ShippingProvider:
    # Later: switch on PROVIDER to real implementations
    return DummyShipping()
