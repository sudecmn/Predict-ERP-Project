from fastapi import APIRouter, HTTPException
from app.models.schemas import InboundRequest, OutboundRequest
from app.services.inventory_service import get_inventory_list, inbound_stock, outbound_stock

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/")
def list_inventory():
    return get_inventory_list()


@router.post("/inbound")
def create_inbound(req: InboundRequest):
    try:
        return inbound_stock(req.product_name, req.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/outbound")
def create_outbound(req: OutboundRequest):
    try:
        return outbound_stock(req.product_name, req.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))