from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import sqlite3


# Database setup
DATABASE_URL = "sqlite:///detections.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Detection model
class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    duration = Column(Float)
    image_path = Column(String)

Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expected POST format
class DetectionData(BaseModel):
    timestamp: str
    duration: float
    image: str

@app.post("/log")
def log_detection(data: DetectionData):
    try:
        dt = datetime.fromisoformat(data.timestamp)
        detection = Detection(timestamp=dt, duration=data.duration, image_path=data.image)
        session.add(detection)
        session.commit()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/summary")
def get_summary():
    today = date.today()
    detections_today = session.query(Detection).filter(
        Detection.timestamp >= datetime(today.year, today.month, today.day)
    ).all()
    total_sessions = len(detections_today)
    avg_duration = sum(d.duration for d in detections_today) / total_sessions if total_sessions else 0
    return {"total_sessions": total_sessions, "avg_duration": round(avg_duration, 2)}


@app.get("/trend")
def get_trend():
    conn = sqlite3.connect("detections.db")
    df = pd.read_sql("SELECT timestamp FROM detections", conn)
    conn.close()

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['time'] = df['timestamp'].dt.strftime('%H:%M')
    counts = df['time'].value_counts().sort_index()

    return JSONResponse(content=counts.to_dict())


@app.get("/duration-categories")
def get_duration_categories():
    today = date.today()
    detections = session.query(Detection).filter(
        Detection.timestamp >= datetime(today.year, today.month, today.day)
    ).all()
    short = sum(1 for d in detections if d.duration < 30)
    medium = sum(1 for d in detections if 30 <= d.duration <= 90)
    long = sum(1 for d in detections if d.duration > 90)
    return {"short": short, "medium": medium, "long": long}

@app.get("/feeding-by-hour")
def get_feeding_by_hour():
    today = date.today()
    detections = session.query(Detection).filter(
        Detection.timestamp >= datetime(today.year, today.month, today.day)
    ).all()
    by_hour = {}
    for d in detections:
        hour = d.timestamp.strftime("%H:00")
        by_hour[hour] = by_hour.get(hour, 0) + 1
    return by_hour

@app.get("/time-distribution")
def get_time_distribution():
    conn = sqlite3.connect("detections.db")
    df = pd.read_sql("SELECT timestamp FROM detections", conn)
    conn.close()

    if df.empty:
        return JSONResponse(content={})

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    df['hour'] = df['timestamp'].dt.hour
    counts = df['hour'].value_counts().sort_index()

    labels = [f"{h:02d}:00" for h in counts.index]
    return JSONResponse(content=dict(zip(labels, counts.tolist())))
