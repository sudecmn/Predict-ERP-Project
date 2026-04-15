from app.database import get_db


def fetch_inventory():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Inventory ORDER BY ProductID")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_stock(product_name: str, quantity: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Inventory
        SET StockLevel = StockLevel + ?
        WHERE ProductName = ?
        """,
        (quantity, product_name),
    )

    if cursor.rowcount == 0:
        conn.close()
        raise ValueError("Ürün bulunamadı.")

    conn.commit()
    conn.close()


def remove_stock(product_name: str, quantity: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT StockLevel FROM Inventory WHERE ProductName = ?",
        (product_name,),
    )
    row = cursor.fetchone()

    if row is None:
        conn.close()
        raise ValueError("Ürün bulunamadı.")

    current_stock = row["StockLevel"]
    if quantity > current_stock:
        conn.close()
        raise ValueError("Yetersiz stok.")

    cursor.execute(
        """
        UPDATE Inventory
        SET StockLevel = StockLevel - ?
        WHERE ProductName = ?
        """,
        (quantity, product_name),
    )

    conn.commit()
    conn.close()