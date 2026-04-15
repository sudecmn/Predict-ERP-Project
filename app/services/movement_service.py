from app.repositories.movement_repo import fetch_movements


def get_movements_list():
    rows = fetch_movements()
    return [dict(row) for row in rows]