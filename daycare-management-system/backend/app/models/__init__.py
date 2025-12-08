# Models Package Initialization
# ============================================

from app.models.base import BaseModel
from app.models.user import User

# Import all models here so Alembic can detect them
# from app.models.child import Child
# from app.models.parent import Parent
# etc...

__all__ = [
    "BaseModel",
    "User",
]