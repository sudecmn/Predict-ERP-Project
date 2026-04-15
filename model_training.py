import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

np.random.seed(42)

regions = ['Asya', 'Avrupa', 'İç_Pazar', 'Amerika']
countries_map = {
    'Asya': ['Çin', 'Tayvan', 'Hindistan'],
    'Avrupa': ['Almanya', 'İtalya', 'Polonya'],
    'İç_Pazar': ['Türkiye'],
    'Amerika': ['ABD', 'Meksika']
}
transport_modes = ['DenizYolu', 'HavaYolu', 'KaraYolu']

data = []

for _ in range(2000):
    region = np.random.choice(regions)
    country = np.random.choice(countries_map[region])

    if country in ['Çin', 'Tayvan']:
        country_risk = np.random.randint(40, 85)
    elif country in ['Almanya', 'Türkiye', 'ABD']:
        country_risk = np.random.randint(10, 35)
    else:
        country_risk = np.random.randint(20, 60)

    transport = np.random.choice(transport_modes)
    rel_score = np.random.randint(50, 100)
    qty = np.random.randint(100, 10000)
    lead_time = np.random.randint(7, 45)

    risk_score = 0
    if rel_score < 70:
        risk_score += 30
    if country_risk > 60:
        risk_score += 25
    if transport == 'DenizYolu' and lead_time < 20:
        risk_score += 45
    if transport == 'HavaYolu':
        risk_score -= 15
    if qty > 5000:
        risk_score += 15

    risk_score += np.random.randint(-10, 20)

    is_delayed = 1 if risk_score > 50 else 0

    data.append({
        'Region': region,
        'Country': country,
        'Country_Risk_Index': country_risk,
        'Transport_Mode': transport,
        'Reliability_Score': rel_score,
        'Order_Quantity': qty,
        'Expected_Lead_Time_Days': lead_time,
        'Base_Cost_Multiplier': round(np.random.uniform(0.8, 1.5), 2),
        'Carbon_Footprint_Multiplier': round(np.random.uniform(0.5, 2.0), 2),
        'Is_Delayed': is_delayed
    })

df = pd.DataFrame(data)

X = df.drop('Is_Delayed', axis=1)
y = df['Is_Delayed']

X_encoded = pd.get_dummies(X, columns=['Region', 'Country', 'Transport_Mode'])

model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
model.fit(X_encoded, y)

joblib.dump(model, 'risk_prediction_model.joblib')
joblib.dump(list(X_encoded.columns), 'model_features.joblib')

print("Model ve feature dosyaları oluşturuldu.")