from app.repositories.supplier_repo import fetch_suppliers, fetch_supplier_by_id


def get_suppliers_list():
    rows = fetch_suppliers()
    return [dict(row) for row in rows]


def get_supplier(supplier_id: str):
    row = fetch_supplier_by_id(supplier_id)
    if row is None:
        raise ValueError("Supplier not found.")
    return dict(row)