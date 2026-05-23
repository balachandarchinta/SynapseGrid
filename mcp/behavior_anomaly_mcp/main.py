import os
import json
import httpx
from collections import deque
from fastapi import FastAPI, HTTPException, Request
from jsonschema import validate, ValidationError

app = FastAPI(title="Behavior Anomaly MCP Service", description="Computes kinetic crowd anomalies and behavioral indexes.")

# Configuration
PERSISTENCE_URL = os.getenv("PERSISTENCE_URL", "http://localhost:8007")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", os.path.join(os.path.dirname(__file__), "../../contracts/situation.schema.json"))
ROLLING_WINDOW_SIZE = 10

# Rolling state store in memory
# Node ID -> Deque of float velocities
node_velocity_history = {
    "Gate A": deque(maxlen=ROLLING_WINDOW_SIZE),
    "Gate B": deque(maxlen=ROLLING_WINDOW_SIZE),
    "Main Concourse": deque(maxlen=ROLLING_WINDOW_SIZE),
    "South Seating": deque(maxlen=ROLLING_WINDOW_SIZE),
    "North Seating": deque(maxlen=ROLLING_WINDOW_SIZE),
    "Food Court": deque(maxlen=ROLLING_WINDOW_SIZE)
}

def load_schema():
    try:
        with open(SCHEMA_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema: {e}")
        return None

schema_cache = load_schema()

@app.post("/analyze")
async def analyze_behavior(request: Request):
    """Processes frame, updates rolling history, calculates kinetic variance, and raises anomaly alerts."""
    try:
        frame = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Schema validation
    if schema_cache:
        try:
            validate(instance=frame, schema=schema_cache)
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=f"Schema Validation Error: {ve.message}")

    nodes = frame.get("nodes", {})
    assessments = {}
    anomalies_detected = []

    async with httpx.AsyncClient() as client:
        for node_id, node_data in nodes.items():
            domain_vals = node_data.get("domain_numeric_values", {})
            vel = domain_vals.get("crowd_velocity_mps", 0.0)
            density = domain_vals.get("density_per_sqm", 0.0)
            flow = domain_vals.get("turnstile_flow_rate", 0.0)
            raw_cognitive_drift = domain_vals.get("cognitive_drift_index", 0.0)

            # Update rolling velocities
            history = node_velocity_history[node_id]
            history.append(vel)

            # Compute Kinetic Acceleration Variance
            # a_t = (v_t - v_t-1)
            accelerations = []
            if len(history) > 1:
                for i in range(1, len(history)):
                    accelerations.append(history[i] - history[i-1])
            
            accel_variance = 0.0
            if len(accelerations) > 1:
                mean_acc = sum(accelerations) / len(accelerations)
                accel_variance = sum((a - mean_acc) ** 2 for a in accelerations) / len(accelerations)

            # Behavior logic anomalies
            anomaly_flag = False
            anomaly_type = "NORMAL"
            confidence = 0.0
            msg = "Stable crowd dynamics."

            # Case A: Stampede / High kinetic surge (Sudden high speed & variance at high densities)
            if vel > 4.5 and density > 2.5 and accel_variance > 0.5:
                anomaly_flag = True
                anomaly_type = "STAMPEDE_PANIC"
                confidence = float(min(0.5 + accel_variance * 0.4, 0.99))
                msg = f"CRITICAL: Sudden unified velocity surge detected at {node_id}! High stampede / crush probability."

            # Case B: Medical Crush / Bottleneck (Hyper-density and near-zero flow/velocity)
            elif density > 5.0 and vel < 0.3 and flow < 10.0:
                anomaly_flag = True
                anomaly_type = "CROWD_CRUSH_HAZARD"
                confidence = float(min(0.6 + (density / 15.0) * 0.39, 0.99))
                msg = f"CRITICAL: Structural crowd stagnation detected at {node_id}! Density is {density}/sqm with zero flow rate."

            # Case C: High Turbulence (Unusual speed fluctuations but moderate density)
            elif accel_variance > 0.8 and density > 2.0:
                anomaly_flag = True
                anomaly_type = "TURBULENCE_WARNING"
                confidence = 0.75
                msg = f"WARNING: Chaotic velocity vectors detected at {node_id} (Variance: {accel_variance:.2f})."

            # Derive Cognitive Drift Index based on real-time physics anomalies
            # CDI = (Density normalized + Kinetic Variance normalized) / 2
            norm_density = min(density / 10.0, 1.0)
            norm_var = min(accel_variance / 2.0, 1.0)
            cognitive_drift_index = float(0.4 * norm_density + 0.3 * norm_var + 0.3 * raw_cognitive_drift)

            if anomaly_flag:
                anomalies_detected.append({
                    "node_id": node_id,
                    "anomaly_type": anomaly_type,
                    "confidence": confidence,
                    "log": msg
                })
                # Post anomaly upstream to persistence server
                try:
                    await client.post(
                        f"{PERSISTENCE_URL}/log_anomaly",
                        json={
                            "anomaly_type": anomaly_type,
                            "confidence": confidence,
                            "raw_log_str": f"[{node_id}] {msg} (Density: {density}, Velocity Var: {accel_variance:.3f})"
                        },
                        timeout=2.0
                    )
                except Exception as e:
                    print(f"Error logging anomaly to persistence: {e}")

            assessments[node_id] = {
                "node_id": node_id,
                "anomaly_type": anomaly_type,
                "kinetic_acceleration_variance": accel_variance,
                "cognitive_drift_index": cognitive_drift_index,
                "confidence": confidence,
                "description": msg
            }

    return {
        "status": "success",
        "assessments": assessments,
        "anomalies_detected": anomalies_detected
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
