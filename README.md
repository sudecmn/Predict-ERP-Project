# 🚀 PredictERP – AI-Powered Supply Chain Management System

PredictERP is an intelligent ERP system designed to optimize supply chain operations using machine learning and real-time decision support.

This project simulates a real-world enterprise system where inventory, suppliers, and logistics decisions are enhanced with AI.

---
## 🎯 Features

* 📦 Inventory Management (Inbound / Outbound)
* 🚚 Order Creation & Tracking
* 🤖 AI-based Risk Prediction (Delay Probability)
* 🌍 Supplier & Country Risk Analysis
* 📊 Dashboard with Real-time Insights
* 📈 Demand Simulation (Next Week Forecast)
* 🧠 Explainable AI (Risk Reasons & Recommendations)

---

## 🧠 AI Model

The system uses a **Random Forest Classifier** trained on synthetic supply chain data.

### Input Features:

* Supplier Reliability Score
* Country Risk Index
* Transport Mode (Air / Sea / Land)
* Order Quantity
* Lead Time

### Output:

* Delay Risk Probability
* Risk Level (LOW / HIGH)
* Risk Reasons
* Actionable Recommendations

---

## 🏗️ Architecture

```text
Streamlit (Frontend UI)
        ↓
FastAPI (Backend API)
        ↓
SQLite Database + ML Model
```

---

## ⚙️ Tech Stack

* Python
* FastAPI
* Streamlit
* Scikit-learn
* Pandas / NumPy
* SQLite
* Joblib

---

## 📂 Project Structure

```text
app/
 ├── routers/
 ├── services/
 ├── repositories/
 ├── models/
 ├── main.py
 └── database.py

streamlit_app.py
requirements.txt
erp_cognitive_supply.db
risk_prediction_model.joblib
model_features.joblib
```

---

## 🚀 How to Run Locally

### 1. Clone repository

```bash
git clone https://github.com/sudecmn/Predict-ERP-Project.git
cd Predict-ERP-Project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run backend

```bash
python -m uvicorn app.main:app --reload
```

### 4. Run frontend

```bash
streamlit run streamlit_app.py
```

---

## 💡 Why This Project?

This project demonstrates:

* Full-stack data-driven application design
* Machine learning integration into business workflows
* API-based architecture (FastAPI)
* Real-world ERP system simulation

---

## 📌 Future Improvements

* Docker deployment
* Cloud hosting (AWS / Render)
* Real-time data integration
* Advanced forecasting models (LSTM / Prophet)
* Authentication & user roles

---

## 👩‍💻 Author

**Sude Naz Çimen**
Computer Engineering Student

---

## ⭐ If you like this project

Feel free to ⭐ star the repo!
