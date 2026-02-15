# 🛡️ IoT-Safety-Hub <div align="center">
**Enterprise-grade continuous gas monitoring and automated compliance logging designed specifically for MSMEs.** 

## 📖 The Problem vs. The Solution

Large industrial factories utilize complex SCADA systems for continuous hazard monitoring. MSMEs (Chemical units, Pharma labs, Woodshops, Food processing) cannot afford these, leaving them reliant on isolated, reactive buzzers. **IoT-Safety-Hub** is a highly affordable local-edge IoT architecture that replaces passive alarms with continuous behavioral monitoring, remote escalation, and legally compliant data logging.

### Key Value Propositions
* 🚨 **Solving the "Silent Night" Vulnerability:** Standalone buzzers ring to empty rooms at 2 AM. This system features a background escalation engine to alert owners remotely.
* 📈 **Proactive "Near-Miss" Detection:** By logging continuous PPM data, owners can spot slow upward gas trends (e.g., a failing generator valve) days before it triggers a critical alarm.
* 📑 **Closing the Audit Gap:** 88% of small factories fail fire audits due to missing records. This system generates tamper-evident, one-click safety reports compliant with **IS 14489:1998** standards.


## 🏗️ System Architecture

The system operates on a highly reliable **"Pull" architecture (Continuous Polling)** over a Local Area Network (LAN), ensuring stability on standard MSME hardware without requiring expensive cloud computing.

1. **Sensing Layer:** ESP32 reads MQ-7 (Carbon Monoxide) and MQ-4 (Methane) sensors via 12-bit ADC.
2. **Transmission Layer:** Data is packaged into JSON and transmitted over HTTP POST.
3. **Processing Vault (Backend):** A Python **FastAPI** edge server validates payloads via Pydantic and commits them to a permanent **SQLite** database.
4. **Presentation Layer (Frontend):** A **Streamlit** dashboard polls the SQL database every 5 seconds to render live behavioral graphs and export audit logs.



## 📂 Repository Structure

```text
IOT-safety-hub/
│
├── backend/                  # The Data Vault & Listener
│   ├── main.py               # FastAPI server & Escalation Engine
│   └── requirements.txt      # Python dependencies (fastapi, uvicorn, sqlalchemy)
│
├── frontend/                 # The Presentation Layer
│   ├── app.py                # Streamlit live dashboard & Audit Exporter
│   └── requirements.txt      # Python dependencies (streamlit, pandas)
│
└── hardware/                 # The Physical Layer
    └── esp32_firmware.ino    # C++ Arduino IDE firmware
```

---

## 🚀 Local Deployment Guide

### 1. Backend Setup (The Listener)
Open a terminal, navigate to the `backend` directory, and start the FastAPI server:

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows (Use 'source venv/bin/activate' for Mac/Linux)
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be live at `http://localhost:8000`. The SQLite database (`safety_hub_logs.db`) will auto-generate upon receiving the first data packet.

### 2. Frontend Setup (The Dashboard)
Open a new terminal tab, navigate to the `frontend` directory, and launch the UI:

```bash
cd frontend
python -m venv venv
venv\Scripts\activate      
pip install -r requirements.txt
streamlit run app.py
```
The dashboard will automatically open in your browser at `http://localhost:8501`, polling the database every 5 seconds.

### 3. Hardware Setup (The Sensors)
1. Turn on a Local Area Network (e.g., Mobile Hotspot) and connect your PC.
2. Find your PC's local IPv4 address.
3. Open `hardware/esp32_firmware.ino` in the Arduino IDE.
4. Update the `ssid`, `password`, and `serverName` variables with your network details and IP address.
5. Connect the ESP32 via USB and click **Upload**.

---

## 📡 API Reference

**`POST /ingest`**

Receives analog sensor data from the ESP32, validates the structure, writes to the SQL vault, and evaluates the 2-minute critical escalation protocol.

**Expected JSON Payload:**

```json
{
  "mq7_ppm": 25.5,
  "mq4_ppm": 10.2,
  "temperature": 30.5,
  "humidity": 55.0
}
```

---

## 🔮 Future Enhancements
* **GSM Module Integration:** Fallback hardware redundancy for localized Wi-Fi failures.
* **Automated Actuators:** Hardware relays to trigger exhaust fans or solenoid shut-off valves based on SQL thresholds.
* **Cloud Migration:** Transitioning the local Edge FastAPI server to AWS/Heroku for multi-facility dashboarding.