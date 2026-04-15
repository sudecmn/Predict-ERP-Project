from fastapi import APIRouter
from app.services.movement_service import get_movements_list

router = APIRouter(prefix="/movements", tags=["Movements"])


@router.get("/")
def list_movements():
    return get_movements_list()