from datetime import datetime
from app.database import get_db


def fetch_movements():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Stock_Movements ORDER BY CreatedAt DESC, MovementID DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_movement(product_name: str, quantity: int, movement_type: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(MAX(MovementID), 0) as max_id FROM Stock_Movements")
    next_id = cursor.fetchone()["max_id"] + 1
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO Stock_Movements (MovementID, ProductName, Quantity, MovementType, CreatedAt)
        VALUES (?, ?, ?, ?, ?)
        """,
        (next_id, product_name, quantity, movement_type, created_at)
    )

    conn.commit()
    conn.close()

    return {
        "MovementID": next_id,
        "ProductName": product_name,
        "Quantity": quantity,
        "MovementType": movement_type,
        "CreatedAt": created_at,
    }