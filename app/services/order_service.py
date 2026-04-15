from app.repositories.order_repo import fetch_orders, create_order


def get_orders_list():
    rows = fetch_orders()
    return [dict(row) for row in rows]


def create_purchase_order(supplier_id: str, product_name: str, quantity: int, lead_time: int, transport_mode: str):
    return create_order(supplier_id, product_name, quantity, lead_time, transport_mode)