from fastapi import APIRouter, HTTPException
from app.services.supplier_service import get_suppliers_list, get_supplier

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("/")
def list_suppliers():
    return get_suppliers_list()


@router.get("/{supplier_id}")
def supplier_detail(supplier_id: str):
    try:
        return get_supplier(supplier_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))