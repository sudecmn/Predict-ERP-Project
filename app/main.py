from fastapi import FastAPI
from app.routers import inventory, suppliers, dashboard, ai, orders, movements

app = FastAPI(
    title="PredictERP API",
    description="Supply Chain ERP backend powered by FastAPI",
    version="1.0.0",
)

app.include_router(inventory.router)
app.include_router(suppliers.router)
app.include_router(dashboard.router)
app.include_router(ai.router)
app.include_router(orders.router)
app.include_router(movements.router)


@app.get("/")
def root():
    return {
        "message": "PredictERP API is running",
        "status": "ok"
    }