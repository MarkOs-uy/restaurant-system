from fastapi import APIRouter, Depends

from app.schemas.layout import LayoutOut, LayoutUpdate
from app.dependencies.auth import get_current_user
from app.domain.layout.dependencies import get_layout_service
from app.domain.layout.layout_service import LayoutService
from app.models.user import User

router = APIRouter(prefix="/layout", tags=["layout"])


@router.get("/", response_model=LayoutOut)
def get_layout(
    user: User = Depends(get_current_user),
    service: LayoutService = Depends(get_layout_service)
):
    return service.get_layout(user.restaurant_id)


@router.patch("/", response_model=LayoutUpdate)
def update_layout(
    data: LayoutUpdate,
    user: User = Depends(get_current_user),
    service: LayoutService = Depends(get_layout_service)
):
    return service.update_layout(
        user.restaurant_id,
        data
    )