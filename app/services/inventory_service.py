from app.repositories.inventory_repo import fetch_inventory, add_stock, remove_stock
from app.repositories.movement_repo import create_movement


def get_inventory_list():
    rows = fetch_inventory()
    return [dict(row) for row in rows]


def inbound_stock(product_name: str, quantity: int):
    add_stock(product_name, quantity)
    create_movement(product_name, quantity, "IN")
    return {
        "message": "Stok başarıyla artırıldı.",
        "product_name": product_name,
        "quantity": quantity,
        "operation": "IN",
    }


def outbound_stock(product_name: str, quantity: int):
    remove_stock(product_name, quantity)
    create_movement(product_name, quantity, "OUT")
    return {
        "message": "Stok başarıyla azaltıldı.",
        "product_name": product_name,
        "quantity": quantity,
        "operation": "OUT",
    }