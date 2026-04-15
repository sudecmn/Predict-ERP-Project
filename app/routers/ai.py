from fastapi import APIRouter, HTTPException
from app.models.schemas import RiskPredictionRequest
from app.services.ai_service import predict_order_risk

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/predict")
def predict_risk(req: RiskPredictionRequest):
    try:
        return predict_order_risk(
            supplier_id=req.supplier_id,
            quantity=req.quantity,
            lead_time=req.lead_time,
            transport_mode=req.transport_mode,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))