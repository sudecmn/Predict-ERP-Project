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
    .stApp {
        background-color: #F7F9FC;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E6EAF0;
    }

    p, span, label, li, ul, ol {
    color: #2C3E50 !important;
    }

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
        width: 100%;
        height: 46px;
        border-radius: 10px;
        border: 1px solid #4A90E2;
        color: #4A90E2 !important;
        font-weight: 600;
        transition: 0.3s;
        background-color: transparent;
    }

    .stButton > button:hover {
        background-color: #4A90E2 !important;
        color: #FFFFFF !important;
    }

    .section-label {
        font-size: 13px;
        font-weight: 700;
        color: #6B7280 !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-top: 10px;
        margin-bottom: 8px;
    }

    .big-score {
        font-size: 32px;
        font-weight: 700;
        color: #1F2937 !important;
        margin-bottom: 6px;
    }

    .small-muted {
        font-size: 13px;
        color: #6B7280 !important;
        margin-bottom: 10px;
    }

    div[data-testid="stTextInput"] > div,
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stTextArea"] > div {
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    input, textarea {
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    div[data-baseweb="select"] {
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
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
    response = None

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

        raise RuntimeError(f"API error: {detail or str(e)}") from e

    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            "Unable to connect to the FastAPI backend. Please make sure the API is running."
        ) from e

    except requests.exceptions.Timeout as e:
        raise RuntimeError("The API request timed out.") from e

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"An error occurred during the request: {str(e)}") from e


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
        st.info("No data available to display.")
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
        "Menu",
        [
            "Dashboard",
            "Operations",
            "Inventory",
            "Order History",
            "Stock Movements",
            "AI Insights"
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("v1.0 • AI ERP System")


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
    st.header("Global Supply Chain Overview")

    try:
        summary = get_dashboard_summary()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Stock", summary.get("total_stock", 0))
        col2.metric("Active Suppliers", summary.get("active_suppliers", 0))
        col3.metric("Average Risk", f"{summary.get('average_country_risk', 0)}/100")
        col4.metric("Critical Items", summary.get("critical_stock_count", 0))

        st.markdown("---")

        st.subheader("Critical Stock Alerts")
        low_stock = inv_df[inv_df["StockLevel"] < 250]

        if not low_stock.empty:
            st.warning(f"{len(low_stock)} items are at critical stock level.")
            st.dataframe(low_stock, use_container_width=True, hide_index=True)
        else:
            st.success("All stock levels are healthy.")

        st.markdown("---")

        st.subheader("Top Supplier")
        if not sup_df.empty:
            best_supplier = sup_df.sort_values(by="Reliability_Score", ascending=False).iloc[0]
            st.success(
                f"{best_supplier['SupplierID']} - {best_supplier['Country']} "
                f"(Score: {best_supplier['Reliability_Score']})"
            )

        st.markdown("---")

        st.subheader("Weekly Demand Simulation")
        chart_data = pd.DataFrame(
            np.random.randn(7, 2) + [20, 15],
            columns=["Demand", "Safety Stock"]
        )
        st.area_chart(chart_data)

        st.markdown("---")

        st.subheader("System Insights")
        col_a, col_b = st.columns(2)

        with col_a:
            st.info("The system is currently operating in a stable state.")
            st.write("• Stock levels are balanced")
            st.write("• The supply chain remains traceable")

        with col_b:
            high_risk_suppliers = (
                sup_df[sup_df["Reliability_Score"] < 70]
                if not sup_df.empty else pd.DataFrame()
            )
            st.warning(f"{len(high_risk_suppliers)} suppliers are considered high risk.")

    except RuntimeError as e:
        st.error(str(e))


elif menu == "Operations":
    st.header("Operations")
    tab_in, tab_out = st.tabs(["Inbound Orders", "Outbound Transactions"])

    with tab_in:
        st.subheader("Create Purchase Order")

        if inv_df.empty or sup_df.empty:
            st.warning("Required data for the order screen is not available.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Order Parameters")
                selected_supplier = st.selectbox("Supplier", sup_df["SupplierID"])
                selected_product = st.selectbox("Product", inv_df["ProductName"], key="in_prod")
                qty = st.number_input(
                    "Quantity",
                    min_value=100,
                    max_value=10000,
                    value=500,
                    key="in_qty"
                )
                lead_time = st.slider("Lead Time (Days)", 7, 45, 14)
                transport_mode = st.selectbox("Transport Mode", ["Sea", "Air", "Road"])

            with col2:
                st.write("AI Decision Support")

                try:
                    with st.spinner("Running risk analysis..."):
                        result = predict_risk(selected_supplier, qty, lead_time, transport_mode)

                    st.info(
                        "Final risk score is adjusted using business rules to better reflect "
                        "real-world supply chain risks."
                    )

                    st.markdown('<div class="section-label">Supplier Overview</div>', unsafe_allow_html=True)
                    st.write(
                        f"Country: {result.get('country', '-')}"
                        f" (Risk: {result.get('country_risk_index', '-')}/100)"
                    )
                    st.write(f"Region: {result.get('region', '-')}")
                    st.write(f"Reliability: {result.get('reliability_score', '-')}")
                    st.write(f"Transport Mode: {result.get('transport_mode', '-')}")

                    st.markdown('<div class="section-label">Risk Analysis</div>', unsafe_allow_html=True)

                    raw_score = result.get("base_risk_probability", "-")
                    risk = result.get("risk_probability", 0)

                    st.write(f"Model Score (Raw): %{raw_score}")
                    st.markdown(f'<div class="big-score">%{risk}</div>', unsafe_allow_html=True)
                    st.markdown(
                        '<div class="small-muted">Final calibrated risk score</div>',
                        unsafe_allow_html=True
                    )

                    st.progress(float(risk) / 100)

                    risk_label = result.get("risk_label", result.get("risk_level", "Unknown"))

                    if result.get("risk_level") == "HIGH":
                        st.error(risk_label)
                    elif result.get("risk_level") == "MEDIUM":
                        st.warning(risk_label)
                    else:
                        st.success(risk_label)

                    reasons = result.get("reasons", [])
                    recommendations = result.get("recommendations", [])

                    st.markdown("### Risk Factors")

                    if reasons:
                        for reason in reasons:
                            st.markdown(f"- {reason}")
                    else:
                            st.markdown("<span style='color:#6B7280'>No risk factors found.</span>", unsafe_allow_html=True)


                            st.markdown("### Recommendations")

                    if recommendations:
                        for recommendation in recommendations:
                            st.markdown(f"- {recommendation}")
                    else:
                            st.markdown("<span style='color:#6B7280'>No recommendations available.</span>", unsafe_allow_html=True)

                except RuntimeError as e:
                    st.error(str(e))

                st.write("---")

                if st.button("Approve Order and Add to Inventory", use_container_width=True):
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
                            f"Order created: {order.get('OrderID', '-')}",
                            f"{qty} units of {selected_product} were added to inventory."
                        ]
                        st.rerun()

                    except RuntimeError as e:
                        st.session_state.error_message = str(e)
                        st.rerun()

    with tab_out:
        st.subheader("Outbound Transaction")

        if inv_df.empty:
            st.warning("Product data for outbound transactions is not available.")
        else:
            col3, col4 = st.columns(2)

            with col3:
                st.markdown("### Transaction Parameters")
                out_prod = st.selectbox("Product", inv_df["ProductName"], key="out_prod")
                out_qty = st.number_input(
                    "Outbound Quantity",
                    min_value=1,
                    max_value=5000,
                    value=50,
                    key="out_qty"
                )

            with col4:
                st.write("Transaction Details")
                st.text_input("Customer / Department", "Main Assembly Line")

                if st.button("Confirm Outbound Transaction"):
                    try:
                        outbound_stock(out_prod, out_qty)
                        st.session_state.success_messages = [
                            f"{out_qty} units of {out_prod} were removed from inventory."
                        ]
                        st.rerun()

                    except RuntimeError as e:
                        st.session_state.error_message = str(e)
                        st.rerun()


elif menu == "Inventory":
    st.header("Inventory Overview")
    st.dataframe(inv_df, use_container_width=True, hide_index=True)


elif menu == "Order History":
    st.header("Order History")

    try:
        orders_df = safe_dataframe(get_orders())
        st.dataframe(orders_df, use_container_width=True, hide_index=True)
    except RuntimeError as e:
        st.error(str(e))


elif menu == "Stock Movements":
    st.header("Stock Movements")

    try:
        movements_df = safe_dataframe(get_movements())
        st.dataframe(movements_df, use_container_width=True, hide_index=True)
    except RuntimeError as e:
        st.error(str(e))


elif menu == "AI Insights":
    st.header("AI Insights")

    if not sup_df.empty:
        best = sup_df.sort_values(by="Reliability_Score", ascending=False).iloc[0]
        st.success(
            f"Recommendation: The supplier with the highest reliability is "
            f"{best['SupplierID']} ({best['Country']})."
        )

    low = inv_df[inv_df["StockLevel"] < 250] if not inv_df.empty else pd.DataFrame()
    if not low.empty:
        st.warning(f"Alert: {len(low)} items are at critical stock level.")

    st.markdown("---")
    st.subheader("Next Week Demand Simulation")

    chart_data = pd.DataFrame(
        np.random.randn(7, 2) + [15, 12],
        columns=["Forecasted Demand", "Safety Stock"]
    )
    st.area_chart(chart_data)