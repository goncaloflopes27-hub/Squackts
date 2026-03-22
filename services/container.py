from __future__ import annotations

from repositories.client_repo import ClientRepository
from repositories.log_repo import LogRepository
from repositories.order_repo import OrderRepository
from repositories.product_repo import ProductRepository
from repositories.settings_repo import SettingsRepository
from services.client_service import ClientService
from services.dashboard_service import DashboardService
from services.order_service import OrderService
from services.production_service import ProductionService
from services.product_service import ProductService
from services.system_service import SystemService


def build_services() -> dict:
    repos = {
        "clients": ClientRepository(),
        "products": ProductRepository(),
        "orders": OrderRepository(),
        "logs": LogRepository(),
        "settings": SettingsRepository(),
    }
    product_service = ProductService(repos["products"], repos["logs"])
    client_service = ClientService(repos["clients"], repos["logs"])
    order_service = OrderService(repos["orders"], repos["products"], repos["settings"], repos["logs"])
    production_service = ProductionService(repos["orders"])
    dashboard_service = DashboardService()
    system_service = SystemService(repos["logs"])
    return {
        "product_service": product_service,
        "client_service": client_service,
        "order_service": order_service,
        "production_service": production_service,
        "dashboard_service": dashboard_service,
        "system_service": system_service,
    }
