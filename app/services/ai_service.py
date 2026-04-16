import joblib
import pandas as pd
from pathlib import Path
from app.repositories.supplier_repo import fetch_supplier_by_id

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "risk_prediction_model.joblib"
FEATURES_PATH = BASE_DIR / "model_features.joblib"

try:
    model = joblib.load(MODEL_PATH)
    model_features = joblib.load(FEATURES_PATH)
except Exception as e:
    raise RuntimeError(f"Model files could not be loaded: {e}") from e


TRANSPORT_MODE_MAP_EN_TO_TR = {
    "Sea": "DenizYolu",
    "Air": "HavaYolu",
    "Road": "KaraYolu",
}

TRANSPORT_MODE_MAP_TR_TO_EN = {
    "DenizYolu": "Sea",
    "HavaYolu": "Air",
    "KaraYolu": "Road",
}

REGION_MAP_TR_TO_EN = {
    "Avrupa": "Europe",
    "Asya": "Asia",
    "Amerika": "America",
    "İç_Pazar": "Domestic Market",
}

RISK_LEVEL_LABELS = {
    "HIGH": "High Risk",
    "MEDIUM": "Medium Risk",
    "LOW": "Low Risk",
}


def normalize_transport_mode(transport_mode: str) -> str:
    if transport_mode in TRANSPORT_MODE_MAP_TR_TO_EN:
        return transport_mode
    if transport_mode in TRANSPORT_MODE_MAP_EN_TO_TR:
        return TRANSPORT_MODE_MAP_EN_TO_TR[transport_mode]
    raise ValueError("Invalid transport mode.")


def apply_business_rules(
    risk_probability: float,
    supplier,
    quantity: int,
    lead_time: int,
    transport_mode_tr: str,
) -> float:
    country_risk = supplier["Country_Risk_Index"]
    reliability = supplier["Reliability_Score"]
    region = supplier["Region"]

    # High country risk should never look too safe
    if country_risk >= 70:
        risk_probability = max(risk_probability, 50.0)

    if country_risk >= 85:
        risk_probability = max(risk_probability, 70.0)

    # Very low reliability should push the score upward
    if reliability < 70:
        risk_probability = max(risk_probability, 55.0)
    elif reliability < 80:
        risk_probability = max(risk_probability, 40.0)

    # Short lead time with sea transport is operationally risky
    if transport_mode_tr == "DenizYolu" and lead_time < 20:
        risk_probability += 8.0

    # Road transport for distant regions is riskier
    if transport_mode_tr == "KaraYolu" and region in ["Asya", "Amerika"]:
        risk_probability += 10.0

    # Large orders increase operational pressure
    if quantity > 7000:
        risk_probability += 10.0
    elif quantity > 5000:
        risk_probability += 6.0

    # Strong reliability can soften the result slightly,
    # but should not completely override major structural risks
    if reliability >= 90:
        risk_probability -= 5.0
    elif reliability >= 85:
        risk_probability -= 3.0

    # Keep the score within a valid range
    risk_probability = max(0.0, min(risk_probability, 100.0))
    return round(risk_probability, 2)


def generate_risk_reasons_en(supplier, quantity: int, lead_time: int, transport_mode_tr: str):
    reasons = []

    country_risk = supplier["Country_Risk_Index"]
    reliability = supplier["Reliability_Score"]
    region_tr = supplier["Region"]
    country = supplier["Country"]

    if country_risk >= 70:
        reasons.append(f"The country risk index is very high ({country_risk}/100).")
    elif country_risk >= 50:
        reasons.append(f"The country risk index is moderately high ({country_risk}/100).")

    if reliability < 70:
        reasons.append(f"The supplier reliability score is low ({reliability}).")
    elif reliability < 80:
        reasons.append(f"The supplier reliability score is below the ideal level ({reliability}).")

    if transport_mode_tr == "DenizYolu" and lead_time < 20:
        reasons.append("Sea transport is selected with a short lead time; the delay risk may increase.")

    if transport_mode_tr == "KaraYolu" and region_tr in ["Asya", "Amerika"]:
        region_en = REGION_MAP_TR_TO_EN.get(region_tr, region_tr)
        reasons.append(f"Road transport may be risky for the {region_en} region.")

    if quantity > 7000:
        reasons.append(f"The order quantity is very high ({quantity}); the operational load may increase.")
    elif quantity > 5000:
        reasons.append(f"The order quantity is high ({quantity}); it may create production and delivery pressure.")

    if country in ["Çin", "Tayvan"] and transport_mode_tr == "DenizYolu":
        reasons.append(f"Sea transport on the {country} route may create additional supply chain risk.")

    if lead_time <= 10:
        reasons.append("The lead time is very short; planning flexibility may decrease.")

    if not reasons:
        reasons.append("No clear high-risk signal was detected.")

    return reasons


def generate_recommendations_en(
    supplier,
    quantity: int,
    lead_time: int,
    transport_mode_tr: str,
    risk_probability: float
):
    recommendations = []

    country_risk = supplier["Country_Risk_Index"]
    reliability = supplier["Reliability_Score"]

    if risk_probability >= 70:
        recommendations.append("Strongly consider evaluating an alternative supplier for this order.")
    elif risk_probability >= 50:
        recommendations.append("The order parameters should be reviewed again.")

    if transport_mode_tr == "DenizYolu" and lead_time < 20:
        recommendations.append("The lead time can be increased, or Air transport can be considered.")

    if quantity > 5000:
        recommendations.append("The order quantity can be split into batches to reduce operational risk.")

    if country_risk >= 60:
        recommendations.append("Compare this supplier with alternatives that have lower country risk.")

    if reliability < 75:
        recommendations.append("Suppliers with stronger historical performance can be prioritized.")

    if lead_time <= 10:
        recommendations.append("A more flexible delivery schedule is recommended.")

    if not recommendations:
        recommendations.append("The current order parameters appear acceptable.")

    return recommendations


def get_risk_level(risk_probability: float) -> str:
    if risk_probability >= 70:
        return "HIGH"
    if risk_probability >= 40:
        return "MEDIUM"
    return "LOW"


def build_model_input(supplier, quantity: int, lead_time: int, transport_mode_tr: str):
    input_dict = {
        "Order_Quantity": quantity,
        "Expected_Lead_Time_Days": lead_time,
        "Country_Risk_Index": supplier["Country_Risk_Index"],
        "Base_Cost_Multiplier": supplier["Base_Cost_Multiplier"],
        "Carbon_Footprint_Multiplier": supplier["Carbon_Footprint_Multiplier"],
        "Reliability_Score": supplier["Reliability_Score"],
    }

    for feature in model_features:
        if feature.startswith("Region_"):
            input_dict[feature] = 1 if supplier["Region"] == feature.replace("Region_", "") else 0
        elif feature.startswith("Country_"):
            input_dict[feature] = 1 if supplier["Country"] == feature.replace("Country_", "") else 0
        elif feature.startswith("Transport_Mode_"):
            input_dict[feature] = 1 if transport_mode_tr == feature.replace("Transport_Mode_", "") else 0

    input_df = pd.DataFrame([input_dict])

    for feature in model_features:
        if feature not in input_df.columns:
            input_df[feature] = 0

    return input_df[model_features]


def predict_order_risk(supplier_id: str, quantity: int, lead_time: int, transport_mode: str):
    supplier = fetch_supplier_by_id(supplier_id)

    if supplier is None:
        raise ValueError("Supplier not found.")

    if quantity <= 0:
        raise ValueError("Order quantity must be greater than zero.")

    if lead_time <= 0:
        raise ValueError("Lead time must be greater than zero.")

    transport_mode_tr = normalize_transport_mode(transport_mode)

    try:
        input_df = build_model_input(supplier, quantity, lead_time, transport_mode_tr)
        base_risk_probability = float(model.predict_proba(input_df)[0][1] * 100)
    except Exception as e:
        raise RuntimeError(f"An error occurred during risk prediction: {e}") from e

    risk_probability = apply_business_rules(
        risk_probability=base_risk_probability,
        supplier=supplier,
        quantity=quantity,
        lead_time=lead_time,
        transport_mode_tr=transport_mode_tr,
    )

    risk_level = get_risk_level(risk_probability)

    reasons = generate_risk_reasons_en(supplier, quantity, lead_time, transport_mode_tr)
    recommendations = generate_recommendations_en(
        supplier, quantity, lead_time, transport_mode_tr, risk_probability
    )

    return {
        "supplier_id": supplier_id,
        "country": supplier["Country"],
        "region": REGION_MAP_TR_TO_EN.get(supplier["Region"], supplier["Region"]),
        "country_risk_index": supplier["Country_Risk_Index"],
        "reliability_score": supplier["Reliability_Score"],
        "transport_mode": TRANSPORT_MODE_MAP_TR_TO_EN.get(transport_mode_tr, transport_mode_tr),
        "order_quantity": quantity,
        "lead_time": lead_time,
        "base_risk_probability": round(base_risk_probability, 2),
        "risk_probability": risk_probability,
        "risk_level": risk_level,
        "risk_label": RISK_LEVEL_LABELS[risk_level],
        "reasons": reasons,
        "recommendations": recommendations,
    }