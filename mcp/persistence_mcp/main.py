import os
import sqlite3
import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

# Define FastMCP server
mcp = FastMCP("PersistenceMCP")

# Database Path configuration
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "stadium_telemetry.db")

# Detect database configuration (SQLite local fallback vs PostgreSQL Cloud SQL)
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Initializes and returns either a PostgreSQL or SQLite connection."""
    if DB_URL:
        import psycopg2
        return psycopg2.connect(DB_URL)
    else:
        return sqlite3.connect(DB_PATH)

def get_placeholder():
    """Returns %s parameter style for PostgreSQL and ? for SQLite."""
    return "%s" if DB_URL else "?"

def init_db():
    """Initializes database tables with dialect-appropriate definitions."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    
    # Dialect compatibility for primary keys
    pk_style = "SERIAL PRIMARY KEY" if DB_URL else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS agent_telemetry (
        id {pk_style},
        timestamp TEXT NOT NULL,
        agent_name TEXT NOT NULL,
        metric_type TEXT NOT NULL,
        target_node_id TEXT NOT NULL,
        value REAL NOT NULL,
        metadata_str TEXT
    )
    """)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS behavior_anomalies (
        id {pk_style},
        timestamp TEXT NOT NULL,
        anomaly_type TEXT NOT NULL,
        confidence REAL NOT NULL,
        raw_log_str TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Direct functions implementing core database operations
def db_log_telemetry(agent_name: str, metric_type: str, target_node_id: str, value: float, metadata_str: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    p = get_placeholder()
    cursor.execute(
        f"INSERT INTO agent_telemetry (timestamp, agent_name, metric_type, target_node_id, value, metadata_str) VALUES ({p}, {p}, {p}, {p}, {p}, {p})",
        (now, agent_name, metric_type, target_node_id, value, metadata_str)
    )
    conn.commit()
    conn.close()

def db_log_anomaly(anomaly_type: str, confidence: float, raw_log_str: str):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    p = get_placeholder()
    cursor.execute(
        f"INSERT INTO behavior_anomalies (timestamp, anomaly_type, confidence, raw_log_str) VALUES ({p}, {p}, {p}, {p})",
        (now, anomaly_type, confidence, raw_log_str)
    )
    conn.commit()
    conn.close()

def db_get_summary() -> dict:
    conn = get_connection()
    df = pd.read_sql_query("SELECT metric_type, value FROM agent_telemetry", conn)
    conn.close()
    if df.empty:
        return {}
    summary = df.groupby("metric_type")["value"].agg(["mean", "std", "var"]).to_dict(orient="index")
    # Clean NaN values
    for m, stats in summary.items():
        if pd.isna(stats["std"]): stats["std"] = 0.0
        if pd.isna(stats["var"]): stats["var"] = 0.0
    return summary

# ----------------- FastMCP Tool Definitions -----------------

@mcp.tool()
def log_agent_telemetry(agent_name: str, metric_type: str, target_node_id: str, value: float, metadata_str: str = "") -> str:
    """Log stadium metrics for a given target node."""
    db_log_telemetry(agent_name, metric_type, target_node_id, value, metadata_str)
    return f"Logged telemetry successfully for {agent_name} - {metric_type} on {target_node_id} = {value}"

@mcp.tool()
def log_anomaly_alert(anomaly_type: str, confidence: float, raw_log_str: str) -> str:
    """Log an anomaly alert with confidence levels."""
    db_log_anomaly(anomaly_type, confidence, raw_log_str)
    return f"Logged anomaly '{anomaly_type}' successfully."

@mcp.tool()
def generate_statistical_summary() -> str:
    """Retrieve statistical telemetry aggregates utilizing pandas dataframes."""
    stats = db_get_summary()
    if not stats:
        return "No telemetry records found."
    return str(stats)

# ----------------- FastAPI Web Application -----------------

app = FastAPI(
    title="Synapse Grid Persistence Server",
    description="Exposes SQLite stadium_telemetry.db storage and tools."
)

class TelemetryPayload(BaseModel):
    agent_name: str
    metric_type: str
    target_node_id: str
    value: float
    metadata_str: str = ""

class AnomalyPayload(BaseModel):
    anomaly_type: str
    confidence: float
    raw_log_str: str

@app.post("/log_telemetry")
async def api_log_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks):
    """Enforces non-blocking L3 asynchronous writes using FastAPI background workers."""
    try:
        background_tasks.add_task(
            db_log_telemetry,
            payload.agent_name,
            payload.metric_type,
            payload.target_node_id,
            payload.value,
            payload.metadata_str
        )
        return {"status": "queued", "message": "Telemetry queued for background SQLite flush."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log_anomaly")
async def api_log_anomaly(payload: AnomalyPayload, background_tasks: BackgroundTasks):
    """Enforces non-blocking L3 asynchronous writes using FastAPI background workers."""
    try:
        background_tasks.add_task(
            db_log_anomaly,
            payload.anomaly_type,
            payload.confidence,
            payload.raw_log_str
        )
        return {"status": "queued", "message": "Anomaly alert queued for background SQLite flush."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary")
async def api_get_summary():
    """Reads directly from independent relational views (Materialized queries)."""
    try:
        conn = get_connection()
        df_telemetry = pd.read_sql_query("SELECT timestamp, agent_name, metric_type, target_node_id, value, metadata_str FROM agent_telemetry ORDER BY id DESC LIMIT 100", conn)
        df_anomalies = pd.read_sql_query("SELECT timestamp, anomaly_type, confidence, raw_log_str FROM behavior_anomalies ORDER BY id DESC LIMIT 50", conn)
        conn.close()

        summary = db_get_summary()

        return {
            "status": "success",
            "summary": summary,
            "recent_telemetry": df_telemetry.to_dict(orient="records"),
            "recent_anomalies": df_anomalies.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
