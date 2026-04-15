from app.database import get_db


def fetch_suppliers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Suppliers ORDER BY Reliability_Score DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def fetch_supplier_by_id(supplier_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Suppliers WHERE SupplierID = ?", (supplier_id,))
    row = cursor.fetchone()
    conn.close()
    return row