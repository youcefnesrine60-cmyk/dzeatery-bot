from app.handlers.callbacks.owner.router import register_owner_routes
from app.handlers.callbacks.owner.owner_dashboard_routes import register_owner_dashboard_routes

__all__ = [
    "register_owner_routes",
    "register_owner_dashboard_routes",
]