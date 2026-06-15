from datetime import date

from fastapi import APIRouter, Depends, Query

from app.dependencies.roles import admin_only
from app.domain.reports.dependencies import get_report_service
from app.domain.reports.report_service import ReportService
from app.models.user import User


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sales")
def sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_sales_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/sales/orders")
def sales_orders_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_sales_orders_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/products")
def products_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    category_id: int | None = Query(None),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_products_report(
        restaurant_id=user.restaurant_id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )


@router.get("/products/{product_id}/evolution")
def product_evolution_report(
    product_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    user: User = Depends(admin_only),
    service: ReportService = Depends(get_report_service)
):
    return service.get_product_evolution_report(
        restaurant_id=user.restaurant_id,
        product_id=product_id,
        start_date=start_date,
        end_date=end_date
    )
