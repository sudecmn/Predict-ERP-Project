import os
import streamlit as st
import pandas as pd
import requests
import numpy as np

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
REQUEST_TIMEOUT = 10
st.set_page_config(
    page_title="PredictERP",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #F7F9FC; }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E6EAF0;
    }
    p, span, label { color: #2C3E50 !important; }
    h1, h2, h3 {
        color: #4A90E2 !important;
        font-weight: 600 !important;
    }
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E6EAF0;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
    }
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #4A90E2;
        color: #4A90E2 !important;
        transition: 0.3s;
        background-color: transparent;
    }
    .stButton > button:hover {
        background-color: #4A90E2 !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)



# SESSION STATE

if "success_messages" not in st.session_state:
    st.session_state.success_messages = []

if "error_message" not in st.session_state:
    st.session_state.error_message = None


# COMMON API HELPER

def api_request(method: str, endpoint: str, payload: dict | None = None):
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            error_json = response.json()
            detail = error_json.get("detail", "")
        except Exception:
            detail = response.text if response is not None else ""

        raise RuntimeError(f"API hatası: {detail or str(e)}") from e

    except requests.exceptions.ConnectionError as e:
        raise RuntimeError("FastAPI backend'e bağlanılamadı. API çalışıyor mu?") from e

    except requests.exceptions.Timeout as e:
        raise RuntimeError("API isteği zaman aşımına uğradı.") from e

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"İstek sırasında hata oluştu: {str(e)}") from e



# API FUNCTIONS

def get_inventory():
    return api_request("GET", "/inventory/")


def get_suppliers():
    return api_request("GET", "/suppliers/")


def get_dashboard_summary():
    return api_request("GET", "/dashboard/summary")


def predict_risk(supplier_id, quantity, lead_time, transport_mode):
    payload = {
        "supplier_id": supplier_id,
        "quantity": quantity,
        "lead_time": lead_time,
        "transport_mode": transport_mode
    }
    return api_request("POST", "/ai/predict", payload)


def inbound_stock(product_name, quantity):
    payload = {
        "product_name": product_name,
        "quantity": quantity
    }
    return api_request("POST", "/inventory/inbound", payload)


def outbound_stock(product_name, quantity):
    payload = {
        "product_name": product_name,
        "quantity": quantity
    }
    return api_request("POST", "/inventory/outbound", payload)


def get_orders():
    return api_request("GET", "/orders/")


def get_movements():
    return api_request("GET", "/movements/")


def create_order(supplier_id, product_name, quantity, lead_time, transport_mode):
    payload = {
        "supplier_id": supplier_id,
        "product_name": product_name,
        "quantity": quantity,
        "lead_time": lead_time,
        "transport_mode": transport_mode
    }
    return api_request("POST", "/orders/", payload)



# UI HELPERS

def show_flash_messages():
    if st.session_state.success_messages:
        for msg in st.session_state.success_messages:
            st.success(msg)
        st.session_state.success_messages = []

    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = None


def safe_dataframe(data):
    df = pd.DataFrame(data)
    if df.empty:
        st.info("Gösterilecek veri bulunamadı.")
    return df



# SIDEBAR

with st.sidebar:
    st.markdown("### PredictERP")
    st.markdown(
        "<p style='font-size: 12px; color: #7f8c8d; margin-top:-15px;'>Global SCM Engine</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    menu = st.radio(
        "Menü",
        [
            "Dashboard",
            "İşlemler (Sipariş/Sevkiyat)",
            "Envanter Durumu",
            "Sipariş Geçmişi",
            "Stok Hareketleri",
            "AI Analizleri"
        ],
        label_visibility="collapsed"
    )



# INITIAL DATA LOAD

try:
    inv_df = safe_dataframe(get_inventory())
    sup_df = safe_dataframe(get_suppliers())
except RuntimeError as e:
    st.error(str(e))
    st.stop()

show_flash_messages()



# PAGES

if menu == "Dashboard":
    st.header("Küresel Sistem Özeti")

    try:
        summary = get_dashboard_summary()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Toplam Stok", summary.get("total_stock", 0))
        c2.metric("Aktif Tedarikçi", summary.get("active_suppliers", 0))
        c3.metric("Ort. Ülke Riski", f"{summary.get('average_country_risk', 0)} / 100")
        c4.metric("Kritik Ürün", summary.get("critical_stock_count", 0))

        st.markdown("---")
        st.subheader("Tedarikçi Performans ve Ülke Risk Tablosu")

        if not sup_df.empty:
            supplier_cols = ["SupplierID", "Country", "Country_Risk_Index", "Reliability_Score"]
            existing_cols = [c for c in supplier_cols if c in sup_df.columns]
            st.dataframe(
                sup_df[existing_cols].sort_values(by="Reliability_Score", ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Tedarikçi verisi bulunamadı.")

    except RuntimeError as e:
        st.error(str(e))


elif menu == "İşlemler (Sipariş/Sevkiyat)":
    st.header("Operasyonel Kayıtlar")
    tab_in, tab_out = st.tabs(["Satın Alma (Giriş)", "Üretim/Satış (Çıkış)"])

    with tab_in:
        st.subheader("Tedarik Siparişi Oluştur")

        if inv_df.empty or sup_df.empty:
            st.warning("Sipariş ekranı için gerekli veri bulunamadı.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                selected_supplier = st.selectbox("Tedarikçi", sup_df["SupplierID"])
                selected_product = st.selectbox("Ürün", inv_df["ProductName"], key="in_prod")
                qty = st.number_input("Miktar", min_value=100, max_value=10000, value=500, key="in_qty")
                lead_time = st.slider("Beklenen Teslimat Süresi (Gün)", 7, 45, 14)
                transport_mode = st.selectbox("Taşıma Modu", ["DenizYolu", "HavaYolu", "KaraYolu"])

            with col2:
                st.write("**Yapay Zeka Karar Destek**")

                try:
                    with st.spinner("Risk analizi hesaplanıyor..."):
                        result = predict_risk(selected_supplier, qty, lead_time, transport_mode)

                    st.write(f" **Ülke:** {result.get('country', '-')}"
                             f" (Risk: {result.get('country_risk_index', '-')}/100)")
                    st.write(f" **Bölge:** {result.get('region', '-')}")
                    st.write(f" **Güvenilirlik:** {result.get('reliability_score', '-')}")
                    st.write(f" **Taşıma Modu:** {result.get('transport_mode', '-')}")
                    st.write(f" **Risk Olasılığı:** %{result.get('risk_probability', 0)}")

                    if result.get("risk_level") == "HIGH":
                        st.error("YÜKSEK RİSK")
                    else:
                        st.success("GÜVENLİ")

                    st.markdown("### Risk Nedenleri")
                    for reason in result.get("reasons", []):
                        st.write(f"- {reason}")

                    st.markdown("### Öneriler")
                    for recommendation in result.get("recommendations", []):
                        st.write(f"- {recommendation}")

                except RuntimeError as e:
                    st.error(str(e))

                st.write("---")

                if st.button("Siparişi Onayla ve Stoğa Al", use_container_width=True):
                    try:
                        order = create_order(
                            selected_supplier,
                            selected_product,
                            qty,
                            lead_time,
                            transport_mode
                        )

                        inbound_stock(selected_product, qty)

                        st.session_state.success_messages = [
                            f" Sipariş oluşturuldu: {order.get('OrderID', '-')}",
                            f" {qty} adet {selected_product} stoğa eklendi."
                        ]
                        st.rerun()

                    except RuntimeError as e:
                        st.session_state.error_message = str(e)
                        st.rerun()

    with tab_out:
        st.subheader("Üretim Çıkış Belgesi / Satış Faturası")

        if inv_df.empty:
            st.warning("Çıkış işlemi için ürün verisi bulunamadı.")
        else:
            col3, col4 = st.columns(2)

            with col3:
                out_prod = st.selectbox("Ürün", inv_df["ProductName"], key="out_prod")
                out_qty = st.number_input(
                    "Çıkış Miktarı",
                    min_value=1,
                    max_value=5000,
                    value=50,
                    key="out_qty"
                )

            with col4:
                st.write("Belge Detayları")
                st.text_input("Müşteri/Bölüm Adı", "Ana Montaj Hattı")

                if st.button("Çıkışı Onayla ve Envanterden Düş"):
                    try:
                        outbound_stock(out_prod, out_qty)
                        st.session_state.success_messages = [
                            f" {out_qty} adet {out_prod} stoktan düşüldü."
                        ]
                        st.rerun()

                    except RuntimeError as e:
                        st.session_state.error_message = str(e)
                        st.rerun()


elif menu == "Envanter Durumu":
    st.header("Depo Mevcut Stok Listesi")
    st.dataframe(inv_df, use_container_width=True, hide_index=True)


elif menu == "Sipariş Geçmişi":
    st.header("Sipariş Geçmişi")

    try:
        orders_df = safe_dataframe(get_orders())
        st.dataframe(orders_df, use_container_width=True, hide_index=True)
    except RuntimeError as e:
        st.error(str(e))


elif menu == "Stok Hareketleri":
    st.header("Stok Hareketleri")

    try:
        movements_df = safe_dataframe(get_movements())
        st.dataframe(movements_df, use_container_width=True, hide_index=True)
    except RuntimeError as e:
        st.error(str(e))


elif menu == "AI Analizleri":
    st.header("Tahminleme ve Karar Destek")

    if not sup_df.empty:
        best = sup_df.sort_values(by="Reliability_Score", ascending=False).iloc[0]
        st.success(
            f"**Öneri:** En yüksek güvenilirlik "
            f"{best['SupplierID']} ({best['Country']}) tedarikçisinde."
        )

    low = inv_df[inv_df["StockLevel"] < 250] if not inv_df.empty else pd.DataFrame()
    if not low.empty:
        st.warning(f"**Uyarı:** {len(low)} ürün kritik stok seviyesinde.")

    st.markdown("---")
    st.subheader("Gelecek Hafta Talep Simülasyonu")

    chart_data = pd.DataFrame(
        np.random.randn(7, 2) + [15, 12],
        columns=["Tahmini Talep", "Emniyet Stoğu"]
    )
    st.area_chart(chart_data)