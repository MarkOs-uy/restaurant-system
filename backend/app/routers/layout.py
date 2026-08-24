"""
Endpoints para la gestión de la layout del restaurant.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status,
    File,
    UploadFile
)

from app.dependencies.roles import (
    waiter_or_admin, 
    admin_only
)

from app.domain.layout.dependencies import get_layout_service
from app.domain.layout.layout_service import LayoutService

from app.models.user import User

from app.schemas.layout import(
    LayoutOut,
    LayoutUpdate
)

router = APIRouter(prefix="/layout", tags=["layout"])

# ----------------------------------------------------------------------------------------------------
# Subir imagen de fondo
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/background",
    response_model=LayoutOut,
    status_code=status.HTTP_200_OK,
    summary="Aplicar background",
    description="Aplica un background al diseño del restaurant a partir de una imagen cargada desde disco."
)
async def upload_background(
    file: UploadFile = File(..., description="Carga el archivo seleccionado."),
    user: User = Depends(admin_only),
    service: LayoutService = Depends(get_layout_service)
):
    return await service.update_background_image(user.restaurant_id, file)

# ----------------------------------------------------------------------------------------------------
# Obtener el diseño del restaurant
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=LayoutOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener diseño del restaurant",
    description="Obtiene el diseño del restaurant: tamaño, background, grid y snap_to_grid."
)
def get_layout(
    user: User = Depends(waiter_or_admin),
    service: LayoutService = Depends(get_layout_service)
):
    return service.get_layout(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Actualizar el diseño del restaurant
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/",
    response_model=LayoutOut,
    status_code=status.HTTP_200_OK,
    summary="Actualizar diseño del restaurant",
    description="Actualiza el diseño del restaurant: tamaño, background, grid y snap_to_grid."
)
def update_layout(
    data: LayoutUpdate,
    user: User = Depends(admin_only),
    service: LayoutService = Depends(get_layout_service)
):
    return service.update_layout(user.restaurant_id, data)