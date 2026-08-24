"""
Endpoints para la gestión de reportes.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""
from datetime import date

from fastapi import (
    APIRouter, 
    Depends, 
    status,
    Query
)

from app.dependencies.roles import admin_only

from app.domain.reports.dependencies import get_report_service
from app.domain.reports.report_service import ReportService

from app.models.user import User

from app.schemas.reports import (
    ProductEvolutionReportOut,
    SalesOrdersReportOut,
    ProductsReportOut,
    SalesReportOut
)

router = APIRouter(prefix="/reports", tags=["reports"])

# ----------------------------------------------------------------------------------------------------
# Reporte de Ventas
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/sales",
    response_model=SalesReportOut,
    status_code=status.HTTP_200_OK,
    summary="Reporte de ventas",
    description="Reporte conteniendo la evolución de las ventas en un período determinado.")
def sales_report(
    start_date: date = Query(..., description="Fecha inicial del reporte."),
    end_date: date = Query(..., description="Fecha final del reporte."),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_sales_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date
    )

# ----------------------------------------------------------------------------------------------------
# Reporte de ventas por orden
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/sales/orders",
    response_model=SalesOrdersReportOut,
    status_code=status.HTTP_200_OK,
    summary="Reporte de ventas por orden",
    description="Reporte con listado de ventas realizadas en un período determinado."
)
def sales_orders_report(
    start_date: date = Query(..., description="Fecha inicial del reporte."),
    end_date: date = Query(..., description="Fecha final del reporte."),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_sales_orders_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date
    )

# ----------------------------------------------------------------------------------------------------
# Reporte de productos más y menos vendidos
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/products",
    response_model=ProductsReportOut,
    status_code=status.HTTP_200_OK,
    summary="Reporte de productos más y menos vendidos",
    description="Reporte conteniendo el top 10 de los productos más y menos vendidos en un período determinado."
)
def products_report(
    start_date: date = Query(..., description="Fecha inicial del reporte."),
    end_date: date = Query(..., description="Fecha final del reporte."),
    category_id: int | None = Query(None, description="Filtrar por categoría."),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_products_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )

# ----------------------------------------------------------------------------------------------------
# Reporte de evolución de productos
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/products/{product_id}/evolution",
    response_model=ProductEvolutionReportOut,
    status_code=status.HTTP_200_OK,
    summary="Reporte de evolución de las ventas de un producto",
    description="Reporte conteniendo la evolución de las ventas de un producto seleccionado en un período determinado."
)
def product_evolution_report(
    product_id: int,
    start_date: date = Query(..., description="Fecha inicial del reporte."),
    end_date: date = Query(..., description="Fecha final del reporte."),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_product_evolution_report(
        restaurant_id=user.restaurant_id,
        product_id=product_id,
        start_date=start_date,
        end_date=end_date
    )