import pandas as pd
import sqlite3
from datetime import datetime

# --- SUPPLIERS ---
suppliers = [
    ('SUP_001', 'Asya', 'Tayvan', 75, 88, 1.0, 1.8),
    ('SUP_002', 'Avrupa', 'Almanya', 15, 95, 1.4, 0.8),
    ('SUP_003', 'İç_Pazar', 'Türkiye', 25, 82, 0.9, 0.5),
    ('SUP_004', 'Asya', 'Çin', 65, 70, 0.7, 2.0),
    ('SUP_005', 'Amerika', 'ABD', 20, 90, 1.5, 1.2)
]

df_suppliers = pd.DataFrame(
    suppliers,
    columns=[
        'SupplierID',
        'Region',
        'Country',
        'Country_Risk_Index',
        'Reliability_Score',
        'Base_Cost_Multiplier',
        'Carbon_Footprint_Multiplier'
    ]
)

# --- INVENTORY ---
inventory = [
    ('PRD_001', 'Endüstriyel Çip Seti', 9000),
    ('PRD_002', 'Lityum İyon Batarya Blok', 370),
    ('PRD_003', 'Alüminyum Kasa Paneli', 1550),
    ('PRD_004', 'Fiber Optik Konnektör', 2200),
    ('PRD_005', 'Sensör Modülü', 830)
]

df_inventory = pd.DataFrame(
    inventory,
    columns=['ProductID', 'ProductName', 'StockLevel']
)

# --- PURCHASE ORDERS ---
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

purchase_orders = [
    ('PO_001', 'SUP_001', 'Endüstriyel Çip Seti', 500, 14, 'DenizYolu', 'received', now),
    ('PO_002', 'SUP_002', 'Lityum İyon Batarya Blok', 200, 10, 'KaraYolu', 'pending', now),
    ('PO_003', 'SUP_003', 'Alüminyum Kasa Paneli', 300, 7, 'KaraYolu', 'received', now)
]

df_purchase_orders = pd.DataFrame(
    purchase_orders,
    columns=[
        'OrderID',
        'SupplierID',
        'ProductName',
        'Quantity',
        'LeadTime',
        'TransportMode',
        'Status',
        'CreatedAt'
    ]
)

# --- STOCK MOVEMENTS ---
stock_movements = [
    (1, 'Endüstriyel Çip Seti', 500, 'IN', now),
    (2, 'Alüminyum Kasa Paneli', 300, 'IN', now),
    (3, 'Lityum İyon Batarya Blok', 50, 'OUT', now)
]

df_stock_movements = pd.DataFrame(
    stock_movements,
    columns=[
        'MovementID',
        'ProductName',
        'Quantity',
        'MovementType',
        'CreatedAt'
    ]
)

# --- DB SAVE ---
conn = sqlite3.connect('erp_cognitive_supply.db')

df_suppliers.to_sql('Suppliers', conn, if_exists='replace', index=False)
df_inventory.to_sql('Inventory', conn, if_exists='replace', index=False)
df_purchase_orders.to_sql('Purchase_Orders', conn, if_exists='replace', index=False)
df_stock_movements.to_sql('Stock_Movements', conn, if_exists='replace', index=False)

conn.close()

print("Veritabanı başarıyla oluşturuldu.")
print("Tablolar: Suppliers, Inventory, Purchase_Orders, Stock_Movements")