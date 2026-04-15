import joblib
import pandas as pd
from pathlib import Path
from app.repositories.supplier_repo import fetch_supplier_by_id

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "risk_prediction_model.joblib"
FEATURES_PATH = BASE_DIR / "model_features.joblib"

model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)


def generate_risk_reasons(supplier, quantity: int, lead_time: int, transport_mode: str):
    reasons = []

    country_risk = supplier["Country_Risk_Index"]
    reliability = supplier["Reliability_Score"]
    region = supplier["Region"]
    country = supplier["Country"]

    if country_risk >= 60:
        reasons.append(f"Ülke risk indeksi yüksek ({country_risk}/100).")

    if reliability < 75:
        reasons.append(f"Tedarikçi güvenilirlik skoru düşük ({reliability}).")

    if transport_mode == "DenizYolu" and lead_time < 20:
        reasons.append("Denizyolu seçildiği halde teslim süresi kısa; gecikme riski artabilir.")

    if transport_mode == "KaraYolu" and region in ["Asya", "Amerika"]:
        reasons.append(f"{region} bölgesinden karayolu seçimi operasyonel olarak riskli olabilir.")

    if quantity > 5000:
        reasons.append(f"Sipariş miktarı yüksek ({quantity}); üretim ve lojistik baskısı oluşturabilir.")

    if country in ["Çin", "Tayvan"] and transport_mode == "DenizYolu":
        reasons.append(f"{country} hattında denizyolu taşımacılığı ek tedarik zinciri riski oluşturabilir.")

    if not reasons:
        reasons.append("Belirgin bir yüksek risk sinyali görülmedi.")

    return reasons


def generate_recommendations(supplier, quantity: int, lead_time: int, transport_mode: str, risk_probability: float):
    recommendations = []

    if risk_probability > 50:
        recommendations.append("Alternatif tedarikçi değerlendirilmesi önerilir.")

    if transport_mode == "DenizYolu" and lead_time < 20:
        recommendations.append("Teslim süresini artırmak veya Havayolu seçmek riski düşürebilir.")

    if quantity > 5000:
        recommendations.append("Sipariş miktarını partilere bölmek operasyonel riski azaltabilir.")

    if supplier["Country_Risk_Index"] >= 60:
        recommendations.append("Daha düşük ülke riskine sahip bir tedarikçiyle karşılaştırma yapılabilir.")

    if supplier["Reliability_Score"] < 75:
        recommendations.append("Geçmiş performansı daha güçlü tedarikçiler önceliklendirilebilir.")

    if not recommendations:
        recommendations.append("Mevcut sipariş parametreleri kabul edilebilir görünüyor.")

    return recommendations


def predict_order_risk(supplier_id: str, quantity: int, lead_time: int, transport_mode: str):
    supplier = fetch_supplier_by_id(supplier_id)
    if supplier is None:
        raise ValueError("Tedarikçi bulunamadı.")

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
            input_dict[feature] = 1 if transport_mode == feature.replace("Transport_Mode_", "") else 0

    input_df = pd.DataFrame([input_dict])

    for feature in model_features:
        if feature not in input_df.columns:
            input_df[feature] = 0

    input_df = input_df[model_features]

    risk_probability = float(model.predict_proba(input_df)[0][1] * 100)
    risk_level = "HIGH" if risk_probability > 50 else "LOW"

    reasons = generate_risk_reasons(supplier, quantity, lead_time, transport_mode)
    recommendations = generate_recommendations(
        supplier, quantity, lead_time, transport_mode, risk_probability
    )

    return {
        "supplier_id": supplier_id,
        "country": supplier["Country"],
        "region": supplier["Region"],
        "country_risk_index": supplier["Country_Risk_Index"],
        "reliability_score": supplier["Reliability_Score"],
        "transport_mode": transport_mode,
        "risk_probability": round(risk_probability, 2),
        "risk_level": risk_level,
        "reasons": reasons,
        "recommendations": recommendations,
    }