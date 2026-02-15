from fastapi import FastAPI, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

# --- Database Setup (SQLite for Edge Server) ---
DATABASE_URL = "sqlite:///./safety_hub_logs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQL Model ---
class SensorLog(Base):
    __tablename__ = "sensor_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    mq7_ppm = Column(Float)
    mq4_ppm = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)

Base.metadata.create_all(bind=engine)

# --- Pydantic Schema (Expected JSON from ESP32) ---
class Payload(BaseModel):
    mq7_ppm: float
    mq4_ppm: float
    temperature: float
    humidity: float

# --- FastAPI Initialization ---
app = FastAPI(title="IOT-Safety-Hub API")

# Thresholds and State Management
MQ7_DANGER_THRESHOLD = 50.0  # PPM limit for Carbon Monoxide
ALERT_COOLDOWN_MINUTES = 10  # Prevent spamming the owner with calls
last_alert_time = None

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Escalation Logic Engine ---
def check_critical_alert(db: Session):
    global last_alert_time
    now = datetime.utcnow()
    
    if last_alert_time and (now - last_alert_time) < timedelta(minutes=ALERT_COOLDOWN_MINUTES):
        return

    two_minutes_ago = now - timedelta(minutes=2)
    recent_logs = db.query(SensorLog).filter(SensorLog.timestamp >= two_minutes_ago).all()

    if not recent_logs:
        return

    consistently_high = all(log.mq7_ppm >= MQ7_DANGER_THRESHOLD for log in recent_logs)
    oldest_log_in_window = recent_logs[0]
    time_span_valid = (now - oldest_log_in_window.timestamp) >= timedelta(minutes=1, seconds=50)

    if consistently_high and time_span_valid:
        trigger_voice_escalation(recent_logs[-1].mq7_ppm)
        last_alert_time = now

def trigger_voice_escalation(current_ppm: float):
    print(f"\n🚨 CRITICAL ALERT TRIGGERED! 🚨")
    print(f"MQ-7 levels have been consistently high. Current PPM: {current_ppm}")
    print("Initiating automated escalation protocol...\n")

# --- API Endpoints ---
@app.post("/ingest")
def ingest_sensor_data(data: Payload, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    new_log = SensorLog(
        mq7_ppm=data.mq7_ppm,
        mq4_ppm=data.mq4_ppm,
        temperature=data.temperature,
        humidity=data.humidity
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    background_tasks.add_task(check_critical_alert, db)
    return {"status": "success", "message": "Data securely logged", "log_id": new_log.id}

@app.get("/health")
def health_check():
    return {"status": "active", "system": "IOT-Safety-Hub Listener"}