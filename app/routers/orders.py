from fastapi import APIRouter
from app.models.schemas import PurchaseOrderCreateRequest
from app.services.order_service import get_orders_list, create_purchase_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/")
def list_orders():
    return get_orders_list()


@router.post("/")
def create_order(req: PurchaseOrderCreateRequest):
    return create_purchase_order(
        supplier_id=req.supplier_id,
        product_name=req.product_name,
        quantity=req.quantity,
        lead_time=req.lead_time,
        transport_mode=req.transport_mode,
    )