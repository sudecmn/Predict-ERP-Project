from app.database import get_db


def get_dashboard_summary():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(StockLevel), 0) AS total_stock FROM Inventory")
    total_stock = cursor.fetchone()["total_stock"]

    cursor.execute("SELECT COUNT(*) AS supplier_count FROM Suppliers")
    active_suppliers = cursor.fetchone()["supplier_count"]

    cursor.execute("SELECT COALESCE(AVG(Country_Risk_Index), 0) AS avg_risk FROM Suppliers")
    average_country_risk = cursor.fetchone()["avg_risk"]

    cursor.execute("SELECT COUNT(*) AS critical_count FROM Inventory WHERE StockLevel < 250")
    critical_stock_count = cursor.fetchone()["critical_count"]

    conn.close()

    return {
        "total_stock": total_stock,
        "active_suppliers": active_suppliers,
        "average_country_risk": round(float(average_country_risk), 2),
        "critical_stock_count": critical_stock_count,
    }