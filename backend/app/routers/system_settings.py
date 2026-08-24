"""
Endpoints para la gestión de la configuración del sistema.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import admin_only

from app.domain.settings.dependencies import get_settings_service

from app.domain.settings.settings_service import SettingsService

from app.models.user import User

from app.schemas.system_settings import (
    SettingsUpdateRequest,
    SettingsResponse,
    EmailTestResponse
)

router = APIRouter(prefix="/settings", tags=["settings"])

# ----------------------------------------------------------------------------------------------------
# Testear correo electrónico configurado
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/test-email",
    response_model=EmailTestResponse,
    status_code=status.HTTP_200_OK,
    summary="Testear el e-mail",
    description="Testea el correo electrónico configurado enviando un correo de prueba.")
def test_email(
    user: User = Depends(admin_only),
    service: SettingsService = Depends(get_settings_service)
):
    return service.send_test_email(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Obtener settings del sistema
# ----------------------------------------------------------------------------------------------------
@router.get(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener settings",
    description="Obtiene las settings del sistema."
)
def get_settings(
    user: User = Depends(admin_only),
    service: SettingsService = Depends(get_settings_service)
):
    settings = service.get_settings(user.restaurant_id)
    return service.to_response(settings)

# ----------------------------------------------------------------------------------------------------
# Actualizar settings del sistema
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar settings",
    description="Actualiza settings del sistema.")
def update_settings(
    data: SettingsUpdateRequest,
    user: User = Depends(admin_only),
    service: SettingsService = Depends(get_settings_service)
):
    settings = service.update_settings(user.restaurant_id, data)
    return service.to_response(settings)