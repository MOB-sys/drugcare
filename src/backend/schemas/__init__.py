"""API 스키마 모듈 — 요청/응답 Pydantic 모델."""

from src.backend.schemas.cabinet import (
    CabinetItemCreate,
    CabinetItemResponse,
)
from src.backend.schemas.common import (
    ApiResponse,
    HealthStatus,
    MetaInfo,
    PaginatedData,
)
from src.backend.schemas.drug import (
    DrugDetail,
    DrugSearchItem,
    IngredientInfo,
)
from src.backend.schemas.food import (
    FoodDetail,
    FoodSearchItem,
    FoodSearchResponse,
)
from src.backend.schemas.herbal_medicine import (
    HerbalMedicineDetail,
    HerbalMedicineSearchItem,
    HerbalMedicineSearchResponse,
)
from src.backend.schemas.interaction import (
    InteractionCheckRequest,
    InteractionCheckResponse,
    InteractionItem,
    InteractionResult,
)
from src.backend.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate,
)
from src.backend.schemas.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewSummary,
)
from src.backend.schemas.supplement import (
    SupplementDetail,
    SupplementSearchItem,
)

__all__ = [
    "ApiResponse",
    "CabinetItemCreate",
    "CabinetItemResponse",
    "DrugDetail",
    "DrugSearchItem",
    "FoodDetail",
    "FoodSearchItem",
    "FoodSearchResponse",
    "HerbalMedicineDetail",
    "HerbalMedicineSearchItem",
    "HerbalMedicineSearchResponse",
    "HealthStatus",
    "IngredientInfo",
    "InteractionCheckRequest",
    "InteractionCheckResponse",
    "InteractionItem",
    "InteractionResult",
    "MetaInfo",
    "PaginatedData",
    "ReminderCreate",
    "ReminderResponse",
    "ReminderUpdate",
    "ReviewCreate",
    "ReviewResponse",
    "ReviewSummary",
    "SupplementDetail",
    "SupplementSearchItem",
]
