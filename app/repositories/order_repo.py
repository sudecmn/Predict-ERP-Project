from datetime import datetime
from app.database import get_db


def fetch_orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Purchase_Orders ORDER BY CreatedAt DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_order(supplier_id: str, product_name: str, quantity: int, lead_time: int, transport_mode: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM Purchase_Orders")
    count = cursor.fetchone()["count"] + 1
    order_id = f"PO_{count:03d}"
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO Purchase_Orders
        (OrderID, SupplierID, ProductName, Quantity, LeadTime, TransportMode, Status, CreatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (order_id, supplier_id, product_name, quantity, lead_time, transport_mode, "pending", created_at)
    )

    conn.commit()
    conn.close()

    return {
        "OrderID": order_id,
        "SupplierID": supplier_id,
        "ProductName": product_name,
        "Quantity": quantity,
        "LeadTime": lead_time,
        "TransportMode": transport_mode,
        "Status": "pending",
        "CreatedAt": created_at,
    }