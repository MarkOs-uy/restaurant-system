"""
Endpoints para la gestión de backups.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import admin_only

from app.domain.backup.backup_service import BackupService
from app.domain.backup.dependencies import get_backup_service

from app.models.user import User

from app.schemas.backup import BackupEmailRequest

router = APIRouter(prefix="/backups", tags=["backups"])

# ----------------------------------------------------------------------------------------------------
# Crear un backup
# ----------------------------------------------------------------------------------------------------
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crea un backup",
    description="Crea un backup manual."
)
def create_backup(
    user: User = Depends(admin_only),
    service: BackupService = Depends(
        get_backup_service
    )
):
    return service.create_backup(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Crea un backup y lo envía por correo electrónico
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/email",
    status_code=status.HTTP_201_CREATED,
    summary="Crear backup y enviar por e-mail",
    description="Crea un backup y lo envía por e-mail al e-mail configurado."
)
def create_and_email_backup(
    data: BackupEmailRequest,
    user: User = Depends(admin_only),
    service: BackupService = Depends(
        get_backup_service
    )
):
    return service.create_and_email_backup(data.email, user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Restaura un backup
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/restore/{filename:path}",
    status_code=status.HTTP_201_CREATED,
    summary="Restaurar un backup existente",
    description="Restaura un backup existente a partir del archivo seleccionado."
)
def restore_backup(
    filename: str,
    user: User = Depends(admin_only),
    service: BackupService = Depends(get_backup_service)
):
    return service.restore_backup(
        restaurant_id=user.restaurant_id,
        filename=filename
    )

# ----------------------------------------------------------------------------------------------------
# Obtiene el status de un backup
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Obtener el status del backup",
    description="Obtiene el status del backup seleccionado."
)
def backup_status(
    user: User = Depends(admin_only),
    service: BackupService = Depends(
        get_backup_service
    )
):
    return service.status(
        user.restaurant_id
    )

# ----------------------------------------------------------------------------------------------------
# Obtiene un listado de los backups
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/files",
    status_code=status.HTTP_200_OK,
    summary="Listado de backups",
    description="Obtiene un listado de todos los backups del restaurant autenticado."
)
def list_backups(
    user: User = Depends(admin_only),
    service: BackupService = Depends(get_backup_service)
):
    return service.list_backups(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Descarga un backup a un dispositivo de almacenamiento
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/download/{filename:path}",
    status_code=status.HTTP_200_OK,
    summary="Descargar backup",
    description="Descarga un backup a un dispositivo de almacenamiento."
)
def download_backup(
    filename: str,
    user: User = Depends(admin_only),
    service: BackupService = Depends(get_backup_service)
):
    return service.download_backup(
        restaurant_id=user.restaurant_id,
        filename=filename
    )

# ----------------------------------------------------------------------------------------------------
# Elimina un backup
# ----------------------------------------------------------------------------------------------------
@router.delete(
    "/{filename:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina un backup",
    description="Elimina el backup seleccionado."
)
def delete_backup(
    filename: str,
    user: User = Depends(admin_only),
    service: BackupService = Depends(get_backup_service)
):
    service.delete_backup(
        restaurant_id=user.restaurant_id,
        filename=filename
    )