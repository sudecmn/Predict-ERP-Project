from pydantic import BaseModel, Field


class InventoryResponse(BaseModel):
    ProductID: str
    ProductName: str
    StockLevel: int


class SupplierResponse(BaseModel):
    SupplierID: str
    Region: str
    Country: str
    Country_Risk_Index: int
    Reliability_Score: int
    Base_Cost_Multiplier: float
    Carbon_Footprint_Multiplier: float


class InboundRequest(BaseModel):
    product_name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


class OutboundRequest(BaseModel):
    product_name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


class RiskPredictionRequest(BaseModel):
    supplier_id: str
    quantity: int = Field(..., gt=0)
    lead_time: int = Field(..., ge=1)
    transport_mode: str


class DashboardSummaryResponse(BaseModel):
    total_stock: int
    active_suppliers: int
    average_country_risk: float
    critical_stock_count: int
    
class PurchaseOrderCreateRequest(BaseModel):
    supplier_id: str
    product_name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    lead_time: int = Field(..., ge=1)
    transport_mode: str


class PurchaseOrderResponse(BaseModel):
    OrderID: str
    SupplierID: str
    ProductName: str
    Quantity: int
    LeadTime: int
    TransportMode: str
    Status: str
    CreatedAt: str


class StockMovementResponse(BaseModel):
    MovementID: int
    ProductName: str
    Quantity: int
    MovementType: str
    CreatedAt: str