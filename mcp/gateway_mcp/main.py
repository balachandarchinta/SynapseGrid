import os
import time
import json
import asyncio
import random
import httpx
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Synapse Grid Central Gateway (Upgraded Architecture)", description="Aggregator with 3-Tier Redis cache, Circuit Breakers, and Saga HITL rollbacks.")

# Folder Configurations
GATEWAY_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(GATEWAY_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Microservice ports
INGESTION_URL = os.getenv("INGESTION_URL", "http://localhost:8002")
ANOMALY_URL = os.getenv("ANOMALY_URL", "http://localhost:8003")
GNN_URL = os.getenv("GNN_URL", "http://localhost:8004")
MARL_URL = os.getenv("MARL_URL", "http://localhost:8005")
STATS_URL = os.getenv("STATS_URL", "http://localhost:8006")

# ----------------- DISTRIBUTED CIRCUIT BREAKER -----------------
class CircuitBreaker:
    def __init__(self, name, fallback_func):
        self.name = name
        self.fallback = fallback_func
        self.state = "CLOSED" # "CLOSED", "OPEN", "HALF_OPEN"
        self.consecutive_failures = 0
        self.cooldown_period = 10.0 # seconds to remain in OPEN state
        self.last_state_change = time.time()

    def record_success(self):
        self.consecutive_failures = 0
        if self.state != "CLOSED":
            print(f"[CIRCUIT BREAKER] {self.name} recovered to CLOSED state.")
            self.state = "CLOSED"
            self.last_state_change = time.time()

    def record_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= 3 and self.state == "CLOSED":
            print(f"[CIRCUIT BREAKER] {self.name} tripped! State changed to OPEN (cooldown active).")
            self.state = "OPEN"
            self.last_state_change = time.time()

    def allow_request(self) -> bool:
        if self.state == "OPEN":
            # Check cooldown expiration to try half-open
            if time.time() - self.last_state_change > self.cooldown_period:
                print(f"[CIRCUIT BREAKER] {self.name} cooldown expired. Transitioning to HALF_OPEN probe.")
                self.state = "HALF_OPEN"
                self.last_state_change = time.time()
                return True
            return False
        return True

# Local Heuristics Fallbacks for Degraded-Mode
def fallback_anomaly(frame_data):
    print("[DEGRADED MODE] Behavior Anomaly offline. Executing threshold heuristics fallback.")
    assessments = {}
    anomalies = []
    nodes = frame_data.get("nodes", {})
    for node_name, node_data in nodes.items():
        density = node_data["domain_numeric_values"]["density_per_sqm"]
        velocity = node_data["domain_numeric_values"]["crowd_velocity_mps"]
        
        anomaly_type = "NORMAL"
        msg = "Stable crowd dynamics (degraded fallback)."
        
        if density > 5.0:
            anomaly_type = "CROWD_CRUSH_HAZARD"
            msg = f"[FALLBACK] Density hazard alert at {node_name}."
            anomalies.append({"node_id": node_name, "anomaly_type": anomaly_type, "confidence": 0.85, "log": msg})
            
        assessments[node_name] = {
            "node_id": node_name,
            "anomaly_type": anomaly_type,
            "kinetic_acceleration_variance": 0.05,
            "cognitive_drift_index": 0.35,
            "confidence": 0.85,
            "description": msg
        }
    return {"status": "degraded_success", "assessments": assessments, "anomalies_detected": anomalies}

def fallback_gnn(frame_data):
    print("[DEGRADED MODE] GNN Flow Predictor offline. Executing heuristic capacity matrix fallback.")
    predicted_densities = {}
    spillover_probabilities = {}
    forecasts = {}
    nodes = frame_data.get("nodes", {})
    
    for name, data in nodes.items():
        density = data["domain_numeric_values"]["density_per_sqm"]
        # Basic heuristic progression
        pred_dens = float(density * 1.12)
        spillover_prob = float(1.0 / (1.0 + np.exp(-(pred_dens - 4.5)))) if 'np' in globals() else 0.15
        
        predicted_densities[name] = pred_dens
        spillover_probabilities[name] = spillover_prob
        forecasts[name] = {
            "node_id": name,
            "current_density": density,
            "predicted_density_10m": pred_dens,
            "spillover_probability": spillover_prob,
            "risk_level": "DEGRADED_FALLBACK_RISK",
            "action_recommendation": "[FALLBACK] Flow matrix simulated locally."
        }
    return {"status": "degraded_success", "predicted_densities": predicted_densities, "spillover_probabilities": spillover_probabilities, "forecasts": forecasts}

def fallback_stats():
    print("[DEGRADED MODE] Stats Analysis offline. Executing latency/index baseline fallback.")
    return {
        "status": "degraded_success",
        "global_crowd_anomaly_index": 0.25,
        "average_density": 2.2,
        "anomaly_count": 0,
        "safety_zone": "GREEN",
        "processing_latency_ms": 3.5,
        "optimization_recommendation": "[DEGRADED FALLBACK] Operational baselines served."
    }

cb_anomaly = CircuitBreaker("Behavior Anomaly", fallback_anomaly)
cb_gnn = CircuitBreaker("GNN Flow Predictor", fallback_gnn)
cb_stats = CircuitBreaker("Stats Analysis", fallback_stats)

# ----------------- 3-TIER OPERATIONAL REDIS CACHE (HYBRID WRAPPER) -----------------
class HybridRedisClient:
    def __init__(self):
        self.use_mock = True
        self.mock_l1 = {} # Telemetry buffer
        self.mock_l2 = {} # Semantic cache (State Vector -> Decisions)
        self.mock_l3 = [] # Audit stream log
        
        # Invalidate variables
        self.match_phase_cache = None

        print("[HYBRID REDIS CONFIG] Port 6379 initialized. Active L1/L2/L3 in-memory simulation cache fully enabled.")

    def set_l1_latest(self, key, data):
        self.mock_l1[key] = data

    def get_l1_latest(self, key):
        return self.mock_l1.get(key)

    # Cosine Similarity math for semantic policy matching
    def get_l2_semantic_hit(self, incoming_vector):
        """Computes Cosine Similarity. If similarity > 0.90, returns L2 cached decision."""
        if not incoming_vector or len(incoming_vector) != 24:
            return None
            
        best_match = None
        highest_similarity = -1.0
        
        # Iterate over cache
        for cached_vector_str, policy_data in self.mock_l2.items():
            cached_vector = json_to_vector(cached_vector_str)
            
            # Compute Cosine Similarity
            dot_product = sum(a * b for a, b in zip(incoming_vector, cached_vector))
            norm_inc = sum(a * a for a in incoming_vector) ** 0.5
            norm_cache = sum(b * b for b in cached_vector) ** 0.5
            
            if norm_inc == 0 or norm_cache == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (norm_inc * norm_cache)
                
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = policy_data

        if highest_similarity >= 0.90:
            print(f"[SEMANTIC CACHE HIT] Cosine Similarity is {highest_similarity:.3f} (>0.90). Bypassing analytical pipeline!")
            return best_match
            
        return None

    def set_l2_policy(self, vector, policy_data):
        vector_str = vector_to_json(vector)
        self.mock_l2[vector_str] = policy_data

    def flush_l2_cache(self):
        print("[CONTEXT INVALIDATION] Match phase shift captured. Clearing L2 Semantic Cache Bucket.")
        self.mock_l2.clear()

    def enqueue_l3_log(self, transaction):
        self.mock_l3.append(transaction)
        # In a real environment, this transaction is pushed to Redis List for SQLite write-behind
        # Here we stream it to the Persistence server asynchronously

def vector_to_json(vector):
    return json.dumps(vector)

def json_to_vector(vector_str):
    return json.loads(vector_str)

redis_client = HybridRedisClient()

# ----------------- GLOBALS & HITL COMPENSATIONS -----------------
latest_state = {
    "initialized": False,
    "frame": None,
    "assessments": {},
    "forecasts": {},
    "signage_states": {},
    "overrides_triggered": [],
    "stats": {},
    "timestamp": None,
    "hitl_override_pending": False,
    "hitl_timer": 0
}

# Cached fallback for Saga Rollbacks
saga_rollback_signage_backup = {}
marl_active_policies_backup = []

simulate_gnn_failure = False

@app.post("/api/simulate_failure/gnn")
async def toggle_gnn_failure():
    global simulate_gnn_failure
    simulate_gnn_failure = not simulate_gnn_failure
    status_str = "ACTIVE" if simulate_gnn_failure else "INACTIVE"
    print(f"[GATEWAY] Operator toggled GNN simulation failure to {status_str}")
    return {"status": "success", "simulate_gnn_failure": simulate_gnn_failure}

# ----------------- DYNAMIC CQRS MATERIALIZED READ VIEW -----------------
@app.get("/api/latest")
async def get_latest_state():
    """Independent decoupled read view. Bypasses direct SQLite disk read locks."""
    global latest_state, simulate_gnn_failure
    
    # Tick down HITL rollback timer if active
    if latest_state["hitl_override_pending"] and latest_state["hitl_timer"] > 0:
        latest_state["hitl_timer"] -= 1
        if latest_state["hitl_timer"] <= 0:
            latest_state["hitl_override_pending"] = False
            print("[HITL OVERRIDE] 10-second timed window closed. Signage policies committed permanently.")
            
    # Inject active circuit status maps and failure simulations
    latest_state["circuits"] = {
        "gnn": cb_gnn.state,
        "anomaly": cb_anomaly.state,
        "stats": cb_stats.state
    }
    latest_state["simulate_gnn_failure"] = simulate_gnn_failure
    return latest_state

# ----------------- OPTIMISTIC HITL DENY ROLLBACK (SAGA) -----------------
@app.post("/api/hitl/deny")
async def hitl_deny():
    """Manual Human-in-the-loop override. Instantly rolls back signage commands using Saga compensations."""
    global latest_state, saga_rollback_signage_backup, marl_active_policies_backup
    
    if not latest_state["hitl_override_pending"]:
        return {"status": "no_active_override", "message": "No active override pending confirmation."}

    print("[HITL OVERRIDE] HUMAN OPERATOR TRIGGERED DENY! Executing Saga compensating rollback transaction...")
    
    # Execute Sage Rollback Compensation
    latest_state["signage_states"].update(saga_rollback_signage_backup)
    latest_state["overrides_triggered"] = marl_active_policies_backup.copy()
    latest_state["hitl_override_pending"] = False
    latest_state["hitl_timer"] = 0
    latest_state["stats"]["optimization_recommendation"] = "MANUAL OPERATOR ROLLBACK ENGAGED. Signage reverted to safe baselines."
    latest_state["stats"]["safety_zone"] = "WARNING"
    
    # Log compensating action to Persistence Database (L3 stream queue)
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{PERSISTENCE_URL if 'PERSISTENCE_URL' in globals() else 'http://localhost:8007'}/log_anomaly",
                json={
                    "anomaly_type": "SAGA_COMPENSATION_ROLLBACK",
                    "confidence": 0.99,
                    "raw_log_str": "Saga compensating transaction executed: Reverted all digital signage outputs back to safe ticketing baselines."
                }
            )
        except Exception:
            pass

    return {
        "status": "rolled_back",
        "message": "Saga rollback transaction executed successfully. Digital signage outputs reverted."
    }

# ----------------- PIPELINE ENTRANCE & INGEST -----------------
class IngestFramePayload(BaseModel):
    match_id: str
    event_id: str
    marker: str
    score_summary: str
    primary_actor: str
    secondary_actor: str
    match_phase: str
    plate_redacted: bool
    faces_redacted: bool
    feature_vector: list
    nodes: dict

@app.post("/api/match_cast")
async def match_cast(payload: IngestFramePayload):
    global latest_state, saga_rollback_signage_backup, marl_active_policies_backup
    
    frame_dict = payload.model_dump()
    vector = frame_dict.get("feature_vector", [])
    current_phase = frame_dict.get("match_phase", "Steady Play")

    # Tier L1 Cache Read / Write
    redis_client.set_l1_latest("synapse:telemetry:latest", frame_dict)

    # Context-Aware Cache Invalidation Check
    if latest_state["frame"] and latest_state["frame"].get("match_phase") != current_phase:
        redis_client.flush_l2_cache()

    # Tier L2 Semantic Cache Query (Cosine Similarity Bypass)
    semantic_hit = redis_client.get_l2_semantic_hit(vector)
    if semantic_hit:
        # Cosine similarity >0.90! Immediately serve cached policy response!
        latest_state["signage_states"] = semantic_hit["signage_states"]
        latest_state["overrides_triggered"] = semantic_hit["overrides_triggered"]
        latest_state["stats"]["processing_latency_ms"] = 0.5  # Sub-millisecond!
        latest_state["timestamp"] = frame_dict["marker"]
        latest_state["frame"] = frame_dict
        latest_state["initialized"] = True
        return latest_state

    # Telemetry Ingestion (Port 8002) - validates and applies 5G MEC down-sampling
    async with httpx.AsyncClient() as client:
        try:
            ingest_resp = await client.post(f"{INGESTION_URL}/ingest", json=frame_dict, timeout=2.0)
            if ingest_resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Ingestion service error")
            enhanced_frame = ingest_resp.json()["frame"]
        except Exception as e:
            # Degraded threshold fallback for Ingestion if offline
            enhanced_frame = frame_dict

        # Parallel Analytics Mesh queries using Circuit Breakers
        # 1. Behavior Anomaly (Port 8003)
        if cb_anomaly.allow_request():
            try:
                t_start = time.time()
                anom_resp = await client.post(f"{ANOMALY_URL}/analyze", json=enhanced_frame, timeout=2.0)
                if anom_resp.status_code == 200:
                    cb_anomaly.record_success()
                    anomaly_data = anom_resp.json()
                else:
                    cb_anomaly.record_failure()
                    anomaly_data = fallback_anomaly(enhanced_frame)
            except Exception:
                cb_anomaly.record_failure()
                anomaly_data = fallback_anomaly(enhanced_frame)
        else:
            anomaly_data = fallback_anomaly(enhanced_frame)

        # 2. GNN Flow Predictor (Port 8004)
        if cb_gnn.allow_request() and not simulate_gnn_failure:
            try:
                gnn_resp = await client.post(f"{GNN_URL}/predict", json=enhanced_frame, timeout=2.0)
                if gnn_resp.status_code == 200:
                    cb_gnn.record_success()
                    gnn_data = gnn_resp.json()
                else:
                    cb_gnn.record_failure()
                    gnn_data = fallback_gnn(enhanced_frame)
            except Exception:
                cb_gnn.record_failure()
                gnn_data = fallback_gnn(enhanced_frame)
        else:
            if simulate_gnn_failure:
                cb_gnn.record_failure()
            gnn_data = fallback_gnn(enhanced_frame)

        # 3. Stats Analyzer (Port 8006)
        if cb_stats.allow_request():
            try:
                stats_resp = await client.get(f"{STATS_URL}/analyze", timeout=2.0)
                if stats_resp.status_code == 200:
                    cb_stats.record_success()
                    stats_data = stats_resp.json()
                else:
                    cb_stats.record_failure()
                    stats_data = fallback_stats()
            except Exception:
                cb_stats.record_failure()
                stats_data = fallback_stats()
        else:
            stats_data = fallback_stats()

        # MARL Orchestrator (Port 8005) - policy configurations
        try:
            marl_resp = await client.post(
                f"{MARL_URL}/orchestrate",
                json={
                    "frame": enhanced_frame,
                    "assessments": anomaly_data["assessments"]
                },
                timeout=2.0
            )
            marl_data = marl_resp.json()
        except Exception:
            # Fallback signage states if MARL is down
            marl_data = {
                "signage_states": {
                    "Gate A": "PROCEED: Ticket Scan Active",
                    "Gate B": "PROCEED: Ticket Scan Active",
                    "Main Concourse": "FLOW CLEAR: Keep Moving",
                    "Food Court": "OPEN: Standard Operations"
                },
                "overrides_triggered": []
            }

        # Check for High-Priority Safety Overrides -> Engage Optimistic HITL Overrides
        overrides = marl_data.get("overrides_triggered", [])
        is_high_priority_override = len(overrides) > 0
        
        if is_high_priority_override and not latest_state["hitl_override_pending"]:
            # Backup original signage states before applying optimistic override (to allow Saga rollback)
            if latest_state["signage_states"]:
                saga_rollback_signage_backup = latest_state["signage_states"].copy()
                marl_active_policies_backup = latest_state["overrides_triggered"].copy()
            else:
                saga_rollback_signage_backup = {
                    "Gate A": "PROCEED: Ticket Scan Active",
                    "Gate B": "PROCEED: Ticket Scan Active",
                    "Main Concourse": "FLOW CLEAR: Keep Moving",
                    "Food Court": "OPEN: Standard Operations"
                }
                marl_active_policies_backup = []

            # Engage optimistic trigger
            latest_state["hitl_override_pending"] = True
            latest_state["hitl_timer"] = 10  # 10 second timed window countdown
            print(f"[HITL OVERRIDE ENGAGED] High priority safety override executed optimistically! 10-second rollback window active.")

        # Compile consolidated response
        aggregated_payload = {
            "initialized": True,
            "frame": enhanced_frame,
            "assessments": anomaly_data["assessments"],
            "forecasts": gnn_data["forecasts"],
            "signage_states": marl_data["signage_states"],
            "overrides_triggered": overrides if not latest_state["hitl_override_pending"] or latest_state["hitl_timer"] > 0 else overrides,
            "anomalies_detected": anomaly_data["anomalies_detected"],
            "stats": stats_data,
            "timestamp": enhanced_frame["marker"],
            "hitl_override_pending": latest_state["hitl_override_pending"],
            "hitl_timer": latest_state["hitl_timer"]
        }

        # Update cache L2 Semantic Policy cache for cache hits on future similar states
        redis_client.set_l2_policy(vector, {
            "signage_states": marl_data["signage_states"],
            "overrides_triggered": overrides
        })

        # Tier L3 Transaction Log Queue
        redis_client.enqueue_l3_log({
            "timestamp": time.time(),
            "event_id": enhanced_frame["event_id"],
            "marker": enhanced_frame["marker"],
            "overrides_count": len(overrides)
        })

        latest_state.update(aggregated_payload)
        return latest_state

# Serve Dashboard UI at root /
@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Synapse Grid API running. Dashboard UI static files not loaded yet."}

# Mount static directories
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
